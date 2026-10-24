# ULWS / PHONEX — Universal Language Word Sets and Phonetic Exchange Engine

**Research commission ULWS/PHONEX 0.1 · 23 October 2026 · Abed × 7u · for Codex, Muse, and Substrate University**

## Founding scope and non-interference

Create a **lateral cross-language atlas** that preserves and augments the earlier Arabic Timeless, WAZNOMIA, FNMS, Division Infinity, Q-Strings and Substrate University work without editing, overwriting, renaming, or migrating those projects. The user's newer Corpus Engine belongs to Abed and Muse; PHONEX is a standalone service that can export evidence-bearing proposals to it, not edit its internals. Treat language and dialect varieties as first-class, versioned identities, including historical, extinct, unwritten, and community-governed varieties when documentary evidence and data-use permissions exist. The phrase **universal** refers to an extensible schema and aspiration for coverage; it is not a claim that every human language is documented or that sounds universally determine meanings.

## 1. The international sound reference

- **International Phonetic Association / International Phonetic Alphabet (IPA)**: maintained standardized symbol inventory and conventions for transcribing human speech. Distinguish phonemes `/.../` from phones `[...]`, narrow/broad transcription, dialect, stress, length, tone, nasalization and secondary articulation. Official chart: https://www.internationalphoneticassociation.org/node/1061.
- A **letter** is a grapheme; a **phoneme** is a contrastive category in a specific language; a **phone** is a produced sound; one grapheme may represent several phonemes and a language can have no traditional alphabet. Hence never model every language as an alphabet of fixed grapheme→sound pairs.
- ISO 639-3 + BCP 47 language tags, ISO 15924 scripts, and Glottolog's **glottocodes** serve different purposes. Scope a lexical item by variety, dialect/accent, time, register and source; preserve conflicting taxonomies rather than forcibly reconciling them.
- CLTS supplies cross-linguistic sound transcription mappings and features; PHOIBLE provides phonological inventories, not a massive all-word pronunciation dictionary; Wiktionary/WikiPron and other authorized resources provide word-level pronunciations. Language inventories do not automatically resolve pronunciation of spellings.
- For ancient or extinct varieties, label sound representations *attested*, *conventionally reconstructed*, *speculative*, or *unknown*. Do not present reconstructions as audio-measured fact. For signed languages, add a separate non-vocal modality rather than pretending they can be captured by IPA sound transcription.

## 2. Ontological objects: do not collapse four types of likeness

`LanguageVariety(id, glottocode?, iso639_3?, bcp47?, script?, epoch, region, status, identifiers_source)`

`Lexeme(id, language_variety_id, lemma, part_of_speech, etymological_record_ids[], source_refs[])`

`Form(id, lexeme_id, original_surface, script, writing_system, morpheme_boundaries?, epoch, source_refs[], canonical_bytes_hash)`

`Pronunciation(id, form_id, ipa_raw, segments[], level=phonemic|phonetic, accent, dialect, tone, stress, variants, method=human_attested|dictionary_extracted|g2p_predicted|historically_reconstructed, source, confidence)`

`Sense(id, lexeme_id, definition, sense_language, concepticon_id?, domain, glosses[], source)`

`Morpheme(id, form_id, span, morpheme_type, root_or_etymon?, pattern?, licensed_operations[], provenance)`

`Source(id, URI, revision, retrieval_time, checksum, license, attribution, redistribution_allowed, commercial_allowed, cultural_authority, cultural_protocol, access_policy)`

`QRelation(id, roles[], endpoints[], predicate, guard, score_components, epistemic_grade, proof_or_witness, source_ids[], creation_operation, model_version, review_history)`

**Relations that MUST remain distinct:**

1. `phonetic_near`: measured resemblance under a declared tokenizer, metric, scope, threshold and sample.
2. `same_concept`: evidence-supported semantic correspondence, not necessarily translation equivalence.
3. `translation_attested`: source-documented use as a translation in a specified context.
4. `morphologically_related`: language-specific root/derivation claim.
5. `loanword_candidate`: candidate borrowing direction with dated context, donor, and constraints.
6. `cognate_attested`: historical relationship established by comparative evidence.
7. `etymological_hypothesis`: tentative directional path with evidence and alternatives.
8. `homophone` and `false_friend`: similarity but independently identified meanings/histories.
9. `same_rasm_fiber`: Arabic Timeless model-specific positional-dot equivalence.
10. `analogical_only`: permitted traversal with explicit uncertainty, never promoted to genealogy.

A matching score is **not** an etymological posterior probability, unless specifically calibrated on labeled held-out datasets; do not display it as one. Keep separate fields for phonetic distance, translation evidence, known linguistic family, historical compatibility, source quality and confidence calibration.

## 3. Mapping from letters to phonetic sequences

The functions are typed and noninvertible by default:

`segmentGraphemes: (original_surface, writing_system, version) -> grapheme_sequence + alignment`

`G2P: (surface, variety, context, model_version) -> Set[PronunciationCandidate]`

`transcribe: (audio, speaker, context) -> Set[PhoneHypothesis]` [an optional, future trained model; not in first MVP]

`tokenizeIPA: (IPA symbols + combining marks + tie bars + suprasegmentals) -> phone segments + features + uncertainty`

`extractMorphemes: (surface, lexeme, analyzer_version) -> Set[MorphemeParse]`

`projectRasm: (ArabicForm, orthography_chart) -> positional_skeleton + loss_certificate`.

Store Unicode raw bytes and a canonical NFC search view separately. IPA combining diacritics must attach to the correct base; multi-code-point affricates must remain one segment where the transcription says they are. Preserve stress, length, tone, accent and syllable boundaries as independent channels and optionally use controlled ablations. For Arabic, do not strip iʿjām or hamza-bearing forms in the immutable original. The existing Arabic Timeless fold may be used as a named, explicitly lossy projection in its own chart.

**Why phonetic prefix search instead of spelling prefix search:** English `topology`, Arabic `طوبولوجيا` / `توبولوجيا`, and French `topologie` have substantially different original graphemes, but their learned/transcribed phone sequences can be compared. The two Arabic orthographic variants should remain distinct surface forms whose pronunciations depend on a *source-attested variety*. The letter `ط` typically represents an emphatic/pharyngealized coronal stop contrasted with `ت`, but pronunciation and the choice of term must be verified from a real lexicon for each variety. Arabic use of a Greek-derived scientific loan does not entail that the Arabic spelling is an independently derived Semitic-root compound.

## 4. Universal Language Word Set (ULWS)

For query `q`, corpus snapshot `D_v`, metric `d`, matching policy `θ`, and search mode `μ`:

`ULWS(q;D_v,d,θ,μ) = { (w, witness, score): w∈D_v, admissible_μ(q,w), d(q,w)≤θ }`.

The set is a computed **answer view** with a stable snapshot hash. It is neither a universal synset nor a proven genealogical family. Multiple senses or distinct lexemes may appear with identical pronunciations. Support:

- `EXACT_INITIAL`: candidate phone sequence starts with exact query phone sequence.
- `NEAR_INITIAL`: align entire query with a candidate's **initial contiguous prefix**, allowing weighted segment substitutions/insertions/deletions. No scattered-subsequence search.
- `INITIAL_MORPHEME`: match initial morpheme boundaries where actually attested; do not guess boundaries from typography alone.
- `ANY_CONTIGUOUS`: a separately requested mode matching an internal uninterrupted span, indexed by n-grams/suffix array; NOT the default.
- `COMPOUND_PART`: align contiguous multi-morpheme subforms, with a recorded morphological segmentation and permissible transformations.
- `CARRY`: bounded widening of admissible phone variations after finding a new well-attested form. Every widening step must carry a directed witness and penalty. It never globally rewrites source pronunciations.

**Candidate ranking** is multicomponent, never one magic score:

`C_phone = weighted_edit(query_segments, candidate_initial_prefix)` (minimize);

`C_stress`, `C_tone`, `C_length`, `C_morph_boundary`, `C_dialect`, `C_transcription_uncertainty`, `C_extra_hops` are separate, switchable costs;

`Q_source` and `Q_evidence` are positive evidence-quality indicators, not interchangeable with phonetic distance.

Use a fixed, documented weighting function only as a ranking strategy and calibrate it later on known pairs, nonpairs, and family-balanced controls. Provide full alignment paths, edit operations, omitted vowels, original scripts, and proof of actual prefix alignment. Return UNKNOWN if source IPA transcription is missing; G2P prediction, if allowed, must remain visibly predicted.

### 4.1 Carrying sound alternatives

Example: query phoneme sequence starts `/t/`. A source-attested Arabic form begins `/tˤ/`; its shared coronal closure plus secondary-articulation difference can make it a *near phonetic hit*. The hit adds a **candidate expansion proposal** (`/t/ ~ /tˤ/` conditioned on language and score) to the *next-hop search frontier*. It does NOT change the query's original pronunciation to `/tˤ/`, and DOES NOT make the sound change an etymological fact.

At each hop, record `from_id`, `to_id`, exact phone spans, normalized alignment, feature changes, corpus version, cumulative cost, carried constraint and source. Deduplicate visited `(phonetic_variant, query, policy)` states, cap hops/beam width/expansion budget, and avoid feedback loops. Promote a feature transition rule as historical sound change only after multiple independently supported lexical correspondences in a historical lineage.

### 4.2 Query complexity

With `N` pronunciations, maximum/mean length `L`, initial-query length `m`, candidate count `K`, matched length `n`:

- Prefix trie/FST build: expected O(total phone tokens) time and index space, subject to encoding and data structure.
- Exact prefix lookup: O(m + K) to enumerate K postings, not O(1) for enumeration.
- Approximate initial matching: use restricted sound-feature buckets/neighborhood postings + rank top-K; worst-case scan all `N`, DP O(mn) per candidate, so O(Nmn) worst-case.
- An ordinary hash map gives O(1) **expected equality lookup** once a canonical key exists, not O(1) fuzzy search, graph traversal, or output of millions of hits.
- N-gram index / suffix array for optional noninitial contiguous matching. BK/VP trees require a metric; weighted, normalized, directional alignment may not obey triangle inequality; only use verified admissible metric with these indexes. Approximate nearest-neighbor embeddings can return partial results and must report recall.
- Semantic concept index and Q-String hypergraph indexes are separate from phonetic prefix indexes. Avoid constructing all cross-language pairs, which is O(N²). Use posting lists and materialize links lazily or for independently attested relations.

## 5. Provenance and comparative historical analysis

Do not treat an IPA resemblance, a Latin-looking gloss, or a Greek-derived Arabic spelling as proof of common origin or semantic universality. Existing historical linguistics already supplies a comparative method with recurring sound correspondences, direction/chronology, and independent evidence. PHONEX adds a **language-agnostic candidate discovery machine** and explicitly tests whether its phonetic candidate classes predict held-out etymology, borrowing, semantic shifts or recurrent nomenclature. The new proposal challenges candidate-generation limitations, not basic logical requirements for historical evidence.

Evaluation for claims like 'sound combinations have conserved meanings across languages':

1. Form preregistered hypothesis and units: phones, syllables, onset/feature classes, morphemes, semantics, and epoch.
2. Split by language family, geography, domain, lexical item and source document to control leakage.
3. Compare against pronunciation-length-, inventory-, source-size-, and frequency-matched shuffles; account for loanwords and genealogical relatedness.
4. Measure precision@k, recall@k, F1 for known borrowing/cognate/translation labels, calibration error and false-discovery rate under many tested correspondences.
5. Include negative controls (similar sound, different meaning; similar meaning, different sound; same loan across multiple languages) and linguistic expert review.
6. Never elevate a sound similarity score into an etymology claim solely because Arabic morphology yielded an interesting apparent decomposition.

If no supported global semantic regularities are found, the phonetic atlas remains valuable for corpus discovery, typology, pronunciation research, orthographic mapping, and source comparison.

## 6. Database and program architecture

**Immutable acquisition:** `sources/sha256/[hash]` + source manifests (provider, exact version, license, access policy, checksum, dates). No automated redistribution of source that disallows it. Keep raw HTML/audio/IPA source separately by rights tier.

**Normalized tables:** `language_variety`, `writing_system`, `lexeme`, `form`, `pronunciation`, `phonetic_segment`, `sense`, `morpheme_parse`, `concept_alignment`, `evidence`, `qrelation`, `query_run`, `operation_run`, `dataset_manifest`. Use stable surrogate IDs and content hashes for immutable payload snapshots; never make a hash reversible by invention.

**Physical indexes:** SQLite/Postgres B-tree for metadata and source constraints; FST/radix trie for sound prefix, sound-feature neighbor postings for fuzzy first pass, inverted morpheme and concept postings, exact pronunciation hash lookup, phonetic-shingle index for optional internal matching. `QRelation` incidence index supports typed graph traversal; Neo4j is an optional projection, not canonical truth. Parquet/Arrow files may be used for large immutable analytical columns after rights review.

**Computation stages:**

`SourceRegister -> LicenseGate -> LexemeExtract -> VarietyResolve -> PronunciationImport -> IPAValidate -> FeatureMap(CLTS/PanPhon) -> MorphologyCandidates -> PrefixIndex -> PhoneticCandidateQuery -> EvidenceJoin -> WAZNOMIAAnalysis -> QRelationProposal -> ReviewQueue -> Export`.

An unspoken language source with no sound data can still enter the language metadata layer, but must not hallucinate phonetic entries. A language without a conventional writing system can enter using recorded/transcribed speech; source's community permissions still govern use.

**Transducer grammar** (canonical AST, not an informal string interpreted via `eval`):

```
FIND WORDSET FROM "topology"
  LANGUAGE "eng" DIALECT "source-attested"
  TRANSCRIBE REQUIRE ATTESTED
  MATCH PHONETIC INITIAL NEAR FEATURE_PROFILE "phonex-v1"
  ALLOW SECONDARY_ARTICULATION COST <= 0.25
  CARRY MAX_HOPS 2 BEAM 32
  INCLUDE ALL_SENSES, ORIGINAL_SCRIPT, MORPHEMES
  EXPLAIN ALIGNMENTS, PROVENANCE, LOSSES
  LIMIT 50;
```

Start with a grammar that compiles into a **typed query AST** and parameterized SQL/trie calls. Query cannot execute arbitrary Python, external shell, unbounded recursion or network I/O; put resource budgets, RBAC and corpus access policy in the compiler's typechecker. `FIND ETYMOLOGY` should require a different epistemic type and supporting source; `FIND WORDSET` must not silently output derivation assertions.

**Service surfaces:** `phonex` CLI for indexed source import, validation, query, explanation, export; localhost read-only `/v1/wordsets`, `/v1/sounds`, `/v1/lexemes`, `/v1/provenance`, `/v1/query/explain`; authenticated, versioned write/promote endpoints reserved for review process; optional PURL/SEURL resolver mapping stable addresses to frozen snapshots and typed operations. Q-String addresses `qstr:v1:sha256(canonical record)` retrieve content from a store, never 'decode' SHA-256 by inversion.

## 7. Source inventory and licenses: acquisition candidates, not ingested

| Source | Intended role | Source | Key restriction |
|---|---|---|---|
| International Phonetic Association | IPA chart/phonetic standard | https://www.internationalphoneticassociation.org/node/1061 | Chart attributed under CC BY-SA 4.0; chart is not dictionary |
| CLTS / pyclts | sound identity + transcription features | https://github.com/cldf-clts/clts | Check source-level licensing and mappings separately |
| PHOIBLE 2.0 | phonological inventories | https://phoible.org/download | CC BY-SA 3.0; not full lexical pronunciations |
| Glottolog 5.3 | language variety, dialect family, IDs | https://glottolog.org/meta/downloads | CC BY 4.0; taxonomy not pronouncing dictionary |
| WikiPron | Wiktionary-extracted IPA | https://github.com/CUNY-CL/wikipron/releases | Upstream Wiktionary text/dataset rights distinct from Apache-licensed software; verify per data export |
| Wiktextract/Kaikki | lexical forms, pronunciations and etymologies | https://kaikki.org/dictionary/rawdata.html | Wiktionary-derived share-alike/attribution terms; check actual dataset license |
| Epitran | script-to-IPA prediction baseline | https://github.com/dmort27/epitran | Predicted != attested; trained/rule coverage differs |
| PanPhon | articulatory feature edit distances | https://github.com/dmort27/panphon | Weighted distance only one feature taxonomy; tune/validate |
| Lexibank CLDF | cross-language lexicon | https://github.com/lexibank | Per-dataset licensing; individual datasets vary |
| Concepticon | concept identifiers | https://github.com/concepticon/concepticon-cldf | CC BY 4.0; labels not dictionary senses |
| UniMorph | morphological paradigms | https://unimorph.github.io/ | Per-language releases/licenses; not all morphology is root-and-pattern |
| Universal Dependencies | syntax/morphology annotations | https://universaldependencies.org | Per-treebank license and coverage |

**Community governance is mandatory.** Follow CARE principles (collective benefit, authority to control, responsibility, ethics) and respect Local Contexts TK Labels/permissions where applicable. A language being 'under-documented' or 'extinct' does not make source data open. Explicit allowlist, restricted-tier storage and fail-closed export endpoints are mandatory. https://www.gida-global.org/care-principles-copy ; https://localcontexts.org/labels/about-the-labels/ .

## 8. Integration without rewriting earlier sciences

- Arabic Timeless unchanged: send Arabic candidates into its current *rasm-state chart* and store the projection's losses, not its lossy normalization as a source-of-truth identity.
- WAZNOMIA unchanged: supply phonetic candidate groups to root/morphological analysis with status `proposed`; WAZNOMIA returns independently evaluated functional/morphological candidates, not automatic cognacy.
- Muse's Corpus Engine unchanged: export S0 source metadata, S1 attested spans, S2 proposed Form Cards, S3 typed graded edges and S4 operation histories using a dedicated export adapter. No direct writes to its production stores without its versioned schema and Muse's consent.
- Substrate University six divisions and the separately discussed Division IX/Infinity unchanged: register a *new research surface* referenced by QIA, not another numbered university division.
- Q-Strings reuse evidence-bearing typed hyperedge semantics, not physical entanglement claims; any names `QUANTUM` or `SUPERPOSITION` remain analogy-only unless a genuine quantum formalism is supplied.

## 9. Verification gates and milestones

**A: Corpus contract.** Source inventory with exact license, fingerprint, glottocode/script metadata and policy labels; refuse unsupported imports. Unit fixtures include no fictitious 'real' attested IPA.

**B: Sound pipeline.** Unicode IPA segmentation, tie-bars, combining diacritics, tone/stress/length, no destructive normalization; test bilingual/loanword/dialect variation and G2P uncertainty.

**C: Indexed candidate query.** Exact and near-initial prefix matches; every result includes witness and original form. Assert **no noninitial substring matches** under `INITIAL`. Compare against brute-force reference on small held-out corpus to measure approximate-candidate recall.

**D: Carry and graph.** Two-hop bounded search, best-path witness, dedup, no score laundering; sound similarity never automatically implies translation, cognate or inheritance.

**E: WAZNOMIA and Timeless adapters.** Versioned JSON envelopes and loss statements; Arabic dot-state computation only on requests and under a declared historical/orthographic chart.

**F: Benchmark.** Real data, reproducible machine specs, build time, wall/CPU latency p50/p95/p99, RSS + on-disk index bytes, peak ingest memory, recall@k, language/dialect coverage, false positives, by-language family macro average. Compare at least unindexed linear baseline vs SQLite prefix vs FST plus candidate refinement, and with/without phonetic feature carrying. **No universal O(1) claim**.

**G: Deployment.** Separate VM directory, nonroot user, container or venv, loopback-bound API with authentication when exposed, resource budget, pinned source manifests, checkpoint/resume, monitoring, rollback. No DNS or public network changes without authorization. Existing services untouched.

## 10. Testable new scientific hypotheses

- **H1 (initial-phone carrying):** An articulatory-feature-aware prefix index increases cross-script loanword candidate recall over exact IPA prefixes at a tolerable precision loss.
- **H2 (cross-channel witnesses):** Arabic Timeless rasm + articulation + WAZNOMIA morphology jointly improve rank of independently attested candidate sets relative to any one channel, tested with ablations and held-out lexemes.
- **H3 (phonetic nomenclature bridge):** Morphologically analyzed cross-language loanwords yield independently reproducible function labels more frequently than matched unrelated sound-alikes. Reject or revise if not significant.
- **H4 (universal sound–meaning):** Only treat this as a hypothesis to falsify; control language families, areal contact, borrowing, lexical frequency and repeated tests. Do not assert a universal correspondence from a handful of appealing names.

**Status:** This file is a research design; the included `src/phonex.py` is a small stdlib-only, illustrative offline reference with deliberate incomplete candidate generation. No external datasets were downloaded, no Oracle VM commands executed, and no changes made to Arabic Timeless, QIA, Muse's corpus or Substrate University.
