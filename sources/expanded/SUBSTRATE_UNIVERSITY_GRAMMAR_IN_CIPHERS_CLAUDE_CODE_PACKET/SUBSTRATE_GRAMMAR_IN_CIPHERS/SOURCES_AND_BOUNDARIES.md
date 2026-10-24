# Primary Sources, Repository Boundaries, and How to Verify

## Connected GitHub repositories inspected during preparation

| Source | Role | Branch/entry files |
|---|---|---|
| [akadaan310/abedkadaancom](https://github.com/akadaan310/abedkadaancom) | current Substrate University structure | `claude/new-session-xd8auu`: `README.md`, `docs/UNIVERSITY_REBUILD.md`, `src/content/registry.ts`, `src/content/types.ts`; six typed divisions |
| [akadaan310/assufrciphertheory](https://github.com/akadaan310/assufrciphertheory) | strongest existing source of the 29-site corpus, qiraat and interpretation register | `ccr-6bf87543-8lv1az`: `README.md`, `TERMS.md`, `PROVENANCE.md`, `data/sites_input.json`, `lab/sites.py`; `data/quran/tanzil-uthmani.txt`, `tanzil-simple-clean.txt` listed in repo, **not copied into this packet** |
| [akadaan310/computationalgrammartheory](https://github.com/akadaan310/computationalgrammartheory) | formal operational and structural grammars | `ccr-04ad16b1-q42wck`: `DEFINITIONS.md`, `FORMAL_MODELS.md`; CGT-DEF-003 and CGT-DEF-005 |
| [akadaan310/grammarinnumbers](https://github.com/akadaan310/grammarinnumbers) | numeral/representation/admissibility layers | `claude/happy-newton-r2t17c`: `DEFINITIONS.md`, `FORMAL_MODELS.md`; GIN-DEF-001 through -008 |
| [akadaan310/substrates](https://github.com/akadaan310/substrates) | bottom-up ladder of primitives | `claude/minimal-adaptive-topology-nzeu63` `README.md` |
| [akadaan310/substrateIO](https://github.com/akadaan310/substrateIO) | substrate research secondary reference | `research/ONTOLOGY.md`, `research/CHARTER.md` listed; not fully audited |

**Limits:** This was a targeted inspection of the linked repositories and their relevant files, **not a comprehensive review of every file/commit/branch**. The accessible public website could not be fetched with the web reader, so repo inspection is the source. The user's Division Infinity material was not found in the inspected repo paths; the future agent must search current branches and any author-provided attachments before declaring its precise rules. The source tree is not modified by this package.

## Canonical textual sources

The existing cipher-theory project provides Tanzil Uthmani and Simple Clean v1.1, along with 8 KFGQPC recitation resources and checksum tests. Read upstream LICENSE/attributions and preserve unmodified copied Qur'anic text. The prompt only references, does not bundle, the complete sacred-text corpus. For public reading crosschecks, these reference URLs were used:

- [Quran 36:14](https://quran.com/36/14) — two reinforced by a third.
- [Quran 18:18](https://quran.com/18/18) — youths, dog, threshold and observer.
- [Quran 18:19](https://quran.com/18/19) — one asks about duration, group response.
- [Quran 18:22](https://quran.com/18/22) — reported 3/4, 5/6, 7/8 and epistemic warning.
- [Quran 27:18](https://quran.com/27/18) — ant and valley.
- [Quran 16:68](https://quran.com/16/68) — bee and dwellings.
- [Quran 27:88](https://quran.com/27/88) — mountains, perception, صنع.
- [Quran 30:3](https://quran.com/30/3) — أدنى الأرض.
- [Quran 12:30](https://quran.com/12/30), [12:36](https://quran.com/12/36), [18:60](https://quran.com/18/60) — youth expressions.
- [Quran 40:36–37](https://quran.com/40/36-37) — ṣarḥ and ascension motif.
- [Quran 6:143–144](https://quran.com/6/143-144) — eight pairs.
- [Quran 15:87](https://quran.com/15/87) — seven oft-repeated.

## Verification protocol

1. Clone/read upstream repositories and check their latest heads; branch names above are *inspected provenance*, not instructions to overwrite current work.
2. Run cipher-theory source tests before using any text. Lock revision + checksums.
3. Extract 29 sites using upstream `data/sites_input.json` and `lab/sites.py`, not newly invented handwritten verses. Compare independently with this packet's `29_cipher_sites.json`.
4. Load full canonical Qur'an from the locked source and verify that every displayed quote agrees exactly; derive 114 surahs and ayah counts from its manifest, including any edition-specific counting.
5. Report all qiraat comparisons per narration; no silent cross-edition normalized equality claims.
6. Use separate methods for `rasm`, Uthmani code points, normalized orthography, phonetic recitation, morphology, and semantic annotations.
7. Never change text to make a counting hypothesis succeed.
