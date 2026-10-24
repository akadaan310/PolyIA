# Corpus Engine — Design (Abed + Muse, 2026-10-23)

POC: `corpus_poc.py` in this folder (runs end-to-end today).

## Data structure — five strata, one graph

- **S0 Sources (immutable).** Every input as-is + SHA-256: website repo files, books
  (Computational Grammar Theory, Grammar in Numbers, …), research zips, Abed's prompts.
  Never edited. Everything else points back here.
- **S1 Spans.** Cleaned text units with stable IDs and provenance (source hash + offsets).
  Two text layers per span: *vocalized* (as authored) and *skeleton* (search-normalized).
- **S2 Form Cards.** The atom. `{id (content hash), term, domain(s), senses[],
  etymons[] {form, language, gloss, function}, sarf {root, pattern, delta},
  pure_function (verb-phrase signature), epistemic_grade}`.
  Seed schema = Substrate University's own glossary type (Term/Sense/status) — extend, don't replace.
- **S3 Edges (typed, directed, graded).** `sense-of · related · bridges · translates-to ·
  derives-from (sarf) · applies-to · contradicts · refines`. SU glossary already ships
  `related` + `bridges`; ingestion lifts them verbatim.
- **S4 Operations.** The deduction machines are corpus citizens, not external tools:
  Ṣarf Machine, Etymon Lens, Circular Bridge, Prompt Lens, State-Lens renderer.
  Every operation run is itself recorded (input hash, operation, output) — provenance all the way down.

Store: JSONL strata + SQLite index for the POC; Neo4j/Cypher export is a projection of
S2+S3, not a rewrite. Maturity metrics: % Form Cards at grade `verified`, bridge density,
orphan count (nodes with no cross-domain edge) — the anti-orphaning gauge.

## Cleaning pipeline (per source)

acquire (hash, register) → extract (per-format: TS/JSX, HTML, MD, PDF, EPUB, DOCX, TXT)
→ normalize (Unicode NFC; Arabic: preserve vocalized layer, skeleton layer strips
diacritics/tatweel; Latin/Greek: case + accent-folded index layer) → segment into spans
→ term mining (glossary-first, then pattern/frequency mining over books) → decomposition
(operations S4) → linking (edge proposals) → epistemic grading
(`established / house / inferred / proposed` — SU's own status vocabulary, extended)
→ review queue for inferred edges → publish (CLI/API/web-form index).

## The feedback operation (how deduction grows the corpus)

Operations never write to S0–S1. A deduction produces **candidate Form Cards / edges** in
a staging area with `epistemic_grade = inferred|proposed` and full provenance
(operation, inputs, timestamp). Promotion: repeated independent derivation, source
attestation in a new stratum, or human sign-off → `verified`. Corpus size grows by
ingestion; corpus **maturity** grows by promotion. The lens reads only the graph,
so every promoted deduction immediately informs every future prompt analysis.

## Arabic nomenclature — the decipher key

Arabic scientific coinage uses three visible strategies, all machine-readable:
1. **اشتقاق (sarf derivation)** — e.g. تشاكل *isomorphism* = Form VI of شكل (mutual form!),
   اشتقاق *derivation* itself = Form VIII of شقّ (drawing off with effort),
   دالّة *function* from دلّ (to indicate — a function is the indicator),
   الجبر *algebra* = restoration. Run academy terms through the Ṣarf Machine and the
   function the coiners saw falls out.
2. **تعريب (transliteration)** — الطوبولوجيا for topology; still segmentable on the Greek side.
3. **نحت (blending)** — compounds compressed into one derived pattern.
Reverse method: EN deep term → Arabic academy term → Ṣarf/etymon analysis → pure function
→ does the Greek/Latin analysis agree? Agreement = a verified quantum string.

## Open datasets / libraries to plug into the POC slots (Claude Code phase)

- Arabic morphology: CAMeL Tools (morphological DB/analyzer), Buckwalter lexicon,
  Wiktionary/Kaikki Arabic entries + derived-form tables.
- Greek: Morpheus/Perseus morphology, CLTK corpora, Kaikki Greek.
- Latin: Whitaker's Words / CLTK Latin, Kaikki Latin.
- Translations: Wiktionary translation tables (Kaikki), WordNet + Arabic WordNet,
  OmegaWiki — always as *attestation sources*, graded, never silent truth.

## Measured POC results (2026-10-23, this machine)

- Glossary graph ingested: 93 terms, 9 domains, related+bridges edges verbatim.
- Full content scan: 11 files / 184,573 bytes under src/content; 91 of 93 glossary
  terms attested in >=2 files (grammar, word, map, ratio, type in all 10+).
- Sarf generation verified for شكل and كتب (10 forms + participles, diacritized).
- Decipher operation: 13 academy terms — 12 resolved to correct root+form by machine
  (incl. doubled roots دلل/حلل/صفف via participle rules); الطوبولوجيا honestly
  unresolved (transliteration). Discovery logged: Arabic coinages reach for
  **Form VI (تفاعل)** whenever the concept is mutual/relational — تشاكل (isomorphism),
  تكامل (integral), تماثل (symmetry): تفاعل is Arabic nomenclature's relational operator.

## The computational map of Arabic's own sciences (representation layer)

Each classical Arabic science IS a computational representation, and the corpus models
them as operations, not topics:
- **النحو (syntax)** — a governor/operator system: العوامل are operators binding
  dependents; الإعراب is a type/case system. Computational form: dependency grammar.
- **الصرف (morphology)** — finite-state transducers (built: Sarf Machine).
- **العروض (prosody)** — regular languages over تفعيلات; الخليل's five circles are a
  CYCLIC GENERATOR of the meter space; الزحافات والعلل are licensed rewrite rules
  (built: 6 meters generated; الخبن verified: مستفعلن → متفعلن).
- **البلاغة (rhetoric)** — البديع = string/phonetic operations (جناس = permutation &
  edit classes; سجع = terminal-rhyme constraint; طباق = antonym pairing = negation edge);
  البيان = mapping operations (تشبيه is a 4-place relation: مشبه/مشبه به/أداة/وجه الشبه;
  استعارة = cross-domain mapping with source suppressed — the corpus's own transfer op,
  theorized in Arabic a millennium ago; كناية = indirection);
  المعاني + الجرجاني's نظم = compositionality: meaning computed from grammatical
  relations, not word lists — semantics as graph composition.
- **المعاجم (lexicography)** — root-keyed indexing (لسان العرب = hash by root).

Open data for the Claude Code phase (verified to exist, 2026-10-23):
Tafilat (GitHub: all meter patterns + zihafat/ilal, binary prosodic encoding),
MetRec / Arabic-Poetry (meter-labeled verses), Ashaar datasets (HuggingFace:
diacritized + gold arudi representations), Diwan corpus (~14M annotated verses).

## Continuation results (same night, round 2)

- Sarf Machine extended: hollow roots (أجوف) scoped I/IV/X — قول verified
  (قال/قائل/قول، أقال/مقيل، استقال/مستقيل/استقالة); doubled roots (مضاعف) merged
  forms verified (شدّ: شدَّ، شدّد، اشتدّ).
- Scansion (تقطيع) engine built: vocalized line -> /0 pattern (madd, shadda,
  tanwin, ishba' rules). Verified on the Mu'allaqa's first hemistich
  (قفا نبك من ذكرى حبيب ومنزل): pattern resolves exactly to
  فعولن مفاعيلن فعولن مفاعلن and is recognized as بحر الطويل.
