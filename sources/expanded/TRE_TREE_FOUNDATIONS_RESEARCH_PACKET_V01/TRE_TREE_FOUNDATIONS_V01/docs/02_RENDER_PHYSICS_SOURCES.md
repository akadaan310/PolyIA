# Rendering and Physics Source Implementation Survey

**Decision at this phase:** build **our own domain model, render graph, scene compiler and scheduling contracts**, but do **not** reimplement Vulkan/Metal drivers, GPU shader compiler toolchains, collision kernels, or window managers without quantified reasons. Wrapping a tested library behind our API remains an original engine architecture. GPL/other licensing restrictions must be assessed per linked package.

## 1. Reference implementation matrix

| Project | Role | Reported license | Recommendation | Boundary |
|---|---|---|---|---|
| [wgpu](https://github.com/gfx-rs/wgpu) | Safe cross-platform GPU abstraction; WGSL; native and Web/WASM | MIT/Apache-2.0 | **Primary research candidate** if Rust system core is chosen | Platform backend, not scene or render graph design |
| [Dawn / Tint](https://github.com/google/dawn) | Native WebGPU and WGSL compiler | BSD-3-Clause (repo README) | Alternate C/C++ backend + shader reference | Research as separate adapter; do not combine with wgpu by default |
| [bgfx](https://github.com/bkaradzic/bgfx) | Small cross-platform renderer abstraction, WebGL2 / GLES / Vulkan / Metal | BSD-2-Clause | Strong C++/mobile baseline; **alternative**, not simultaneous dependency | Its abstraction does not implement TREE semantics |
| [Godot](https://github.com/godotengine/godot) | Full MIT-licensed engine with rendering architecture | MIT core + third-party notices | Study architecture/rendering pipelines; optional benchmark | Do not import the monolithic engine as TRE |
| [Jolt Physics](https://github.com/jrouwe/JoltPhysics) | Rigid-body collision/contact solver | MIT | Preferred C++ physics **oracle/reference**; cross-platform determinism options require configuration checks | Not botanical growth or resource exchange |
| [Rapier](https://github.com/dimforge/rapier) | Rust physics with JS/Web and FFI options | Apache-2.0 | Preferred Rust/Web physics **oracle/reference** | Existing HOMELESS web research already used Rapier; no mandate to port |
| [Bullet](https://github.com/bulletphysics/bullet3) | Collision and rigid-body alternative | zlib for primary code, exceptions in subfolders | Independent second physics oracle | Avoid conflating its GPU prototypes with turnkey mobile support |
| [SDL3](https://github.com/libsdl-org/SDL) | Cross-platform window/input/audio glue | zlib | Optional native host layer | Does not replace an OS or GPU driver |
| [Khronos glTF 2.0](https://registry.khronos.org/glTF/) | Portable rendered scene interchange format | Royalty-free standard | Adopt for asset exchange and validation | glTF JSON is asset metadata, **not** native source syntax |

**Unreal Engine:** Epic provides source access through an authenticated Epic↔GitHub association and permits source study. Unreal Engine source is **source-available under the EULA**, not a general MIT/BSD-style code source. Epic explicitly says copying any of its code into an independent product subjects that product to the EULA. Therefore: **architecture study yes, code copying into TRE no** unless the user intentionally accepts the resulting license obligations and adjusts the project contract. Inspect Epic's Render Dependency Graph (RDG), Nanite/VSM, Chaos, Dataflow at the level of techniques and observable contracts. We did not download private UE source and do not claim to have audited it. See Epic official license/source access and RDG docs in SOURCES.md.

## 2. TRE render graph IR (candidate)

```text
Resource: id, format, extent, lifetime, read/write constraints, producer
Pass: id, inputs[], outputs[], shader_ref, workgroup/draw domain
Dependency: produced resource or explicit barrier from pass i -> pass j
Backend capability: feature set, limits, shader language, buffer alignment
```

Validation: no read-before-write for transient resources; no conflicting alias lifetimes; DAG acyclic; shader source passes compiler validation; memory budgets declared; normalized scene transform; explicit color space, depth/clip conventions; observable GPU errors. Liveness and transient allocation are separate optimization stages. Use platform-specific shader backends and compute capabilities, not one universal shader binary.

Conceptual pipeline:

`TREE world transitions → SceneIR + MeshIR → transform/visibility → RenderGraph → ShaderIR → GPU backends → present/trace`

A tree morphology is not a literal render scene graph: a renderable entity may instance one mesh into hundreds of occurrences, and one render pass consumes resources from many scene nodes. Separate structural and scheduling graphs.

## 3. TRE physics contract (candidate)

```text
PhysicsWorld(tick, bodies, colliders, joints, fields)
    step(dt_fixed, input_events) -> state_next, contact_events, proof_trace
```

Tests: fixed-step replay, collision symmetry/sensitivity, stacking, contact budgets, stable order of events, energy drift reporting, broadphase vs narrowphase agreement, cross-backend differential tests with tolerances. Determinism is a **specific mode and configuration** rather than an automatic property across CPUs and floating-point platforms.

## 4. Source incorporation decision states

`study-only → benchmark-only → adapter-approved → vendored-with-audit → production-pinned`.

Each state records: upstream URI, immutable commit/version, license/third-party notices, compatible target platforms, exported ABI, component surface, footprint, CVEs/advisories, and required provenance. A source available online is **not yet a dependency**; no third-party source code has been vendored into this v0.1 packet.

## 5. Rational engineering order

1. Run a CPU-only reference transform/raster pipeline with pixel fixtures.
2. Compile one canonical mesh and PBR-free basic material into SceneIR.
3. Execute one validated render DAG via WebGPU or GLES backend, **on a working GPU**.
4. Add physics state projection and collision fixtures, keeping simulation separate from rendering.
5. Compare multiple engine backends and measure device performance (frame p95, CPU/GPU time, peak residency, shader compilation).
6. Only after evidence, select a pinned runtime for an independent TRE release.
