# SNAD research register, version 1

This register distinguishes observations, conjectural generalization, rejected claims, and finite reconstruction. Its primary evidence is [experiments.json](../evidence/experiments.json), schema `snad.experiments.v1`; JSON references below are field paths or ID predicates within that file. Corpus measurements additionally reference [corpus-status.json](../evidence/corpus-status.json) and [benchmark.json](../evidence/benchmark.json). Fixed inputs and seed 6236 reproduce numerical outputs; runtime and memory are machine observations.

The 20 entries below are supported engineering/fixture candidate observations. They are not 20 mathematical or linguistic discoveries; novel discoveries claimed is zero. Their routine character is retained openly rather than manufacturing findings to fill a stretch target. Evidence status for authored labels means the supplied annotation was observed as an input declaration, not independently verified as a statement about natural text.

## Candidate observations

| ID | Status | Supported statement | Exact evidence field |
| --- | --- | --- | --- |
| O01 | observation | The input fixture contains exactly 6236 records. | `inputSummary.ayahs` |
| O02 | observation | All 114 surahs are represented. | `inputSummary.surahs` |
| O03 | observation | The source fixture includes 204 ayahs below three surface tokens. | `inputSummary.shortAyahsUnder3Tokens` |
| O04 | observation | The independent ranked sample contains twelve passages outside the five prescribed loci. | `independentSampling` |
| O05 | observation | The authored boundary gold has six positive and two negative pairs. | `baselines.examples` |
| O06 | observation | No-change misses six authored typed boundaries. | `baselines.metrics.noChange` |
| O07 | observation | Person-only misses four authored typed boundaries. | `baselines.metrics.personOnly` |
| O08 | observation | Speaker-only misses four authored typed boundaries. | `baselines.metrics.speakerOnly` |
| O09 | observation | The manually labelled three-language paths share the documented restricted signature. | `crossLinguistic` |
| O10 | observation | The 81 finite composable triples agree with independent list concatenation. | `reconstructions.R1` |
| O11 | observation | Forest edge-counting predictions match every enumerated path subset and the triangle control. | `reconstructions.R2` |
| O12 | observation | All 256 generated bijective speaker renamings plus lexical replacements preserve signature. | `reconstructions.R3` |
| O13 | observation | A person transition can leave every speaker unresolved. | `negativeControls.NC1` |
| O14 | observation | Empty and missing features can produce a valid zero-transition analysis. | `negativeControls.NC2` |
| O15 | observation | Identical text can coincide with an explicitly supplied attribution change. | `negativeControls.NC3` |
| O16 | observation | Disjoint text alone does not induce a typed boundary. | `negativeControls.NC4` |
| O17 | observation | A homogeneous-feature two-speaker path can collide with its reversal under the restricted signature. | `selfCommissioned` |
| O18 | observation | Noninjective speaker collapse can destroy structural equivalence. | `negativeControls.NC6` |
| O19 | observation | Equal path topology can conceal distinct typed boundary kinds. | `negativeControls.NC7` |
| O20 | observation | The adjacent-token independent detector and carried-person source detector disagree on at least one pinned case. | `differential.cases` |

`observations[id=Oxx].supported` is true for every retained entry. O01–O04 concern the source domain and sampling, O05–O12 authored contracts/finite models, O13–O19 actual negative-control witnesses, and O20 algorithm/scope disagreement. The observations are not statistically independent results and are not counted as separate novel discoveries.

## Falsifiable hypotheses

Each hypothesis carries `epistemicStatus: conjecture` or `epistemicStatus: rejected`; each O-entry carries `status: observation`. “Finite-support” means only that the stated finite test domain passed; it is not a proof of the universal claim or a new theorem. “Rejected” means the named explicit witness falsifies the universal formulation. “Untested” remains an open empirical prediction with no validating data. H1/H2/H4 are familiar mathematical constructions whose implementation is checked, not claims of original mathematics.

| ID | Status | Claim/prediction | Falsifier | Exact evidence field |
| --- | --- | --- | --- | --- |
| H1 | finite-support | For all composable typed finite paths, concatenation is associative. | A composable triple whose two parenthesizations have different endpoints or edge sequences. | `R1` |
| H2 | finite-support | For every typed path, the empty path at each endpoint acts as identity. | A path changed by composition with its matching empty endpoint path. | `R1` |
| H3 | finite-support | Every bijective identity renaming and text replacement preserves this restricted signature when features, identity partitions, and quotation nesting are fixed. | A generated partition-preserving rename or lexical replacement with a different signature. | `R3` |
| H4 | finite-support | All edge subsets of a simple n-vertex path have n−m weak components and cycle rank zero. | An enumerated path subset with a different weak component count or positive cycle rank. | `R2` |
| H5 | rejected | Many-to-one speaker renaming always preserves structural equivalence. | An A,B,A speaker pattern collapsed to X,X,X changes signature. | `NC6` |
| H6 | rejected | Reversing a nonidentical two-unit discourse always changes the restricted signature. | Homogeneous features and a two-speaker switch produce equal forward/reverse signatures. | `NC5` |
| H7 | rejected | A person-only baseline detects all types of explicitly annotated boundary in the authored gold set. | A gold speaker, number, tense, or addressee boundary missed by person-only. | `baselines` |
| H8 | rejected | Lexical continuity equal to one guarantees no attribution change. | Identical text with an explicit speaker change. | `NC3` |
| H9 | rejected | Topology alone uniquely determines the typed transition sequence. | A person-only path and a speaker-only path with identical topology. | `NC7` |
| H10 | untested | On a preregistered held-out expert-annotated multilingual dialogue set with independently supplied input features, typed boundary detection reaches F1 ≥ 0.90. | Held-out F1 below 0.90 using the frozen input/label protocol. | `No held-out expert corpus, independent annotations, or human validation available; authored examples do not test this claim.` |

The current signature schema is `snad-signature/2`: it uses full identity-occurrence partitions across roles, with referent lists treated as sets. H3 fixes quotation nesting in addition to features and role-identity equality partitions. Inserting quote punctuation can change nesting and therefore lies outside the tested lexical-replacement invariant. H10 requires independent held-out labels; the authored eight-pair baseline cannot satisfy it.

## Independently reconstructed finite results

| ID | Status | Independent construction | Tested domain | Evidence |
| --- | --- | --- | --- | --- |
| R1 | finite reconstruction | Plain-list typed-path concatenation independent of SDK `compose` | 81 composable triples over 3 endpoints; 162 identity checks | `reconstructions[id=R1]` |
| R2 | finite reconstruction | Forest edge counting predicts weak components `V−E`; triangle predicts cycle rank 1 | All path-edge subsets with 0–8 vertices plus triangle, 257 checks | `reconstructions[id=R2]` |
| R3 | finite reconstruction | Enumerated binary person/speaker patterns and an independently applied injective rename | 256 four-unit patterns with lexical replacement and fixed quote nesting | `reconstructions[id=R3]` |

No proof is inferred from enumeration. The results reproduce standard path concatenation, graph forest counting and equality-partition invariance within a restricted representation.

## Negative controls and counterexamples

All seven controls pass their rejection criteria. Their exact authored inputs and output witnesses are retained; none uses a claimed interpretation of the Qur'an.

| ID | Status | Universal claim rejected | Exact witness |
| --- | --- | --- | --- |
| NC1 | rejected universal claim | A grammatical-person change proves a speaker change. | `negativeControls[id=NC1]` |
| NC2 | rejected universal claim | Missing or empty features justify a detected grammar boundary. | `negativeControls[id=NC2]` |
| NC3 | rejected universal claim | Identical words guarantee attribution continuity. | `negativeControls[id=NC3]` |
| NC4 | rejected universal claim | Changed words require a typed grammatical or attribution transition. | `negativeControls[id=NC4]` |
| NC5 | rejected universal claim | A restricted structural signature recovers surface order or speaker names. | `negativeControls[id=NC5]` |
| NC6 | rejected universal claim | Any identity renaming, including many-to-one collapse, preserves structural equivalence. | `negativeControls[id=NC6]` |
| NC7 | rejected universal claim | Graph topology alone identifies the kind of discourse boundary. | `negativeControls[id=NC7]` |

The self-commissioned NC5 witness asks a question not tied to the prescribed corpus examples: whether exchangeable speaker names plus homogeneous features allow surface-content reversal to collide under a restricted signature. The result is a representational collision, not a general statement that ordered feature sequences lose direction. Retain source content alongside signatures.

## Experiment cycle and baseline discipline

1. Observe the explicit feature/identity paths and corpus missingness without filling gaps.
2. Formalize typed path concatenation, role-equality partitions, Jaccard continuity, and weak graph summaries.
3. Predict partition-preserving invariance, known path-forest summaries and baseline blind spots.
4. Perturb via deterministic feature dropping, speaker masking and reversal (`perturbationForge.trials`). The seed is recorded even though these three ablations are deterministic rather than stochastic.
5. Falsify overstrong claims with NC1–NC7, preserving witnesses and the original-source 13 differential mismatches.
6. Compare no-change/person-only/speaker-only/richer typed comparator on authored eight-pair gold (`baselines`). Do not treat contract fit as empirical linguistic accuracy.
7. Retain finite reconstructions, reject false universals, and leave expert-held-out evaluation open as H10.

English, Arabic and Spanish authored nonreligious examples use manual person/speaker declarations (`crossLinguistic`). Equal output signatures establish that the same supplied structure is representable across surface languages. They provide no automatic parser evaluation. Evidence confidence 0.2 in the perturbation fixture is a propagated grade, not a calibrated probability (`perturbationForge.minimumEvidenceConfidence`). Repeated two-boundary motifs are counts, not proof of a natural grammar.

## Corpus boundaries and source comparison

The entire 6,236-ayah domain is covered in `corpus-status.loci`; morphology is partial. Addressable, text-parsed, analyzed, detected, visualized and audio-verified each have their own count and 6,236 denominator. The numerical pass verifies no browser render or audio. The 1,000 legacy selection remains a separate highlight fixture. Exact text is preserved.

`differential.cases` preserves all 22 pinned source cases: 9 equal person-endpoint lists and 13 mismatches. Independent adjacent comparisons and original surah-context carried-person seams answer different questions. That mismatch rate cannot establish either semantic accuracy or an engine regression. Original fixture counterexamples in `differential.originalFailureCases` are kept under their own evidence scope.

## Related work and unclosed questions

These are implementation-level applications of established constructions: path/free categories (Mac Lane, *Categories for the Working Mathematician*), graph cycle rank (Diestel, *Graph Theory*), identity-renaming/equality-partition ideas related to alpha-equivalence (Barendregt, *The Lambda Calculus*), and Jaccard set similarity. This contextual list is not a systematic literature review, and the restricted discourse signature is not claimed to be a linguistic or semantic equivalence theorem. Root project documentation separately audits the candidate Computational Grammar Theory, Grammar in Numbers, SubstrateIO, ISNAAD and integration sources.

Open: held-out expert gold and F1 (H10); quotation cues without typographic marks; alignment/morphology accuracy beyond surface checks; speaker/coreference annotation under partial information; human usability; audio; annotation licensing review for future redistribution formats; temporal-logic/model-checking evaluation; minimized or generalizing grammar models beyond memorized observed strings; systematic novelty review. These are not completed by visualizing a graph or passing finite tests.
