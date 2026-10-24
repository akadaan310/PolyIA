# SNAD computational evidence report

This release establishes a reproducible research instrument and finite computational checks. It does not establish a new theorem, a linguistic discovery, an interpretation of speaker intent, or a theological result. The research stretch target remains open: the register contains 20 supported engineering/fixture observations, not 20 claimed novel discoveries. Ten falsifiable hypotheses, seven negative controls, three independently reconstructed finite results, and a simpler-baseline comparison are recorded in [experiments.json](../evidence/experiments.json).

## Reproduce

From the repository root, run `npm ci`, `npm test`, `npm run typecheck`, `npm run experiments`, and `npm run benchmark`. `experiments.json` and `corpus-status.json` are deterministic for fixed code and data. Benchmark time/memory depend on the current machine and runtime. A benchmark invocation overwrites its previous observation; the retained report describes one pass, not a statistical study. Property tests use seed 6236. Independent passage selection ranks SHA-256 digests of `snad-independent-v1:` plus canonical locus and excludes the five prescribed loci before selecting twelve.

## Complete source domain and separate denominators

All 6,236 ayahs across 114 surahs are canonical inputs. The exhaustive test compares each ayah's source text directly with the pinned upstream Risan JSON and roundtrips its canonical locus. All 204 ayahs shorter than three tokens and all 28 single-token ayahs remain addressable and analyzed. The original 1,000-node selection is retained in [legacy-selection.json](../data/legacy-selection.json) as a highlight baseline; its minimum-three-word filter is not used for corpus coverage.

| Denominator | Result | Meaning |
| --- | ---: | --- |
| addressable | 6,236 / 6,236 | Canonical locus present and unique; lookup roundtrips. |
| parsed | 6,236 / 6,236 | JSON source text and locus parsed; no claim of linguistic completeness. |
| analyzed | 6,236 / 6,236 | SDK analyze completed, including zero-transition and missing-feature cases. |
| detected | 2,738 / 6,236 | At least one typed transition detected under the supplied feature projection. |
| visualized | 0 / 6,236 | Per-locus browser rendering explicitly verified in this pass; no browser was run. |
| audioVerified | 0 / 6,236 | Recitation/audio comparison explicitly verified; no audio verification performed. |

The computational pass has 4,929 typed transitions in 2,738 ayahs; 3,498 ayahs have zero detected transitions. An analyzed result with no detected transition remains a valid result. Zero attribution transitions means speaker/addressee/referent identities were not supplied or inferred by this corpus adapter; grammatical-person changes do not identify speakers. Visualized zero describes this numerical pass, which does not run a browser. Browser smoke journeys and UI capacity require their own evidence. Audio verification is zero.

[corpus-status.json](../evidence/corpus-status.json) preserves one explicit row per ayah with stable locus, status, source identifier, exact-text SHA-256, morphology source/status, feature counts and transitions. The text is preserved verbatim; any alignment key is separate from stored orthography.

## Morphology coverage is a separate measurement

The text corpus has 77,429 whitespace tokens. The QAC v0.4 mirror snapshot has 77,429 words and 128,219 segments. The projection aligns 73,092 words, supplies nonempty feature dictionaries for 72,590 words in 6,204 ayahs, withholds mapping for 4,337 words, and preserves 478 words with ambiguous fields in separate segment records. This is evidence-aware partial annotation, not complete linguistic annotation. A mapped word can still have no projected feature. Absence and conflicting fields remain absent.

The QAC snapshot is attributed to the official corpus but was retrieved from pinned mirrors. The official endpoint digest was not independently verified; two mirror bodies agree after CRLF/LF folding. The exact raw file remains unchanged with its GPL, Tanzil CC BY-ND, and verbatim/no-changing notices. The independent text corpus has its own CC BY-SA attribution. See [quran.provenance.json](../data/quran.provenance.json), [quran.morphology.provenance.json](../data/quran.morphology.provenance.json), and [QAC-NOTICES.txt](../data/upstream/QAC-NOTICES.txt). The original ISNAAD fixture's source corpus reports 130,030 segments, whereas this independently pinned QAC snapshot has 128,219; the two corpora are not asserted to be byte-identical.

QAC PERF/IMPF remain aspect labels; IMPV is retained as mood rather than being mislabeled as aspect. No tense is inferred. The current typed transition detector compares person, number, tense and aspect, and preserves other feature fields without turning them into additional typed change categories. The 4,929 count therefore follows this explicitly limited detector definition.

## Measured whole-corpus pass

The retained [benchmark.json](../evidence/benchmark.json) records Node v24.19.0, linux x64, `AMD EPYC 9V74 80-Core Processor`, and 5 reported logical CPUs. It measures one sequential pass after loading text and the full evidence-bearing morphology projection.

- Input load: 318.75 ms; analysis/status pass: 2261.76 ms; combined: 2580.52 ms.
- Sampled peak process RSS: 368,730,112 bytes (351.65 MiB); sampled peak heap used: 232,157,960 bytes (221.40 MiB).
- Memory includes Node, the input corpus, the full morphology data, allocation and retained status rows. Samples occur every 100 ayahs plus endpoints; the reported peak is a lower bound on the true peak. Deltas are not per-ayah memory costs.

There is no warmup, repeated-run variance estimate, comparative machine study, peak profiler, forced GC, or speedup claim. Status hashing and memory sampling are included in analysis time. The JSON records exact input hashes and unrounded measurements.

## Numerical definitions and independent reconstructions

A typed path is `(from, to, edge-ID sequence)`. The identity at an endpoint has an empty edge sequence. Composition requires matching endpoints and concatenates edge sequences left to right. R1 independently constructs a plain-list reference and checks 81 composable triples over three vertices, plus 162 identity checks. These are regression checks of a standard path construction, not an original categorical theorem.

For the graph summary, vertices are input units and edges are detected typed boundaries. Weak components and cycle rank use the underlying undirected multigraph: `cycleRank = E − V + C`. Density uses distinct directed non-self pairs divided by `V(V−1)`; mean out-degree is `E/V`, with zero conventions for empty inputs. R2 predicts forest components by `V−E` independently of the SDK union-find implementation. All 256 path subsets for 0–8 vertices plus a triangle control pass (257 checks). Equal topology can hide different transition types (NC7).

The restricted structural signature, `snad-signature/2`, records ordered unit features, canonical full-occurrence equality partitions of supplied role identities across roles, frame partitions, typed boundary endpoints/kinds, and quotation nesting. Referents are sets: their order and duplicate entries do not change the signature. It omits surface words, source IDs and identity names. R3 enumerates 256 four-unit binary-person/binary-speaker paths and checks bijective speaker renaming plus lexical replacement. Text replacement must preserve quotation nesting. These checks do not establish semantic equivalence. Noninjective identity collapse breaks the invariant (NC6).

The independently commissioned question was whether this signature could recover the original content order of a homogeneous-feature pair with exchangeable speaker names. A two-turn path and its reversal have equal signatures (NC5). This is an intentional representational collision, not a claim that all reversals collide: heterogeneous feature sequences can distinguish direction. Original source units must accompany signatures in an export.

Lexical continuity is Jaccard overlap of lowercased whitespace-token sets. The authored 2×2 lexical-continuity/explicit-speaker-change grid exhibits all four combinations; identical text can contain an explicit speaker change, and disjoint words can retain an attribution state. No speaker identity is inferred from this statistic.

The seeded perturbation forge starts with three typed boundaries. Dropping grammatical features leaves one explicit speaker boundary; masking speakers leaves two grammatical boundaries. Reversal is deterministic, original input remains unchanged, and two-transition motifs count repeated authored paths. Evidence confidence propagates as the minimum supplied grade (or the documented default), illustrated by a 0.2 input grade. It is uncalibrated evidence quality, never probability of speaker truth. Motif counting does not demonstrate induced natural-language grammar.

## Simpler baselines on explicit authored gold

The task is detecting any supplied typed grammatical or attribution boundary between two authored units. Eight nonreligious pairs are labeled before detector evaluation: six positive and two negative. The negative pairs are unchanged text/state and lexical-only change. Positive pairs cover person, speaker, number, tense, addressee, and a combined boundary. These authored cases deliberately exercise supported API dimensions; they are not a Qur'an accuracy benchmark or held-out natural-language evaluation.

| Detector | TP | FP | TN | FN | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| noChange | 0 | 0 | 2 | 6 | 0.00 |
| personOnly | 2 | 0 | 2 | 4 | 0.50 |
| speakerOnly | 2 | 0 | 2 | 4 | 0.50 |
| snad | 6 | 0 | 2 | 0 | 1.00 |

The richer comparator fits its designed contract on this tiny authored set. This does not establish empirical superiority: features and identities are already supplied, class balance is authored, and there is no independent expert gold. English, Arabic and Spanish nonreligious sample utterances are also manually labeled with the same person and speaker paths and produce equal restricted signatures. That demonstrates adapter neutrality with supplied annotations, not automatic multilingual parsing or translation accuracy.

## Original-detector differential and retained mismatches

The source fixture is pinned to ISNAAD commit `4c059a1691920a13ea973146e42518e83f31573c`. The independent implementation reads only input morphology-row person tags for verbs or standalone pronouns, preferring verbs and omitting conflicting principal tags. It does not copy source engine code or its role/weighting heuristics. The SDK then compares adjacent tokens inside the fixture ayah. Original seams were calculated in full-surah context and carry known person across words without principal person evidence and sometimes across ayah boundaries. The scopes differ deliberately.

Nine of 22 cases have equal person-endpoint lists; thirteen disagree. Zero/zero agreement on short or featureless cases is included, so the agreement fraction is not an accuracy metric. Exact original seams, independent endpoints, cross-boundary context and mismatches are preserved in `differential.cases`; no mismatch was deleted or relabeled as a successful reproduction. The fixture also preserves original source counterexamples for a same-person object-suffix heuristic, a distance-summary collision, and mutation/stale annotations. Those fixture observations are not proof that the entire original engine is invalid.

| Locus | Original person seams | Independent adjacent seams | Comparison |
| --- | ---: | ---: | --- |
| 11:29 | 4 | 0 | mismatch |
| 11:36 | 1 | 0 | mismatch |
| 50:2 | 0 | 0 | match |
| 28:4 | 0 | 0 | match |
| 28:5 | 3 | 0 | mismatch |
| 1:1 | 0 | 0 | match |
| 20:1 | 0 | 0 | match |
| 36:1 | 0 | 0 | match |
| 55:64 | 0 | 0 | match |
| 5:116 | 9 | 2 | mismatch |
| 16:64 | 3 | 1 | mismatch |
| 80:34 | 0 | 0 | match |
| 20:108 | 2 | 0 | mismatch |
| 38:15 | 0 | 0 | match |
| 20:132 | 2 | 0 | mismatch |
| 2:45 | 1 | 0 | mismatch |
| 18:76 | 3 | 0 | mismatch |
| 42:28 | 0 | 0 | match |
| 39:56 | 2 | 0 | mismatch |
| 40:23 | 1 | 0 | mismatch |
| 27:9 | 1 | 0 | mismatch |
| 26:208 | 2 | 0 | mismatch |

## Required and independently selected passages

All entries below were analyzed with the same separately sourced feature projection. Their source text and exact transition-kind lists are in `requiredPassages` and `independentSampling.analyses` in the experiment artifact. These are structural extracts with unresolved speaker identity, not tafsir.

| Locus | Source tokens | Feature units | Transitions | Morphology status |
| --- | ---: | ---: | ---: | --- |
| quran:11:29 | 22 | 20 | 0 | partial |
| quran:11:36 | 17 | 16 | 1 | partial |
| quran:50:2 | 11 | 10 | 2 | partial |
| quran:28:4 | 19 | 17 | 2 | partial |
| quran:28:5 | 12 | 11 | 0 | partial |
| quran:105:5 | 3 | 3 | 0 | aligned |
| quran:10:49 | 22 | 21 | 0 | partial |
| quran:13:33 | 39 | 38 | 4 | partial |
| quran:18:2 | 15 | 15 | 1 | aligned |
| quran:2:197 | 29 | 27 | 0 | partial |
| quran:66:5 | 17 | 17 | 1 | aligned |
| quran:83:35 | 3 | 3 | 0 | aligned |
| quran:11:2 | 9 | 7 | 0 | partial |
| quran:21:27 | 6 | 6 | 0 | aligned |
| quran:11:17 | 39 | 38 | 2 | partial |
| quran:7:48 | 14 | 14 | 2 | aligned |
| quran:22:19 | 17 | 15 | 4 | partial |

## Research status and next falsification

The [research register](research-register.md) names each observation, hypothesis, finite reconstruction and negative control with exact JSON references. No new operator beyond established path, partition, set-overlap and graph constructions is claimed. Standard prior art includes path categories and free categories (Mac Lane, *Categories for the Working Mathematician*), graph cycle rank (Diestel, *Graph Theory*), renaming/equality-partition ideas related to alpha-equivalence (Barendregt, *The Lambda Calculus*), and Jaccard's set-overlap coefficient. These contextual references are not a comprehensive novelty search or a claim that discourse signatures equal lambda-calculus alpha-equivalence.

The next empirical experiment is H10: freeze a multilingual held-out annotation protocol, commission independent expert grammatical and attribution labels, keep missingness explicit, then evaluate the 0.90 F1 threshold with all errors retained. Expert annotation, human usability evaluation, recitation/audio checking, morphology accuracy validation and a systematic related-work search remain open. Definitions, finite tests and visual resemblance cannot close those questions.
