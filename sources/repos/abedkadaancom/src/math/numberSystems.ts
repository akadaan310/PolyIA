// The Arithmetic of Possibility: explicit number systems with declared laws.
//
// Division is treated as the converse of multiplication: a / b asks for the set
// of c with b·c = a. That set is empty (an image failure: a is not in the image
// of c ↦ b·c), a single element (a quotient), or larger (a kernel failure: the
// map c ↦ b·c is not injective, so the answer is not determined). This is the
// classification of Grammar in Numbers, GIN-THM-001 (Kadaan, 2026), restating
// the standard fact that in a commutative ring the solutions of b·c = a are
// empty or a coset of the annihilator Ann(b).

import { Q } from './rational';

export type SystemId = 'N' | 'Z' | 'Q' | 'F2' | 'Z6';

export interface DivisionResult {
  kind: 'unique' | 'none' | 'many';
  /** Which test failed: image (no solution) or kernel (no unique solution). */
  failure: null | 'image' | 'kernel';
  quotient: string | null;
  /** All solutions, when the system is finite. */
  solutions: string[] | null;
  explanation: string;
}

export interface MapSummary {
  /** Image of c ↦ b·c, as a description and (for finite systems) as a set. */
  image: string;
  imageSet: string[] | null;
  kernel: string;
  kernelSet: string[] | null;
  injective: boolean;
  surjective: boolean;
}

export interface NumberSystem {
  id: SystemId;
  name: string;
  symbol: string;
  isField: boolean;
  /** Number of elements, or null if infinite. */
  size: number | null;
  description: string;
  parse(s: string): string | null;
  add(a: string, b: string): string | null;
  mul(a: string, b: string): string | null;
  divide(a: string, b: string): DivisionResult;
  multiplicationMap(b: string): MapSummary;
  elements(): string[] | null;
}

const INT = /^\s*-?\d{1,30}\s*$/;
const RAT = /^\s*(-?\d{1,30})\s*(?:\/\s*(-?\d{1,30}))?\s*$/;

function parseQ(s: string): Q | null {
  const m = RAT.exec(s);
  if (!m) return null;
  const d = m[2] === undefined ? 1n : BigInt(m[2]);
  if (d === 0n) return null;
  return Q.of(BigInt(m[1]!), d);
}

/** ℕ = {0, 1, 2, …} (the successor algebra; 0 included, following Dedekind/Peano as in GIN-DEF-001). */
const naturals: NumberSystem = {
  id: 'N',
  name: 'Natural numbers',
  symbol: 'ℕ',
  isField: false,
  size: null,
  description: 'ℕ = {0, 1, 2, …}, generated from 0 by the successor S. Addition and multiplication are total; subtraction and division are partial.',
  parse(s) {
    if (!INT.test(s)) return null;
    const v = BigInt(s.trim());
    return v >= 0n ? v.toString() : null;
  },
  add: (a, b) => (BigInt(a) + BigInt(b)).toString(),
  mul: (a, b) => (BigInt(a) * BigInt(b)).toString(),
  divide(a, b) {
    return divideIntegers(BigInt(a), BigInt(b), 'ℕ', true);
  },
  multiplicationMap(b) {
    const bb = BigInt(b);
    if (bb === 0n) return infiniteZeroMap('ℕ');
    return {
      image: bb === 1n ? 'ℕ (every natural number)' : `${bb}ℕ = {0, ${bb}, ${2n * bb}, …}`,
      imageSet: null,
      kernel: '{0}',
      kernelSet: ['0'],
      injective: true,
      surjective: bb === 1n,
    };
  },
  elements: () => null,
};

const integers: NumberSystem = {
  id: 'Z',
  name: 'Integers',
  symbol: 'ℤ',
  isField: false,
  size: null,
  description: 'ℤ = {…, −2, −1, 0, 1, 2, …}, a commutative ring. Every element has an additive inverse; only ±1 have multiplicative inverses.',
  parse(s) {
    return INT.test(s) ? BigInt(s.trim()).toString() : null;
  },
  add: (a, b) => (BigInt(a) + BigInt(b)).toString(),
  mul: (a, b) => (BigInt(a) * BigInt(b)).toString(),
  divide(a, b) {
    return divideIntegers(BigInt(a), BigInt(b), 'ℤ', false);
  },
  multiplicationMap(b) {
    const bb = BigInt(b);
    if (bb === 0n) return infiniteZeroMap('ℤ');
    const unit = bb === 1n || bb === -1n;
    return {
      image: unit ? 'ℤ (every integer)' : `${bb < 0n ? -bb : bb}ℤ, the multiples of ${bb < 0n ? -bb : bb}`,
      imageSet: null,
      kernel: '{0}',
      kernelSet: ['0'],
      injective: true,
      surjective: unit,
    };
  },
  elements: () => null,
};

const rationals: NumberSystem = {
  id: 'Q',
  name: 'Rational numbers',
  symbol: 'ℚ',
  isField: true,
  size: null,
  description: 'ℚ, the field of fractions of ℤ. Every non-zero element has a multiplicative inverse, so a / b is defined exactly when b ≠ 0.',
  parse(s) {
    const q = parseQ(s);
    return q ? q.toString() : null;
  },
  add: (a, b) => parseQ(a)!.add(parseQ(b)!).toString(),
  mul: (a, b) => parseQ(a)!.mul(parseQ(b)!).toString(),
  divide(a, b) {
    const qa = parseQ(a)!;
    const qb = parseQ(b)!;
    if (!qb.isZero()) {
      const c = qa.div(qb);
      return {
        kind: 'unique',
        failure: null,
        quotient: c.toString(),
        solutions: [c.toString()],
        explanation: `${b} ≠ 0 has the inverse ${Q.one.div(qb).toString()} in ℚ, so the unique c with ${b}·c = ${a} is c = ${a}·${Q.one.div(qb).toString()} = ${c.toString()}.`,
      };
    }
    return zeroDivisor(qa.isZero(), a, 'ℚ');
  },
  multiplicationMap(b) {
    const qb = parseQ(b)!;
    if (qb.isZero()) return infiniteZeroMap('ℚ');
    return { image: 'ℚ (every rational)', imageSet: null, kernel: '{0}', kernelSet: ['0'], injective: true, surjective: true };
  },
  elements: () => null,
};

function modular(n: number, id: SystemId, name: string, symbol: string, description: string): NumberSystem {
  const els = Array.from({ length: n }, (_, i) => i.toString());
  const norm = (x: bigint) => (((x % BigInt(n)) + BigInt(n)) % BigInt(n)).toString();
  return {
    id,
    name,
    symbol,
    isField: isPrime(n),
    size: n,
    description,
    parse(s) {
      return INT.test(s) ? norm(BigInt(s.trim())) : null;
    },
    add: (a, b) => norm(BigInt(a) + BigInt(b)),
    mul: (a, b) => norm(BigInt(a) * BigInt(b)),
    divide(a, b) {
      const sols = els.filter((c) => norm(BigInt(b) * BigInt(c)) === a);
      if (sols.length === 1) {
        return {
          kind: 'unique',
          failure: null,
          quotient: sols[0]!,
          solutions: sols,
          explanation: `Checking all ${n} elements, exactly one c satisfies ${b}·c = ${a} in ${symbol}: c = ${sols[0]}.`,
        };
      }
      if (sols.length === 0) {
        return {
          kind: 'none',
          failure: 'image',
          quotient: null,
          solutions: [],
          explanation: `No element c of ${symbol} satisfies ${b}·c = ${a}: ${a} is not in the image of c ↦ ${b}·c. This is an image failure.`,
        };
      }
      return {
        kind: 'many',
        failure: 'kernel',
        quotient: null,
        solutions: sols,
        explanation: `Every c in {${sols.join(', ')}} satisfies ${b}·c = ${a} in ${symbol}. The solutions form a coset of the kernel of c ↦ ${b}·c, so no single quotient is determined. This is a kernel failure.`,
      };
    },
    multiplicationMap(b) {
      const img = [...new Set(els.map((c) => norm(BigInt(b) * BigInt(c))))].sort((x, y) => +x - +y);
      const ker = els.filter((c) => norm(BigInt(b) * BigInt(c)) === '0');
      return {
        image: `{${img.join(', ')}}`,
        imageSet: img,
        kernel: `{${ker.join(', ')}}`,
        kernelSet: ker,
        injective: ker.length === 1,
        surjective: img.length === n,
      };
    },
    elements: () => els,
  };
}

const f2 = modular(
  2,
  'F2',
  'The two-element field',
  'F₂',
  'F₂ = {0, 1} with addition and multiplication modulo 2. It is a field: 1 is its own inverse. Because 1 + 1 = 0, it has characteristic 2.',
);
const z6 = modular(
  6,
  'Z6',
  'Integers modulo 6',
  'ℤ/6',
  'ℤ/6 = {0, …, 5} modulo 6: a ring with zero divisors (2·3 = 0), so some non-zero divisors still fail to give unique quotients.',
);

function isPrime(n: number): boolean {
  if (n < 2) return false;
  for (let i = 2; i * i <= n; i++) if (n % i === 0) return false;
  return true;
}

function infiniteZeroMap(symbol: string): MapSummary {
  return {
    image: '{0}',
    imageSet: ['0'],
    kernel: `${symbol} (every element is sent to 0)`,
    kernelSet: null,
    injective: false,
    surjective: false,
  };
}

function zeroDivisor(aIsZero: boolean, a: string, symbol: string): DivisionResult {
  if (!aIsZero) {
    return {
      kind: 'none',
      failure: 'image',
      quotient: null,
      solutions: [],
      explanation: `Every c in ${symbol} has 0·c = 0, so no c gives 0·c = ${a}. ${a} is not in the image of c ↦ 0·c = {0}. This is an image failure: there is nothing to choose.`,
    };
  }
  return {
    kind: 'many',
    failure: 'kernel',
    quotient: null,
    solutions: null,
    explanation: `Every c in ${symbol} satisfies 0·c = 0. The kernel of c ↦ 0·c is all of ${symbol}, so the converse relation does not pick out one value. This is a kernel failure: there is too much to choose from.`,
  };
}

function divideIntegers(a: bigint, b: bigint, symbol: string, naturalsOnly: boolean): DivisionResult {
  if (b === 0n) return zeroDivisor(a === 0n, a.toString(), symbol);
  if (a % b === 0n && (!naturalsOnly || a / b >= 0n)) {
    const c = a / b;
    return {
      kind: 'unique',
      failure: null,
      quotient: c.toString(),
      solutions: [c.toString()],
      explanation: `c ↦ ${b}·c is injective on ${symbol} (its kernel is {0}), and ${b}·${c} = ${a}, so the unique quotient is ${c}.`,
    };
  }
  return {
    kind: 'none',
    failure: 'image',
    quotient: null,
    solutions: [],
    explanation: `${a} is not a multiple of ${b} within ${symbol}, so it is not in the image of c ↦ ${b}·c. The quotient exists in a larger system (ℚ) but not here. This is an image failure.`,
  };
}

export const SYSTEMS: Record<SystemId, NumberSystem> = { N: naturals, Z: integers, Q: rationals, F2: f2, Z6: z6 };
export const GATE_SYSTEMS: SystemId[] = ['N', 'Z', 'F2'];

/**
 * How JavaScript's IEEE 754 binary64 encoding represents a division. This is
 * an encoding-layer fact (GIN-DEF-003), not a definition of field division.
 */
export function ieeeRepresentation(a: number, b: number): { value: string; note: string } {
  const v = a / b;
  if (Number.isNaN(v)) return { value: 'NaN', note: 'IEEE 754 returns the special datum NaN ("not a number"). NaN is not a number in any field; it marks that the operation had no determined result.' };
  if (!Number.isFinite(v)) return { value: v > 0 ? 'Infinity' : '-Infinity', note: 'IEEE 754 returns the special datum ∞. ∞ is not an element of ℚ or ℝ, and assigning it gives up the field laws (∞·0 has no consistent value).' };
  return { value: Object.is(v, -0) ? '-0' : String(v), note: 'An ordinary binary64 value. It agrees with the field quotient when that quotient is exactly representable.' };
}
