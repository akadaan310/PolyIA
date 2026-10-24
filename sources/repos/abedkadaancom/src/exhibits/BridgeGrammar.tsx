import { useMemo, useState } from 'react';
import { DOORS, admissibleTransformation, applyTransformation, evaluateWord, DFA, INITIAL_BRIDGES, type BridgeType, type DoorId, type Transformation } from '../math/bridgeGrammar';
import { DIVISIONS } from '../content/registry';
import { recordExercise, updateWorld, useStore, type ExerciseRecord } from '../state/store';
import { bridgeRecord } from './records';
import { plateFor } from '../books/plates';
import { PlateSvg } from '../ui/PlateSvg';

const NAMES: Record<DoorId, string> = Object.fromEntries(DOORS.map((d, i) => [d, DIVISIONS[i]!.name])) as Record<DoorId, string>;

export function BridgeGrammarExhibit({ onRecord }: { onRecord?: (r: ExerciseRecord) => void }) {
  const bridges = useStore((s) => s.world.bridges);
  const [word, setWord] = useState('FRPG');
  const [op, setOp] = useState<'add' | 'remove'>('add');
  const [a, setA] = useState<DoorId>('P');
  const [b, setB] = useState<DoorId>('A');
  const [type, setType] = useState<BridgeType>('gold');
  const result = useMemo(() => evaluateWord(word, bridges), [word, bridges]);
  const t: Transformation = op === 'add' ? { op, a, b, type } : { op, a, b };
  const pred = admissibleTransformation(bridges, t);
  const plate = useMemo(() => plateFor('bridge-grammar', { ...bridgeRecord(word, bridges), at: '' }), [word, bridges]);

  const run = () => {
    const rec = recordExercise(bridgeRecord(word, bridges));
    onRecord?.(rec);
  };

  return (
    <section aria-label="The Bridge Grammar exhibit">
      <p className="small muted">
        Doors: {DOORS.map((d) => `${d} = ${NAMES[d]}`).join(' · ')}. A word is a walk such as <code>FRPG</code>. {DFA.description}
      </p>
      <label htmlFor="bg-word">Walk (door letters)</label>
      <input id="bg-word" type="text" value={word} onChange={(e) => setWord(e.target.value.toUpperCase().replace(/[^FRPGAW]/g, '').slice(0, 16))} inputMode="text" autoCapitalize="characters" />
      <div className="verdict" aria-live="polite">
        <span className={`lamp ${result.realizable ? 'on' : 'off'}`}>
          <i /> realizable
        </span>
        <span className={`lamp ${result.admissible ? 'on' : 'off'}`}>
          <i /> admissible
        </span>
        <div className="small" style={{ marginTop: 4 }}>{result.verdict}</div>
      </div>
      <div className="math-block">
        {['q₀ = 0', ...result.steps.map((s, i) => (s.bridge ? `${s.from}→${s.to}: ${s.bridge}; q${i + 1} = ${s.dfaState}${s.dfaState === 2 ? ' (dead)' : ''}` : `${s.from}→${s.to}: no bridge`))].join('\n')}
      </div>
      <figure className="figure">
        <PlateSvg plate={plate} />
        <figcaption>{plate.caption}</figcaption>
      </figure>
      <div className="btn-row">
        <button className="btn primary" onClick={run}>
          Record this walk
        </button>
      </div>

      <fieldset>
        <legend>Transform the bridges (typed admissibility predicate)</legend>
        <div className="btn-row" role="radiogroup" aria-label="operation">
          {(['add', 'remove'] as const).map((o) => (
            <label key={o} className="choice">
              <input type="radio" name="bg-op" checked={op === o} onChange={() => setOp(o)} /> {o}
            </label>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
          <div>
            <label htmlFor="bg-a">from</label>
            <select id="bg-a" value={a} onChange={(e) => setA(e.target.value as DoorId)}>
              {DOORS.map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="bg-b">to</label>
            <select id="bg-b" value={b} onChange={(e) => setB(e.target.value as DoorId)}>
              {DOORS.map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="bg-t">type</label>
            <select id="bg-t" value={type} onChange={(e) => setType(e.target.value as BridgeType)} disabled={op === 'remove'}>
              <option>gold</option>
              <option>stone</option>
            </select>
          </div>
        </div>
        <ul className="small">
          {pred.checks.map((c) => (
            <li key={c.name} style={{ color: c.ok ? '#b9d6b3' : '#f0b3bb' }}>
              {c.ok ? '✓' : '✗'} {c.name}: {c.detail}
            </li>
          ))}
        </ul>
        <div className="btn-row">
          <button className="btn" disabled={!pred.passes} onClick={() => updateWorld({ bridges: applyTransformation(bridges, t) })}>
            {pred.passes ? 'Apply (predicate passes)' : 'Refused by the predicate'}
          </button>
          <button className="btn" onClick={() => updateWorld({ bridges: INITIAL_BRIDGES })}>
            Restore original bridges
          </button>
        </div>
        <p className="small muted">The atrium’s bridges change only when the predicate passes. Every bridge you see in the 3D campus is this list.</p>
      </fieldset>
    </section>
  );
}
