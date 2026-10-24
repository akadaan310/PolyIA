import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GATE_SYSTEMS, ieeeRepresentation, SYSTEMS, type SystemId, type DivisionResult } from '../math/numberSystems';
import { analyse, fmtVec, mat } from '../math/matrix';
import { updateGate, updateWorld, useStore, recordExercise, markVisited } from '../state/store';
import { imageRecord } from '../exhibits/records';
import { MatrixEditor } from '../exhibits/ImageSculpture';
import { Crumbs, usePageTitle } from '../ui/bits';

/** The moving diagram: arrows c ↦ b·c over a window of elements, image and kernel highlighted. */
function MultiplicationDiagram({ system, b }: { system: SystemId; b: string }) {
  const sys = SYSTEMS[system];
  const els = sys.elements() ?? ['-3', '-2', '-1', '0', '1', '2', '3'].filter((x) => sys.parse(x) === x);
  const map = sys.multiplicationMap(b);
  const W = 320;
  const H = 150;
  const x = (i: number) => 30 + (i * (W - 60)) / Math.max(1, els.length - 1);
  const outIndex = (v: string) => els.indexOf(v);
  return (
    <figure className="figure">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Diagram of c maps to ${b} times c in ${sys.symbol}`}>
        <style>{`.flow{stroke-dasharray:4 4;animation:dash 1.4s linear infinite}@keyframes dash{to{stroke-dashoffset:-16}}`}</style>
        <text x="8" y="22" fill="#b6ab9a" fontSize="10">c</text>
        <text x="8" y="132" fill="#b6ab9a" fontSize="10">{b}·c</text>
        {els.map((c, i) => {
          const out = sys.mul(b, c)!;
          const j = outIndex(out);
          const inKernel = out === '0';
          return (
            <g key={c}>
              <circle cx={x(i)} cy={26} r={11} fill={inKernel ? '#8d232c' : '#1a1a1a'} stroke="#d6ac62" />
              <text x={x(i)} y={30} textAnchor="middle" fontSize="11" fill="#f4ebdc">{c}</text>
              {j >= 0 ? <line className="flow" x1={x(i)} y1={38} x2={x(j)} y2={114} stroke={inKernel ? '#c0394a' : '#d6ac62'} strokeWidth={1.4} /> : <line className="flow" x1={x(i)} y1={38} x2={x(i)} y2={70} stroke="#d6ac62" strokeWidth={1} opacity={0.5} />}
            </g>
          );
        })}
        {els.map((c, i) => {
          const inImage = map.imageSet ? map.imageSet.includes(c) : els.some((e) => sys.mul(b, e) === c);
          return (
            <g key={`o${c}`}>
              <rect x={x(i) - 11} y={114} width={22} height={22} rx={3} fill={inImage ? '#d6ac62' : '#121110'} stroke="#d6ac62" />
              <text x={x(i)} y={129} textAnchor="middle" fontSize="11" fill={inImage ? '#0a0a0a' : '#6b6358'}>{c}</text>
            </g>
          );
        })}
      </svg>
      <figcaption>
        Gold squares: the image of c ↦ {b}·c ({map.image}). Crimson circles: its kernel ({map.kernel}). {sys.size === null ? 'Only a window of the infinite system is drawn.' : ''}
      </figcaption>
    </figure>
  );
}

function DivisionRow({ label, r }: { label: string; r: DivisionResult }) {
  return (
    <div className={`verdict ${r.kind === 'unique' ? 'ok' : 'bad'}`}>
      <strong className="math">{label}</strong> — {r.kind === 'unique' ? `quotient ${r.quotient}` : r.failure === 'image' ? 'no solution (image failure)' : 'no unique solution (kernel failure)'}
      <div className="small">{r.explanation}</div>
    </div>
  );
}

const MATRICES: { name: string; m: number[][] }[] = [
  { name: 'Shadow on the floor', m: [[1, 0], [0, 0]] },
  { name: 'Turn a quarter', m: [[0, -1], [1, 0]] },
  { name: 'Collapse to a line', m: [[1, 2], [2, 4]] },
  { name: 'Annihilate', m: [[0, 0], [0, 0]] },
];

function TransformDiagram({ m }: { m: number[][] }) {
  const a = analyse(mat(m));
  const S = 26;
  const C = 130;
  const pts: [number, number][] = [];
  for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) pts.push([i, j]);
  const f = ([x, y]: [number, number]): [number, number] => [m[0]![0]! * x + m[0]![1]! * y, m[1]![0]! * x + m[1]![1]! * y];
  const k = a.kernel[0]?.map((q) => q.toNumber());
  return (
    <figure className="figure">
      <svg viewBox="0 0 260 260" role="img" aria-label="Grid of inputs and their images under the matrix">
        <line x1="0" y1={C} x2="260" y2={C} stroke="#3a342c" />
        <line x1={C} y1="0" x2={C} y2="260" stroke="#3a342c" />
        {pts.map((p, i) => (
          <circle key={`i${i}`} cx={C + p[0] * S} cy={C - p[1] * S} r={2.4} fill="#5e574d" />
        ))}
        {pts.map((p, i) => {
          const [u, v] = f(p);
          return <circle key={`o${i}`} cx={C + Math.max(-4.8, Math.min(4.8, u)) * S} cy={C - Math.max(-4.8, Math.min(4.8, v)) * S} r={4} fill="#f1d79c" opacity={0.85} />;
        })}
        {k ? <line x1={C - k[0]! * 200} y1={C + k[1]! * 200} x2={C + k[0]! * 200} y2={C - k[1]! * 200} stroke="#c0394a" strokeWidth={2} /> : null}
      </svg>
      <figcaption>Grey: inputs. Gold: their images. Crimson: the kernel line (inputs sent to the origin).</figcaption>
    </figure>
  );
}

export function Gate() {
  usePageTitle('The Gate · Hall of First Principles');
  const gate = useStore((s) => s.world.gate);
  const navigate = useNavigate();
  const [answer, setAnswer] = useState('');
  const [m, setM] = useState<number[][]>(gate.matrix ?? MATRICES[2]!.m);
  const [applied, setApplied] = useState(Boolean(gate.matrix));
  const [survives, setSurvives] = useState<string | null>(gate.survivesAnswer);
  const system = gate.system;
  const sys = system ? SYSTEMS[system] : null;
  const correctSum = sys ? sys.add('1', '1')! : null;
  /** In a finite system, only the listed residues are elements as written (2 is not an element of F₂, though 2 ≡ 0). */
  const canonical = (x: string) => (sys?.elements() ? sys.elements()!.includes(x.trim()) : true);
  const a = useMemo(() => analyse(mat(m)), [m]);
  const truthSurvives = a.rank === 2 ? 'everything' : a.rank === 1 ? 'a line' : 'only the origin';

  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['The Gate']]} />
      <h1>The Arithmetic of Possibility</h1>
      <p>The Gate asks three questions. None of them is a test of intelligence: every answer leads somewhere, and several questions have more than one right answer, because the answer depends on the structure you are standing in.</p>

      <section aria-labelledby="g1">
        <h2 id="g1">I. What is one plus one?</h2>
        <fieldset>
          <legend>First choose your numbers</legend>
          {GATE_SYSTEMS.map((id) => (
            <label key={id} className="choice">
              <input type="radio" name="system" checked={system === id} onChange={() => { updateGate({ system: id, stage: Math.max(gate.stage, 1) as 1 }); setAnswer(''); }} />
              <span>
                <strong className="math">{SYSTEMS[id].symbol}</strong> — {SYSTEMS[id].name}. <span className="small muted">{SYSTEMS[id].description}</span>
              </span>
            </label>
          ))}
        </fieldset>
        {sys ? (
          <>
            <label htmlFor="sum">In {sys.symbol}, 1 + 1 =</label>
            <input id="sum" type="text" inputMode="numeric" value={answer} onChange={(e) => setAnswer(e.target.value)} onBlur={() => updateGate({ sumAnswer: answer })} placeholder="your answer" />
            {answer.trim() !== '' ? (
              <div className={`verdict ${sys.parse(answer) === correctSum && canonical(answer) ? 'ok' : 'bad'}`} aria-live="polite">
                {sys.parse(answer) === correctSum && !canonical(answer)
                  ? `“${answer.trim()}” is not an element of ${sys.symbol} as written; read modulo ${sys.size}, it is ${correctSum}, which is indeed 1 + 1 in ${sys.symbol}.`
                  : sys.parse(answer) === correctSum
                  ? `Yes: in ${sys.symbol}, 1 + 1 = ${correctSum}.`
                  : sys.parse(answer) === null
                    ? `“${answer}” is not an element of ${sys.symbol}. ${sys.symbol === 'F₂' ? 'F₂ has only 0 and 1.' : ''} In ${sys.symbol}, 1 + 1 = ${correctSum}.`
                    : `In ${sys.symbol} your answer is the element ${sys.parse(answer)}, but 1 + 1 = ${correctSum}.`}{' '}
                {system === 'F2' ? 'Addition in F₂ is addition modulo 2: 1 + 1 = 2 ≡ 0. The field has characteristic 2, so adding 1 to itself returns to 0. This is the arithmetic of parity, and of every bit in your computer.' : 'Here 1 + 1 = 2 because 2 is defined as the successor of 1, and addition satisfies m + S(n) = S(m + n).'}
              </div>
            ) : null}
            <table className="data" style={{ marginTop: 8 }}>
              <thead>
                <tr><th>structure</th><th>1 + 1</th></tr>
              </thead>
              <tbody>
                {(['N', 'Z', 'Q', 'F2', 'Z6'] as SystemId[]).map((id) => (
                  <tr key={id}><td>{SYSTEMS[id].symbol}</td><td className="math">{SYSTEMS[id].add('1', '1')}</td></tr>
                ))}
              </tbody>
            </table>
            <div className="btn-row">
              <button className="btn primary" onClick={() => updateGate({ stage: Math.max(gate.stage, 2) as 2, sumAnswer: answer })}>
                Next: zero, one and division
              </button>
            </div>
          </>
        ) : null}
      </section>

      {gate.stage >= 2 && sys ? (
        <section aria-labelledby="g2">
          <h2 id="g2">II. 0 / 1, 1 / 0 and 0 / 0</h2>
          <p>Read a / b as a question: <em>which c satisfy b · c = a?</em> The map c ↦ b·c has an <strong>image</strong> (what it can reach) and a <strong>kernel</strong> (what it sends to 0). Division succeeds exactly when a is in the image and the kernel is trivial.</p>
          <DivisionRow label={`0 / 1 in ${sys.symbol}`} r={sys.divide('0', '1')} />
          <MultiplicationDiagram system={system!} b="1" />
          <DivisionRow label={`1 / 0 in ${sys.symbol}`} r={sys.divide('1', '0')} />
          <DivisionRow label={`0 / 0 in ${sys.symbol}`} r={sys.divide('0', '0')} />
          <MultiplicationDiagram system={system!} b="0" />
          <div className="notice">
            <strong>About JavaScript’s answers.</strong> Your browser’s IEEE 754 arithmetic gives 1/0 = <code>{ieeeRepresentation(1, 0).value}</code> and 0/0 = <code>{ieeeRepresentation(0, 0).value}</code>. {ieeeRepresentation(1, 0).note} {ieeeRepresentation(0, 0).note} These are encodings of special data, not definitions of field division; neither 1/0 nor 0/0 is a valid field quotient.
          </div>
          <p className="small muted">Source: the classification of division failures as image and kernel failures follows Grammar in Numbers (GIN-THM-001), packaging the standard fact that solutions of b·c = a in a commutative ring are empty or a coset of the annihilator.</p>
          <div className="btn-row">
            <button className="btn primary" onClick={() => updateGate({ stage: 3, divisionsSeen: ['0/1', '1/0', '0/0'] })}>
              Next: transform something
            </button>
          </div>
        </section>
      ) : null}

      {gate.stage >= 3 ? (
        <section aria-labelledby="g3">
          <h2 id="g3">III. What survives a transformation?</h2>
          <p>Choose a matrix (or edit it). Apply it to the plane and watch the grid. Then say what information survives.</p>
          <div className="btn-row">
            {MATRICES.map((x) => (
              <button key={x.name} className="btn small" onClick={() => { setM(x.m); setApplied(false); setSurvives(null); }}>
                {x.name}
              </button>
            ))}
          </div>
          <MatrixEditor m={m} onChange={(v) => { setM(v); setApplied(false); setSurvives(null); }} />
          <div className="btn-row">
            <button className="btn" onClick={() => { setApplied(true); updateGate({ matrix: m }); }}>
              Apply the transformation
            </button>
          </div>
          {applied ? (
            <>
              <TransformDiagram m={m} />
              <fieldset>
                <legend>Which information survives?</legend>
                {['everything', 'a line', 'only the origin'].map((o) => (
                  <label key={o} className="choice">
                    <input type="radio" name="survives" checked={survives === o} onChange={() => { setSurvives(o); updateGate({ survivesAnswer: o }); }} /> {o}
                  </label>
                ))}
              </fieldset>
              {survives ? (
                <div className={`verdict ${survives === truthSurvives ? 'ok' : 'bad'}`} aria-live="polite">
                  {survives === truthSurvives ? 'Exactly. ' : `Not quite: what survives is ${truthSurvives}. `}
                  rank A = {a.rank}, dim ker A = {a.nullity}. Image: span{'{'}{a.image.map((v) => `(${fmtVec(v)})`).join(', ') || '∅'}{'}'}; kernel: span{'{'}{a.kernel.map((v) => `(${fmtVec(v)})`).join(', ') || '∅'}{'}'}. {a.summary}
                </div>
              ) : null}
              <div className="btn-row">
                <button
                  className="btn primary"
                  disabled={!survives}
                  onClick={() => {
                    updateGate({ doorOpened: true, matrix: m });
                    updateWorld((w) => ({ sculpture: m, inscriptionShift: w.inscriptionShift === 0 ? 1 : -w.inscriptionShift }));
                    recordExercise(imageRecord(m));
                    markVisited('gate:demonstrated');
                    navigate('/divisions/foundations');
                  }}
                >
                  Demonstrate image and kernel: open the first door
                </button>
              </div>
              <p className="small muted">Opening raises an image-space sculpture of your matrix in the Hall of First Principles and moves the Gate’s inscription.</p>
            </>
          ) : null}
        </section>
      ) : null}
      {gate.doorOpened ? (
        <p className="notice gold">
          You have opened the first door. Continue to <Link to="/divisions/foundations">Foundations of Computation</Link> or walk into <Link to="/atrium">the Atrium</Link>.
        </p>
      ) : null}
    </article>
  );
}
