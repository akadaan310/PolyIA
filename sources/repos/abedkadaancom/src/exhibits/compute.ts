// Runs the small computations referenced by registry examples (Example.compute).
import { SYSTEMS, type SystemId } from '../math/numberSystems';
import { addressRecord, foldRecord, imageRecord, intervalRecord, loomRecord } from './records';
import { frequency } from '../math/music';

export function runCompute(spec: string): string[] {
  const [kind, ...rest] = spec.split(':');
  try {
    switch (kind) {
      case 'numbers': {
        const [, sysId, a, b] = rest;
        const sys = SYSTEMS[sysId as SystemId];
        if (!sys) return ['unknown number system'];
        const pairs: [string, string][] = a !== undefined && b !== undefined ? [[a, b]] : [['0', '1'], ['1', '0'], ['0', '0']];
        return pairs.map(([x, y]) => {
          const r = sys.divide(x, y);
          return `${x} / ${y} in ${sys.symbol}: ${r.kind === 'unique' ? `= ${r.quotient}` : r.failure === 'image' ? 'image failure (no c)' : 'kernel failure (many c)'}`;
        });
      }
      case 'matrix':
        return imageRecord(JSON.parse(rest.join(':')) as number[][]).output;
      case 'fold':
        return foldRecord(rest[0] ?? '', 99).output;
      case 'music':
        if (rest[0] === 'frequency') return [`MIDI ${rest[1]}: f = 440 · 2^((${rest[1]} − 69)/12) = ${frequency(Number(rest[1])).toFixed(3)} Hz`];
        return intervalRecord(Number(rest[1])).output;
      case 'loom':
        return addressRecord(rest.join(':')).output;
      case 'world':
        return loomRecord(Number(rest[0])).output;
      case 'borne':
        return loomRecord(90, rest[0] ?? null).output.slice(-2);
      default:
        return [];
    }
  } catch (e) {
    return [`computation failed: ${(e as Error).message}`];
  }
}
