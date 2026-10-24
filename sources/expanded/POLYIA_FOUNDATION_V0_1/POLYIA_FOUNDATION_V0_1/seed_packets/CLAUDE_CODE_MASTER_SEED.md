# MASTER SEED — PILLAR9 / Corpus-Aware Native Language / Scoped Model Architecture

**For Claude Code or other coding agent.**

You are implementing the independent PILLAR9 language-and-knowledge research path for Substrate University. The user rejects the earlier “JASON as JSON program interpreter” approach. **DO NOT extend, migrate, or reinterpret the older JASON runtime as the foundation.** It is a negative reference for design failures. Work in this newly provided PILLAR9 packet. Do not change the previously commissioned Qur’an cipher book, JASON package, CLOCK9, PURL, SEURL, Substrate University, or another project without a separate explicit user instruction.

## Author's aim

Build a compiler-oriented language for agents to represent and execute knowledge-processing operations where corpus content is addressable, finite scopes have positive and negative grammar, inverse mappings declare missing information, and micro-specialists can compose through typed G-ship relations. The target is a substrate-native alternative to depending on one monolithic LLM. The goal is not to claim universal O(1) inference, but to engineer constant-time *specific indexed operations*, and to expose the total costs of retrieval, verification, compilation, generation, and update.

## Baseline you must personally verify

1. Inspect `README.md`, `docs/CONSTITUTION.md`, `docs/COMPLEXITY.md`, `docs/LANGUAGE_AND_SPECIALISTS.md`, `docs/CORPUS_UNIVERSE.md`, `docs/SOURCES.md`.
2. Run `python -m pillar9 test`; report the exact test count and any failures.
3. Run `python run_experiments.py`; inspect `results/EXPERIMENTS.json`. It previously processed 220 real local Python standard-library files, yielding 218 unique content digests after content de-duplication; count may vary by environment.
4. Run `python run_scaling.py`; test expected O(1) direct hash lookup versus logarithmic *proof length*, while explicitly stating this demo recomputes proofs O(N).
5. Run `python -m pillar9 compile examples/hello.p9`; run its bytecode; expected `162`.
6. Run `python -m pillar9 demo "draw a spinning blue cube"`; confirm it emits `.p9s` and `.html`, then test JS parse and browser WebGL rendering **separately**. Previous headless Chromium could parse HTML but reported WebGL context unavailable. No GPU conformance has been established.
7. Verify that the older JASON and scripture packets are byte-for-byte unchanged.

## Mandatory next engineering sequence (do not jump to giant neural training)

**Stage A — improve the real language**

- Formalize a complete lexer/CST/AST; typed symbol table, effect system, modules/imports, closures, arrays/records, memory layout and a stable binary ABI. Ensure the language itself is written in a source syntax, not JSON operation trees.
- Introduce dependent/admissibility constraints and explicit author-proof certificates where tractable. Add an actual reference compiler to WASM or LLVM IR; compare against the bytecode interpreter and preserve semantic equivalence.
- Define “parenthology” as parser/grouping, “pillar” as typed invariant/support, “tower” as typed expansion between alphabets and languages; reject unsupported translation.
- Add bytecode verification (stack heights, safe constant loading, bounded memory) before loading untrusted compiled programs.

**Stage B — corpus-before-corpus framework**

- Define pre-ingestion manifest and adapters for Python, JS/TS/GLSL, HTML/CSS, graphics docs, MediaWiki XML. Include canonical positions, revision/namespace, license, text/code split, source trust and payload hashes.
- Implement a disk-backed content-addressed store (SQLite/LMDB/RocksDB) with efficient offset/cached lookup; build typed inverted indexes and Merkle DAG structural sharing. Support incremental updates. Distinguish original and derived content.
- Build a verified `lookup(cid)` path, a `proof(cid, root)` path, and a guarded `search(query)` path with measured complexity. No whole-document output in O(1).
- Open-source integrations must credit source licenses. MDN prose may require CC BY-SA attribution/share-alike; Khronos tests and three.js are separate MIT sources. Do not bundle third-party material casually.

**Stage C — compiler and reverse grammar bridges**

- Use Tree-sitter or Babel for real JS/TS AST/CST extraction. Preserve source offsets, type bindings, symbol identity, module references, side effects and versioned environment assumptions.
- Inverse-grammar engine should produce candidate productions and minimal rejection witnesses. Require held-out examples and negative controls to avoid mere memorization.
- Build typing/effect-preserving bridges from English instructions → Graphics IR → GLSL shader + WebGL DOM. A bridge must specify source type, target type, loss function (if any), evidence and counterexamples.
- Build G-ship algebra with edge composition, search budgets, provenance, ambiguity detection, and testable route identities; prevent semantic inference from topology alone.

**Stage D — actual micro-LLM or hybrid specialists**

- Implement a *baseline* deterministic symbolic specialist, plus small neural baselines only if training resources and datasets exist. Research nanochat / LitGPT / llama.cpp / small open model licenses. Differentiate pretrained weights, architecture source, and actually untrained-from-scratch weights.
- A truly trained specialist must report architecture, seed, corpus/license, train/validation/test split, optimizer or non-gradient alternative, loss/quality metrics and compute. If using only a grammar/dictionary, call it symbolic—not an LLM.
- Language expert and graphics expert should remain independent services or modules, bridged by a typed contract, and be capable of returning an “unknown/unsupported” answer.
- Include an ablation suite: template only vs retrieval only vs small transformer only vs verifier-backed hybrid; actual GPU screenshots and WebGL conformance where possible.
- Resource-gate Android/Termux integration (CPU, memory, battery, filesystem sandbox, model downloads). APK is **not** part of this v0.1 baseline.

**Stage E — CLOCK9 integration**

- Author's actual CLOCK9 ZIP may be attached later. Until then, use the public `akadaan310/clock9` README as a conceptual clue **only**. Never invent CLOCK9's internal algorithms, weights, or protocol.
- Once supplied, map typed grammar clocks to real event traces and deterministic verifier phases; retain ownership and provenance distinct from model identity.

## Stop conditions and honesty rules

- No fabricated O(1) end-to-end LLM. Bound output work Ω(T), file hashing Ω(L), proof verification O(log N).
- No fabricated “trained” specialists, encyclopedia ingestion, GPU pass, or production readiness.
- Do not execute corpus text as trusted commands or import Python modules merely to inspect them.
- Do not modify original source repos or copyrighted scripture text.
- Record every failed test and uncertain result. Counterexamples should remain in the ledger after remediation.

## Deliverables for next run

- Updated language/compiler spec with formal grammar, type judgments and cost model.
- Executable compiler, binary IR, verifier, tests, profiling instrumentation.
- Pluggable content-addressed corpus store and deterministic Merkle proofs with scalable updates.
- Domain grammar + inverse grammar experiments with real held-out corpora.
- WebGL artifacts tested in browser with screenshots, separately from JS syntax checks.
- Clear tiny-symbolic vs neural comparison, reproducibility manifest and limitations.
- PR-ready branch scoped to the new project only; no deployments or pushes without permission.

**Authorship:** Abed Kadan, Substrate University Research Commission. **Method:** rigorous constructive operations, computed witnesses, negatives and reproducible experiments, with semantic claims separated from structural facts.
