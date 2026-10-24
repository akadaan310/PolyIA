import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import fc from 'fast-check';
import { analyze, adaptQuran, parseLocus, quranLocus } from '../packages/snad-core/src/index.js';
import { indexCorpus, runCorpusPass } from '../scripts/benchmark.js';
import type { QuranRecord } from '../packages/snad-core/src/types.js';

const corpus = JSON.parse(readFileSync(new URL('../data/quran.json', import.meta.url), 'utf8')) as QuranRecord[];
const original = JSON.parse(readFileSync(new URL('../data/upstream/risan-quran-v3.1.2.json', import.meta.url), 'utf8')) as { id: number; verses: { id: number; text: string }[] }[];

test('all 6236 source ayahs are canonically addressable and roundtrip without orthographic changes', () => {
  const index = indexCorpus(corpus);
  assert.equal(index.size, 6236);
  assert.equal(new Set(corpus.map(record => record.surah)).size, 114);
  for (const chapter of original) for (const verse of chapter.verses) {
    const id = quranLocus(chapter.id, verse.id);
    const locus = parseLocus(id);
    assert.deepEqual(locus, { id, surah: chapter.id, ayah: verse.id });
    assert.equal(index.get(id)?.text, verse.text, `source orthography ${id}`);
    assert.equal(index.get(id)?.id, id);
  }
});

test('canonical locus validation rejects bounds, ambiguous encodings, and duplicate corpus identity', () => {
  for (const id of ['quran:1:8', 'quran:2:287', 'quran:114:7', 'quran:115:1', 'quran:0:1', 'quran:1:0', 'quran:01:1', 'quran:1:01', 'quran:1:1junk', '1:1', 'quran:1.0:1']) assert.throws(() => parseLocus(id), id);
  assert.throws(() => indexCorpus([corpus[0], corpus[0]]), /duplicate/i);
  assert.throws(() => indexCorpus([{ ...corpus[0], id: 'quran:1:2' }]), /identity|locus/i);
});

test('whole-corpus text-only pass includes short verses and reports independent denominators', () => {
  const before = createHash('sha256').update(JSON.stringify(corpus)).digest('hex');
  const result = runCorpusPass(corpus);
  assert.deepEqual(result.counts, { addressable: 6236, parsed: 6236, analyzed: 6236, detected: 0, visualized: 0, audioVerified: 0 });
  assert.equal(result.loci.length, 6236);
  assert.equal(result.loci.filter(row => row.sourceTokenCount < 3).length, 204);
  assert(result.loci.every(row => row.status === 'analyzed' && row.sourceTextSha256.length === 64));
  assert.equal(result.loci.find(row => row.id === 'quran:20:1')?.sourceTokenCount, 1);
  assert.equal(result.loci.find(row => row.id === 'quran:11:29')?.transitions, 0);
  assert.equal(createHash('sha256').update(JSON.stringify(corpus)).digest('hex'), before);
});

test('short and empty-feature verses remain valid without inferred attribution', () => {
  fc.assert(fc.property(fc.array(fc.constantFrom('أ', 'ب', 'ق', '😀', ''), { maxLength: 2 }), parts => {
    const text = parts.join(' ');
    const record = { id: 'quran:20:1', surah: 20, ayah: 1, text, features: Array.from({ length: Math.max(1, text.match(/\S+/gu)?.length ?? 0) }, () => ({})) };
    const analysis = analyze(adaptQuran(record));
    assert.equal(analysis.input.id, record.id);
    assert.equal(analysis.input.metadata?.originalText, text);
    assert.equal(analysis.transitions.length, 0);
    assert(analysis.units.every(unit => unit.attribution.speaker.status === 'unknown'));
    assert(analysis.units.every(unit => text.slice(unit.span!.start, unit.span!.end) === unit.text));
  }), { seed: 6236, numRuns: 200 });
});
