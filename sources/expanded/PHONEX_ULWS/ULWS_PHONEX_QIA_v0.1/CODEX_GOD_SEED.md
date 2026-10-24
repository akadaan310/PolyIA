# CODEX IMPLEMENTATION COMMISSION — PHONEX / ULWS 0.1

**Title:** Universal Phonetic Word-Set Research Engine; evidence-first, VM deployable, with safe adapter surfaces.

## Command for Codex

You are lead compiler engineer, data architect, quantitative linguist and reliability tester. Implement the attached `FOUNDATIONAL_RESEARCH.md` as an isolated production-candidate service on the Oracle VM **without modifying the user's live existing applications, repositories or Muse's corpus**. Do not rely on large language models to infer the core lookup paths. Start with the attached `src/phonex.py` and its 25 passing tests as a **toy mathematical contract only**. Rewrite/extend it where required for correct IPA parsing, licenses, cross-language scale and source-data ingestion.

### Constitutional rules

1. User assets are immutable references; no destructive git operation, repo modification, external pushes, production DNS/network changes or global installs.
2. Ask before deploying exposed services or using credentials not already authorized for this work. Bind development API only to localhost, with no unauthenticated write capability. Never reveal secrets in logs.
3. **Never claim phonetic resemblance proves translation or cognacy.** Each edge stores type, provenance and epistemic grade. Separate labels `phonetic_near`, `translated_attested`, `borrowed_attested`, `cognate_attested`, `hypothesized`, `unrelated`, `unresolved`.
4. Preserve IPA diacritics/affricates/stress/tone and original spelling bytes. Make G2P prediction visibly nonattested. Epoch, dialect, writing-system and variety IDs are mandatory or marked unknown.
5. Preserve Arabic Timeless twenty-layer semantics and do not overwrite the folded hamza, tāʾ marbūṭa, or dotless mapping into source originals. Consume and produce explicit adapters only.
6. Dataset downloads only from trusted pinned releases and under dataset-specific licenses; record checksum/version/permissions. For community-governed languages honor usage protocols and export controls.
7. Every exported relation carries source IDs and a reproducible witness. Reject score-only promotion to verified.
8. Every algorithm carries bound declarations. No O(1) claims for fuzzy search, full graph traversal or listing results.

### Step 0 — Preflight

- Inventory CPU cores/RAM/disk/operating system and current services non-destructively; record output in `reports/ENVIRONMENT.md`.
- Create independent working tree `$HOME/workspaces/phonex-ulws` unless the operator supplies another authorized path. No root dependency.
- Ensure expected versioned application boundary. Keep a `STOP/NEEDS_APPROVAL.md` when a task requires external access/privileges.

### Step 1 — Schema + policy

- Implement validated typed models for language variety, writing system, lexeme, form, IPA pronunciation variant, phoneme/feature set, morpheme, sense, source, attested etymological relation, hypothesis, Q-String, query run and witness.
- Use SQLite in WAL for MVP with migrations and transactionally consistent snapshots; optionally Parquet for bulk chunks. Do NOT make Neo4j a mandatory primary store. Add indexes and results history.
- Schema includes cultural authority, source license, redistribution and commercialization allowances, access scope, source revision, hash, historical certainty. Deny uncertain data export by default.

### Step 2 — Pin source contracts

- Discover stable releases for Glottolog, CLTS, PHOIBLE, Wiktionary-derived IPA datasets, Lexibank/Concepticon. Validate actual licenses for each edition and dictionary dump separately; software licenses do not automatically cover scraped/derived corpora.
- Begin with three small, approved multilingual sources and one Arabic-specialist source; avoid downloading massive dumps before schema and license gate pass. Provide download manifest with checksums. No hidden scraping.
- Preserve original input plus loss-accounted Unicode NFC normalized search views. Import word pronunciations as *variant-scoped* evidence.

### Step 3 — IPA + orthography compiler

- Segment IPA properly (combining modifiers, tie bars, affricates, length, stress, tone, syllables), normalize with CLTS and record unknown symbol cases without silent replacement.
- Implement per-variety orthography→pronunciation adapter with attested lookup first, G2P optionally later; annotate generated/uncertain output.
- Implement cross-language feature vectors against versioned CLTS/PanPhon compatible tables; weight/stress/length toggles are explicit query settings.
- Add independent Arabic rasm projection adapter driven by exported Timeless tables. Rasm is a *different* relation from phonetic similarity.

### Step 4 — Indexes and search

- Build deterministic segment-prefix trie/FST and exact key hash index; feature-family neighbor index for candidate expansion. Add optional suffix/n-gram index only when `ANY_CONTIGUOUS` is requested.
- Implement `EXACT_INITIAL`, `NEAR_INITIAL`, `INITIAL_MORPHEME`, `CARRY` with bounded hops and alignment witnesses, shortest-cost frontier plus finite beam limits. Use a typed AST for PHONEX query grammar, no arbitrary execution.
- Implement self-check against brute-force reference on sampled corpora; measure recall/latency/false positives and report limitations.

### Step 5 — Layers, graphs and export

- Keep distinct phonetic, semantic, morphological, translational, etymological and Arabic-dot-state edges. Use Q-String-like typed incidence records with evidence and epistemic status.
- Implement JSONL exports to Muse's S0–S4 design via opt-in adapter: `source`, `span`, `form-card-proposal`, `edge-proposal`, `operation-run`, rather than writing into her corpus directly.
- Implement WAZNOMIA function/root candidate proposals with multiple results, not deterministic proof of word etymology.

### Step 6 — CLI/API & documented examples

CLI commands (improve syntax as appropriate):

```bash
phonex source list
phonex source verify --manifest manifests/pinned.json
phonex ingest --manifest manifests/approved-small-corpora.json --dry-run
phonex index build --snapshot current
phonex words match 'topology' --language eng --mode near-initial --carry 2 --explain --json
phonex words match-ipa 't ə p ɒ l' --mode near-initial --show-alignment
phonex relations explain --qstring 'qstr:v1:...'
phonex export --format corpus-s0-s4 --proposals-only --out exports/muse
phonex benchmark --baseline scan --index trie --report reports/benchmarks.json
phonex api serve --bind 127.0.0.1 --port 8877
```

- Provide OpenAPI read endpoints `/v1/words/match`, `/v1/sets/{id}`, `/v1/sources/{id}`, `/v1/relations/{id}`, `/v1/explain/{query_id}`, health and version. Do not expose unauthenticated HTTP to the Internet.
- Include an example `topology` multi-language phonetic query with both Arabic spellings `طوبولوجيا` and `توبولوجيا` **only if independently source-attested**, otherwise use clearly marked fixture observations and return source status.

### Step 7 — Testing, measurement, gate

- Unit/property tests: IPA segmentation, Unicode canonicalization, dot-loss declaration, exact prefix/near prefix, noninitial false matches, no semantic inference, provenance, license-denied export, duplicate language identifiers, bounded carry cycles, cache version invalidation.
- Independent historical linguist review of etymology promotion rubric; no false automatic promotion.
- Benchmark at several corpus sizes using CPU/wall time, p50/p95/p99, peak RSS, on-disk index size, recall@k against full scan. Show both wins and losses. Include counterexamples and family-balanced sampling.
- Produce `reports/PROOF_LEDGER.md` with every implemented law/assumption, witness and counterexample; `reports/DATA_RIGHTS.md`; `reports/DEPENDENCY_LOCK.md`; `reports/COVERAGE.md`; `reports/BENCHMARKS.md`; `reports/RELEASE_GATE.md`.
- Run typecheck/lint/tests and independent sample data replay before release candidate status. If a stage cannot pass, isolate scope, document limitations, and stop promotion rather than fabricate success.

### Deliverables

A pinned, reproducible source repository (or isolated new branch under explicit operator authorization); typed schema/migrations; ingestion adapters + license registry; proper IPA segment parser; multi-phonetic index; wordset query engine; grammar compiler; Q-String relationship store; self-explaining CLI and local-only API; WAZNOMIA/Timeless read-only adapters; Muse S0–S4 proposal exporter; example queries; quantitative benchmark and independent test record.

**Definition of done:** For at least three independently sourced multilingual datasets, a query returns relevant **initial contiguous** phonetic candidate matches with original writing, scoped pronunciation, source identity, calibrated distance component(s), alignment witness, language status and full provenance; rejects unsupported etymological inference; records incomplete coverage. Timeless and the existing Corpus Engine remain byte-for-byte unchanged. No production claim without a reproducible benchmark and access-control verification.
