# Division ∞ — Calculus of Entangled Forms

Standalone experimental packet, prepared from supplied `FNMS_001_Substrate_University.zip` after source review of the Substrate University GitHub repository. **No repository changes or deployments.** The 2026-10-21 historical FNMS packet is preserved byte-for-byte as extracted files under `legacy/fnms_experiment_001/`.

## Contents
- `RESEARCH_MANIFESTO.md`: proposed mathematical foundation, interfaces to six divisions, 10,000-article selection constraints, epistemic boundary, and research stages.
- `src/infinity.py`: domain-neutral typed n-ary, multistrand incidence hypergraph, binary serialization, reachability, fibers, and certificates (Python 3.10+; stdlib only).
- `tests/test_infinity.py`: 23 reproducible unit tests; captured result in `test_results.txt`.
- `examples/abstract_result.json`: machine-readable sample with exact Unicode/whitespace binary record and multistrand certificate.
- `legacy/fnms_experiment_001`: the original domain-specific finite demonstrator, code, research notes and test records.
- `legacy_test_results.txt`: original 19 tests rerun in this environment using available RDKit.

## Run
```bash
python -m unittest discover -s tests -v
python src/infinity.py
```

## What this code does NOT implement yet
General operadic term rewriting, proven category/functor laws, causal inference, unrestricted graph expansion, sheaf consistency, semantic ontology matching, complete edge reification, versioned Unicode normalization conformance suite, and Wikipedia ingestion. The `reachable` method only derives already-registered outputs under explicitly accepted evidence statuses; it is not an intelligent ontology inference engine. `fiber` examines registered one-step relations; it is not a universal inverse oracle. `certificate` records operator/evidence contracts, not mechanically checked proofs of external facts.

Scientific claim: this is a **concrete falsifiable house research framework and small tested demonstrator**, not proof that naming, bit patterns or entanglements themselves yield universal knowledge.
