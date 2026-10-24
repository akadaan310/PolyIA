import type { Analysis, GrammarState, InducedGrammar } from './types.js';
import { record, requireValid, stable } from './validation.js';

const kinds = ['person', 'number', 'tense', 'aspect', 'speaker', 'addressee', 'referents', 'narrator', 'frame'];
function sequence(analysis: Analysis): string[] {
  requireValid(record(analysis) && analysis.schemaVersion === 'snad/1' && Array.isArray(analysis.transitions), 'grammar analysis');
  return analysis.transitions.map(transition => {
    requireValid(record(transition) && Array.isArray(transition.kinds) && transition.kinds.length > 0 && transition.kinds.every(kind => kinds.includes(kind)) && new Set(transition.kinds).size === transition.kinds.length, 'grammar transition kinds');
    return transition.kinds.join('+');
  });
}
function compile(sequences: string[][]): InducedGrammar {
  const unique = new Map<string, string[]>();
  for (const sequence of sequences) unique.set(stable(sequence), [...sequence]);
  const trainingSequences = [...unique.values()].sort((a, b) => a.length - b.length || (stable(a) < stable(b) ? -1 : stable(a) > stable(b) ? 1 : 0));
  const states: GrammarState[] = [{ id: 'q0', accepting: false, transitions: {} }];
  const byId = new Map(states.map(state => [state.id, state]));
  for (const sequence of trainingSequences) {
    let state = states[0];
    for (const symbol of sequence) {
      if (!Object.hasOwn(state.transitions, symbol)) {
        const next: GrammarState = { id: `q${states.length}`, accepting: false, transitions: {} };
        state.transitions[symbol] = next.id; states.push(next); byId.set(next.id, next);
      }
      state = byId.get(state.transitions[symbol])!;
    }
    state.accepting = true;
  }
  return { schemaVersion: 'snad-grammar/1', definition: 'finite-observed-transition-language', alphabet: [...new Set(trainingSequences.flat())].sort(), startState: 'q0', states, trainingSequences, trainingSignature: stable({ definition: 'finite-observed-transition-language', sequences: trainingSequences }) };
}
/** Prefix-trie DFA that memorizes exactly the observed transition-kind sequences. */
export function induceGrammar(value: Analysis | Analysis[]): InducedGrammar {
  return compile((Array.isArray(value) ? value : [value]).map(sequence));
}
export function acceptsGrammar(grammar: InducedGrammar, analysis: Analysis): boolean {
  requireValid(record(grammar) && grammar.schemaVersion === 'snad-grammar/1' && Array.isArray(grammar.trainingSequences) && grammar.trainingSequences.every(row => Array.isArray(row) && row.every(symbol => typeof symbol === 'string' && symbol.length > 0 && symbol.split('+').every(kind => kinds.includes(kind)))), 'induced grammar schema/training sequences');
  requireValid(stable(grammar) === stable(compile(grammar.trainingSequences)), 'induced grammar state/signature mismatch');
  const states = new Map(grammar.states.map(state => [state.id, state])); let state = states.get(grammar.startState)!;
  for (const symbol of sequence(analysis)) { const next = state.transitions[symbol]; if (next === undefined) return false; state = states.get(next)!; }
  return state.accepting;
}
