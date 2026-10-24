import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { DIVISIONS, division, topic, topicsOf, EPISTEMIC_LABELS } from '../content/registry';
import { findTerm, termSlug } from '../content/glossary';
import { Exhibit } from '../exhibits/Exhibit';
import { runCompute } from '../exhibits/compute';
import { useStore } from '../state/store';
import { analyseInterval } from '../math/music';
import { RESIDENTS, residentLocation } from '../world/residents';
import { openResident } from '../ui/residentBus';
import { Crumbs, SourceList, Status, usePageTitle } from '../ui/bits';
import { NotFound } from './NotFound';

export function Atrium() {
  usePageTitle('The Atrium of Six Divisions');
  const w = useStore((s) => s.world);
  const hour = new Date().getHours();
  const present = RESIDENTS.filter((r) => residentLocation(r, hour) === 'atrium');
  const iv = analyseInterval(w.interval);
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Atrium']]} />
      <h1>The Atrium of Six Divisions</h1>
      <p>Six doors stand around the atrium, each opening a realm. The court itself is a working instrument: its bridges, walkway, arches and frieze are computed from the state of the exhibits.</p>
      <div className="grid">
        {DIVISIONS.map((d) => (
          <Link key={d.id} className="card" to={`/divisions/${d.id}`} style={{ borderColor: w.visited.includes(`division:${d.id}`) ? d.accent : undefined }}>
            <div className="k" style={{ color: d.accent }}>
              {d.numeral} · {d.door}
            </div>
            <div className="t">{d.name}</div>
            <div className="small muted">{w.visited.includes(`division:${d.id}`) ? 'Door open' : 'Door closed: visit to open'}</div>
          </Link>
        ))}
      </div>
      <h2>The court’s present state</h2>
      <table className="data">
        <tbody>
          <tr><th>Bridges</th><td>{w.bridges.length} ({w.bridges.filter((b) => b.type === 'gold').length} gold): {w.bridges.map((b) => `${b.a}–${b.b}`).join(', ')}. Change them in <Link to="/divisions/foundations">Foundations</Link>.</td></tr>
          <tr><th>Walkway</th><td><code>{w.foldWord}</code>, folded {Math.min(w.foldDepth, w.foldWord.length)} time(s). Fold it in <Link to="/divisions/relational">Relational</Link>.</td></tr>
          <tr><th>Arches</th><td>{iv.orbitLength} of 12 lit: interval {iv.k} ({iv.name}). Tune them in <Link to="/divisions/acoustic">Acoustic</Link>.</td></tr>
          <tr><th>Sculpture</th><td>{w.sculpture ? `the image of ${JSON.stringify(w.sculpture)}` : 'none yet: accept a matrix at the Gate or in Geometry'}</td></tr>
          <tr><th>Portal</th><td>{w.portal ? `fictional portal for a ${(w.portal.similarity * 100).toFixed(0)}% path correspondence (${w.portal.mode})` : 'closed: find a path correspondence in the Observatory'}</td></tr>
        </tbody>
      </table>
      <h2>Who is here now</h2>
      <p className="small muted">Fictional residents keep schedules by your local clock ({hour}:00). Select one in the 3D court or here.</p>
      <div className="btn-row">
        {(present.length ? present : RESIDENTS.slice(0, 3)).map((r) => (
          <button key={r.id} className="btn" onClick={() => openResident(r.id)}>
            {r.name}
          </button>
        ))}
      </div>
    </article>
  );
}

export function DivisionPage() {
  const { id = '' } = useParams();
  const d = division(id);
  usePageTitle(d ? d.name : 'Not found');
  if (!d) return <NotFound />;
  const topics = topicsOf(d.id);
  const terms = [...new Set(topics.flatMap((t) => t.glossary))].map((g) => findTerm(g)).filter(Boolean);
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Atrium', '/atrium'], [d.name]]} />
      <p className="engraved small" style={{ color: d.accent }}>
        Division {d.numeral} · {d.door}
      </p>
      <h1>{d.name}</h1>
      <p className="luminous" style={{ fontSize: '1.15rem' }}>{d.motto}</p>
      <p>{d.description}</p>

      <h2>Signature exhibit · {d.exhibitTitle}</h2>
      <p className="small muted">This exhibit computes in your browser and changes the realm behind the door{d.id === 'foundations' || d.id === 'relational' || d.id === 'acoustic' ? ' and the atrium itself' : ''}.</p>
      <Exhibit id={d.exhibit} />

      <h2>Curriculum path</h2>
      <ol className="path">
        {topics.map((t) => (
          <li key={t.id}>
            <Link to={`/divisions/${d.id}/${t.id}`}>{t.title}</Link> <span className="tag">{t.level}</span> <Status s={t.status} />
          </li>
        ))}
      </ol>
      <h2>Glossary of this division</h2>
      <p>
        {terms.map((t) => (
          <Link key={t!.id} to={`/glossary/${termSlug(t!.id)}`} className="tag" style={{ textDecoration: 'none' }}>
            {t!.term}
          </Link>
        ))}
      </p>
    </article>
  );
}

export function TopicPage() {
  const { id = '', topic: tid = '' } = useParams();
  const t = topic(tid);
  const d = division(id);
  const [reveal, setReveal] = useState(false);
  usePageTitle(t ? t.title : 'Not found');
  if (!t || !d || t.division !== d.id) return <NotFound />;
  const idx = d.curriculum.indexOf(t.id);
  const next = d.curriculum[idx + 1];
  return (
    <article>
      <Crumbs items={[['Campus', '/'], [d.name, `/divisions/${d.id}`], [t.subject]]} />
      <p>
        <Status s={t.status} /> <span className="tag">{t.level}</span> <span className="tag">source: {t.sourceStatus.replace('-', ' ')}</span>
      </p>
      <h1>{t.title}</h1>
      <p>{t.summary}</p>
      <p className="small muted">{EPISTEMIC_LABELS[t.status].description}</p>
      <h2>Definitions</h2>
      {t.definitions.map((x) => (
        <div key={x.term} className="def">
          <b>{x.term}</b> <Status s={x.status} />
          <div>{x.text}</div>
        </div>
      ))}
      {t.constraints.length ? (
        <>
          <h2>Constraints and limits</h2>
          <ul>{t.constraints.map((c) => <li key={c}>{c}</li>)}</ul>
        </>
      ) : null}
      <h2>Examples</h2>
      {t.examples.map((e) => (
        <div key={e.title} className="def">
          <b>{e.title}.</b> {e.body}
          {e.compute ? <div className="math-block">{runCompute(e.compute).join('\n')}</div> : null}
        </div>
      ))}
      {t.prerequisites.length ? (
        <>
          <h2>Before this</h2>
          <ul>
            {t.prerequisites.map((p) => {
              const pt = topic(p)!;
              return (
                <li key={p}>
                  <Link to={`/divisions/${pt.division}/${pt.id}`}>{pt.title}</Link>
                </li>
              );
            })}
          </ul>
        </>
      ) : null}
      {t.transformations.length ? (
        <>
          <h2>Transformations studied</h2>
          <p>{t.transformations.join(' · ')}</p>
        </>
      ) : null}
      <h2>In the campus</h2>
      <p>{t.visualLesson}</p>
      {t.domainAdapter ? (
        <p>
          <Link to={`/divisions/${d.id}`}>Run the {d.exhibitTitle}</Link>{t.domainAdapter !== d.exhibit ? ` (this topic also uses the ${t.domainAdapter} adapter, found in another division)` : ''}.
        </p>
      ) : null}
      <h2>Challenge</h2>
      <p>{t.challenge.prompt}</p>
      <p className="small muted">Hint: {t.challenge.hint}</p>
      {reveal ? <div className="verdict ok">{t.challenge.answer}</div> : <button className="btn" onClick={() => setReveal(true)}>Show the answer</button>}
      <h2>Glossary</h2>
      <p>
        {t.glossary.map((g) => (
          <Link key={g} className="tag" style={{ textDecoration: 'none' }} to={`/glossary/${termSlug(g)}`}>
            {findTerm(g)?.term ?? g}
          </Link>
        ))}
      </p>
      <h2>Sources</h2>
      <SourceList sources={t.sources} />
      {next ? (
        <p>
          Next on the path: <Link to={`/divisions/${d.id}/${next}`}>{topic(next)!.title}</Link>
        </p>
      ) : null}
    </article>
  );
}
