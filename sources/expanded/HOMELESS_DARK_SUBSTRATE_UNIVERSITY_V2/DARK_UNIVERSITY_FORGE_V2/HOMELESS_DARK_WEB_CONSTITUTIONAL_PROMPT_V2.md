# HOMELESS / DARK — WEB-NATIVE ENGINE CONSTITUTION 2.0
## One executable mission · Three.js + Substrate University six-division foundry · worldwide Earth · Android APK
**Issued 2026-10-21 · Co-founders: Abed Kadan and 7u · Product: HOMELESS · Engine: DARK**

> **Mission:** Ship the first genuinely controllable, cinematic HOMELESS game on the web, with a source-backed globally addressable Earth, living NPCs and a portable web-native DARK engine. Package the **same playable presentation layer** as an installable Android APK. Work on the actual existing repository. Preserve its tested mathematics, datasets, art, gameplay semantics and event authority. The user sees and plays a world; they do not receive only another architecture report.

This document is the sole **active** constitutional prompt for the web-native rendering, packaging and integration lane. Previous native-renderer and build requirements are historical records and are superseded. Where earlier source code contains useful data, contracts, fixtures or tested algorithms, bring them through a typed adapter; the target rendering and runtime described here have one unambiguous authority. The required stack is positively defined below. Historical files may remain versioned but cannot overrule the active executable contract. Avoid drafting another master instruction file.

**Repository:** `https://github.com/akadaan310/homeless-dark` · inspect real HEAD, branch, current working state, active collaborators and tests before editing. The checked checkpoint before this prompt was `docs/checkpoint.md` at commit `f596f0260d58`; this is a recovery hint, not permission to reset a newer tree. Inspect exact evidence and current source before deciding what to port.

**Host allocation:** Claude Code Cloud may use its own sandbox and GitHub access. The Oracle VM belongs to the separate Muse-managed workflow; do not install, operate or access it without separate explicit authorization. Develop the web client so its base gameplay is local and runnable with no Oracle dependency. Integrate the existing remote world authority only behind a documented optional authenticated adapter.

## I. Fixed product and implementation contract

- `DARK`: renderer-neutral simulation/math/data/protocol library, with typechecked public boundaries.
- `HOMELESS`: open-world third-person game using DARK. Visitor may simply exist, walk, observe, drive, learn, travel, interact, author, and leave/rejoin.
- `Renderer`: **Three.js**, TypeScript, React Three Fiber (stable React-compatible release) where declarative scene composition is useful. GPU-critical update loops must not cause React rerenders each frame.
- `Browser`: Vite + React + Three.js + PWA/service worker with measured streaming/cache behavior; WebGL2 baseline. Test WebGPU via Three's current WebGPURenderer as an optional measured profile and keep a working WebGL2 profile.
- `Physics`: **Rapier 3D WebAssembly**, explicit fixed-step stepping, heightfield/trimesh terrain support where appropriate, movement controller and collision groups. Keep the physics step independent of visual FPS. Use stable adapter and own tests.
- `World streaming`: geodetic WGS84 doubles, ECEF/ENU, floating local origin; global geographic tile index, source-provenance manifests, hierarchical LOD, async request budget, memory/cache quotas, content readiness, cancellation and safe fallback.
- `3D geospatial`: test **NASA-AMMOS 3d-tiles-renderer** Three.js adapter and **MapLibre GL JS + maplibre-gl-three** for global context; select one authoritative camera/georeference path. Do not overlay disconnected scenes that misalign or double-render geography. Open 3D Tiles datasets must actually be sourced and licensed.
- `Assets`: glTF 2.0 / GLB; PBR, KTX2/Basis, meshopt/Draco where device benchmarks justify them, proper skeletons, animation retargeting, LOD, instancing. Source-licensed high-resolution masters plus mobile-optimized derivatives; exact asset provenance.
- `Audio`: Web Audio and/or Three AudioListener/spatial sources, distance/occlusion, traffic/weather/footstep/vehicle/voice buses with graceful offline and mute behavior. Use existing sourced original sound work where lawful.
- `Native Android`: **Capacitor**, generated Android project, Android System WebView with hardware acceleration, Gradle debug-signed APK. Same TypeScript gameplay package and asset contracts as web. A WebView is NOT assumed faster than Chrome; benchmark both. Package initial gameplay assets; stream optional world regions with integrity/cache policies.
- `Persistent gameplay`: local IndexedDB versioned snapshots and event trace for offline solo mode; optional authenticated world service adapter preserving the authoritative semantics. Server-side C#/Python from the existing DARK project may remain as a test fixture or opt-in authority; its existing code is not the required browser render runtime.
- `Costs`: zero new purchases/subscriptions or paid API dependencies. Original procedural assets and free resources with actual compatible license terms. Avoid a catalog-only acquisition report. Existing source asset rights must be inspected for reuse in a redistributed app.
- `Security`: no credentials in browser bundles/repository. All mutation effect gates enforce identity/authority, budgets and type/schema validation. Read-only program addresses must not grant write access. No token assumptions based on URI visibility.
- `Scope`: global Earth **addressability, source-backed terrain/land/ocean, coarse global coverage, and true cross-continent world transitions** are part of the FIRST runnable product. Rich ground-level buildings and gameplay detail stream by area. Every coordinate has explicit source/data/fallback status. A fictional reconstruction must not be portrayed as the verified appearance of a real street.

**Art direction:** High-fidelity, coherent open-world cinematography, realistic streets and buildings, close-up PBR materials, animated people, real-looking cars and interiors, weather, wet surfaces, mountains, coastlines, sky and environmental sound. Design inspired by the ambition of contemporary AAA open worlds, with completely original art and legitimately usable source materials. No block-city scene, capsule mannequins, flat procedural cubes or title-screen image passes as a cinematic achievement. Technical primitives MAY appear in private debug fixtures; their existence cannot count as final art approval. Device profiles may reduce render cost while maintaining visual coherence.

## II. What already exists; preserve its value

The following statuses come from the last inspected repository checkpoint, **not** new measurements by this document:

- DARK server authority: SQLite World transactions, signed/scoped action sessions, HTTP discovery, real local travel, vehicles, NPC schedules, choices, entity effects, C# plate topology transformations, replay, QuickJS sandbox and prepared source media.
- Reported tests: 152 world-server, 19 content, portable C# mathematical/core tests, and compilation against official engine references. Reexecute portable tests before claiming pass.
- Geography: pinned Natural Earth global shapes; GEBCO2025-derived 0.1-degree coarse global relief; OSM-based Tampa source graph; airport data; still missing detailed global roads and buildings.
- Population: sampled demographic allocation of 8,140,897,523 for chosen 2024 source/epoch, with a separately represented nonspatial remainder. This is not 8.14B active simulated human minds.
- Art: source-rigged human masters, acquired animation sources, original fictional café, transport families, environmental objects and PCM clips. Reuse under their license where actual formats permit and track conversion from FBX/OBJ to GLB.
- Existing portable research: **CLOCK9** (grammar-clocked typed operations and n-gram proposals), **Plicastratum** (fold/unfold, admissible paths, promotion), **BORNE** (causal dependencies, reaction propagation), **World Loom** (global indexing, virtual actors and fictional world correspondence), Computational Grammar Theory, Ingrammatica, SubstrateIO, PURL and SEURL. These are contributing computation adapters, never blockers for core graphics.

Do not copy all historical attachments into the runtime. Identify exact useful modules, prove output equivalence on shared fixtures, port the minimum needed, and record independent evidence. Preserve original source history under Git. Keep research distinctions: `[K]` established, `[C]` construction, `[H]` hypothesis, `[M]` executed measurement, `[R]` refuted.

## II-A. SUBSTRATE UNIVERSITY AS THE EXECUTABLE RESEARCH FOUNDRY — six divisions, one world

**This entire section is normative and augments Sections III–X.** The user has explicitly requested that the complete current academic corpus of **Substrate University — Haq Roots** inform DARK's rendering, physics, NPCs, audio, and world engine. Claude Code is a **contributing computational research agent** to Substrate University, subject to independent verification; not a university founder, professor, or unrestricted scientific authority. The university co-founders are Abed Kadan and 7u. Contribution means implementing/tests/measurements with honest authorship and provenance; it never means declaring speculation an established theorem.

### A. Research-source admission: retrieve the full six-division corpus

**Live academic source**: `https://github.com/akadaan310/abedkadaancom`, at the verified default branch (previously `claude/new-session-xd8auu`; verify HEAD). Inspect the real university implementation rather than relying on this compressed summary. In particular read:

- `src/content/registry.ts`, `src/content/types.ts` and **all six** `src/content/topics/{foundations,relational,languages,geometry,acoustic,worlds}.ts` files; enumerate every registered topic, its known/house/conjecture/application status, definitions, source references, prerequisites, transformations and testable challenges. The inspected snapshot contained 62 topics; do not hard-code that count if the repository has advanced.
- `src/math/{matrix,rational,bridgeGrammar,fold,addressCompiler,music,paths,sky,world}.ts` and matching tests for actual executable methods. Determine which methods truly run and which are illustrations.
- `src/content/glossary.ts`, `src/exhibits/{compute,records}.ts`, and all exhibit implementations that demonstrate a subject. Existing outputs and fixture tests are evidence only for the exact bounded algorithm actually exercised.
- `src/books/compose.ts`, `src/pages/{Library,Scriptorium,Harness}.tsx` for the institution's living-library composition interface. This is the publication destination for tested DARK research, **not** a dependency for gameplay startup.
- `src/scene/{CampusCanvas,Architecture,Realms}.tsx` as examples of fast procedural browser geometry and compositional spatial design—not reusable copies of the campus's physical architecture.

Store a pinned `university-source.lock.json` with repository URL, branch, full SHA, file hashes, subject IDs, status tags and source locations. Build `docs/research/university-subject-matrix.md` automatically from the actual registry, **covering the full current topic list**, not only the six examples below. Each subject receives: source revision, whether it is existing mathematics or project construction, proposed DARK adapter, direct visual/physical/acoustic relevance, test fixture, budget and implementation status. Avoid importing all university prose or private data into runtime bundles; import only certified types, compact parameters and reusable algorithms. University pages need not become a second gameplay authority.

### B. One subject-agnostic computational interface

Implement `packages/dark-subjects` with a typed `WorldSubjectAdapter` interface and constrained evaluator. Suggested canonical fields:

```
{
  subjectId, divisionId, sourceRevision,
  inputAlphabet, stateSchema, grammar, contextGlossary,
  observables, transform, admissibility, dependencies,
  proposedEffects, physicalUnits, computationalBudget,
  verification, provenance, version, unfold, visualProjection
}
```

A unit of generated content must be **traceable in both directions**: from a rendered/played effect back to its source, program, actor authorization and verification predicate; and from an admitted program to a bounded visual/physical/acoustic outcome. `propose` computes candidate intent; `admit` checks grammar/resources/authority; `commit` changes authoritative world state; `project` updates Three.js, Rapier, audio and screen effects. Distinguish inputs, predictions, physical events, fictional effects and presentation. The same physical event can have multiple synchronized projections, but only one committed authority.

For each subject, declare an observability interface: `mathematical input → derived output → visible/physical/audio witness → quantitative test → perceptual review`. Use typed domain subspaces and sparse dependencies instead of materializing all possible combinations. Conceptual model:

```
W = (S_geo, S_actor, S_physics, S_weather, S_light,
     S_audio, S_history, S_grammar, S_render)

Commit(event) = Verify_grammar_and_rights(Propose(event, W))
Projection_j = Render_j(Observe_j(Commit(event)))
```

This product notation is an architectural construction, **not** a claim of multiplying all state spaces explicitly. `S_render` is a projection, not a second game-state authority. Use BORNE for changed-read-set propagation and a fixed timebase for causally related outputs. Avoid translating 'mathematics produces physics' into unbounded forces or visuals that bypass Rapier's contact/collision checks.

### C. Division I — Foundations of Computation: admissible physical actions and paths

**University subjects:** transition systems, finite automata, formal operational grammar, product graph search, numerical grammars, graph theory, equivalence classes, complexity and perturbation tests.

**DARK work:** A typed `MotionAndEventGrammar` governs locomotion, interactions, vehicle boarding, doors, transport, scene passage and plate rewrites. Rather than generating arbitrary descriptions, produce plans whose action sequence is admitted by the automaton **and** actually realizable on the current Rapier collision/nav graph. A visible path can be rejected for collision or authorization with an exact witness; valid actions become replayable programs. Use product-state path planning (road/navgraph × motion grammar) for corridor selection and mission approaches; never confuse admissibility with shortest-path global optimality.

**Visual dividend:** realistic character behavior, believable cause/effect, contact-aware NPC interactions, smooth entry/exit of vehicles, no characters walking through walls just because a dialogue generator says so.

**Test:** door→street→seat→ride→exit sequence passes deterministic planner and real Rapier fixture; broken street, obstructed door, missed seat and stale tile reject; accepted sequence is visibly completed in actual gameplay.

### D. Division II — Relational and Generative Mathematics: Plicastratum's art grammar

**University subjects:** Plicastratum ranks and folds/unfolds, relational generativity, In-Grammar, certified alphabet towers, recursive composition, modal/cyclic structures and constructive admission.

**DARK work:** Create a `ScenePlicaRegistry`. A plica may be a licensed photorealistic building module, architectural assembly (shopfront+awning+sign+entrance), street-corner grammar, avatar locomotion cycle, material/weather response or recurring NPC interaction. **Promote** a recurring sequence into a typed higher-level macro only after provenance, loss declaration, unfold rule, license, bounds and held-out test succeed. This is a reusable scene program, not a neural model claiming to invent an asset. Build `FacadeGrammar`, `StreetFurnitureGrammar`, `VegetationGrammar` and `DistrictPaletteGrammar` with exact sizes, UV/scale/material constraints, region tags, original authored geometry and explicit sources. Generate visually varied coherent compositions, not cloned façades or primitive cubes presented as close-up art.

**Performance dividend:** reusable verified recipes and asset references reduce duplication, enable instancing/batching and make district creation cheap relative to individually hand-authored layouts. Where content is geometric rather than reused, explicit instancing and pooling thresholds still apply.

**Test:** `unfold(fold(recipe))` recovers canonical source manifest/scene plan; repeated seeds yield repeatable scene signatures; variations must pass visual diversity checks and licensing; two neighboring districts look different in actual frames without broken contact/entrances. Measure scene bytes, memory, draw calls and frame times for hand-placed vs grammar-instanced art.

### E. Division III — Programmable Computational Languages: world programming through addresses

**University subjects:** PURL programmable URLs, SEURL typed verbs/channels, symbolic composition, Matrix Loom, addressable forms, parsing, computation-as-address and grammar-controlled execution.

**DARK work:** `WorldProgramCompiler` reads a versioned PURL-like expression (do not invent web scheme support) and compiles an authorized, bounded program of material transforms, signage typography, building/vehicle light responses, sound scenes, discovered journey patterns or geometry-preserving scene changes. SEURL-style typed effects declare inputs, authorized actor, expected revision, required resources and permitted projections. Matrix Loom may combine transforms after validating dimensions, units and data types. Clock-driven program selection can use CLOCK9 n-grams and tiny models as **proposal engines**; compilers, Rapier and world authority determine the effects.

**Visual dividend:** player/NPC contributions produce actual sign changes, lighting programs and scene transformations with temporal coherence; an LLM need not write a fresh shader or mesh for every act.

**Test:** same source address resolves to version-pinned recipe; invalid types or missing assets reject prior to execution; changed authorized sign appears on actual Three.js geometry; reading an address never mutates; operator can unfold the resulting program to admitted primitives. Benchmark compilation and replay over diverse addresses; no unjustified O(1) arbitrary execution claim.

### F. Division IV — Geometry, Physics and Representation: the cinematic image substrate

**University subjects:** Imagistratum, image/preimage/kernel, rank/nullity, projection loss, projective cameras, topology, curvature, spatial tensors, coordinate charts, image formation and invisible sensing.

**DARK work (highest direct visual impact):** Create `ImageAndWorldGeometry` to connect WGS84/ECEF/ENU with a double-precision global world and floating-origin local Three/Rapier coordinates. Define a `PerceptualLOD` compiler with view-dependent distance, screen-space error, silhouette preservation, importance of faces/vehicles, terrain and map uncertainty, collision quality and shader/memory budgets. A projection `π_r` at resolution r must declare what geometry/material/signal is lost. Fine art near the camera can use glTF PBR with KTX2/meshopt; far geometry can use decimated meshes and batched/instanced forms. Photorealistic appearance depends on actual source assets, calibrated material/lighting choices and compositing, not on the word Imagistratum.

For camera/occlusion/interaction use actual projective matrices and `three-mesh-bvh` spatial queries where benchmarked; synchronize collider/terrain geometry with Rapier independently of camera visibility. Give the scene a **camera grammar** for third-person follow, gaze, vehicle interiors, arrival cinematics and comfortable transitions. Distinguish frustum-candidate, unoccluded, rendered-visible, salient and agent-aware. Visibility alone is not NPC mind-reading. Use `3d-tiles-renderer` for licensed 3D Tiles with explicit source provenance and caching rights. The existing global coarse terrain does not certify detailed street topography.

**Visual dividend:** continuous continent-scale spatial precision, plausible close-ups and atmospheric distance, stable camera, believable view-dependent detail and interactive signs/billboards; less popping and fewer floating objects.

**Test:** WGS round trips and date-line/pole edge cases; same building retains dimensions and identity across origin shift and LOD transitions; camera avoids clipping near moving passengers; source mesh GLB loads with normal maps; screenshot comparisons show stable silhouettes, textures and shadows across mobile tiers; collision data readiness gates spawning.

### G. Division V — Acoustic and Generative Sciences: sensory mathematics

**University subjects:** sampling, Fourier/time-frequency representation, phase, envelope, interval cycles, music grammar, synthesis, spatial acoustics, Phonogrammatica as general human vocal-expression mathematics.

**DARK work:** Make `AcousticEventGrammar` produce sound from verified world events: footstep impulse on assigned surface, vehicle speed/gear load, rain intensity and roof occlusion, interior/exterior transitions, traffic distance, ocean waves, instruments and individual actor voices. Use a Web Audio spatial stack with HRTF panners on supported browsers, chosen attenuation curves, convolution/reverb where budgeted, clock-aligned sample events, ducking and readable captions. Integrate already licensed recordings with source hashes and exact rights; original DSP synthesis fills gaps. `MusicClock` may schedule motifs with deterministic event and interval grammar; an optional small model can propose dialogue but may not dictate physical facts. No external corpus is needed for the baseline.

**Sensory dividend:** ears can infer world location/material/proximity, coherent interaction sound and cinema-like atmospherics; silence can intentionally stage attention instead of meaning stalled loading.

**Test:** spectral/loudness/peak and temporal alignment checks, actor velocity → sonic Doppler/attenuation under authored constraints, door closing changes high-frequency energy, rain event changes pavement wetness and footfall samples concurrently; human listening tests sound credible; Android sound unlock/autoplay restrictions handled with user gestures.

### H. Division VI — Computational Worlds and Emergence: living global worlds

**University subjects:** World Loom, cellular automata, GLM/LGM/GWM, agent grammars, simulated populations, navigation, BORNE dependencies, generative environments and HOMELESS itself.

**DARK work:** Preserve the existing authoritative global source data and NPC identities. Implement `WorldLoomScheduler` with virtual/cohort/active/focused tiers; only active/causally relevant agents update individually. Use `recast-navigation-js` for local navmesh, crowd avoidance and dynamic obstacles where it outperforms alternatives. Use a global transportation graph for routing; Recast does not magically provide worldwide roads, aviation or marine network authority. `BORNE` computes dependency cones for traffic, relationships, store behavior, weather and diegetic signage; use bounded propagation with recorded witnesses. `PlateRewrite` transforms typed connected-graph neighborhoods and resolves inhabitants through continuous, physically legal carriage or explicit approved fictional relocation, while maintaining world identity and sound/camera cohesion. `Visit/overlay/braid` remain separate program effects, with loaded destination ready before activation.

**World dividend:** NPCs have commitments and social consequences, a street can be transformed as a playable discovery, and the whole Earth remains geographically addressable without pretending all possible actors and assets are resident in memory.

**Test:** actual walking in a detailed current region; 2+ NPCs continue distinct actions when ignored; visible causal response to one player action; continuous plate transform and inverse with animated passengers; distant region loaded with documented real vs fictional data; snapshots restore relationships and scene position; benchmark active count and CPU time on the device.

### I. The cinematic integration laboratory — six results converging in one scene

Implement a continuous **Tampa wet-night sequence** with the following exact audit trail:

1. Real world cell resolves sourced roads, material candidates, actor schedules and environment forecast/fictional weather status (Division VI).
2. The active environment emits a typed `RAIN_START` event admitted by the state machine (Division I).
3. BORNE traces dependent wetness, footwear audio, headlights, wet surfaces, fog, umbrellas/behavior and vehicle effects (Division VI).
4. ScenePlica composes calibrated pavement/curb/vegetation/façade and reuses verified textures/meshes with coherent region grammar (Division II).
5. Imagistratum maps the scene into LOD-projected meshes/materials and correct camera/lighting passes, declaring projection losses (Division IV).
6. Acoustic grammar positions tires, raindrops, footsteps and room transition sounds against actual world events (Division V).
7. A typed SEURL/PURL-style `SIGN_LIGHT_SHIFT` operation performs a consensual diegetic signage change by an NPC, compiled and admitted before the GPU reflects it (Division III).
8. Show third-person player and moving car in one unbroken native browser capture; provide event trace, asset manifest, average/p95 frame time, source-data attribution, and a separate renderer screenshot/witness list.

Do not let this scenario delay the first playable street. It is a **second visual quality milestone**, built incrementally over the same scene. The expected look is coherent rain/lighting/actors/sound with realistic sourced art; actual result must be measured and reviewed, not declared equivalent to a proprietary AAA engine.

### J. Actual library and implementation leads — verify pinned compatibility before admitting

- Three.js `WebGLRenderer` baseline; optional `WebGPURenderer`/TSL for shaders, fog, post-processing, lights, rain, reflections and GPU-assisted spatial effects **only when features and FPS actually work**. Official Three WebGPU docs note experimental behavior and non-portability of legacy shader/EffectComposer code. https://threejs.org/manual/#en/webgpurenderer and https://threejs.org/docs/pages/TSL.html
- Realistic asset input: `GLTFLoader`, `KTX2Loader`, meshopt and Draco, glTF 2.0 PBR extensions. https://threejs.org/docs/pages/GLTFLoader.html and https://threejs.org/docs/pages/KTX2Loader.html
- Render-cost control: `THREE.InstancedMesh`, `THREE.BatchedMesh`, selective LOD, resource disposal, adaptive DPR, R3F performance measurements. https://threejs.org/docs/pages/BatchedMesh.html and https://r3f.docs.pmnd.rs/advanced/scaling-performance
- Spatial queries/occlusion: `three-mesh-bvh` for geometry raycasting and proximity; it does not substitute for Rapier's physical solver. https://github.com/gkjohnson/three-mesh-bvh
- Physics/movement: `@dimforge/rapier3d-compat` or compatible Rapier entry; Rapier character/controller and vehicle APIs, checked for current version; `ecctrl` is an optional comparison for existing R3F/Rapier character/vehicle/touch integration. https://www.rapier.rs/docs/user_guides/javascript/character_controller/ and https://github.com/pmndrs/ecctrl
- Local navigation/crowds: `recast-navigation-js`, Three integration; test offline build vs runtime generation, character radius, temporary obstacles, crowd CPU costs. https://github.com/isaac-mason/recast-navigation-js
- Source-backed 3D geospatial: NASA-AMMOS `3d-tiles-renderer` with Three.js integration. Its existence does not grant access to a high-fidelity global tileset; respect each source license, cache and offline permissions. https://github.com/NASA-AMMOS/3DTilesRendererJS
- Sound: Web Audio `AudioContext`, PannerNode, ConvolverNode and offline rendering; adaptive mix after user gesture. https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- Optional game-state implementation: dedicated TypeScript ECS or sparse entity stores; benchmark small simple typed maps against ECS before selecting library. Web Workers may precompute graph/shader/asset/physics preprocessing under explicit budgets and abort rules.

**No new spending.** Sources/products are admitted by concrete compatible licenses, actual acquisition, visual validation and on-device performance—not by brand name. Existing Unity-source assets may be converted to glTF only if redistribution rights and import pipelines permit. Avoid substituting low-poly/flat-shaded hero art. Refuse to describe generated sky/roads/assets as source-verified when they are fictionally filled.

### K. Claude Code contributes to Substrate University — evidence, not just narrative

At each executable integration milestone, generate one `UniversityResearchContribution` record with:

```
{ subjectId, divisionId, universityCommit, darkCommit,
  establishedReferences[], constructionDefinition,
  hypothesisOrQuestion, algorithm, inputFixtureHashes[],
  sourceCodePaths[], runCommands[], outputArtifacts[],
  measuredBeforeAfter, nullOrBaseline, limitations[],
  resultStatus, visualWitnesses[], audioWitnesses[],
  proposer: "Claude Code (implementing research agent)",
  review: "pending co-founder acceptance" }
```

Produce `docs/research/contributions/{divisionId}/{experimentId}.md` plus machine-readable JSON in DARK. A generated recipe enters the University research catalogue only after actual tests; an academic status is not promoted merely because an agent wrote it. For example, E-01 `Grammar-Façade` compares number of unique valid storefront programs, glTF bytes and draw calls; E-02 `Imagistratum LOD` compares distance/image loss vs frame time; E-03 `BORNE wet-night` compares recomputation volume after rain; E-04 `NPC Dialogue Act` compares grammar validity, grounding and latency; E-05 `Acoustic Scene` compares event timestamp drift and listener ratings; E-06 `PURL World Program` checks typed round-trip and authorized scene effects. Include refutations and visual defects.

**Cross-repository workflow:** Existing DARK constitutional prompt remains sole executable authority for the GAME. The University's existing books, labels, and co-founder-owned subject registry remain its own identity. Read University source via pinned SHA; do not modify its deploy branch while building DARK. Where user-authorized access exists, stage a separate reviewable university contribution under `docs/research/dark-contributions/` on an independent branch after producing verified results. Never concurrently write to another agent's active university branch, change a University topic's epistemic status without co-founder review, or claim a paper was published just because a Markdown file exists. Export a versioned importable contribution manifest even without that repository access.

**External AI use:** The machine-readable university discovery manifest can list the topic IDs, executable fixtures, extension capabilities and test commands. It cannot turn a one-time Claude session into an always-on professor, guardian or world actor. Contribution is recorded work, not a claim of persistent independent agency.

### L. Execution priority and successful outcome

**The visualization must lead the work.** Begin the existing Section III playable street first, then add the wet-night integrated proof. Parallel workers can inventory and port university subjects while the renderer is being assembled, but no academic audit may block installing Three.js/Rapier, importing actual art, or obtaining the first playable screenshot. The six division inventories can be completed in parallel; implement only the immediately useful adapters first and add research contributions as each actually proves value. Demonstrate one end-to-end event that changes physics, appearance, audible atmosphere and NPC behavior and is explained through all six division traces; then measure mobile performance before expanding the world. Keep original worldwide/Capacitor APK gates intact.

**Definition of success of this section:** (i) all six actual university divisions and their current topics inventoried with source revision; (ii) at least one concrete executable world function per division with a fixture and an in-game witness (possible progressively over increments); (iii) one continuous shared-world wet-night scenario with realistic assets and typed cause/effect; (iv) performance and perceptual results honestly labeled by environment; (v) research contributions importable into the university; (vi) render and mobile APK gates remain in force. An educational exposition without playable visual consequence is `NOT_RUN` for the game acceptance.

## III. The first visual proof — **playable before polished prose**

**Within the first build increment**, deliver a genuine, continuously renderable third-person scene using real licensed/author-created high-quality asset masters: detailed asphalt and sidewalks, region-appropriate façades/storefronts, crosswalk, at least two animated humanoids, moving car, realistic sky and lighting, actual positional ambience and footfalls, camera collision and a player who can walk and turn on keyboard AND touch screen. Include pause, resume and reset to safe spawn. This scene starts near the source-backed Tampa anchor, with an **explicitly fictional** initial café/façade. Ground collisions must track the actual mesh; the character must not fall through unloaded tiles.

Before any extra documentation, run this in a browser and save **actual browser screenshots and a short screen recording** at desktop and Android-sized viewports. The image must contain nonblank rendered geometry. A screenshot of source code, a 3D reference image or a static composited mockup is not evidence. If high-quality art sources cannot be fetched, produce faithful authored alternatives, show provenance, and mark visual review honestly.

**Immediately afterward**, make a WORLD selector or in-world transport menu that can travel to three separated source-backed world locations (e.g., Tampa, London, and a third continent), loads the new coarse terrain and local context, updates geographic coordinates and sky/weather source clock, and preserves player world state. Realistic sourced streets are required only where actual source data exists; never invent missing data as measured streets. Show safe loading and cancel behavior. These locations are examples, not global hardcoding: the same resolver must accept valid coordinates worldwide including oceans, poles and dateline.

## IV. The renderer-independent generative core

Keep these independently testable typed modules with modular imports (names illustrative):

1. `dark-core/world`: authoritative local world state, entity registry, clock, deterministic actions, actor roles, object identity, source provenance and expected-version commits.
2. `dark-core/grammar`: operational `Σ,Q,G,I,δ,denotation,projection,V`, effect permissions, refusal witnesses and Ingrammatica contextual ranking. A legal description is not automatically an enacted event.
3. `dark-core/folds`: Plicastratum certified motifs, exact unfold paths and evidence; recurring patterns can be promoted only after tests. Preserve finite expansion and cost budgets.
4. `dark-core/clock9`: n-gram/glossary-backed proposal and typed small-program compilation; optional local compact language-model connector separated from the core. CLOCK9 proposes; world authority admits. Do not claim neural acceleration without controlled measurement.
5. `dark-core/causality`: BORNE event dependencies, causal cones, scoped observers, deterministic keyed randomness, cancellation, revision and masked effects.
6. `dark-core/protocols`: PURL/SEURL typed address/verb/resolve, pure inspection, authenticated effects, immutable result witnesses, browser-friendly serialization and protocol conformance.
7. `dark-world/geography`: WGS84, ECEF/ENU, local rebasing; authoritative source grids and transport graph overlays. Separate verified geography, model estimates, and fictional plate/portal changes.
8. `dark-world/population`: virtual identities, aggregate cohorts, nearby active NPCs with individually persisted memories and schedules, no massive per-entity JS objects; deterministic promotion/demotion and sparse relationship graphs.
9. `dark-graphics/three`: render graph, camera, sky, PBR asset streaming, instancing, LOD, day/night, water/weather, animation and audio adapters. Rendering never becomes a second authoritative world state.
10. `dark-physics/rapier`: physics bodies, joints and characters, kinematic player controller, seats, wheels and safe relocation; authoritative gameplay action witnesses govern allowed physics effects.
11. `dark-content`: HOMELESS-specific scenes, optional storylets, NPC behaviors, cinematic opening, vehicles, music, ambient events and contributions.
12. `dark-platform/capacitor`: same game built for Android with local assets and source-confirmed remote fetches.

**Seven-strata adapter** remains a documented optional checklist for each computational subject—metastratum, epistratum, superstratum, substratum, hyposubstratum, infrasubstratum, cryptosubstratum—not an assumed cosmic law. No arbitrary numerical symbolism may override tests.

## V. Planetary source data and quality promises

Use the existing pinned global datasets FIRST. Define a `WorldCellManifest` with stable global ID, tile bounding region, WGS84 transform, source release/epoch/datum, provenance/license, terrain LOD, road/building source state, asset bundles and checksums, collision readiness, local active NPC budget, cache status and quality tier.

- **Land/sea:** Natural Earth shape plus GEBCO global relief at its declared resolution; where finer verified elevation is legally available, composite with datum-aware rules. Treat GEBCO as a model with missing precision and do not use it for navigation safety.
- **Roads/buildings/addresses:** use Overture's partitioned transportation/building/address data and explicitly licensed OSM-derived extracts. Query/index only the demanded partitions; build real geometry from measured footprints where available, then add regional authored façades and quality-scored artist assets. Licenses vary, especially ODbL-derived material; produce `licenses.lock.json` and attribution. Existing original Tampa graph is a first fixture, not the universal map implementation.
- **3D tiles:** OGC 3D Tiles via `3d-tiles-renderer` or a verified compatible adapter. Tile-server rights, quota, caching and offline terms must be explicitly checked. A renderer library alone is not a worldwide photogrammetry dataset. Zero-cost core launch cannot depend on a paid map service.
- **Weather and sky:** seeded offline physical approximation with a source-status flag; optional licensed live forecast feed. Real celestial ephemeris/star catalogs where available, epoch-dependent visibility, observer lat/lon and atmospheric limitations. Fictional effects as explicit overlay.
- **Ocean and mountains:** true land/sea boundaries, water surface, terrain meshes with triangle/texture LOD, normal/tangent quality and collision only where geom readiness verified. Oceans and polar regions remain valid world cells, not imaginary roads.
- **Transport:** road, walk, aircraft and marine networks are separate; speed/route constraints and collision readiness are real predicates. Air travel can switch simulation fidelity, then stream target region before landing. A cinematic plane animation is not a tested flight system.

**Reality contract:** A location may be source-backed in one layer and fictional in another. Every visible object has a data-status class: verified, derived/interpolated, authored, or unavailable. Do not claim Google-Earth-equivalent photographic truth, complete interiors, every human resident, or AAA-wide scene detail without source evidence and measurable implementation.

## VI. Art acquisition, animation and quality

Create a `content-lock.json` with per-asset source URL/license/allowed redistribution, file SHA, original format, materials, triangles, LOD status, import status, native render status, and quality reviewer. Categories:
- hero human faces, hair, garments and 25+ everyday actions; independently rigged bodies, correct scale, tracked feet, seated contact;
- cinematic street surfaces, shop windows, masonry, signs, benches, streetlights, urban clutter, plants and trees by biome;
- cars with proper wheels, steering, lighting, doors and at least one usable interior; buses, bikes and trucks;
- aircraft, helicopter, boats and marinas with playable interactions and progressively improved interior completeness;
- terrain/coasts/mountains, foliage, water, weather, clouds, sky, night reflections;
- regional acoustic atmospheres, footsteps, traffic, voice performances and vehicle sounds.

Start by inspecting actually acquired assets and source code in `/assets`, `/data`, and `/unity` of the existing repo **for formats and rights**; the renderer imports supported FBX/OBJ through offline Blender conversion to optimized glTF/GLB. Use original artwork or specifically verified free high-fidelity assets from legitimate suppliers. Do not move restricted masters into a distributable SDK; attach fetch/conversion scripts when redistribution is limited. Generic procedural cubes/capsules are instrumentation, not final cinematic assets.

**GPU fidelity tiers:** low-power device 30 fps target, streamed/static PBR and conservative shadow/reflection costs; desktop richer shadows, post-processing and detail. Record device-specific fidelity tradeoffs. DO NOT use bloom/fog or a static sky to conceal missing close-up detail. Maintain one coherent authored look, not unrelated pack styles.

## VII. Physics and believable agents

Run Rapier with a fixed 60-Hz desired simulation step and measured substep catch-up cap; benchmark whether 30/60 Hz authoritative simulation is preferable on low-end phones. Use WASM feature detection, fallbacks and immutable state packets to render interpolation. Gravity, collision, slopes, stairs, kerbs, foot placement, camera obstacle avoidance and grounded/airborne transition must work. Moving vehicles have checked driver/passenger ownership, safe doors/seats, ordinary traffic behavior and explicit manual/autonomous choice. Scripted cinematic movement may not pass through collision geometry. Implement observation radius, environmental interest levels, speech distance/occlusion and readable NPC behavior.

Implement active NPCs with real schedules/goals/refusals and authored interactions. A globally addressable virtual population can be huge, but live CPU simulation stays limited to active and causally relevant agents with bounded cohort summaries. Every user-visible statement of scope must distinguish identity capacity, measured active agents and worldwide source coverage.

Use a stable schema so a third-party AI or agent can propose typed game actions without running the same code as the renderer. It can observe public facts and make valid requests; independent authorization gates enforce writes. Offline solo gameplay works without agent APIs.

## VIII. First three playable generative mechanics — minimum early proofs under the six-division foundry

Deliver at least **three playable** domain-generation features using actual mathematical kernels, each with visible player effects and reproducible witnesses. These are the early integration proofs; implement the complete six-division subject mapping and progressive demonstrations specified in Section II-A without waiting for every academic topic to be ported:

1. **Plicastratum street walks.** Encode player route into turns/junctions/length features, match source-backed candidate routes across distant regions with a saved tolerance/null baseline; learn a symbolic traversal. Allow an explicitly fictional `visit`, `overlay`, or `braid` transition that truly changes rendered experience, subject to loading and user choice. Use existing checked Plicastratum tests, not only a text paragraph.
2. **BORNE reaction propagation.** A committed local act (help, traffic interaction, NPC social event, authored shop change) has causal dependencies; nearby and distant affected systems recompute only when dependencies change. NPC memories and world cues change; graph/replay verification proves which actions caused which effects.
3. **CLOCK9-authored world operation.** Tiny non-neural grammar generates/chooses a typed world program (light/color/approved sign change, alternate ambient music, admissible navigation cue), validates it, executes safely, records provenance and optionally promotes reusable motifs. Pure n-gram generation is enough for baseline; neural augmentation is optional. The effect must be perceptible in the **actual Three.js world**.

Use one shared `SubjectAdapter` family so external generators can eventually create signs, music, sound, assets, and world behaviors, but implement concrete primitives with tests first. Rendering quality is independent from generative proposal validity.

## IX. Android installation and packaging

The same web source must build and run in:
- desktop Chrome/Firefox (document versions);
- Android Chrome mobile browser;
- **Capacitor Android debug APK** using locally generated Gradle/Android project with no app-store signing credentials required.

Prefer a supported Android SDK/JDK/Gradle path in Claude's actual environment. If not present, implement `npm run android:prepare` and `npm run android:build` plus a **zero-new-cost** Android GitHub Actions build workflow with a reproducible lockfile and artifact upload (no production signing keys). Keep the job under repository-owner approved workflows and current free quota; never activate paid compute without explicit permission. Bundle playable offline opening and WASM runtime assets; remote tiles use versioned manifests, bounded disk cache, expiry and observable failures. Test Android back-button, app pause/resume, orientation, audio focus, WebGL context loss, touch controls, minimum storage, and network interruption.

Measure Browser vs APK on the same phone. An APK is not a claim of native graphics acceleration beyond what Android WebView offers. If a genuine native renderer profile becomes useful, evaluate it only as a separate evidence-based experimental adapter after the web+Capacitor route is playable.

## X. Test program and evidence

**Tests are executed behavior, not wishes.** Use Vitest/Node for portable contracts, Playwright with real Chromium WebGL for graphics integration, and Android instrumentation/ADB on any actually accessible device. Report `PASS`, `FAIL`, `BLOCKED` or `NOT_RUN`, with command, environment, revision, artifact and screenshot hash.

**Required numeric/math tests:**
- deterministic CLOCK9 baseline (22 previously executed checks), world-engine contract (7), BORNE (16), Plicastratum (13); rerun from bundled original sources or port fixtures after importing them;
- WGS84 geodetic↔ECEF↔ENU roundtrips including poles, ocean, high mountains and antimeridian; distance/error bound explicitly specified;
- Rapier ground contact/settling, collision groups, kinematic player slope movement, fixed-step replay under seeded fixtures;
- fold/unfold identity and finite expansion, typed grammar refusals, prefix-address roundtrip, no write from reads;
- causal graph propagation, saved/restored NPC identity across tile retirement and return, selected actor replay;
- tile load ordering; cancellation/disconnect/duplicate response; availability and collision readiness before spawn;
- recorded source-to-display provenance, missing map details never represented as verified geometry.

**Required real Three.js/browser integration tests:**
- actual `THREE.Scene`, `PerspectiveCamera`, `WebGLRenderer` and a GLB asset imported successfully;
- visible shaded geometry pixels in a WebGL screenshot, not a black/blank frame;
- raycast intersects a known street collider and not a hidden/non-interactive object;
- `InstancedMesh` transforms correspond to physics/canonical source objects;
- textures/geometry and 3D tiles disposed/evicted without growth beyond declared memory budget;
- context loss/recovery; screenshot of day and night PBR, rain, two animated humans, one moving vehicle;
- third-person keyboard and touch movement, arrival, conversation and learned world transform;
- continent-to-continent terrain transition with measured source metadata and target cell readiness.

**Performance gates:** set budgets from actual device memory/GPU and verify on phone, not emulator alone. Provisional mobile target **sustained 30 fps; p95 ≤ 33.3 ms** over a 10–20 minute representative route at the chosen adaptive tier. Record resolution, tier, p99, thermal state, peak heap/GL allocations, network bytes, tile latency, hitch intervals and audio glitches. Benchmark WebGL2 and WebGPU only on devices that support both. Smoothness, fidelity and download size are distinct axes. When not measured, report `NOT_RUN` rather than fabricated values.

**Visual gate:** continuous gameplay recording at user-visible quality, inspected close-up PBR textures and character deformations, camera, traffic, lighting and atmosphere. Do not claim photorealism by shader names or asset screenshots alone.

**Global gate:** coordinate resolution anywhere, source-backed world surface, sampled worldwide safe transfers, land/ocean and elevation tests, geographic coverage report. Detailed world photo-accuracy and every building's interior are explicitly separate unsatisfied gates until actual data proves them.

## XI. Immediate execution order for the NEXT Claude Code Cloud run

0. `git status`, branch, origin and current checkpoint; confirm active HEAD. Preserve previous tested work, commit history and any concurrent edits. Read `CLOCK9` and `BORNE` sources when available and re-run their tests. Do not wait on historical attachments that aren't mounted.
1. Write this as the one **active** `HOMELESS_DARK_WEB_CONSTITUTION.md` (v2), commit normally and mark previous renderer-specific requirements superseded in one short `docs/renderer-migration.md`. Historic specs remain archival evidence, not operative instructions. Determine selected npm versions from current upstream compatibility; write lockfile. Pin current Substrate University repo SHA and start the complete six-division subject inventory in parallel with visual startup (Section II-A).
2. Bootstrap `apps/homeless-web` and `packages/dark-*` TypeScript monorepo modules with Vite, React, Three, React Three Fiber, Rapier, assets, input and world-state. Make `npm run dev` work as early as possible and fix actual errors. Add meaningful npm scripts `test`, `typecheck`, `build`, `test:e2e`, `android:prepare`, `android:build`.
3. Import initial cinematic source art, actual camera, locomotion, lighting, physics, audio and keyboard/touch controls. Produce first **real** browser screenshot and short recording, inspect artifacts and fix flaws. Do not stop at code generation.
4. Wire source-backed initial geography, global coarse Earth view, source manifest, new-world location selection and continent transfer. Show real streamed world visuals at multiple continents under valid source-resolution constraints.
5. Wire actual NPC interactions, travel/vehicle modes, event witnesses, Plicastratum/BORNE/CLOCK9 perceptible mechanics and the six-division foundry adapters. Implement each through one concrete before/after playable scenario and tests.
6. Ship first actual Android debug APK from the same source via local Android build or free available CI. If environment lacks Android build, record exact tool prerequisite and deploy tested web URL while completing independently actionable tasks. Never rename source code as an APK.
7. Capture screenshots and clips from actual browser and any actual APK run; record six-division research contribution manifests with verified artifacts, keep image and source hashes with a concise capability report. Commit tested work and leave a clean resumable checkpoint only after significant executable progress.

**First acceptance checkpoint:** I can open HOMELESS on a URL, move a high-quality character through a genuinely rendered street with real collision, see/approach another active character, hear spatial audio, and travel to another globally addressed location while the scene streams without losing control. This experience must be built before expending most of the session on documents, research lists or dashboards. This is an incremental proof, not a claim that every worldwide AAA surface is already complete.

**Second acceptance checkpoint:** Same game launches as a locally installable debug APK; tested native Android behavior and measured quality are reported truthfully.

**Ultimate commission:** worldwide, high-fidelity, generatively evolving HOMELESS powered by the renderer-neutral DARK engine, preserving all playable world, transport, social, sky/audio, programmable-language and source-data obligations. The incremental deliverables do not reduce this target.

## XII. Completion response contract

Report (1) playable URL and controls, (2) real screenshots/recordings with exact commit, (3) which worldwide data is ingested vs missing, (4) passing/failing tests actually executed, (5) Android APK path + SHA256 if built, (6) known visual and performance limits, (7) actionable outstanding work, and (8) source commits. Give exact evidence, no arbitrary completion percentage. A successful program build does not mean a complete world, and a failed APK build does not negate verified world-engine progress.

**Execute the work now. The game must become playable.**
