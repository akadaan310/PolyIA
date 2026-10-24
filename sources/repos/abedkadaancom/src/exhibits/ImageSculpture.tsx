import { useMemo, useState } from 'react';
import { analyse, fmtVec, mat, preimage, vec } from '../math/matrix';
import { recordExercise, updateWorld, useStore, type ExerciseRecord } from '../state/store';
import { imageRecord } from './records';
import { plateFor } from '../books/plates';
import { PlateSvg } from '../ui/PlateSvg';

const PRESETS: { name: string; m: number[][] }[] = [
  { name: 'Floor projection', m: [[1, 0, 0], [0, 1, 0], [0, 0, 0]] },
  { name: 'Rotation (invertible)', m: [[0, -1, 0], [1, 0, 0], [0, 0, 1]] },
  { name: 'Line crush', m: [[1, 2, 3], [2, 4, 6], [1, 2, 3]] },
  { name: 'Shear', m: [[1, 1, 0], [0, 1, 0], [0, 0, 1]] },
  { name: 'Zero map', m: [[0, 0, 0], [0, 0, 0], [0, 0, 0]] },
  { name: '2×2 singular', m: [[1, 2], [2, 4]] },
];

export function MatrixEditor({ m, onChange }: { m: number[][]; onChange: (m: number[][]) => void }) {
  return (
    <div className="matrix-input" style={{ gridTemplateColumns: `repeat(${m[0]!.length}, auto)` }} role="group" aria-label="matrix entries">
      {m.map((row, i) =>
        row.map((v, j) => (
          <input
            key={`${i}-${j}`}
            type="number"
            step={1}
            min={-9}
            max={9}
            value={v}
            aria-label={`row ${i + 1} column ${j + 1}`}
            onChange={(e) => {
              const n = Math.max(-9, Math.min(9, Math.trunc(Number(e.target.value) || 0)));
              onChange(m.map((r, a) => r.map((x, b) => (a === i && b === j ? n : x))));
            }}
          />
        )),
      )}
    </div>
  );
}

export function ImageSculptureExhibit({ onRecord }: { onRecord?: (r: ExerciseRecord) => void }) {
  const stored = useStore((s) => s.world.sculpture);
  const [m, setM] = useState<number[][]>(stored ?? PRESETS[0]!.m);
  const n = m[0]!.length;
  const [target, setTarget] = useState<number[]>(n === 3 ? [1, 2, 0] : [3, 6]);
  const a = useMemo(() => analyse(mat(m)), [m]);
  const t = target.length === m.length ? target : Array.from({ length: m.length }, (_, i) => target[i] ?? 0);
  const pre = useMemo(() => preimage(mat(m), vec(t)), [m, t]);
  const plate = useMemo(() => plateFor('image-sculpture', { ...imageRecord(m), at: '' }), [m]);
  return (
    <section aria-label="The Image Sculpture exhibit">
      <div className="btn-row">
        {PRESETS.map((p) => (
          <button key={p.name} className="btn small" onClick={() => { setM(p.m); setTarget(p.m.length === 3 ? [1, 2, 0] : [3, 6]); }}>
            {p.name}
          </button>
        ))}
      </div>
      <MatrixEditor m={m} onChange={setM} />
      <div className="math-block" aria-live="polite">
        {[`rank A = ${a.rank}   dim ker A = ${a.nullity}   (rank + nullity = ${a.rank + a.nullity} = n)`, a.determinant !== null ? `det A = ${a.determinant}` : '', `im A = span{${a.image.map((v) => `(${fmtVec(v)})`).join(', ') || '∅'}}`, `ker A = span{${a.kernel.map((v) => `(${fmtVec(v)})`).join(', ') || '∅'}}`, `what survives: ${a.survives}`].filter(Boolean).join('\n')}
      </div>
      <p className="small">{a.summary}</p>
      <fieldset>
        <legend>Preimage of an output b</legend>
        <div className="matrix-input" style={{ gridTemplateColumns: `repeat(${t.length}, auto)` }}>
          {t.map((v, i) => (
            <input key={i} type="number" value={v} aria-label={`b component ${i + 1}`} onChange={(e) => setTarget(t.map((x, j) => (j === i ? Math.trunc(Number(e.target.value) || 0) : x)))} />
          ))}
        </div>
        <p className="small" aria-live="polite">
          <strong>{pre.kind === 'empty' ? 'Empty.' : pre.kind === 'point' ? 'One point.' : 'An affine family.'}</strong> {pre.explanation}
        </p>
      </fieldset>
      <details>
        <summary>Counterexample control: two inputs, one output</summary>
        {a.kernel[0] ? (
          <p className="small">
            Take x = 0 and x′ = ({fmtVec(a.kernel[0])}). Both are sent to 0 by A, so no observer of the output can tell them apart. Information was identified, not erased at random.
          </p>
        ) : (
          <p className="small">This A is injective: no two different inputs share an output. Try the “Line crush” preset.</p>
        )}
      </details>
      <figure className="figure">
        <PlateSvg plate={plate} />
        <figcaption>{plate.caption}</figcaption>
      </figure>
      <div className="btn-row">
        <button
          className="btn primary"
          onClick={() => {
            updateWorld((w) => ({ sculpture: m, inscriptionShift: w.inscriptionShift === 0 ? 1 : -w.inscriptionShift }));
            onRecord?.(recordExercise(imageRecord(m, t)));
          }}
        >
          Accept matrix: raise the sculpture and record
        </button>
      </div>
      <p className="small muted">Accepting places the image-space sculpture in the Hall of First Principles and in this realm, and moves the Gate’s inscription.</p>
    </section>
  );
}
