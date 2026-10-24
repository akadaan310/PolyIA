# Provenance Record

## 1. Originator

**Abed Kadaan** is the Founding Principal Researcher of Grammar in Numbers (GiN). He formulated the research question ("What is the computational grammar of number?"), its relationship to Computational Grammar Theory, the central experimental narrative

  0 → 1 → 2 → 3 → 4, then 1 + 1 → 2, 2 + 2 → 4, 0 / 1 → 0, 1 / 0 → ?, 0 / 0 → ?

the proposal to read `1 / 0` and `0 / 0` as two *different* grammatical failures (no candidate versus too many candidates), the segment notation `0{1,2,3}4` as an object of investigation, the requirement that number, numeral, digit, machine word and abstract value be distinguished, and the governance rules of this publication (ladder of claims, read-only CGT boundary, honesty about novelty).

Kadaan is also the originator of the parent program, Computational Grammar Theory (CGT); see the CGT repository's `PROVENANCE.md`.

## 2. Contributors in this phase

- **Abed Kadaan**: research program, research mandate, the questions listed above, governance rules.
- **Claude (AI research assistant, session 1, 2026-10-08)**: workspace, definitions GIN-DEF-xxx, hypotheses GIN-H-xxx, the `ginsdk` SDK, all experiment code, proofs written in `RESULTS.md`, literature baseline, book text and website. All of it is subject to review; nothing has been externally reviewed.

## 3. The CGT boundary (read-only)

The CGT repository (`akadaan310/computationalgrammartheory`, branch `claude/happy-newton-r2t17c`, head `b3a29f3` at the time of reading) was **read, never modified**.

- What was read: all ledger files (`DEFINITIONS.md`, `FORMAL_MODELS.md`, `RESULTS.md`, `HYPOTHESES.md`, `COUNTEREXAMPLES.md`, `OPEN_PROBLEMS.md`, `PROVENANCE.md`, `DECISION_LOG.md`, `BOOK_OUTLINE.md`, `PUBLICATION_AUDIT.md`, `EXPERIMENTS.md`), the book sources' structure, the book build tool `book/tools/build.mjs`, its example checker, its stylesheet and its JavaScript.
- What was reused, and how: GiN's book build (`book/tools/build.mjs`) and example checker follow the *design* of CGT's (Markdown + KaTeX at build time, environments with status badges, build-time integrity checks). The GiN files were written for this repository and are adapted to its content; there is no runtime or build-time dependency on the CGT repository. The visual identity deliberately shares CGT's typography and paper palette and changes the accent colour, so that the two publications read as one family.
- What was *not* reused: no CGT code is imported by `ginsdk` or by any experiment. Where a GiN result concerns a CGT object (for example the heap numeration of CGT-DEF-006), GiN re-implements it independently (`ginsdk.numerals.heap_word`).
- Verification: `git status` in the CGT checkout was clean at the end of the session (`DECISION_LOG.md`, GIN-D-002).

CGT identifiers cited in GiN (CGT-DEF-006, CGT-THM-003, CGT-THM-004, CGT-THM-006, CGT-DEF-011, CGT-PROP-002, …) refer to the CGT ledger at the commit above.

## 4. Classification of every result

"Proved here" means a proof is written in `RESULTS.md` by the session-1 collaborator and checked exhaustively on small cases by `experiments/check_theorems.py`; it does **not** mean the statement is new. Almost everything in arithmetic is old.

| ID | Category | Origin | Relationship to prior work |
|---|---|---|---|
| GIN-DEF-001…004 (four layers) | definition | this investigation, from **Kadaan's** mandate | standard distinctions (number/numeral; value/representation) made explicit as layers |
| GIN-DEF-005…008 digit grammars, canonical numerals | definition | this investigation | positional notation is classical; the CGT packaging (moves, address, transition monoid) is new framing |
| GIN-DEF-012 segment notation `a{I}b` | definition | **Kadaan's** proposal, formalized here | equivalent to a marked interval; no new mathematics (see RESULTS §B) |
| GIN-DEF-015…017 converse problem, admissibility, repairs | definition | this investigation | relational converse is standard; the classification vocabulary is GiN's |
| GIN-PROP-001…005, 008, 009 | proposition | classical facts, proofs written here | positional numeration (Knuth TAOCP vol. 2 §4.1); bijective numeration (Smullyan 1961; Foster 1947 [U]) |
| GIN-PROP-006 heap conjugacy | proposition | proved here | elementary; very likely folklore; novelty unverified |
| GIN-PROP-010 increment flips 2N − popcount(N) | proposition | proved here | the amortized binary counter is textbook (CLRS §17); the exact closed form is elementary and almost certainly known |
| GIN-THM-001…003 converse structure in rings | theorem | standard algebra, proofs written here | elementary ring theory |
| GIN-THM-004 extension trilemma | reinterpretation | this investigation | synthesizes cited facts about extended reals, projective line, IEEE 754, meadows, wheels |
| GIN-THM-005 addition finite-state, multiplication not | theorem | **known** (Büchi; Hodgson; Khoussainov & Nerode; Blumensath & Grädel; Gödel/Church) | restated as a grammar-class boundary |
| GIN-PROP-020 carry monoid | proposition | known in substance (Brent & Kung 1982; Ladner & Fischer 1980) | restated as CGT arithmetic compilation |
| GIN-PROP-021 ripple counts | proposition | proved here | elementary, for the specific construction |
| GIN-PROP-023 restoring divider on 0 | proposition | proved here | the RISC-V specification's own rationale already says all-ones is "the natural value" for simple dividers; GiN supplies a proof and gate-level check, not a new fact |
| GIN-PROP-030, 031 representability | proposition | proved here | elementary and well known |
| GIN-PROP-040…043 number theory | historical / proposition | classical (Euclid; Lamé 1844; Bézout; Sunzi/CRT; Fermat; Korselt 1899; Miller 1976; Rabin 1980) | restated as transition systems |
| GIN-HIST-001 Brahmagupta's zero rules | historical result | Brahmagupta 628 CE, via secondary sources | GiN's reading of 0/0 = 0 as a *selection* (a totalization), not an error of derivation, is an interpretation |
| GIN-OBS-xxx | empirical | experiments here | n/a |
| GIN-IMP-001 IEEE simulator agrees with hardware | implementation result | experiments here | the method (exact rational then one rounding) is the standard's own definition |
| GIN-NEG-xxx | counterexamples | experiments and analysis here | several are well known (float non-associativity, pseudoprimes) |

## 5. Priority statement

No claim of historical priority is made for any mathematical result in this repository. The candidate contributions of session 1 are: (i) a **framing** of arithmetic as CGT operational grammars with an explicit four-layer outcome model (syntax · typing · semantics · execution); (ii) the **converse-admissibility** reading of inverse operations, which classifies `1 / 0` (no solution) and `0 / 0` (non-unique) uniformly with `0 − 1` in ℕ, `√−1` in ℝ, `7 / 2` in ℤ and modular inverses; (iii) a set of **executable, cross-validated artefacts** (an IEEE simulator matched to hardware including flags, measured machine semantics across seven toolchains, gate-level circuits); (iv) several **precise links to CGT** (numerals as addresses, carry-lookahead as arithmetic compilation, Horner vs. balanced evaluation as a grammar-shape trade-off). Whether any of this is new beyond presentation is assessed honestly in `RESULTS.md` §F.
