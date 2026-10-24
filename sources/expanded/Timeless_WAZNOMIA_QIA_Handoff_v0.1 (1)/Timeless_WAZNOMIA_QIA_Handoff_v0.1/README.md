# Timeless Arabic × WAZNOMIA × QIA — Research & Muse Handoff

This package is **not** a redesign of Muse's Corpus Engine. It is a research bridge back to her with a source-backed mathematical design and a tiny verified prototype.

- `FOUNDATIONAL_STUDY.md` — detailed research memorandum, audits, historical/linguistic distinctions, formal operators, refutations, next-step experiments.
- `MUSE_RELAY_COMMISSION.md` — immediately reusable implementation and verification commission.
- `src/rasm_state.py` — minimal Python reference library; manually transcribed the source-derived class tables under the named inventory.
- `tests/test_rasm_state.py` — 30 unit tests.
- `run_demo.py` — grounded toy demonstration.
- `results/demo.json`, `results/test_output.txt`, `results/run_output.txt` — executed results.

Run with Python >= 3.10 and no external dependencies:

```bash
python -m unittest discover -s tests -v
python run_demo.py
```

**Status:** Source code was reviewed via linked GitHub connector. This package's Python tests were executed independently. The remote Timeless Next.js app, its Vitest suite, external corpus POC, and live website were not run. This is not proof of full Arabic morphology or a universal theory of semantics.
