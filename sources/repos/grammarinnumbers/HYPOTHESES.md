# Hypothesis Ledger

Status values: **open**, **supported** (evidence agrees, no counterevidence, not proved), **established** (proved or exhaustively verified within a stated scope; see the result), **partly supported**, **rejected**, **reformulated** (superseded by a sharper statement).

### GIN-H-000 The founding question *(A. Kadaan)*
- **Statement.** Arithmetic and elementary number theory can be described as computational grammars: objects, symbols, states, admissible operations, transitions, invariants, information requirements and machinery, such that "undefined" expressions are explained by which grammatical condition fails.
- **Status.** **Reformulated** into H-001 … H-035. The descriptive half is supported throughout: every operation studied has a CGT operational grammar, and every failure studied is classified by layer and cause (GIN-DEF-061, GIN-THM-001, GIN-THM-004). Whether the description yields new *mathematics* is answered "not so far" (RESULTS §G).

| ID | Statement (short) | Test | Status | Evidence |
|---|---|---|---|---|
| GIN-H-001 | The value map on standard numerals is surjective and non-injective exactly by leading zeros. | EXP-001 | **established** | PROP-001 |
| GIN-H-002 | Zero's canonical numeral is the empty word. | EXP-001 | **established** | PROP-002 |
| GIN-H-003 | Bijective notation removes all non-injectivity. | EXP-001 | **established** | PROP-004 |
| GIN-H-004 | The CGT heap grammar is bijective binary, shifted by one. | EXP-001 | **established** | PROP-006 |
| GIN-H-005 | Unary (Peano) arithmetic costs time linear in the values, i.e. exponential in binary length. | EXP-001 | **established** | PROP-003, OBS-001 |
| GIN-H-006 | Counting 0 → N flips exactly 2N − popcount(N) bits. | EXP-002 | **established** | PROP-010 |
| GIN-H-007 | The mean longest carry chain is log₂ n + O(1). | EXP-002 | **supported** (measured n ≤ 4096; known in the literature) | OBS-002 |
| GIN-H-008 | Division failures split into exactly two kinds, and in a commutative ring the solution set of b·c = a is empty or a coset of Ann(b). | EXP-003 | **established** | THM-001 |
| GIN-H-009 | In ℤ/n the share of pairs with a unique quotient is φ(n)/n. | EXP-003 | **established** | THM-002 |
| GIN-H-010 | The same expression fails at different layers in different domains. | EXP-003, EXP-004 | **supported** | OBS-003, OBS-004 |
| GIN-H-011 | "Division by zero" is not one behaviour on real systems. | EXP-004 | **supported** (seven toolchains, one host) | OBS-004…006 |
| GIN-H-012 | The SDK's machine models agree with every measurable behaviour on the host. | EXP-004 | **supported** (14/14) | IMP-002 |
| GIN-H-013 | Instruction selection maps `/` to different instructions per ISA and type. | EXP-004 | **supported** | OBS-007 |
| GIN-H-014 | Exact rational evaluation + one RNE rounding reproduces hardware results bit for bit. | EXP-005 | **supported** (80,600 cases) | IMP-001 |
| GIN-H-015 | …and reproduces all five flags when tininess is detected as on the host. | EXP-005 | **supported after correction** (signaling NaNs had to be modelled) | IMP-001, REJ-002 |
| GIN-H-016 | Ripple: 5n − 3 gates, depth 2n − 1; prefix adders: more gates, logarithmic depth. | EXP-006 | **established** (ripple), **supported** (prefix: measured n ≤ 256) | PROP-021, OBS in SUMMARY |
| GIN-H-017 | All four adders are correct. | EXP-006 | **established** n ≤ 8, supported to n = 64 | IMP-003 |
| GIN-H-018 | A restoring divider without a divisor test outputs (2ⁿ − 1, dividend) on a zero divisor = RISC-V DIVU/REMU. | EXP-007 | **established** | PROP-023 |
| GIN-H-019 | Array multiplier and divider sizes grow quadratically. | EXP-007 | **supported** (n ≤ 32) | SUMMARY |
| GIN-H-020 | Counted word operations: linear (+, −, cmp), quadratic (schoolbook ×, ÷, gcd), n^1.585 (Karatsuba), cubic (modexp). | EXP-008 | **supported** | OBS-010 |
| GIN-H-021 | CPython int timings show the same ordering. | EXP-008 | **supported** (secondary evidence only) | exp008.json |
| GIN-H-022 | Lamé: smallest pair with k steps is (F_{k+2}, F_{k+1}). | EXP-009 | **established** (classical; checked) | PROP-040 |
| GIN-H-023 | Average steps follow (12 ln 2/π²) ln n + Porter's constant. | EXP-009 | **supported** with a convention offset of exactly 1 | OBS-011 |
| GIN-H-024 | Extended-Euclid coefficients are bounded by b/(2g), a/(2g). | EXP-009 | **supported** (20,000 samples) | exp009.json |
| GIN-H-025 | Published pseudoprime counts below 10⁶ (245 / 46 / 43). | EXP-010 | **supported** (reproduced exactly) | PROP-043 |
| GIN-H-026 | Deterministic Miller–Rabin agrees with the sieve up to 10⁶. | EXP-010 | **supported** | PROP-043 |
| GIN-H-027 | Sieve ~ n ln ln n crossings; trial division ~ √n/2 divisions for primes. | EXP-010 | **supported** (sieve ratio 0.81 at 10⁶ — the lower-order terms are not negligible there) | exp010.json |
| GIN-H-028 | Pollard rho ~ √p steps. | EXP-010 | **supported** | OBS-012 |
| GIN-H-029 | Horner and balanced numeral evaluation use the same compositions; depth k vs ⌈log₂ k⌉. | EXP-011 | **established** | PROP-005 |
| GIN-H-030 | Shape alone gains no bit-cost exponent; it pays asymptotically only with a subquadratic multiplication. | EXP-011 | **supported** (and refined: shape alone gives a constant factor ≈ 6.7 at 8,192 digits) | OBS-013, REJ-003 |
| GIN-H-031 | Least unrepresentable positive integer is 2ᵖ + 1. | EXP-012 | **established** | PROP-030 |
| GIN-H-032 | Exactly 2ᵏ − 1 of the k-digit decimals are binary-representable. | EXP-012 | **established** | PROP-031 |
| GIN-H-033 | Float + is commutative but not associative. | EXP-012 | **established** | PROP-032 |
| GIN-H-034 | Summation order changes the computed harmonic sum. | EXP-012 | **supported** | OBS-015 |
| GIN-H-035 | MAX + 1 gives MIN under wraparound for every width. | EXP-012 | **established** (definition of wraparound) | exp012.json |
| GIN-H-036 | Every indeterminate form of projective arithmetic on pairs is the null pair (0, 0), the unique pair that cannot be an element. | check_theorems | **established** | THM-006 |
| GIN-H-037 | Optimizing compilers delete a zero test that follows a division by the tested variable. | EXP-004 | **partly supported**: clang 18 does, gcc 13.3 does not | OBS-008, NEG-004 |
