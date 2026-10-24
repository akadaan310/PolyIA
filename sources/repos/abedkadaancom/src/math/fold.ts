// Plicastratum (house construction, Substrate University): the layered stratum
// of folds of a word.
//
// A fold replaces one adjacent pair of symbols (a digram) everywhere it occurs
// by a fresh glyph, recording the rule glyph → pair. Choosing the most frequent
// digram is Re-Pair (Larsson & Moffat, Proc. IEEE 88(11), 2000), an established
// grammar-compression algorithm. Folding until one glyph remains yields a
// straight-line program (SLP) whose root derives the whole word. Unfolding
// expands the rules. The invariant is unfold(fold(w)) = w.
//
// What is house terminology here: the word "Plicastratum" and the reading of
// the SLP's levels as navigable strata. What is established: Re-Pair and SLPs.

export interface FoldRule {
  glyph: string;
  left: string;
  right: string;
  /** How many occurrences the fold replaced. */
  count: number;
}

export interface FoldState {
  original: string[];
  current: string[];
  rules: FoldRule[];
}

/** Fresh glyphs for new nonterminals: Greek capitals, then numbered. */
const GLYPHS = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'.split('');

export function startFold(word: string): FoldState {
  const syms = [...word.replace(/\s+/g, '')];
  return { original: syms, current: syms, rules: [] };
}

function freshGlyph(i: number): string {
  return GLYPHS[i] ?? `X${i}`;
}

/** Count non-overlapping occurrences of each digram, left to right. */
export function digramCounts(s: string[]): Map<string, number> {
  const counts = new Map<string, number>();
  const lastEnd = new Map<string, number>();
  for (let i = 0; i + 1 < s.length; i++) {
    const k = `${s[i]}\u0000${s[i + 1]}`;
    if ((lastEnd.get(k) ?? -1) > i) continue; // overlaps the previous occurrence (e.g. "aaa")
    counts.set(k, (counts.get(k) ?? 0) + 1);
    lastEnd.set(k, i + 2);
  }
  return counts;
}

/** One fold step. Most frequent digram first (Re-Pair); ties by first occurrence. */
export function foldOnce(st: FoldState): FoldState {
  if (st.current.length < 2) return st;
  const counts = digramCounts(st.current);
  let best = '';
  let bestN = 0;
  for (let i = 0; i + 1 < st.current.length; i++) {
    const k = `${st.current[i]}\u0000${st.current[i + 1]}`;
    const n = counts.get(k) ?? 0;
    if (n > bestN) {
      best = k;
      bestN = n;
    }
  }
  const [left, right] = best.split('\u0000') as [string, string];
  const glyph = freshGlyph(st.rules.length);
  const next: string[] = [];
  let count = 0;
  for (let i = 0; i < st.current.length; i++) {
    if (i + 1 < st.current.length && st.current[i] === left && st.current[i + 1] === right) {
      next.push(glyph);
      count++;
      i++;
    } else next.push(st.current[i]!);
  }
  return { ...st, current: next, rules: [...st.rules, { glyph, left, right, count }] };
}

export function foldAll(st: FoldState): FoldState {
  let s = st;
  while (s.current.length > 1) s = foldOnce(s);
  return s;
}

/** Undo the most recent fold (one stratum up). */
export function unfoldOnce(st: FoldState): FoldState {
  const rule = st.rules[st.rules.length - 1];
  if (!rule) return st;
  const next = st.current.flatMap((g) => (g === rule.glyph ? [rule.left, rule.right] : [g]));
  return { ...st, current: next, rules: st.rules.slice(0, -1) };
}

/** Fully expand a symbol through the rule set. */
export function expand(symbol: string, rules: FoldRule[]): string[] {
  const r = rules.find((x) => x.glyph === symbol);
  if (!r) return [symbol];
  return [...expand(r.left, rules), ...expand(r.right, rules)];
}

export function unfoldAll(st: FoldState): string[] {
  return st.current.flatMap((g) => expand(g, st.rules));
}

/** Grammar size: symbols in the current word plus two per rule. */
export function grammarSize(st: FoldState): number {
  return st.current.length + 2 * st.rules.length;
}
