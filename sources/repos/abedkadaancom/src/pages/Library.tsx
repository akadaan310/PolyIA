import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { CGT } from '../content/cgt';
import { DIVISIONS } from '../content/registry';
import { specimens, specimen, SPECIMEN_LABEL } from '../world/specimens';
import { useStore } from '../state/store';
import { composeBooks } from '../books/compose';
import { cloudConfigured, listPublicBooks, type PublicBook } from '../lib/cloud';
import { Crumbs, Status, usePageTitle } from '../ui/bits';
import { NotFound } from './NotFound';

export const CGT_BASE = '/cgt/';

export function Library() {
  usePageTitle('The Library of Forms');
  const harness = useStore((s) => s.harness);
  const mine = useMemo(() => (harness.completedAt ? composeBooks({ harness }) : []), [harness]);
  const [filter, setFilter] = useState<string>('all');
  const all = specimens();
  const shown = filter === 'all' ? all : all.filter((s) => s.a.division === filter);
  const [publicBooks, setPublicBooks] = useState<PublicBook[] | null>(null);
  const [publicError, setPublicError] = useState<string | null>(null);
  useEffect(() => {
    if (!cloudConfigured) return;
    listPublicBooks().then(setPublicBooks, (e: Error) => setPublicError(e.message));
  }, []);
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Library']]} />
      <h1>The Library of Forms</h1>
      <p>Three kinds of book live here, and the Library never confuses them: the founding work, books that visitors have chosen to publish, and specimen volumes generated from the subject registry.</p>

      <h2>The founding shelf</h2>
      <Link className="card" to="/library/computational-grammar-theory">
        <div className="k">Real publication · working edition 0.1</div>
        <div className="t">{CGT.title}</div>
        <div className="small">{CGT.subtitle}. By {CGT.author}.</div>
        <div className="small muted">{CGT.status}</div>
      </Link>

      <h2>Participant books</h2>
      {mine.length ? (
        <>
          <p className="small">Your six volumes, on this device only (not published):</p>
          <ul>
            {mine.map((b) => (
              <li key={b.id}>
                <Link to={`/scriptorium/${b.id}`}>{b.title}</Link> <span className="small muted">— {b.divisionName}</span>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p className="small muted">You have no volumes yet. Complete the <Link to="/harness">One-Day Harness</Link> and the Scriptorium will typeset six.</p>
      )}
      {cloudConfigured ? (
        publicError ? (
          <p className="small">The public catalogue could not be loaded: {publicError}</p>
        ) : publicBooks === null ? (
          <p className="small muted">Loading the public catalogue…</p>
        ) : publicBooks.length === 0 ? (
          <p className="small">No participant has published a book yet. Counts here come only from stored, consented records.</p>
        ) : (
          <>
            <p className="small">{publicBooks.length} book(s) published by participants with consent:</p>
            <ul>
              {publicBooks.map((b) => (
                <li key={b.book_id}>
                  {b.title} — {b.author_display} <span className="tag">{b.division}</span>
                </li>
              ))}
            </ul>
          </>
        )
      ) : (
        <p className="notice small">The public contributor catalogue needs the optional cloud facility, which is not configured on this deployment. No participant books are listed, and no counts are shown, because none are stored.</p>
      )}

      <h2>{SPECIMEN_LABEL}s</h2>
      <p className="small muted">
        {all.length} specimen volumes, each generated from two real registry topics that share a term or a prerequisite. They glow on the 3D shelves and lead to lessons. They are previews, not publications, and never anyone’s book.
      </p>
      <label htmlFor="spec-filter">Shelf</label>
      <select id="spec-filter" value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All divisions</option>
        {DIVISIONS.map((d) => (
          <option key={d.id} value={d.id}>
            {d.numeral}. {d.name}
          </option>
        ))}
      </select>
      <div className="grid" style={{ marginTop: 10 }}>
        {shown.slice(0, 60).map((s) => (
          <Link key={s.id} className="card" to={`/library/specimens/${s.id}`} style={{ borderLeft: `3px solid ${s.color}` }}>
            <div className="k">{SPECIMEN_LABEL}</div>
            <div className="t" style={{ fontSize: '1.02rem' }}>{s.title}</div>
          </Link>
        ))}
      </div>
      {shown.length > 60 ? <p className="small muted">…and {shown.length - 60} more on the 3D shelves.</p> : null}
    </article>
  );
}

export function CgtReader() {
  usePageTitle(CGT.title);
  const [chapter, setChapter] = useState<string>('index');
  const src = chapter === 'index' ? `${CGT_BASE}index.html` : `${CGT_BASE}chapters/${chapter}.html`;
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Library', '/library'], [CGT.title]]} />
      <p className="engraved small" style={{ color: 'var(--gold)' }}>Founding shelf · real publication</p>
      <h1>{CGT.title}</h1>
      <p className="luminous">{CGT.subtitle}</p>
      <p>
        By <strong>{CGT.author}</strong>, {CGT.role}. {CGT.edition}.
      </p>
      <p className="small muted">{CGT.status}</p>
      <p>{CGT.description}</p>
      <div className="btn-row">
        <a className="btn primary" href={`${CGT_BASE}index.html`} target="_blank" rel="noopener" style={{ textDecoration: 'none' }}>
          Open the full book
        </a>
        <a className="btn" href={`${CGT_BASE}downloads/computational-grammar-theory.pdf`} target="_blank" rel="noopener" style={{ textDecoration: 'none' }}>
          PDF edition
        </a>
        <a className="btn" href="https://github.com/akadaan310/computationalgrammartheory" target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
          Source repository
        </a>
      </div>
      <figure className="figure" style={{ padding: 0 }}>
        <iframe title={`${CGT.title} — reader`} src={src} style={{ width: '100%', height: '60vh', border: 0, background: '#fff' }} loading="lazy" />
        <figcaption style={{ padding: '0.4rem' }}>The book is served unmodified from its own deployment, under this site at /cgt/. If the reader does not load here, use “Open the full book”.</figcaption>
      </figure>
      <h2>Contents</h2>
      {CGT.parts.map((p) => (
        <section key={p.id}>
          <h3>
            {p.id === 'A' ? 'Appendices' : `Part ${p.id}`}: {p.title}
          </h3>
          <ul>
            {p.chapters.map((c) => (
              <li key={c.slug}>
                <button className="btn small" style={{ marginRight: 6 }} onClick={() => setChapter(c.slug)} aria-label={`Read ${c.title} here`}>
                  Read
                </button>
                <a href={`${CGT_BASE}chapters/${c.slug}.html`} target="_blank" rel="noopener">
                  {c.title}
                </a>
                <div className="small muted">{c.description}</div>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </article>
  );
}

export function SpecimenPage() {
  const { id = '' } = useParams();
  const s = specimen(id);
  usePageTitle(s ? s.title : 'Not found');
  if (!s) return <NotFound />;
  const shared = s.a.glossary.filter((g) => s.b.glossary.includes(g));
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Library', '/library'], [SPECIMEN_LABEL]]} />
      <div className="notice">
        <strong>{SPECIMEN_LABEL}.</strong> This volume was generated by the Library from two registry topics. It is a preview of how the subjects connect, not a publication and not a participant’s book.
      </div>
      <h1>{s.title}</h1>
      <p className="small">
        Combines <Link to={`/divisions/${s.a.division}/${s.a.id}`}>{s.a.title}</Link> <Status s={s.a.status} /> and <Link to={`/divisions/${s.b.division}/${s.b.id}`}>{s.b.title}</Link> <Status s={s.b.status} />.
      </p>
      <h2>Preview</h2>
      <p>{s.a.summary}</p>
      <p>{s.b.summary}</p>
      <p>
        {shared.length
          ? `The two subjects meet in the term${shared.length > 1 ? 's' : ''} ${shared.map((g) => `“${g}”`).join(', ')}, whose senses differ between them; the glossary field shows how.`
          : `${s.a.title} is a prerequisite of ${s.b.title}, so reading them in this order follows the curriculum path.`}
      </p>
      <p className="small muted">Generated text above is composed of the two topics’ registry summaries; no new claims are added.</p>
    </article>
  );
}
