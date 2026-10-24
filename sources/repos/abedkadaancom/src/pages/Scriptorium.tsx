import { useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { composeBooks, ROMAN, type Block, type Book } from '../books/compose';
import type { FontBytes } from '../books/pdf';
import { defaultHarness, updateHarness, useStore, type HarnessState } from '../state/store';
import { cloudConfigured, publishBook, saveManifest } from '../lib/cloud';
import { PlateSvg } from '../ui/PlateSvg';
import { Crumbs, download, slug, usePageTitle } from '../ui/bits';
import { pageTurn } from '../audio/engine';
import { DIVISIONS } from '../content/registry';
import { NotFound } from './NotFound';

/** A demonstration journey: no exercises, no reflections, a clearly fictional name. */
export function sampleHarness(): HarnessState {
  const at = '2026-10-21T09:00:00.000Z';
  return {
    ...defaultHarness(),
    runId: 'sample',
    startedAt: at,
    completedAt: at,
    displayName: 'Sample Harnesser (demonstration)',
    interest: 'geometry',
    stations: Object.fromEntries(DIVISIONS.map((d) => [d.id, { division: d.id, topicId: '', enteredAt: at, exercise: null, reflection: '', completedAt: at }])),
  };
}

let fontCache: Promise<FontBytes> | null = null;
/** The PDF engine (pdf-lib + fontkit) is downloaded only when a visitor asks for a PDF. */
async function pdfFor(b: Book): Promise<Uint8Array> {
  const { bookToPdf, fetchFonts } = await import('../books/pdf');
  fontCache ??= fetchFonts();
  return bookToPdf(b, await fontCache, location.origin);
}

function useBooks(): { books: Book[]; sample: Book[] } {
  const h = useStore((s) => s.harness);
  const books = useMemo(() => (h.completedAt ? composeBooks({ harness: h, now: h.completedAt }) : []), [h]);
  const sample = useMemo(() => composeBooks({ harness: sampleHarness(), now: '2026-10-21T09:00:00.000Z' }), []);
  return { books, sample };
}

export function Scriptorium() {
  usePageTitle('The Scriptorium');
  const h = useStore((s) => s.harness);
  const { books, sample } = useBooks();
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [rename, setRename] = useState(h.displayName ?? '');
  const [consent, setConsent] = useState(false);
  const dl = async (b: Book) => {
    setBusy(b.id);
    try {
      download(`${slug(b.title)}-${b.id}.pdf`, await pdfFor(b), 'application/pdf');
      pageTurn();
    } catch (e) {
      setMsg(`PDF generation failed: ${(e as Error).message}`);
    } finally {
      setBusy(null);
    }
  };
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Scriptorium']]} />
      <h1>The Scriptorium</h1>
      <p>Here a day becomes six books. Each volume is composed in your browser from the university’s vetted lessons, the computations you ran, and the words you wrote. Each one says plainly which is which.</p>
      {books.length ? (
        <>
          <h2>Your six volumes</h2>
          <p className="small">Credited to <strong>{books[0]!.author}</strong> · edition {h.edition}. Nothing has been sent anywhere.</p>
          <div className="grid">
            {books.map((b) => (
              <div key={b.id} className="card" style={{ borderLeft: `3px solid ${DIVISIONS.find((d) => d.id === b.division)!.accent}` }}>
                <div className="k">
                  {b.numeral} · {b.divisionName}
                </div>
                <div className="t">{b.title}</div>
                <div className="small muted">{b.subtitle}</div>
                <div className="small">{b.depth === 'exercised' ? 'You ran this exhibit.' : b.depth === 'visited' ? 'Brief encounter: worked example on standard inputs.' : 'Not entered.'}</div>
                <div className="btn-row">
                  <Link className="btn small" to={`/scriptorium/${b.id}`} style={{ textDecoration: 'none' }}>
                    Read
                  </Link>
                  <button className="btn small" onClick={() => dl(b)} disabled={busy !== null}>
                    {busy === b.id ? 'Typesetting…' : 'PDF'}
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div className="btn-row">
            <button
              className="btn primary"
              disabled={busy !== null}
              onClick={async () => {
                for (const b of books) await dl(b);
              }}
            >
              Download all six PDFs
            </button>
            <button className="btn" onClick={() => updateHarness((x) => ({ edition: x.edition + 1 }))}>
              Regenerate (new edition: new titles, same content)
            </button>
          </div>
          <fieldset>
            <legend>Rename or go private</legend>
            <label htmlFor="rn">Display name</label>
            <input id="rn" type="text" value={rename} onChange={(e) => setRename(e.target.value)} maxLength={60} />
            <div className="btn-row">
              <button className="btn" onClick={() => updateHarness({ displayName: rename.trim() || null })}>
                Apply name
              </button>
              <button className="btn" onClick={() => { setRename(''); updateHarness({ displayName: null }); }}>
                Remain private
              </button>
            </div>
          </fieldset>
          {cloudConfigured ? (
            <fieldset>
              <legend>Keep or publish (optional cloud facility)</legend>
              <p className="small">Saving stores a manifest (titles, credits, ledger) in your account. Publishing lists a book in the Library’s public catalogue under your display name. Nothing is published without the box below.</p>
              <label className="choice">
                <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} /> I consent to publishing these books publicly under the name “{books[0]!.author}”.
              </label>
              <div className="btn-row">
                <button className="btn" onClick={() => Promise.all(books.map(saveManifest)).then(() => setMsg('Saved to your account.'), (e: Error) => setMsg(e.message))}>
                  Save manifests
                </button>
                <button className="btn" disabled={!consent} onClick={() => Promise.all(books.map((b) => publishBook(b, consent))).then(() => setMsg('Published.'), (e: Error) => setMsg(e.message))}>
                  Publish to the Library
                </button>
              </div>
            </fieldset>
          ) : (
            <p className="small muted">Saving to an account and public publication need the optional cloud facility, which is not configured on this deployment. Your books remain downloadable, printable and regenerable here.</p>
          )}
          {msg ? <p className="small" role="status">{msg}</p> : null}
        </>
      ) : (
        <>
          <p className="notice gold">
            {h.startedAt ? `Your harness is in progress (${Object.values(h.stations).filter((s) => s?.completedAt).length} of 6 stations).` : 'You have not begun a harness.'} <Link to="/harness">{h.startedAt ? 'Continue the harness' : 'Enter the One-Day Harness'}</Link> to have six books made for you.
          </p>
          <h2>A sample volume</h2>
          <p className="small">To see what the Scriptorium makes, read a demonstration volume composed for “Sample Harnesser (demonstration)”, a fictional participant who visited every station without running exhibits or writing reflections. It shows the structure, and how a book admits what was not done.</p>
          <div className="btn-row">
            {sample.map((b) => (
              <Link key={b.id} className="btn small" to={`/scriptorium/${b.id}`} style={{ textDecoration: 'none' }}>
                {b.numeral}. {b.divisionName}
              </Link>
            ))}
          </div>
        </>
      )}
    </article>
  );
}

function BlockView({ b }: { b: Block }) {
  const by = 'by' in b ? <span className={`by tag ${b.by}`}>{b.by === 'participant' ? 'by you' : b.by}</span> : null;
  switch (b.k) {
    case 'p':
      return <p>{b.text} {b.by !== 'generated' ? by : null}</p>;
    case 'h':
      return <h3>{b.text}</h3>;
    case 'eq':
      return (
        <div>
          <div className="math-block">{b.lines.join('\n')}</div>
          {by}
        </div>
      );
    case 'quote':
      return (
        <blockquote>
          {b.text}
          <div className="by">— {b.who} {by}</div>
        </blockquote>
      );
    case 'list':
      return <ul>{b.items.map((i) => <li key={i}>{i}</li>)}</ul>;
    case 'def':
      return (
        <div className="def">
          <b>{b.term}</b> <span className="tag">{b.status}</span>
          <div>{b.text}</div>
        </div>
      );
  }
}

export function BookReader() {
  const { bookId = '' } = useParams();
  const { books, sample } = useBooks();
  const b = [...books, ...sample].find((x) => x.id === bookId);
  const [busy, setBusy] = useState(false);
  usePageTitle(b ? b.title : 'Book not found');
  if (!b) return <NotFound />;
  const isSample = sample.includes(b);
  return (
    <article>
      <Crumbs items={[['Scriptorium', '/scriptorium'], [b.title]]} />
      {isSample ? <div className="notice no-print">Demonstration volume for a fictional sample participant. Not anyone’s book.</div> : null}
      <div className="btn-row no-print">
        <button
          className="btn primary"
          disabled={busy}
          onClick={async () => {
            setBusy(true);
            try {
              download(`${slug(b.title)}-${b.id}.pdf`, await pdfFor(b), 'application/pdf');
            } finally {
              setBusy(false);
            }
          }}
        >
          {busy ? 'Typesetting…' : 'Download PDF'}
        </button>
        <button className="btn" onClick={() => window.print()}>
          Print
        </button>
      </div>
      <div className="reader">
        <div className="cover">
          <div className="engraved small" style={{ color: 'var(--gold)' }}>
            Substrate University · Division {b.numeral}
          </div>
          <div className="t">{b.title}</div>
          <div className="luminous">{b.subtitle}</div>
          <p style={{ marginTop: '1rem' }}>{b.author}</p>
          <div className="small muted">
            edition {b.edition} · {b.createdAt.slice(0, 10)} · local id {b.id}
          </div>
        </div>
        <section>
          <h2>Credits</h2>
          <p>{b.credits.participant}</p>
          {b.credits.foundingWorks.length ? <p className="small">Founding works cited: {b.credits.foundingWorks.join('; ')}.</p> : null}
          <p className="small">Generated educational material: {b.credits.generatedBy}.</p>
        </section>
        {b.chapters.map((c, i) => (
          <section key={c.id} className="ch">
            <h2>
              {ROMAN[i]}. {c.title}
            </h2>
            {c.blocks.map((bl, j) => (
              <BlockView key={j} b={bl} />
            ))}
            {c.id === 'plate' ? (
              <figure className="figure">
                <PlateSvg plate={b.plate} />
                <figcaption>{b.plate.title}</figcaption>
              </figure>
            ) : null}
          </section>
        ))}
        <section className="ch">
          <h2>{ROMAN[b.chapters.length]}. Glossary</h2>
          {b.glossary.map((g) => (
            <div key={g.term} className="def">
              <b>{g.term}</b> <span className="tag">{g.status}</span>
              <div>{g.text}</div>
            </div>
          ))}
        </section>
        <section className="ch">
          <h2>{ROMAN[b.chapters.length + 1]}. Bibliography and links</h2>
          <ul>
            {b.bibliography.map((s) => (
              <li key={s.title}>
                {s.authors}
                {s.year ? ` (${s.year})` : ''}. {s.url ? <a href={s.url}>{s.title}</a> : <em>{s.title}</em>}
                {s.locator ? `. ${s.locator}` : ''}.
              </li>
            ))}
          </ul>
        </section>
      </div>
    </article>
  );
}
