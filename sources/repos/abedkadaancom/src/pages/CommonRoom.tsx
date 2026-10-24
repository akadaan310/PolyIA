import { useState } from 'react';
import { Link } from 'react-router-dom';
import { setState, useStore } from '../state/store';
import { RESIDENTS, FICTION_NOTE } from '../world/residents';
import { openResident } from '../ui/residentBus';
import { Crumbs, usePageTitle } from '../ui/bits';

export function CommonRoom() {
  usePageTitle('Founder Office · Common Room');
  const notes = useStore((s) => s.notes);
  const [text, setText] = useState('');
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Common Room']]} />
      <h1>Founder Office · Common Room</h1>
      <p>A warm room off the north cloister: long tables, lamps, a notice board and a door marked <em>Founder Office</em>. The room is fictional; the conversation it invites is real. For now it is text only.</p>

      <h2>From the founding charter</h2>
      <blockquote style={{ borderLeft: '2px solid var(--gold)', margin: 0, padding: '0.3rem 1rem' }}>
        <p className="luminous" style={{ fontSize: '1.2rem', margin: 0 }}>“Build the university itself. Its campus is the interface, mathematics is its choreography, and every visitor leaves with something they truly made.”</p>
        <p className="small muted" style={{ margin: '0.4rem 0 0' }}>— from the university’s constitutional prompt, written by its commissioner and co-founder, Abed Kadaan (21 October 2026).</p>
      </blockquote>

      <h2>The notice board</h2>
      <p className="small muted">Pin a note for yourself: a question to bring back, an idea for a harness. Notes stay in this browser and are never published.</p>
      <label htmlFor="note">A note</label>
      <textarea id="note" value={text} onChange={(e) => setText(e.target.value)} maxLength={800} />
      <div className="btn-row">
        <button
          className="btn primary"
          disabled={!text.trim()}
          onClick={() => {
            setState((s) => ({ ...s, notes: [{ text: text.trim(), at: new Date().toISOString() }, ...s.notes].slice(0, 50) }));
            setText('');
          }}
        >
          Pin note
        </button>
      </div>
      {notes.length ? (
        <ul>
          {notes.map((n, i) => (
            <li key={n.at + i}>
              {n.text} <span className="small muted">({new Date(n.at).toLocaleString()})</span>{' '}
              <button className="btn small" onClick={() => setState((s) => ({ ...s, notes: s.notes.filter((_, j) => j !== i) }))} aria-label="Remove note">
                ✕
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="small muted">The board is empty.</p>
      )}

      <h2>Questions and collaboration</h2>
      <p>Questions for the co-founders, proposals to collaborate, and errata in the founding works travel best as a written request: draft one in the <Link to="/harness-masters">Hall of Harness Masters</Link>. Errata and independent checks for Computational Grammar Theory have their own form inside <Link to="/library/computational-grammar-theory">the book</Link>.</p>

      <h2>Future invitations</h2>
      <p className="small">Planned, not yet open: human-led Harness Master sessions, reading circles around the founding works, and a public shelf of participant books (requires the optional cloud facility and each author’s consent). Nothing here is scheduled.</p>

      <h2>Residents in the room</h2>
      <p className="small muted">{FICTION_NOTE}</p>
      <div className="btn-row">
        {RESIDENTS.filter((r) => r.role !== 'Harness Master').map((r) => (
          <button key={r.id} className="btn" onClick={() => openResident(r.id)}>
            {r.name}
          </button>
        ))}
      </div>
    </article>
  );
}
