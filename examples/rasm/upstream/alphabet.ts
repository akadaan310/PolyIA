/**
 * The twenty-eight letters, and every table the layers are built on.
 *
 * Every table here is authored data — the irreducible inventory the engine
 * starts from. Everything else in the engine is derived from these by
 * computation, never by another table.
 *
 * See spec/00-inherited.md for the inventory these tables encode.
 */

// ---------------------------------------------------------------------------
// Orderings (Layer 3)
// ---------------------------------------------------------------------------

/** الترتيب الهجائي — ordered by kinship of shape. */
export const HIJAI = [
  "ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص",
  "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي",
] as const;

/** الترتيب الأبجدي — أبجد هوز حطي كلمن سعفص قرشت ثخذ ضظغ */
export const ABJADI = [
  "ا", "ب", "ج", "د", "ه", "و", "ز", "ح", "ط", "ي", "ك", "ل", "م", "ن",
  "س", "ع", "ف", "ص", "ق", "ر", "ش", "ت", "ث", "خ", "ذ", "ض", "ظ", "غ",
] as const;

export type Letter = (typeof HIJAI)[number];

export const ALPHABET_SIZE = HIJAI.length; // 28

// ---------------------------------------------------------------------------
// Abjad magnitudes (Layer 10)
// ---------------------------------------------------------------------------

const ABJAD_SEQUENCE = [
  1, 2, 3, 4, 5, 6, 7, 8, 9,
  10, 20, 30, 40, 50, 60, 70, 80, 90,
  100, 200, 300, 400, 500, 600, 700, 800, 900,
  1000,
];

export const ABJAD_VALUE: Record<string, number> = Object.fromEntries(
  ABJADI.map((l, i) => [l, ABJAD_SEQUENCE[i]]),
);

// ---------------------------------------------------------------------------
// Shape classes (Layers 0, 4, 8)
//
// The classes are position-dependent. In initial and medial position the
// tooth carries five letters; in final and isolated position ن and ي take
// forms of their own, leaving three.
// ---------------------------------------------------------------------------

export type Position = "initial" | "medial" | "final" | "isolated";

/** Skeleton glyph → the letters that collapse onto it, in medial position. */
export const CLASSES_MEDIAL: Record<string, string[]> = {
  "ٮ": ["ب", "ت", "ث", "ن", "ي"], // ٮ dotless beh — the tooth
  "ح": ["ج", "ح", "خ"],
  "د": ["د", "ذ"],
  "ر": ["ر", "ز"],
  "س": ["س", "ش"],
  "ص": ["ص", "ض"],
  "ط": ["ط", "ظ"],
  "ع": ["ع", "غ"],
  "ٯ": ["ف", "ق"], // ٯ dotless qaf
  "ا": ["ا"],
  "ك": ["ك"],
  "ل": ["ل"],
  "م": ["م"],
  "ه": ["ه"],
  "و": ["و"],
};

/**
 * In final and isolated position the tooth splits: ن takes the deep bowl ں
 * and ي takes the extended ى, leaving ٮ = {ب ت ث}.
 */
export const CLASSES_FINAL: Record<string, string[]> = {
  ...CLASSES_MEDIAL,
  "ٮ": ["ب", "ت", "ث"],
  "ں": ["ن"], // ں dotless noon
  "ى": ["ي"], // ى alef maksura
};

export function classesFor(position: Position): Record<string, string[]> {
  return position === "final" || position === "isolated"
    ? CLASSES_FINAL
    : CLASSES_MEDIAL;
}

/**
 * The common refinement of the medial and final classes.
 *
 * A substitution is silent — invisible on the page — only if it preserves the
 * skeleton in EVERY position. Because ن and ي leave the tooth in final and
 * isolated position, swapping ب↔ن is silent medially and visible finally.
 * The universally silent classes are therefore finer than the medial ones,
 * and this is the table the silent subgroup is actually built on.
 */
export const CLASSES_UNIVERSAL: Record<string, string[]> = {
  "ٮ": ["ب", "ت", "ث"],
  "ں": ["ن"],
  "ى": ["ي"],
  "ح": ["ج", "ح", "خ"],
  "د": ["د", "ذ"],
  "ر": ["ر", "ز"],
  "س": ["س", "ش"],
  "ص": ["ص", "ض"],
  "ط": ["ط", "ظ"],
  "ع": ["ع", "غ"],
  "ٯ": ["ف", "ق"],
  "ا": ["ا"],
  "ك": ["ك"],
  "ل": ["ل"],
  "م": ["م"],
  "ه": ["ه"],
  "و": ["و"],
};

/** letter → skeleton glyph, for a given position. */
export function skeletonOf(letter: string, position: Position): string {
  const table = classesFor(position);
  for (const [glyph, members] of Object.entries(table)) {
    if (members.includes(letter)) return glyph;
  }
  return letter;
}

// ---------------------------------------------------------------------------
// Joining (Layers 2, 7)
// ---------------------------------------------------------------------------

/** المنفصلة — accept a connection from the right, refuse one to the left. */
export const CLOSED = new Set(["ا", "د", "ذ", "ر", "ز", "و"]);

export const isClosed = (l: string) => CLOSED.has(l);
export const valence = (l: string) => (CLOSED.has(l) ? 1 : 2);

/**
 * Unicode presentation forms, so the four faces can actually be rendered.
 * [isolated, final, initial, medial] — the order used by the U+FE70 block.
 * A null entry means the letter has no such face.
 */
export const PRESENTATION: Record<string, [string, string, string | null, string | null]> = {
  "ا": ["ﺍ", "ﺎ", null, null],
  "ب": ["ﺏ", "ﺐ", "ﺑ", "ﺒ"],
  "ت": ["ﺕ", "ﺖ", "ﺗ", "ﺘ"],
  "ث": ["ﺙ", "ﺚ", "ﺛ", "ﺜ"],
  "ج": ["ﺝ", "ﺞ", "ﺟ", "ﺠ"],
  "ح": ["ﺡ", "ﺢ", "ﺣ", "ﺤ"],
  "خ": ["ﺥ", "ﺦ", "ﺧ", "ﺨ"],
  "د": ["ﺩ", "ﺪ", null, null],
  "ذ": ["ﺫ", "ﺬ", null, null],
  "ر": ["ﺭ", "ﺮ", null, null],
  "ز": ["ﺯ", "ﺰ", null, null],
  "س": ["ﺱ", "ﺲ", "ﺳ", "ﺴ"],
  "ش": ["ﺵ", "ﺶ", "ﺷ", "ﺸ"],
  "ص": ["ﺹ", "ﺺ", "ﺻ", "ﺼ"],
  "ض": ["ﺽ", "ﺾ", "ﺿ", "ﻀ"],
  "ط": ["ﻁ", "ﻂ", "ﻃ", "ﻄ"],
  "ظ": ["ﻅ", "ﻆ", "ﻇ", "ﻈ"],
  "ع": ["ﻉ", "ﻊ", "ﻋ", "ﻌ"],
  "غ": ["ﻍ", "ﻎ", "ﻏ", "ﻐ"],
  "ف": ["ﻑ", "ﻒ", "ﻓ", "ﻔ"],
  "ق": ["ﻕ", "ﻖ", "ﻗ", "ﻘ"],
  "ك": ["ﻙ", "ﻚ", "ﻛ", "ﻜ"],
  "ل": ["ﻝ", "ﻞ", "ﻟ", "ﻠ"],
  "م": ["ﻡ", "ﻢ", "ﻣ", "ﻤ"],
  "ن": ["ﻥ", "ﻦ", "ﻧ", "ﻨ"],
  "ه": ["ﻩ", "ﻪ", "ﻫ", "ﻬ"],
  "و": ["ﻭ", "ﻮ", null, null],
  "ي": ["ﻱ", "ﻲ", "ﻳ", "ﻴ"],
};

// ---------------------------------------------------------------------------
// Strokes (Layer 1)
//
// The six atomic motions, and each letter's rasm decomposed into them.
// Decomposition is of the SKELETON — the dots are marks, not strokes, and
// are counted separately.
// ---------------------------------------------------------------------------

export type Stroke = "upright" | "tooth" | "bowl" | "knot" | "tail" | "shoulder";

export const STROKES: Record<Stroke, { ar: string; en: string; character: string }> = {
  upright:  { ar: "الألف",  en: "Upright",  character: "a single vertical descent" },
  tooth:    { ar: "السن",   en: "Tooth",    character: "a short wedge — up, then down" },
  bowl:     { ar: "الحوض",  en: "Bowl",     character: "a concave sweep, open upward" },
  knot:     { ar: "العقدة", en: "Knot",     character: "a closed or near-closed loop" },
  tail:     { ar: "الذيل",  en: "Tail",     character: "an unbounded descent below the line" },
  shoulder: { ar: "الكتف",  en: "Shoulder", character: "a shallow arc riding the line" },
};

export interface LetterMotion {
  strokes: Stroke[];
  lifts: number;
  /** i'jām dots — added marks, not part of the motion. */
  dots: number;
  dotPosition: "above" | "below" | "none";
}

export const MOTION: Record<string, LetterMotion> = {
  "ا": { strokes: ["upright"],                          lifts: 1, dots: 0, dotPosition: "none"  },
  "ب": { strokes: ["bowl"],                             lifts: 1, dots: 1, dotPosition: "below" },
  "ت": { strokes: ["bowl"],                             lifts: 1, dots: 2, dotPosition: "above" },
  "ث": { strokes: ["bowl"],                             lifts: 1, dots: 3, dotPosition: "above" },
  "ج": { strokes: ["shoulder", "bowl"],                 lifts: 1, dots: 1, dotPosition: "below" },
  "ح": { strokes: ["shoulder", "bowl"],                 lifts: 1, dots: 0, dotPosition: "none"  },
  "خ": { strokes: ["shoulder", "bowl"],                 lifts: 1, dots: 1, dotPosition: "above" },
  "د": { strokes: ["shoulder"],                         lifts: 1, dots: 0, dotPosition: "none"  },
  "ذ": { strokes: ["shoulder"],                         lifts: 1, dots: 1, dotPosition: "above" },
  "ر": { strokes: ["tail"],                             lifts: 1, dots: 0, dotPosition: "none"  },
  "ز": { strokes: ["tail"],                             lifts: 1, dots: 1, dotPosition: "above" },
  "س": { strokes: ["tooth", "tooth", "tooth", "bowl"],  lifts: 1, dots: 0, dotPosition: "none"  },
  "ش": { strokes: ["tooth", "tooth", "tooth", "bowl"],  lifts: 1, dots: 3, dotPosition: "above" },
  "ص": { strokes: ["knot", "bowl"],                     lifts: 1, dots: 0, dotPosition: "none"  },
  "ض": { strokes: ["knot", "bowl"],                     lifts: 1, dots: 1, dotPosition: "above" },
  "ط": { strokes: ["knot", "upright"],                  lifts: 1, dots: 0, dotPosition: "none"  },
  "ظ": { strokes: ["knot", "upright"],                  lifts: 1, dots: 1, dotPosition: "above" },
  "ع": { strokes: ["knot", "tail"],                     lifts: 1, dots: 0, dotPosition: "none"  },
  "غ": { strokes: ["knot", "tail"],                     lifts: 1, dots: 1, dotPosition: "above" },
  "ف": { strokes: ["knot", "bowl"],                     lifts: 1, dots: 1, dotPosition: "above" },
  "ق": { strokes: ["knot", "bowl"],                     lifts: 1, dots: 2, dotPosition: "above" },
  "ك": { strokes: ["upright", "shoulder"],              lifts: 1, dots: 0, dotPosition: "none"  },
  "ل": { strokes: ["upright", "bowl"],                  lifts: 1, dots: 0, dotPosition: "none"  },
  "م": { strokes: ["knot", "tail"],                     lifts: 1, dots: 0, dotPosition: "none"  },
  "ن": { strokes: ["bowl"],                             lifts: 1, dots: 1, dotPosition: "above" },
  "ه": { strokes: ["knot"],                             lifts: 1, dots: 0, dotPosition: "none"  },
  "و": { strokes: ["knot", "tail"],                     lifts: 1, dots: 0, dotPosition: "none"  },
  "ي": { strokes: ["bowl"],                             lifts: 1, dots: 2, dotPosition: "below" },
};

// ---------------------------------------------------------------------------
// Articulation — المخارج (Layer 17)
//
// Seventeen points in five zones, ordered from the interior outward.
// ---------------------------------------------------------------------------

export type Zone = "jawf" | "halq" | "lisan" | "shafatan" | "khayshum";

export const ZONES: Record<Zone, { ar: string; en: string }> = {
  jawf:     { ar: "الجوف",     en: "The cavity" },
  halq:     { ar: "الحلق",     en: "The throat" },
  lisan:    { ar: "اللسان",    en: "The tongue" },
  shafatan: { ar: "الشفتان",   en: "The lips" },
  khayshum: { ar: "الخيشوم",   en: "The nose" },
};

export interface ArticulationPoint {
  /** depth index — 0 is deepest, higher is further forward */
  depth: number;
  zone: Zone;
  ar: string;
  en: string;
}

export const POINTS: ArticulationPoint[] = [
  { depth: 0,  zone: "jawf",     ar: "الجوف",              en: "the cavity" },
  { depth: 1,  zone: "halq",     ar: "أقصى الحلق",         en: "deepest throat" },
  { depth: 2,  zone: "halq",     ar: "وسط الحلق",          en: "mid throat" },
  { depth: 3,  zone: "halq",     ar: "أدنى الحلق",         en: "nearest throat" },
  { depth: 4,  zone: "lisan",    ar: "أقصى اللسان",        en: "back of tongue, soft palate" },
  { depth: 5,  zone: "lisan",    ar: "أقصى اللسان الأمامي", en: "back of tongue, hard palate" },
  { depth: 6,  zone: "lisan",    ar: "وسط اللسان",         en: "middle of tongue" },
  { depth: 7,  zone: "lisan",    ar: "حافة اللسان",        en: "edge of tongue, molars" },
  { depth: 8,  zone: "lisan",    ar: "حافة اللسان الأمامية", en: "edge of tongue, gums" },
  { depth: 9,  zone: "lisan",    ar: "طرف اللسان",         en: "tip of tongue" },
  { depth: 10, zone: "lisan",    ar: "طرف اللسان الخلفي",  en: "tip of tongue, drawn back" },
  { depth: 11, zone: "lisan",    ar: "طرف اللسان وأصول الثنايا", en: "tip against upper incisor roots" },
  { depth: 12, zone: "lisan",    ar: "طرف اللسان والثنايا السفلى", en: "tip against lower incisors" },
  { depth: 13, zone: "lisan",    ar: "طرف اللسان وأطراف الثنايا",  en: "tip against upper incisor tips" },
  { depth: 14, zone: "shafatan", ar: "الشفة والثنايا",     en: "lip against upper teeth" },
  { depth: 15, zone: "shafatan", ar: "الشفتان",            en: "both lips" },
  { depth: 16, zone: "khayshum", ar: "الخيشوم",            en: "the nasal cavity" },
];

/** letter → depth index into POINTS. */
export const ARTICULATION: Record<string, number> = {
  "ا": 0,
  "ه": 1,
  "ع": 2, "ح": 2,
  "غ": 3, "خ": 3,
  "ق": 4,
  "ك": 5,
  "ج": 6, "ش": 6, "ي": 6,
  "ض": 7,
  "ل": 8,
  "ن": 9,
  "ر": 10,
  "ط": 11, "د": 11, "ت": 11,
  "ص": 12, "ز": 12, "س": 12,
  "ظ": 13, "ذ": 13, "ث": 13,
  "ف": 14,
  "ب": 15, "م": 15, "و": 15,
};

// ---------------------------------------------------------------------------
// Diacritics (Layers 11, 18) — the marks that are not letters
// ---------------------------------------------------------------------------

export const FATHA = "َ";
export const DAMMA = "ُ";
export const KASRA = "ِ";
export const SUKUN = "ْ";
export const SHADDA = "ّ";
export const FATHATAN = "ً";
export const DAMMATAN = "ٌ";
export const KASRATAN = "ٍ";

export const SHORT_VOWELS = new Set([FATHA, DAMMA, KASRA]);
export const TANWIN = new Set([FATHATAN, DAMMATAN, KASRATAN]);

/** Every combining mark the engine recognizes as tashkīl. */
export const TASHKIL = new Set([
  FATHA, DAMMA, KASRA, SUKUN, SHADDA, FATHATAN, DAMMATAN, KASRATAN,
  "ٓ", "ٔ", "ٕ", "ٖ", "ٗ", "٘", "ٰ",
]);

/** Letters that are written but carry no consonantal weight of their own. */
export const LONG_VOWELS = new Set(["ا", "و", "ي"]);

// ---------------------------------------------------------------------------
// Derived — computed once, never tabulated
// ---------------------------------------------------------------------------

export const HIJAI_INDEX: Record<string, number> = Object.fromEntries(
  HIJAI.map((l, i) => [l, i]),
);

export const ABJADI_INDEX: Record<string, number> = Object.fromEntries(
  ABJADI.map((l, i) => [l, i]),
);

/** letter → its skeleton class members, medial position. */
export const CLASS_OF: Record<string, string[]> = (() => {
  const out: Record<string, string[]> = {};
  for (const members of Object.values(CLASSES_MEDIAL)) {
    for (const l of members) out[l] = members;
  }
  return out;
})();

/** The six letters alone in their class — Layer 15's unmoved alphabet. */
export const UNMOVED: string[] = HIJAI.filter((l) => CLASS_OF[l].length === 1);

export const isLetter = (ch: string) => ch in HIJAI_INDEX;
