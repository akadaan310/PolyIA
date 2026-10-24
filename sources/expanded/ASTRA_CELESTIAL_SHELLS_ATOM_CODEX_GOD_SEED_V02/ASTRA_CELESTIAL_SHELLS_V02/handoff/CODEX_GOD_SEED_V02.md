# ASTRA UNIVERSAL TRAVERSALS — CELESTIAL SHELLS / SONIFICATION / ATOM COMMISSION

**Version:** ASTRA-CELESTIAL/0.2 — engineering commission for Codex or another tool-enabled harness.  
**Commissioning creator:** Abed Kadan.  
**Project:** ASTRA · Universal Traversals. Its universal state/orchestration framework is ATOM.  
**Authority:** This file governs continuation within the extracted `ASTRA_CELESTIAL_SHELLS_V02/` workspace; it does **not** grant authority to rewrite any external Isnad, PURL, Qur'an, Astro, TRE, or HOMELESS project.  
**Status:** Executable reference increment; not a shipped universe-scale game, WebGL benchmark, Gaia ingestion, commercially verified asset library, or native mobile app.

## 0. Read this before doing anything

The task is an **end-to-end working scientific universe/game experience**, not a proposal, collage, screenshot-only product, or synthetic demonstration mislabeled as science. Inspect the implementation and run its current tests before editing. The user provided real mobile screenshots of Isnad with stitched constellation shells, a navigational flight-management computer, and a motion-heavy astronomical interface. Those screenshots establish interaction and aesthetic targets; *no Qur'anic text, recitation, or Isnad-specific sacred domain semantics are required for ASTRA*. Import only general-purpose behavior with permission and attribution, not arbitrary source snippets or private data.

```
cd ASTRA_CELESTIAL_SHELLS_V02
python -m unittest discover -s tests -v
node tests/test_sky_node.cjs
python -m atom.cli --root .atom-state teach   # if clean root, initialize state safely
python -m atom.server --project . --port 8765
# http://127.0.0.1:8765
```

First, inspect `README.md`, `docs/SCIENTIFIC_AND_AUDIO_CONTRACT.md`, `docs/IMPLEMENTATION_AND_GATES.md`, `atom/core.py`, `atom/driver.py`, `web/sky.js`, `web/star-gpu.js`, `web/audio.js`, and `evidence/browser-checks.json`. Review the exact current source and run tests locally. Create a fresh branch. Do not destroy prior source checkpoints or falsify browser evidence. Use no paid services or copyrighted media without a verified grant.

## 1. Governing success condition

Create an **interactive planetarium/travel game** with a first-class programmable celestial universe, deterministic state-machine operations and checkpoint integrity, and extremely responsive graphical and auditory feedback. The same world structure must support web/mobile/desktop adapters; browser delivery is the first accepted target. Never promise 60 FPS without real hardware measurements. Use the small current model with explicit provenance until Gaia/Horizons are integrated.

You must deliver source code, tests, accessible runtime, actual browser render screenshots, scientific source/manifests, measured frame pacing, generated/licensed audio, a signed-off feature matrix (PASS/FAIL/NOT_RUN), and the current ATOM checkpoint report.

## 2. Formal model: celestial state is not the screenshot

The minimum world state is

```
Universe = (Corpus, Frames, Entities, Geometries, Signals,
            Viewports, Journeys, Automata, Evidence, Epoch)
Entity   = (id, kind, provenance, frame, position_or_direction,
            timestamp, uncertainties, displayGrammar, audioGrammar)
Plate    = (id, renderer, depth, opacity, worldTransform, clipping,
            dependencies, budget, drawPasses)
Journey  = (sourceObserver, targets[], schedule, transitionProgram,
            referenceFrame, replayLog)
Atom     = (id, type, state, allowedInputs, guardedTransition,
            evidence, resources, parent, checkpoint)
```

All functions and communication paths are typed. Structured data MUST distinguish measured, catalog-derived, ephemeris-derived, computed, illustrative, synthetic, and unknown. Save data provenance and computational formulae. A measured star direction with unknown distance is a *direction*, NOT a real nearby 3D coordinate. A black hole's possible sonification is a model, not sound physically traversing the vacuum. Unknown extrasolar planet climates, weather, geometry and black-hole internal worlds are fictional until supported.

Use typed resource IDs and coordinate frames. Always carry frame and epoch. ICRS/J2000 star RA and Dec become a unit direction vector:

```
V(α,δ) = (cosδ sinα, sinδ, cosδ cosα)
```

Never collapse angle-only stars into actual XYZ stellar positions. With Gaia parallaxes, validate parallax quality, estimate distances using a documented model (not naive inversion for noisy/nonpositive parallaxes), carry uncertainty; then convert to barycentric or Galactocentric coordinates with explicit conventions. Solar-system geometry should come from JPL Horizons or an equivalent pinned ephemeris at a real timestamp, using a declared observer and requested frame. NASA information is not implicit endorsement.

## 3. Geometry: stitched, expanding, recursive shells

Implement a spherical spatial language (SHELL/0.1): each shell is a typed 2D manifold embedded in 3D with `radius`, `frame`, `epoch`, `angular grid`, `topological links`, `LOD`, `materials`, and `render passes`. Neighbor relations are not physically established constellation shapes unless they have specific cited reference data. Separate: 1) ICRS measured star positions; 2) graph edges derived by stated visual algorithm; 3) designed artistic mesh; 4) physical orbits. The current bright sample consists of only 20 directions; annotations and synthetic dust must be labeled accordingly.

Give player-visible tiers: **Inner Observatory → Local Constellation → Solar Neighborhood → Galactic Structure**. At each expansion, keep current selection and context, stream detail by budget, avoid popping/jitter, and compose neighboring shells into a consistent spatial map. Allow inward/outward movement, perspective rotation, object focus, orbit, slow cinematic auto-tour, and inspection. Use hierarchical spatial indexing (HEALPix or equivalent for sky directions; octree/BVH for true XYZ) and tile streaming when catalog size grows. Millions/billions of points CANNOT be resident as one JS array on a phone. Snapshot and resume camera path and object selection.

Current prototype: `web/sky.js` implements a tested 3D projection to Canvas2D plus an optional WebGL2 shader point pass in `web/star-gpu.js`; no shader in this file was actually verified on a working GPU in the first test environment. Your first rendering gate is to run this on a real WebGL2 context and a real Android GPU, compare to fallback, and collect actual screenshots and frame-time quantiles. Build improved GPU-resident BufferGeometry/instancing, batching, quality tiers, floating origins, and context-loss recovery. Do not rewrite the stable Canvas fallback until GPU parity tests pass. Preserve raw evidence.

## 4. Travel / flight-management computer

All visible objects support a unified inspection and targeting API. Clicking a planetary marker, a telescope target, an orbit, or a synthetic object produces a structured selection (`id`, `provenance`, `frame`, `time`, `uncertainty`). Implement route planning and travel as a *state machine*, not blind camera tweening. Proposed journey phases:

```
IDLE → TARGETED → PLAN_VERIFIED → DEPART → TRANSIT → ARRIVE → OBSERVE → CHECKPOINT
```

If a target lacks real ephemeris, permit clearly marked demo motion and never generate unsupported astronomical coordinate claims. Distinguish instantaneous visual shift from physically feasible travel (time of flight, relativistic/propulsion effects and actual spacecraft planning are not claimed). Give the user a route overview and undo via checkpoints. Include planets, representative moons, asteroid targets, ISS only when observational data actually permits a current position, Galactic Center as direction, and real Gaia stars subject to distance uncertainty. Handle near-Earth local sky and planet-local skies by transforming an observer vector, not by relabeling an Earth viewpoint. Preserve an optional adapter for user-specified path waypoints. Every journey can be exported as a typed event trace.

## 5. SOUND/0.1 — astronomical grammar and signal calculus

Audio is an interpreted data channel and an artistic instrument: **no sound propagation through vacuum is asserted**. Build typed source feature vectors `F = {brightness, spectralClass, orbitalFrequency, skyLongitude, angularVelocity, spectralFlux, spectralCentroid, temporalEvents, confidence}`. A configurable synthesis mapping `A : F -> (pitch, harmonicity, envelope, gain, pan, filter, spatialPosition, reverberation)` is explicit, testable, and reversible only where the mapping is injective or retains auxiliary evidence. The listener can inspect why a sound was heard.

Use Web Audio `AudioContext` activated only by an explicit interaction, oscillators + filters + envelopes + `AudioWorklet` as appropriate, `PannerNode`/`StereoPannerNode` with stable listener location, optional impulse responses, low-frequency atmospheres and authored effects. Start with seven diatonic classes C,D,E,F,G,A,B, extend across octaves using `f(n) = f0 * 2^(n/12)` for equal-tempered semitone offsets; *seven named scale degrees are not seven notes per octave in the sense of the twelve-tone equal-tempered chromatic system*. The current reference starts seven voices and supports pan and soft timing. Derive spectral intensity envelope and celestial mappings without pretending measured astronomical sounds are acoustic wave recordings.

Volume calculus: default moderate output, gain automation with smoothing, user mute and independent ambience/effects/music controls, compressor/peak limiter, and no abrupt jumps. **Do not require users to maximize device volume or circumvent OS-level user control.** Prove headroom with offline-rendered waveforms, report clipping percentage and peak/RMS; support loudness and distance without high playback level. Respect OS media playback and audio focus. Prefer original synthesized samples; inspect NASA and other archives for recordings only with source URLs and exact redistribution rights, no implicit inclusion of third-party media. `audio_assets/celestial-drift.wav` and `portal-chime.wav` are generated by the project and do not require third-party attribution. Audio must stay smooth while navigations or render frames are slow; never clock verse or sample boundaries from requestAnimationFrame. Audio performance measured independently.

Programmatic audio actions: `audio.enable`, `audio.disable`, `audio.travel`, `audio.focus`, `audio.emission`, `audio.mute`, `audio.snapshot`. For celestial classes define grammars for stars, atmospheres, dust, moons, asteroids, and speculative modeled exotic objects. Physical weather sound applies only to supported atmosphere simulation; label fictional weather.

Optional vibration: `navigator.vibrate` only after user gesture, support check, rate limit, reduce-motion and opt-out settings; fall back silently when unsupported. Provide a haptic event grammar independent of audio; haptics should never be required to understand the UI.

## 6. ATOM/0.2 — micro-automaton semantics and project-building state machine

The existing controller `atom/core.py` has `OBSERVE → PROPOSE → ADMIT → EXECUTE → VERIFY → CHECKPOINT → HOLD → OBSERVE`. A transition is a typed, bounded result with a deterministic verdict. A locked checkpoint contains content-addressed source archives, a parent hash, and the machine's state. This is **local integrity**, not tamperproof identity. Build an ASTRA-specific intent bus that can optionally ask ATOM for admission; allow fast read-only UI transitions without blocking each animation frame on disk operations. Persistent world changes, expensive computations, paid tokens and source writes go through guarded operations.

Micro-atom classes: `WORLD`, `SHELL`, `VIEW`, `JOURNEY`, `SOUND`, `LIGHT`, `FIELD`, `WEATHER`, `PHYSICS`, `EVIDENCE`, `CHECKPOINT`, `ECONOMY`, `BUILD`, `TEST`, `REVIEW`. Every atom has a self-API: inputs/outputs, permission requirements, machine state, lineage, resource budgets, code hash, and test contract. Register atomic grammar in JSON Schema or an equivalent typed manifest but do **not** require every computation to be written as an interpreted JSON program. The UI is a realization of the underlying compiled/typed program and engine state.

The game-theoretical decision policy may use a declared payoff matrix, a maximin/minimax strategy or robust resource allocation, but it never overrides authorization or physics. Distinguish strategy optimization from formal verification. A proposal from an LLM or agent must be interpreted as untrusted data, typechecked, simulated where possible, and admitted only by the owning machine.

### Automaton-to-automaton exchange

For tools/LLMs/Codex, carry the typed envelope:

```
{
 "protocol":"ATOM-HANDOFF/0.2",
 "machine_id":"...", "parent_checkpoint":"sha256:...",
 "operation":"...", "phase":"OBSERVE|PROPOSE|...",
 "input_digest":"sha256:...", "evidence":[],
 "candidate_transition":{ "preconditions":[], "effects":[], "budget":{} },
 "verdict":"PROPOSED|ADMITTED|PASS|FAIL|NOT_RUN",
 "checkpoint":null, "next_actions":[...]
}
```

Handoff messages do not carry authority merely by referencing a resource. Use explicit approvals for remote actions, credential use and charges. Sandbox all third-party code; never silently execute arbitrary shell commands from generated content. The harness is a tool **without** a model by default and accepts independently authorized LLM adapters. Expose the same self-inspection API to agents and UI. Support optional PURL addresses and SEURL affordance and state-diff projections once proven, not by guessing unvalidated endpoints.

### Harness clock / build lifecycle

```
DISCOVER → SOURCE_LOCK → FORMALIZE → BUILD → TEST → VIEW → SCIENCE_REVIEW
→ CHECKPOINT → RELEASE_REVIEW
```

At each phase:
1. invoke a bounded CLI script rather than narrating tool output;
2. collect source hashes, test result, raster capture if applicable;
3. compare against criterion, issue PASS/FAIL/NOT_RUN;
4. on PASS lock the checkpoint; on FAIL stop this lane and preserve failure, continue independent lanes;
5. publish concise machine-readable delta for the next agent.

A checkpoint is immutable and replayable, but successors can branch and supersede prior implementations through explicit lineage. Never silently overwrite an earlier checkpoint. Provide a visible outer shell that lets users see provenance/checkpoint motions without covering the celestial universe. Preserve the existing ATOM controller until improved unit/e2e coverage demonstrates parity.

### Game product and economy

Design the first-class travel game as free exploration, scientific exhibits, collectibles earned for verified discoveries, and replayable voyages. Future computation tokens are *only a concept*; `ECONOMY` remains a simulated, non-redeemable ledger until actual payments, pricing, legal compliance, consumer protection and fraud prevention are separately reviewed. No crypto mining, token issuance or financial transaction is authorized by this commission.

## 7. Corpus and astronomical science

Progressively integrate (with versioned data manifests):
- Hipparcos directional samples already licensed and included.
- Gaia DR3: ~1.81 billion source rows; use TAP/ADQL for bounded samples, partitioned HEALPix tiles, density/LOD hierarchies and checksums, not a client-side full-catalog load.
- JPL Horizons: observer/state vectors at specified epoch/time scales; cache with provenance, uncertainties and correct center.
- optional TLE/SGP4 as time-sensitive **estimated** ISS positions, with source freshness, not long-lived hard-coded orbits.
- NIST spectral databases for wave and light exhibits, physical feature extraction with emission vs absorption, ionization and source conditions.

Never conflate a computed sinusoid with experimentally measured light or periodic chemical identity. Split scientific modes from fantasy modes at the data level. Every number on screen must be either source-backed, computed from sourced parameters, or labeled synthetic. A billion-scale Gaia backend is a separate major integration that is NOT implemented in v0.2.

## 8. Visual design and experience

Preserve the existing nocturnal navy/teal/gold language. No generic dashboard or button wall should dominate the sky. Borrow interaction patterns (not assets/content) from the user-shared Isnad screenshots: camera inside nested star shells, spherical netting, slow glowing connections, constellation-like clusters, surgical crosshair, uncluttered overlay, motion-continuous flight panel. Implement depth-aware glow, volumetric-inspired fog, directional labels which never overlap excessively, detail expansion on approach, optional alt/az sky grid, one-handed mobile controls, quick bookmark/return, accessible high-contrast labels, reduced-motion support. Keep audio and movement coherent; single tap focuses, drag rotates, pinch/wheel traverses, long-press opens object context. No eye tracking; optional attention inference is pointer-based and labeled.

Render plates have independently ownable draw and visibility state, with explicit depth and priority. Waves, spectra, constellation geometry, orbital trajectories, labels, particles and focus rings are different passes. Modern WebGL2/WebGPU GPU work must be grounded in actual tests. A scientifically meaningful star point and an artistic faint dot are visibly distinguishable on inspection.

## 9. Implementation sequence / actions Codex MUST take

**A — Recover & freeze:** reproduce baseline 23 Python tests, 14 JS assertions, 16 browser checks, check license/manifest, make new checkpoint. Document source tree and current limitations.

**B — Rendering:** open browser with actual WebGL2 hardware if available. Fix WebGL shader/link/orientation/parity, add real GPU screenshot and mobile p95/memory evidence; keep CPU fallback. Optimize the spherical wireframe and intelligent labels. Add procedural shell fixtures and real ICRS projection unit tests.

**C — Audio:** measure 7-voice synthesis in browser, inspect recording with AudioWorklet/OfflineAudioContext, add file-playback and safe mix envelopes, accessible media activation, stereo/spatial movement tests, optional haptic; gate on hearing comfort and click/peak limits, not maximum loudness.

**D — Astronomy:** integrate bounded Gaia tile ingestion, JPL Horizons observer vector end-to-end, at least a real observer-time sky scene for Earth and another supported body; show provenance, coordinate transforms and scientific uncertainty.

**E — Micro-automata:** unify UI intent with ATOM events; typed handoff, manifest discovery, checkpoint + replay of same journey/audio state; independent headless execution, timeout and code ownership policies.

**F — Multiplatform:** responsive phone/browser, installable PWA, offline fixture set, optional Android wrapper only after realistic GPU/frame measurements and permissions. Desktop/web first, then APK/IPA on supported build infrastructure; do not claim an APK exists when it does not.

**G — Game:** convert demonstrations to a journey loop with discovery goals, research cards, optional comparison of spectra and orbits, checkpointed progression, repeatability and onboarding. No enforced monetization.

**H — Release audit:** run all unit, integration, browser, audio, physics, math and device-specific gates, output honest PASS/FAIL/NOT_RUN and an artifact list. Ensure no stale status from previous research reports.

## 10. Acceptance gates (fail closed)

- S1: retained ATOM regression tests green, no checkpoint/replay changes without cross-version tests.
- S2: star directions and reference-frame math tested at poles, wrap-around, and several epochs; no fictitious distance presented as measured.
- S3: screen shows an evident *nested sphere*, and expansion/retraction keeps selection and creates reproducible camera traces.
- S4: GPU shader compiles and actually produces pixels on at least one real supported WebGL2 device. If not: GPU NOT_RUN/FAIL, fallback separately PASS.
- S5: browser desktop + phone screenshots, object selection, pointer/gesture and journey check; capture real frame-time p50/p95 and missed frame ratio with hardware details.
- S6: audio requires action, starts at conservative gain, soft stops/crossfades, no clipping in encoded samples, master mute and independent source control; spatial movement verifiable.
- S7: scientific labels and data hashes reviewed, JPL and Gaia contents verified; synthetic and real geometry remain disjoint.
- S8: all significant events typed and checkpointed; report and replay can be read by another harness without missing hidden state.
- S9: bundle contains a release-ready README, generated original/licensed media, operational run commands, explicit blockers, and every claim backed by test output.

Success is continuous functioning software with proof of each gate, not a numerical percentage. If a lane cannot finish in the current execution environment, preserve a buildable checkpoint and record blockers explicitly. Do not stop at a God Seed when actual implementation can continue.

## 11. Canonical upstream reading

- https://github.com/akadaan310/isnaad (study the WebGL/FMC implementation style; read-only)
- https://github.com/akadaan310/QuraanImmersion (read-only audio/GLSL clock architecture)
- https://github.com/akadaan310/abedkadaancom (Substrate University mathematical registry)
- https://github.com/akadaan310/purl and https://github.com/akadaan310/seurl (protocols, read-only)
- https://gea.esac.esa.int/archive/ and https://www.cosmos.esa.int/web/gaia/dr3
- https://ssd-api.jpl.nasa.gov/doc/horizons.html
- https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API
- https://www.nasa.gov/nasa-brand-center/images-and-media/ (NASA media usage limitations)

## 12. Completion report format

Provide: last committed hash; direct local launch command; screenshots and exact environment; mathematical results; GPU status; audio measurement status; ATOM parent checkpoint + newest checkpoint; all source data licenses; explicit PASS/FAIL/NOT_RUN; open bugs; independent next valid transition. Report honest unsolved blockers. Cite linked source implementations and user code with proper provenance. Never say 'complete game' until acceptance gates are met.
