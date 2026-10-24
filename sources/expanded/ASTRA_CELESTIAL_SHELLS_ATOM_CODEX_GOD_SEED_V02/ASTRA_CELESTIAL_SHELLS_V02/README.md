# ASTRA — Universal Traversals / Celestial Shells v0.2

A runnable, local, state-machine-backed celestial game lab with real 3D coordinate projection into a stitched sky-shell view, four levels of celestial expansion, selectable stars and illustrative planets, an independent moving plasma field, interactive flight console, programmatic seven-note spatial sound, and the retained ATOM checkpoint controller.

## Start

Requires Python 3.11+. No Node package installation is necessary to run the web prototype.

```bash
cd ASTRA_CELESTIAL_SHELLS_V02
python -m atom.server --project . --port 8765
# On the same device, open http://127.0.0.1:8765
```

The backend is loopback-only and unauthenticated; never expose it to a public network without hardening. On Android with Termux Python, run the command in Termux and visit localhost with the same device browser. No APK or IPA is provided.

## Play

- Rotate celestial shell by dragging, tap a celestial body to inspect, scroll or press **EXPAND/CONTRACT** to shift shell scale. Four authored shell scales illustrate deeper spatial views; they are not real radial distances.
- Pick Mars, Moon, Jupiter, Saturn, Neptune, ISS, Earth, or Galactic Center direction in Traveler console, then tap **ENGAGE CELESTIAL SHIFT**. Other than the Earth reference, destinations are modeled and do not use live JPL ephemerides. The 20 HIP catalogue nodes use reported sky directions, while their radii are illustrative.
- Enable sound with a tap; it starts at a reduced gain with a compressor, and offers a master mix control and mute. Headphones help spatial perception but are optional. You do NOT have to maximize device volume.
- ATOM states remain separate from render frames. Admit an atom, advance through each verification phase, and checkpoint. Read-only view gestures are not persistent world changes.

## Verify

```bash
python -m unittest discover -s tests -v
node tests/test_sky_node.cjs
python -m atom.driver --project . --plan examples/mission-plan.json --state .atom-test-state --execute
python -m atom.cli --root .atom-test-state verify
```

The visual browser tests are recorded in `evidence/browser-checks.json`; browser navigation and WebGL2 were restricted in the present environment. The existing Canvas2D fallback worked in Chromium, but GPU acceleration on a real phone is **not certified**. Data corpus counts are **20** HIP sampled bright directions and ~hundreds of artistically synthetic dots, not Gaia DR3 billion-scale ingestion.

## Source and continuation

- `web/sky.js` — native 3D shell geometry, rotating frame, angular mapping, selection and four expansions.
- `web/star-gpu.js` — optional WebGL2 star points (GPU execution not verified on present host).
- `web/audio.js` — live WebAudio synthesis, filter/pan/gain, compressor, mute, bounded chimes.
- `audio_assets/` — two entirely original procedural WAV samples (distributed in ZIP).
- `atom/core.py` — typed micro-automata, guarded transitions, Merkle-style content-addressed source snapshots and replay checks.
- `docs/` — scientific/source status, audio safety and engineering gates.
- `handoff/CODEX_GOD_SEED_V02.md` — full self-contained Codex commission with implementation order, test gates, and independent harness lifecycle.

The prior ASTRA, Isnad, PURL, Qur'an, TREE and Homeless repositories were not modified. No paid datasets or external audio were embedded. Provenance must accompany every future source.
