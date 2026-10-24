import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { evaluateBaselines, independentSample, runExperiments } from '../scripts/experiments.js';
import type { QuranRecord } from '../packages/snad-core/src/types.js';
const corpus = JSON.parse(readFileSync(new URL('../data/quran.json', import.meta.url), 'utf8')) as QuranRecord[];
const fixture = JSON.parse(readFileSync(new URL('../data/original-detectors.json', import.meta.url), 'utf8'));

test('independent passages use SHA256-ranked sampling and exclude prompted loci', () => {
  const excluded = new Set(['quran:11:29', 'quran:11:36', 'quran:50:2', 'quran:28:4', 'quran:28:5']);
  const expected = corpus.filter(row => !excluded.has(row.id!)).map(row => ({ id: row.id!, digest: createHash('sha256').update(`snad-independent-v1:${row.id}`).digest('hex') })).sort((a, b) => a.digest.localeCompare(b.digest)).slice(0, 12);
  assert.deepEqual(independentSample(corpus), expected);
  assert(!independentSample(corpus).some(row => excluded.has(row.id)));
});

test('authored gold cases expose complementary errors in person-only and speaker-only baselines', () => {
  const result = evaluateBaselines();
  assert.equal(result.goldKind, 'authored explicit synthetic feature/attribution transitions; not Quran ground truth');
  assert.equal(result.cases, 8);
  assert.deepEqual(result.metrics.snad, { truePositive: 6, falsePositive: 0, trueNegative: 2, falseNegative: 0, precision: 1, recall: 1, f1: 1 });
  assert(result.metrics.noChange.falseNegative > 0);
  assert(result.metrics.personOnly.falseNegative > 0);
  assert(result.metrics.speakerOnly.falseNegative > 0);
});

test('experiments preserve independently reconstructed results and real counterexamples', () => {
  const report = runExperiments(corpus, fixture);
  assert.equal(report.reconstructions.length, 3);
  assert(report.reconstructions.every(row => row.passed && row.checked > 0));
  assert(report.negativeControls.length >= 5);
  assert(report.negativeControls.every(row => row.passed));
  assert.equal(report.crossLinguistic.length, 3);
  assert(report.crossLinguistic.every(row => row.manualFeatures && row.signatureMatchesEnglish));
  assert.equal(report.selfCommissioned.signatureCollidesUnderReversal, true);
  assert.equal(report.selfCommissioned.orderIsRecoverableFromSignature, false);
  assert.equal(report.hypotheses.length, 10);
});

test('differential evidence compares pinned original fixtures and retains disagreements', () => {
  const report = runExperiments(corpus, fixture);
  assert.equal(report.differential.cases.length, fixture.cases.length);
  assert(report.differential.cases.every(row => Array.isArray(row.originalPersonEndpoints) && Array.isArray(row.independentPersonEndpoints)));
  assert(report.differential.mismatchingCases > 0);
  assert.equal(report.differential.scope, 'Independent adjacent token comparison versus original surah-context carried-person seams; mismatch is not an accuracy judgment.');
  assert.deepEqual(runExperiments(corpus, fixture), report);
});

test('seeded perturbation forge separates grammatical ablation from speaker masking and retains source input', () => {
  const report = runExperiments(corpus, fixture);
  assert.equal(report.perturbationForge.referenceTransitions, 3);
  assert.equal(report.perturbationForge.trials.find(row => row.kind === 'drop-features')?.transitions, 1);
  assert.equal(report.perturbationForge.trials.find(row => row.kind === 'mask-speakers')?.transitions, 2);
  assert(report.perturbationForge.trials.every(row => row.replayDeterministic));
  assert.equal(report.perturbationForge.originalUnchanged, true);
  assert.equal(report.perturbationForge.minimumEvidenceConfidence, 0.2);
  assert.equal(report.perturbationForge.confidenceMeaning, 'uncalibrated-evidence-quality');
});
