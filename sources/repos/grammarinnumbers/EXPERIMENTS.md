# Experiments

**Code:** `experiments/` (git history is the version record). **Reproduce:** `sh experiments/run_all.sh` (≈ 1.5 minutes; writes `experiments/results/*.json` and `results/SUMMARY.md`). **Determinism:** fixed seeds; `python3 experiments/verify_reproduction.py` re-runs everything and reports identical counted fields (last run: identical in all files). **Environment of the recorded runs:** CPython 3.13.16, Linux 6.18 x86_64, Intel Xeon @ 2.80 GHz; gcc 13.3.0, clang 18.1.3, OpenJDK 21.0.12.1, rustc 1.97.0, go 1.24.7, Node.js 22.22.0 (recorded per file in `environment`).
**Cost methodology:** primary dependent variables are counted steps under the cost model stated in each script's docstring (rule applications, bit flips, gates and depth, 32-bit limb operations, division steps). Wall-clock time is secondary and appears only in fields ending in `_s`.
**Theorem checks:** `experiments/check_theorems.py` checks the exact statement of every "proved here" result on small cases (21 checks, all passing). They guard against mis-statement; they are not proofs.
**What is measured vs specified:** machine experiments (EXP-004, EXP-005) run on the host. AArch64 and RISC-V behaviour is *not* measured (no such hardware or emulator was available); those models are specification models and are labelled as such.

---

## GIN-EXP-001 Numerals and the successor grammar (`exp001_numerals.py`)
- **Hypotheses.** H-001 … H-005.
- **Design.** (1) For bases 2, 3, 10, enumerate all words up to length L and count those denoting n < 30. (2) For bijective bases 1, 2, 3, 10, enumerate all words up to a length bound and check that values are distinct and form an initial segment. (3) Heap conjugacy for n < 200,000. (4) Two's complement vs 2-adic truncation for widths 4, 8, 16. (5) Peano rule counts vs binary bit operations for n = 2ᵏ − 1, k ≤ 20.
- **Falsification.** Any count off the formula L − |addr(n)| + 1; any collision in a bijective system; any heap mismatch.
- **Result.** All formulas hold; 0 collisions; 0 mismatches (PROP-001…006, 008; OBS-001).

## GIN-EXP-002 Increment and carries (`exp002_increment_carries.py`)
- **Hypotheses.** H-006, H-007. **Seed** 20261008.
- **Design.** Exact flips for every increment up to 2¹⁷; longest carry chain over 3,000 (n ≤ 1024) or 1,000 random pairs for n = 4 … 4096; K/P/G frequencies.
- **Result.** Flip formula exact; chains log₂ n − 0.66 … 0.84 (OBS-002); K, P, G ≈ 1/4, 1/2, 1/4.
- **Limitation.** The constant offset depends on the definition of chain length; GiN counts the generating position plus the propagating positions it travels through.

## GIN-EXP-003 Converse admissibility census (`exp003_converse_census.py`)
- **Hypotheses.** H-008 … H-010. Exhaustive; no randomness.
- **Design.** All (a, b) in ℤ/n for n ≤ 64; the meaning table of 14 expressions × 15 domains via `ginsdk.expr`; the x/0, 0/x, x/x families exactly and symbolically; 1/x in binary64 as x → 0±; other converse problems (√, log, modular inverse).
- **Result.** 0 coset violations; unique share = φ(n)/n; the meaning table (SUMMARY); OBS-003, OBS-016.

## GIN-EXP-004 Machine division on this host (`exp004_machine_division.py`, sources in `experiments/machine/`)
- **Hypotheses.** H-011 … H-013, H-037.
- **Design.** C compiled with gcc -O0 and -O2 (operands from argv to prevent constant folding): int x/0, 0/0, INT_MIN/−1, −7/2; double x/0, 0/0, signed zero, overflow, underflow, √−1, with fenv flags. Post-division zero test compiled by gcc -O0/-O2 and clang -O2/-O3, assembly inspected. Constant `1/0` in C, Go, Rust, Java (compile and run). Java, Rust (debug and release; `/`, `checked_div`, `wrapping_div`), Go, JavaScript (Number and BigInt), Python (in process; AST and bytecode of `x / y`). Instruction selection with clang -O2 for x86_64, aarch64 and riscv64 targets (compile only).
- **Result.** OBS-004…008; model agreement 14/14 (IMP-002).
- **Limitation.** One host; one version per toolchain; AArch64/RISC-V not executed.

## GIN-EXP-005 IEEE simulator vs hardware (`exp005_ieee_validation.py`, oracle `machine/fpharness.c`)
- **Hypotheses.** H-014, H-015. **Seed** 754.
- **Design.** For binary32 and binary64: 40,000 cases over +, −, ×, ÷, √ (random bit patterns; special and boundary values; nearby exponents; subnormal territory) plus 300 targeted products whose exact value lies in (λ(1 − 2⁻ᵖ), λ), λ = smallest normal — the only region where before- and after-rounding tininess differ. Compare results (NaN-ness only for NaNs) and the five flags, under both tininess models.
- **Result.** 0 result mismatches; 0 flag mismatches with after-rounding tininess (after modelling signaling NaNs); 158/159 mismatches with before-rounding, all in the targeted family (IMP-001, OBS-009).
- **History.** The first run showed 92 (binary32) + 9 (binary64) flag mismatches, all signaling-NaN operands (REJ-002); fixed in `ginsdk.ieee`, then re-run.

## GIN-EXP-006 Adder circuits (`exp006_adder_circuits.py`)
- **Hypotheses.** H-016, H-017. **Seed** 6.
- **Design.** Ripple-carry, Sklansky, Kogge–Stone, Brent–Kung; exhaustive n ≤ 8 (65,536 pairs at n = 8), 300 random pairs for n = 16, 32, 64; gates and depth for n = 1 … 256; carry monoid table; NAND-only full adder.
- **Result.** 0 errors; ripple 5n − 3 / 2n − 1; at n = 256: Sklansky 3,584 / 18, Kogge–Stone 5,891 / 17, Brent–Kung 2,018 / 30, ripple 1,277 / 511.

## GIN-EXP-007 Multiplier and divider circuits (`exp007_mul_div_circuits.py`)
- **Hypotheses.** H-018, H-019.
- **Design.** Array multiplier and restoring divider, exhaustive n ≤ 6; zero-divisor outputs compared with the RISC-V DIVU/REMU and AArch64 UDIV models; sizes for n ≤ 32.
- **Result.** 0 errors; zero divisor gives (2ⁿ − 1, a) = RISC-V for all n ≤ 6 (PROP-023).

## GIN-EXP-008 Bit complexity (`exp008_bit_complexity.py`)
- **Hypotheses.** H-020, H-021. **Seed** 8.
- **Design.** Random L-bit operands, L = 64 … 16,384 (gcd to 4,096, modexp to 512): counted limb operations of `ginsdk.bigint`; CPython timings as secondary data; log–log slopes between successive sizes.
- **Result.** OBS-010.

## GIN-EXP-009 Euclid (`exp009_euclid.py`)
- **Hypotheses.** H-022 … H-024. **Seed** 9.
- **Design.** All pairs below 1,200 (smallest pair per step count, histogram); average steps for primes n = 1009 … 1,000,003; Bézout coefficient bounds on 20,000 random pairs; binary vs Euclidean gcd on 5,000 random 64-bit pairs.
- **Result.** Lamé pairs match; OBS-011; 0 bound violations; binary gcd ≈ 45.2 subtractions vs Euclid ≈ 37.8 divisions (each subtraction is cheaper).

## GIN-EXP-010 Primes (`exp010_primes.py`)
- **Hypotheses.** H-025 … H-028. **Seed** 10.
- **Design.** Sieve to 10⁶ with crossing count; Fermat base-2 and strong base-2 pseudoprimes and Carmichael numbers below 10⁶; deterministic Miller–Rabin vs sieve; trial-division counts for primes of 11 … 31 bits; Pollard rho on p·q with p of 10 … 26 bits.
- **Result.** 245 / 46 / 43 (published values); 0 disagreements; OBS-012.

## GIN-EXP-011 Numeral evaluation shapes (`exp011_numeral_shapes.py`)
- **Hypotheses.** H-029, H-030. **Seed** 11.
- **Design.** Decimal numerals of k = 64 … 8,192 digits converted to binary limbs by Horner, balanced composition with schoolbook multiplication, and balanced composition with Karatsuba; counted limb operations; compositions and depth.
- **Result.** OBS-013, OBS-014.

## GIN-EXP-012 Representation boundaries (`exp012_representation_boundaries.py`)
- **Hypotheses.** H-031 … H-035.
- **Design.** Least unrepresentable integer by search (full search for p = 4, 11; windows for p = 24, 53); exactly representable k-digit decimals, k ≤ 4; associativity over all tenth-triples; harmonic sum H₂₀₀₀₀ in binary32 in both orders; MAX + 1 for widths 8 … 64 under each overflow policy.
- **Result.** PROP-030, PROP-031, PROP-032, OBS-015.
