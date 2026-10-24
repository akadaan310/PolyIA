import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { BRIDGES, DOMAIN_LABELS, TERMS, bridge, termFromSlug, termSlug, type Bridge, type Domain } from '../content/glossary';
import { topic } from '../content/registry';
import { Crumbs, Status, usePageTitle } from '../ui/bits';
import { NotFound } from './NotFound';

function BridgeRunner({ b }: { b: Bridge }) {
  const [input, setInput] = useState(b.defaultInput);
  const out = b.run(input);
  return (
    <div className="def">
      <b>{b.title}</b> <span className="tag">computable bridge</span>
      <p className="small">{b.explanation}</p>
      <label htmlFor={`br-${b.id}`}>{b.inputLabel}</label>
      <input id={`br-${b.id}`} type="text" value={input} onChange={(e) => setInput(e.target.value.slice(0, 120))} />
      <div className="math-block" aria-live="polite">{out.join('\n')}</div>
    </div>
  );
}

export function Glossary() {
  usePageTitle('The Glossary Field');
  const [ctx, setCtx] = useState<Domain | 'all'>('all');
  const [q, setQ] = useState('');
  const terms = TERMS.filter((t) => (ctx === 'all' || t.senses.some((s) => s.domain === ctx)) && t.term.toLowerCase().includes(q.toLowerCase())).sort((a, b) => b.senses.length - a.senses.length || a.term.localeCompare(b.term));
  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Glossary']]} />
      <h1>The Glossary Field</h1>
      <p>This glossary is the school’s memory, organized as a field rather than a list: one word can mean different things in different divisions. Choose an active context to see the senses that apply there. Where a computation connects two senses, the bridge runs here.</p>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <div>
          <label htmlFor="ctx">Active context</label>
          <select id="ctx" value={ctx} onChange={(e) => setCtx(e.target.value as Domain | 'all')}>
            <option value="all">All contexts</option>
            {(Object.keys(DOMAIN_LABELS) as Domain[]).map((d) => (
              <option key={d} value={d}>
                {DOMAIN_LABELS[d]}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="gq">Find a term</label>
          <input id="gq" type="text" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
      </div>
      <p className="small muted">{terms.length} terms · {terms.filter((t) => t.senses.length > 1).length} with several senses · {BRIDGES.length} computable bridges</p>
      <div className="grid">
        {terms.map((t) => {
          const sense = ctx === 'all' ? t.senses[0]! : t.senses.find((s) => s.domain === ctx)!;
          return (
            <Link key={t.id} className="card" to={`/glossary/${termSlug(t.id)}`}>
              <div className="k">{t.senses.length > 1 ? `${t.senses.length} senses` : DOMAIN_LABELS[sense.domain]}</div>
              <div className="t">{t.term}</div>
              <div className="small muted">{sense.text.slice(0, 110)}{sense.text.length > 110 ? '…' : ''}</div>
            </Link>
          );
        })}
      </div>
      <h2>Computable bridges</h2>
      {BRIDGES.map((b) => (
        <BridgeRunner key={b.id} b={b} />
      ))}
    </article>
  );
}

export function GlossaryTerm() {
  const { term = '' } = useParams();
  const t = termFromSlug(term);
  usePageTitle(t ? `${t.term} · Glossary` : 'Not found');
  if (!t) return <NotFound />;
  return (
    <article>
      <Crumbs items={[['Glossary', '/glossary'], [t.term]]} />
      <h1>{t.term}</h1>
      <p className="small muted">{t.senses.length} sense{t.senses.length === 1 ? '' : 's'}, each attributed to a context. The mathematics of each sense is unchanged by choosing another; only the context changes.</p>
      {t.senses.map((s, i) => {
        const tp = s.topic ? topic(s.topic) : undefined;
        return (
          <div key={i} className="def">
            <b>{DOMAIN_LABELS[s.domain]}</b> <Status s={s.status} />
            <div>{s.text}</div>
            {tp ? (
              <div className="small">
                Lesson: <Link to={`/divisions/${tp.division}/${tp.id}`}>{tp.title}</Link>
              </div>
            ) : null}
          </div>
        );
      })}
      {(t.bridges ?? []).map((id) => {
        const b = bridge(id);
        return b ? <BridgeRunner key={id} b={b} /> : null;
      })}
      {t.related.length ? (
        <>
          <h2>Nearby in the field</h2>
          <p>
            {t.related.map((r) => (
              <Link key={r} className="tag" style={{ textDecoration: 'none' }} to={`/glossary/${termSlug(r)}`}>
                {r}
              </Link>
            ))}
          </p>
        </>
      ) : null}
    </article>
  );
}
