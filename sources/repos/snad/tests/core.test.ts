import test from 'node:test';
import assert from 'node:assert/strict';
import fc from 'fast-check';
import { readFileSync } from 'node:fs';
import { analyze, analyzeStream, adaptDialogue, adaptQuran, quranLocus, parseLocus, identity, compose, transitionMorphism, structuralSignature, perturb, mineMotifs, topology, serialize, deserialize, tokenize, induceGrammar, acceptsGrammar } from '../packages/snad-core/src/index.js';
import type { DiscourseInput, Features } from '../packages/snad-core/src/types.js';

const source = { id: 'synthetic:manual', kind: 'synthetic', title: 'Domain-neutral manual annotations; not corpus claims' };
const sample = (): DiscourseInput => adaptDialogue([
  { id: 'a', text: 'I wait.', features: { person: '1', number: 'singular' }, speaker: 'Mira' },
  { id: 'b', text: 'You wait.', features: { person: '2', number: 'singular' }, speaker: 'Mira' },
  { id: 'c', text: 'They wait.', features: { person: '3', number: 'plural' }, speaker: 'Sami' },
], source);

test('person changes are separate from identity and unknown identities remain explicit', () => {
  const result = analyze(sample());
  assert.equal(result.transitions.length, 2);
  assert.deepEqual(result.transitions[0].kinds, ['person']);
  assert.deepEqual(result.transitions[1].kinds, ['person', 'number', 'speaker']);
  assert.equal(result.units[0].attribution.addressee.status, 'unknown');
  const unknown = analyze(adaptDialogue([{ text: 'I', features: { person: '1' } }, { text: 'you', features: { person: '2' } }], source));
  assert.equal(unknown.units[0].attribution.speaker.status, 'unknown');
  assert(!unknown.transitions[0].kinds.includes('speaker'));
  assert.equal(unknown.transitions[0].confidenceMeaning, 'uncalibrated-evidence-quality');
  assert.equal(unknown.transitions[0].evidence[0].status, 'derived');
});

test('Quran adapter validates actual canonical ayah ranges and preserves source text and offsets', () => {
  assert.equal(quranLocus(11, 29), 'quran:11:29');
  assert.deepEqual(parseLocus('quran:50:2'), { id: 'quran:50:2', surah: 50, ayah: 2 });
  for (const invalid of ['11:29', 'quran:011:29', 'quran:1:8', 'quran:115:1', 'quran:0:1', 'quran:1:0']) assert.throws(() => parseLocus(invalid));
  const text = '  وَقَالَ  هُوَ\n';
  const input = adaptQuran({ surah: 11, ayah: 29, text, source: 'synthetic:Arabic' });
  assert.equal(input.metadata?.originalText, text);
  for (const unit of input.units) assert.equal(text.slice(unit.span!.start, unit.span!.end), unit.text);
  const result = analyze(input);
  assert.equal(result.transitions.length, 0);
  assert(result.units.every(unit => Object.keys(unit.features).length === 0));
  assert.equal(result.units[0].attribution.speaker.status, 'unknown');
});

test('tokenization retains UTF-16 source spans including Arabic and supplementary codepoints', () => {
  const text = ' A😀  قَالَ\tB ';
  const tokens = tokenize(text, 'unit');
  assert.deepEqual(tokens.map(t => t.text), ['A😀', 'قَالَ', 'B']);
  assert(tokens.every(token => text.slice(token.span.start, token.span.end) === token.text));
});

test('empty text and empty features are valid analyzed inputs', () => {
  const result = analyze(adaptQuran({ surah: 20, ayah: 1, text: '' }));
  assert.equal(result.units.length, 1);
  assert.equal(result.units[0].text, '');
  assert.deepEqual(result.units[0].tokens, []);
  assert.equal(result.transitions.length, 0);
  assert.equal(result.status, 'analyzed');
  assert.equal(analyze({ id: 'empty', source, units: [] }).topology.vertices, 0);
});

test('canonical analysis identity survives empty annotation arrays and empty lexical entries', () => {
  for (const fixture of [{ text: '', features: [] }, { text: ' ', features: [{}, {}] }, { text: 'أ ', features: [{}, {}] }]) {
    const input = adaptQuran({ surah: 20, ayah: 1, ...fixture });
    const result = analyze(input);
    assert.equal(result.id, 'quran:20:1');
    assert.equal(result.transitions.length, 0);
  }
});

test('explicit separately sourced morphology can drive grammatical detections', () => {
  const evidence = [{ id: 'manual:e1', sourceId: source.id, status: 'observed' as const, method: 'synthetic manual fixture' }];
  const result = analyze(adaptQuran({ surah: 1, ayah: 1, text: 'أنا أنت', source, morphology: [{ tokenIndex: 0, features: { person: '1' }, evidence }, { tokenIndex: 1, features: { person: '2' }, evidence }] }));
  assert.deepEqual(result.transitions[0].kinds, ['person']);
  assert.equal(result.units[0].evidence[0].id, 'manual:e1');
});

test('nested reported speech has explicit punctuation evidence without assigning speakers', () => {
  const result = analyze(adaptDialogue([{ id: 'quote', text: 'Mira said, “Sami replied, ‘Go.’”' }], source));
  assert.equal(result.frames.length, 2);
  assert.equal(result.frames[0].depth, 1);
  assert.equal(result.frames[1].parentId, result.frames[0].id);
  assert.equal(result.frames[1].depth, 2);
  assert.equal(result.frames[0].evidence.method, 'quotation-punctuation-heuristic');
  assert.equal(result.units[0].attribution.speaker.status, 'unknown');
  assert.equal(analyze(result.input, { quoteCues: false }).frames.length, 0);
  assert.equal(analyze(adaptDialogue([{ text: '"a \'b\' c"' }], source)).frames.length, 2);
  assert.equal(analyze(adaptDialogue([{ text: "don't stop" }], source)).frames.length, 0);
});

test('timestamps and uncertainty survive adapters, analysis and portable serialization', () => {
  const timestamp = { start: 12.3, end: 13.2, uncertainty: 0.4, unit: 'seconds', original: '00:12.3 ± 0.4' };
  const result = analyze(adaptDialogue([{ text: 'Hello', timestamp }], source));
  const restored = deserialize(serialize(result));
  assert.deepEqual(restored, result);
  assert.deepEqual(restored.units[0].timestamp, timestamp);
  assert.throws(() => deserialize('{"schemaVersion":"snad/999"}'), /version|schema/i);
  assert.throws(() => deserialize(JSON.stringify({ ...result, transitions: [{ from: 'missing', to: 'missing' }] })), /transition|invalid|schema/i);
});

test('provenance references existing nodes and derivations point to both source units', () => {
  const result = analyze(sample());
  const ids = new Set(result.provenance.nodes.map(node => node.id));
  assert.equal(ids.size, result.provenance.nodes.length);
  assert(result.provenance.edges.every(edge => ids.has(edge.from) && ids.has(edge.to)));
  const transition = result.transitions[0];
  const derived = result.provenance.edges.filter(edge => edge.from === `transition:${transition.id}`);
  assert.deepEqual(derived.map(edge => edge.to).sort(), [`unit:${transition.from}`, `unit:${transition.to}`].sort());
});

test('separately attributed feature sources stay reachable in the provenance graph', () => {
  const input = sample();
  input.units[0].evidence!.push({ id: 'external:1', sourceId: 'manual:annotator', method: 'synthetic-manual-fixture', status: 'observed' });
  const result = analyze(input);
  assert(result.provenance.nodes.some(node => node.id === 'source:manual:annotator' && node.kind === 'source'));
  assert(result.provenance.edges.some(edge => edge.from === 'unit:a' && edge.to === 'source:manual:annotator' && edge.relation === 'derived-from'));
});

test('morphisms enforce matching endpoints and obey identity and associativity', () => {
  const t = analyze(sample()).transitions;
  const a = transitionMorphism(t[0]); const b = transitionMorphism(t[1]);
  assert.deepEqual(compose(identity(a.from), a), a);
  assert.deepEqual(compose(a, identity(a.to)), a);
  assert.deepEqual(compose(compose(a, b), identity(b.to)), compose(a, compose(b, identity(b.to))));
  assert.throws(() => compose(b, a), /endpoint|compose/i);
});

test('structural equivalence ignores lexical replacement while retaining grammatical transition types', () => {
  const input = sample(); const other = structuredClone(input);
  other.units.forEach((unit, index) => { unit.text = ['A', 'B', 'C'][index]; });
  assert.equal(structuralSignature(analyze(input)), structuralSignature(analyze(other)));
  assert.notEqual(structuralSignature(analyze(input)), structuralSignature(analyze(perturb(input, { kind: 'drop-features', seed: 6236 }))));
});

test('referent comparison safely distinguishes arbitrary Unicode identity sets', () => {
  const input = adaptDialogue([
    { id: 'left', text: 'a', referents: ['A\u0000B', 'C'] },
    { id: 'right', text: 'b', referents: ['A', 'B\u0000C'] },
  ], source);
  const result = analyze(input);
  assert.deepEqual(result.transitions.map(transition => transition.kinds), [['referents']]);
  assert.deepEqual(deserialize(serialize(result)), result);
});

test('reference partitions ignore referent set order, repetition and identity renaming', () => {
  const fixture = (first: string[], second: string[]) => analyze(adaptDialogue([{ id: 'a', text: 'a', referents: first }, { id: 'b', text: 'b', referents: second }], source));
  const a = fixture(['A', 'B'], ['A']);
  const reordered = fixture(['B', 'A'], ['A']);
  const renamed = fixture(['Z', 'X'], ['Z']);
  const repeated = fixture(['B', 'A', 'A'], ['A']);
  assert.equal(structuralSignature(a), structuralSignature(reordered));
  assert.equal(structuralSignature(a), structuralSignature(renamed));
  assert.equal(structuralSignature(a), structuralSignature(repeated));
  const knownRole = adaptDialogue([{ id: 'a', text: 'a', referents: ['A', 'B'] }, { id: 'b', text: 'b', speaker: 'A' }], source);
  const renamedRole = adaptDialogue([{ id: 'a', text: 'a', referents: ['X', 'Z'] }, { id: 'b', text: 'b', speaker: 'Z' }], source);
  assert.equal(structuralSignature(analyze(knownRole)), structuralSignature(analyze(renamedRole)));
});

test('caller frame declarations preserve unresolved provenance without inventing containment', () => {
  const input = adaptDialogue([{ id: 'a', text: 'a' }, { id: 'b', text: 'b' }], source);
  input.units[1].attribution!.frameId = 'external:unresolved:frame';
  const result = analyze(input);
  assert.deepEqual(result.transitions[0].kinds, ['frame']);
  assert.equal(result.frames.length, 0);
  assert(result.uncertainty.some(entry => entry.unitId === 'b' && entry.field === 'frame' && /external:unresolved:frame/.test(entry.reason) && /unresolved/i.test(entry.reason)));
  assert(result.provenance.nodes.some(node => node.id === 'unit:b'));
  assert(result.provenance.nodes.find(node => node.id === 'unit:b')?.evidence?.some(evidence => evidence.method === 'supplied-frame-declaration' && /unvalidated/i.test(evidence.note ?? '')));
  assert(!result.provenance.nodes.some(node => node.id === 'frame:external:unresolved:frame'));
});

test('publishable SDK includes the complete repository MIT notice', () => {
  const packagePath = new URL('../packages/snad-core/', import.meta.url);
  const metadata = JSON.parse(readFileSync(new URL('package.json', packagePath), 'utf8'));
  assert(metadata.files.includes('LICENSE'));
  assert.equal(readFileSync(new URL('LICENSE', packagePath), 'utf8'), readFileSync(new URL('../LICENSE', import.meta.url), 'utf8'));
});

test('perturbations replay deterministically preserve original identity and isolate input mutation', () => {
  const input = sample(); const before = structuredClone(input);
  for (const kind of ['drop-features', 'reverse-units', 'mask-speakers'] as const) {
    const result = perturb(input, { kind, seed: 6236 });
    assert.deepEqual(result, perturb(input, { kind, seed: 6236 }));
    assert.equal(result.id, input.id);
    assert.deepEqual(result.units.map(unit => unit.id).sort(), input.units.map(unit => unit.id).sort());
  }
  assert.deepEqual(perturb(input, { kind: 'reverse-units', seed: 6236 }).units.map(u => u.id), ['c', 'b', 'a']);
  assert(perturb(input, { kind: 'mask-speakers', seed: 6236 }).units.every(unit => unit.attribution?.speaker?.status === 'unknown'));
  assert.deepEqual(input, before);
  const result = analyze(input); result.units[0].features.person = '3';
  assert.equal(input.units[0].features?.person, '1');
  assert.equal(result.input.units[0].features?.person, '1');
});

test('streaming analyzes each input without shared mutable analysis state', async () => {
  async function* inputs() { yield sample(); yield sample(); }
  const results = [];
  for await (const result of analyzeStream(inputs())) results.push(result);
  assert.deepEqual(results[0], results[1]);
  results[0].units[0].text = 'changed';
  assert.notEqual(results[0].units[0].text, results[1].units[0].text);
});

test('motifs count repeated typed transition paths and topology includes isolated vertices', () => {
  const result = analyze(sample());
  const motifs = mineMotifs([result, result], 2);
  assert.equal(motifs.length, 1);
  assert.equal(motifs[0].count, 2);
  assert.equal(motifs[0].occurrences[0].transitionIds.length, 2);
  assert.deepEqual(topology(['a', 'b', 'c', 'isolated'], [{ from: 'a', to: 'b' }, { from: 'b', to: 'c' }]), { vertices: 4, edges: 2, components: 2, cycleRank: 0, density: 1 / 6, meanOutDegree: 0.5 });
});

test('malformed features, duplicate ids, invalid spans and identity claims fail clearly', () => {
  const bad = (mutate: (input: DiscourseInput) => void) => { const input = sample(); mutate(input); assert.throws(() => analyze(input), /invalid|duplicate|span|person|identity|timestamp|feature/i); };
  bad(input => { input.units[1].id = input.units[0].id; });
  bad(input => { input.units[0].span = { start: 9, end: 2 }; });
  bad(input => { input.units[0].features = { person: '9' } as unknown as Features; });
  bad(input => { input.units[0].features = { tense: 4 } as unknown as Features; });
  bad(input => { input.units[0].timestamp = { start: 4, end: 1 }; });
  bad(input => { input.units[0].attribution = { speaker: { id: '', status: 'known' } }; });
  bad(input => { input.units[0].span = { start: 0, end: 7 }; input.units[1].text = 'I wait.'; input.units[1].span = { start: 0, end: 7 }; });
  assert.throws(() => analyze(null as unknown as DiscourseInput), /invalid/i);
});

test('portable inputs reject hidden non-JSON source and annotation values clearly', () => {
  const input = sample();
  (input.source as unknown as Record<string, unknown>).extra = Number.NaN;
  assert.throws(() => analyze(input), /invalid.*nonfinite/i);
  const cyclic = sample(); cyclic.metadata = {}; cyclic.metadata.loop = cyclic.metadata;
  assert.throws(() => analyze(cyclic), /invalid.*cyclic/i);
  const annotation = sample();
  (annotation.units[0].evidence![0] as unknown as Record<string, unknown>).extra = () => 'unserializable';
  assert.throws(() => analyze(annotation), /invalid.*JSON/i);
});

test('arbitrary Unicode identifiers remain collision-free and transition identity ignores changed features', () => {
  const input = sample(); input.units[0].id = '\ud800'; input.units[1].id = 'x>y';
  const result = analyze(input);
  assert.equal(result.transitions[0].from, '\ud800');
  assert.equal(new Set(result.transitions.map(transition => transition.id)).size, 2);
  const changed = structuredClone(input); changed.units[0].features!.person = '3';
  assert.equal(analyze(changed).transitions[0].id, result.transitions[0].id);
});

test('generated valid paths obey associativity and preserve all transition ids', () => {
  fc.assert(fc.property(fc.array(fc.string({ minLength: 1, maxLength: 15 }), { minLength: 4, maxLength: 4 }), endpoints => {
    const paths = endpoints.slice(1).map((endpoint, index) => ({ from: endpoints[index], to: endpoint, path: [`edge:${index}`] }));
    const [a, b, c] = paths;
    assert.deepEqual(compose(compose(a, b), c), compose(a, compose(b, c)));
    assert.deepEqual(compose(identity(a.from), a), a);
    assert.deepEqual(compose(c, identity(c.to)), c);
    assert.deepEqual(compose(...paths).path, ['edge:0', 'edge:1', 'edge:2']);
  }), { seed: 6236, numRuns: 150 });
});

test('finite observed-language grammar accepts training and rejects unseen transition sequences', () => {
  const training = analyze(sample());
  const empty = analyze(adaptDialogue([{ text: 'No annotated changes' }], source));
  const grammar = induceGrammar([training, empty]);
  assert.equal(grammar.schemaVersion, 'snad-grammar/1');
  assert.equal(grammar.definition, 'finite-observed-transition-language');
  assert(acceptsGrammar(grammar, training));
  assert(acceptsGrammar(grammar, empty));
  const unseen = analyze(adaptDialogue([{ text: 'a', speaker: 'Mira' }, { text: 'b', speaker: 'Sami' }], source));
  assert.equal(acceptsGrammar(grammar, unseen), false);
  const shortened = sample(); shortened.units.pop();
  assert.equal(acceptsGrammar(grammar, analyze(shortened)), false);
  assert.deepEqual(grammar, induceGrammar([empty, training, training]));
  const rephrased = sample(); rephrased.units.forEach((unit, index) => { unit.text = `Lexical alternative ${index}`; });
  assert(acceptsGrammar(grammar, analyze(rephrased)));
  training.transitions[0].kinds = ['speaker'];
  assert.equal(grammar.trainingSequences[0].length, 0);
  assert.equal(grammar.trainingSequences[1][0], 'person');
  assert.equal(acceptsGrammar(induceGrammar([]), empty), false);
});

test('generated short texts preserve identity, roundtrip, provenance and no grammar-to-speaker inference', () => {
  fc.assert(fc.property(fc.array(fc.record({ text: fc.string({ maxLength: 25 }), person: fc.option(fc.constantFrom('1', '2', '3'), { nil: undefined }) }), { maxLength: 8 }), rows => {
    const input = adaptDialogue(rows.map((row, index) => ({ id: `unit:${index}`, text: row.text, features: row.person ? { person: row.person as '1' | '2' | '3' } : {} })), source);
    const result = analyze(input);
    assert.equal(result.id, analyze(perturb(input, { kind: 'reverse-units', seed: 6236 })).id);
    assert.deepEqual(deserialize(serialize(result)), result);
    assert(result.units.every(unit => unit.attribution.speaker.status === 'unknown'));
    assert(result.transitions.every(transition => !transition.kinds.includes('speaker')));
    assert.equal(new Set(result.units.map(unit => unit.id)).size, rows.length);
    assert(result.provenance.edges.every(edge => result.provenance.nodes.some(node => node.id === edge.from) && result.provenance.nodes.some(node => node.id === edge.to)));
  }), { seed: 6236, numRuns: 150 });
});
