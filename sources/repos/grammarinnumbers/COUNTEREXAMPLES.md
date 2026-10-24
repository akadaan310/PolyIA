# Counterexamples and Negative Results

Each entry is a constructed or measured case in which a plausible claim about arithmetic, or a claim made earlier in this investigation, fails. These cases set the scope of the theory.

| ID | Plausible claim | Counterexample | Failure mode | Source |
|---|---|---|---|---|
| GIN-NEG-001 | Floating-point addition is associative. | (0.1 + 0.1) + 0.4 = 0.6000000000000001 ≠ 0.6 = 0.1 + (0.1 + 0.4) in binary64; 242 of 729 tenth-triples fail. | one rounding per operation | PROP-032, EXP-012 |
| GIN-NEG-002 | If aⁿ⁻¹ ≡ 1 (mod n) then n is prime. | 341 = 11·31 (base 2); 561 = 3·11·17 passes every coprime base; 245 base-2 pseudoprimes below 10⁶. | Fermat's condition is necessary, not sufficient | PROP-043, EXP-010 |
| GIN-NEG-003 | Division by zero is always an error. | AArch64 SDIV returns 0 and RISC-V DIV returns −1, with no signal; IEEE returns ±∞. | totalization (repair 5) | THM-004, MACHINE_MODEL |
| GIN-NEG-004 | Compilers always exploit "division by zero is undefined" to delete a later zero test. | gcc 13.3 -O2 keeps the test (test + cmove); clang 18 -O2 deletes it. | the permission is not an obligation; behaviour is compiler-specific | OBS-008 |
| GIN-NEG-005 | 1/0 = ∞. | In IEEE 754, 0 × ∞ = NaN, so ∞ does not solve 0·c = 1; on the projective line ∞ exists but 0·∞ is undefined; in ℝ there is no ∞. | the value is a limit-motivated selection, not a converse solution | PROP-015, THM-006 |
| GIN-NEG-006 | Symbolic simplification preserves meaning. | x/x → 1 and (x² − 1)/(x − 1) → x + 1 enlarge the domain (to include 0, resp. 1). | cancellation drops the condition g ≠ 0 | PROP-014 |
| GIN-NEG-007 | Truncated subtraction is subtraction. | 0 ∸ 1 = 0 but 1 + 0 ≠ 0. | totalization, not converse | PROP-016 |
| GIN-NEG-008 | Re-shaping an evaluation (balanced instead of Horner) makes it asymptotically cheaper. | With schoolbook multiplication both shapes are Θ(k²) in limb operations (slopes 1.998 vs 1.949 → 2). | shape changes depth; bit work depends on the multiplication used | OBS-013 |
| GIN-NEG-009 | 0⁰ has a determined value. | As the empty product 0⁰ = 1 by convention; as a limit form lim f^g with f, g → 0 it is indeterminate. The evaluator marks the convention. | convention vs converse/limit | expr, EXP-003 |
| GIN-NEG-010 | Python floats follow IEEE 754 on division by zero. | Python raises ZeroDivisionError for 1.0/0.0 (language check before the IEEE operation); C, Java, Go and JavaScript return +inf. | the language adds a signal layer | OBS-006 |
| GIN-NEG-011 | `-2147483648` is an int32 literal. | In C (and in GiN's evaluator) it is unary minus applied to 2147483648, which does not fit in int32; libraries define INT_MIN as (−2147483647 − 1). | typing layer | expr, EXP-003 |
| GIN-NEG-012 | Brahmagupta's 0/0 = 0 is inconsistent. | It is a consistent *selection*: meadows and Lean's mathlib adopt exactly 0⁻¹ = 0. It fails only as a claim to *solve* 0·c = 0 uniquely. | conflating totalization with derivation | HIST-001 |
| GIN-NEG-013 | (own design error) Exponents can be evaluated in the same domain as the base. | 0^−1 in ℤ/6 evaluated as 0⁵ = 0, because −1 ≡ 5. Exponents are integers acting on the domain (and only exponents ≡ mod the group exponent may be reduced, for units). | type confusion between a ring and the integers acting on it | RESULTS §J C-001 |
| GIN-NEG-014 | A complete residue digit system gives unique numerals. | b = 2, D = {−1, 2}: the word (−1)(2) denotes 0, so leading "zero-denoting" blocks are not just zeros. | prefixes denoting 0 | PROP-004 |
| GIN-NEG-015 | Ordinary binary names every integer. | The residue expansion of −1 never terminates (…111); fixed-width hardware truncates it. | negative numbers have only infinite (2-adic) standard numerals | PROP-008 |
| GIN-NEG-016 | Adjoining a "0/0" element to the fractions is harmless. | (0,0) is cross-multiplication-related to every pair, so (1,0) ~ (0,0) ~ (0,1) while (1,0) ≁ (0,1): transitivity fails. | the null pair collapses the quotient | THM-006 |
| GIN-NEG-017 | Floating-point overflow and division by zero are the same event. | 1/10⁻³²⁰ → +∞ with overflow (the divisor is subnormal, not zero); 1/10⁻³³⁰ → +∞ with divideByZero (the literal rounded to +0). | distinct flags, same datum | OBS-016 |

## Rejected hypotheses

- **GIN-REJ-001** "1/0 = +∞ answers the converse question." Rejected by PROP-015 and THM-006 (NEG-005).
- **GIN-REJ-002** (session-1 working assumption) "The simulator need not model signaling NaNs to match hardware flags." Rejected by EXP-005: all 101 initial flag mismatches were operations on signaling NaNs, where hardware raises *invalid*. Kept as evidence that the experiment can find defects in the instrument.
- **GIN-REJ-003** "Balanced evaluation of numerals is asymptotically cheaper than Horner's rule in bit cost." Rejected for schoolbook multiplication (NEG-008); the surviving form needs a subquadratic multiplication.
- **GIN-REJ-004** "Compilers delete post-division zero tests" as a general statement (NEG-004).
