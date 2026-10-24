# Sources and provenance — researched 2026-10-22

## Renderer / engines

- [Epic — Unreal Engine on GitHub](https://www.unrealengine.com/ue-on-github/) — authenticated source access and explicit warnings about incorporating UE code into independent products. **Source-available, not permissively open-source.**
- [Epic — Unreal Engine EULA](https://www.unrealengine.com/eula/unreal) — EULA and engine tool/distribution restrictions.
- [Epic — Render Dependency Graph](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine) — GPU resource lifetime scheduling / pass graph architecture.
- [Epic — Dataflow Graph](https://dev.epicgames.com/documentation/unreal-engine/dataflow-graph) — nondestructive procedural editor graph architecture.
- [wgpu](https://github.com/gfx-rs/wgpu) — Rust WebGPU-inspired API, Apache-2.0/MIT repo license.
- [Dawn](https://github.com/google/dawn) — WebGPU and Tint, repository BSD-3-Clause license. Read the exact pinned LICENSE before incorporating.
- [bgfx](https://github.com/bkaradzic/bgfx) and [overview](https://github.com/bkaradzic/bgfx/blob/master/docs/overview.rst) — graphics API abstraction; BSD-2-Clause.
- [Godot renderer layering](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html) — graphics driver vs abstraction vs rendering method.
- [Godot license](https://docs.godotengine.org/en/stable/about/complying_with_licenses.html) — MIT and third-party license notice requirements.
- [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) — portable scene format; JSON metadata + binary payload.
- [SDL source](https://github.com/libsdl-org/SDL) — zlib-licensed cross-platform window, input and audio.

## Physics

- [Jolt Physics source](https://github.com/jrouwe/JoltPhysics) — MIT license, high-performance collision library.
- [Jolt deterministic simulation docs](https://jrouwe.github.io/JoltPhysicsDocs/5.0.0/index.html) — replay order and cross-platform deterministic build option.
- [Rapier source](https://github.com/dimforge/rapier) and [user guide](https://rapier.rs/docs/) — Apache-2.0, Rust and language bindings.
- [Bullet Physics](https://github.com/bulletphysics/bullet3) — mostly zlib; exceptions in third-party directories.

## Tree and plant mathematics

- [Runions, Lane & Prusinkiewicz (2007), Modeling Trees with a Space Colonization Algorithm](https://doi.org/10.2312/NPH/NPH07/063-070).
- [Prusinkiewicz & Lindenmayer (1990), The Algorithmic Beauty of Plants](https://link.springer.com/book/10.1007/978-1-4613-8476-2).
- [OpenAlea Multi-scale Tree Graph](https://github.com/openalea/mtg), CeCILL-C; study/validate license before copying source.
- [OpenAlea functional structural modeling](https://openalea.readthedocs.io/en/latest/packages/modelling.html).
- [Lacointe (2000), Carbon allocation among tree organs](https://doi.org/10.1051/forest:2000139).
- [GreenLab FSPM review (2024)](https://doi.org/10.34133/plantphenomics.0118).

## Own research code and heritage (read-only at this phase)

- [Substrate University](https://github.com/akadaan310/abedkadaancom): `src/content/registry.ts`, `src/content/topics/relational.ts`, `src/math` (six established live-campus divisions; IX/Infinity distinct research).
- [SubstrateIO](https://github.com/akadaan310/substrateIO): typed transformation, observation, provenance.
- [Computational Grammar Theory](https://github.com/akadaan310/computationalgrammartheory): grammar signatures, structural/operational distinction, cost notation.
- [Grammar in Numbers](https://github.com/akadaan310/grammarinnumbers): value/numeral/encoding/machine-state distinctions.
- [PURL](https://github.com/akadaan310/purl), [SEURL](https://github.com/akadaan310/seurl): addressable operations and machine-reading surfaces.
- [CLOCK9](https://github.com/akadaan310/clock9): published README is minimal; no recovered implementation claims.
- [HOMELESS/Dark](https://github.com/akadaan310/homeless-dark): current repository and its distinct web and Unity commission documents.

## Source hygiene

These are references to open, primary published sources. No third-party engine code is embedded in this packet. No inaccessible Unreal source was claimed to be downloaded or inspected. Licensing statements are summaries, not legal advice; check exact release/tag, code files, third-party notices and platform requirements before any vendoring or distribution. The Python implementation here is original research glue, not a port or copy of the referenced source.
