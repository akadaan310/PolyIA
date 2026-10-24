# ISNAAD reconstruction and limits

ISNAAD was inspected as a read-only reference. Its original remote, branches, settings, database and deployments were not changed. A clean local clone at `/workspace/references/isnaad` supplied the evidence. All execution and instrumentation occurred in a disposable copy at `/tmp/isnaad-audit`; SNAD does not import that project at runtime.

This reconstruction records computational behavior. Detector scores, frame labels and narrative descriptions are not verified meanings, speaker identities, intentions, tafsīr or calibrated probabilities.

## Branch inventory

The remote advertised three branches and no tags at inspection on 2026-10-18:

| Branch | Exact tip | Role |
| --- | --- | --- |
| `claude/quran-isnad-explorer-prototype-0ml0tp` | `4c059a1691920a13ea973146e42518e83f31573c` | Default; primary reconstruction pin |
| `claude/computational-universe-api-aksppy` | `f7b2937f6472218ed942c66fb507947e3866e2ec` | Older source-addressing protocol and generated index |
| `claude/nav-computed-relationships-af4xla` | `db345c34bfa4db1b51734f665d970056306b34c6` | Adds relation-group convergence and navigation |

`src/lib/engine`, `corpus.ts`, `morphology.ts`, `isnad.ts`, `scripts/ingest-cosmos.ts` and `data/corpus` have identical Git objects at all three tips. The engine tree is `21f744b56d90692fda70e41b3edd731af6727c52`; the corpus tree is `af5f8af0cd32f96a86c5f39be06e2d36bf479a70`. The API branch's `docs/fihris.meta.json` defines an `isnaad://` source-addressing convention and request vocabulary; this is documentation, not an implemented transport protocol. The navigation branch adds code and verification beyond the default branch and was separately executed.

Machine-readable inventory, exact source-file hashes and original verification transcripts are in [isnaad-source.json](../evidence/isnaad-source.json).

## Inputs and rights

The source ingestion script fetches unpinned branches of `mustafa0x/quran-morphology` and `risan/quran-json`. It splits morphology by surah, removing only the surah prefix from each locator; per-surah rows otherwise preserve the source forms and features. Display orthography is a separate Uthmani text stream in `data/corpus/meta.json`.

GitHub reports `license: null` for ISNAAD, and no license/notice file is tracked at any inspected tip. No open-source grant for the ISNAAD code is inferred from its public visibility. SNAD contains independently written implementation and provenance-bound compatibility outputs, not copied ISNAAD engine modules.

The mustafa morphology fork has no explicit license discovered. Its content is modified from Quranic Arabic Corpus (QAC) v0.4; the original QAC declares GPL terms plus verbatim/no-changing conditions. Rights for the fork's modifications remain unresolved. The small source excerpts and derived expected outputs in `original-detectors.json` are labeled compatibility evidence, with no new license grant inferred. They must not be treated as a licensed replacement corpus.

Separately, the corpus intake established that all 6,236 ISNAAD Uthmani ayah strings match the pinned `risan/quran-json` v3.1.2 text at commit `64c0d713a91923c6ee1216b7c0206bad9a7846b8`, with its explicit CC BY-SA 4.0 notice. Original QAC v0.4 and its notices are preserved separately by SNAD's corpus intake. The QAC original and the mustafa fork are distinct tokenizations; never assert their word or segment identities are interchangeable. See `data/quran.provenance.json` and the original files under `data/upstream/` for that independent intake.

## Reconstructed pipeline

The source citations below use primary commit `4c059a1691920a13ea973146e42518e83f31573c`; paths and line anchors refer to that immutable revision.

1. [`parseCorpus`, corpus.ts:67](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/corpus.ts#L67) reads `ayah:word:segment`, form, class and feature columns. Malformed locators and non-finite coordinates are silently skipped; ordering, positivity, completeness and unique coordinates are not comprehensively validated. `buildSurah` constructs boundaries from surviving rows, so source-text verses without morphology would disappear from its assembled domain.
2. [`parseFeatures`, morphology.ts:39](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/morphology.ts#L39) extracts root, lemma, person, number, gender, tense/aspect, case, passive voice, form, mood and clitic status. Bare `P` is a preposition, not plural. Person and noun number/gender are separate patterns; noun case applies only to class `N`. Original feature tokens survive internally.
3. [`assignRoles`, isnad.ts:23](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/isnad.ts#L23) mutates segment roles. The word spine chooses verb subject, nasikh subject, detached pronoun, then subject enclitic. Object, possessive, prepositional and vocative references remain distinct from that spine. This is grammatical person attribution, not entity identity resolution.
4. [`personVector`, isnad.ts:101](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/isnad.ts#L101) counts every reference, weighting subject roles 1 and other references 0.6. The authored projection assigns second person 0, first person 0.5 and third person 1. Zero reference mass has distance 0.5 and a zero vector. `findSeams` skips words with no spine and compares adjacent surviving spines for person, known number, known gender and known tense differences. It can span ayah boundaries.
5. [`buildFrames`, frames.ts:138](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/engine/frames.ts#L138) opens only on verbal root `قول`, despite a broader unused saying-root set. Third-person or imperative reporting replaces the stack; first/second non-imperative reporting nests if a stack exists. The maximum stack length is 4. Frames may continue through six following ayat without another opening. Speaker resolution tries a nominative noun within three words, then the nearest named lexicon actor within fourteen preceding words, then the verb's form. `noun`, `context` and `verb` indicate how the label was obtained; none proves identity. `quoteStart` skips apparent nominative subjects and `لـ` complements heuristically.
6. [`runAllDetectors`, detectors.ts:658](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/engine/detectors.ts#L658) runs eight detectors, suppresses same-kind overlapping spans when shared length divided by the shorter span is at least 0.6, then sorts by score. Defaults: stitch window 8 words, root echo window 22, minimum absence run 2, narrative run 4 and score floor 0.28. Windows are within a surah stream, not always within one ayah.

| Source kind | Implemented structural trigger | Important limitation |
| --- | --- | --- |
| `istihdar` | A third-person spine run ends; a second-person reference arrives among the next four spines | It does not establish that absent and addressed entities are the same |
| `raj-al-jidhr` | Consecutive occurrences of a root within 22 words differ in frame depth, voice or spine person | Root equality is not lexical sense equality; its `corefers` flag is weak agreement |
| `jisr-al-naba` | A third-person run containing a perfect is followed by first-person imperfect | Imperfect morphology does not entail physical present time |
| `ribat` | A grammatical seam shares roots across fixed windows | Root continuity is an authored feature, not semantic equivalence |
| `nasikh-mirror` | Consecutive nasikh carriers of one particle family have different persons | Family membership and thresholds are authored choices |
| `alsinat-al-khalq` | Closed entity lexicon plus nominative/vocative evidence or nearby agency verb | Nearby verbs are not parsed dependencies; unavailable lexemes are missed |
| `tabaqat-al-isnad` | A heuristic quote frame has positive nesting depth | It inherits frame and label errors |
| `rusul-echo` | A frame label matches the messenger lexicon and its span has at least two spine words | Despite its kind name, it does not compare two messenger contours |

The lexical stitch is `sharedRootCount / sqrt(unionRootCount)`, clamped to [0,1]. Seam magnitude weights absolute person-axis change 0.6, person change 0.2, tense change 0.15, number change 0.08 and gender change 0.05, then clamps. Ribat is `clamp(1.15 * sqrt(stitch * seamMagnitude))`, with threshold `minScore + 0.12`. These are reproducible definitions, not discovered laws.

## Motifs, graph relations and composition

[`motifs.ts`](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/engine/motifs.ts#L126) uses a suffix automaton over twelve person × tense symbols. Null-spine words do not contribute symbols. The default candidate length range is 5–24, occurrence minimum 2, surah spread minimum 2 and output limit 400. Candidate preselection keeps up to `limit * 3` by occurrence count × length; each retained motif stores only its first 60 occurrences, while spread is calculated before that truncation. The header's “no ceiling on length” describes the automaton capability, not the default output. The ingestion script inserts surah sentinels and filters results by recorded occurrence start surah. All 400 committed motifs were checked: none has an unknown/sentinel symbol in its pattern. The filter is not a proof against boundary contamination for other parameters or corpora; both endpoints and all symbols should be validated in a general adapter.

[`graph.ts`](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/engine/graph.ts#L68) ranks compressed-person signature equality, 1↔3 inversion, reversal, then vector cosine fallback (`>0.985` with distance difference `<0.06`). These equalities discard lexical content, word multiplicity and quotation identities. The chamber walk greedily alternates authored operation families and includes curated seeds.

[`aalam-miner.ts`](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/engine/aalam-miner.ts#L40) matches declarative lemma/root/phrase/case/definiteness/co-root constraints and optional hand-named loci. [`assembler.ts`](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/engine/assembler.ts#L61) interleaves marker hits with selected detector stations and curated associated loci. [`surah-composition.ts`](https://github.com/akadaan310/isnaad/blob/4c059a1691920a13ea973146e42518e83f31573c/src/lib/engine/surah-composition.ts#L24) instead keeps one station per ayah and attaches the highest-ranked allowed annotation. Those are presentation rules, not new discourse morphisms or compositionality proofs.

The navigation branch's [`convergence.ts`](https://github.com/akadaan310/isnaad/blob/db345c34bfa4db1b51734f665d970056306b34c6/src/lib/cosmos/convergence.ts#L79) groups motif and resonance into one contour class, roots into lexical, and discoveries into detector. It excludes fixed-degree generated neighbors from evidence; a two-leg route is explicitly not an endpoint relation. The class split acknowledges detector/lexical dependence and does not prove statistical independence. Executed source verification finds 117 of 1,000 placed ayat have at least one convergence, yielding 86 unordered pairs. These numbers describe its selected field only.

## Exact reconstruction results

Whole-source analysis, using its committed corpus and default options, produced:

| Denominator or output | Measured count |
| --- | ---: |
| Surahs / addressable ayat | 114 / 6,236 |
| Morphology words / actual parsed segments | 77,429 / 130,030 |
| Ayat shorter than three morphology words | 204 |
| Ayat with zero person-reference evidence | 352 |
| Heuristic quotation frames / grammatical seams | 1,607 / 16,231 |
| Deduplicated discoveries / nested-frame discoveries | 7,057 / 77 |
| Maximum heuristic frame depth | 4 |
| Committed global discovery index | strongest 2,500 of 7,057 |

The committed manifest says 130,031 segments. `scripts/ingest-quran.ts:265` actually stores `lineNo`, incremented for every newline-split entry before empty/malformed entries are skipped. The measured parsed count is therefore used here; the manifest counter is not accepted as a segment denominator.

The original acceptance script passes its five exemplar conditions: 11:29 istihdar score 0.940, 11:29 nasikh mirror 0.660, 50:2 root return for `عجب` 0.808, 28:5 bridge 1.000 and 28:5 ribat 0.535. Those passages were used to design the original detectors; they are reconstruction checks, not independent validation. Hūd 11:36, short/zero-feature cases and twelve deterministically selected additional loci are also preserved in [original-detectors.json](../data/original-detectors.json). The 22 cases are examples within a complete-source pass, never a claim of semantic annotation for the entire Quran.

### Legacy highlight baseline

The exact `scripts/ingest-cosmos.ts` selection algorithm was executed in the disposable copy. Its 1,000 ordered loci matched the committed payload exactly. Every rebuilt payload field except the time-dependent `builtAt` matched too.

The algorithm excludes fewer-than-three-word ayat, leaving 6,032 candidates. It chooses by rounded score, with stable source-order tie breaking and a maximum of `ceil((1000/114)*3.2) = 29` ayat per surah. It selects 1,000 across 72 surahs. The score is:

```text
1.5 * bestDiscoveryScore
+ 0.16 * min(seams, 6)
+ 0.32 * min(markerHits, 4)
+ 0.9 * timeTension
+ 0.5 * clockBridge
```

Scores are rounded to four decimals before ranking. Selection depends on the committed marker index as well as morphology, time features and detectors. The complete 1,000-locus compatibility fixture, ranks, scores and word counts are versioned in [legacy-selection.json](../data/legacy-selection.json). Ordered-locus SHA-256 is `11f28b9bef873b0aa068d3f2ce280ef8df7888f0236e8a8f61245b327652ece4`. This selection is a highlight baseline; SNAD's input universe remains all 6,236 ayat, including the 204 this legacy filter excludes. Astronomy-related placement and imagery are not adopted into SNAD.

## Counterexamples and inherited failure cases

The following are observed source behavior or explicitly bounded source-code limitations:

- **Same-person suffix ambiguity, executed synthetic input.** A third-person singular verb plus a third-person singular object-shaped suffix is labeled `verb-subject` + `subject-enclitic`. The rule tests person only. Number, gender, transitivity and syntactic dependency are not sufficient safeguards in that implementation. The fixture preserves the actual roles instead of blessing them as correct.
- **Mutation isolation failure, executed.** For surah 11, a default pass stamps 18 `word.khalq` annotations. Re-analyzing that same object with `minScore: 1` reports zero khalq discoveries but retains those 18 word annotations. A fresh surah built at that threshold has zero annotations. `analyze` and `detectKhalq` mutate caller objects; stale annotations can survive threshold changes.
- **Lossy distance equivalence, executed.** A zero person vector and a pure first-person vector both map to distance 0.5. Equal projection values cannot establish equal attribution or equal evidence.
- **Weak root-return coreference, source inspection.** `detectors.ts:253` tests quoted-speaker number against an earlier verbal subject and requires speaker person 3. It does not check gender, named identity or compatible referents; equal unknown numbers (`null === null`) can satisfy the number check. The field is an agreement heuristic, not entity coreference.
- **Nested-frame speaker labels, observed.** Source verification prints a depth-four surah 5 chain beginning `مريم → أَقُولَ → قُلْتُهُۥ → قُلْتُ`. This is the resolver's output, not a verified speaker genealogy. Third-person saying inside quoted content is necessarily treated as a sibling by the inflection rule.
- **Boundary and lexical assumptions, source inspection.** Missing rows can remove loci; windows cross ayah boundaries; nominated subjects and nearby agency roots are not dependency parses; closed actor/entity lexicons cannot establish completeness.

The source documentation also records previously fixed bugs: aggregate vectors computed before role resolution, omitted noun number/gender, runaway quote nesting when every imperative nested, and byte-order differences causing a time lemma to match nothing. These historical fixes are useful regression cases; they were not newly discovered defects in the inspected tips. The celestial-name bug mentioned there is unrelated to SNAD.

## Reproduction procedure

1. Clone ISNAAD separately and detach at the primary commit above. Confirm the captured advertised branch tips and that the reference tree is clean.
2. Copy `src`, `scripts` and `data` to a disposable directory. Run source programs only there; ingestion overwrites derived artifacts.
3. Use the source's pinned `tsx` 4.19.1/TypeScript 5.6.2 toolchain, or Node 24 type stripping with a resolver hook that appends `.ts` for relative extensionless imports. The reconstruction used Node `v24.19.0` and the latter loader; it did not rewrite source algorithms.
4. Run `scripts/verify-exemplars.ts`, `scripts/verify-cosmos.ts` and `scripts/ingest-cosmos.ts`. The navigation branch additionally supplies `scripts/verify-convergence.ts` and `src/lib/cosmos/convergence.ts`; execute those from their exact branch pin in the disposable directory.
5. Compare ordered `(surah, ayah)` pairs and the payload excluding `builtAt` with the committed payload. For score/word-count capture, the disposable script was instrumented only to serialize its `chosen` array before placement; the selection logic remained byte-for-byte the source algorithm.
6. Recompute cases over complete surahs. Fixture spans and frame IDs use absolute word indices within their source surah. Slicing one ayah before analyzing changes context and is not an equivalent replay.

Every source acceptance program exited 0. Its tests validate source-internal consistency and reconstruction, not accuracy against independent human annotations. No original production deployment, audio verification or full semantic validation was performed during this audit.
