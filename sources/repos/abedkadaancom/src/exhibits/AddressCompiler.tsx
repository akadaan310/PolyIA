import { useMemo, useState } from 'react';
import { compile } from '../math/addressCompiler';
import { recordExercise, updateWorld, type ExerciseRecord } from '../state/store';
import { addressRecord } from './records';
import { plateFor } from '../books/plates';
import { PlateSvg } from '../ui/PlateSvg';

const EXAMPLES = [
  'loom://plate/START/ROTATE:90/SCALE:2/SHIFT:1,0/COMMIT',
  'loom://plate/START/SHEAR:1/REFLECT:x/COMMIT',
  'loom://plate/START/SCALE:1%2F2,3/COMMIT',
  'loom://plate/COMMIT',
  'loom://plate/START/ROTATE:45/COMMIT',
];

export function AddressCompilerExhibit({ onRecord }: { onRecord?: (r: ExerciseRecord) => void }) {
  const [address, setAddress] = useState(EXAMPLES[0]!);
  const r = useMemo(() => compile(address), [address]);
  const plate = useMemo(() => plateFor('address-compiler', { ...addressRecord(address), at: '' }), [address]);
  return (
    <section aria-label="The loom:// compiler exhibit">
      <p className="small muted">
        Teaching scheme <code>loom://</code>: a typed machine <code>idle —START→ open —ops→ open —COMMIT→ committed</code>. Operations: <code>ROTATE:k·90</code>, <code>SCALE:s</code> or <code>s,t</code>, <code>SHIFT:x,y</code>, <code>SHEAR:k</code>, <code>REFLECT:x|y</code>. Rational arguments are exact and percent-encoded, <code>1%2F2</code> for 1/2, because a literal <code>/</code> would end the path segment (RFC 3986).
      </p>
      <label htmlFor="loom-addr">Address</label>
      <input id="loom-addr" type="text" value={address} onChange={(e) => setAddress(e.target.value.slice(0, 200))} spellCheck={false} />
      <div className="btn-row">
        {EXAMPLES.slice(1).map((e) => (
          <button key={e} className="btn small" onClick={() => setAddress(e)}>
            {e.replace('loom://plate/', '…/')}
          </button>
        ))}
      </div>
      <div className={`verdict ${r.ok ? 'ok' : 'bad'}`} aria-live="polite">
        <strong>{r.ok ? 'Admitted and compiled.' : 'Refused.'}</strong> {r.diagnostics.join(' · ')}
      </div>
      <table className="data">
        <thead>
          <tr>
            <th>token</th>
            <th>type</th>
            <th>state after</th>
          </tr>
        </thead>
        <tbody>
          {r.tokens.map((t, i) => (
            <tr key={i}>
              <td>
                <code>{t.raw}</code>
              </td>
              <td>{t.error ? <span style={{ color: '#f0b3bb' }}>{t.error}</span> : t.type}</td>
              <td>{r.states[i + 1] ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {r.matrix ? <div className="math-block">{`M = \n${r.matrix.map((row) => `[ ${row.map((q) => q.toString().padStart(4)).join(' ')} ]`).join('\n')}`}</div> : null}
      <figure className="figure">
        <PlateSvg plate={plate} />
        <figcaption>{plate.caption}</figcaption>
      </figure>
      <div className="btn-row">
        <button
          className="btn primary"
          onClick={() => {
            if (r.ok) updateWorld({ compiledAddress: address });
            onRecord?.(recordExercise(addressRecord(address)));
          }}
        >
          {r.ok ? 'Weave into the realm and record' : 'Record this refusal'}
        </button>
      </div>
    </section>
  );
}
