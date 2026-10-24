# Corpus sources, licenses and coverage

SNAD's addressable input domain contains **6,236 ayahs in 114 surahs**. The identifiers are `quran:<surah>:<ayah>`, using the numbering of the pinned source. Every ayah is included, including one-word passages and passages with no projected grammatical features. Corpus membership is independent of detector output, the legacy highlight selection, and visualization selection.

## Exact text snapshot

The text is the unchanged `text` field of [risan/quran-json v3.1.2, commit `64c0d713a91923c6ee1216b7c0206bad9a7846b8`](https://github.com/risan/quran-json/blob/64c0d713a91923c6ee1216b7c0206bad9a7846b8/dist/quran.json). Risan Bagja Pradana distributes this dataset under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); the pinned README credits its Uthmani Arabic text to [The Noble Qur'an Encyclopedia](https://quranenc.com/en/home). No endorsement is implied.

The upstream dataset and this derived corpus arrangement retain CC BY-SA 4.0. The generic SDK's license does not replace these data terms. The complete upstream license and pinned README are included under `data/upstream/`.

| Artifact | Purpose |
|---|---|
| `data/upstream/risan-quran-v3.1.2.json` | Original upstream file, unchanged bytes |
| `data/upstream/risan-LICENSE-CC-BY-SA-4.0.txt` | Upstream license |
| `data/upstream/risan-README-v3.1.2.md` | Source attribution and original dataset documentation |
| `data/quran.json` | Flattened locus records; each source text string is unchanged |
| `data/quran.provenance.json` | Commit, source URL, SHA-256, derivation and exhaustive per-surah counts |

The raw snapshot SHA-256 is `d8a8adff387f60ce3ff7dbe3238dd9b27120bfe29d8fcb07ad2e89cad37cefd4`. Its 6,236 text strings equal all 6,236 strings in ISNAAD's `data/corpus/meta.json` at commit `4c059a1691920a13ea973146e42518e83f31573c`; the exact-string comparison found zero differences. Neither Unicode normalization nor trimming, diacritic removal or punctuation replacement is applied to stored text. JSON container formatting and added IDs/source fields are the only transformations.

At the time of this audit, Risan's current `main` had removed the old `dist/quran.json` path during its overhaul. The old URL in ISNAAD's ingestion script is therefore insufficient to reproduce that historical source. SNAD pins a reachable historical version whose text was actually compared against ISNAAD.

## Separate original QAC morphology

SNAD uses the **Quranic Arabic Corpus morphology v0.4**, copyright 2011 Kais Dukes, with its full original copyright blocks. Its underlying text is Tanzil Uthmani v1.0.2, copyright 2008–2009 Tanzil.info. The morphology file labels its annotations GNU General Public License without specifying a version. Its text block labels the underlying text CC BY-ND 3.0 Unported. Both blocks expressly permit verbatim copying and distribution, require source attribution and links, and prohibit changes to the source file. The complete notices are reproduced in `data/upstream/QAC-NOTICES.txt` and `data/quran.morphology.provenance.json`. The original file is unchanged. Projections are separate derived objects.

Sources: [QAC's official download and terms page](https://corpus.quran.com/download/), [Tanzil](https://tanzil.net/), and the unchanged source snapshot [mirrored by taziksh/quran-frequencies at `079cdc74cd494ec1b35011363288d80cae047c51`](https://github.com/taziksh/quran-frequencies/blob/079cdc74cd494ec1b35011363288d80cae047c51/data/quranic-corpus-morphology-0.4.txt).

The file was obtained from that pinned public mirror rather than by submitting an invented email to QAC's download form. A second pinned mirror, [AhmedSaadi0/quran-words at `a6d4217a9e1422978c367eadc833ff4883db77fb`](https://github.com/AhmedSaadi0/quran-words/blob/a6d4217a9e1422978c367eadc833ff4883db77fb/data/quranic-corpus-morphology-0.4.txt), had identical contents after comparing CRLF/LF line endings. The bundled first mirror retains its original CRLF bytes. **An official published digest was not available or verified**, so mirror agreement is explicitly weaker than verification against an official digest.

| Item | Value |
|---|---|
| Raw QAC file | `data/upstream/quranic-corpus-morphology-0.4.txt` |
| Raw bytes | 6,309,503 |
| Raw SHA-256 | `a1d12923815341face765083805d2148ed2d9f5cc3f7d6665219d887675d8c46` |
| Source segment rows | 128,219 |
| Distinct source words | 77,429 |
| Source ayahs | 6,236 |
| Full inspectable projection | `data/quran.morphology.json` |
| Compact equivalent features | `data/quran.features.json` |
| Projection provenance, notices, schema and hashes | `data/quran.morphology.provenance.json` |

The number 77,915 sometimes reported for QAC is its count of **STEM-tagged segments**, not its distinct word count. Multiple STEM segments can belong to one source word. This was checked directly from the rows.

ISNAAD instead uses the modified [mustafa0x/quran-morphology fork](https://github.com/mustafa0x/quran-morphology), inspected at `8f38b39016824284f9ed16ae15069ff9102c4acf`. That fork changes root/lemma tags and segmentation and has no repository LICENSE file. It is documented as an inherited source, but its full modified data are not silently repackaged under SNAD's code license. Original-detector compatibility is a separate exercise; differences from original QAC are not automatically SNAD bugs.

## Explicit alignment and uncertainty

QAC coordinates `(surah:ayah:word:segment)` remain addressable in the unchanged source file. QAC Buckwalter forms are decoded using the published character correspondence. A QAC word can supply features to a zero-based whitespace token of the exact stored Arabic text only when:

1. Its ayah's QAC word count equals the exact text's whitespace token count.
2. The concatenated Arabic forms of that word's source segments equal that token under the declared alignment key.

The alignment key removes Unicode combining characters in categories `Mn`/`Me`, removes tatweel U+0640, and folds alef wasla U+0671 to alef U+0627. This key exists **only for alignment**. The original text, original forms, segment flags and raw file remain intact. Base-letter differences outside that narrow rule are retained as failed alignments. No edit-distance matching, semantic guessing or forced position matching fills the gaps.

Word-level `person`, `number`, `aspect`, `mood`, `root` and `lemma` values are projected only when all source segments that specify that field agree. Disagreements are retained in `segmentFeatures` and `ambiguousFields`, and the conflicting aggregate field is absent. `PERF` and `IMPF` remain aspect tags; imperative `IMPV` is kept separately as a mood tag. No past/future time or speaker identity is inferred. Root and lemma strings are transliterated to Arabic without linguistic editing. A missing field stays missing. A grammatical third-person suffix is not a known speaker, addressee or referent.

The compact file is schema `snad.qac-features.v1`: its object keys are locus IDs, and values contain `{sourceId, status, features:[[tokenIndex, features]], unalignedWords, ambiguousWords}`. Each tuple is a derived `qac-tag-projection-v1` result using the enclosing `sourceId`. The full projection retains the per-word source indices, segment disagreements, evidence and failed-alignment reasons.

| Coverage denominator | Count |
|---|---:|
| Addressable exact-text ayahs | 6,236 / 6,236 |
| Ayahs with original QAC morphology | 6,236 / 6,236 |
| Surface-aligned words | 73,092 / 77,429 |
| Mappings withheld | 4,337 / 77,429 |
| Words with at least one projected field | 72,590 / 77,429 |
| Words with projected grammatical person | 21,774 / 77,429 |
| Words with conflicting segment fields retained | 478 / 77,429 |
| Ayahs with at least one projected field | 6,204 / 6,236 |
| Fully aligned ayahs | 3,638 / 6,236 |
| Partially aligned ayahs | 2,586 / 6,236 |
| Ayahs without usable mappings under this gate | 12 / 6,236 |
| Audio verified by this audit | 0 / 6,236 |

Twenty additional fully aligned ayahs have no projected fields, explaining why 12 unaligned ayahs does not mean 6,224 feature-bearing ayahs. Coverage is not detection, linguistic correctness, semantic validation or audio validation. For example, `quran:20:1` remains addressable and fully aligned with an empty feature list.

## Rebuilding and checking

Run `python scripts/prepare-corpus.py` to regenerate corpus and projection files from the local immutable snapshots without network access. The script rejects mismatching source hashes, malformed QAC coordinates, wrong counts or missing locus membership. The source IDs, processing method and generated artifact hashes are in the provenance manifests. The corpus tests independently check all 6,236 source text roundtrips, unique loci, short passages and adapter behavior. Runtime analysis, detected transitions and visualization denominators are reported by the experiment suite, separately from this intake audit.

No corpus annotation produced here establishes speaker intention or a theological interpretation.
