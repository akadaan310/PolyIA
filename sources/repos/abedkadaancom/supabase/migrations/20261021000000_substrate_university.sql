-- Substrate University — Haq Roots: optional cloud facility.
-- Applied only to a Supabase project the owner authorizes. The site runs fully
-- without it. Browser code uses the publishable (anon) key only; every table is
-- protected by row-level security. Public book listing requires a positive
-- opt-in flag set by the owner.

create table if not exists public.members (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text check (display_name is null or char_length(display_name) between 1 and 80),
  public_name_consent boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.harness_runs (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references auth.users (id) on delete cascade default auth.uid(),
  local_run_id text not null,
  interest text,
  stations jsonb not null default '{}'::jsonb,
  started_at timestamptz,
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  unique (owner, local_run_id)
);

create table if not exists public.book_manifests (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references auth.users (id) on delete cascade default auth.uid(),
  book_id text not null,
  division text not null check (division in ('foundations','relational','languages','geometry','acoustic','worlds')),
  title text not null check (char_length(title) <= 200),
  author_display text not null check (char_length(author_display) <= 80),
  edition int not null default 1,
  manifest jsonb not null,
  created_at timestamptz not null default now(),
  unique (owner, book_id)
);

create table if not exists public.book_publications (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references auth.users (id) on delete cascade default auth.uid(),
  manifest_id uuid not null references public.book_manifests (id) on delete cascade,
  published boolean not null default false,
  consent_at timestamptz,
  created_at timestamptz not null default now(),
  constraint consent_required check (published = false or consent_at is not null)
);

create table if not exists public.contributions (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references auth.users (id) on delete cascade default auth.uid(),
  kind text not null check (kind in ('glossary-sense','example','question')),
  term text check (char_length(term) <= 80),
  body text not null check (char_length(body) between 1 and 4000),
  created_at timestamptz not null default now()
);

create table if not exists public.subject_feedback (
  id uuid primary key default gen_random_uuid(),
  owner uuid references auth.users (id) on delete set null default auth.uid(),
  topic_id text not null check (char_length(topic_id) <= 80),
  body text not null check (char_length(body) between 1 and 4000),
  created_at timestamptz not null default now()
);

alter table public.members enable row level security;
alter table public.harness_runs enable row level security;
alter table public.book_manifests enable row level security;
alter table public.book_publications enable row level security;
alter table public.contributions enable row level security;
alter table public.subject_feedback enable row level security;

-- Owners manage their own rows.
create policy members_own on public.members for all to authenticated using (id = (select auth.uid())) with check (id = (select auth.uid()));
create policy runs_own on public.harness_runs for all to authenticated using (owner = (select auth.uid())) with check (owner = (select auth.uid()));
create policy manifests_own on public.book_manifests for all to authenticated using (owner = (select auth.uid())) with check (owner = (select auth.uid()));
create policy publications_own on public.book_publications for all to authenticated using (owner = (select auth.uid())) with check (owner = (select auth.uid()));
create policy contributions_own on public.contributions for all to authenticated using (owner = (select auth.uid())) with check (owner = (select auth.uid()));
create policy feedback_insert on public.subject_feedback for insert to authenticated with check (owner = (select auth.uid()));
create policy feedback_own_read on public.subject_feedback for select to authenticated using (owner = (select auth.uid()));

-- Public catalogue: only deliberately published books, through a view that
-- exposes no owner ids and no unpublished manifests.
create policy manifests_public_read on public.book_manifests for select to anon, authenticated
  using (exists (select 1 from public.book_publications p where p.manifest_id = book_manifests.id and p.published));
create policy publications_public_read on public.book_publications for select to anon, authenticated using (published);

create or replace view public.public_books with (security_invoker = true) as
  select m.book_id, m.division, m.title, m.author_display, m.edition, p.consent_at as published_at
  from public.book_manifests m join public.book_publications p on p.manifest_id = m.id
  where p.published;

grant select on public.public_books to anon, authenticated;
