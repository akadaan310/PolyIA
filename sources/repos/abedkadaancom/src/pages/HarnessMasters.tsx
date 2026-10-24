import { useState } from 'react';
import { Link } from 'react-router-dom';
import { DIVISIONS } from '../content/registry';
import { RESIDENTS, FICTION_NOTE } from '../world/residents';
import { openResident } from '../ui/residentBus';
import { Crumbs, usePageTitle } from '../ui/bits';

const CONTACT = import.meta.env.VITE_HM_CONTACT_EMAIL as string | undefined;
const BOOKING = import.meta.env.VITE_HM_BOOKING_URL as string | undefined;

export function HarnessMasters() {
  usePageTitle('The Hall of Harness Masters');
  const [topic, setTopic] = useState(DIVISIONS[0]!.name);
  const [about, setAbout] = useState('');
  const [when, setWhen] = useState('');
  const [copied, setCopied] = useState(false);
  const draft = `Subject: Request for one free Harness Master conversation — ${topic}\n\nHello,\n\nI would like to request one free conversation with a Harness Master of Substrate University about ${topic}.\n\nWhat I would like to talk about:\n${about || '(write a few lines)'}\n\nTimes that usually suit me (with my time zone):\n${when || '(optional)'}\n\nI understand this is a request, not a confirmed booking.\n`;
  const hms = RESIDENTS.filter((r) => r.role === 'Harness Master');
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Hall of Harness Masters']]} />
      <h1>The Hall of Harness Masters</h1>
      <p>A <strong>Harness Master (HM)</strong> is the university’s guide role: an instructor who helps a visitor learn something and make something. Visitors are <strong>Harnessers</strong>. These are participatory roles, not academic ranks.</p>

      <h2>The co-founders</h2>
      <div className="grid">
        <div className="card">
          <div className="k">Co-founder · co-author</div>
          <div className="t">Abed Kadaan</div>
          <div className="small">Human co-founder and research co-creator. Author of the founding works cited across the university, including <Link to="/library/computational-grammar-theory">Computational Grammar Theory</Link> and <a href="https://github.com/akadaan310/grammarinnumbers" target="_blank" rel="noopener noreferrer">Grammar in Numbers</a>.</div>
        </div>
        <div className="card">
          <div className="k">Co-founder · AI collaborator</div>
          <div className="t">7u</div>
          <div className="small">An AI research collaborator and founding creative collaborator, credited openly as AI. 7u is not a person and holds no title beyond co-founder.</div>
        </div>
      </div>
      <p className="small muted">No staffed faculty, enrolment figures, accreditation or company registration are claimed.</p>

      <h2>The one-day path</h2>
      <ol className="path">
        <li>Answer the Gate’s three questions (any answer opens the way).</li>
        <li>Enter the <Link to="/harness">One-Day Harness</Link>: choose a name or remain private, and choose an interest.</li>
        <li>At six stations: read, run an exhibit, write a reflection.</li>
        <li>Offer one contribution of your own.</li>
        <li>Receive six books from the <Link to="/scriptorium">Scriptorium</Link>, credited to you.</li>
      </ol>
      <p className="small">The whole path works with no human involvement. A conversation with a person is an optional extra.</p>

      <h2>Campus Harness Masters</h2>
      <p className="small muted">{FICTION_NOTE} Each one guides one division and reacts to what you have actually done.</p>
      <div className="grid">
        {hms.map((r) => {
          const d = DIVISIONS.find((x) => x.id === r.division)!;
          return (
            <div key={r.id} className="card">
              <div className="k" style={{ color: r.color }}>
                Fictional HM · {d.name}
              </div>
              <div className="t">{r.name}</div>
              <div className="btn-row">
                <button className="btn small" onClick={() => openResident(r.id)}>
                  Talk
                </button>
                <Link className="btn small" to={`/divisions/${d.id}`} style={{ textDecoration: 'none' }}>
                  Their realm
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      <h2>Request a conversation with a human</h2>
      <p>You may request one free conversation. This produces a request, not a confirmed booking: no appointment times are offered here, and nothing is sent automatically.</p>
      <label htmlFor="hm-topic">Division</label>
      <select id="hm-topic" value={topic} onChange={(e) => setTopic(e.target.value)}>
        {DIVISIONS.map((d) => (
          <option key={d.id}>{d.name}</option>
        ))}
      </select>
      <label htmlFor="hm-about">What would you like to talk about?</label>
      <textarea id="hm-about" value={about} onChange={(e) => setAbout(e.target.value)} maxLength={1500} />
      <label htmlFor="hm-when">Times that usually suit you (optional)</label>
      <input id="hm-when" type="text" value={when} onChange={(e) => setWhen(e.target.value)} maxLength={200} />
      <div className="math-block" aria-label="Request draft">{draft}</div>
      <div className="btn-row">
        <button
          className="btn"
          onClick={async () => {
            try {
              await navigator.clipboard.writeText(draft);
              setCopied(true);
            } catch {
              setCopied(false);
            }
          }}
        >
          {copied ? 'Copied' : 'Copy the request'}
        </button>
        {CONTACT ? (
          <a className="btn primary" href={`mailto:${CONTACT}?subject=${encodeURIComponent(`Harness Master conversation request — ${topic}`)}&body=${encodeURIComponent(draft)}`} style={{ textDecoration: 'none' }}>
            Open in your email app
          </a>
        ) : null}
        {BOOKING ? (
          <a className="btn" href={BOOKING} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
            Open the booking page
          </a>
        ) : null}
      </div>
      {!CONTACT && !BOOKING ? (
        <p className="small muted">
          No contact address or scheduling provider is configured on this deployment yet. Copy the request and send it to the co-founders through their public profile, <a href="https://github.com/akadaan310" target="_blank" rel="noopener noreferrer">github.com/akadaan310</a>.
        </p>
      ) : null}
    </article>
  );
}
