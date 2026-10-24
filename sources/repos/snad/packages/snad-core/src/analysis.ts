import type { Analysis, AnalyzeOptions, AnalyzedUnit, Attribution, DiscourseInput, Evidence, Identity, QuotationFrame, Transition, TransitionKind } from './types.js';
import { tokenize, unknownIdentity } from './adapters.js';
import { clone, stable, validateInput } from './validation.js';
import { topology } from './operators.js';

function punctuationFrames(unit: AnalyzedUnit, sourceId: string): QuotationFrame[] {
  const frames: QuotationFrame[] = [];
  const stack: { frame: QuotationFrame; close: string }[] = [];
  const pairs: Record<string, string> = { '“': '”', '‘': '’', '«': '»', '"': '"', "'": "'" };
  for (let offset = 0; offset < unit.text.length; offset++) {
    const char = unit.text[offset];
    if ((char === "'" || char === '’') && /[\p{L}\p{N}]/u.test(unit.text[offset - 1] ?? '') && /[\p{L}\p{N}]/u.test(unit.text[offset + 1] ?? '')) continue;
    const current = stack.at(-1);
    if (current?.close === char) { current.frame.span.end = offset + 1; stack.pop(); continue; }
    if (!pairs[char]) continue;
    const id = `${unit.id}:quote:${offset}`;
    const frame: QuotationFrame = { id, parentId: current?.frame.id ?? null, depth: stack.length + 1, unitId: unit.id, span: { start: offset, end: unit.text.length }, cue: char, evidence: { id: `${id}:evidence`, status: 'derived', method: 'quotation-punctuation-heuristic', sourceId, note: 'Punctuation cue only; quoted speaker and reported intent remain unresolved.', confidence: 0.5 } };
    frames.push(frame); stack.push({ frame, close: pairs[char] });
  }
  for (const { frame } of stack) frame.evidence.note = 'Unclosed punctuation cue; frame extends to unit end; speaker remains unresolved.';
  return frames;
}
const resolvedAttribution = (partial: Partial<Attribution> | undefined): Attribution => ({ speaker: clone(partial?.speaker ?? unknownIdentity()), addressee: clone(partial?.addressee ?? unknownIdentity()), narrator: clone(partial?.narrator ?? unknownIdentity()), referents: clone(partial?.referents ?? []), frameId: partial?.frameId ?? 'root' });
const identityChanged = (left: Identity, right: Identity): boolean => left.status === 'known' && right.status === 'known' && left.id !== right.id;
function lexicalContinuity(left: AnalyzedUnit, right: AnalyzedUnit): number {
  const a = new Set(left.tokens.map(token => token.text.toLowerCase())); const b = new Set(right.tokens.map(token => token.text.toLowerCase()));
  const union = new Set([...a, ...b]); if (!union.size) return 0;
  return [...a].filter(token => b.has(token)).length / union.size;
}
function changes(left: AnalyzedUnit, right: AnalyzedUnit): TransitionKind[] {
  const kinds: TransitionKind[] = [];
  for (const kind of ['person', 'number', 'tense', 'aspect'] as const) if (left.features[kind] !== undefined && right.features[kind] !== undefined && left.features[kind] !== right.features[kind]) kinds.push(kind);
  for (const role of ['speaker', 'addressee'] as const) if (identityChanged(left.attribution[role], right.attribution[role])) kinds.push(role);
  const a = left.attribution.referents; const b = right.attribution.referents;
  if (a.length && b.length && a.every(identity => identity.status === 'known') && b.every(identity => identity.status === 'known') && stable([...new Set(a.map(identity => identity.id))].sort()) !== stable([...new Set(b.map(identity => identity.id))].sort())) kinds.push('referents');
  if (identityChanged(left.attribution.narrator, right.attribution.narrator)) kinds.push('narrator');
  if (left.attribution.frameId !== right.attribution.frameId) kinds.push('frame');
  return kinds;
}

/** Evidence-limited adjacent-unit comparison. Missing features never imply a change. */
export function analyze(value: DiscourseInput, options: AnalyzeOptions = {}): Analysis {
  validateInput(value);
  const input = clone(value);
  const units: AnalyzedUnit[] = input.units.map(unit => ({ ...clone(unit), tokens: tokenize(unit.text, unit.id), features: clone(unit.features ?? {}), attribution: resolvedAttribution(unit.attribution), evidence: clone(unit.evidence ?? []) }));
  const frames = options.quoteCues === false ? [] : units.flatMap(unit => punctuationFrames(unit, input.source.id));
  const localFrames = new Set(frames.map(frame => frame.id));
  const transitions: Transition[] = [];
  for (let index = 1; index < units.length; index++) {
    const left = units[index - 1]; const right = units[index]; const kinds = changes(left, right);
    if (!kinds.length) continue;
    // JSON escaping makes even lone UTF-16 surrogates safe before URI encoding.
    const id = `tr:${encodeURIComponent(JSON.stringify(left.id))}>${encodeURIComponent(JSON.stringify(right.id))}`;
    const qualities = [...left.evidence, ...right.evidence].map(e => e.confidence).filter((quality): quality is number => quality !== undefined);
    const confidence = qualities.length ? Math.min(...qualities) : 0.5;
    transitions.push({ id, from: left.id, to: right.id, kinds, confidence, confidenceMeaning: 'uncalibrated-evidence-quality', lexicalContinuity: lexicalContinuity(left, right), attributionChange: kinds.some(kind => ['speaker', 'addressee', 'referents', 'narrator', 'frame'].includes(kind)), evidence: [{ id: `${id}:evidence`, status: 'derived', method: 'adjacent-explicit-feature-comparison', sourceId: input.source.id, note: 'Only compares supplied features and resolved identity declarations; confidence is evidence quality, not probability.', confidence }] });
  }
  const provenance: Analysis['provenance'] = { nodes: [{ id: `source:${input.source.id}`, kind: 'source' }], edges: [] };
  const sources = new Set([input.source.id]);
  for (const unit of units) {
    const observed: Evidence = { id: `${unit.id}:text`, status: 'observed', method: 'source-text-preservation', sourceId: input.source.id, note: 'Source-preserved text; annotations remain separate.' };
    const frameDeclaration: Evidence[] = unit.attribution.frameId !== 'root' && !localFrames.has(unit.attribution.frameId) ? [{ id: `${unit.id}:frame-declaration`, status: 'observed', method: 'supplied-frame-declaration', sourceId: input.source.id, note: `Caller-declared frame ${JSON.stringify(unit.attribution.frameId)}; containment and nesting are unvalidated.` }] : [];
    provenance.nodes.push({ id: `unit:${unit.id}`, kind: 'unit', evidence: [observed, ...clone(unit.evidence), ...frameDeclaration] });
    provenance.edges.push({ from: `source:${input.source.id}`, to: `unit:${unit.id}`, relation: 'contains' });
    for (const sourceId of new Set(unit.evidence.map(evidence => evidence.sourceId))) if (sourceId !== input.source.id) {
      if (!sources.has(sourceId)) { provenance.nodes.push({ id: `source:${sourceId}`, kind: 'source' }); sources.add(sourceId); }
      provenance.edges.push({ from: `unit:${unit.id}`, to: `source:${sourceId}`, relation: 'derived-from' });
    }
  }
  for (const transition of transitions) {
    provenance.nodes.push({ id: `transition:${transition.id}`, kind: 'transition', evidence: clone(transition.evidence) });
    provenance.edges.push({ from: `transition:${transition.id}`, to: `unit:${transition.from}`, relation: 'derived-from' }, { from: `transition:${transition.id}`, to: `unit:${transition.to}`, relation: 'derived-from' });
  }
  for (const frame of frames) {
    provenance.nodes.push({ id: `frame:${frame.id}`, kind: 'frame', evidence: [clone(frame.evidence)] });
    provenance.edges.push({ from: `frame:${frame.id}`, to: `unit:${frame.unitId}`, relation: 'derived-from' });
  }
  const uncertainty: Analysis['uncertainty'] = [];
  for (const unit of units) {
    for (const role of ['speaker', 'addressee', 'narrator'] as const) if (unit.attribution[role].status === 'unknown') uncertainty.push({ unitId: unit.id, field: role, reason: 'No explicit resolved identity declaration; grammatical person cannot establish identity.' });
    if (!unit.attribution.referents.length || unit.attribution.referents.some(identity => identity.status === 'unknown')) uncertainty.push({ unitId: unit.id, field: 'referents', reason: 'Referent identity unresolved.' });
    if (!Object.keys(unit.features).length) uncertainty.push({ unitId: unit.id, field: 'features', reason: 'No grammatical annotation supplied; no features inferred from surface text.' });
    if (unit.timestamp?.uncertainty !== undefined) uncertainty.push({ unitId: unit.id, field: 'timestamp', reason: `Supplied temporal uncertainty: ${unit.timestamp.uncertainty} ${unit.timestamp.unit ?? 'unspecified units'}.` });
    if (unit.attribution.frameId !== 'root' && !localFrames.has(unit.attribution.frameId)) uncertainty.push({ unitId: unit.id, field: 'frame', reason: `Caller-declared frame ${JSON.stringify(unit.attribution.frameId)} is unresolved: no local frame definition, containment or nesting has been established.` });
  }
  for (const frame of frames) uncertainty.push({ unitId: frame.unitId, field: 'frame', reason: frame.evidence.note! });
  return { schemaVersion: 'snad/1', id: input.id, input, units, transitions, frames, provenance, topology: topology(units, transitions), uncertainty, status: 'analyzed', methods: ['adjacent-explicit-feature-comparison', 'lowercase-token-jaccard', ...(options.quoteCues === false ? [] : ['quotation-punctuation-heuristic'])] };
}
export async function* analyzeStream(inputs: AsyncIterable<DiscourseInput>, options: AnalyzeOptions = {}): AsyncGenerator<Analysis> {
  for await (const input of inputs) yield analyze(input, options);
}
