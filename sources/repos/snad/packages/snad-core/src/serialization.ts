import type { Analysis } from './types.js';
import { analyze } from './analysis.js';
import { clone, record, requireValid, stable } from './validation.js';

function validated(value: unknown): Analysis {
  requireValid(record(value) && value.schemaVersion === 'snad/1', 'analysis schema version (expected snad/1)');
  requireValid(Array.isArray(value.methods), 'analysis methods');
  const reconstructed = analyze(value.input as Analysis['input'], { quoteCues: value.methods.includes('quotation-punctuation-heuristic') });
  requireValid(stable(value) === stable(reconstructed), 'analysis schema or derived transition/provenance mismatch; replay input with analyze');
  return clone(reconstructed);
}
export function serialize(analysis: Analysis): string { return JSON.stringify(validated(analysis), null, 2); }
export function deserialize(text: string): Analysis {
  requireValid(typeof text === 'string', 'serialized analysis string');
  let value: unknown; try { value = JSON.parse(text); } catch { throw new TypeError('Invalid serialized analysis JSON'); }
  return validated(value);
}
