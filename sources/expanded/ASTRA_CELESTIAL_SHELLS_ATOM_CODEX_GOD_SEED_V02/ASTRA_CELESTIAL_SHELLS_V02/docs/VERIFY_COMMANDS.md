# Verification runbook

```bash
cd ASTRA_CELESTIAL_SHELLS_V02
python -m unittest discover -s tests -v
node tests/test_sky_node.cjs
node tests/test_intent_bus.cjs
python tools/audit_sound.py
python -m atom.driver --project . --plan examples/mission-plan.json --state /tmp/astra-atom-e2e --execute
python -m atom.cli --root /tmp/astra-atom-e2e verify
python -m atom.server --project . --port 8765
```

This session's Chromium network policy returned `ERR_BLOCKED_BY_ADMINISTRATOR` on localhost. `evidence/browser-checks.json` uses exact source content in about:blank with API calls bridged to a real temporary HTTP server; screenshots are actual Chromium frames, not product mocks. WebGL2 GPU unavailable in that environment; fallback Canvas2D verified instead. GPU hardware p95, audio subjective listening, native Android all NOT_RUN.
