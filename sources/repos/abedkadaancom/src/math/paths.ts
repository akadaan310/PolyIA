// Geometry of linked places: a street path becomes a typed word.
//
// A polyline p₀ … pₙ (in a local metric plane) has segments sᵢ = pᵢ₊₁ − pᵢ and
// signed turn angles θᵢ = atan2(sᵢ × sᵢ₊₁, sᵢ · sᵢ₊₁) ∈ (−π, π], positive to
// the left. Each turn is quantized to the alphabet
//     L (θ > 60°)   l (20° < θ ≤ 60°)   S (|θ| ≤ 20°)   r (−60° ≤ θ < −20°)   R (θ < −60°)
// and the signature is that word, with relative segment lengths and the degree
// of each junction. Two signatures are compared by normalized Levenshtein
// distance (Levenshtein 1966) on the turn words after a chosen normalization.
//
// A geometric correspondence between two paths is a statement about shapes.
// It does not imply any physical, causal or historical connection.

export type Pt = [number, number];
export type Turn = 'L' | 'l' | 'S' | 'r' | 'R';
export type Normalization = 'none' | 'reverse' | 'mirror' | 'reverse+mirror';

export const TURN_THRESHOLDS = { sharp: 60, slight: 20 };

export function signedAngle(u: Pt, v: Pt): number {
  const cross = u[0] * v[1] - u[1] * v[0];
  const dot = u[0] * v[0] + u[1] * v[1];
  return Math.atan2(cross, dot);
}

export function quantizeTurn(rad: number): Turn {
  const d = (rad * 180) / Math.PI;
  if (d > TURN_THRESHOLDS.sharp) return 'L';
  if (d > TURN_THRESHOLDS.slight) return 'l';
  if (d >= -TURN_THRESHOLDS.slight) return 'S';
  if (d >= -TURN_THRESHOLDS.sharp) return 'r';
  return 'R';
}

/** Equirectangular projection to metres about a reference latitude (adequate for paths under a few km). */
export function project(lonLat: Pt[], refLat?: number): Pt[] {
  const R = 6371008.8;
  const lat0 = ((refLat ?? lonLat.reduce((s, p) => s + p[1], 0) / Math.max(1, lonLat.length)) * Math.PI) / 180;
  return lonLat.map(([lon, lat]) => [((lon * Math.PI) / 180) * R * Math.cos(lat0), ((lat * Math.PI) / 180) * R]);
}

/** Drop consecutive duplicate points (zero-length segments have no direction). */
export function dedupe(pts: Pt[], eps = 1e-6): Pt[] {
  const out: Pt[] = [];
  for (const p of pts) {
    const q = out[out.length - 1];
    if (!q || Math.hypot(p[0] - q[0], p[1] - q[1]) > eps) out.push(p);
  }
  return out;
}

export interface PathSignature {
  word: Turn[];
  turnsDeg: number[];
  relLengths: number[];
  totalLength: number;
  totalTurnDeg: number;
  junctionDegrees: number[];
}

export function signature(points: Pt[], junctionDegrees: number[] = []): PathSignature {
  const p = dedupe(points);
  const segs: Pt[] = [];
  for (let i = 0; i + 1 < p.length; i++) segs.push([p[i + 1]![0] - p[i]![0], p[i + 1]![1] - p[i]![1]]);
  const lens = segs.map((s) => Math.hypot(s[0], s[1]));
  const total = lens.reduce((a, b) => a + b, 0);
  const turns: number[] = [];
  for (let i = 0; i + 1 < segs.length; i++) turns.push(signedAngle(segs[i]!, segs[i + 1]!));
  return {
    word: turns.map(quantizeTurn),
    turnsDeg: turns.map((t) => (t * 180) / Math.PI),
    relLengths: lens.map((l) => (total > 0 ? l / total : 0)),
    totalLength: total,
    totalTurnDeg: (turns.reduce((a, b) => a + b, 0) * 180) / Math.PI,
    junctionDegrees,
  };
}

const MIRROR: Record<Turn, Turn> = { L: 'R', l: 'r', S: 'S', r: 'l', R: 'L' };

/** Traversing a path backwards reverses the word and swaps left/right. */
export function normalize(word: Turn[], n: Normalization): Turn[] {
  let w = word.slice();
  if (n === 'reverse' || n === 'reverse+mirror') w = w.reverse().map((t) => MIRROR[t]);
  if (n === 'mirror' || n === 'reverse+mirror') w = w.map((t) => MIRROR[t]);
  return w;
}

export function levenshtein<T>(a: T[], b: T[]): number {
  const dp = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    let prev = dp[0]!;
    dp[0] = i;
    for (let j = 1; j <= b.length; j++) {
      const tmp = dp[j]!;
      dp[j] = Math.min(dp[j]! + 1, dp[j - 1]! + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1));
      prev = tmp;
    }
  }
  return dp[b.length]!;
}

export interface Correspondence {
  normalization: Normalization;
  distance: number;
  similarity: number;
  exact: boolean;
  status: 'exact' | 'approximate' | 'weak';
}

/** Compare under one normalization. similarity = 1 − d / max(|a|, |b|). */
export function compare(a: PathSignature, b: PathSignature, n: Normalization): Correspondence {
  const wa = a.word;
  const wb = normalize(b.word, n);
  const d = levenshtein(wa, wb);
  const m = Math.max(wa.length, wb.length, 1);
  const similarity = 1 - d / m;
  const exact = d === 0 && wa.length > 0;
  return { normalization: n, distance: d, similarity, exact, status: exact ? 'exact' : similarity >= 0.6 ? 'approximate' : 'weak' };
}

/** The best correspondence over all four normalizations (the path's symmetry group action). */
export function bestCorrespondence(a: PathSignature, b: PathSignature): Correspondence {
  const ns: Normalization[] = ['none', 'reverse', 'mirror', 'reverse+mirror'];
  return ns.map((n) => compare(a, b, n)).sort((x, y) => y.similarity - x.similarity)[0]!;
}

export function wordString(w: Turn[]): string {
  return w.length ? w.join('') : '∅ (straight segment, no turns)';
}
