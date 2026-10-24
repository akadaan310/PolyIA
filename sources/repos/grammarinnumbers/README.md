# Grammar in Numbers

**Arithmetic, Number Theory, and the Computational Grammar of Number**

Founding Principal Researcher: **Abed Kadaan**. Parent research program: [Computational Grammar Theory](https://github.com/akadaan310/computationalgrammartheory) (CGT), used here as a read-only reference corpus.

An independent research publication that asks: *what is the computational grammar of number?* It does not treat `1 + 1 = 2` or `6 / 3 = 2` as primitive notation. For every expression it asks what the objects, symbols, states, admissible operations and transitions are, what is preserved, what it costs in bit operations, what machinery implements it, and — when an expression asks for a transition the grammar does not admit — exactly *which* condition fails.

## Findings of session 1 in brief

- **Numerals are programs.** A positional numeral is a word of moves x ↦ b·x + d applied to 0; its value is its denotation (CGT syntax vs semantics). The canonical numeral is a CGT grammatical address, and **zero's address is the empty word** (GIN-PROP-002). CGT's heap numeration of binary trees **is bijective binary shifted by one** (GIN-PROP-006). Positional notation is grammar compression of the unary successor term, with the same shape as square-and-multiply exponentiation (GIN-PROP-007).
- **Inverse operations are converses, and "undefined" has two kinds.** In any commutative ring the solutions of b·c = a are empty or a coset of Ann(b) (GIN-THM-001). So **1/0 is an image failure** (no c with 0·c = 1) and **0/0 is a kernel failure** (every c satisfies 0·c = 0), while **0/1 = 0** passes both tests. The same classification covers 0 − 1 in ℕ, 7/2 in ℤ, √−1 in ℝ, 2/4 in ℤ/6, modular inverses and the CRT.
- **Every way of giving 1/0 a value gives something up** (GIN-THM-003/004): the ring laws (projective line, wheels, extended reals), the converse reading of division (IEEE ∞, meadows, Lean's mathlib, AArch64 returning 0, RISC-V returning −1), or 0 ≠ 1. In fractions-as-pairs, **all indeterminate forms (0/0, 0·∞, ∞ ± ∞, ∞/∞) compute the single null pair (0, 0)**, which is exactly the pair that cannot be admitted without destroying the equivalence (GIN-THM-006).
- **Machines disagree, measurably.** On one x86-64 host, `1/0` traps, raises, panics, returns ∞, or is rejected at compile time depending on the language; clang deletes a zero test after a division while gcc keeps it; Python raises on `1.0/0.0` where IEEE says ∞ (GIN-EXP-004). A reference IEEE 754 simulator matches the CPU **bit for bit and flag for flag** on 80,600 cases, and shows the host detects tininess after rounding (GIN-EXP-005).
- **A divider that never tests its divisor returns all ones** on division by zero — exactly the RISC-V choice (GIN-PROP-023).
- **Addition is finite-state; multiplication is not** (GIN-THM-005, classical): the carry automaton's three-element monoid {kill, propagate, generate} is what carry-lookahead adders compute in parallel.
- **What is new?** Honestly: a framework and a set of cross-validated artefacts, not new theorems. Every proved statement is classical or elementary; the closest candidates for unrecorded statements (GIN-PROP-006, the pair-level form of GIN-THM-006) are probably folklore. See `RESULTS.md` §G.

## Navigate
`RESEARCH_CHARTER.md` · `PROVENANCE.md` · `CGT_CONCEPT_MAP.md` · `DEFINITIONS.md` · `NUMBER_GRAMMAR.md` · `ARITHMETIC_GRAMMAR.md` · `FORMAL_MODELS.md` · `MACHINE_MODEL.md` · `NUMBER_THEORY.md` · `HYPOTHESES.md` · `EXPERIMENTS.md` · `RESULTS.md` · `COUNTEREXAMPLES.md` · `LITERATURE_REVIEW.md` · `OPEN_PROBLEMS.md` · `BOOK_OUTLINE.md` · `DECISION_LOG.md`

## Reproduce
```sh
# SDK (Python ≥ 3.10, standard library only)
cd sdk && PYTHONPATH=src python3 -m unittest discover -s tests

# All experiments, theorem checks and the summary (≈ 1.5 min; EXP-004/005 need gcc, optionally clang, java, rustc, go, node)
sh experiments/run_all.sh && cat experiments/results/SUMMARY.md
python3 experiments/verify_reproduction.py      # re-run and compare counted fields

# The book and website (Node ≥ 18)
cd book && npm install && npm run verify         # build + JS tests + executed examples + link check
npm run serve                                    # http://localhost:8080
```

## Layout
`sdk/` the `ginsdk` package and tests · `experiments/` scripts, machine sources, JSON results · `book/content/` chapters, glossary, bibliography · `book/tools/` build, checks · `book/site/` styles and the laboratory's JavaScript · `book/tests/` lab-vs-SDK fixture tests.
