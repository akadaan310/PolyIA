// Optional Supabase facility. Configured only by VITE_SUPABASE_URL and
// VITE_SUPABASE_PUBLISHABLE_KEY (publishable/anon key; never a service key).
// When unset, the client library is never downloaded and nothing leaves the
// browser. Every call here is initiated by an explicit visitor action.

import type { SupabaseClient } from '@supabase/supabase-js';
import type { Book } from '../books/compose';
import type { Contribution, HarnessState } from '../state/store';

const SB_URL = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string | undefined;

export const cloudConfigured = Boolean(SB_URL && KEY);
export const cloudHost = SB_URL ? new URL(SB_URL).host : null;

let client: Promise<SupabaseClient> | null = null;
function sb(): Promise<SupabaseClient> {
  if (!cloudConfigured) return Promise.reject(new Error('cloud facility not configured on this deployment'));
  client ??= import('@supabase/supabase-js').then(({ createClient }) => createClient(SB_URL!, KEY!, { auth: { persistSession: true, detectSessionInUrl: true } }));
  return client;
}

export async function sessionEmail(): Promise<string | null> {
  if (!cloudConfigured) return null;
  const { data } = await (await sb()).auth.getSession();
  return data.session?.user.email ?? null;
}

export async function signInWithEmail(email: string): Promise<void> {
  const { error } = await (await sb()).auth.signInWithOtp({ email, options: { emailRedirectTo: `${location.origin}/harness` } });
  if (error) throw error;
}

export async function signOut(): Promise<void> {
  await (await sb()).auth.signOut();
}

export async function syncHarness(h: HarnessState): Promise<void> {
  const c = await sb();
  const { error } = await c.from('harness_runs').upsert(
    { local_run_id: h.runId, interest: h.interest, stations: h.stations, started_at: h.startedAt, completed_at: h.completedAt, updated_at: new Date().toISOString() },
    { onConflict: 'owner,local_run_id' },
  );
  if (error) throw error;
}

export async function saveManifest(b: Book): Promise<string> {
  const c = await sb();
  const manifest = { id: b.id, division: b.division, title: b.title, subtitle: b.subtitle, author: b.author, edition: b.edition, depth: b.depth, topicId: b.topicId, createdAt: b.createdAt, credits: b.credits, ledger: b.ledger };
  const { data, error } = await c
    .from('book_manifests')
    .upsert({ book_id: b.id, division: b.division, title: b.title, author_display: b.author, edition: b.edition, manifest }, { onConflict: 'owner,book_id' })
    .select('id')
    .single();
  if (error) throw error;
  return (data as { id: string }).id;
}

/** Publishing requires an explicit consent action; it is never automatic. */
export async function publishBook(b: Book, consent: boolean): Promise<void> {
  if (!consent) throw new Error('publication requires explicit consent');
  const c = await sb();
  const manifestId = await saveManifest(b);
  const { error } = await c.from('book_publications').insert({ manifest_id: manifestId, published: true, consent_at: new Date().toISOString() });
  if (error) throw error;
}

export interface PublicBook {
  book_id: string;
  division: string;
  title: string;
  author_display: string;
  edition: number;
  published_at: string;
}

export async function listPublicBooks(): Promise<PublicBook[]> {
  const { data, error } = await (await sb()).from('public_books').select('*').order('published_at', { ascending: false }).limit(200);
  if (error) throw error;
  return (data ?? []) as PublicBook[];
}

export async function submitContribution(c: Contribution): Promise<void> {
  const { error } = await (await sb()).from('contributions').insert({ kind: c.kind, term: c.term, body: c.text });
  if (error) throw error;
}
