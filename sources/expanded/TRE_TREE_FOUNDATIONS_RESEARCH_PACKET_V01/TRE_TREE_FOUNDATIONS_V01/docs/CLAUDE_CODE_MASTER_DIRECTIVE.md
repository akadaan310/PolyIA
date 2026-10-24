# Claude Code Master Directive — TRE/TREE formal machine foundation

Role: architectural researcher, compiler/runtime engineer and verification owner. Read this file in full, then `README.md`, `docs/00_CONSTITUTION.md`, all architectural specifications, executable examples/tests, and finally linked repositories. **Current user priority: establish the hierarchy and systems first. Do not start rebuilding HOMELESS or copying an existing game engine.**

## Nonnegotiable objectives

1. Treat TREE as the **formal growth/structure substrate** and TRE as the eventual **True Real Engine**, with separate structural arborescences and typed, potentially cyclic cross-network coupling.
2. Preserve the strict layer boundaries: natural corpus → grammar/extraction → typed semantics → compiler IR → VM/runtime → SceneIR/PhysicsIR → backend → observations and evidence.
3. Use the project’s own CGT/Grammar in Numbers / Substrate University / SubstrateIO concepts to state precise costs and admissibility. Protect the independent Division IX / Infinity research; do not invent missing VII/VIII divisions.
4. Keep PILLAR9 as a **native compiled language lineage**, not a JSON program interpreter. Prior JASON is a historical negative case, not an implementation architecture to recycle. JSON is permitted for manifests/results only.
5. Preserve PURL/SEURL access vs authority distinction: a view/URL never itself authorizes mutation. Keep CGIT typed commits distinct from Git wire-format objects and immutable evidence distinct from truth.
6. Compare permissive GPU/physics implementations using the pinned-source review. Unreal’s source is source-available under Epic EULA. **Do not copy Unreal code into TRE**. Study architectural patterns via official docs, and if independently authorized to inspect private source, keep a clean-room boundary and record access/license terms.
7. Keep `akadaan310/homeless-dark` untouched unless the user explicitly authorizes a migration. It has web and Unity directions recorded at different times; do not resolve those by silent rewriting.
8. No payment/new subscription/cloud provisioning, no game assets from unspecified marketplaces, no mobile release claims without real hardware/build evidence. No blind recursive downloads of heavy repositories.

## Already implemented in this isolated reference packet

- `tre/core.py`: typed parent graph, support coupling edges, deterministic test geometry, resource accounting, negative grammar and versioned events.
- `tre/corpus.py`: signed-off shape contracts before ingestion, license/source envelopes, negative grammar, bridge refusal for missing required fields.
- `tre/cgit.py`: domain-separated content-addressed immutable object DAG with tamper detection; not Git or a cryptographically trusted chain.
- Python unittest fixtures with deterministic replay and counterexamples. **Rerun them**; do not trust counts as substitute for local results.

## Immediate program (same session, preserve tests)

**Phase 1 — formal model:** expand schema and formalize all invariants, proof obligations and counterexamples; classify known vs untested; implement source-position type, renderer/physics effect types, reversible and lossy collapses with witnesses. Benchmark incremental graph ops and complexity, not clocks without accounting.

**Phase 2 — compiler bridge:** integrate with the actual PILLAR9 source after verifying the source files/revision and testing the API. Compile a tiny declarative 3D triangle surface description `.p9` through typed IR to a CPU pixel rasterizer. Do not use an interpreted JSON scene as language semantics. Save deterministic output and acceptance tests.

**Phase 3 — GPU graph:** implement `RenderGraph` with resource lifetime/hazard checks; prove DAG topology and read/write integrity; build an isolated benchmark adapter with pinned wgpu or bgfx, only after recording license/build availability. Compare real frames/pixels against CPU oracle and record GPU features. Build no engine-wide renderer before the graph contract is verifiable.

**Phase 4 — physics graph:** define fixed-tick `PhysicsIR` and integrate one pinned open-source physics benchmark (Jolt/Rapier/Bullet as appropriate), with deterministic/replay and contact differential tests. Keep plant growth as a distinct domain dynamic.

**Phase 5 — biological families:** implement parametric L-system, 3D space-colonization and multiscale tree graph *independently*, then compare branch structure, energy accounting, computation cost, negative controls, geometry reconstruction and source provenance. Do not claim all trees have golden ratios.

**Phase 6 — portable machine:** expose runtime targets WebAssembly/web and native Android/iOS/desktop as different backends of one typed and versioned SceneIR/PhysicsIR; treat signing, GPU drivers, storage and OS sandbox as platform-dependent, not virtualized-away facts.

## Source and license research sequence

Start with the curated URLs in `docs/SOURCES.md`. Verify repo URL/version and **license file for every candidate**. Do not vendor anything in the foundational branch. Track candidates as `study-only`, `benchmark-only`, `adapter-approved`, `vendored-with-audit`, `production-pinned`. Avoid using restricted UE code in another engine. Avoid treating glTF's JSON metadata as a programming language implementation.

## Acceptance proofs to deliver for each new increment

- Architecture decision record and typed interfaces.
- Tests and negative controls, with command, environment, output and source IDs.
- Measured CPU/memory/render timings *only after a real implementation runs*.
- Inputs, immutable hashes and output/checkpoint manifest.
- Explicit unresolved limitations and conflicts.
- A working demo with exact run instructions; if GPU device absent, mark GPU test `NOT_RUN`.
- No claim that a new micro-specialist is a trained LLM until genuine model training/inference exists.

## Forbidden shortcuts

- No full Unreal fork as TRE foundation.
- No 'O(1)' for arbitrary traversal, parsing, query, rasterizing, or output generation.
- No silent alteration of user corpuses or source text.
- No authorization via URL or LLM confidence.
- No visual fidelity claims from a headless scene compiler alone.
- No proposal-only completion report; continue with actual code/tests available in the environment, but never invent missing GPU/native evidence.
