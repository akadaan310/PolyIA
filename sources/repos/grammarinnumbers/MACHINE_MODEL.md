# Machine Models: how a mathematical grammar becomes an executable one

"The machine" is not one thing. Every row below names its source: **[M]** measured on the session host (x86-64, Linux 6.18; toolchains in `EXPERIMENTS.md`), **[S]** taken from a specification (not executed). Data: `experiments/results/exp004.json`, `exp005.json`.

## 1. From `x / y` to an instruction
1. **Lexical analysis**: `x`, `/`, `y` become identifier, operator, identifier tokens.
2. **Parsing**: a tree BinOp(Name x, Div, Name y) — CPython's AST is exactly this [M].
3. **Typing**: the operand types select the operation: int / int (truncating integer division in C, Java, Go, Rust; true division to float in Python 3), double / double, BigInt / BigInt.
4. **Intermediate representation and lowering**: CPython compiles to `LOAD_NAME x; LOAD_NAME y; BINARY_OP /` [M]; C compilers lower to `sdiv`/`fdiv` IR operations.
5. **Instruction selection** (clang 18 -O2) [M, compile only for non-x86]:

| type | x86-64 | AArch64 | RISC-V 64 |
|---|---|---|---|
| int | `cltd; idivl` | `sdiv` | `divw` |
| unsigned | `xorl; divl` | `udiv` | `divuw` |
| double | `divsd` | `fdiv` | `fdiv.d` |

6. **Execution**: the instruction's semantics on the operands (below), including traps and flags.

## 2. Integer division at its two boundaries

| model | x / 0 | INT_MIN / −1 | source |
|---|---|---|---|
| x86-64 `idiv` | #DE trap → SIGFPE | #DE trap → SIGFPE | [S] Intel SDM; [M] via C |
| AArch64 `sdiv` | 0, no signal | INT_MIN | [S] Arm ARM (secondary sources) |
| RISC-V `div` / `divu` | −1 / 2ʷ − 1; rem = dividend | INT_MIN; rem 0 | [S] RISC-V ISA, M extension |
| ISO C | undefined behaviour | undefined behaviour | [S] C17 §6.5.5; [M] gcc: SIGFPE on x86 |
| Java | ArithmeticException | INT_MIN (no exception) | [S] JLS §15.17.2; [M] |
| Rust (debug and release) | panic "attempt to divide by zero" | panic "attempt to divide with overflow" | [S] Rust reference; [M] |
| Rust `checked_div` | None | None | [M] |
| Go | run-time panic "integer divide by zero" | INT_MIN (no panic) | [S] Go spec; [M] |
| Python `//` | ZeroDivisionError | 2³¹ (unbounded ints) | [S] Python reference; [M] |
| JS BigInt | RangeError | 2³¹ | [S] ECMA-262; [M] |
| constant `1/0` at compile time | Go: compile error; Rust: compile error (deny lint); C: warning, then SIGFPE at run time; Java: compiles, ArithmeticException at run time | | [M] |

**Rounding of integer quotients.** Truncation toward zero (x86, C, Java, Go, Rust, JS BigInt: −7/2 = −3) vs floor (Python: −7//2 = −4) [M]. Mathematically both are *selections* from the solutions of a = qb + r with different remainder conditions.

**Optimization under undefined behaviour** [M]: for `int q = a / b; if (b == 0) return -1; return q;`, clang 18 -O2/-O3 compiles to `idiv; ret` (test deleted); gcc 13.3 -O2 keeps `test; cmove`. Both are conforming: the test is unreachable in every execution with defined behaviour.

## 3. Floating point (IEEE 754 binary64) [M] on x86-64 SSE, flags via fenv.h

| operation | result | flags |
|---|---|---|
| 1 / 0 | inf | divideByZero |
| −1 / 0, 1 / −0 | −inf | divideByZero |
| 0 / 0 | NaN (printed `-nan`: the x86 default NaN has its sign bit set) | invalid |
| 0 / 1 | 0 | none |
| 1 / 3 | 0.333… | inexact |
| 1e308 / 1e−10 | inf | overflow, inexact |
| 1e−310 / 1e10 | 9.99989e−321 (subnormal) | underflow, inexact |
| √−1 | NaN | invalid |

Language layers on top: Java, Go, Rust, JavaScript and C return these data; **Python raises ZeroDivisionError for 1.0/0.0** [M]. Tininess is detected after rounding on this host [M, GIN-OBS-009]. The reference simulator `ginsdk.ieee` matches results and flags on 80,600 cases [M, GIN-IMP-001].

## 4. Fixed-width addition overflow
| policy | 2147483647 + 1 (int32) | where |
|---|---|---|
| wrap | −2147483648 | hardware add on all three ISAs; Java; Go; Rust release |
| saturate | 2147483647 | DSP and SIMD saturating instructions |
| trap/exception | panic | Rust debug; checked arithmetic |
| undefined | — | ISO C signed overflow |

## 5. Arbitrary precision
CPython `int`: unbounded; cost grows with operand length (GIN-EXP-008 secondary timings); int ↔ decimal string conversion capped at 4,300 digits by default since 3.11 (GIN-OBS-014). `ginsdk.bigint` makes the limb-level cost explicit.

## 6. Universal claims GiN does not make
GiN does not claim that any behaviour above holds on other hosts, other compiler versions or other flags, except where a specification is cited. AArch64 and RISC-V results are specification-level only (GIN-OPEN-009).
