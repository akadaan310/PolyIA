import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { analyze, adaptDialogue, adaptQuran, compose, identity, structuralSignature, topology, perturb, mineMotifs } from '../packages/snad-core/src/index.js';
import type { Analysis, DialogueTurn, Features, Morphism, QuranRecord, Source } from '../packages/snad-core/src/types.js';
import { readCorpus, readMorphology } from './benchmark.js';
import type { MorphologyMap } from './benchmark.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const hash = (text: string) => createHash('sha256').update(text).digest('hex');
const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
const source: Source = { id: 'snad:authored-experiments:v1', kind: 'synthetic', title: 'Authored nonreligious manual features and explicit attribution; not empirical annotation gold' };
const manualEvidence = [{ id: 'manual:v1', status: 'observed' as const, sourceId: source.id, method: 'authored-input-not-inferred' }];
const turns = (rows: DialogueTurn[]): Analysis => analyze(adaptDialogue(rows.map((row, index) => ({ id: `unit:${index}`, evidence: manualEvidence, ...row })), source));
export function independentSample(corpus: readonly QuranRecord[], count = 12) {
  const excluded = new Set(['quran:11:29', 'quran:11:36', 'quran:50:2', 'quran:28:4', 'quran:28:5']);
  return corpus.filter(row => !excluded.has(row.id!)).map(row => ({ id: row.id!, digest: hash(`snad-independent-v1:${row.id}`) })).sort((a, b) => a.digest.localeCompare(b.digest)).slice(0, count);
}

const baselineCases: { id: string; left: DialogueTurn; right: DialogueTurn; gold: boolean; annotation: string }[] = [
  { id: 'unchanged', left: { text: 'tea', speaker: 'A', features: { person: '1' } }, right: { text: 'tea', speaker: 'A', features: { person: '1' } }, gold: false, annotation: 'No typed grammatical or attribution boundary.' },
  { id: 'lexical-only', left: { text: 'tea', speaker: 'A', features: { person: '1' } }, right: { text: 'stone', speaker: 'A', features: { person: '1' } }, gold: false, annotation: 'Surface vocabulary changes while explicit state stays constant.' },
  { id: 'person-only', left: { text: 'I wait', speaker: 'A', features: { person: '1' } }, right: { text: 'you wait', speaker: 'A', features: { person: '2' } }, gold: true, annotation: 'Grammatical person boundary; speaker remains A.' },
  { id: 'speaker-only', left: { text: 'Ready', speaker: 'A', features: { person: '1' } }, right: { text: 'Ready', speaker: 'B', features: { person: '1' } }, gold: true, annotation: 'Explicit authored speaker boundary; grammar constant.' },
  { id: 'number-only', left: { text: 'one', features: { number: 'singular' } }, right: { text: 'several', features: { number: 'plural' } }, gold: true, annotation: 'Supplied grammatical number boundary.' },
  { id: 'tense-only', left: { text: 'waited', features: { tense: 'past' } }, right: { text: 'waits', features: { tense: 'present' } }, gold: true, annotation: 'Supplied tense boundary.' },
  { id: 'addressee-only', left: { text: 'Welcome', speaker: 'A', addressee: 'B' }, right: { text: 'Welcome', speaker: 'A', addressee: 'C' }, gold: true, annotation: 'Explicit authored addressee boundary.' },
  { id: 'combined', left: { text: 'I speak', speaker: 'A', features: { person: '1' } }, right: { text: 'you speak', speaker: 'B', features: { person: '2' } }, gold: true, annotation: 'Both person and explicit speaker boundary.' },
];
function score(predictions: boolean[], gold: boolean[]) {
  let truePositive = 0, falsePositive = 0, trueNegative = 0, falseNegative = 0;
  for (let index = 0; index < gold.length; index++) {
    if (gold[index]) predictions[index] ? truePositive++ : falseNegative++;
    else predictions[index] ? falsePositive++ : trueNegative++;
  }
  const precision = truePositive + falsePositive ? truePositive / (truePositive + falsePositive) : 0;
  const recall = truePositive + falseNegative ? truePositive / (truePositive + falseNegative) : 0;
  return { truePositive, falsePositive, trueNegative, falseNegative, precision, recall, f1: precision + recall ? 2 * precision * recall / (precision + recall) : 0 };
}
export function evaluateBaselines() {
  const examples = baselineCases.map(row => {
    const analysis = turns([row.left, row.right]);
    return { ...row, predictions: { noChange: false, personOnly: row.left.features?.person !== undefined && row.right.features?.person !== undefined && row.left.features.person !== row.right.features.person, speakerOnly: row.left.speaker !== undefined && row.right.speaker !== undefined && row.left.speaker !== row.right.speaker, snad: analysis.transitions.length > 0 }, kinds: analysis.transitions.flatMap(transition => transition.kinds) };
  });
  const gold = examples.map(row => row.gold);
  return {
    goldKind: 'authored explicit synthetic feature/attribution transitions; not Quran ground truth',
    cases: examples.length,
    task: 'Detect any supplied typed grammatical or attribution boundary between two units.',
    metrics: {
      noChange: score(examples.map(row => row.predictions.noChange), gold),
      personOnly: score(examples.map(row => row.predictions.personOnly), gold),
      speakerOnly: score(examples.map(row => row.predictions.speakerOnly), gold),
      snad: score(examples.map(row => row.predictions.snad), gold),
    },
    examples,
    limitation: 'Cases deliberately span supported dimensions. Perfect fit is an API contract demonstration, not evidence of real-world detection accuracy, automatic feature extraction, or superiority on natural text.',
  };
}

function reconstructComposition() {
  let checked = 0, identityChecks = 0;
  const failures: unknown[] = [];
  // Independent reference: path concatenation in a typed directed multigraph.
  const reference = (a: Morphism, b: Morphism): Morphism => ({ from: a.from, to: b.to, path: [...a.path, ...b.path] });
  for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) for (let c = 0; c < 3; c++) for (let d = 0; d < 3; d++) {
    const x = { from: `${a}`, to: `${b}`, path: ['edge:x'] };
    const y = { from: `${b}`, to: `${c}`, path: ['edge:y'] };
    const z = { from: `${c}`, to: `${d}`, path: ['edge:z'] };
    const expected = reference(reference(x, y), z);
    if (!same(compose(compose(x, y), z), expected) || !same(compose(x, compose(y, z)), expected)) failures.push({ x, y, z });
    if (!same(compose(identity(x.from), x), x) || !same(compose(x, identity(x.to)), x)) failures.push({ identityFailure: x });
    checked++; identityChecks += 2;
  }
  return { id: 'R1', name: 'Typed path concatenation agrees with an independent list reference', checked, identityChecks, passed: failures.length === 0, failures, scope: '81 composable triples over 3 vertices plus 162 identity checks. Finite regression; not a new categorical theorem.' };
}
function reconstructTopology() {
  let checked = 0;
  const failures: unknown[] = [];
  for (let n = 0; n <= 8; n++) for (let mask = 0; mask < 2 ** Math.max(0, n - 1); mask++) {
    const units = Array.from({ length: n }, (_, index) => `u${index}`);
    const edges = units.slice(1).flatMap((to, index) => mask & (1 << index) ? [{ from: units[index], to }] : []);
    // Every subset of a simple path is a forest: each edge merges two components.
    const expected = { vertices: n, edges: edges.length, components: n - edges.length, cycleRank: 0, density: n > 1 ? edges.length / (n * (n - 1)) : 0, meanOutDegree: n ? edges.length / n : 0 };
    const actual = topology(units, edges);
    if (!same(actual, expected)) failures.push({ n, mask, actual, expected });
    checked++;
  }
  const triangle = topology(['a', 'b', 'c'], [{ from: 'a', to: 'b' }, { from: 'b', to: 'c' }, { from: 'a', to: 'c' }]);
  if (triangle.cycleRank !== 1 || triangle.components !== 1) failures.push({ triangle });
  checked++;
  return { id: 'R2', name: 'Weak graph component and cycle summaries agree with forest edge counting', checked, passed: failures.length === 0, failures, scope: 'All edge subsets of paths with 0–8 vertices plus one triangle. Topology summarizes the constructed graph, not the semantics of a conversation.' };
}
function reconstructRenaming() {
  let checked = 0;
  const failures: unknown[] = [];
  for (let speakers = 0; speakers < 16; speakers++) for (let persons = 0; persons < 16; persons++) {
    const rows: DialogueTurn[] = Array.from({ length: 4 }, (_, index) => ({ text: `word${index}`, speaker: speakers & (1 << index) ? 'A' : 'B', features: { person: persons & (1 << index) ? '1' : '2' } }));
    const renamed = rows.map(row => ({ ...row, text: 'replacement', speaker: row.speaker === 'A' ? 'renamed:X' : 'renamed:Y' }));
    if (structuralSignature(turns(rows)) !== structuralSignature(turns(renamed))) failures.push({ speakers, persons });
    checked++;
  }
  return { id: 'R3', name: 'Restricted signatures preserve bijective identity renaming and lexical replacement', checked, passed: failures.length === 0, failures, scope: '256 authored four-unit binary-person/binary-speaker paths. This is structural equivalence under the documented representation, not semantic equivalence.' };
}

interface OriginalWord { idx: number; n: number; text: string; person: number | null }
interface OriginalSeam { at: number; fromWord: number; from: number; to: number; person: boolean; [key: string]: unknown }
export interface OriginalFixture { source: Record<string, unknown>; cases: { locus: string; purpose: string; input: { morphologyRows: string[]; context: string }; original: { words: OriginalWord[]; seams: OriginalSeam[] } }[]; syntheticFailureCases?: unknown[] }
/** Independent conservative feature projection; it deliberately does not copy source detector role heuristics. */
function independentPrincipalFeatures(rows: string[]): Map<number, Features> {
  const candidates = new Map<number, { priority: number; features: Features }[]>();
  for (const row of rows) {
    const [locus, , cls, raw = ''] = row.split('\t');
    const fields = locus.split(':').map(Number);
    const n = fields[1];
    const tags = raw.split('|');
    const personTag = tags.find(tag => /^[123](?:M|F)?(?:S|D|P)$/.test(tag));
    if (!personTag || (!Number.isInteger(n))) continue;
    const standalonePronoun = tags.includes('PRON') && !tags.includes('SUFF') && !tags.includes('PREF');
    if (cls !== 'V' && !standalonePronoun) continue;
    const features: Features = { person: personTag[0] as '1' | '2' | '3' };
    const list = candidates.get(n) ?? [];
    list.push({ priority: cls === 'V' ? 0 : 1, features }); candidates.set(n, list);
  }
  return new Map([...candidates].map(([n, values]) => {
    const bestPriority = Math.min(...values.map(value => value.priority));
    const best = values.filter(value => value.priority === bestPriority);
    return [n, new Set(best.map(value => value.features.person)).size === 1 ? best[0].features : {}];
  }));
}
function differential(fixture: OriginalFixture) {
  const cases = fixture.cases.map(row => {
    const features = independentPrincipalFeatures(row.input.morphologyRows);
    const input = adaptDialogue(row.original.words.map(word => ({ id: `word:${word.n}`, text: word.text, features: features.get(word.n) ?? {} })), { id: 'original:qac-fixture', kind: 'compatibility-input' });
    const analysis = analyze(input);
    const byGlobal = new Map(row.original.words.map(word => [word.idx, `word:${word.n}`]));
    const originalPersonEndpoints = row.original.seams.filter(seam => seam.person).map(seam => ({ from: byGlobal.get(seam.fromWord) ?? `surah-context:${seam.fromWord}`, to: byGlobal.get(seam.at) ?? `surah-context:${seam.at}`, fromPerson: `${seam.from}`, toPerson: `${seam.to}` }));
    const independentPersonEndpoints = analysis.transitions.filter(transition => transition.kinds.includes('person')).map(transition => ({ from: transition.from, to: transition.to, fromPerson: analysis.units.find(unit => unit.id === transition.from)!.features.person!, toPerson: analysis.units.find(unit => unit.id === transition.to)!.features.person! }));
    return { locus: row.locus, purpose: row.purpose, originalPersonEndpoints, independentPersonEndpoints, matches: same(originalPersonEndpoints, independentPersonEndpoints), originalSeams: row.original.seams, context: row.input.context };
  });
  return { source: fixture.source, scope: 'Independent adjacent token comparison versus original surah-context carried-person seams; mismatch is not an accuracy judgment.', projection: 'Read morphology-row person tags for verbs or standalone pronouns; prefer verbs; omit conflicting principal person tags. No inherited role assignment, weighting, or carried-person heuristic.', cases, matchingCases: cases.filter(row => row.matches).length, mismatchingCases: cases.filter(row => !row.matches).length, originalFailureCases: fixture.syntheticFailureCases ?? [] };
}

function perturbationForge() {
  const forgeRows: DialogueTurn[] = [
    { id: 'forge:0', text: 'I wait', speaker: 'A', features: { person: '1', number: 'singular' } },
    { id: 'forge:1', text: 'you wait', speaker: 'A', features: { person: '2', number: 'singular' } },
    { id: 'forge:2', text: 'you wait', speaker: 'B', features: { person: '2', number: 'singular' } },
    { id: 'forge:3', text: 'they wait', speaker: 'B', features: { person: '3', number: 'plural' } },
  ];
  const input = adaptDialogue(forgeRows.map((row, index) => ({ ...row, evidence: [{ id: `forge:e${index}`, status: 'observed' as const, method: 'authored-input-not-inferred', sourceId: source.id, confidence: index === 1 ? 0.2 : 0.9 }] })), source);
  const before = JSON.stringify(input);
  const reference = analyze(input);
  const trials = (['drop-features', 'mask-speakers', 'reverse-units'] as const).map(kind => {
    const ablated = perturb(input, { kind, seed: 6236 });
    const analysis = analyze(ablated);
    return { kind, seed: 6236, replayDeterministic: same(ablated, perturb(input, { kind, seed: 6236 })), transitions: analysis.transitions.length, kinds: analysis.transitions.map(transition => transition.kinds), signature: structuralSignature(analysis), unknownSpeakers: analysis.units.filter(unit => unit.attribution.speaker.status === 'unknown').length };
  });
  return { referenceTransitions: reference.transitions.length, referenceKinds: reference.transitions.map(row => row.kinds), trials, originalUnchanged: before === JSON.stringify(input), minimumEvidenceConfidence: Math.min(...reference.transitions.map(row => row.confidence)), confidenceMeaning: reference.transitions[0].confidenceMeaning, confidenceScope: 'Minimum supplied evidence grade (plus adapter annotation grade), never a probability of speaker truth. No confidence calibration data available.', motifs: mineMotifs([reference, analyze(input)], 2), motifScope: 'Overlapping two-transition strings counted in two repeated authored inputs; a motif count is not a learned discourse grammar.' };
}

export function runExperiments(corpus: readonly QuranRecord[], fixture: OriginalFixture, morphology: MorphologyMap = {}) {
  const baselines = evaluateBaselines();
  const reconstructions = [reconstructComposition(), reconstructTopology(), reconstructRenaming()];
  const crossRows: { language: string; text: string[] }[] = [
    { language: 'English', text: ['I wait.', 'You wait.', 'They wait.'] },
    { language: 'Arabic', text: ['أنا أنتظر.', 'أنت تنتظر.', 'هم ينتظرون.'] },
    { language: 'Spanish', text: ['Yo espero.', 'Tú esperas.', 'Ellos esperan.'] },
  ];
  const languageAnalyses = crossRows.map(row => turns(row.text.map((text, index) => ({ text, speaker: index === 2 ? 'B' : 'A', features: { person: `${index + 1}` as '1' | '2' | '3' } }))));
  const crossLinguistic = crossRows.map((row, index) => ({ ...row, manualFeatures: true, manuallySuppliedPersons: ['1', '2', '3'], manuallySuppliedSpeakers: ['A', 'A', 'B'], signature: structuralSignature(languageAnalyses[index]), signatureMatchesEnglish: structuralSignature(languageAnalyses[0]) === structuralSignature(languageAnalyses[index]), transitions: languageAnalyses[index].transitions.map(transition => transition.kinds), scope: 'Authored nonreligious inputs with manual feature labels. No automatic translation, parsing, cross-language generalization, or native-speaker validation claimed.' }));
  const lexicalGrid = [true, false].flatMap(sharedVocabulary => [false, true].map(changeSpeaker => {
    const leftText = 'tea cup', rightText = sharedVocabulary ? 'tea cup' : 'stone moon';
    const result = turns([{ text: leftText, speaker: 'A' }, { text: rightText, speaker: changeSpeaker ? 'B' : 'A' }]);
    const leftSet = new Set(leftText.toLowerCase().split(/\s+/u)), rightSet = new Set(rightText.toLowerCase().split(/\s+/u));
    const independentOverlap = [...leftSet].filter(token => rightSet.has(token)).length / new Set([...leftSet, ...rightSet]).size;
    return { sharedVocabulary, changeSpeaker, lexicalContinuity: result.transitions[0]?.lexicalContinuity ?? independentOverlap, continuityMeasuredOn: result.transitions.length ? 'typed transition lexical Jaccard' : 'independent set overlap for the no-transition pair', transitions: result.transitions.length, attributionChange: result.transitions.some(transition => transition.attributionChange) };
  }));
  const personOnly = turns([{ text: 'I', features: { person: '1' } }, { text: 'you', features: { person: '2' } }]);
  const empty = turns([{ text: '' }, { text: 'word' }]);
  const identicalWords = turns([{ text: 'same', speaker: 'A' }, { text: 'same', speaker: 'B' }]);
  const lexicalOnly = turns([{ text: 'tea', speaker: 'A' }, { text: 'stone', speaker: 'A' }]);
  const orderRows = [{ text: 'first content', speaker: 'A', features: { person: '1' as const } }, { text: 'second content', speaker: 'B', features: { person: '1' as const } }];
  const forward = turns(orderRows), backward = turns([...orderRows].reverse());
  const separate = turns([{ text: 'a', speaker: 'A' }, { text: 'b', speaker: 'B' }, { text: 'c', speaker: 'A' }]);
  const collapsed = turns([{ text: 'a', speaker: 'X' }, { text: 'b', speaker: 'X' }, { text: 'c', speaker: 'X' }]);
  const speakerPath = turns([{ text: 'a', speaker: 'A' }, { text: 'b', speaker: 'B' }]);
  const negativeControls = [
    { id: 'NC1', claimRejected: 'A grammatical-person change proves a speaker change.', passed: personOnly.units.every(unit => unit.attribution.speaker.status === 'unknown') && !personOnly.transitions.some(transition => transition.kinds.includes('speaker')), witness: personOnly.transitions.map(transition => transition.kinds) },
    { id: 'NC2', claimRejected: 'Missing or empty features justify a detected grammar boundary.', passed: empty.transitions.length === 0, witness: { transitions: empty.transitions.length, unknownSpeakers: empty.units.every(unit => unit.attribution.speaker.status === 'unknown') } },
    { id: 'NC3', claimRejected: 'Identical words guarantee attribution continuity.', passed: identicalWords.transitions[0].lexicalContinuity === 1 && identicalWords.transitions[0].attributionChange, witness: identicalWords.transitions[0] },
    { id: 'NC4', claimRejected: 'Changed words require a typed grammatical or attribution transition.', passed: lexicalOnly.transitions.length === 0, witness: { left: 'tea', right: 'stone', transitions: lexicalOnly.transitions.length } },
    { id: 'NC5', claimRejected: 'A restricted structural signature recovers surface order or speaker names.', passed: structuralSignature(forward) === structuralSignature(backward), witness: { forward: orderRows, reverse: [...orderRows].reverse(), sharedSignature: structuralSignature(forward) } },
    { id: 'NC6', claimRejected: 'Any identity renaming, including many-to-one collapse, preserves structural equivalence.', passed: structuralSignature(separate) !== structuralSignature(collapsed), witness: { original: structuralSignature(separate), collapsed: structuralSignature(collapsed) } },
    { id: 'NC7', claimRejected: 'Graph topology alone identifies the kind of discourse boundary.', passed: same(personOnly.topology, speakerPath.topology) && !same(personOnly.transitions[0].kinds, speakerPath.transitions[0].kinds), witness: { sharedTopology: personOnly.topology, firstKinds: personOnly.transitions[0].kinds, secondKinds: speakerPath.transitions[0].kinds } },
  ];
  const diff = differential(fixture);
  const samples = independentSample(corpus);
  const passageSummary = (id: string) => {
    const record = corpus.find(row => row.id === id)!;
    const annotation = morphology[id];
    const analysis = analyze(adaptQuran({ ...record, morphology: annotation?.morphology }));
    return { id, status: analysis.status, originalText: record.text, sourceTextSha256: hash(record.text), morphologyStatus: annotation?.status ?? 'not-supplied', featureUnits: analysis.units.filter(unit => Object.keys(unit.features).length > 0).length, sourceTokenCount: record.text.match(/\S+/gu)?.length ?? 0, transitions: analysis.transitions.map(transition => ({ from: transition.from, to: transition.to, kinds: transition.kinds })), attributionChanges: analysis.transitions.filter(transition => transition.attributionChange).length, unknownSpeakers: analysis.units.filter(unit => unit.attribution.speaker.status === 'unknown').length, wholeCorpusStatusReference: `evidence/corpus-status.json#${id}` };
  };
  const hypotheses = [
    { id: 'H1', claim: 'For all composable typed finite paths, concatenation is associative.', status: 'finite-support', falsifier: 'A composable triple whose two parenthesizations have different endpoints or edge sequences.', evidence: 'R1' },
    { id: 'H2', claim: 'For every typed path, the empty path at each endpoint acts as identity.', status: 'finite-support', falsifier: 'A path changed by composition with its matching empty endpoint path.', evidence: 'R1' },
    { id: 'H3', claim: 'Every bijective identity renaming and text replacement preserves this restricted signature when features, identity partitions, and quotation nesting are fixed.', status: 'finite-support', falsifier: 'A generated partition-preserving rename or lexical replacement with a different signature.', evidence: 'R3' },
    { id: 'H4', claim: 'All edge subsets of a simple n-vertex path have n−m weak components and cycle rank zero.', status: 'finite-support', falsifier: 'An enumerated path subset with a different weak component count or positive cycle rank.', evidence: 'R2' },
    { id: 'H5', claim: 'Many-to-one speaker renaming always preserves structural equivalence.', status: 'rejected', falsifier: 'An A,B,A speaker pattern collapsed to X,X,X changes signature.', evidence: 'NC6' },
    { id: 'H6', claim: 'Reversing a nonidentical two-unit discourse always changes the restricted signature.', status: 'rejected', falsifier: 'Homogeneous features and a two-speaker switch produce equal forward/reverse signatures.', evidence: 'NC5' },
    { id: 'H7', claim: 'A person-only baseline detects all types of explicitly annotated boundary in the authored gold set.', status: 'rejected', falsifier: 'A gold speaker, number, tense, or addressee boundary missed by person-only.', evidence: 'baselines' },
    { id: 'H8', claim: 'Lexical continuity equal to one guarantees no attribution change.', status: 'rejected', falsifier: 'Identical text with an explicit speaker change.', evidence: 'NC3' },
    { id: 'H9', claim: 'Topology alone uniquely determines the typed transition sequence.', status: 'rejected', falsifier: 'A person-only path and a speaker-only path with identical topology.', evidence: 'NC7' },
    { id: 'H10', claim: 'On a preregistered held-out expert-annotated multilingual dialogue set with independently supplied input features, typed boundary detection reaches F1 ≥ 0.90.', status: 'untested', falsifier: 'Held-out F1 below 0.90 using the frozen input/label protocol.', evidence: 'No held-out expert corpus, independent annotations, or human validation available; authored examples do not test this claim.' },
  ].map(row => ({ ...row, epistemicStatus: row.status === 'rejected' ? 'rejected' : 'conjecture' }));
  const observations = [
    { id: 'O01', statement: 'The input fixture contains exactly 6236 records.', supported: corpus.length === 6236, value: corpus.length, evidence: 'inputSummary.ayahs' },
    { id: 'O02', statement: 'All 114 surahs are represented.', supported: new Set(corpus.map(row => row.surah)).size === 114, value: new Set(corpus.map(row => row.surah)).size, evidence: 'inputSummary.surahs' },
    { id: 'O03', statement: 'The source fixture includes 204 ayahs below three surface tokens.', supported: corpus.filter(row => (row.text.match(/\S+/gu)?.length ?? 0) < 3).length === 204, value: corpus.filter(row => (row.text.match(/\S+/gu)?.length ?? 0) < 3).length, evidence: 'inputSummary.shortAyahsUnder3Tokens' },
    { id: 'O04', statement: 'The independent ranked sample contains twelve passages outside the five prescribed loci.', supported: samples.length === 12, value: samples.map(row => row.id), evidence: 'independentSampling' },
    { id: 'O05', statement: 'The authored boundary gold has six positive and two negative pairs.', supported: baselines.metrics.snad.truePositive === 6 && baselines.metrics.snad.trueNegative === 2, value: baselines.cases, evidence: 'baselines.examples' },
    { id: 'O06', statement: 'No-change misses six authored typed boundaries.', supported: baselines.metrics.noChange.falseNegative === 6, value: baselines.metrics.noChange.falseNegative, evidence: 'baselines.metrics.noChange' },
    { id: 'O07', statement: 'Person-only misses four authored typed boundaries.', supported: baselines.metrics.personOnly.falseNegative === 4, value: baselines.metrics.personOnly.falseNegative, evidence: 'baselines.metrics.personOnly' },
    { id: 'O08', statement: 'Speaker-only misses four authored typed boundaries.', supported: baselines.metrics.speakerOnly.falseNegative === 4, value: baselines.metrics.speakerOnly.falseNegative, evidence: 'baselines.metrics.speakerOnly' },
    { id: 'O09', statement: 'The manually labelled three-language paths share the documented restricted signature.', supported: crossLinguistic.every(row => row.signatureMatchesEnglish), value: 3, evidence: 'crossLinguistic' },
    { id: 'O10', statement: 'The 81 finite composable triples agree with independent list concatenation.', supported: reconstructions[0].passed, value: reconstructions[0].checked, evidence: 'reconstructions.R1' },
    { id: 'O11', statement: 'Forest edge-counting predictions match every enumerated path subset and the triangle control.', supported: reconstructions[1].passed, value: reconstructions[1].checked, evidence: 'reconstructions.R2' },
    { id: 'O12', statement: 'All 256 generated bijective speaker renamings plus lexical replacements preserve signature.', supported: reconstructions[2].passed, value: reconstructions[2].checked, evidence: 'reconstructions.R3' },
    { id: 'O13', statement: 'A person transition can leave every speaker unresolved.', supported: negativeControls[0].passed, value: personOnly.units.map(unit => unit.attribution.speaker.status), evidence: 'negativeControls.NC1' },
    { id: 'O14', statement: 'Empty and missing features can produce a valid zero-transition analysis.', supported: negativeControls[1].passed, value: empty.transitions.length, evidence: 'negativeControls.NC2' },
    { id: 'O15', statement: 'Identical text can coincide with an explicitly supplied attribution change.', supported: negativeControls[2].passed, value: identicalWords.transitions[0].lexicalContinuity, evidence: 'negativeControls.NC3' },
    { id: 'O16', statement: 'Disjoint text alone does not induce a typed boundary.', supported: negativeControls[3].passed, value: lexicalOnly.transitions.length, evidence: 'negativeControls.NC4' },
    { id: 'O17', statement: 'A homogeneous-feature two-speaker path can collide with its reversal under the restricted signature.', supported: negativeControls[4].passed, value: true, evidence: 'selfCommissioned' },
    { id: 'O18', statement: 'Noninjective speaker collapse can destroy structural equivalence.', supported: negativeControls[5].passed, value: true, evidence: 'negativeControls.NC6' },
    { id: 'O19', statement: 'Equal path topology can conceal distinct typed boundary kinds.', supported: negativeControls[6].passed, value: true, evidence: 'negativeControls.NC7' },
    { id: 'O20', statement: 'The adjacent-token independent detector and carried-person source detector disagree on at least one pinned case.', supported: diff.mismatchingCases > 0, value: diff.mismatchingCases, evidence: 'differential.cases' },
  ].map(row => ({ ...row, status: 'observation', novelty: 'Not claimed; fixture/computational observation only.' }));
  return {
    schemaVersion: 'snad.experiments.v1',
    seed: 6236,
    inputSummary: { ayahs: corpus.length, surahs: new Set(corpus.map(row => row.surah)).size, shortAyahsUnder3Tokens: corpus.filter(row => (row.text.match(/\S+/gu)?.length ?? 0) < 3).length, canonicalJsonSha256: hash(JSON.stringify(corpus)), morphologyCanonicalJsonSha256: Object.keys(morphology).length ? hash(JSON.stringify(morphology)) : null, morphologyProvenance: 'data/quran.morphology.provenance.json', originalFixtureCanonicalJsonSha256: hash(JSON.stringify(fixture)) },
    independentSampling: { method: 'Twelve smallest SHA256(seed + canonical locus) digests; excludes the five prescribed loci; independent of legacy ranking and outcome.', seed: 'snad-independent-v1:', samples, analyses: samples.map(row => passageSummary(row.id)) },
    requiredPassages: ['quran:11:29', 'quran:11:36', 'quran:50:2', 'quran:28:4', 'quran:28:5'].map(passageSummary),
    baselines, reconstructions, crossLinguistic, lexicalGrid, negativeControls, perturbationForge: perturbationForge(),
    selfCommissioned: { question: 'Does the restricted signature retain the order of homogeneous-feature turns whose two speaker identities are exchangeable?', commissionedBy: 'Independent experiment design during this build; not a prescribed corpus example.', signatureCollidesUnderReversal: structuralSignature(forward) === structuralSignature(backward), orderIsRecoverableFromSignature: structuralSignature(forward) !== structuralSignature(backward), interpretation: 'The signature intentionally quotients lexical content and identity names; equal signatures cannot reconstruct original turn content/order. Preserve original units alongside signatures.', witness: { forward: orderRows, reversed: [...orderRows].reverse(), signature: structuralSignature(forward) } },
    differential: diff, observations, hypotheses,
    summary: { supportedCandidateObservations: observations.filter(row => row.supported).length, candidateObservations: observations.length, falsifiableHypotheses: hypotheses.length, negativeControls: negativeControls.length, independentlyReconstructedFiniteResults: reconstructions.filter(row => row.passed).length, novelDiscoveriesClaimed: 0 },
    limits: ['All result claims are finite computations or supplied-feature demonstrations; no new theorem is established.', 'No expert or held-out linguistic gold, speaker-intent validation, tafsir result, or native-speaker review is supplied.', 'Authored cross-language feature paths demonstrate adapter neutrality only.', 'Source differential compares deliberately different algorithms/scopes and preserves all mismatches; neither output is semantic truth.'],
  };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const fixture = JSON.parse(readFileSync(resolve(root, 'data/original-detectors.json'), 'utf8')) as OriginalFixture;
  const report = runExperiments(readCorpus(), fixture, readMorphology());
  mkdirSync(resolve(root, 'evidence'), { recursive: true });
  writeFileSync(resolve(root, 'evidence/experiments.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ ...report.summary, differentialMatchingCases: report.differential.matchingCases, differentialMismatchingCases: report.differential.mismatchingCases }, null, 2));
  if (report.negativeControls.some(row => !row.passed) || report.reconstructions.some(row => !row.passed) || report.observations.some(row => !row.supported)) process.exitCode = 1;
}
