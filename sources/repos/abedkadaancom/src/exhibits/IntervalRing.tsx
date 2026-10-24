import { useMemo, useState } from 'react';
import { analyseInterval, INTERVAL_NAMES, PITCH_NAMES } from '../math/music';
import { recordExercise, updateWorld, useStore, type ExerciseRecord } from '../state/store';
import { intervalRecord } from './records';
import { plateFor } from '../books/plates';
import { PlateSvg } from '../ui/PlateSvg';
import { playOrbit } from '../audio/engine';

export function IntervalRingExhibit({ onRecord }: { onRecord?: (r: ExerciseRecord) => void }) {
  const k = useStore((s) => s.world.interval);
  const sound = useStore((s) => s.settings.sound);
  const a = useMemo(() => analyseInterval(k), [k]);
  const plate = useMemo(() => plateFor('interval-ring', { ...intervalRecord(k), at: '' }), [k]);
  const [msg, setMsg] = useState<string | null>(null);
  return (
    <section aria-label="The Interval Ring exhibit">
      <label htmlFor="iv">Interval k (semitones): {k} — {INTERVAL_NAMES[k]}</label>
      <input id="iv" type="range" min={0} max={11} value={k} onChange={(e) => updateWorld({ interval: Number(e.target.value) })} />
      <div className="math-block" aria-live="polite">
        {[`orbit of C: ${a.orbit.map((p) => PITCH_NAMES[p]).join(' ')}`, `gcd(12, ${a.k}) = ${a.gcd}  ⇒  |⟨${a.k}⟩| = ${a.orbitLength}  (${a.starPolygon})`, `2^(${a.k}/12) = ${a.equalTemperedRatio.toFixed(5)}  vs just ${a.justRatio[0]}/${a.justRatio[1]}  (${a.centsDeviation >= 0 ? '+' : ''}${a.centsDeviation.toFixed(2)} cents)`, `campus: ${a.orbitLength} arches lit, hue ${a.hue}°`].join('\n')}
      </div>
      <figure className="figure">
        <PlateSvg plate={plate} />
        <figcaption>{plate.caption}</figcaption>
      </figure>
      <div className="btn-row">
        <button className="btn" onClick={() => setMsg(playOrbit(a.orbit) ? 'Playing the computed orbit.' : 'Sound is off. Turn it on in Settings to hear the orbit; the lights carry the same information.')}>
          Play orbit {sound ? '' : '(sound off)'}
        </button>
        <button className="btn primary" onClick={() => onRecord?.(recordExercise(intervalRecord(k)))}>
          Record this interval
        </button>
      </div>
      {msg ? <p className="small muted" aria-live="polite">{msg}</p> : null}
    </section>
  );
}
