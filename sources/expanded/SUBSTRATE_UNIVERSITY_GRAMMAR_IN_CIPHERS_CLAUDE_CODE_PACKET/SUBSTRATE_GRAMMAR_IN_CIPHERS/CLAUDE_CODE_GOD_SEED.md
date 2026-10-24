# GOLDEN SEED COMMISSION
## SUBSTRATE UNIVERSITY × GRAMMAR IN CIPHERS
### The Twenty-Nine: A Computational and Literary Atlas of the Whole Qur'an

**To:** Claude Code, acting as research architect, mathematical editor, text conservator, literary compositor, and full-stack publication builder.

**From:** Research commission of Abed Kadan, with 7u research synthesis, 2026-10-22.

**MANDATE:** Do the work. Do not answer with a generalized proposal, a short PRD, or an attractive prototype that omits the text and mappings. Create an inspectable, source-verified and genuinely typeset **complete-Qur'an atlas and original book** grounded in the 29 opening **cipher sites**. The university already has a constitution and divisions; **do not restructure or modify it** to implement this commission. Build a separate research/publication workstream and import University principles *read-only*. Do not deploy, change domains or amend old book projects without authorization. A concise final report with paths and testing evidence is required.

**LANGUAGE:** Communicate with author in English. Preserve original Qur'anic Arabic and proper orthography. The literary voice of existing `لؤلؤ العربية` is inviting colloquial Palestinian/Jordanian Arabic for general readers, not dry technical prose; create a compatible **Arabic narrative edition** for this new sibling work, alongside high-quality English scholarly introduction, atlas labels, definitions, and a parallel bilingual navigation layer. If resources limit full bilingual prose, privilege the Arabic complete manuscript, with English overview and full navigational apparatus.

**PRIMARY READ:** Read all companion packet files before editing anything: `AUTHOR_INTENT_DOSSIER.md`, `FORMAL_LEDGER.md`, `29_cipher_sites.json`, `cipher_alphabets.json`, `research_edges.json`, `SOURCES_AND_BOUNDARIES.md`. This seed is independently intelligible, but the sibling files provide machine-readable records. Every proposed pattern here is an object to test, not a revealed theological fact.

---

## 1. Immediate governing invariants

1. The canonical Arabic text is a **read-only, byte-verified source**, never generated from a model or silently corrected. Import licensed source directly from `akadaan310/assufrciphertheory/data/quran/` with its code, citation, checksum and attribution conditions. Use macros/reference lookups for all displayed ayat; do not transcribe them into templates. Verify recitation/narration/edition before comparisons.
2. **29 surah sites** in Qur'an order; **30 independent verse-level opening units** because `42:1=حم` and `42:2=عسق`; **14 distinct unit sequences**; **78 opening-letter tokens**; **14 cipher base letters** and **14 complementary in-cipher base letters** out of the conventional 28-letter alphabet. Surah-level grouping also yields **14 distinct opening configurations**, but their segmentation differs; do not conflate these distinct type systems.
3. Four Sin-bearing unit *types* `يس`, `طس`, `طسم`, `عسق`, but **five Sin-bearing occurrences**: `26:1`, `27:1`, `28:1`, `36:1`, `42:2`. Four are in ayah 1 and one (42:2) in ayah 2. `عسق` is the sole second-verse opening unit among these sites.
4. Seven Hawamim: surahs `40–46`, each with `حم` in verse 1, and the Shura branch `42:2 عسق`. Preserve distinct nodes for all 7 **حم** witnesses and for the separate **عسق**.
5. Anchor the user's expression **جمالة الصفر** (*the beauty of the cipher*) and the proposal **Grammar in Ciphers / Cipherable Grammars / In-Cipher**. Cipher and in-cipher are **house-defined research registers**, not secret proven meanings of revelation. A proposed symbolic reading is distinct from ordinary Arabic grammar, transmitted tafsir, and canonical qiraat.
6. Keep an explicit **epistemic type** for every statement: `VERIFIED_TEXT | OBSERVED_STRUCTURE | STANDARD_MATHEMATICS | HOUSE_DEFINITION | AUTHOR_READING | COMPUTATIONAL_HYPOTHESIS | TESTED_HYPOTHESIS | COUNTEREXAMPLE | OPEN_QUESTION | AUDIO_UNCERTAIN`. Never promote a category without evidence.
7. The full-Qur'an result means **all 114 surahs and every ayah of the edition indexed and reachable**; it does not mean fabricating 6,000+ interpretations. Build the complete coverage index and carefully authored, verified readings (~100 target), anchored by the 29 opening sites and their typed reach into other surahs.

---

## 2. READ THE REAL SOURCES FIRST: read-only research reconnaissance

Search/review linked user GitHub repositories in this order:

| Repository | Exact files or targets | Reason |
|---|---|---|
| `akadaan310/abedkadaancom` | `src/content/registry.ts`, `types.ts`, `topics/*`, `src/math/{bridgeGrammar,fold,matrix,addressCompiler}.ts`, `README.md`, `docs/UNIVERSITY_REBUILD.md` | **Substrate University** canonical typed divisions & methods |
| `akadaan310/assufrciphertheory` | `README.md`, `TERMS.md`, `PROVENANCE.md`, `data/sites_input.json`, `data/sites.json`, `data/quran/`, `lab/{quran,sites,experiments,build}.py`, `tests/test_invariants.py`, `book/chapters/` | The **existing 29-site registry**, verified Qur'an text, recitations, protected terms, dozens of research records; do not destroy the predecessor book |
| `akadaan310/computationalgrammartheory` | `DEFINITIONS.md`, `FORMAL_MODELS.md`, `HYPOTHESES.md`, `RESULTS.md`, `COUNTEREXAMPLES.md` | CGT operation grammar, transition relations, syntax/semantics/execution separation |
| `akadaan310/grammarinnumbers` | `DEFINITIONS.md`, `FORMAL_MODELS.md`, `NUMBER_GRAMMAR.md`, `ARITHMETIC_GRAMMAR.md`, `COUNTEREXAMPLES.md` | GiN value/numeral/encoding/machine layer, admissibility, numerical change and inversion |
| `akadaan310/substrates` | `README.md`, `substrates/s0_substrate.py` through `s4_universe.py` | Bottom-up substrate, coupling, topology, mediation, bounded spaces |
| `akadaan310/substrateIO` | `research/ONTOLOGY.md`, `research/CHARTER.md` | Secondary ontological vocabulary, if available |

Inspected branch examples as of commission: University `claude/new-session-xd8auu`, cipher theory `ccr-6bf87543-8lv1az`, CGT `ccr-04ad16b1-q42wck`, GiN `claude/happy-newton-r2t17c`, substrates `claude/minimal-adaptive-topology-nzeu63`. **Verify current branch HEAD/revisions instead of assuming these are the latest authoritative branches.** Read full source and protected vocabulary before design. Preserve old decisions unless author explicitly supersedes them.

Current site registry defines six realized divisions (see next section). The author's Division IX / Substrate University and Division Infinity framework have separate prior conceptual status, but were not located as a complete canonical specification in the inspected source paths. Search current repo branches/documents, user-provided artifacts, and relevant documentation; do not invent nonexisting 7th and 8th divisions. If absent, mark Division Infinity mappings as **house proposal pending source**. No requirement to change the public campus architecture, existing six doorways, or historical book titles.

For each source record `repository, file path, revision SHA, text edition, license, retrieved_at, usage`. If inaccessible, explicitly mark gaps; never hallucinate contents.

---

## 3. University methodology mapping — typed, non-destructive

Use University methods as **adapters** for research results; an integration matrix must be generated. This is not a new administrative division.

| Source division | Operations | Book/atlas realization |
|---|---|---|
| I. Foundations of Computation | labelled transitions, admissibility language, equivalence, graph theory, CGT cost | formal machine for cipher transformation paths and evidence status |
| II. Relational & Generative Mathematics | alphabets, tower grammars, `Ingrammatica`, folds/unfolds, constructive admission, cycles | `C ⊔ I`, the 29-site indexed alphabet, graph of Sin witnesses, Hawamim tower, reverse counts |
| III. Programmable Computational Languages | typed machines, PURL/SEURL addressability, compilation | permalinks `quran://42/2?layer=cipher`, machine-verifiable paths, printable provenance addresses; **URI is representation, not Qur'anic content** |
| IV. Geometry, Physics & Representation | topology, rank/image/kernel, projection loss, frames | visual graph plates, cave/dog observer topology, mapped/forgotten information, place/habitat geometry |
| V. Acoustic & Generative Sciences | pronunciation/phonetics, signal vs symbol, intervals | strict separation of rasm, letter names, recitation, qiraat, phonetics and Uthmani vocalization |
| VI. Computational Worlds & Emergence | states/agents, spatial field maps, automata, world loom | typed place graph (valley, mountain, cave, land, city, Egypt), event/voice/state diagrams |
| Division IX / meta-university author proposal | organization and cross-division field maps | use as **research meta-index** only if recovered from constitutional source; never claim a deployed existing 9th faculty |
| Division Infinity (proposed or recovered) | bidirectional relational/categorical traversal, lifting/projection, new substrates from intersections | **candidate crosswalk**, documented formal definitions and evidence needed before canonical adoption |

### The substrate below a substrate

Represent every discovery as a **typed witness unit** `W = (address, datum, representation, rule, evidence, uncertainty, provenance, version)`. A letter is a symbol; a site is a position; a relation is an edge; a transition is an action; a reading is a derived interpretation. Do not use *unit* as a generic undifferentiated record: each has its own type and admissibility laws.

Apply the existing CGT operational grammar `G=(Σ, 𝔄, ⟦·⟧, ℒ)`, and GiN's four evaluation layers `syntax → typing → semantics → execution`. Every claim must specify source and target object sorts (e.g., `Glyph → Glyph`, `Verse → Verse`, `Location → Location`, `OrdinalClaim → OrdinalClaim`, `Lemma → Lemma`, `AuthorReading → BookPlate`). An invalid type coercion is evidence of **mapping failure**, not a discovery.

---

## 4. The alphabet constitution

`A28 = ['ا','ب','ت','ث','ج','ح','خ','د','ذ','ر','ز','س','ش','ص','ض','ط','ظ','ع','غ','ف','ق','ك','ل','م','ن','ه','و','ي']`

`C14 = ['ا','ح','ر','س','ص','ط','ع','ق','ك','ل','م','ن','ه','ي']` — the **Cipher alphabet**.

`I14 = ['ب','ت','ث','ج','خ','د','ذ','ز','ش','ض','ظ','غ','ف','و']` — the complementary **In-Cipher alphabet**.

`A28 = C14 ⊔ I14`, `C14 ∩ I14 = ∅` and `|C14|=|I14|=14`.

**Source-critical guard:** This is the conventional base-letter inventory, not a partition of arbitrary Unicode glyphs. `أ/إ/آ/ٱ`, `ى`, `ء`, `ة`, marks, ligatures, grapheme clusters, and reading/pronunciation features need named, independent profiles. `ة` is not silently turned into `ه` for an interesting count. Distinguish lam–alif, ligatures, orthography and diacritic signs from independent abstract letters. Arabic 28-letter inventory is a chosen editorial standard, not a claim that all orthographic systems have 28 distinct Unicode characters.

Let 29 ordered opening sites be a **site alphabet** `S29` with distinct tokens `s_1…s_29`; let the 30 verse expressions be `U30`, and let `T14` be the set of distinct unit letter strings. Do not say "29 distinct cipher letters": a site is a location-token; an element of C14 is a letter-type. Model separately `site → sura → unit → grapheme index → normalized letter`, all with provenance.

### All 29 sites, authoritative expected inventory

| Site | Sura | Opening unit(s) | Verse location(s) |
|---:|---:|:---:|---|
| 01 | 2 — Al-Baqarah | **الم** | 2:1 |
| 02 | 3 — Ali Imran | **الم** | 3:1 |
| 03 | 7 — Al-Araf | **المص** | 7:1 |
| 04 | 10 — Yunus | **الر** | 10:1 |
| 05 | 11 — Hud | **الر** | 11:1 |
| 06 | 12 — Yusuf | **الر** | 12:1 |
| 07 | 13 — Ar-Rad | **المر** | 13:1 |
| 08 | 14 — Ibrahim | **الر** | 14:1 |
| 09 | 15 — Al-Hijr | **الر** | 15:1 |
| 10 | 19 — Maryam | **كهيعص** | 19:1 |
| 11 | 20 — Ta-Ha | **طه** | 20:1 |
| 12 | 26 — Ash-Shuara | **طسم** | 26:1 |
| 13 | 27 — An-Naml | **طس** | 27:1 |
| 14 | 28 — Al-Qasas | **طسم** | 28:1 |
| 15 | 29 — Al-Ankabut | **الم** | 29:1 |
| 16 | 30 — Ar-Rum | **الم** | 30:1 |
| 17 | 31 — Luqman | **الم** | 31:1 |
| 18 | 32 — As-Sajdah | **الم** | 32:1 |
| 19 | 36 — Ya-Sin | **يس** | 36:1 |
| 20 | 38 — Sad | **ص** | 38:1 |
| 21 | 40 — Ghafir | **حم** | 40:1 |
| 22 | 41 — Fussilat | **حم** | 41:1 |
| 23 | 42 — Ash-Shura | **حم عسق** | 42:1, 42:2 |
| 24 | 43 — Az-Zukhruf | **حم** | 43:1 |
| 25 | 44 — Ad-Dukhan | **حم** | 44:1 |
| 26 | 45 — Al-Jathiyah | **حم** | 45:1 |
| 27 | 46 — Al-Ahqaf | **حم** | 46:1 |
| 28 | 50 — Qaf | **ق** | 50:1 |
| 29 | 68 — Al-Qalam | **ن** | 68:1 |

All canonical Arabic inscriptions must come from the live locked corpus at compile time; above is a metadata expectation for comparison. In particular 42 has **two units**, not an embedded one-verse five-letter string.

### Frequency invariants (opening-unit letters only)

`ا:13, ل:13, م:17, ص:3, ر:6, ك:1, ه:2, ي:2, ع:2, ط:4, س:5, ح:7, ق:2, ن:1`; sum = **78**. Test against the connected project's source at the targeted SHA and again at any revised canonical HEAD.

### Morphological boundary examples

- `النمل` (27:18): `ا ل ن م ل` = all **C**.
- `النحل` (16:68): `ا ل ن ح ل` = all **C**.
- Their difference is exactly **one substitution** `م ↔ ح` at a single internal position — both already cipher letters. Both are insects with collective behavior; ant and bee literary scenes differ. Compare against matched single-letter word-pairs and frequencies **before** making an enrichment claim.
- `صنع` (27:88) = `ص ن ع` = all **C**.
- `صرح` (40:36) = `ص ر ح` = all **C**; its shared cipher membership does not establish a secret etymology.
- `الفتية` (18:13) crosses C/I and retains an explicit non-base orthographic ending `ة`.
- `صنوان` (13:4) contains in-cipher `و` among cipher letters. Its contrast with `غير صنوان` is a lexeme/semantics relation, separate from the letters.
- Stripping `الـ` (itself two cipher letters) could substantially change class proportions. Test unsegmented and segmented forms, surface and lemma.

---

## 5. A formal language of Cipherable Grammar

Define typed carriers `Glyph`, `OpeningUnit`, `SurahSite`, `Verse`, `Token`, `Lemma`, `Morph`, `QiraatWitness`, `CountAssertion`, `Speaker`, `Location`, `Habitat`, `Event`, `Representation`, `Reading`, `Evidence`.

Propose the following **operator signatures** and build an extensible grammar with type checking:

```text
SUBSTITUTE(glyph_position, from_C_or_I, to_C_or_I): OpeningUnit -> CandidateUnit
EXTEND(suffix): OpeningUnit -> CandidateUnit
PROJECT_LAYER(profile): TextWitness -> Representation
LOOKUP_WITNESS(candidate): CandidateUnit -> Set[OpeningUnit]
SHARE_LETTER(a,b): Unit×Unit -> SharedGlyphWitness
FOLD(path)/UNFOLD(folded): Path <-> EncodedPath      [lossless only with proof]
PAIR/ORDER/INDEX/REVERSE: CountAssertion -> CountAssertion
INTERPOSE(event,interval): EventSequence -> CandidateEventSequence
TEMPORAL_COMPARE(e1,e2): Event×Event -> TemporalRelation [requires independent evidence]
CIPHER_MASK(normalization): Token -> Vector[C|I|EXTRA]
MORPH_COMPARE: Token×Token -> Lemma/MorphWitness
PLACE_BRIDGE: Verse×Verse -> SpatialAnalogy [typed positions; no site identity]
IMAGE_KERNEL: RichRepresentation -> ProjectionWitness [record lost data]
AUTHOR_READING: VerifiedPath -> CandidateLiteraryPlate
COUNTEREXAMPLE_SEARCH: CandidateClaim -> EvidenceReport
```

Every transformation has a reversible/no-inverse marker, set of preconditions, type signature, source/target witnesses, calculation, validity class, counterexample search, and complexity profile. Preserve distinct **glyph equality**, **word morphological relation**, **semantic analogy**, **temporal relation**, **speaker reference**, **editorial insight**. Do not smuggle semantics through character substitution.

### Cipher, in-cipher, in-grammar and anti-grammar are *not the same operation*

`C14` and `I14` are base-letter complements. `L_in` may be the language generated *within* the I14 subsystem. A genuine `L_anti` must declare which base language it negates/contrasts and how. The complement of a formal language `Σ* \ L(G)` is not equivalent to using complementary **letters**. Expose these as distinct computational experiments and explain their meaning to ordinary readers without equations in the main story.

### Primary Sin graph, non-negotiable

```text
36:1  يس   -- SUB(ي→ط at position 1) --> 27:1 طس
                                              | \
                                              |  \-- EXTEND(م) --> 28:1 طسم
                                              \----- EXTEND(م) --> 26:1 طسم
42:1  حم   -- NEXT_VERSE, preserve seam --> 42:2 عسق
                                            \ shared س with all four first-ayah instances
19:1  كهيعص -- shared ع --> 42:2 عسق -- shared ق --> 50:1 ق
38:1  ص    -- shared ص --> 19:1 كهيعص
68:1  ن    -- singleton analogue --> 50:1 ق
```

**NOTE:** 42:2 shares **س** with the four first-ayah occurrences but not “three occurrences”. When grouped by type instead of occurrence, the count is three *other types* (يس، طس، طسم). Treat the author's "three pillars" as **ع–س–ق itself**, distinct from the cardinality of other Sin-bearing types.

---

## 6. Deep exegesis-adjacent research threads — keep each source separate

These are seeds for **جمالة الصفر** literary readings with robust epistemic disclosure, **not** new scripture, tafsir, or claims of divinely intended mathematical encoding.

### Thread A — Ant → Bee → Youth → Geography

- **27:1 طس / 27:18**: the ant, valley (`واد النمل`), homes (`مساكنكم`), speech, shelter, awareness; distinguish the plural collective `النمل` and individual `نملة`.
- **16:68–69**: the bee (`النحل`) and houses in mountains, trees, built structures. 16 is **not** one of the 29 ciphred surah openings; that's exactly why an atlas needs whole-Qur'an reach. `النمل` ↔ `النحل` differs by a single base letter substitution `م ↔ ح`; retain source geography distinct.
- **18:9–22**: cave/youths, shelter, sleep, group speech, dog at threshold, elapsed time and reported cardinalities. Do **not** claim the cave is expressly on a mountain or the youths are invisible.
- **26:1 طسم / 26:225**: poet's `واد` shares valley lexeme with 27:18, but contexts differ; **26:1 طسم** extends 27:1 **طس**. The two independent edges create a tractable relational cycle.
- **30:1 الم / 30:3**: `أدنى الأرض` and Romans; do not turn figurative earth-position similarity into a shared coordinate. `أدنى` is contextually near/nearer or lower according to interpretation; avoid insisting on a topographic depth that the text has not specified.
- **27:88**: mountains imagined still but moving like clouds; `صنع` all C; geometry, perception and image/kernel form a **representation experiment**.
- Distinguish **Egypt, city, town, land, valley, mountains, cave, home, entrance and sky** as spatial category nodes, not a shared physical place. Use `PLACE_BRIDGE` with stated relation and uncertainty.

### Thread B — Two, Three, Seven, Eight; the question of speaker and time

- **36:14**: two sent, rejected, reinforced with a **third**, and collective **فقالوا إنا إليكم مرسلون**. The verb relates a speaking group. There is no date for when the third joined; simulation `18 → 27 → 36` is a **counterfactual numerical illustration**, not a historical claim.
- **18:19**: one of the young men asks `كم لبثتم`, group says `لبثنا يوما أو بعض يوم`, then `ربكم أعلم بما لبثتم`. **Duration** is the explicit question; spatial substrate reframing is an experimental metaphor, not translation.
- **18:18**: youths sleeping/being turned; dog extending its forelegs at the threshold. `لو اطلعت عليهم` refers to **them**, the youths — no scriptural claim of optical invisibility. A **dog-observer-index** model can be a literary simulation marked as such.
- **18:22**: reported sequences `3 → dog 4`, `5 → dog 6`, `7 → dog 8`. Invert *reported ordinal relations* `8→7`, `6→5`, `4→3` as computational grammar, not recovered actual youth count. Preserve `رَجْمًا بِٱلْغَيْبِ`, `قُل رَبِّي أَعْلَمُ بِعِدَّتِهِم`, `مَا يَعْلَمُهُمْ إِلَّا قَلِيلٌ` as the epistemic center.
- **6:143–144**: `ثمانية أزواج` and male/female groupings — eight as a different **number grammar**. Never equate the counted entities with the youths/dog.
- **12:30, 12:36, 18:60, 18:10–22**: grammatical chain `فتاها / فتيان / فتاه / الفتية`; distinct people and narratives; compare morphological number, possession, speaker deixis and social setting. One particularly clear real dual is `فتيان` in 12:36.
- Use GiN to distinguish **cardinal numeral**, **ordinal**, **numeral word**, **speaker count**, **reported conjecture**, **counting backward**, and **time interval insertion**. A syntactic parallel is not proof of same historical group.

### Thread C — The seven حم tower, the second-verse branch, and the صرح

- Draw seven vertical levels: 40 through 46 inclusive, each opening with **حم**. At level 42, a branch or inner chamber with **42:2 عسق** emerges. Nodes are verse-located and remain separately addressable.
- Bring in **19:1 كهيعص**, **20:1 طه**, **50:1 ق**, **68:1 ن**, **38:1 ص** through explicit shared-letter or singleton graph relations. Preserve 7 vs 8 **as author-proposed numerical/structural bridges**, not forced equivalence.
- **40:36–37**: Pharaoh's **صرح** and the pathways (`الأسباب`) of the heavens. The metaphor of a *tower exposing letters* may accompany a beautiful visual plate, but **do not** claim the historical ṣarḥ had seven storeys or encodes the Hawamim.
- **15:87** seven oft-repeated **سبعا من المثاني**. Include as the author's analogy but **do not identify it as the seven Hawamim in the literal text**.
- The author's audio included ambiguous fourfold `طه/ه` enumeration, a claim about `هيهات هيهات` at **23:36**, and **صنوان وغير صنوان** at **13:4**. Preserve uncertain statements as **AUDIO_UNCERTAIN** until groundable. Analyze **ح** vs **ه** as different base letters.
- A secondary plate: 13:1 **المر**, 13:4 **صنوان وغير صنوان**, 30:1 **الم**, and 27:88 **صنع**. The existing repository's "Mim diving" house rule is **المر (13)**, not **الم (30)**; preserve editorial provenance.

### Research question behind the book

What can a *typed, reproducible, falsifiable* system of cipher-site transitions, character complements, morphology, number grammar, space/topology and narrative perspective actually **do** — and which visually suggestive bridges fail under baseline or reveal a counterexample? The book must celebrate both fertile correspondences and the discipline of rejecting unsupported ones.

---

## 7. Data model and storage contract

Use **versioned JSON/JSONL + deterministic generators** and a relational database only if necessary; do not put canon source text into manually editable records. Minimum types:

```typescript
export type Epistemic =
  'VERIFIED_TEXT' | 'OBSERVED_STRUCTURE' | 'STANDARD_MATHEMATICS' |
  'HOUSE_DEFINITION' | 'AUTHOR_READING' | 'COMPUTATIONAL_HYPOTHESIS' |
  'TESTED_HYPOTHESIS' | 'COUNTEREXAMPLE' | 'OPEN_QUESTION' | 'AUDIO_UNCERTAIN';
export type Unit = {
  id: string; siteId: string; sura: number; ayah: number; unitOffset: number;
  canonicalTextRef: string; seqBaseLetters: string[]; graphemeSeq: string[];
  edition: string; sourceRevision: string; normalizationProfile: string;
};
export type WitnessEdge = {
  id: string; fromId: string; toId: string; relationType: string;
  inputTypes: string[]; outputType: string; operatorId: string;
  sourceRefs: string[]; evidence: Epistemic; assumptions: string[];
  explanation: string; falsifier?: string; counterexamples: string[];
  computation?: {script: string; resultHash: string; baselineId?: string};
};
export type BookReading = {
  id: string; titleAr: string; titleEn: string; verseRefs: string[];
  pathwayIds: string[]; authorReading: string; verifiedQuotes: string[];
  epistemicLabels: Epistemic[]; counterReading?: string; editorialStatus: 'DRAFT'|'REVIEWED';
};
```

Minimum records: `QuranEdition`, `Surah`, `Verse`, `Word`, `Grapheme`, `CanonicalUnit`, `Site`, `CipherType`, `LetterType`, `TextWitness`, `Reading`, `Rule`, `Transformation`, `Edge`, `Place`, `Speaker`, `Event`, `CountAssertion`, `TimeRelation`, `ManuscriptPlate`, `Provenance`.

**Indexes:** `sura:ayah`, `site_id`, `unit_ref`, `base_letter`, `cipher_type`, `lemma`, `morph`, `edge_type`, `evidence`, `qiraat`, `plate_id`, `location_type`. Build a lightweight visual search/graph explorer but **a book is primary**. Every verse view should reveal exact Arabic, its surah/ayah, basic lexical view, presence/absence of mapped links, and status of any editorial interpretation.

**Normalization:** store `raw_uthmani`, `simple_clean`, `base_letters`, `rasm_approx`, `morphological_segmentation`, `recitation` in **distinct** read-only or derivative fields. Never overwrite any one with another. One authoritative Qur'anic text edition in main print, with explicitly identified alternative witness layers in appendix.

**Data path** for outputs in a new independent workspace (prefer `grammar-in-ciphers/`, unless an existing author-owned project specifically named for this work already exists):

```text
grammar-in-ciphers/
  source/README.md                # immutable sources, URLs, SHAs, licenses
  source/text/README.md           # instructions to materialize licensed original text, NOT generated text
  research/constitution.md        # definitions, rules, decisions, open questions
  research/authors-notes.md       # dossier, uncertain audio mapping
  research/claims.jsonl           # sourced claims with evidence classes
  data/sites.json                 # 29, verified
  data/units.json                 # 30, exact verse positions
  data/cipher_alphabets.json      # C14 and I14
  data/all_verses.jsonl           # 114 surahs/all canonical ayats with text pointers
  data/edges.jsonl                # typed verse/unit/lexeme links
  data/verse_coverage.jsonl       # one record for every verse
  data/readings.jsonl             # original editorial ~100 readings, cited
  data/counterexamples.jsonl      # null/failed experiments preserved
  experiments/                   # baseline, exact counts, grammar transforms
  scripts/                       # deterministic ingest, validation, build
  book/manuscript/               # human-authored story & book chapters
  book/plates/                   # legible print-ready diagrams
  book/typography.md             # Arabic shaping/font/license/style specifications
  atlas/                         # navigable book-like static web reader
  builds/                        # print-ready PDF, EPUB if validated, HTML
  tests/                         # invariants, text integrity, rendering
  reports/                       # findings, limitations, coverage, final report
```

No unspecified user data or external accounts should be exposed. Do not push to a repo, create a PR, or deploy unless available authority allows that operation and the user actually requested it; local/work-branch artifact and final handoff are sufficient. Do not mix the new manuscript with or rename the prior *لؤلؤ العربية* work. If it is appropriate to create a new Git branch, use an isolated worktree and explicit change log.

---

## 8. Build order — execute to evidence, not to appearance

### Phase A — source recovery, audit, canonical checks

1. Inspect all source modules and present repo layout, including `assufrciphertheory/lab/sites.py` and tests. Resolve actual git SHAs.
2. Establish exact text license and file digests. Run existing invariant tests. Do not alter upstream. Collate 29 site records from the existing input; compute the 30 canonical unit objects.
3. Build a full-Qur'an normalized/tokenized index from the locked source. Automatically enumerate all 114 surahs and their verified ayah counts. Verify every verse address occurs once in the expected edition. Use source-defined Kufan numbering, not rough guesses.
4. Emit immutable textual witness signatures and explain different verse numbering/qiraat where relevant.

### Phase B — ontology and 29-site + 14/14 map

1. Create exact C14/I14 partition and projected glyph classes under declared normalization.
2. Create 29 site cards; 30 verse-level unit cards; 14 distinct sequence cards; their appearances and 78 total letter positions. Explicitly display count denominators in captions.
3. Compute co-occurrence matrices, digraph/tower graph, subword containment, partial orders, sequence transformations, character frequency, and shared-letter distances.
4. Build substantive **Sin transducer**, **Ayn-Sin-Qaf branch**, **Hawamim tower**, and **Ant/Bee orthographic substitution** exemplars with verifiable witnesses.
5. Build cross-division maps from six university divisions without altering any of them; inventory every new term as standard versus house term.

### Phase C — whole-Qur'an mapping

1. Index every verse; identify motifs via **full-text**, normalized form, roots/lemmas where grounded, speech roles, numeric assertions, locations, repeated lexical forms and graph traversal.
2. Include **surahs lacking opening letters** as first-class participants in the verse network. All 114 surahs must be navigable, none erased because it lacks a cipher opening.
3. Prioritize direct evidence, author-origin candidate edges, and second-order (typed) paths; do not produce unbounded combinatorial meaningless connections. Include negative examples and absent edges.
4. Every graph edge gets reason, source quote pointer, metadata, type, counterexample, and relevance assessment. Provenance may include comparative qiraat only with source and recension.
5. Run null-model tests and robustness checks (see Phase D) before promoting novel patterns to reader-facing interpretations.

### Phase D — reproducible mathematical experiments

Required: (i) exact count 29/30/14/14/78; (ii) Sin four-type/five-occurrence test; (iii) 7 Hawamim with separate 42 branch; (iv) proposed substitution and extension membership; (v) all-verse letter-mask frequencies and ant/bee/ṣunʿ controls; (vi) cardinal/ordinal/reversal transformations with negative examples; (vii) morphological youth comparison with referent separation; (viii) geography graph; (ix) versioned projections/partial inverse demonstrations; (x) qiraat divergence report; (xi) semantic network baseline with multiple-testing correction; (xii) round-trip source-to-display script/ayah invariants.

Null models: Arabic **letter frequency- and word-length-matched** token controls, article-stripped controls, graph-degree and lemma-frequency-matched rewiring, and unbiased sampling of other one-letter word pairs. Report effect sizes, distributional assumptions, uncertainties and failure cases. Beware selection effects: this book began with the *ant/bee* pair, so significance cannot be inferred from a post-hoc random-word p-value.

**Acceptance: failure is a result**. Patterns may be beautiful author readings even where statistical distinctiveness is unproven; label them accordingly. Never counterfeit validation or change the text to make a theory true.

### Phase E — the book, not just a database

**Working title:** *THE TWENTY-NINE — Grammar in Ciphers: A Substrate Atlas of the Qur'an*. Subtitle/Arabic title to be crafted in harmony with pre-existing *لؤلؤ العربية: الأَولى في اللغات العالمي، الكوني، والحسابي* and `جمالة الصفر` while keeping both books distinct.

Proposed structure, revise only with editorial rationale:

1. **Front gate:** beautiful opening story: ant, bee, fitya, one question about duration and one about number; how a letter can become a boundary, not an unsupported secret.
2. **Book I — Letters and complement:** full 28 alphabet / C14 / I14; 29 sites; type/instance distinction; `النمل`/`النحل` one-letter transition; letters, masks, words, numbers and their limitations.
3. **Book II — The Sin pathways:** 36:1, 27:1, 26:1, 28:1, 42:2; proposed substitution and extension; Ayn-Sin-Qaf in its independent verse; KHYAS, Tā Hā, singleton letters and the 30-unit network.
4. **Book III — Voices, shelter and time:** messengers' 2+1; youth morphological family, cave question, dog, counts, reversal, eight pairs; geography of valley, home, cave, mountains, city and earth.
5. **Book IV — Seven towers and the frame of perception:** Hawamim 40–46, branch 42:2, Pharaoh's ṣarḥ as literary tower, visual geometry/image/kernel, perception of mountains, math of symbolic and physical towers.
6. **Book V — The 114-surah atlas:** 114 substantial navigable surah leaves; all ayats addressable, exact text references, site-opening classification where present, crosswalks to other surahs, no invented cipher marking for non-opening surahs.
7. **Book VI — The 29 plates:** each individual opening site has a dedicated beautiful plate, not a generic repeated template; include 42:1 and 42:2 separately as **a double plate**.
8. **Appendices:** machine-readable grammar, 14/14 mask inventory, total counts, mathematical proofs/limitations, source and edition bibliography, qiraat witness ledger, counterexample report, research definitions, uncertainty register and transparent reproduction instructions.

**Composition requirements:** at least **~100 carefully chosen `جمالة الصفر` readings** sourced to precise verses across the entire Qur'an and reviewed for textual accuracy; intellectual narrative first, registries/experiment IDs in margin, endnotes or appendices. No indiscriminate claim that each ayah encodes a cipher. Narratives should be striking and readable to a young teenager or a literature scholar. Reader is invited to consider and test, never forced to accept cryptography as revealed fact.

**Design system:** beautifully typeset Arabic with independently verified Uthmani script shaping and right-to-left layout; editorial gold/ink/ivory or dark manuscript palette; large readable verses, smaller narrative paragraphs, delicate copper/gold rules, clear English secondary glosses; elegant page navigation, 29 collectible opening plates, Sin network foldouts, spatial maps, number-rotation wheels, seven Hawamim tower and C/I alphabet mirror. Use licensed fonts and documented rendering stack; distribute only permitted assets. Do not turn the book into dashboard screenshots. Validate print bleeds, pagination, no orphaned verses, glyph ligatures, bidi marks, text extraction and PDF/EPUB accessibility.

**Outputs:** `THE_TWENTY_NINE_Grammar_in_Ciphers.pdf` (print), `THE_TWENTY_NINE_Grammar_in_Ciphers.epub` when validated, static HTML book/atlas, complete `manuscript/`, machine-readable research registry and `REPRODUCE.md`; all final outputs should have hashes and current source revision. Do not announce completed versions unless files were rendered, inspected and pass tests.

### Phase F — audit and final report

- Report corpus edition, 114-surah/full-verse coverage total, passage linkage counts and missing fields. Show exactly how complete the book and atlas are (not aspirational counts).
- Assertions must include `sites == 29`, `units == 30`, `distinct_unit_types == 14`, `opening_letter_tokens == 78`, `C14 ∩ I14 == ∅`, `C14 ∪ I14 == A28`, `sin_occurrences == 5`, `sin_ayah_1 == 4`, `sin_ayah_2 == 1`, `hawamim_surahs == [40,41,42,43,44,45,46]`, `unit(42:1) == حم`, `unit(42:2) == عسق`, and all source verses byte-verifiable.
- For 18:22, mark 3+4/5+6/7+8 as **reported hypotheses**, not verified actual youth counts.
- For 18:18, reject any script claiming the youths are **literally invisible**.
- For 36:14, reject any fixed numerical dating of third messenger.
- For 15:87, reject a doctrinal equivalence with Hawamim unless separately sourced in scholarship and correctly attributed; even then distinguish viewpoints.
- For ant/bee, show both article-inclusive and article-stripped statistics, not just handpicked cipher-only examples.
- Test `fold/unfold` invariants, operator type checks, non-interchangeability of Arabic Hamza vs ordinary Alif and `ح` vs `ه` vs `خ`, qiraat source scopes, missing/unclassifiable characters, bidi/typographic integrity.
- Provide a named open-questions table for uncertain audio and unresolved Division Infinity formalism.
- **Do not use a fabricated quote or a hallucinated verse** even to make a visually beautiful plate.

---

## 9. The book's philosophical pivot

The author's central observation is not that '29' alone is magical. It is that the same fixed Qur'anic text can be modeled as distinct **validly typed projection spaces**: positions, letters, complements, words, morphologies, speech actors, numbers, intervals, reported knowledge, spatial habitats and inter-surah paths. Each projection retains certain facts and loses others. The intersections may generate new *readings* — but a beautiful visual coincidence is not automatically a theorem.

Do not reduce the author to alphabet numerology or erase the experimental dimension. Equally, do not present conjectures as divinely authenticated facts. The most interesting line in the youth passage for the epistemology of this book is **"ما يعلمهم إلا قليل"** — the verse's own caution about knowledge. Preserve that modesty in the machine, while taking the mathematics and literary exploration as far as the evidence allows.

**EXECUTION DIRECTIVE:** Read the source repositories, build the actual 29-site/cipher/in-cipher map, create the whole-Qur'an typed index, test and document the proposed operators, and compose the reader's book. Keep the University and old book untouched; deliver concrete files, proofs, citations, examples, counterexamples and an honest completion report. Do not stop at planning.
