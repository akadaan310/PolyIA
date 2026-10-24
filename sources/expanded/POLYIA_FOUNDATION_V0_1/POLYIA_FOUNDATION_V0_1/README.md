# POLYIA — Polymorphic Intelligence Agency · Founding Research Package v0.1

**Abed Kadan × 7u · 23 October 2026**

This is an **independent, non-destructive foundation** for a central capability library, deterministic compiler/concierge, and proof-bearing composed machine artifacts. It is a proposal with a **running small reference**, not a deployed global service or implementation of every source research project.

## First run — Python 3.10+, standard library only

```sh
python3 -m unittest discover -s tests -v
python3 -m polyia compile examples/topology.poly --out build/topology
# inspect build/topology/plan.pir, automaton.dot, automaton.html, automaton.json
python3 -m polyia harness init --dir /tmp/polyia-proof-run
python3 -m polyia harness status --dir /tmp/polyia-proof-run
```

A commission is **real parenthesized source syntax**, lexed, parsed, typed, and composed as a declared capability DAG. A single typed provider is required for every port. The compiler refuses unknown capabilities, ambiguous providers, dependency cycles, evidence-policy violations, budget overflow, and omitted core denials. It emits `plan.pir` and a state-machine artifact (`.dot`, `.html`, machine-readable JSON audit). JSON is an interchange format, not the source language or its semantics.

**Limits:** The example modules are *metadata-only fixture capabilities*; the compiled automaton describes an executable composition but does **not** perform a real universal multilingual phonetic search. This iteration demonstrates the commissioning/compiler and harness contracts, not real dictionary/IPA execution. An evidential `attested` commission intentionally refuses fixture providers.

## Core design

1. **POLYIA Atom:** capability + explicit typed ports + grammar + declared effects + version + provenance + executable witness.
2. **POLYIA Pillar:** typed preservation/refusal law on a mapping, independently checked.
3. **POLYIA Tower:** composable representation maps `L0→L1→…→Ln`; every transition records loss or inverse witness.
4. **POLYIA Forge:** a composition compiler that makes a machine from admitted atoms and typed ports.
5. **POLYIA Concierge:** a deterministic problem intake/compiler: parse → classify → resolve → assemble → verify → emit a tailored machine.
6. **POLYIA Agency Profile:** a package (e.g. PHONEX/ULWS, QIA, physics, ASTRO, browser) selecting a consistent subset of capabilities at exact versions.

## Files

- `docs/CODEX_CONSTITUTION.md` — implementation mandate and constitutional clauses.
- `docs/STATE_MACHINE.md` — explicit stage gates and evidence receipt laws.
- `docs/TECHNICAL_TREATISE.md` — formal objects, determinism, generative mechanisms, complexity.
- `docs/CONCIERGE_CONTRACT.md` — problem-to-machine compiler.
- `docs/REPOSITORY_ATLAS.md` — source repos, scope, verified entry points and unresolved sources.
- `docs/QIA_62_CAPABILITY_ATLAS.md` — 62 topic-to-component proposals **without falsifying implementation**.
- `docs/PHONEX_SPECIALIST_ARCHITECTURE.md` — per-language automata and higher machine synthesis.
- `docs/ACCEPTANCE_AND_SECURITY.md` — end-to-end gates, performance and boundary conditions.
- `schemas/Q_THEORIES_62.json` — sourced, proposed Q-theory register.
- `seed_packets/` — archival user research packets preserved as provided, never treated as live installable code.
- `polyia/` — executable *small* reference.
- `tests/`, `examples/topology_compiled/`, `reports/` — reproducing compiler and harness behavior.

## Governance

Nothing in this package creates a GitHub repository, deploys to the Oracle VM, edits Substrate University, HOMELESS, ASTRO, CIA Browser, PURL/SEURL, Arabic Timeless, or Muse's Corpus Engine. Reuse is by **versioned adapters and imports** after source verification; no code wholesale copied from source repos. Divisions I–VI remain six and exactly 62 topics; VII/VIII remain uninstantiated; Division ∞ is unnumbered; Division IX retains its separate proposal status; Arabic Timeless remains outside the university's academic registry.

Read `docs/CODEX_CONSTITUTION.md` before directing Codex to begin any deployment or repository mutation.
