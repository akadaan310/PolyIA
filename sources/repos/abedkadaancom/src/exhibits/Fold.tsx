import { useMemo } from 'react';
import { foldOnce, grammarSize, startFold, unfoldAll } from '../math/fold';
import { recordExercise, updateWorld, useStore, type ExerciseRecord } from '../state/store';
import { foldRecord } from './records';
import { plateFor } from '../books/plates';
import { PlateSvg } from '../ui/PlateSvg';

export function FoldExhibit({ onRecord }: { onRecord?: (r: ExerciseRecord) => void }) {
  const word = useStore((s) => s.world.foldWord);
  const depth = useStore((s) => s.world.foldDepth);
  const st = useMemo(() => {
    let x = startFold(word);
    for (let i = 0; i < depth && x.current.length > 1; i++) x = foldOnce(x);
    return x;
  }, [word, depth]);
  const plate = useMemo(() => plateFor('fold', { ...foldRecord(word, 99), at: '' }), [word]);
  const ok = unfoldAll(st).join('') === word;
  return (
    <section aria-label="The Plicastratum Walkway exhibit">
      <label htmlFor="fold-word">A path word (letters such as N E S W)</label>
      <input id="fold-word" type="text" value={word} onChange={(e) => updateWorld({ foldWord: e.target.value.replace(/\s+/g, '').slice(0, 32), foldDepth: 0 })} />
      <p className="small muted">The atrium walkway is paved with this word. Each fold merges the most frequent adjacent pair into one glowing glyph (Re-Pair).</p>
      <div className="math-block" aria-live="polite">
        {[`stratum ${st.rules.length}: ${st.current.join(' ')}`, ...st.rules.map((r) => `${r.glyph} → ${r.left}${r.right}  (×${r.count})`), `grammar size = |w| + 2·rules = ${grammarSize(st)}`, `unfold(fold(w)) = w: ${ok ? '✓' : '✗'}`].join('\n')}
      </div>
      <div className="btn-row">
        <button className="btn" disabled={st.current.length < 2} onClick={() => updateWorld({ foldDepth: depth + 1 })}>
          Fold once
        </button>
        <button className="btn" disabled={depth === 0} onClick={() => updateWorld({ foldDepth: Math.max(0, depth - 1) })}>
          Unfold once
        </button>
        <button className="btn" onClick={() => updateWorld({ foldDepth: 99 })}>
          Fold to one glyph
        </button>
        <button className="btn primary" onClick={() => onRecord?.(recordExercise(foldRecord(word, st.rules.length)))}>
          Record this fold
        </button>
      </div>
      <figure className="figure">
        <PlateSvg plate={plate} />
        <figcaption>{plate.caption}</figcaption>
      </figure>
    </section>
  );
}
