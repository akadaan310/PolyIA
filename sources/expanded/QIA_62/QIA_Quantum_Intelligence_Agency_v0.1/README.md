# QIA/0.1 — Quantum Intelligence Agency

**21 October 2026 · Abed Kadan × 7u**

Standalone research artifact. This packet is an evidence-conditioned computational research proposal, not a deployed or empirically validated universal quantum/physics engine.

## Read / inspect

1. [`QIA_FOUNDATIONAL_TREATISE.md`](QIA_FOUNDATIONAL_TREATISE.md) — research exposition (nomenclature, field mathematics, toy mapping, physical modeling, string completeness, compiler, evaluation criteria).
2. [`Q_THEORY_ATLAS_62.md`](Q_THEORY_ATLAS_62.md) — 62 distinct source-grounded topics, each with a **proposed** typed Q-theory contract, invariant and compilation target.
3. [`schemas/Q_THEORIES_62.json`](schemas/Q_THEORIES_62.json) — machine-readable overlay preserving source division/topic/status.
4. [`src/qia.py`](src/qia.py) — portable, **standard-library-only** deterministic prototype: typed hyperedge solver with refusal and status checking, name fibers, Unicode fidelity, numerical quantum toy, spring-mass and acoustic toy, dimensions, formal context closure.
5. [`tests/test_qia.py`](tests/test_qia.py) — new 35-test suite.
6. [`examples/TOY_RESULTS.json`](examples/TOY_RESULTS.json) — recorded outputs and evidence statuses.
7. [`examples/TEST_REPORT.txt`](examples/TEST_REPORT.txt), [`examples/INFINITY_RETEST.txt`](examples/INFINITY_RETEST.txt), [`examples/FNMS_RETEST.txt`](examples/FNMS_RETEST.txt) — execution evidence of 35 new tests plus 23 Division ∞ and 19 FNMS tests **rerun separately**.
8. [`REPOSITORY_ALIGNMENT.md`](REPOSITORY_ALIGNMENT.md) — current read-only repository/source reconciliation and limitations.

## Run

```sh
cd QIA_Quantum_Intelligence_Agency_v0.1
python3 -m unittest discover -s tests -v
python3 src/qia.py > examples/TOY_RESULTS.json
python3 build_registry.py
```

Python 3.10+; no network, RDKit or quantum device necessary for **new QIA tests**. The original FNMS 19 tests use RDKit and are distributed only in the user-supplied FNMS and Division ∞ ZIPs. The independent 23 Division ∞ tests run on Python stdlib.

## Constitutional invariants

- Active university registry: six divisions / 62 topics.
- VII and VIII reserved, not created.
- IX is separately proposed, not automatically enacted.
- ∞ is unnumbered, not IX, and the agency QIA is a research and operational layer, not a newly enumerated division.
- No university repository edits, GitHub commits, UI changes, outside corpus ingestion, production VM actions or Unreal deployments were performed.

## Epistemic boundaries

The 62 Q-theory contracts are an enumerated research blueprint, not 62 verified scientific theories. A named “quantum field” is an information field unless explicitly modeled as a physical field. The 2-state amplitude experiment is classically simulated and makes **no hardware quantum-speedup claim**. “String completeness” is here defined only relative to explicitly enumerated finite schema and physics resolution budgets, not every particle in the universe or physical string theory. The FNMS “Head Pain Reliever” hypothetical brand-to-active identity is a user stipulation; semantic meaning alone has a nonunique inverse.
