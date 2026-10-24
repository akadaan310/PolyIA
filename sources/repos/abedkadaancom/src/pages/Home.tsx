import { Link } from 'react-router-dom';
import { DIVISIONS } from '../content/registry';
import { getState, useStore } from '../state/store';
import { welcomeLine } from '../world/residents';
import { LOCATIONS } from '../world/locations';
import { usePageTitle } from '../ui/bits';

export function Home() {
  usePageTitle('The Approach');
  const lastRoute = useStore((s) => s.lastRoute);
  const harness = useStore((s) => s.harness);
  const resume = lastRoute && lastRoute !== '/' ? LOCATIONS.find((l) => lastRoute.startsWith(l.path) && l.path !== '/') : null;
  return (
    <article>
      <p className="engraved small" style={{ color: 'var(--gold)' }}>The Approach</p>
      <h1>Substrate University — Haq Roots</h1>
      <p className="luminous" style={{ fontSize: '1.2rem' }}>A free, public university of ideas devoted to the mathematics of possible worlds. The campus is the interface; mathematics decides what it does.</p>
      <div className="notice gold">
        <span className="engraved small">Harness Master · </span>
        {welcomeLine(getState())}
      </div>
      <div className="btn-row">
        <Link className="btn primary" to="/gate" style={{ textDecoration: 'none' }}>
          Begin at the Gate: what is 1 + 1?
        </Link>
        <Link className="btn" to="/harness" style={{ textDecoration: 'none' }}>
          {harness.startedAt && !harness.completedAt ? 'Continue your One-Day Harness' : 'Enter the One-Day Harness'}
        </Link>
        {resume ? (
          <Link className="btn" to={lastRoute!} style={{ textDecoration: 'none' }}>
            Resume at {resume.short}
          </Link>
        ) : null}
      </div>

      <h2>Six doors</h2>
      <p className="small muted">Each door opens a realm with lessons, a glossary, a curriculum and one exhibit that genuinely computes. Select a door in the 3D atrium or here.</p>
      <div className="grid">
        {DIVISIONS.map((d) => (
          <Link key={d.id} className="card" to={`/divisions/${d.id}`}>
            <div className="k">
              {d.numeral} · {d.door}
            </div>
            <div className="t">{d.name}</div>
            <div className="small muted">{d.motto}</div>
          </Link>
        ))}
      </div>

      <h2>How the campus works</h2>
      <ul>
        <li>Every interactive change in the world is a computation you can inspect: bridges appear only where a typed predicate passes; arches light by a gcd; a walkway folds by a grammar; a sculpture is the image of your matrix.</li>
        <li>Everything runs in your browser. No AI model, no server program. Progress stays on this device unless you opt in to cloud sync.</li>
        <li>Each subject carries a label: <span className="tag established">Established mathematics</span> <span className="tag house">House construction</span> <span className="tag application">Application in development</span> <span className="tag mythology">Campus mythology</span>.</li>
        <li>Residents and campus Harness Masters are fictional characters; the founders are real: <strong>Abed Kadaan</strong> and <strong>7u</strong>, an AI collaborator.</li>
        <li>This is a university of ideas and experiences, not an accredited degree-granting institution.</li>
      </ul>
      <h2>Places</h2>
      <div className="grid">
        {[
          ['/library', 'The Library of Forms', 'Specimen volumes, the founding Computational Grammar Theory book, and books visitors choose to publish.'],
          ['/observatory', 'The Observatory', 'Your location, the real sky above it, and the geometry of linked places.'],
          ['/harness-masters', 'Hall of Harness Masters', 'Co-founders, the HM role, and requesting a conversation.'],
          ['/scriptorium', 'The Scriptorium', 'Where a one-day harness becomes six books, typeset in your browser.'],
          ['/common-room', 'Founder Office · Common Room', 'Questions, notes and invitations.'],
          ['/glossary', 'The Glossary Field', 'One word, several meanings, and the computations that bridge them.'],
        ].map(([to, t, d]) => (
          <Link key={to} className="card" to={to!}>
            <div className="t">{t}</div>
            <div className="small muted">{d}</div>
          </Link>
        ))}
      </div>
    </article>
  );
}
