import { useEffect, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import type { Epistemic, Source } from '../content/types';
import { EPISTEMIC_LABELS } from '../content/registry';

export function usePageTitle(title: string) {
  useEffect(() => {
    document.title = `${title} · Substrate University — Haq Roots`;
  }, [title]);
}

export function Status({ s }: { s: Epistemic }) {
  return (
    <span className={`tag ${s}`} title={EPISTEMIC_LABELS[s].description}>
      {EPISTEMIC_LABELS[s].label}
    </span>
  );
}

export function Crumbs({ items }: { items: [string, string?][] }) {
  return (
    <nav className="crumbs" aria-label="Breadcrumb">
      {items.map(([label, to], i) => (
        <span key={i}>
          {i > 0 ? ' / ' : ''}
          {to ? <Link to={to}>{label}</Link> : label}
        </span>
      ))}
    </nav>
  );
}

export function SourceList({ sources }: { sources: Source[] }) {
  return (
    <ul className="small">
      {sources.map((s) => (
        <li key={s.title}>
          {s.authors}
          {s.year ? ` (${s.year})` : ''}. {s.url ? s.url.startsWith('/') ? <Link to={s.url}>{s.title}</Link> : <a href={s.url} rel="noopener noreferrer" target="_blank">{s.title}</a> : <em>{s.title}</em>}
          {s.locator ? `. ${s.locator}` : ''}. <span className="tag">{s.status.replace('-', ' ')}</span>
        </li>
      ))}
    </ul>
  );
}

export function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export function download(name: string, data: Uint8Array | string, type: string) {
  const blob = new Blob([data as BlobPart], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}

export function slug(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
}
