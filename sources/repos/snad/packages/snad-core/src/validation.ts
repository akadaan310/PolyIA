import type { DiscourseInput, Evidence, Features, Identity, Source, Timestamp } from './types.js';

export function requireValid(condition: unknown, message: string): asserts condition {
  if (!condition) throw new TypeError(`Invalid ${message}`);
}
export const record = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
export const nonempty = (value: unknown): value is string => typeof value === 'string' && value.length > 0;
export const clone = <T>(value: T): T => structuredClone(value);
export function stable(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  if (record(value)) return `{${Object.keys(value).sort().filter(key => value[key] !== undefined).map(key => `${JSON.stringify(key)}:${stable(value[key])}`).join(',')}}`;
  return JSON.stringify(value) ?? 'null';
}
export function jsonValue(value: unknown, path = 'metadata', visited = new Set<unknown>()): void {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (typeof value === 'number') { requireValid(Number.isFinite(value), `${path}: nonfinite number`); return; }
  requireValid(record(value) || Array.isArray(value), `${path}: expected JSON value`);
  requireValid(Array.isArray(value) || Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null, `${path}: expected plain JSON object`);
  requireValid(!visited.has(value), `${path}: cyclic value`);
  visited.add(value);
  for (const [key, child] of Object.entries(value)) jsonValue(child, `${path}.${key}`, visited);
  visited.delete(value);
}
export function validateSource(value: unknown): asserts value is Source {
  requireValid(record(value) && nonempty(value.id) && nonempty(value.kind), 'source id/kind');
  for (const field of ['title', 'uri', 'license', 'revision']) requireValid(value[field] === undefined || typeof value[field] === 'string', `source.${field}`);
}
export function validateFeatures(value: unknown): asserts value is Features {
  requireValid(record(value), 'features object');
  for (const [key, feature] of Object.entries(value)) requireValid(typeof feature === 'string', `feature ${key} must be a string`);
  requireValid(value.person === undefined || ['1', '2', '3'].includes(value.person as string), 'person feature');
  requireValid(value.number === undefined || ['singular', 'dual', 'plural'].includes(value.number as string), 'number feature');
}
export function validateIdentity(value: unknown): asserts value is Identity {
  requireValid(record(value) && nonempty(value.id) && ['known', 'unknown'].includes(value.status as string), 'identity id/status');
  requireValid(value.label === undefined || typeof value.label === 'string', 'identity label');
}
export function validateEvidence(value: unknown): asserts value is Evidence {
  requireValid(record(value) && nonempty(value.id) && nonempty(value.sourceId) && nonempty(value.method), 'evidence id/sourceId/method');
  requireValid(['observed', 'derived', 'hypothesis', 'interpretation'].includes(value.status as string), 'evidence status');
  requireValid(value.confidence === undefined || (typeof value.confidence === 'number' && Number.isFinite(value.confidence) && value.confidence >= 0 && value.confidence <= 1), 'evidence confidence');
  requireValid(value.note === undefined || typeof value.note === 'string', 'evidence note');
}
function validateTimestamp(value: unknown): asserts value is Timestamp {
  requireValid(record(value), 'timestamp object');
  for (const field of ['start', 'end', 'uncertainty']) requireValid(value[field] === undefined || (typeof value[field] === 'number' && Number.isFinite(value[field])), `timestamp ${field}`);
  requireValid(value.uncertainty === undefined || (value.uncertainty as number) >= 0, 'timestamp uncertainty');
  requireValid(value.start === undefined || value.end === undefined || (value.start as number) <= (value.end as number), 'timestamp order');
  for (const field of ['unit', 'original']) requireValid(value[field] === undefined || typeof value[field] === 'string', `timestamp ${field}`);
}
export function validateInput(value: unknown): asserts value is DiscourseInput {
  requireValid(record(value) && nonempty(value.id) && Array.isArray(value.units), 'discourse input id/units');
  validateSource(value.source);
  const ids = new Set<string>(); const spans = new Set<string>();
  for (const unit of value.units) {
    requireValid(record(unit) && nonempty(unit.id) && typeof unit.text === 'string', 'unit id/text');
    requireValid(!ids.has(unit.id), `duplicate unit id: ${unit.id}`); ids.add(unit.id);
    if (unit.span !== undefined) {
      requireValid(record(unit.span) && Number.isSafeInteger(unit.span.start) && Number.isSafeInteger(unit.span.end), `unit ${unit.id} span`);
      requireValid((unit.span.start as number) >= 0 && (unit.span.end as number) >= (unit.span.start as number) && (unit.span.end as number) - (unit.span.start as number) === unit.text.length, `unit ${unit.id} span bounds/length`);
      const spanKey = `${unit.span.start}:${unit.span.end}`;
      requireValid(!spans.has(spanKey), `duplicate source span: ${spanKey}`); spans.add(spanKey);
      if (record(value.metadata) && typeof value.metadata.originalText === 'string') requireValid((unit.span.end as number) <= value.metadata.originalText.length && value.metadata.originalText.slice(unit.span.start as number, unit.span.end as number) === unit.text, `unit ${unit.id} span differs from originalText`);
    }
    if (unit.features !== undefined) validateFeatures(unit.features);
    if (unit.attribution !== undefined) {
      requireValid(record(unit.attribution), 'attribution object');
      for (const role of ['speaker', 'addressee', 'narrator']) if (unit.attribution[role] !== undefined) validateIdentity(unit.attribution[role]);
      if (unit.attribution.referents !== undefined) { requireValid(Array.isArray(unit.attribution.referents), 'referents array'); unit.attribution.referents.forEach(validateIdentity); }
      requireValid(unit.attribution.frameId === undefined || nonempty(unit.attribution.frameId), 'frame id');
    }
    if (unit.evidence !== undefined) { requireValid(Array.isArray(unit.evidence), 'unit evidence array'); unit.evidence.forEach(validateEvidence); }
    if (unit.timestamp !== undefined) validateTimestamp(unit.timestamp);
  }
  if (value.metadata !== undefined) { requireValid(record(value.metadata), 'metadata object'); jsonValue(value.metadata); }
  jsonValue(value, 'input');
}
