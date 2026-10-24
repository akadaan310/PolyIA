# ULWS × PHONEX × QIA — 0.1

A **separate, non-destructive research extension** for Abed's Substrate University, Arabic Timeless, WAZNOMIA and Muse's forthcoming corpus. Built as a seed handoff to Codex on the Oracle VM.

- `FOUNDATIONAL_RESEARCH.md`: full mathematical scope, schema, evidence contracts, algorithm costs, multilingual sources, validation gates and governance.
- `CODEX_GOD_SEED.md`: complete VM implementation commission for Codex.
- `src/phonex.py`: deliberately small standard-library-only toy initial-phonetic matcher with fixed feature distance, prefix preindex and auditable witness output; **NOT** full IPA parsing or trained linguistics.
- `tests/test_phonex.py`: reference contracts for the demonstrator.
- `examples/topology_toy_results.json`: example of toy query, not attested multilingual data.
- `results/tests.txt`: actual Python unittest output from this environment.

## Reproduce the toy tests

```
python -m unittest discover -s tests -v
python src/phonex.py match --segments 't ə p ɒ l' --budget 0.50
```

## Source grounding

- User's attached `Arabic_Timeless...pdf` and `WAZNOMIA_header_doc.md`, `corpus engine design.md`, prior handoff; GitHub repository `akadaan310/ARABIC_TIMELESS` read-only.
- External public references are listed with URLs in the research memo. This ZIP **does not contain acquired third-party corpora**; dataset acquisition is a gated Codex phase.

**Honesty:** A token matching an approximate pronunciation does not prove shared meaning, ancestry or translation. High phonetic recall is an engineering question to measure, not a theorem promised by a hash. Dataset descriptions and licenses must be independently checked for the exact downloadable releases before ingest.
