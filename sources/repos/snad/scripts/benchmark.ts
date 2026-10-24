import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { cpus, platform, arch, totalmem } from 'node:os';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { performance } from 'node:perf_hooks';
import { analyze, adaptQuran, parseLocus, quranLocus } from '../packages/snad-core/src/index.js';
import type { QuranRecord } from '../packages/snad-core/src/types.js';

export interface MorphologyRecord { sourceId?: string; status: string; morphology: NonNullable<QuranRecord['morphology']> }
export type MorphologyMap = Record<string, MorphologyRecord>;
export const sha256 = (value: string | Buffer) => createHash('sha256').update(value).digest('hex');
const root = fileURLToPath(new URL('../', import.meta.url));
export function readCorpus(): QuranRecord[] { return JSON.parse(readFileSync(resolve(root, 'data/quran.json'), 'utf8')); }
export function readMorphology(): MorphologyMap {
  const path = resolve(root, 'data/quran.morphology.json');
  return existsSync(path) ? JSON.parse(readFileSync(path, 'utf8')) : {};
}
export function indexCorpus(records: readonly QuranRecord[]): Map<string, QuranRecord> {
  const index = new Map<string, QuranRecord>();
  for (const record of records) {
    const id = quranLocus(record.surah, record.ayah);
    parseLocus(id);
    if (record.id !== undefined && record.id !== id) throw new Error(`Corpus identity does not match locus: ${id}`);
    if (typeof record.text !== 'string') throw new Error(`Invalid source text: ${id}`);
    if (index.has(id)) throw new Error(`Duplicate corpus locus: ${id}`);
    index.set(id, record);
  }
  return index;
}

/** Measures a computational pass. Visualization and audio require different evidence. */
export function runCorpusPass(records: readonly QuranRecord[], morphology: MorphologyMap = {}, onAnalyzed?: (index: number) => void) {
  const index = indexCorpus(records);
  const loci = [...index].map(([id, record], position) => {
    const annotation = morphology[id];
    const analysis = analyze(adaptQuran({ ...record, morphology: annotation?.morphology }));
    onAnalyzed?.(position);
    return {
      id, status: analysis.status, sourceId: typeof record.source === 'string' ? record.source : record.source?.id ?? 'quran:unspecified', morphologySourceId: annotation?.sourceId ?? null, sourceTokenCount: record.text.match(/\S+/gu)?.length ?? 0,
      units: analysis.units.length, transitions: analysis.transitions.length,
      grammaticalTransitions: analysis.transitions.filter(row => row.kinds.some(kind => ['person', 'number', 'tense', 'aspect'].includes(kind))).length,
      attributionTransitions: analysis.transitions.filter(row => row.attributionChange).length,
      featureUnits: analysis.units.filter(unit => Object.keys(unit.features).length > 0).length,
      unknownSpeakers: analysis.units.filter(unit => unit.attribution.speaker.status === 'unknown').length,
      morphologyStatus: annotation?.status ?? 'not-supplied',
      sourceTextSha256: sha256(record.text),
    };
  });
  const total = records.length;
  const counts = { addressable: index.size, parsed: records.filter(row => typeof row.text === 'string').length, analyzed: loci.filter(row => row.status === 'analyzed').length, detected: loci.filter(row => row.transitions > 0).length, visualized: 0, audioVerified: 0 };
  const meaning = {
    addressable: 'Canonical locus present and unique; lookup roundtrips.',
    parsed: 'JSON source text and locus parsed; no claim of linguistic completeness.',
    analyzed: 'SDK analyze completed, including zero-transition and missing-feature cases.',
    detected: 'At least one typed transition detected under the supplied feature projection.',
    visualized: 'Per-locus browser rendering explicitly verified in this pass; no browser was run.',
    audioVerified: 'Recitation/audio comparison explicitly verified; no audio verification performed.',
  };
  return {
    schemaVersion: 'snad.corpus-status.v1' as const,
    scope: 'Every source ayah, with no length, score, or highlight exclusion.',
    provenance: { inputCanonicalJsonSha256: sha256(JSON.stringify(records)), sourceOrthographyAndLicense: 'data/quran.provenance.json', morphologyAlignmentAndNotices: 'data/quran.morphology.provenance.json', fullMorphologyEvidence: 'data/quran.morphology.json' },
    counts,
    denominators: Object.fromEntries(Object.entries(counts).map(([key, count]) => [key, { count, total, meaning: meaning[key as keyof typeof meaning] }])),
    totals: {
      surahs: new Set(records.map(row => row.surah)).size,
      sourceTokens: loci.reduce((sum, row) => sum + row.sourceTokenCount, 0),
      analyzedUnits: loci.reduce((sum, row) => sum + row.units, 0),
      transitions: loci.reduce((sum, row) => sum + row.transitions, 0),
      featureUnits: loci.reduce((sum, row) => sum + row.featureUnits, 0),
      featureAyahs: loci.filter(row => row.featureUnits > 0).length,
      shortAyahsUnder3Tokens: loci.filter(row => row.sourceTokenCount < 3).length,
      singleTokenAyahs: loci.filter(row => row.sourceTokenCount === 1).length,
      zeroTransitionAyahs: loci.filter(row => row.transitions === 0).length,
      attributionTransitions: loci.reduce((sum, row) => sum + row.attributionTransitions, 0),
    },
    assumptions: ['Only independently sourced supplied morphology is projected to surface tokens; withheld alignment and ambiguous fields remain missing.', 'No grammatical-person value establishes a speaker identity.', 'Transitions compare adjacent source tokens inside each ayah; this pass does not carry state across ayah boundaries.', 'Visualized and audioVerified counts are evidence from this pass, not the UI addressable capacity.'],
    loci,
  };
}

export function benchmark() {
  const start = performance.now();
  const records = readCorpus();
  const morphology = readMorphology();
  const loaded = performance.now();
  const before = process.memoryUsage();
  let sampledPeakRss = before.rss;
  let sampledPeakHeapUsed = before.heapUsed;
  let samples = 1;
  const result = runCorpusPass(records, morphology, index => {
    if (index % 100 === 0 || index === records.length - 1) {
      const memory = process.memoryUsage();
      sampledPeakRss = Math.max(sampledPeakRss, memory.rss);
      sampledPeakHeapUsed = Math.max(sampledPeakHeapUsed, memory.heapUsed);
      samples++;
    }
  });
  const end = performance.now();
  const after = process.memoryUsage();
  sampledPeakRss = Math.max(sampledPeakRss, after.rss);
  sampledPeakHeapUsed = Math.max(sampledPeakHeapUsed, after.heapUsed);
  const benchmarkReport = {
    schemaVersion: 'snad.benchmark.v1',
    method: 'One sequential in-process pass; no warmup, repetition, comparison hardware, or forced GC. Corpus and optional morphology loaded before timing the analysis pass.',
    machine: { node: process.version, platform: platform(), arch: arch(), cpuModel: cpus()[0]?.model ?? 'unknown', logicalCpus: cpus().length, totalMemoryBytes: totalmem() },
    inputHashes: {
      corpusSha256: sha256(readFileSync(resolve(root, 'data/quran.json'))),
      morphologySha256: existsSync(resolve(root, 'data/quran.morphology.json')) ? sha256(readFileSync(resolve(root, 'data/quran.morphology.json'))) : null,
    },
    counts: result.counts,
    totals: result.totals,
    run: { loadWallMs: loaded - start, analysisWallMs: end - loaded, totalWallMs: end - start, ayahsPerSecond: records.length / ((end - loaded) / 1000), passes: 1 },
    memory: { unit: 'bytes', before, after, rssDelta: after.rss - before.rss, heapUsedDelta: after.heapUsed - before.heapUsed, sampledPeakRss, sampledPeakHeapUsed, samples: samples + 1, sampleIntervalAyahs: 100, meaning: 'process.memoryUsage samples include runtime, input corpus, morphology, allocation and retained status rows. Sampled peaks are lower bounds on true peaks; deltas are not per-ayah memory costs.' },
    limitations: ['Single-machine single-pass observation; no statistical confidence interval or comparative speed claim.', 'Analysis wall time includes status hashing and memory sampling overhead.', 'No audio verification; browser rendering is tracked separately.', 'Morphology coverage and speaker interpretation are different questions. Missing morphology remains missing.'],
  };
  mkdirSync(resolve(root, 'evidence'), { recursive: true });
  writeFileSync(resolve(root, 'evidence/corpus-status.json'), JSON.stringify(result, null, 2) + '\n');
  writeFileSync(resolve(root, 'evidence/benchmark.json'), JSON.stringify(benchmarkReport, null, 2) + '\n');
  console.log(JSON.stringify({ counts: result.counts, totals: result.totals, run: benchmarkReport.run, memory: { sampledPeakRss, sampledPeakHeapUsed } }, null, 2));
  return benchmarkReport;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) benchmark();
