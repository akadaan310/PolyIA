// Fictional campus residents and Harness Masters. Scripted game characters:
// a statechart (idle → greet → explain → point → react), a schedule, and a
// compact lexical grammar with seeded variation. No language model is used.
// Their only memory is browser-local (how often you met, the last line).

import type { DivisionId } from '../content/types';
import { DIVISIONS } from '../content/registry';
import type { Store } from '../state/store';
import { hashString, mulberry32 } from '../math/world';

export interface Resident {
  id: string;
  name: string;
  role: 'Harness Master' | 'Resident' | 'Archivist' | 'Night Porter' | 'Stargazer' | 'Scribe';
  division: DivisionId | null;
  home: string; // route path
  /** Hours (local) when the resident is at the atrium rather than at home. */
  atriumHours: [number, number];
  color: string;
  lexicon: { greet: string[]; remark: string[] };
}

export const FICTION_NOTE = 'Fictional resident: a scripted character of the campus, not a real person or staff member.';

export const RESIDENTS: Resident[] = [
  { id: 'vell', name: 'HM Ondine Vell', role: 'Harness Master', division: 'foundations', home: '/divisions/foundations', atriumHours: [8, 12], color: '#d6ac62', lexicon: { greet: ['Welcome, Harnesser. Every door here is also a state.', 'Ah. Someone who reads the signs before walking.'], remark: ['Walk a word across the bridges and watch both lamps.', 'Admissible and realizable are different lamps. Keep them apart.'] } },
  { id: 'pliar', name: 'HM Casimir Pliar', role: 'Harness Master', division: 'relational', home: '/divisions/relational', atriumHours: [10, 15], color: '#c9a3d8', lexicon: { greet: ['Mind the walkway; it folds.', 'Good evening. Bring me a word with repetitions.'], remark: ['A fold never loses a step. It moves it into a rule.', 'Count the rules and the stratum together: that is the true size.'] } },
  { id: 'sorrel', name: 'HM Ines Sorrel', role: 'Harness Master', division: 'languages', home: '/divisions/languages', atriumHours: [13, 18], color: '#7fc1c4', lexicon: { greet: ['An address is a sentence. Shall we parse yours?', 'The loom accepts only what it can type.'], remark: ['START before anything, COMMIT at the end. The machine is strict, never cruel.', 'Four operations, one matrix. That is compilation.'] } },
  { id: 'achterberg', name: 'HM Teodor Achterberg', role: 'Harness Master', division: 'geometry', home: '/divisions/geometry', atriumHours: [16, 21], color: '#f1d79c', lexicon: { greet: ['Tell me what survives, and I will tell you the rank.', 'Stand in the light; your shadow is a projection.'], remark: ['The kernel is not destruction. It is identification.', 'Ask of every picture: what map made it, and what did it forget?'] } },
  { id: 'marrow', name: 'HM Lio Marrow', role: 'Harness Master', division: 'acoustic', home: '/divisions/acoustic', atriumHours: [18, 23], color: '#e08a7a', lexicon: { greet: ['Listen, if you like. The lights will tell you anyway.', 'Twelve lamps. Pick a step.'], remark: ['Fifths visit everyone. Thirds keep a small circle.', 'The number of lit arches is twelve over a gcd. No more mystery than that.'] } },
  { id: 'quell', name: 'HM Adaeze Quell', role: 'Harness Master', division: 'worlds', home: '/divisions/worlds', atriumHours: [20, 24], color: '#9fc58a', lexicon: { greet: ['Eight bits make a world. Which eight?', 'Careful with the well. Half the town depends on it.'], remark: ['Pull a fact and everything downstream goes dark.', 'Same rule, same seed, same world. That is how a world becomes citable.'] } },
  { id: 'brask', name: 'Archivist Mott Brask', role: 'Archivist', division: null, home: '/library', atriumHours: [9, 11], color: '#b9a27a', lexicon: { greet: ['The specimens glow; the real books do not need to.', 'Every spine says what it is. Read them.'], remark: ['Specimen volumes are previews. Real volumes are made by visitors, one day at a time.', 'The grammar book on the founding shelf is real. Open it.'] } },
  { id: 'nyx', name: 'Stargazer Wren Okafor-Lind', role: 'Stargazer', division: null, home: '/observatory', atriumHours: [21, 24], color: '#9db4d8', lexicon: { greet: ['The stars here are where the catalogue says they are.', 'Give me a latitude and I will give you a zenith.'], remark: ['The campus constellations are ours; the stars are not.', 'Two similar streets are a correspondence, not a tunnel.'] } },
  { id: 'hale', name: 'Night Porter Esk Hale', role: 'Night Porter', division: null, home: '/gate', atriumHours: [0, 6], color: '#8d232c', lexicon: { greet: ['Gate’s open. It always is, for those who answer anything at all.', 'One and one, traveller. Choose your numbers first.'], remark: ['Wrong answers open the door too. They just open it with a lesson.', 'In F₂, one and one make nothing. Not a trick; a field.'] } },
  { id: 'quire', name: 'Scribe Pell Quire', role: 'Scribe', division: null, home: '/scriptorium', atriumHours: [14, 17], color: '#e8d8b8', lexicon: { greet: ['Six volumes, one day. The ink is yours.', 'I set the type; you write the thoughts.'], remark: ['A book that says what you did not do is an honest book.', 'Rename it, regenerate it: it stays yours.'] } },
];

export function residentLocation(r: Resident, hour: number): 'atrium' | 'home' {
  const [a, b] = r.atriumHours;
  return hour >= a && hour < b ? 'atrium' : 'home';
}

/** Reactive remark grounded in the visitor's actual progress. */
function progressRemark(s: Store, r: Resident): string | null {
  const w = s.world;
  if (r.division) {
    const div = DIVISIONS.find((d) => d.id === r.division)!;
    const rec = w.exercises[div.exhibit];
    if (rec) return `I saw your work at ${div.exhibitTitle}: ${rec.headline}`;
    if (w.visited.includes(`division:${div.id}`)) return `You have stood at ${div.door}. Next time, run ${div.exhibitTitle} yourself.`;
  }
  if (w.gate.doorOpened && r.role === 'Night Porter') return 'You demonstrated an image and a kernel at the Gate. The first door remembers.';
  if (s.harness.completedAt && r.role === 'Scribe') return 'Your six volumes are bound. You may regenerate them whenever you like.';
  if (s.harness.startedAt && !s.harness.completedAt) {
    const done = Object.keys(s.harness.stations).length;
    return `Your harness is ${done} of 6 stations along. The day is long enough.`;
  }
  if (w.portal) return `A portal opened in the courtyard for a correspondence of ${(w.portal.similarity * 100).toFixed(0)}%. Fiction, carefully labelled.`;
  return null;
}

export function residentLine(s: Store, r: Resident, met: number): { line: string; state: 'greet' | 'explain' | 'react' } {
  const rnd = mulberry32(hashString(`${r.id}|${met}|${s.world.visited.length}`));
  const pick = (xs: string[]) => xs[Math.floor(rnd() * xs.length)]!;
  const react = progressRemark(s, r);
  if (met === 0) return { line: pick(r.lexicon.greet), state: 'greet' };
  if (react && met % 2 === 1) return { line: react, state: 'react' };
  return { line: pick(r.lexicon.remark), state: 'explain' };
}

/** The deterministic HM welcome for a newcomer at the Approach. */
export function welcomeLine(s: Store): string {
  const places = s.world.visited.filter((v) => v !== 'approach');
  const returning = places.length > 0;
  if (!returning) return 'Welcome to Substrate University — Haq Roots. The campus is the interface: every door, bridge and lamp here is a computation you can inspect. Begin at the Gate with a question that has more than one right answer: what is one plus one?';
  const n = places.length;
  return `Welcome back. You have visited ${n} place${n === 1 ? '' : 's'} on campus${s.harness.startedAt && !s.harness.completedAt ? ', and your One-Day Harness is in progress' : ''}. Choose a door, or resume where you left off.`;
}
