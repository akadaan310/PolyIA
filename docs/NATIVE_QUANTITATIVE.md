# Typed terms and quantitative native witnesses

This increment implements a canonical typed expression surface and partial
normalizer for the existing pure native profile. The executed evidence contains
**10,000 distinct seeded terms** and **three computational machine families with
1,000 inputs each**. All recorded checks passed within that declared scope.
These are three source-template machines on **one ARM64 host**, not three hardware
machines or three separately deployed systems. No mission acceptance is implied.

## Retained source requirements and scope

The complete applicable clauses were read in the original
[UCG commission](../sources/originals/UCG_CODEX_CONSTITUTIONAL_COMMISSION.md):
UCG-084 at lines 457–461 requires a typed term language for numbers, variables,
functions and operators, canonical form, partial normalization, 10,000 random
parser/printer inverse checks and idempotence. UCG-124 at lines 627–631 requires
typed IR, lowering and executable code, interpreted/compiled agreement for three
machines on 1,000 inputs, and compile/run timings. UCG-083–100 and 123–132 retain
the broader common-math and generator requirements; finite witnesses here do not
silently discharge their neighboring clauses.

The [original Poly IA constitution](../sources/recovered/CODEX_CONSTITUTION.md),
including C-017–024, C-057–058, C-064, C-068–070 and C-074–080, supplies native
grammar, declared-observable round trips, execution restraint, independent-role
and quantitative reporting constraints. GOD_SEED PIA-085–096 and
[scientific foundation SF-08](SCIENTIFIC_FOUNDATIONS.md#sf-08-tools-sdks-apis-and-machines-as-packages)
preserve the distinction between executable packages, diagrams, scientific
claims and scoped evidence.

Also read in full: the retained
[PIR grammar](../sources/expanded/POLYIA_FOUNDATION_V0_1/POLYIA_FOUNDATION_V0_1/schemas/POLYIA_PIR_EBNF.md),
[technical treatise](../sources/expanded/POLYIA_FOUNDATION_V0_1/POLYIA_FOUNDATION_V0_1/docs/TECHNICAL_TREATISE.md),
[language/specialist contract](../sources/expanded/POLYIA_FOUNDATION_V0_1/POLYIA_FOUNDATION_V0_1/seed_packets/LANGUAGE_AND_SPECIALISTS.md),
retained metadata compiler, current native implementation, native tests and
[native language documentation](NATIVE_LANGUAGE.md). The PILLAR9 contract describes
its own grammar and binary discipline. This implementation does not claim to
emit P9BC, to run a PILLAR9 backend, or to share Lisp/P9 semantics merely because
its source contains parentheses.

The harness rehashes the two constitutional source pins on every run:

| Source | SHA-256 |
| --- | --- |
| SRC-UCG156 | `0cf03197777e19330ce36cf478bec9a5c4cad5459fd142c37eb4ae0e82bd6d7e` |
| SRC-POLYIA96 | `cfe0b88f9c701e139372d783db1d9568da272f6433f9e513d6475fe7985a2630` |

## Additive term API

`polyia.native` now exposes three pure functions, each returning an `ok` envelope
or a structured refusal. The term profile is **`polyia.term/0.1`**; compiled
programs retain **`polyia.native/0.1`** and **`polyia.typed-stack/0.1`**.

```python
from polyia.native import parse_term, print_term, normalize_term

context = {"x": "Rational"}
parsed = parse_term(" ; original comment\n(add x (mul 06/08 -0/4))", context)
assert parsed["ok"]
assert print_term(parsed["term"], context)["source"] == "(add x (mul 3/4 0))"
normalized = normalize_term(parsed["term"], context)
assert print_term(normalized["term"], context)["source"] == "(add x 0)"
```

`parse_term(source, bindings=None)` accepts one expression with the existing
native operators. Free variables require an explicit name-to-type mapping;
there is no lookup in process state, files or environment variables. Terms have
the same `literal`, `reference` and typed `call` nodes used by compilation, with
source spans omitted from this semantic representation. The original source,
its SHA-256 and the context remain separate fields in the parse envelope.

`print_term(term, bindings=None)` validates the entire tree and returns canonical
source. Reduced rational literals, stable prefix notation, exact Unicode scalar
sequences and the existing quote/backslash/newline escapes define this form.
It re-parses through the actual typechecker and refuses altered types, extra
fields, unknown operations and noncanonical numeric term nodes. Comments,
whitespace and unreduced numeric spelling are not recoverable from the term
alone. Thus the inverse law is `parse(print(term)) == term`, not identity of
arbitrary original source bytes; raw source is retained separately for custody.

`normalize_term(term, bindings=None)` performs bottom-up constant rational
addition/subtraction/multiplication, constant text concatenation, and removal
of trailing literal-zero polynomial coefficients. It reports the actual rewrite
count. Every successful rule removes tree nodes and produces no new reducible
child at that node; this supplies a termination argument for this finite rule
set. No general critical-pair, theorem-prover or arbitrary rewriting-engine claim
is made. For example, `(add x 0)` remains unchanged. Undefined division and empty
replacement patterns are not canceled or hidden by algebraic identities.

The normalizer returns a fresh tree. Its observable preservation claim concerns
typed values where evaluation succeeds under the declared bounds. It does not
promise equal instruction cost, source text, provenance spans, or equivalence
of all resource-exhaustion behavior. The recorded semantic checks use one explicit
substitution: `x=3/7`, `p=1−2x+3x²`, `d=divmod(1+x²,1+x)`, and text `s="xح"`.
They are not a universal quantification over all free-variable assignments.

Bounds include 32 context names of at most 128 characters, the existing 48-form
depth and 4,096-token ceilings, bounded tree traversal and printed source bytes,
512-bit reduced rationals and 16,384-byte text values. Malformed Unicode, cycles,
foreign node structures and growth outside the existing budgets refuse. The
kernel adds no model, network, file, shell, eval or subprocess effects.

## Package compatibility

The typed expression checker was extracted unchanged from compilation so term
parsing and program compilation use the same signatures. No serialized package
field, source span, lowering rule, runtime opcode, source pin, version or digest
algorithm was changed. Three pre-change packages are retained as source/digest
fixtures in [native_packages.json](../tools/fixtures/native_packages.json); all
three compile to the same package identities after the change.

Those fixtures were captured before editing `native.py`, against release 1.3
commit `9ba60201e30ef838fb3079869cf9751b48751b82`, whose native module SHA-256 was
`c4b92f3026edd94db730a765c0b3afb72276298d2bafd0ab577d68e10dc06d21`.
The module bytes necessarily change for the additive API; downstream code-identity
pins must therefore use the new digest while preserving previous release history.

## Quantitative corpus and evidence roles

[check_native_quantitative.py](../tools/check_native_quantitative.py) constructs
10,000 distinct terms with `random.Random(20261024)`, rejection of duplicates,
and bounded recursive generation. There are exactly 2,500 roots of each supported
type: Rational, Polynomial, Division and Text. All 13 current operator names
occur; observed tree depths are 1–5. This is a declared grammar-biased distribution,
not uniform sampling of all mathematical expressions.

Every generated term is printed, parsed and compared structurally, printed again,
normalized twice and compared for idempotence. Each original and normalized term
is compiled and run at the declared substitution to compare typed VM outputs.
The latter is explicitly self-consistency evidence using the same evaluator,
not an independent semantic oracle. The full run changed **3,893 terms** through
**6,567 rewrites** and recorded zero parser, idempotence or value mismatches.

The three machine families are distinct source templates specialized to each
input because the current ABI has closed literal inputs:

| Machine | Input domain | Constructive expectation |
| --- | --- | --- |
| Polynomial division | Integer coefficients embedded in Q[x]; divisor degree 0–4, quotient degree 0–4, degree-bounded remainder | Build dividend as divisor × chosen quotient + chosen remainder, then compare recovered quotient/remainder. |
| Derivative evaluation | Quadratics with rational coefficients and rational evaluation points, including degenerate coefficients | Compare against the separate closed formula `b + 2*a*x`. |
| Literal substitution | Unicode text with exactly two nonoverlapping `::` sites, quotes, escapes, decomposed marks and varied replacement text | Assemble the expected segments directly, without replace or split. |

For each of the 1,000 inputs per family, the real compiler produces typed AST and
bytecode. Fresh compiled packages run through the VM, the separately implemented
AST evaluator, and the public `execute_program` admission/re-execution path.
All outputs must equal the constructive expectation. All 3,000 cases passed,
including repeated-observable comparisons. The two evaluators share the front
end, encoding and Python `Fraction`. Expected values are constructed by this
harness before compilation; they are independently coded calculations, not a
sealed blind external witness or CAS certification.

The harness's direct private evaluator calls exist only to separate timing
phases for freshly compiled admitted input. They introduce no new service route
or way for a caller to bypass package validation. A deliberate corrupted-reference
mutation test makes the report fail for all three machines.

## Measured timings and reproduction

The retained [executed JSON report](evidence/native_quantitative_20261024.json)
records one CPython **3.13.17**, Linux **aarch64** host using
`time.perf_counter_ns`. No warmup phase or CPU governor control was used. The
10,000-term phase took **30.663 seconds** in the retained run. The table gives
median microseconds for each 1,000-input machine family:

| Machine | Compile | VM | AST reference | Public admitted execute |
| --- | ---: | ---: | ---: | ---: |
| Polynomial division | 373.239 | 69.560 | 61.720 | 859.679 |
| Derivative evaluation | 284.080 | 37.440 | 26.680 | 606.959 |
| Literal substitution | 222.280 | 11.280 | 4.320 | 425.160 |

The public path includes package validation, recompilation, VM execution and
reference agreement. It is substantially more expensive than bare evaluation;
the VM is also slower than the AST reference at the measured medians. The JSON
retains totals, min/max and nearest-rank p50/p95/p99 for every phase. These are
local observations, not throughput, isolation, memory, energy or cross-host
performance certification.

```bash
/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -p 'test_native*.py' -q
/opt/polyia/runtime/bin/python3 -B tools/check_native_quantitative.py --output /tmp/native-replay.json
```

The focused suite passes **25 tests**: 13 existing native tests, eight new term
tests and four quantitative-runner tests. Initial new-term testing recorded eight
red tests with 19 failed assertions before the APIs existed; the runner's first
three tests also failed before its file existed. After implementation the suites
passed. Full quantitative runs used the real runtime; no reports were fabricated
from expected counts. The coordinator owns the later consolidated project suite.

The report stores source and implementation hashes, counted operator coverage,
sample programs, observed outputs, corpus/result hashes and failure counters.
Input/result hashes exclude measured time and wall-clock metadata. The term
corpus hash is
`a5a5e8d78df55bb8e6983b627961c6c23159fc290567891981be426984545edc`;
its result hash is
`a724493483d0996a806282ade384cb9a868011810f1eb043ecde676055f15b33`.
Both remained identical across the two full local runs. A reduced run can be
requested with `--terms` and `--inputs-per-machine`; it explicitly leaves
`thresholds_met` false. Any mismatch marks the report FAIL and the CLI exits 1.

## Remaining inherited breadth

This discharges the requested numerical test counts for the explicit finite
native profile. It does not establish all-source mandate completion. General
function declarations and transcendental/algebraic/special-function vocabularies,
general identity rewriting and domain proofs, arbitrary variable substitutions,
full common-math coverage, GUC-card generation/trace equivalence, module/ABI
resolution, dependency specialization, PILLAR9/P9BC and verified WASM/native
backends, external effect sandboxing and independent external proof remain open.
The normalizer preserves many valid expressions unchanged by design. Release,
durable mission evidence admission and acceptance remain separate coordinator
actions; no shared registry or acceptance status was changed here.
