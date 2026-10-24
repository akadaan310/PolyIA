import { useMemo, useState } from 'react';
import { downstream, ruleTable, topologicalOrder, weave, WORLD_FACTS, density } from '../math/world';
import { recordExercise, updateWorld, useStore, type ExerciseRecord } from '../state/store';
import { loomRecord } from './records';
import { plateFor } from '../books/plates';
import { PlateSvg } from '../ui/PlateSvg';

export function WorldLoomExhibit({ onRecord }: { onRecord?: (r: ExerciseRecord) => void }) {
  const rule = useStore((s) => s.world.loomRule);
  const [removed, setRemoved] = useState<string | null>(null);
  const grid = useMemo(() => weave(rule, 31, 16), [rule]);
  const lost = removed ? downstream(WORLD_FACTS, removed) : [];
  const order = topologicalOrder(WORLD_FACTS)!;
  const plate = useMemo(() => plateFor('world-loom', { ...loomRecord(rule), at: '' }), [rule]);
  return (
    <section aria-label="The World Loom exhibit">
      <label htmlFor="rule">Rule (0–255): {rule}</label>
      <input id="rule" type="range" min={0} max={255} value={rule} onChange={(e) => updateWorld({ loomRule: Number(e.target.value) })} />
      <div className="btn-row">
        {[30, 90, 110, 184, 204].map((r) => (
          <button key={r} className="btn small" onClick={() => updateWorld({ loomRule: r })}>
            rule {r}
          </button>
        ))}
      </div>
      <div className="math-block" aria-live="polite">
        {[`${rule} = ${rule.toString(2).padStart(8, '0')}₂`, ruleTable(rule).map((r) => `${r.neighbourhood}→${r.out}`).join('  '), `density of the cloth: ${(density(grid) * 100).toFixed(1)}%`].join('\n')}
      </div>
      <figure className="figure">
        <PlateSvg plate={plate} />
        <figcaption>{plate.caption}</figcaption>
      </figure>
      <fieldset>
        <legend>BORNE: what must be born before what</legend>
        <p className="small">One valid birth order (Kahn): {order.join(' → ')}</p>
        <label htmlFor="borne">Remove a fact</label>
        <select id="borne" value={removed ?? ''} onChange={(e) => setRemoved(e.target.value || null)}>
          <option value="">(none)</option>
          {WORLD_FACTS.nodes.map((n) => (
            <option key={n}>{n}</option>
          ))}
        </select>
        <p className="small" aria-live="polite">
          {removed ? (lost.length ? `Removing ${removed} leaves without a cause: ${lost.join(', ')}.` : `Nothing depends on ${removed}.`) : 'Choose a fact to see its downstream.'}
        </p>
      </fieldset>
      <div className="btn-row">
        <button className="btn primary" onClick={() => onRecord?.(recordExercise(loomRecord(rule, removed)))}>
          Record this world
        </button>
      </div>
    </section>
  );
}
