// Interval geometry on the pitch-class circle ℤ/12 (established: see
// Tymoczko, A Geometry of Music, 2011; Lewin, Generalized Musical Intervals and
// Transformations, 1987).
//
// Repeatedly stepping by an interval of k semitones visits the cyclic subgroup
// ⟨k⟩ ⊆ ℤ/12. Its size is 12 / gcd(12, k): stepping by 7 (a perfect fifth)
// visits all twelve classes; stepping by 4 (a major third) visits three.
// The campus uses that orbit length as the number of repeated arches and lights.

import { gcdInt, mod } from './rational';

export const PITCH_NAMES = ['C', 'C♯', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B'];

export const INTERVAL_NAMES: Record<number, string> = {
  0: 'unison',
  1: 'minor second',
  2: 'major second',
  3: 'minor third',
  4: 'major third',
  5: 'perfect fourth',
  6: 'tritone',
  7: 'perfect fifth',
  8: 'minor sixth',
  9: 'major sixth',
  10: 'minor seventh',
  11: 'major seventh',
};

/** Simple just-intonation ratios commonly compared with 12-tone equal temperament. */
export const JUST_RATIOS: Record<number, [number, number]> = {
  0: [1, 1],
  1: [16, 15],
  2: [9, 8],
  3: [6, 5],
  4: [5, 4],
  5: [4, 3],
  6: [45, 32],
  7: [3, 2],
  8: [8, 5],
  9: [5, 3],
  10: [16, 9],
  11: [15, 8],
};

export function orbit(start: number, k: number, n = 12): number[] {
  const out: number[] = [];
  let x = mod(start, n);
  do {
    out.push(x);
    x = mod(x + k, n);
  } while (x !== mod(start, n) && out.length <= n);
  return out;
}

export function orbitLength(k: number, n = 12): number {
  const g = gcdInt(mod(k, n), n);
  return n / (g === 0 ? n : g);
}

/** Equal-tempered frequency of MIDI note m, with A4 (m = 69) = 440 Hz. */
export function frequency(midi: number, a4 = 440): number {
  return a4 * 2 ** ((midi - 69) / 12);
}

export function cents(ratio: number): number {
  return 1200 * Math.log2(ratio);
}

export interface IntervalAnalysis {
  k: number;
  name: string;
  orbit: number[];
  orbitLength: number;
  gcd: number;
  starPolygon: string;
  equalTemperedRatio: number;
  justRatio: [number, number];
  centsDeviation: number;
  /** Hue (degrees) for the campus lights: the pitch-class circle mapped to the colour circle. */
  hue: number;
}

export function analyseInterval(k: number): IntervalAnalysis {
  const kk = mod(k, 12);
  const g = gcdInt(kk, 12) || 12;
  const just = JUST_RATIOS[kk]!;
  const et = 2 ** (kk / 12);
  return {
    k: kk,
    name: INTERVAL_NAMES[kk]!,
    orbit: orbit(0, kk),
    orbitLength: orbitLength(kk),
    gcd: g,
    starPolygon: kk === 0 ? 'a single point (the walk never leaves C)' : g === 1 ? `{12/${kk}}` : `${g} disjoint copies of {${12 / g}/${kk / g}}`,
    equalTemperedRatio: et,
    justRatio: just,
    centsDeviation: cents(et) - cents(just[0] / just[1]),
    hue: (kk * 30) % 360,
  };
}
