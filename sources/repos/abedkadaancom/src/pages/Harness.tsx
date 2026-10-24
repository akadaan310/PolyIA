import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { DIVISIONS, division, topicsOf } from '../content/registry';
import type { DivisionId } from '../content/types';
import { Exhibit } from '../exhibits/Exhibit';
import { defaultHarness, getState, updateHarness, useStore, type Contribution, type StationRecord } from '../state/store';
import { cloudConfigured, cloudHost, sessionEmail, signInWithEmail, syncHarness, submitContribution } from '../lib/cloud';
import { hashString } from '../math/world';
import { Crumbs, Status, usePageTitle } from '../ui/bits';
import { NotFound } from './NotFound';

const PROMPTS: Record<DivisionId, string> = {
  foundations: 'In your own words: what is the difference between a walk being admissible and being realizable? Give one example from the bridges.',
  relational: 'What did folding your path move into the rules, and why can nothing be lost?',
  languages: 'Write an address that the loom refuses, and explain which state the machine was in when it refused.',
  geometry: 'Describe something in your daily life that is a projection. What is its kernel: what does it forget?',
  acoustic: 'Why do some intervals light every arch and others only a few? Use the word gcd if you can.',
  worlds: 'Name a fact in a world (real or imagined) that many others depend on. What would go dark without it?',
};

export function stationOrder(interest: DivisionId | null): DivisionId[] {
  const ids = DIVISIONS.map((d) => d.id);
  if (!interest) return ids;
  return [interest, ...ids.filter((i) => i !== interest)];
}

/** The reading at each station: the topic the station's exhibit computes most directly. */
const HARNESS_TOPIC: Record<DivisionId, string> = {
  foundations: 'operational-grammar',
  relational: 'plicastratum',
  languages: 'compilation',
  geometry: 'image-kernel',
  acoustic: 'interval-geometry',
  worlds: 'world-loom',
};

function signatureTopic(id: DivisionId) {
  return topicsOf(id).find((t) => t.id === HARNESS_TOPIC[id]) ?? topicsOf(id)[0]!;
}

export function HarnessHome() {
  usePageTitle('The One-Day Harness');
  const h = useStore((s) => s.harness);
  const navigate = useNavigate();
  const [name, setName] = useState(h.displayName ?? '');
  const [priv, setPriv] = useState(h.startedAt ? h.displayName === null : false);
  const [storage, setStorage] = useState<'local' | 'cloud'>(h.storage);
  const [interest, setInterest] = useState<DivisionId | ''>(h.interest ?? '');
  const [email, setEmail] = useState('');
  const [cloudMsg, setCloudMsg] = useState<string | null>(null);
  const [signedIn, setSignedIn] = useState<string | null>(null);
  useEffect(() => {
    if (cloudConfigured) sessionEmail().then(setSignedIn, () => setSignedIn(null));
  }, []);
  const order = stationOrder(h.interest);
  const done = order.filter((d) => h.stations[d]?.completedAt).length;

  if (!h.startedAt) {
    return (
      <article>
        <Crumbs items={[['Campus', '/'], ['One-Day Harness']]} />
        <h1>The One-Day Harness</h1>
        <p>A free, self-paced day across the six divisions. At each station you read a short lesson, run a real exhibit, and write a reflection. At the end you make one contribution of your own, and the Scriptorium typesets <strong>six books, one per division</strong>, credited to the name you choose.</p>
        <p className="small muted">It is a guided learning and making experience. It is not a degree, an attendance credential, an appointment, or a claim that six fields have been mastered. Pause any time: progress stays in this browser.</p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const now = new Date().toISOString();
            updateHarness({
              ...defaultHarness(),
              runId: `run-${hashString(now + Math.random()).toString(36)}`,
              startedAt: now,
              displayName: priv ? null : name.trim().slice(0, 60) || null,
              storage,
              interest: interest || null,
            });
          }}
        >
          <fieldset>
            <legend>How should your books be credited?</legend>
            <label className="choice">
              <input type="radio" name="priv" checked={!priv} onChange={() => setPriv(false)} /> With a public display name
            </label>
            {!priv ? (
              <>
                <label htmlFor="hn">Display name (as it will appear on your books)</label>
                <input id="hn" type="text" value={name} onChange={(e) => setName(e.target.value)} maxLength={60} autoComplete="nickname" />
              </>
            ) : null}
            <label className="choice">
              <input type="radio" name="priv" checked={priv} onChange={() => setPriv(true)} /> Remain private (books credited to “A Private Harnesser”)
            </label>
          </fieldset>
          <fieldset>
            <legend>Where should progress be kept?</legend>
            <label className="choice">
              <input type="radio" name="st" checked={storage === 'local'} onChange={() => setStorage('local')} /> Only in this browser (default)
            </label>
            <label className="choice">
              <input type="radio" name="st" checked={storage === 'cloud'} onChange={() => setStorage('cloud')} disabled={!cloudConfigured} /> Also sync to the university’s cloud {cloudConfigured ? `(${cloudHost}; requires an email sign-in)` : '— not configured on this deployment'}
            </label>
          </fieldset>
          <label htmlFor="interest">Your intellectual interest (the harness begins there)</label>
          <select id="interest" value={interest} onChange={(e) => setInterest(e.target.value as DivisionId)}>
            <option value="">No preference</option>
            {DIVISIONS.map((d) => (
              <option key={d.id} value={d.id}>
                {d.numeral}. {d.name}
              </option>
            ))}
          </select>
          <div className="btn-row">
            <button className="btn primary" type="submit" disabled={!priv && name.trim() === ''}>
              Enter the harness
            </button>
          </div>
        </form>
      </article>
    );
  }

  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['One-Day Harness']]} />
      <h1>Your One-Day Harness</h1>
      <p>
        Harnesser: <strong>{h.displayName ?? 'A Private Harnesser'}</strong> · started {new Date(h.startedAt).toLocaleString()} · {done} of 6 stations complete · storage: {h.storage === 'cloud' ? 'this browser + cloud' : 'this browser only'}
      </p>
      <ol className="path">
        {order.map((id) => {
          const d = division(id)!;
          const st = h.stations[id];
          return (
            <li key={id}>
              <Link to={`/harness/${id}`}>
                {d.numeral}. {d.name}
              </Link>{' '}
              <span className="tag">{st?.completedAt ? (st.exercise ? 'complete · exercised' : 'complete · visited') : st ? 'in progress' : 'not started'}</span>
            </li>
          );
        })}
      </ol>
      {done === 6 ? <Contribute /> : <p className="small muted">Complete all six stations, then add your contribution to finish the day.</p>}
      {h.completedAt ? (
        <div className="notice gold">
          Your harness is complete. <Link to="/scriptorium">Go to the Scriptorium</Link> to read and download your six books.
        </div>
      ) : null}
      {h.storage === 'cloud' && cloudConfigured ? (
        <fieldset>
          <legend>Cloud sync</legend>
          {signedIn ? (
            <>
              <p className="small">Signed in as {signedIn}.</p>
              <button className="btn" onClick={() => syncHarness(getState().harness).then(() => setCloudMsg('Synced.'), (e: Error) => setCloudMsg(e.message))}>
                Sync progress now
              </button>
            </>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); signInWithEmail(email).then(() => setCloudMsg('Check your email for a sign-in link.'), (err: Error) => setCloudMsg(err.message)); }}>
              <label htmlFor="em">Email for a one-time sign-in link</label>
              <input id="em" type="text" inputMode="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <button className="btn" type="submit">Send link</button>
            </form>
          )}
          {cloudMsg ? <p className="small">{cloudMsg}</p> : null}
        </fieldset>
      ) : null}
      <div className="btn-row">
        <button className="btn" onClick={() => { if (confirm('Start a new harness? Your current stations will be cleared from this browser.')) { updateHarness(defaultHarness()); navigate('/harness'); } }}>
          Start over
        </button>
      </div>
    </article>
  );
}

function Contribute() {
  const h = useStore((s) => s.harness);
  const navigate = useNavigate();
  const [kind, setKind] = useState<Contribution['kind']>(h.contribution?.kind ?? 'example');
  const [term, setTerm] = useState(h.contribution?.term ?? '');
  const [text, setText] = useState(h.contribution?.text ?? '');
  const [msg, setMsg] = useState<string | null>(null);
  return (
    <fieldset>
      <legend>Your contribution to the university</legend>
      <p className="small">Offer one thing of your own: an example, a new sense for a glossary term, or a question for a future harness. It appears in your interest volume, credited to you.</p>
      <label htmlFor="ck">Kind</label>
      <select id="ck" value={kind} onChange={(e) => setKind(e.target.value as Contribution['kind'])}>
        <option value="example">An example</option>
        <option value="glossary-sense">A glossary sense</option>
        <option value="question">A question</option>
      </select>
      <label htmlFor="ct">Term it concerns (optional)</label>
      <input id="ct" type="text" value={term} onChange={(e) => setTerm(e.target.value)} maxLength={60} />
      <label htmlFor="cx">Your contribution</label>
      <textarea id="cx" value={text} onChange={(e) => setText(e.target.value)} maxLength={2000} />
      <div className="btn-row">
        <button
          className="btn primary"
          disabled={text.trim().length < 10}
          onClick={() => {
            const c: Contribution = { kind, term: term.trim(), text: text.trim(), at: new Date().toISOString() };
            updateHarness({ contribution: c, completedAt: new Date().toISOString() });
            if (h.storage === 'cloud' && cloudConfigured) submitContribution(c).catch((e: Error) => setMsg(`Saved locally; cloud submission failed: ${e.message}`));
            navigate('/scriptorium');
          }}
        >
          Complete the harness and go to the Scriptorium
        </button>
      </div>
      {msg ? <p className="small">{msg}</p> : null}
    </fieldset>
  );
}

export function HarnessStation() {
  const { division: did = '' } = useParams();
  const d = division(did);
  const h = useStore((s) => s.harness);
  const navigate = useNavigate();
  usePageTitle(d ? `Harness · ${d.name}` : 'Not found');
  const st = d ? h.stations[d.id] : undefined;
  const [reflection, setReflection] = useState(st?.reflection ?? '');
  useEffect(() => {
    if (!d || !h.startedAt || st) return;
    const rec: StationRecord = { division: d.id, topicId: signatureTopic(d.id).id, enteredAt: new Date().toISOString(), exercise: null, reflection: '', completedAt: null };
    updateHarness((x) => ({ stations: { ...x.stations, [d.id]: rec } }));
  }, [d, h.startedAt, st]);
  if (!d) return <NotFound />;
  if (!h.startedAt) {
    return (
      <article>
        <h1>{d.name}</h1>
        <p>
          This is a harness station. <Link to="/harness">Enter the One-Day Harness</Link> first, or explore <Link to={`/divisions/${d.id}`}>the division</Link> freely.
        </p>
      </article>
    );
  }
  const t = signatureTopic(d.id);
  const order = stationOrder(h.interest);
  const next = order[order.indexOf(d.id) + 1];
  return (
    <article>
      <Crumbs items={[['Harness', '/harness'], [`Station ${order.indexOf(d.id) + 1} of 6`]]} />
      <p className="engraved small" style={{ color: d.accent }}>
        {d.numeral} · {d.door}
      </p>
      <h1>{d.name}</h1>
      <h2>Reading · {t.title}</h2>
      <p>
        <Status s={t.status} />
      </p>
      <p>{t.summary}</p>
      {t.definitions.slice(0, 2).map((x) => (
        <div key={x.term} className="def">
          <b>{x.term}</b> <Status s={x.status} />
          <div>{x.text}</div>
        </div>
      ))}
      <p className="small">
        <Link to={`/divisions/${d.id}/${t.id}`}>Read the full lesson</Link>
      </p>
      <h2>Exercise · {d.exhibitTitle}</h2>
      {st?.exercise ? <div className="verdict ok small">Recorded: {st.exercise.headline} You can run it again; the latest recording is kept.</div> : <p className="small muted">Run the exhibit and press its “Record” button. Your inputs and the computed result become Chapter IV of your {d.name} volume.</p>}
      <Exhibit id={d.exhibit} onRecord={(rec) => updateHarness((x) => ({ stations: { ...x.stations, [d.id]: { ...(x.stations[d.id] as StationRecord), exercise: rec } } }))} />
      <h2>Reflection</h2>
      <label htmlFor="refl">{PROMPTS[d.id]}</label>
      <textarea id="refl" value={reflection} onChange={(e) => setReflection(e.target.value)} onBlur={() => updateHarness((x) => ({ stations: { ...x.stations, [d.id]: { ...(x.stations[d.id] as StationRecord), reflection } } }))} maxLength={3000} />
      <div className="btn-row">
        <button
          className="btn primary"
          onClick={() => {
            updateHarness((x) => ({ stations: { ...x.stations, [d.id]: { ...(x.stations[d.id] as StationRecord), reflection, completedAt: new Date().toISOString() } } }));
            navigate(next ? `/harness/${next}` : '/harness');
          }}
        >
          Complete this station{next ? ` · next: ${division(next)!.name}` : ' · return to the harness'}
        </button>
      </div>
      <p className="small muted">Your words are stored only in this browser{h.storage === 'cloud' ? ' (and synced when you choose to)' : ''}. They appear verbatim in your book.</p>
    </article>
  );
}
