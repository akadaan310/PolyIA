# ASTRA/ATOM v0.1 — Executed verification report

## Results observed in this session

- Python deterministic core + driver: **23 unit tests PASS** (see `evidence/unit_tests.txt`), including malformed inputs, ledger tampering, checkpoint chaining, content-addressed source archival, headless multi-atom execution, no-execution dry-run, and restricted command kinds.
- Headless no-LLM plan: **5 atom jobs CHECKPOINTED** — science, journey, rendering, focus, simulated economy. Each phase was run in-process by the explicitly invoked driver, with `verify()` after every step. `evidence/headless-execution.json` contains typed outputs, receipts, source checkpoints and final machine report. `evidence/headless-verification.json` checks the journal.
- Chromium visual interaction: **10/10 checks passed**, two separate clean isolated runs, 0 console/page errors. Actual canvas rendering, API communication, machine registration, two checkpoints, resumption, spring input, focus proxy, mobile dimensions and report verification. See `evidence/browser_report.json`. Screenshots: `astra-desktop.png`, `astra-interaction.png`, `astra-mobile.png`. The GIF `astra-wave-motion.gif` consists of **16 actual browser frames**; capture overhead prevents using its frame intervals as a frame-rate benchmark.
- Browser HTTP navigation is **blocked by administrator policy** in this execution environment. For verification, Playwright injected identical page sources into `about:blank`; the UI's JavaScript fetch calls were bridged through Python to the actual loopback HTTP server. This proves UI logic and backend interoperability under the test bridge, not production navigation/security/network behavior.

## Explicitly not verified / not implemented

- No actual eye-tracking or cognitive-state inference. The focus cursor is a pointer/idle heuristic.
- No WebGL/WebGPU physics-based optics, actual plasma simulation, quantum machine, or physically accurate orbital travel. Canvas2D field waves and CSS plate springs are interactive demonstrations.
- No Gaia billion-source ingestion, full planet ephemeris, NIST line-import backend, or Isnad corpus/audio plugin mounted.
- No live Codex / Hermes / OpenClaw instance or purchased cloud computation. The driver is *deterministic and model-free*.
- No real-money token sale, Bitcoin network, payment gateway, blockchain wallet, or exchange functionality.
- No formal third-party attestation, digital signature, or crash-atomic multi-file transaction guarantee for checkpoints.
- No Samsung Galaxy A16/Android APK or other physical-device benchmark; Chromium mobile viewport is simulated.

This report does **not** classify the system as commercially deployable or security hardened.
