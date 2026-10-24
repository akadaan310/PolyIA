# Research Charter: Grammar in Numbers

**Founding Principal Researcher:** Abed Kadaan
**Parent research program:** Computational Grammar Theory (CGT), `github.com/akadaan310/computationalgrammartheory`
**Research collaborator for this phase:** Claude (AI research assistant)
**Charter date:** 2026-10-08 (session 1)
**Status:** independent research publication, discovery phase. Nothing here is a finished theory.

---

## 1. The question

> **What is the computational grammar of number?**

Grammar in Numbers (GiN) asks whether arithmetic and elementary number theory can themselves be described as computational grammars in the sense of CGT: a structure, a signature of moves, a relational semantics, an admissibility language and an explicit cost model. It does not begin by assuming that `1 + 1 = 2` or `6 / 3 = 2` are primitive notation that needs no structural investigation. It asks, for every arithmetic expression:

1. **Objects.** What are the values, and what are the symbols that name them?
2. **Moves.** What are the admissible operations, and what transitions do they induce?
3. **Admissibility.** When does an expression denote a result, when does it denote nothing, and when does it denote too much?
4. **Representation.** What changes when the same value is written in a different numeral system, stored in a different machine format, or computed by a different circuit?
5. **Cost.** What does each operation cost, in bit operations, under an explicit machine model?
6. **Novelty.** Which findings are new? Which are classical results restated, which are reinterpretations, which are measurements, which are conjectures?

The first target is not "advanced number theory". It is **the grammar of number itself**: 0, 1, 2, 3, 4, … and the operations +, −, ×, /.

## 2. Relationship to CGT

GiN is an *independent* publication. It is not a chapter of the CGT book.

- The CGT repository is a **read-only reference corpus**. GiN may read it, cite it, compare with it and propose extensions to it. GiN never modifies it. (See `PROVENANCE.md` §3 for the boundary and how it was enforced.)
- GiN is independently buildable: it has its own SDK (`sdk/`, package `ginsdk`), experiments, book sources and website build. It imports no CGT code at runtime.
- The relationship of every CGT concept to arithmetic is recorded in `CGT_CONCEPT_MAP.md`: which concepts survive unchanged, which need refinement, which become especially clear, and where arithmetic shows something CGT had not isolated.

## 3. Rules of the work

The CGT discipline is inherited, with additions specific to arithmetic.

- **Order.** Discover, then formalize, then experiment, then prove or falsify. The book and website come last.
- **Ladder of claims.** Every claim has exactly one category from this list:

  | Label | Meaning |
  |---|---|
  | DEFINITION | a precise object; not a discovery |
  | AXIOM | an assumption of a formal system being studied |
  | LEMMA / PROPOSITION / THEOREM / COROLLARY | proved statements (proof given here or cited) |
  | HISTORICAL RESULT | a classical theorem, cited to its source |
  | REINTERPRETATION | a known fact re-expressed in CGT/GiN terms; not a new result |
  | CONJECTURE | believed, not established |
  | EMPIRICAL OBSERVATION | a reproducible measurement; not a proof |
  | IMPLEMENTATION RESULT | a property of code written here (e.g. "the simulator agrees with hardware on N cases") |
  | COUNTEREXAMPLE | an instance where a proposed claim fails |
  | OPEN PROBLEM | a precisely stated unanswered question |

  Nothing is silently promoted. A visualization is not a proof. A benchmark is not a theorem. A new notation is not a new theory. A reinterpretation is not a new result. An implementation is not an algorithmic improvement.
- **Bit complexity is mandatory.** Unit-cost arithmetic ("one addition costs 1") is used only when the operand size is bounded and the bound is stated. Otherwise costs are in bit operations or in w-bit word operations on a stated machine model (`FORMAL_MODELS.md` §1).
- **Number, numeral, encoding and machine state are kept apart** (`DEFINITIONS.md` GIN-DEF-001…004). Any claim that crosses layers says so.
- **"The machine" is never universal.** Every claim about machine behaviour names the ISA, the language, the compiler and the version, and says whether it was *measured on this host* or *taken from a specification* (`MACHINE_MODEL.md`).
- **"Undefined" is never the end of an analysis.** For every inadmissible expression the ledger states *which* condition fails (no solution, more than one solution, outside the domain, outside the representable range) and what would have to change for it to have a value.
- **Counterexamples are first-class results** (`COUNTEREXAMPLES.md`).
- **No priority claims without literature review.** Most of arithmetic is millennia old. The default assumption for any fact here is that it is known. Novelty is claimed only for precisely isolated statements, and even then marked "novelty unverified" until checked (`LITERATURE_REVIEW.md`, `PROVENANCE.md`).
- **Self-containment and reproducibility.** The SDK and experiments use the Python standard library only. Machine experiments that run compiled C, Java, Rust or JavaScript record the exact toolchain. Every experiment is deterministic given its seed.
- **History is preserved.** Rejected hypotheses stay in the ledger. Revisions go in `DECISION_LOG.md`.

## 4. Identifier convention

`GIN-DEF-nnn` definition · `GIN-AX-nnn` axiom system · `GIN-H-nnn` hypothesis · `GIN-CONJ-nnn` conjecture · `GIN-LEM/PROP/THM/COR-nnn` proved statements · `GIN-HIST-nnn` historical result · `GIN-REI-nnn` reinterpretation · `GIN-OBS-nnn` empirical observation · `GIN-IMP-nnn` implementation result · `GIN-EXP-nnn` experiment · `GIN-NEG-nnn` counterexample · `GIN-REJ-nnn` rejected hypothesis · `GIN-OPEN-nnn` open problem · `GIN-D-nnn` decision. CGT identifiers (`CGT-…`) always refer to the parent corpus.

## 5. Workspace

| Path | Purpose |
|---|---|
| `README.md` | entry point and summary of findings |
| `RESEARCH_CHARTER.md` | this document |
| `PROVENANCE.md` | contributors, origin of every result, the CGT read-only boundary |
| `CGT_CONCEPT_MAP.md` | how each CGT concept behaves on numbers |
| `DEFINITIONS.md` | GIN-DEF-xxx |
| `NUMBER_GRAMMAR.md` | the grammar of 0, 1, 2, 3, …: successor, numerals, addresses |
| `ARITHMETIC_GRAMMAR.md` | +, −, ×, / as transitions; converse problems; admissibility |
| `FORMAL_MODELS.md` | cost models, the four layers, the expression language |
| `MACHINE_MODEL.md` | ISA/language semantics, measured and specified |
| `NUMBER_THEORY.md` | divisibility, Euclid, congruences, primes as transition systems |
| `HYPOTHESES.md` | GIN-H-xxx with status |
| `EXPERIMENTS.md` | protocols GIN-EXP-xxx |
| `RESULTS.md` | propositions, theorems, observations, with proofs |
| `COUNTEREXAMPLES.md` | GIN-NEG-xxx, rejected hypotheses |
| `LITERATURE_REVIEW.md` | prior work by area |
| `OPEN_PROBLEMS.md` | GIN-OPEN-xxx |
| `BOOK_OUTLINE.md` | the book's architecture, revised from the evidence |
| `DECISION_LOG.md` | dated decisions |
| `sdk/` | `ginsdk`, the executable companion (Python ≥ 3.10, stdlib only) with tests |
| `experiments/` | reproducible experiments, raw JSON, `results/SUMMARY.md` |
| `book/` | book sources (`book/content`), build tools, website assets, tests |

## 6. Exit criteria for a first edition

1. The definitions of the four layers and of converse admissibility are stable across a second round of experiments.
2. Every "Proved here" statement is checked exhaustively on small cases by code in `experiments/check_theorems.py`.
3. Every machine claim is either measured on a recorded toolchain or cited to a specification.
4. The frontier assessment (`RESULTS.md` §F) honestly states what, if anything, is new.
