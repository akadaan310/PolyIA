/**
 * Written variants that fold to a base letter.
 *
 * Hamza-bearing forms, tāʾ marbūṭa and alif maqṣūra are all later marking
 * conventions laid over a base letter. Folding them is the first step of the
 * projection: it undoes the marking layer that is not i'jām.
 */

export const ARABIC_TATWEEL = "ـ";
export const TA_MARBUTA = "ة";
export const ALIF_MAQSURA = "ى";
export const HAMZA = "ء";

/** Written form → the base letter it is written on. */
export const HAMZA_FOLD: Record<string, string> = {
  "أ": "ا", // hamza above alif
  "إ": "ا", // hamza below alif
  "آ": "ا", // madda above alif
  "ٱ": "ا", // wasla above alif
  "ؤ": "و", // hamza on waw
  "ئ": "ي", // hamza on ya
  "ء": "ا", // bare hamza — carried on alif in the skeleton
};

/** True when the character is a hamza-bearing variant rather than a base letter. */
export const isHamzaVariant = (ch: string): boolean => ch in HAMZA_FOLD;

/**
 * What each variant contributes beyond its base, for display. These are
 * marks in exactly the sense Layer 4 means: distinctions written onto a
 * skeleton that the skeleton itself does not carry.
 */
export const VARIANT_NOTE: Record<string, string> = {
  "أ": "hamza above",
  "إ": "hamza below",
  "آ": "madda",
  "ٱ": "wasla",
  "ؤ": "hamza on wāw",
  "ئ": "hamza on yāʾ",
  "ء": "bare hamza",
  "ة": "tāʾ marbūṭa — hāʾ with two dots",
  "ى": "alif maqṣūra — the dotless yāʾ",
};
