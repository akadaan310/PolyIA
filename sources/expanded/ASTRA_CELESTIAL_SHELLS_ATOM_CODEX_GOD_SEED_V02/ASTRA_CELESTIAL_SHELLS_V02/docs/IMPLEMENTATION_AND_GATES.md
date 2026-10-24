# ASTRA Celestial Shells v0.2 — Implementation map and gate ledger

| Feature | Implementation | Verification | Status |
|---|---|---|---|
| 3D spherical coordinate projections | `web/sky.js` | Node geometric assertions; browser selected object | PASS for CPU |
| Four expandable layers | `SkyEngine.expand/contract` | Browser desktop/mobile | PASS |
| Celestial object inspection | `SkyEngine.pick` / `selectHandler` | Browser Jupiter selection | PASS for sample |
| WebGL2 point shaders | `web/star-gpu.js` | static JS syntax; real GL context unavailable | NOT_RUN GPU |
| Canvas2D fallback | `web/sky.js` and `web/app.js` | Chromium screenshots | PASS |
| Plasma/functional wave independent canvas | `web/app.js` | inherited renders; screenshots | PASS |
| Seven-source spatial oscillator synthesis | `web/audio.js` | browser AudioContext and voice count | PASS (initialization) |
| Measured acoustic quality / phone loudness | pending | requires calibrated playback / analyzer | NOT_RUN |
| Original audio WAV assets | `audio_assets/*.wav` | generated PCM file headers / peak samples | PASS source creation |
| JPL live planetary views | planned | API + observer time transform | NOT_RUN |
| Gaia billion-star backing data | planned | tiled ingestion + source snapshots | NOT_RUN |
| ATOM checkpoint controller | `atom/` | 23 inherited tests | PASS |
| ATOM source snapshot includes new modules | `atom/core.py` | source archive tests | PASS |
| Cross-machine signed checkpoints | planned | cryptographic trust anchors | NOT_RUN |
| Android native GPU p50/p95 | planned | physical device trace | NOT_RUN |
| Real eye tracking | excluded by design | only pointer/idle focus proxy | NOT IMPLEMENTED |
| Real-money/token sale | excluded | play credits only | NOT IMPLEMENTED |

The Codex master commission is in `handoff/CODEX_GOD_SEED_V02.md`. The initial ATOM harness remains deliberately bounded. All speculative celestial locations are explicitly marked MODEL.
