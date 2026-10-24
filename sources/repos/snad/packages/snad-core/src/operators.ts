import type { Analysis, DiscourseInput, Morphism, Motif, Perturbation, Topology, Transition } from './types.js';
import { clone, nonempty, requireValid, stable, validateInput } from './validation.js';
import { unknownIdentity } from './adapters.js';

export function identity(endpoint: string): Morphism { requireValid(nonempty(endpoint), 'identity endpoint'); return { from: endpoint, to: endpoint, path: [] }; }
function validateMorphism(value: Morphism): void { requireValid(value && nonempty(value.from) && nonempty(value.to) && Array.isArray(value.path) && value.path.every(nonempty), 'morphism endpoint/path'); requireValid(value.path.length > 0 || value.from === value.to, 'identity morphism endpoints'); }
export function transitionMorphism(transition: Transition): Morphism { requireValid(transition && nonempty(transition.id) && nonempty(transition.from) && nonempty(transition.to), 'transition endpoints'); return { from: transition.from, to: transition.to, path: [transition.id] }; }
/** Left-to-right path composition: compose(A→B, B→C) = A→C. */
export function compose(...morphisms: Morphism[]): Morphism {
  requireValid(morphisms.length > 0, 'compose requires a morphism (use identity for empty paths)');
  morphisms.forEach(validateMorphism);
  for (let i = 1; i < morphisms.length; i++) requireValid(morphisms[i - 1].to === morphisms[i].from, `compose endpoint mismatch: ${morphisms[i - 1].to} != ${morphisms[i].from}`);
  return { from: morphisms[0].from, to: morphisms[morphisms.length - 1].to, path: morphisms.flatMap(morphism => [...morphism.path]) };
}
/** Restricted structural equivalence, not semantic equivalence or speaker intent. */
export function structuralSignature(analysis: Analysis): string {
  // Full occurrence patterns canonically order identities without reading their names.
  // Referents form sets: their input order and repeated declarations have no effect.
  const occurrences = new Map<string, string[]>();
  const note = (id: string, unit: number, role: string): void => { if (!occurrences.has(id)) occurrences.set(id, []); occurrences.get(id)!.push(stable([unit, role])); };
  analysis.units.forEach((unit, index) => {
    for (const role of ['speaker', 'addressee', 'narrator'] as const) if (unit.attribution[role].status === 'known') note(unit.attribution[role].id, index, role);
    for (const id of new Set(unit.attribution.referents.filter(identity => identity.status === 'known').map(identity => identity.id))) note(id, index, 'referent');
  });
  const patterns = [...occurrences].map(([id, pattern]) => ({ id, pattern: stable(pattern) })).sort((a, b) => a.pattern < b.pattern ? -1 : a.pattern > b.pattern ? 1 : 0);
  const identities = new Map(patterns.map(({ id }, index) => [id, index])); const frames = new Map<string, number>();
  const rank = (map: Map<string, number>, id: string): number => { if (!map.has(id)) map.set(id, map.size); return map.get(id)!; };
  const units = analysis.units.map(unit => {
    const referents: (number | '?')[] = [...new Set(unit.attribution.referents.filter(identity => identity.status === 'known').map(identity => identities.get(identity.id)!))].sort((a, b) => a - b);
    if (unit.attribution.referents.some(identity => identity.status === 'unknown')) referents.push('?');
    return { features: unit.features, speaker: unit.attribution.speaker.status === 'known' ? identities.get(unit.attribution.speaker.id) : '?', addressee: unit.attribution.addressee.status === 'known' ? identities.get(unit.attribution.addressee.id) : '?', narrator: unit.attribution.narrator.status === 'known' ? identities.get(unit.attribution.narrator.id) : '?', referents, frame: rank(frames, unit.attribution.frameId) };
  });
  const index = new Map(analysis.units.map((unit, i) => [unit.id, i]));
  return stable({ version: 'snad-signature/2', units, transitions: analysis.transitions.map(transition => ({ from: index.get(transition.from), to: index.get(transition.to), kinds: transition.kinds })), quoteNesting: analysis.frames.map(frame => ({ unit: index.get(frame.unitId), depth: frame.depth })) });
}
export function perturb(input: DiscourseInput, options: Perturbation): DiscourseInput {
  validateInput(input); requireValid(options && Number.isSafeInteger(options.seed), 'perturbation seed');
  requireValid(['drop-features', 'reverse-units', 'mask-speakers'].includes(options.kind), 'perturbation kind');
  const result = clone(input);
  if (options.kind === 'reverse-units') result.units.reverse();
  if (options.kind === 'drop-features') result.units.forEach(unit => { unit.features = {}; });
  if (options.kind === 'mask-speakers') result.units.forEach(unit => { unit.attribution = { ...unit.attribution, speaker: unknownIdentity() }; });
  result.metadata = { ...result.metadata, perturbation: { kind: options.kind, seed: options.seed, stochastic: false } };
  return result;
}
export function mineMotifs(value: Analysis | Analysis[], width = 2): Motif[] {
  requireValid(Number.isSafeInteger(width) && width > 0, 'motif width');
  const analyses = Array.isArray(value) ? value : [value]; const motifs = new Map<string, Motif>();
  for (const analysis of analyses) for (let i = 0; i + width <= analysis.transitions.length; i++) {
    const path = analysis.transitions.slice(i, i + width);
    if (path.some((transition, index) => index > 0 && path[index - 1].to !== transition.from)) continue;
    const signature = path.map(transition => transition.kinds.join('+')).join(' → ');
    if (!motifs.has(signature)) motifs.set(signature, { signature, count: 0, occurrences: [] });
    const motif = motifs.get(signature)!; motif.count++; motif.occurrences.push({ analysisId: analysis.id, transitionIds: path.map(transition => transition.id) });
  }
  return [...motifs.values()].sort((left, right) => right.count - left.count || left.signature.localeCompare(right.signature));
}
/** Components and cycle rank use the underlying undirected multigraph; density is directed/simple. */
export function topology(units: readonly (string | { id: string })[], transitions: readonly { from: string; to: string }[]): Topology {
  const ids = units.map(unit => typeof unit === 'string' ? unit : unit.id); requireValid(ids.every(nonempty) && new Set(ids).size === ids.length, 'topology unit ids/duplicates');
  const parent = new Map(ids.map(id => [id, id]));
  const find = (id: string): string => { let root = id; while (parent.get(root) !== root) root = parent.get(root)!; while (id !== root) { const next = parent.get(id)!; parent.set(id, root); id = next; } return root; };
  const simple = new Set<string>();
  for (const edge of transitions) { requireValid(parent.has(edge.from) && parent.has(edge.to), 'topology edge endpoint'); parent.set(find(edge.from), find(edge.to)); if (edge.from !== edge.to) simple.add(stable([edge.from, edge.to])); }
  const vertices = ids.length; const edges = transitions.length; const components = new Set(ids.map(find)).size;
  return { vertices, edges, components, cycleRank: edges - vertices + components, density: vertices > 1 ? simple.size / (vertices * (vertices - 1)) : 0, meanOutDegree: vertices ? edges / vertices : 0 };
}
