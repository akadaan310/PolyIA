# Formal Models

## 1. Cost models
- **Bit/word model (default for growing operands).** Operands are measured by bit length L. A word operation acts on w-bit limbs (w = 32 in `ginsdk.bigint`): add/subtract with carry, limb product, two-by-one-limb quotient estimate, limb comparison (GIN-DEF-070). Statements of the form "Θ(L²)" refer to counted word operations.
- **Unit-cost model (bounded operands only).** One arithmetic operation costs 1 when operands fit in a fixed width; the width is stated (e.g. int32). Every unit-cost claim names the bound — this is the arithmetic form of CGT-THM-003 ("O(1) only while the address fits in a word").
- **Rule-application model.** For Peano arithmetic, one rewrite step per primitive-recursion equation (GIN-DEF-010).
- **Circuit model.** Gate count and depth over a stated basis with fan-in ≤ 2 (GIN-DEF-040). Fan-out and wire length are not modelled (Brent & Kung's area model is not used).
- **Wall-clock time** is secondary evidence only, recorded in fields ending `_s`.

## 2. The four layers of an arithmetic outcome
GIN-DEF-061 refines CGT's three layers by inserting **typing** between syntax and semantics:

| Layer | Question | Formal object | Example where it fails |
|---|---|---|---|
| syntax | well-formed sentence? | parse tree | `1 +` |
| typing | do literals and variables denote elements of the domain? | lifted operands | `0.5` in ℤ; `2147483648` in int32; `x` with no value |
| semantics | does each operation have exactly one result? | Sol (GIN-DEF-015) | `1/0` (no solution), `0/0` (non-unique), `0 − 1` in ℕ |
| execution | what does the machine model do? | outcome (GIN-DEF-062) | `2147483647 + 1` wraps or is UB; `1/0` traps on x86; `1.0/0.0` raises in Python |

The layers are independent in the sense of CGT-PROP-002: syntactically fine but ill-typed (`0.5` in ℤ); well-typed but semantically empty (`1/0` in ℚ); semantically fine but failing at execution (`(−2147483647 − 1)/−1` has the unique integer solution 2,147,483,648, but x86 traps); semantically inadmissible but executing to a value (`1/0` on AArch64 gives 0).

## 3. The expression language
Grammar (GIN-DEF-060), precedence low → high:

```
expr    := term (('+' | '-') term)*
term    := unary (('*' | '/' | '//' | '%' | 'mod') unary)*
unary   := ('+' | '-') unary-at-30 | power
power   := atom ('^' unary)?            (right-associative; -2^2 = -(2^2))
atom    := NUMBER | 'x' | '(' expr ')' | ('sqrt' | 'gcd') '(' expr (',' expr)* ')'
NUMBER  := decimal integer | decimal fraction | 0b… | …₂ | 0x…
```
Unicode × · ÷ − are accepted as aliases. Exponents are evaluated in exact ℤ regardless of the domain (exponentiation is an action, GIN-NEG-013).

## 4. Domains of evaluation (`ginsdk.expr.DOMAINS`)
Exact: N, Z, Q, R (rational arithmetic plus flagged 40-digit approximations of irrational roots), C (Gaussian rationals), Z/n. Floating point: binary64, binary32, binary16, binary8 (a 1-4-3 teaching format), "JS Number" (= binary64). Languages and ISAs (32-bit): x86-64, AArch64, RISC-V, C, Java, Rust (debug), Go; Python (unbounded int, true division to binary64, exceptions on zero divisors); JS BigInt. Symbolic: rational functions of x over ℚ with definedness conditions.

## 5. Cost accounting conventions in the evaluator
Exact domains report a schoolbook bit-operation *estimate* (max(L_a, L_b) + 1 for ±, L_a·L_b for × and ÷) — a cost model, not a measurement; floating-point and machine domains report one operation per step. The limb-level measurements of GIN-EXP-008 are the authoritative cost data.
