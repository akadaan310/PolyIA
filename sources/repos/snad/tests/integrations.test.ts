import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const moduleUrl = new URL('../scripts/integrations/acsp.mjs', import.meta.url);
const adapter: Record<string, any> = await import(moduleUrl.href).catch(() => ({}));
const input = () => ({
  sessionId: 'snad-test-session',
  idempotencyKey: 'snad-test-artifact-0001',
  title: 'Attribution evidence export',
  summary: 'Local computational analysis; speaker identity remains unresolved.',
  objective: 'Preserve an inspectable source-bound analysis.',
  analysis: { locus: '11:36', evidenceStatus: 'derived', observed: false, uncertainty: ['unresolved speaker'] },
  refs: [{ url: 'https://github.com/akadaan310/snad', note: 'Independent research code' }],
});

test('ACSP export preserves scientific objects inside a real reference TOK proposal', () => {
  assert.equal(typeof adapter.buildAcspProposal, 'function', 'offline ACSP proposal builder is missing');
  const source = input();
  const envelope = adapter.buildAcspProposal(source);
  assert.equal(envelope.protocol, 'ACSP/0.1');
  assert.equal(envelope.operation, 'propose');
  assert.equal(envelope.payload.operation, 'append');
  assert.equal(envelope.payload.payload.type, 'reference');
  assert.equal(envelope.payload.payload.stated_confidence, 'unclassified');
  assert.deepEqual(JSON.parse(envelope.payload.payload.content).analysis, source.analysis);
  assert.deepEqual(envelope.payload.payload.refs, source.refs);
  assert.deepEqual(adapter.validateAcspProposal(envelope), []);
});

test('offline validator rejects unsupported semantics, credentials and invalid source references', () => {
  assert.equal(typeof adapter.validateAcspProposal, 'function', 'offline ACSP validator is missing');
  const good = adapter.buildAcspProposal(input());
  for (const mutate of [
    (x: any) => { x.protocol = 'ACSP/fiction'; },
    (x: any) => { x.payload.operation = 'embody'; },
    (x: any) => { x.capability = 'never-export-a-secret'; },
    (x: any) => { x.actor.session_id = 'invalid session'; },
    (x: any) => { x.payload.payload.refs = [{ url: 'file:///private/evidence' }]; },
    (x: any) => { x.payload.payload.verified = true; },
    (x: any) => { x.payload.payload.stated_confidence = 'proven'; },
  ]) {
    const bad = structuredClone(good);
    mutate(bad);
    assert.ok(adapter.validateAcspProposal(bad).length > 0);
  }
});

test('builder enforces source attribution, finite JSON and service limits without silent truncation', () => {
  assert.equal(typeof adapter.buildAcspProposal, 'function');
  assert.throws(() => adapter.buildAcspProposal({ ...input(), refs: [] }), /reference/i);
  assert.throws(() => adapter.buildAcspProposal({ ...input(), analysis: { score: NaN } }), /finite|JSON/i);
  assert.throws(() => adapter.buildAcspProposal({ ...input(), analysis: { score: undefined } }), /JSON/i);
  assert.throws(() => adapter.buildAcspProposal({ ...input(), analysis: { [Symbol('hidden evidence')]: true } }), /JSON/i);
  const hidden = Object.defineProperty({}, 'evidence', { value: 'would disappear', enumerable: false });
  assert.throws(() => adapter.buildAcspProposal({ ...input(), analysis: hidden }), /JSON/i);
  assert.throws(() => adapter.buildAcspProposal({ ...input(), title: 'x'.repeat(201) }), /title/i);
  assert.throws(() => adapter.buildAcspProposal({ ...input(), analysis: { text: 'x'.repeat(20_001) } }), /content/i);
  const cyclic: any = {}; cyclic.self = cyclic;
  assert.throws(() => adapter.buildAcspProposal({ ...input(), analysis: cyclic }), /cycl|JSON/i);
  const large = adapter.buildAcspProposal(input());
  large.payload.rationale = '😀'.repeat(2_500);
  large.payload.payload.content = '😀'.repeat(10_000);
  large.payload.payload.summary = '😀'.repeat(1_000);
  large.payload.payload.refs = Array.from({ length: 20 }, () => ({ citation: '😀'.repeat(500) }));
  assert.ok(adapter.validateAcspProposal(large).some((x: string) => /bytes|65,?536/.test(x)));
});

test('prepared exports are deterministic snapshots and preserve explicit version guards', () => {
  assert.equal(typeof adapter.buildAcspProposal, 'function');
  const source = { ...input(), expectedVersion: 12 };
  const first = adapter.buildAcspProposal(source);
  assert.equal(first.expected_version, 12);
  assert.deepEqual(first, adapter.buildAcspProposal(source));
  source.analysis.uncertainty.push('later edit');
  source.refs[0].note = 'later edit';
  assert.equal(JSON.parse(first.payload.payload.content).analysis.uncertainty.length, 1);
  assert.equal(first.payload.payload.refs[0].note, 'Independent research code');
  assert.throws(() => adapter.buildAcspProposal({ ...input(), expectedVersion: 0 }), /expected_version/i);
});

test('executable example writes only a prepared request to stdout', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'snad-acsp-'));
  try {
    const path = join(directory, 'input.json');
    await writeFile(path, JSON.stringify(input()));
    const result = spawnSync(process.execPath, [moduleUrl.pathname, '--input', path], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    const envelope = JSON.parse(result.stdout);
    assert.equal(envelope.operation, 'propose');
    assert.deepEqual(adapter.validateAcspProposal(envelope), []);
    assert.equal(envelope.capability, undefined);
  } finally { await rm(directory, { recursive: true, force: true }); }
});
