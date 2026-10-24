import { adaptDialogue, analyze, analyzeStream, induceGrammar, acceptsGrammar, serialize } from '../packages/snad-core/src/index.js';

const input = adaptDialogue([
  { id: 'arrival', speaker: 'Mira', text: 'I brought the book.', features: { person: '1', number: 'singular' }, timestamp: { start: 0, end: 1200, unit: 'ms', uncertainty: 50, original: '00:00.000–00:01.200 ±50ms' } },
  { id: 'reply', speaker: 'Omar', text: 'You brought the book.', features: { person: '2', number: 'singular' }, timestamp: { start: 1400, end: 2600, unit: 'ms', uncertainty: 80 } }
], { id: 'authored-dialogue-example-v1', kind: 'synthetic', title: 'Manually annotated SDK example; not observed conversation' });
const analysis = analyze(input);
const grammar = induceGrammar(analysis);
for await (const replay of analyzeStream((async function* () { yield input; })())) {
  console.log(JSON.stringify({ locus: replay.id, transitions: replay.transitions.map(t => ({ kinds: t.kinds, lexicalContinuity: t.lexicalContinuity, attributionChange: t.attributionChange })), grammarAcceptsTraining: acceptsGrammar(grammar, analysis), serializedBytes: serialize(replay).length, uncertainty: replay.uncertainty }, null, 2));
}
