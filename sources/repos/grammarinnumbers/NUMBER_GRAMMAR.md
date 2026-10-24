# The Grammar of Number: 0, 1, 2, 3, 4, …

This document develops the first target of the research: the grammar of number itself. Formal statements are in `DEFINITIONS.md` and `RESULTS.md`; this is the synthesis.

## 1. Twelve readings of "3", kept apart

| Reading | What "3" is | Layer (GIN-DEF-001…004) |
|---|---|---|
| mathematical object | the element S(S(S(0))) of the successor algebra | value |
| count | the cardinality of {a, b, c} | value (via cardinality) |
| position | the fourth place in 0, 1, 2, 3, … (or the third, counting from 1) | value with an order convention |
| state | a node of the successor transition system T_ℕ | value as state |
| address | the canonical numeral addr(3) in some digit grammar: `3`, `11₂`, `SSS`, `10₃` | numeral |
| digit | the symbol `3` of the decimal alphabet | numeral alphabet |
| symbol | a token in an expression such as `3 + 1` | syntax |
| sequence | the word 3 in the language of decimal numerals | numeral |
| machine representation | `0x00000003` (int32), `0x4008000000000000` (binary64) | encoding |
| transition result | the value of `1 + 2`, `S(2)`, `6 / 2` | value (output of a move) |
| algebraic element | 3 ∈ ℤ, ℚ, ℝ, ℂ; the class 3 + nℤ in ℤ/n; 3 = 0 in ℤ/3 | value in a chosen structure |
| computational value | what a register holds after `mov eax, 3` | machine state |

Where they agree: every reading denotes, or encodes, the same value 3 in ℕ. Where they diverge: a digit is not a number (`3` is a symbol); a numeral is not a number (`03` and `3` are different words); a binary representation is not the number (`11₂` vs `3`); a machine word is not the integer (`0xFFFFFFFF` decodes to −1 or 4,294,967,295 depending on signedness); a residue class is not an integer (3 = 0 in ℤ/3).

## 2. The smallest grammar: 0 → 1 → 2 → 3 → 4

The structural grammar ℕ → 0 | S(ℕ) generates the terms 0, S(0), S(S(0)), …. Read as a transition system T_ℕ, the transition 0 → 1 → 2 → 3 → 4 is four applications of the single move S. Three facts make this the smallest laboratory for transition grammar:

1. **Every value is reached from 0 by a unique word** (Sⁿ), so the unary numeral is simultaneously the value's *name*, its *address* and the *program* that computes it.
2. **The converse move P is partial**: P is inadmissible at 0. This is the first boundary of arithmetic, and it is the boundary that 0 − 1 meets in ℕ.
3. **n + 1 is a grammatical transition, not merely notation**: by the primitive-recursive definition add(m, S n) = S(add(m, n)), adding 1 *is* one application of S, and adding k is k applications (GIN-PROP-003).

The segment [0, 4] — written `0{1,2,3}4` in the notation proposed by A. Kadaan (GIN-DEF-012) — is the finite neighbourhood in which these facts can be inspected: the boundary {0, 4} where exactly one move is admissible, the interior {1, 2, 3} where both are. GIN-REI-010 records the honest verdict: the notation is formal (checkable, diagnosable) but adds no mathematics.

## 3. Numerals as programs

A positional numeral is a word over digit moves d : x ↦ b·x + d (GIN-DEF-005). Consequences, each proved in `RESULTS.md`:

- **Numeral ≠ number** (PROP-001): the value map is surjective and non-injective exactly by leading zeros.
- **Zero's address is the empty word** (PROP-002): the written "0" is a convention.
- **Bijective notation** has no zero digit and is a bijection between words and ℕ (PROP-004).
- **Compilation**: a numeral compiles to the affine map x ↦ b^{|w|}x + val(w) (PROP-005); concatenation of numerals is composition of maps.
- **CGT's heap numeration is bijective binary shifted by one** (PROP-006).
- **Positional notation is compression**: the binary numeral of n is a straight-line program of size O(log n) for the unary term Sⁿ(0) — CGT's M-SHARE — with exactly the shape of square-and-multiply exponentiation (PROP-007, PROP-041).
- **Negative numbers have no finite standard numerals**: the residue expansion of −1 is …111, the 2-adic expansion; fixed-width two's complement keeps its first w digits (PROP-008). Balanced ternary names every integer finitely (PROP-004).
- **Rationals have eventually periodic expansions** produced by a finite transition system on remainders (PROP-009).

## 4. Number systems as grammars

| Carrier | Total ops | Admissibility of inverses | Identities | Order | Typical representations |
|---|---|---|---|---|---|
| ℕ | +, × | a − b iff a ≥ b; a/b iff b ≠ 0 and b \| a | 0 (+), 1 (×) | total, well-founded | unary, positional, bijective |
| ℤ | +, −, × | a/b iff b ≠ 0 and b \| a | 0, 1 | total | sign–magnitude, balanced ternary, two's complement (fixed width) |
| ℚ | +, −, × | a/b iff b ≠ 0 | 0, 1 | total, dense | pairs in lowest terms; periodic positional expansions |
| ℝ | +, −, × | a/b iff b ≠ 0; √a iff a ≥ 0 (two roots, principal branch) | 0, 1 | total, complete | infinite expansions; computable reals; floating-point approximations |
| ℂ | +, −, × | a/b iff b ≠ 0; √a always (two roots for a ≠ 0); log a iff a ≠ 0 (infinitely many) | 0, 1 | none compatible with the field | pairs of reals |
| ℤ/n | +, −, × | a/b iff gcd(b, n) \| a, unique iff gcd(b, n) = 1 (THM-002) | 0, 1 | none compatible | residues 0 … n−1 |
| ℤ_p (p-adic integers) | +, −, × | a/b iff v_p(b) ≤ v_p(a) | 0, 1 | none compatible | infinite digit sequences to the left |
| w-bit words | +, −, × mod 2ʷ | division per machine model (MACHINE_MODEL) | 0, 1 | signed/unsigned interpretations | bit strings |
| IEEE binary64 | +, −, ×, ÷, √ (all total, with special data) | no inverse is exact in general; x/0 = ±∞, 0/0 = NaN | +0 for + (with signed-zero rules), 1 for × | total on non-NaN (with −0 = +0) | 64-bit strings |

Each step ℕ → ℤ → ℚ → ℝ → ℂ is an admissibility repair (GIN-DEF-017, GIN-PROP-017): the carrier grows exactly so that a family of converse problems acquires solutions. ℤ/n and fixed-width words take the other route — a quotient that makes subtraction total by giving up order. Floating point takes a third route: it keeps every operation total by giving up exactness and some algebraic laws (associativity, PROP-032; the converse reading of division, PROP-015).

## 5. Zero and one

**Zero** is: the additive identity; the empty count (|∅|); the base of the successor grammar; the address-free value (empty numeral); a positional placeholder; an absorbing element for × (derived in rings, assumed in semirings: PROP-012); the boundary of P in T_ℕ; the fixed point of x ↦ 2x and of x ↦ x²; the origin; and, in machines, the bit pattern `0…0`. Zero is **not**: NULL (absence of a reference), undefined (no meaning), the empty string (a numeral, not a number), false (a truth value, encoded identically in many languages), absence, uninitialized memory (no defined value; reading it can be undefined behaviour in C), or NaN (a datum that is not a number and is unequal to itself). IEEE 754 has two zeros, +0 and −0, equal under comparison but distinguished by 1/x.

**One** is: the multiplicative identity; the unit; S(0); the generator of ℕ under + (every n is 1 + 1 + ⋯ + 1); the scale of positional notation's lowest place; a fixed point of squaring. The distinction **identity vs generator** matters: 0 is the identity of + but generates nothing; 1 is the identity of × but generates all of ℕ under +. The transitions 0 → 1 and 1 → 2 are the same move S, but 0 → 1 crosses from the empty count to the first non-empty one, and only 0 has no predecessor.

## 6. Fixed points

| Sense | Example | Computational content |
|---|---|---|
| f(x) = x | x² = x has solutions 0, 1 in ℤ; four idempotents in ℤ/6 (0, 1, 3, 4) | solving an equation (a converse problem) |
| limit of iteration | Newton's x ↦ (x + a/x)/2 converges to √a; CGT's PageRank | existence, uniqueness, rate, stopping rule |
| least fixed point | ℕ = least X with {0} ∪ S(X) ⊆ X | induction, recursion; the definition of the grammar itself |
| terminal state | Euclid's (g, 0); a state with no admissible move | termination of a transition system |

These share a definition, not a method (GIN-REI-007).
