/**
 * Normalization and projection: modern written Arabic → the rasm.
 *
 * This is the pipeline the whole app is built on. Modern Arabic is the
 * fully-bound state; the skeleton is the unbound one. Because we start from
 * the bound state we hold the ground truth, which is what lets the engine
 * show the architecture *recovering* what the projection discarded.
 */

import {
  ARABIC_TATWEEL, HAMZA_FOLD, TA_MARBUTA, ALIF_MAQSURA,
} from "./variants";
import {
  TASHKIL, isClosed, isLetter, skeletonOf, classesFor,
  type Position,
} from "./alphabet";
import type { Glyph, Word } from "./types";

export { ARABIC_TATWEEL };

/**
 * Fold a written character to its base letter.
 * Returns null for anything that is not a letter of the alphabet.
 */
export function fold(ch: string): string | null {
  if (ch in HAMZA_FOLD) return HAMZA_FOLD[ch];
  if (ch === TA_MARBUTA) return "ه";
  if (ch === ALIF_MAQSURA) return "ي";
  return isLetter(ch) ? ch : null;
}

/** Strip tashkīl and tatweel, leaving only letters. */
export function stripMarks(text: string): string {
  return [...text]
    .filter((ch) => !TASHKIL.has(ch) && ch !== ARABIC_TATWEEL)
    .join("");
}

/** Split a run of text into words on whitespace and punctuation. */
export function tokenize(text: string): string[] {
  return text
    .split(/[\s،؛؟.,;:!?()[\]{}"'«» -⁯]+/u)
    .filter((t) => t.length > 0);
}

/**
 * Resolve each letter's position from the joining rules.
 *
 * A letter feeds the next iff it is not closed. A letter receives from the
 * previous iff the previous exists and is not closed. Two binary conditions,
 * four positions — spec/02-face.md §2.2.
 */
export function positionsOf(letters: string[]): Position[] {
  return letters.map((_, i) => {
    const receivesRight = i > 0 && !isClosed(letters[i - 1]);
    const feedsLeft = i < letters.length - 1 && !isClosed(letters[i]);
    if (receivesRight && feedsLeft) return "medial";
    if (receivesRight) return "final";
    if (feedsLeft) return "initial";
    return "isolated";
  });
}

/** Parse one written word into the engine's representation. */
export function parseWord(raw: string): Word {
  const letters: string[] = [];
  const surfaces: string[] = [];
  const markRuns: string[][] = [];
  let voweled = false;

  for (const ch of raw) {
    if (ch === ARABIC_TATWEEL) continue;
    if (TASHKIL.has(ch)) {
      voweled = true;
      if (markRuns.length > 0) markRuns[markRuns.length - 1].push(ch);
      continue;
    }
    const base = fold(ch);
    if (base === null) continue;
    letters.push(base);
    surfaces.push(ch);
    markRuns.push([]);
  }

  const positions = positionsOf(letters);

  const glyphs: Glyph[] = letters.map((letter, i) => {
    const position = positions[i];
    const skeleton = skeletonOf(letter, position);
    const table = classesFor(position);
    return {
      letter,
      surface: surfaces[i],
      marks: markRuns[i],
      position,
      skeleton,
      domain: table[skeleton] ?? [letter],
      index: i,
    };
  });

  return {
    raw,
    letters,
    glyphs,
    skeleton: glyphs.map((g) => g.skeleton).join(""),
    voweled,
  };
}

/** Rebuild a Word from a plain letter string, recomputing positions. */
export function wordFromLetters(letters: string[]): Word {
  return parseWord(letters.join(""));
}

/** Parse a whole composition into words. */
export function parseText(text: string): Word[] {
  return tokenize(text).map(parseWord).filter((w) => w.letters.length > 0);
}

// ---------------------------------------------------------------------------
// Projection and expansion
// ---------------------------------------------------------------------------

/** The rasm of a word — Layer 4's projection. */
export const project = (word: Word): string => word.skeleton;

/** The slot vector: each position's domain. Singletons declare no slot. */
export function slots(word: Word): { index: number; domain: string[] }[] {
  return word.glyphs
    .map((g) => ({ index: g.index, domain: g.domain }))
    .filter((s) => s.domain.length > 1);
}

/** Arity — the number of free variables. spec/04-void.md §4.2. */
export const arity = (word: Word): number => slots(word).length;

/** Degree — the number of ways to bind everything at once. */
export const degree = (word: Word): number =>
  word.glyphs.reduce((acc, g) => acc * g.domain.length, 1);

/** Bits the skeleton withholds. */
export const bitsWithheld = (word: Word): number => Math.log2(degree(word));

/**
 * Expand a skeleton into its candidate set — the Cartesian product of the
 * slot domains laid back into position.
 *
 * Capped, because degree grows multiplicatively and a long word can reach
 * millions. The cap is a display concern only; `degree` reports the truth.
 */
export function expand(word: Word, cap = 5000): { candidates: string[]; truncated: boolean } {
  const domains = word.glyphs.map((g) => g.domain);
  const total = domains.reduce((a, d) => a * d.length, 1);
  const truncated = total > cap;

  let acc: string[] = [""];
  for (const domain of domains) {
    const next: string[] = [];
    for (const prefix of acc) {
      for (const letter of domain) {
        next.push(prefix + letter);
        if (next.length >= cap) break;
      }
      if (next.length >= cap) break;
    }
    acc = next;
  }
  return { candidates: acc, truncated };
}

// ---------------------------------------------------------------------------
// Observables shared across layers
// ---------------------------------------------------------------------------

/** Run-length profile — Layer 7. */
export function profile(letters: string[]): number[] {
  const runs: number[] = [];
  let cur = 0;
  for (const l of letters) {
    cur += 1;
    if (isClosed(l)) {
      runs.push(cur);
      cur = 0;
    }
  }
  if (cur > 0) runs.push(cur);
  return runs;
}

export const profileOf = (word: Word): number[] => profile(word.letters);
