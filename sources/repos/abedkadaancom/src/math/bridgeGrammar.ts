// The Bridge Grammar: an operational grammar G = (Σ, 𝔄, ⟦·⟧, ℒ) in the sense of
// CGT-DEF-003 (Computational Grammar Theory, Kadaan 2026), staged on the
// atrium's six doors.
//
//   𝔄   the six division doors, joined by typed bridges (stone or gold)
//   Σ   moves: "go to door X"  (letters F R P G A W)
//   ⟦X⟧ the relation {(u, X) : a bridge joins u and X}
//   ℒ   admissibility: the sequence of bridge types crossed must be accepted by
//       a DFA ("never cross two gold bridges in a row")
//
// A word is checked on two separate layers, which CGT insists are kept apart:
// syntactic admissibility (is the type sequence in ℒ?) and semantic
// realizability (does every step exist in the structure?).

export type DoorId = 'F' | 'R' | 'P' | 'G' | 'A' | 'W';
export type BridgeType = 'stone' | 'gold';

export interface Bridge {
  a: DoorId;
  b: DoorId;
  type: BridgeType;
}

export const DOORS: DoorId[] = ['F', 'R', 'P', 'G', 'A', 'W'];

export const INITIAL_BRIDGES: Bridge[] = [
  { a: 'F', b: 'R', type: 'stone' },
  { a: 'R', b: 'P', type: 'gold' },
  { a: 'P', b: 'G', type: 'stone' },
  { a: 'G', b: 'A', type: 'stone' },
  { a: 'A', b: 'W', type: 'gold' },
  { a: 'W', b: 'F', type: 'stone' },
];

/** DFA over {stone, gold}: state 0 = last crossing stone (or start), 1 = last gold, 2 = dead. */
export const DFA = {
  states: [0, 1, 2] as const,
  start: 0,
  accepting: new Set([0, 1]),
  delta(q: number, t: BridgeType): number {
    if (q === 2) return 2;
    if (t === 'gold') return q === 1 ? 2 : 1;
    return 0;
  },
  description: 'Accepts every sequence of bridge types with no two consecutive gold crossings: the regular language (stone | gold·stone)*(ε | gold).',
};

export function findBridge(bridges: Bridge[], u: DoorId, v: DoorId): Bridge | undefined {
  return bridges.find((x) => (x.a === u && x.b === v) || (x.a === v && x.b === u));
}

export function degree(bridges: Bridge[], d: DoorId): number {
  return bridges.filter((x) => x.a === d || x.b === d).length;
}

export interface WordStep {
  from: DoorId;
  to: DoorId;
  bridge: BridgeType | null;
  dfaState: number;
}

export interface WordResult {
  word: string;
  realizable: boolean;
  admissible: boolean;
  steps: WordStep[];
  failedAt: number | null;
  verdict: string;
}

/** Evaluate a walk such as "FRPG" starting at its first letter. */
export function evaluateWord(word: string, bridges: Bridge[]): WordResult {
  const letters = word.toUpperCase().replace(/[^FRPGAW]/g, '').split('') as DoorId[];
  const steps: WordStep[] = [];
  let q = DFA.start;
  let realizable = true;
  let failedAt: number | null = null;
  for (let i = 1; i < letters.length; i++) {
    const from = letters[i - 1]!;
    const to = letters[i]!;
    const br = findBridge(bridges, from, to);
    if (!br) {
      realizable = false;
      failedAt ??= i;
      steps.push({ from, to, bridge: null, dfaState: q });
      continue;
    }
    q = DFA.delta(q, br.type);
    if (q === 2) failedAt ??= i;
    steps.push({ from, to, bridge: br.type, dfaState: q });
  }
  const admissible = DFA.accepting.has(q);
  let verdict: string;
  if (letters.length < 2) verdict = 'A walk needs at least two doors.';
  else if (realizable && admissible) verdict = 'Realizable and admissible: every bridge exists and the type sequence is in ℒ.';
  else if (!realizable && admissible) verdict = `Admissible on the bridges that exist, but not realizable: there is no bridge for step ${failedAt}.`;
  else if (realizable && !admissible) verdict = `Realizable but not admissible: step ${failedAt} crosses a second gold bridge in a row, which the DFA rejects.`;
  else verdict = 'Neither realizable nor admissible.';
  return { word: letters.join(''), realizable, admissible, steps, failedAt, verdict };
}

export type Transformation =
  | { op: 'add'; a: DoorId; b: DoorId; type: BridgeType }
  | { op: 'remove'; a: DoorId; b: DoorId };

export interface PredicateResult {
  passes: boolean;
  checks: { name: string; ok: boolean; detail: string }[];
}

/**
 * The typed admissibility predicate for graph transformations:
 *  add(a, b, t)  requires a ≠ b, no existing bridge, deg ≤ 2 at both ends before
 *                adding (so deg ≤ 3 after), and, for t = gold, that the gold
 *                subgraph stays a forest (no gold cycle).
 *  remove(a, b)  requires the bridge to exist and the door graph to stay connected.
 */
export function admissibleTransformation(bridges: Bridge[], t: Transformation): PredicateResult {
  const checks: PredicateResult['checks'] = [];
  if (t.op === 'add') {
    checks.push({ name: 'distinct doors', ok: t.a !== t.b, detail: `${t.a} ≠ ${t.b}` });
    checks.push({ name: 'no parallel bridge', ok: !findBridge(bridges, t.a, t.b), detail: `no existing bridge ${t.a}–${t.b}` });
    checks.push({ name: 'degree bound', ok: degree(bridges, t.a) <= 2 && degree(bridges, t.b) <= 2, detail: `deg(${t.a}) = ${degree(bridges, t.a)}, deg(${t.b}) = ${degree(bridges, t.b)}; each must be ≤ 2 before adding` });
    if (t.type === 'gold') {
      const gold = bridges.filter((x) => x.type === 'gold');
      const cyc = connected(gold, t.a, t.b);
      checks.push({ name: 'gold forest', ok: !cyc, detail: cyc ? `${t.a} and ${t.b} are already joined by gold; a gold cycle would form` : 'no gold path joins the ends yet' });
    }
  } else {
    const exists = !!findBridge(bridges, t.a, t.b);
    checks.push({ name: 'bridge exists', ok: exists, detail: `${t.a}–${t.b}` });
    if (exists) {
      const rest = bridges.filter((x) => x !== findBridge(bridges, t.a, t.b));
      const ok = DOORS.every((d) => connected(rest, 'F', d));
      checks.push({ name: 'stays connected', ok, detail: ok ? 'every door still reachable from F' : 'removing it would strand a door' });
    }
  }
  return { passes: checks.every((c) => c.ok), checks };
}

export function applyTransformation(bridges: Bridge[], t: Transformation): Bridge[] {
  if (!admissibleTransformation(bridges, t).passes) return bridges;
  if (t.op === 'add') return [...bridges, { a: t.a, b: t.b, type: t.type }];
  const br = findBridge(bridges, t.a, t.b);
  return bridges.filter((x) => x !== br);
}

function connected(edges: Bridge[], s: DoorId, t: DoorId): boolean {
  if (s === t) return true;
  const seen = new Set<DoorId>([s]);
  const stack: DoorId[] = [s];
  while (stack.length) {
    const u = stack.pop()!;
    for (const e of edges) {
      const v = e.a === u ? e.b : e.b === u ? e.a : null;
      if (v && !seen.has(v)) {
        if (v === t) return true;
        seen.add(v);
        stack.push(v);
      }
    }
  }
  return false;
}
