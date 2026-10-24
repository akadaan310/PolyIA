# Literature Review (session 1 baseline)

The canonical bibliography, with per-entry verification status, is `book/content/bibliography.json` (57 entries: 30 metadata-verified by web search on 2026-10-08, 12 cited from standards or secondary sources, 15 from the collaborator's knowledge and marked unverified). **"Metadata verified" never means the full text was read.** Primary-source reading is a recorded debt (GIN-OPEN-005).

For each area: what is known, what GiN adopts, and what (if anything) GiN adds.

## 1. Foundations of number
- **Known.** Dedekind (1888) and Peano (1889) characterize ℕ as the successor algebra; primitive recursion defines +, ×, ^; Church (1941) represents numbers as iterators. The integers, rationals, reals and complex numbers are obtained by standard constructions (Grothendieck group, field of fractions, completion, algebraic closure).
- **GiN adopts** all of this unchanged (GIN-DEF-001, 009, 010, 013).
- **GiN adds** a reading of the constructions ℕ → ℤ → ℚ as *admissibility repairs* that keep the unanswered converse problem as data (GIN-PROP-017), and the observation (GIN-THM-006) that in the pair construction the null pair (0, 0) is exactly the obstruction to adjoining "0/0". Both are presentations of classical mathematics.

## 2. Positional notation, bijective numeration, b-adic expansions
- **Known.** Positional systems, radix conversion and their costs (Knuth 1997, §4.1, §4.4); bijective base-k ("k-adic") notation (Smullyan 1961; Forslund 1995); balanced ternary; b-adic expansions and two's complement as truncated 2-adic integers (folklore; Knuth §4.1).
- **GiN adds** the CGT packaging: numerals as operation expressions with affine moves, canonical numerals as CGT grammatical addresses with zero's address the empty word (GIN-PROP-002), and the conjugacy of CGT's heap numeration with shifted bijective binary (GIN-PROP-006; not found in the sources reviewed, likely folklore).

## 3. Automata and arithmetic
- **Known.** Büchi (1960) connected weak monadic second-order arithmetic with finite automata; Cobham (1969) showed recognizability depends on the base; Hodgson (1983) and Khoussainov & Nerode (1995) introduced automatic structures, whose first-order theories are decidable; Blumensath & Grädel (2000) developed their theory. (ℕ, +) is automatic; (ℕ, +, ×) is not, because its theory is undecidable (Gödel 1931; Church 1936).
- **GiN adopts** these results as GIN-THM-005 and reads them as a boundary between regular and non-regular operational grammars over numerals. The finite carry monoid is the algebraic face of the automaticity of addition (GIN-PROP-020).

## 4. Carry propagation and adders
- **Known.** The average longest carry chain is about log₂ n (Burks, Goldstine & von Neumann 1946; Knuth 1978). Carry computation is a prefix computation (Ladner & Fischer 1980; Brent & Kung 1982), with classical networks by Sklansky (1960) and Kogge & Stone (1973). Blelloch (1990) surveys prefix sums for any associative operator.
- **GiN adds** the CGT reading: carry-lookahead is CGT arithmetic compilation (CGT-DEF-011) of the carry automaton's three-element transition monoid; ripple vs prefix is CGT-THM-004's shape trade-off; and a candidate sixth mechanism (M-ASSOC, GIN-CONJ-001).

## 5. Grammar compression and addition chains
- **Known.** Straight-line programs; the smallest grammar problem (Charikar et al. 2005). For unary strings, SLPs correspond to addition chains, the classical problem of computing xⁿ with fewest multiplications (Knuth 1997, §4.6.3).
- **GiN adds** the observation that positional notation is exactly this compression of the successor grammar, connecting CGT's M-SHARE with exponentiation (GIN-PROP-007, GIN-REI-008).

## 6. Bit complexity of arithmetic
- **Known.** Schoolbook Θ(n²) multiplication and division, Karatsuba & Ofman (1962) Θ(n^{log₂3}), and O(n log n) multiplication (Harvey & van der Hoeven 2021); Brent & Zimmermann (2010) is a modern reference. Euclid's algorithm takes O(log a) steps (Lamé 1844) and Θ(n²) bit operations naively; its average step count is (12 ln 2/π²) ln n + O(1) (Heilbronn 1969; Dixon 1970; Porter 1975). Binary gcd: Stein (1967).
- **GiN adopts** these as cost targets and *measures* them with counted limb operations (GIN-EXP-008, 009, 011). Nothing new.

## 7. Division by zero and its extensions
- **Known.** Fields exclude division by zero; the projective line and Riemann sphere adjoin a single ∞; the extended reals adjoin ±∞; IEEE 754 (2019) specifies ±∞, NaN, signed zeros and the divideByZero/invalid flags (Goldberg 1991; Kahan 1987 on the sign of zero). Meadows (Bergstra & Tucker 2007) totalize inversion with 0⁻¹ = 0 while keeping the commutative-ring axioms; Lean's mathlib uses the same convention (mathlib Community 2020). Wheels (Carlström 2004) extend any commutative ring with an involution "/" so that division by 0 yields elements, at the cost of 0·x = 0 and with a weakened distributive law. Historically, Brahmagupta (628 CE) gave rules for zero including 0/0 = 0, and Bhāskara II named a quantity with zero divisor *khahara* (MacTutor; Plofker 2009).
- **GiN adds** a single classification — image failure (1/0) vs kernel failure (0/0) — that covers fields and all commutative rings (GIN-THM-001, COR-001), the extension trilemma that sorts every known system by *which law gives way* (GIN-THM-004), and the pair-level characterization of indeterminate forms (GIN-THM-006). The pair construction with (0, 0) kept as an absorbing element is essentially Carlström's wheel of fractions; GiN's statement that every indeterminate form computes the null pair should be checked against Carlström's paper before any novelty is suggested.

## 8. Machine arithmetic semantics
- **Specifications.** Intel SDM (IDIV raises #DE on zero divisor and quotient overflow); Arm ARM (AArch64 SDIV/UDIV: no trap, result 0; secondary sources); RISC-V M extension (x/0 → all ones with remainder = dividend; overflow → −2^{w−1}, remainder 0; rationale: simple divider circuitry, no trap so languages can add a branch); ISO C17 §6.5.5 (undefined behaviour); JLS §15.17.2 (ArithmeticException; MIN/−1 = MIN); Rust (panic on zero divisor and on overflow); Go (run-time panic on zero divisor; constant division by zero is a compile error; MIN/−1 = MIN); ECMAScript (Number follows IEEE; BigInt division by 0n throws RangeError); Python (ZeroDivisionError for int and float).
- **GiN adds** measurements on one host (GIN-EXP-004) confirming each specified behaviour that can be run there, and two empirical observations: the gcc/clang divergence on a post-division zero test (GIN-OBS-008) and the host's after-rounding tininess detection (GIN-OBS-009).

## 9. Number theory
- **Known.** Euclid (*Elements* VII); Bézout; the Chinese remainder theorem; Fermat's little theorem; Korselt's criterion (1899) and the infinitude of Carmichael numbers (Alford, Granville & Pomerance 1994); Miller (1976) and Rabin (1980) strong probable-prime tests; deterministic base sets (Sorenson & Webster 2017); pseudoprime counts (Pomerance, Selfridge & Wagstaff 1980); Pollard's rho (1975).
- **GiN adopts** all of these; presents each algorithm as a transition system with an invariant; reproduces the published counts below 10⁶ (GIN-EXP-010). Nothing new.

## 10. Computational Grammar Theory (parent corpus)
- The CGT ledger (Kadaan 2026; read-only) supplies operational grammars, addresses, transition monoids, arithmetic compilation, the mechanism taxonomy and the three-layer separation. `CGT_CONCEPT_MAP.md` records how each behaves on numbers.

## 11. Areas not yet reviewed
Computer algebra systems' handling of x/0 and of side conditions in simplification; interval arithmetic and its division by intervals containing 0; posits/unums; decimal floating point; proof-assistant conventions beyond Lean's mathlib; the didactics literature on division by zero; category-theoretic treatments of totalization.
