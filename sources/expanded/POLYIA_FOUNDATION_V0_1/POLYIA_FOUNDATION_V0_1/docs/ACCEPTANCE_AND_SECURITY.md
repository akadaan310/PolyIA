# Gates / Benchmark / Security

## Release-gating conditions

1. Current source hashes pinned and source permissions demonstrated; source extraction repeatable.
2. All 62 university topics represented as **source metadata and candidate interfaces**; topic count must not be confused with 62 implemented models.
3. Each shipped atom is independently importable, tested and uses only declared contracts.
4. P9-style native source compilation includes lexical, AST, typed ports and executable output. JSON-only DSL does not count.
5. Deterministic concierge returns machine plan, usable packaging and explicit refusals.
6. At least two distinct effects (pure calculation vs permitted mutation) are proved to have distinct authority paths; GET never mutates.
7. PHONEX is exercised on approved real corpus/variety sources, with published license and source-digest manifests; no made-up etymology.
8. Independent negative controls, corrupted data, invalid IPA, version mismatch, nondeterminism and performance regressions handled.
9. Source projection and inverse failure are explicit; original Unicode retained.
10. At least two integration vertical slices: real multilingual word set + distinct nonlinguistic vertical (e.g. physics toy or PURL resource) to prove generality.
11. Oracle VM CPU/RAM/SSD telemetry, p50/p95/p99, RSS, index size, cold/warm startup, build and runtime steps recorded.
12. SDK package includes interface contract, docs, license, example, lockfile and reproducible tests. No false certification of browser GPU/physics builds.
13. GitHub publish is separate action after explicit authorization; do not use user's credentials by accident.
14. All tests pass locally AND a clean checkout; failures kept with source, reproducible logs, and no hidden repairs.

## Threat model

Untrusted corpora, prompt text, code from old repositories, adversarial configuration, malicious grammars, malformed binary FSTs, unsafe native plugins, source-license leakage, arbitrary outgoing HTTP, fake evidence, secret exfiltration, build-cache poisoning, path traversal, unlimited recursion and unbounded state explosion. Controls include fixed resource limits, no dynamic `eval`, zero network by default, declarative capability manifests, sandboxed plugin worker processes, signing checks when available, stdout redaction, and deny-by-default on unknown rights.

The included Python reference is not a hardened sandbox, compiler optimizer, cryptographically authenticated provenance system, or real phonetic search. It uses a simple hash chain to detect accidental local edits, not adversarial modification by someone controlling both state file and code. A production authorization system must supply authenticated signers and independent evidence.

## Performance comparisons

Compare to plain list scan, dict index, SQLite FTS, trie, a tuned OpenFst/HFST baseline, and optionally a neural G2P model if relevant. Count build cost and peak memory. Report source coverage, matched initial-phone correctness, top-k recall, false semantic links and latency as separate metrics. A composed SDK can outperform a general runtime on restricted tasks via precompiled specialization, but no universal complexity advantage is presumed.
