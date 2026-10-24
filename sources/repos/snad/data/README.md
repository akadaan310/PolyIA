# Dataset notices and boundaries

Generic SDK code is MIT. That license does not relicense the files here.

| Files | Origin and terms |
| --- | --- |
| `quran.json`, `upstream/risan-quran-v3.1.2.json` | Risan Bagja Pradana, `risan/quran-json`, pinned v3.1.2 commit `64c0d713a91923c6ee1216b7c0206bad9a7846b8`; CC BY-SA 4.0. Upstream credits The Noble Qur'an Encyclopedia. Original strings preserved exactly. |
| `upstream/quranic-corpus-morphology-0.4.txt` (see actual path in provenance) | Quranic Arabic Corpus v0.4, Kais Dukes/University of Leeds; verbatim downloaded mirror retained, GPL annotation notice plus verbatim/no-changing conditions. Underlying Tanzil text has its own CC BY-ND 3.0 notice. Exact original notices are in `upstream/QAC-NOTICES.txt` and raw file header. |
| `quran.morphology.json`, `quran.features.json` | Separate SNAD computational projections of the preserved QAC source, with alignment omissions and conflicting segment fields explicitly recorded. They do not replace the original morphology edition. Retain original attribution/notices and `quran.morphology.provenance.json`. |
| `legacy-selection.json`, `original-detectors.json` | Compatibility evidence generated from pinned ISNAAD behavior, including source-derived fixture rows. ISNAAD's inspected repository has no explicit source license; its modified morphology fork has no explicit repository license. These fixtures do not imply a general grant to redistribute the original source or data. See `docs/reconstruction.md`. |

`quran.provenance.json` and `quran.morphology.provenance.json` name exact remote paths, commit hashes, original byte hashes and derivation rules. All 6,236 ayahs are retained. Source text is never silently normalized. The alignment comparison key is used only to decide whether a feature can attach to a text token; 4,337 mappings are withheld.

The original QAC download is independently mirrored with matching content after line-ending comparison; no official cryptographic digest was available. Parsing and stable identity do not certify linguistic annotation accuracy or audio verification. All corpus-derived speaker identities remain unresolved unless explicit separate evidence is supplied.
