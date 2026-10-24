import type { DialogueTurn, DiscourseInput, Evidence, Identity, QuranLocus, QuranRecord, Source, Token } from './types.js';
import { clone, nonempty, record, requireValid, validateEvidence, validateFeatures, validateInput, validateSource } from './validation.js';

/** Canonical Hafs/Cairo ayah enumeration, 114 surahs and 6,236 ayahs. */
export const SURAH_AYAH_COUNTS: readonly number[] = Object.freeze([7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]);
export function quranLocus(surah: number, ayah: number): string {
  requireValid(Number.isInteger(surah) && surah >= 1 && surah <= 114 && Number.isInteger(ayah) && ayah >= 1 && ayah <= SURAH_AYAH_COUNTS[surah - 1], 'Quran locus (canonical surah/ayah range)');
  return `quran:${surah}:${ayah}`;
}
export function parseLocus(locus: string): QuranLocus {
  requireValid(typeof locus === 'string' && /^quran:[1-9]\d{0,2}:[1-9]\d{0,2}$/.test(locus), 'canonical Quran locus syntax');
  const [, s, a] = locus.split(':'); const surah = Number(s); const ayah = Number(a);
  return { id: quranLocus(surah, ayah), surah, ayah };
}
/** Offsets are UTF-16 code units, exactly as used by String.slice and browser selection. */
export function tokenize(text: string, unitId = 'text'): Token[] {
  requireValid(typeof text === 'string' && nonempty(unitId), 'tokenization text/unit id');
  return Array.from(text.matchAll(/\S+/gu), (match, index) => ({ id: `${unitId}:t${index}`, text: match[0], span: { start: match.index!, end: match.index! + match[0].length } }));
}
export const unknownIdentity = (): Identity => ({ id: 'unknown', status: 'unknown' });
function suppliedIdentity(value: string | Identity | undefined): Identity {
  if (value === undefined) return unknownIdentity();
  return typeof value === 'string' ? { id: value, label: value, status: 'known' } : clone(value);
}
export function adaptDialogue(turns: DialogueTurn[], source: Source = { id: 'dialogue:local', kind: 'dialogue', title: 'User-supplied dialogue' }): DiscourseInput {
  requireValid(Array.isArray(turns), 'dialogue turns array'); validateSource(source);
  const input: DiscourseInput = {
    id: source.id, source: clone(source),
    units: turns.map((turn, index) => {
      requireValid(record(turn), 'dialogue turn');
      const id = turn.id ?? `${source.id}:turn:${index}`;
      const evidence: Evidence[] = clone(turn.evidence ?? []);
      if (turn.features || turn.speaker || turn.addressee || turn.referents || turn.narrator) evidence.push({ id: `${id}:annotation`, status: 'observed', sourceId: source.id, method: 'supplied-dialogue-annotation', note: 'Supplied declaration; not independently verified.', confidence: 0.5 });
      return { id, text: turn.text, ...(turn.features ? { features: clone(turn.features) } : {}), attribution: { speaker: suppliedIdentity(turn.speaker), addressee: suppliedIdentity(turn.addressee), narrator: suppliedIdentity(turn.narrator), referents: (turn.referents ?? []).map(suppliedIdentity), frameId: 'root' }, evidence, ...(turn.timestamp ? { timestamp: clone(turn.timestamp) } : {}) };
    }),
  };
  validateInput(input); return input;
}
export function adaptQuran(value: QuranRecord): DiscourseInput {
  requireValid(record(value) && typeof value.text === 'string', 'Quran record/text');
  const id = quranLocus(value.surah, value.ayah);
  requireValid(value.id === undefined || value.id === id, 'Quran record id conflicts with locus');
  const source: Source = typeof value.source === 'string' ? { id: value.source, kind: 'quran' } : clone(value.source ?? { id: 'quran:unspecified', kind: 'quran', title: 'Quran text; source unspecified by caller' });
  validateSource(source);
  const words = tokenize(value.text, id);
  const units = (words.length ? words : [{ id: `${id}:t0`, text: '', span: { start: 0, end: 0 } }]).map((token, index) => ({ id: token.id, text: token.text, span: token.span, features: value.features?.[index] ? clone(value.features[index]) : {}, evidence: [] as Evidence[] }));
  if (value.features !== undefined) {
    requireValid(Array.isArray(value.features), 'Quran features array'); value.features.forEach(validateFeatures);
    const carriesAnnotation = value.features.some(features => Object.keys(features).length > 0);
    requireValid(!carriesAnnotation || value.features.length === units.length, 'Quran features length (nonempty annotations must align with lexical tokens)');
  }
  if (value.morphology !== undefined) {
    requireValid(Array.isArray(value.morphology), 'Quran morphology array'); const seen = new Set<number>();
    for (const annotation of value.morphology) {
      requireValid(record(annotation) && Number.isInteger(annotation.tokenIndex) && annotation.tokenIndex >= 0 && annotation.tokenIndex < units.length && !seen.has(annotation.tokenIndex), 'morphology token index/duplicate');
      validateFeatures(annotation.features); requireValid(Array.isArray(annotation.evidence) && annotation.evidence.length > 0, 'morphology requires attributed evidence'); annotation.evidence.forEach(validateEvidence);
      seen.add(annotation.tokenIndex); units[annotation.tokenIndex].features = clone(annotation.features); units[annotation.tokenIndex].evidence = clone(annotation.evidence);
    }
  }
  const input: DiscourseInput = { id, source, units, metadata: { locus: id, surah: value.surah, ayah: value.ayah, originalText: value.text, featureStatus: value.features || value.morphology ? 'supplied' : 'unavailable' } };
  validateInput(input); return input;
}
