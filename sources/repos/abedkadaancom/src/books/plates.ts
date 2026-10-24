// Generated visual plates: vector drawings computed from a participant's
// exercise. Coordinates are in the unit square, y downwards. The same spec is
// drawn as SVG in the HTML reader and as vector paths in the PDF.

import type { ExhibitId } from '../content/types';
import type { ExerciseRecord } from '../state/store';
import { DOORS, evaluateWord, type Bridge, type DoorId } from '../math/bridgeGrammar';
import { foldAll, startFold, type FoldRule } from '../math/fold';
import { compile, applyHomogeneous } from '../math/addressCompiler';
import { analyse, mat } from '../math/matrix';
import { analyseInterval, PITCH_NAMES } from '../math/music';
import { weave } from '../math/world';

export type Ink = 'gold' | 'ink' | 'crimson' | 'faint';

export type Prim =
  | { t: 'line'; x1: number; y1: number; x2: number; y2: number; ink: Ink; w?: number }
  | { t: 'circle'; cx: number; cy: number; r: number; ink: Ink; fill?: boolean }
  | { t: 'poly'; pts: [number, number][]; ink: Ink; closed?: boolean; fill?: boolean }
  | { t: 'text'; x: number; y: number; text: string; ink: Ink; size?: number; anchor?: 'start' | 'middle' | 'end' }
  | { t: 'rect'; x: number; y: number; w: number; h: number; ink: Ink; fill?: boolean };

export interface Plate {
  title: string;
  caption: string;
  prims: Prim[];
}

const polar = (cx: number, cy: number, r: number, a: number): [number, number] => [cx + r * Math.cos(a), cy + r * Math.sin(a)];

function bridgePlate(rec: ExerciseRecord): Plate {
  const bridges: Bridge[] = ((rec.input.bridges as string[]) ?? []).map((s) => {
    const [ab, type] = s.split(':');
    return { a: ab![0] as DoorId, b: ab![1] as DoorId, type: type as Bridge['type'] };
  });
  const word = String(rec.input.word ?? '');
  const pos = new Map(DOORS.map((d, i) => [d, polar(0.5, 0.52, 0.34, -Math.PI / 2 + (i * Math.PI) / 3)]));
  const prims: Prim[] = [];
  for (const b of bridges) {
    const [x1, y1] = pos.get(b.a)!;
    const [x2, y2] = pos.get(b.b)!;
    prims.push({ t: 'line', x1, y1, x2, y2, ink: b.type === 'gold' ? 'gold' : 'faint', w: b.type === 'gold' ? 2.2 : 1.4 });
  }
  const r = evaluateWord(word, bridges);
  r.steps.forEach((s, i) => {
    const [x1, y1] = pos.get(s.from)!;
    const [x2, y2] = pos.get(s.to)!;
    const bad = r.failedAt === i + 1;
    prims.push({ t: 'line', x1, y1, x2, y2, ink: bad ? 'crimson' : 'ink', w: 1 });
  });
  for (const [d, [x, y]] of pos) {
    prims.push({ t: 'circle', cx: x, cy: y, r: 0.045, ink: 'ink' });
    prims.push({ t: 'text', x, y: y + 0.014, text: d, ink: 'ink', size: 11, anchor: 'middle' });
  }
  return { title: 'Plate: the walk on the doors', caption: `The six doors with their bridges (gold and stone) and your walk ${word || '∅'} overlaid${r.failedAt ? `; the crimson step (${r.failedAt}) is where it first failed` : ''}.`, prims };
}

function foldPlate(rec: ExerciseRecord): Plate {
  const word = String(rec.input.word ?? 'NENENE');
  const st = foldAll(startFold(word));
  const prims: Prim[] = [];
  const rules = new Map<string, FoldRule>(st.rules.map((r) => [r.glyph, r]));
  const leaves = st.original.length;
  let leaf = 0;
  const depthOf = (g: string): number => {
    const r = rules.get(g);
    return r ? 1 + Math.max(depthOf(r.left), depthOf(r.right)) : 0;
  };
  const root = st.current[0] ?? word[0] ?? 'ε';
  const H = Math.max(1, depthOf(root));
  const draw = (g: string, level: number): [number, number] => {
    const r = rules.get(g);
    const y = 0.12 + (0.76 * (H - level)) / H;
    if (!r) {
      const x = 0.06 + (0.88 * (leaf + 0.5)) / leaves;
      leaf++;
      prims.push({ t: 'text', x, y: 0.94, text: g, ink: 'ink', size: 9, anchor: 'middle' });
      return [x, 0.9];
    }
    const a = draw(r.left, level - 1);
    const b = draw(r.right, level - 1);
    const x = (a[0] + b[0]) / 2;
    prims.push({ t: 'line', x1: x, y1: y, x2: a[0], y2: a[1], ink: 'faint' });
    prims.push({ t: 'line', x1: x, y1: y, x2: b[0], y2: b[1], ink: 'faint' });
    prims.push({ t: 'circle', cx: x, cy: y, r: 0.028, ink: 'gold', fill: true });
    prims.push({ t: 'text', x, y: y - 0.04, text: g, ink: 'ink', size: 9, anchor: 'middle' });
    return [x, y];
  };
  if (word.length > 0 && word.length <= 40) draw(root, H);
  return { title: 'Plate: the Plicastratum of your path', caption: `The straight-line program of ${word}: each gold node is a fold glyph; reading the leaves left to right unfolds it.`, prims };
}

function addressPlate(rec: ExerciseRecord): Plate {
  const r = compile(String(rec.input.address ?? ''));
  const prims: Prim[] = [];
  const S = 0.09;
  const map = (x: number, y: number): [number, number] => [0.5 + x * S, 0.5 - y * S];
  for (let i = -5; i <= 5; i++) {
    prims.push({ t: 'line', ...seg(map(i, -5), map(i, 5)), ink: 'faint', w: 0.4 });
    prims.push({ t: 'line', ...seg(map(-5, i), map(5, i)), ink: 'faint', w: 0.4 });
  }
  const sq: [number, number][] = [[0, 0], [1, 0], [1, 1], [0, 1]];
  prims.push({ t: 'poly', pts: sq.map(([x, y]) => map(x, y)), ink: 'ink', closed: true });
  if (r.matrix) {
    const img = sq.map(([x, y]) => applyHomogeneous(r.matrix!, x, y));
    prims.push({ t: 'poly', pts: img.map(([x, y]) => map(clamp(x), clamp(y))), ink: 'gold', closed: true, fill: true });
  }
  return { title: 'Plate: the woven square', caption: r.matrix ? 'The unit square (ink) and its image under your compiled matrix (gold).' : 'Your address was refused, so only the unit square is drawn: nothing was applied.', prims };
}

function imagePlate(rec: ExerciseRecord): Plate {
  const rows = (rec.input.matrix as number[][]) ?? [[1, 0], [0, 1]];
  const a = analyse(mat(rows));
  const n = rows[0]!.length;
  const prims: Prim[] = [];
  const S = 0.11;
  const P = (x: number, y: number): [number, number] => [0.5 + x * S, 0.5 - y * S];
  prims.push({ t: 'line', ...seg(P(-4, 0), P(4, 0)), ink: 'faint' });
  prims.push({ t: 'line', ...seg(P(0, -4), P(0, 4)), ink: 'faint' });
  // grid of inputs and their images (first two output coordinates, oblique for 3D)
  const proj = (v: number[]): [number, number] => (v.length === 2 ? [v[0]!, v[1]!] : [v[0]! + 0.45 * v[2]!, v[1]! + 0.3 * v[2]!]);
  const pts: number[][] = [];
  const R = [-1, 0, 1];
  if (n === 2) for (const x of R) for (const y of R) pts.push([x, y]);
  else for (const x of R) for (const y of R) for (const z of R) pts.push([x, y, z]);
  const f = rows;
  for (const p of pts) {
    const out = f.map((row) => row.reduce((s, c, j) => s + c * p[j]!, 0));
    const [x, y] = proj(out);
    prims.push({ t: 'circle', cx: P(clamp(x), clamp(y))[0], cy: P(clamp(x), clamp(y))[1], r: 0.012, ink: 'gold', fill: true });
  }
  for (const k of a.kernel) {
    const v = k.map((q) => q.toNumber());
    const [x, y] = proj(v);
    const L = Math.hypot(x, y) || 1;
    prims.push({ t: 'line', ...seg(P((-3 * x) / L, (-3 * y) / L), P((3 * x) / L, (3 * y) / L)), ink: 'crimson', w: 1.6 });
  }
  return { title: 'Plate: the image sculpture', caption: `Gold: the image of a grid of inputs under A (rank ${a.rank}). Crimson: the kernel direction${a.kernel.length === 1 ? '' : 's'}, everything sent to 0 (drawn in input coordinates).`, prims };
}

function intervalPlate(rec: ExerciseRecord): Plate {
  const a = analyseInterval(Number(rec.input.k ?? 7));
  const prims: Prim[] = [];
  const pos = (i: number) => polar(0.5, 0.5, 0.36, -Math.PI / 2 + (i * Math.PI) / 6);
  for (let i = 0; i < 12; i++) {
    const [x, y] = pos(i);
    const lit = a.orbit.includes(i);
    prims.push({ t: 'circle', cx: x, cy: y, r: 0.03, ink: lit ? 'gold' : 'faint', fill: lit });
    const [tx, ty] = polar(0.5, 0.5, 0.45, -Math.PI / 2 + (i * Math.PI) / 6);
    prims.push({ t: 'text', x: tx, y: ty + 0.012, text: PITCH_NAMES[i]!, ink: 'ink', size: 9, anchor: 'middle' });
  }
  if (a.orbit.length > 1) prims.push({ t: 'poly', pts: a.orbit.map(pos), ink: 'gold', closed: true });
  return { title: 'Plate: the interval star', caption: `Stepping by ${a.k} (${a.name}) from C: ${a.orbitLength} classes, ${a.starPolygon}.`, prims };
}

function loomPlate(rec: ExerciseRecord): Plate {
  const rule = Number(rec.input.rule ?? 90);
  const g = weave(rule, 31, 16);
  const prims: Prim[] = [];
  const cw = 0.9 / 31;
  const ch = 0.8 / 16;
  g.forEach((row, y) =>
    row.forEach((c, x) => {
      if (c) prims.push({ t: 'rect', x: 0.05 + x * cw, y: 0.1 + y * ch, w: cw * 0.92, h: ch * 0.92, ink: 'gold', fill: true });
    }),
  );
  prims.push({ t: 'rect', x: 0.05, y: 0.1, w: 0.9, h: 0.8, ink: 'faint' });
  return { title: `Plate: the cloth of rule ${rule}`, caption: `Sixteen wefts of rule ${rule} from a single raised cell; each gold cell is a 1.`, prims };
}

function seg(a: [number, number], b: [number, number]) {
  return { x1: a[0], y1: a[1], x2: b[0], y2: b[1] };
}
function clamp(v: number) {
  return Math.max(-4, Math.min(4, v));
}

export function plateFor(exhibit: ExhibitId, rec: ExerciseRecord): Plate {
  switch (exhibit) {
    case 'bridge-grammar': return bridgePlate(rec);
    case 'fold': return foldPlate(rec);
    case 'address-compiler': return addressPlate(rec);
    case 'image-sculpture': return imagePlate(rec);
    case 'interval-ring': return intervalPlate(rec);
    case 'world-loom': return loomPlate(rec);
  }
}
