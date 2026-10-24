// Pure builders for exhibit results. Exhibits call them to record what the
// visitor did; the Scriptorium calls them to rebuild a derivation. The record
// contains only inputs the visitor chose and outputs the browser computed.

import type { ExerciseRecord } from '../state/store';
import { evaluateWord, type Bridge } from '../math/bridgeGrammar';
import { foldOnce, grammarSize, startFold, unfoldAll } from '../math/fold';
import { compile, applyHomogeneous } from '../math/addressCompiler';
import { analyse, fmtVec, mat, preimage, vec } from '../math/matrix';
import { analyseInterval, PITCH_NAMES } from '../math/music';
import { density, downstream, ruleTable, topologicalOrder, weave, WORLD_FACTS } from '../math/world';

type Rec = Omit<ExerciseRecord, 'at'>;

export function bridgeRecord(word: string, bridges: Bridge[]): Rec {
  const r = evaluateWord(word, bridges);
  const output = [
    `bridges: ${bridges.map((b) => `${b.a}–${b.b} (${b.type})`).join(', ')}`,
    ...r.steps.map((s, i) => `step ${i + 1}: ${s.from} → ${s.to} ${s.bridge ? `crosses ${s.bridge}; DFA state ${s.dfaState}` : 'has no bridge (unrealizable step)'}`),
    `realizable: ${r.realizable ? 'yes' : 'no'}; admissible: ${r.admissible ? 'yes' : 'no'}`,
    r.verdict,
  ];
  return {
    exhibit: 'bridge-grammar',
    input: { word: r.word, bridges: bridges.map((b) => `${b.a}${b.b}:${b.type}`) },
    output,
    headline: `The walk ${r.word || '(empty)'} was ${r.realizable ? 'realizable' : 'unrealizable'} and ${r.admissible ? 'admissible' : 'inadmissible'}.`,
  };
}

export function foldRecord(word: string, depth: number): Rec {
  let st = startFold(word);
  const output: string[] = [`stratum 0: ${st.current.join(' ')} (length ${st.current.length})`];
  for (let i = 0; i < depth && st.current.length > 1; i++) {
    st = foldOnce(st);
    const r = st.rules[st.rules.length - 1]!;
    output.push(`fold ${i + 1}: ${r.glyph} → ${r.left}${r.right} replaced ${r.count}×; stratum ${i + 1}: ${st.current.join(' ')}; grammar size ${grammarSize(st)}`);
  }
  const back = unfoldAll(st).join('');
  output.push(`unfold check: ${back === st.original.join('') ? 'unfold(fold(w)) = w ✓' : 'MISMATCH'}`);
  return {
    exhibit: 'fold',
    input: { word, depth: st.rules.length },
    output,
    headline: `The path ${word} was folded ${st.rules.length} time${st.rules.length === 1 ? '' : 's'} to ${st.current.join('')}, and unfolded back exactly.`,
  };
}

export function addressRecord(address: string): Rec {
  const r = compile(address);
  const output = [
    ...r.tokens.map((t, i) => `token ${i + 1}: ${t.raw} — ${t.type}${t.error ? ` — rejected: ${t.error}` : ''}`),
    `machine states: ${r.states.join(' → ')}`,
    ...r.diagnostics,
  ];
  if (r.matrix) {
    output.push(`compiled matrix: ${r.matrix.map((row) => `[${row.map(String).join(' ')}]`).join(' ')}`);
    const corners: [number, number][] = [[0, 0], [1, 0], [1, 1], [0, 1]];
    output.push(`unit square ↦ ${corners.map(([x, y]) => `(${applyHomogeneous(r.matrix!, x, y).map((v) => +v.toFixed(3)).join(', ')})`).join(' ')}`);
  }
  return {
    exhibit: 'address-compiler',
    input: { address },
    output,
    headline: r.ok ? `The address ${address} was admitted and compiled to one 3×3 matrix.` : `The address ${address} was refused: ${r.diagnostics[0] ?? 'inadmissible'}.`,
  };
}

export function imageRecord(rows: number[][], target?: number[]): Rec {
  const A = mat(rows);
  const a = analyse(A);
  const output = [
    `A = ${rows.map((r) => `[${r.join(' ')}]`).join(' ')}`,
    `rank ${a.rank}, nullity ${a.nullity}${a.determinant !== null ? `, det ${a.determinant}` : ''}`,
    `image basis: ${a.image.length ? a.image.map((v) => `(${fmtVec(v)})`).join(', ') : '∅ (image is {0})'}`,
    `kernel basis: ${a.kernel.length ? a.kernel.map((v) => `(${fmtVec(v)})`).join(', ') : '∅ (kernel is {0})'}`,
    `what survives: ${a.survives}`,
    a.summary,
  ];
  if (target) output.push(`preimage of (${target.join(', ')}): ${preimage(A, vec(target)).explanation}`);
  return {
    exhibit: 'image-sculpture',
    input: { matrix: rows, ...(target ? { target } : {}) },
    output,
    headline: `The matrix had rank ${a.rank}: ${a.survives} survived and a ${a.nullity}-dimensional kernel was lost.`,
  };
}

export function intervalRecord(k: number): Rec {
  const a = analyseInterval(k);
  const output = [
    `interval: ${a.k} semitones (${a.name})`,
    `orbit of C: ${a.orbit.map((p) => PITCH_NAMES[p]).join(' ')}`,
    `gcd(12, ${a.k}) = ${a.gcd}; orbit length 12 / ${a.gcd} = ${a.orbitLength}; ${a.starPolygon}`,
    `equal-tempered ratio 2^(${a.k}/12) = ${a.equalTemperedRatio.toFixed(5)}; just ${a.justRatio[0]}/${a.justRatio[1]}; deviation ${a.centsDeviation >= 0 ? '+' : ''}${a.centsDeviation.toFixed(2)} cents`,
    `campus consequence: ${a.orbitLength} arches lit at hue ${a.hue}°`,
  ];
  return { exhibit: 'interval-ring', input: { k: a.k }, output, headline: `Stepping by ${a.k} semitones visited ${a.orbitLength} of the 12 pitch classes.` };
}

export function loomRecord(rule: number, removed: string | null = null): Rec {
  const width = 31;
  const rows = 16;
  const g = weave(rule, width, rows);
  const table = ruleTable(rule).map((r) => `${r.neighbourhood}→${r.out}`).join(' ');
  const output = [
    `rule ${rule} = ${rule.toString(2).padStart(8, '0')}₂: ${table}`,
    `woven ${rows} rows × ${width} cells from a single seed; density ${(density(g) * 100).toFixed(1)}%`,
    `last row: ${g[rows - 1]!.map((c) => (c ? '█' : '·')).join('')}`,
    `BORNE birth order: ${topologicalOrder(WORLD_FACTS)!.join(' → ')}`,
  ];
  if (removed) output.push(`removing ${removed} invalidates: ${downstream(WORLD_FACTS, removed).join(', ') || 'nothing'}`);
  return {
    exhibit: 'world-loom',
    input: { rule, ...(removed ? { removed } : {}) },
    output,
    headline: `The loom wove rule ${rule} into a ${rows}-row world with ${(density(g) * 100).toFixed(0)}% raised cells.`,
  };
}

/** Defaults used when a station was visited without running its exhibit. */
export const DEFAULT_RECORDS: Record<string, () => Rec> = {
  'bridge-grammar': () => bridgeRecord('FRPG', [
    { a: 'F', b: 'R', type: 'stone' },
    { a: 'R', b: 'P', type: 'gold' },
    { a: 'P', b: 'G', type: 'stone' },
    { a: 'G', b: 'A', type: 'stone' },
    { a: 'A', b: 'W', type: 'gold' },
    { a: 'W', b: 'F', type: 'stone' },
  ]),
  fold: () => foldRecord('NENENE', 3),
  'address-compiler': () => addressRecord('loom://plate/START/ROTATE:90/SCALE:2/SHIFT:1,0/COMMIT'),
  'image-sculpture': () => imageRecord([[1, 2], [2, 4]], [3, 6]),
  'interval-ring': () => intervalRecord(7),
  'world-loom': () => loomRecord(90, 'well'),
};
