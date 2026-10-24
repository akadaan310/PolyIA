# Engineering Roadmap: Hierarchy Before Engine

This is a sequence of **verification gates**, not a claim that the whole engine was implemented.

| Gate | Increment | Acceptance | Status |
|---|---|---|---|
| G0 | Governance, source manifests, scope boundaries | Typed roots/verbs, named policy and licensing | `[C]` drafted |
| G1 | Dual TREE structural/coupling graph, resource ledger | Test siblings, cycles, witnesses, replay | `[M]` Python fixture tests passed |
| G2 | Corpus-before-ingestion and typed bridges | Reject uncontracted/malformed records and impossible bridge | `[M]` fixture tests passed |
| G3 | Content-addressed object DAG | Reuse common object, hash tamper detection, typed children | `[M]` fixture tests passed; **not full CGIT** |
| G4 | Native `.p9`/domain grammar compiler → IR → bytecode | End-to-end typed scene program; independent disassembler/verifier | `[BLOCKED]` integration with prior PILLAR9 not run in this packet |
| G5 | World IR, scene IR, render graph IR contracts | DAG hazard tests + shader validation | `[H]` designed |
| G6 | CPU reference rasterizer + glTF importer | Pixel ground truth, format validation, memory bounded | `[H]` proposed |
| G7 | One GPU backend + platform adapter | Real GPU frames with capture/telemetry and device quality gates | `[BLOCKED]` not built |
| G8 | Physics reference + deterministic fixed-step world | Replay and differential invariants against Jolt/Rapier | `[BLOCKED]` not built |
| G9 | Native/web packaging, secure capability boundaries | WASM/web, Android APK, iOS project artifact with signing/build evidence | `[BLOCKED]` not built |

## Separate clocks; do not conflate with prior CLOCK9

Suggested clock families: lex/parse, compiler, simulation, scene, GPU frame, audio, persistence, agent/continuity and network. These are scheduling **hypotheses** and not a recovered authoritative CLOCK9 implementation. Link the actual project's source before claiming equivalence.

## Selection experiments, not ideological commitments

- Rust core + wgpu + Rapier (candidate A) versus C++ core + bgfx + Jolt (candidate B).
- Native backend performance by target device, toolchain compatibility, shader cost, memory and license compliance.
- For geometry, compare simple triangle raster, mesh instancing and GPU-driven draw scheduling; only compare what is running on the same hardware.
- For dynamics, compare deterministic grammar-only tree evolution against environmental space-colonization and physics-augmented growth.
- For corpus routing, compare baseline direct compilation to one or more specialized learned proposers, with latency and failure-rate measured.

## Explicit HOMELESS boundary

On review, `akadaan310/homeless-dark` contains both a former web implementation/continuation and a later Unity-only standalone constitution. The present request reopens an independent engine-design direction, **but this packet never edits the game repository or silently overrides its existing commission**. Any future migration to TRE requires: decision log, source license review, saved assets/commit IDs, portability tests, screenshots, Android acceptance plan, and explicit parity/replacement criteria. Existing achievements remain preserved.

## First post-packet implementation deliverable

A real typed `SceneIR` program compiled from `.p9` to executable, deterministic CPU triangle raster output with a golden pixel file and logged CPU/memory cost. It must not require third-party GPU support to test the language/render boundary. Parallel: pin and build one permissively licensed reference GPU or physics adapter only in a separate experimental branch.
