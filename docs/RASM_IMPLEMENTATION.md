# Contextual Timeless rasm bridge — polyia.rasm/0.1

`polyia.rasm.run_rasm(parameters: dict) -> dict` is a pure, bounded bridge for
PIA-128's retained RSA28 chart. It implements the source's contextual quotient
alphabet, joining rules, set-valued inverse, original-surface side data, and a
strictly scoped chart relation. It has no file, network, subprocess, model or
publication effects. Inputs cannot select executable handlers.

The durable `experiment.run` interface additionally bounds the complete command
at 64 KiB, parameter depth at 12 and each ordinary string at 2,048 characters.
Only the exact versioned `recover` envelope (version, chart, operation,
projection, side_data) receives an 8,192-value census; other operations retain
the generic 2,048-value limit. This permits the tested 400-mark projection to
recover its exact original text through the live command API. A projection near
the pure kernel's 1,024-codepoint limit can still produce side data too large for
one HTTP command: such recovery is explicitly `REQUEST_TOO_LARGE`, not a lossless
round-trip claim over every transport input. The captured projection keeps the
original bytes, and standalone recovery remains available within kernel limits.

The scope is the retained **authored modern chart**, not a universal assertion
about historical Arabic manuscripts. The bridge remains in
`polyia.bridge.timeless`, outside the public Substrate University topic registry.
Every report states `su_registry_export_authorized: false`. This metadata and
the absence of an export operation do not replace the commission's independent
SU export validator; PIA-022/UCG-008's full export gate remains separate.

## Binding sources and reconciliation

Read in full for this increment: the SRC-TIMELESS `FOUNDATIONAL_STUDY.md`,
`README.md`, `MUSE_RELAY_COMMISSION.md`, `src/rasm_state.py`,
`tests/test_rasm_state.py`, `run_demo.py`, and the retained `results/demo.json`.
The original ZIP and its embedded duplicate were compared: both are
SHA-256 `d78020c3e0d04ca4e178ee6eda7a6a02b772a72090d5add4ab23ab2d7ac9a4f2`.
The study and Python source exactly match their original archive members.

The archive root is `Timeless_WAZNOMIA_QIA_Handoff_v0.1/`; the extracted root is
`sources/expanded/Timeless_WAZNOMIA_QIA_Handoff_v0.1 (1)/Timeless_WAZNOMIA_QIA_Handoff_v0.1/`.

| Retained member | Anchors used | SHA-256 |
|---|---|---|
| `FOUNDATIONAL_STUDY.md` | II contextual fibers; III constraint bottom; V كتب/كتم; VII no destruction; VIII normalization risk; XII limits | `1bcd88c5ecfe3c9bf549ff114896551cc1f7adb44a9a64c2b2bb23c9e45f2e6c` |
| `src/rasm_state.py` | HIJAI, CLASS_MEDIAL, CLASS_FINAL, CLOSED, positions, domains, candidates, degree, POINT | `8630918a3a9c33d3b7a0a899260ed274afd13cd4c2961de5e51547f382c66fbf` |
| `results/demo.json` | كتب; كتم; كتب_to_كتم | `2846991f7cd82bfd34b9e28d1a90bd59dd44656c450f09568f4c0d43cf361d9d` |

The original Python prototype transcribes quotient and articulation tables but
does not contain explicit dot counts. To avoid inventing them, the three actual
upstream files named by study XIII were retrieved through the GitHub connector
from `akadaan310/ARABIC_TIMELESS`, branch
`claude/dotless-arabic-language-0p5pcs`, on 2026-10-24. Their bytes are retained
under `examples/rasm/upstream/`, separately from immutable canonical sources:

| Upstream member | Git blob SHA-1 | SHA-256 |
|---|---|---|
| `lib/engine/alphabet.ts` | `dddd9d8e15fce60ab08ce79a867a8744d02be9a5` | `5a1060396116b9bdb3fa620d83b850039fd9605fc6f91c86f804030653bb7906` |
| `lib/engine/text.ts` | `89646ac622167a6a6535d8a109388eae00fdd552` | `bc2f575277d7679e83093458f4b18450c8884ca09bdbb26eac3b3d458d03434e` |
| `lib/engine/variants.ts` | `6bce80be21a2b53ea294c6d0f9ffa89eeb38beb0` | `240501c4a8a8949021b2be8266c74fa90316734ef87ab423cb076f479588ba34` |

Both hashes were recomputed from each saved file. The alphabet was additionally
fetched by its immutable blob ID and agreed byte-for-byte. The
[provenance record](../examples/rasm/upstream/provenance.json) retains repository,
path, requested branch, blob identity, source URL, date and custody scope.
These new copies are **PENDING_SOURCE_REGISTRY_ADMISSION**. No existing
source/registry was edited. The module copies the inspected tables as literal
data; it never imports or executes those TypeScript files.

Also read and retained: GOD_SEED PIA-127/128; Scientific Foundations SF-04/11;
Formal Vocabulary FV-03/05/07; Source Reconciliation's public University boundary;
and the exact original clauses from the inherited-obligation crosswalk:

* POLY-C-006, `sources/recovered/CODEX_CONSTITUTION.md`, lines 39–41:
  Timeless and Muse's Corpus Engine stay outside the University academic registry.
* POLY-C-041, the same source, lines 124–126: adapt actual rasm classes without
  modifying the source or equating the modern chart with every historical style.
* UCG-008, `sources/originals/UCG_CODEX_CONSTITUTIONAL_COMMISSION.md`, lines 137–141:
  preserve the SU subject/export boundary and separate Timeless bridge cards.

The implementation does not treat the historical relay's requests for future
datasets or production changes as ambient authority. Full morphology,
lexicography, phonemic inventories, historical analysis and WAZNOMIA remain
separate work. The current commission authorizes this bounded local adapter.

## API and reports

Every request explicitly pins:

```json
{"version":"polyia.rasm/0.1","chart":"timeless.rsa28/0.1",
 "operation":"project","text":"كتب","candidate_limit":256}
```

Operations and additional fields:

| Operation | Required | Optional |
|---|---|---|
| `project` | `text` | `orthography`, `candidate_limit` |
| `invert` | `skeleton`, `positions` | `constraints`, `candidate_limit` |
| `recover` | `projection`, `side_data` | None |
| `chart` | None | None |
| `relate` | `source`, `target` | `orthography`, `requested_relation` |

Unknown fields, operations, versions and chart names refuse. Reports contain
`status`, `evidence_class`, `result`, `checks`, `limitations`, `kernel_version`,
`chart`, `sources`, `llm_inference: false`, effect and publication scope.
Refusals expose `result.reason` and `result.detail`. After a valid raw text has
been captured for projection, a refused surface retains that `result.raw`.
No input object is modified.

Statuses distinguish a complete admitted operation (`PASS`), malformed or
unsupported input (`REFUSED`), a bounded candidate prefix (`RESOURCE_LIMIT`),
and contradictory supplied constraints (`INCONCLUSIVE`). Successful discrete
chart/count operations use `EXACTLY_CHECKED`. The Hartley value is separately
labeled `BINARY64_LOG_OF_EXACT_COUNT`; the logarithm is not exact arithmetic.
The runtime source pins are references, not assertions that a pure call read
and verified files. The focused tests perform the actual byte checks.

## Exact table, joining and packet example

The base alphabet is the retained 28 letters in HIJAI order. Initial and medial
tables have 15 classes; final and isolated tables have 17. The medial tooth
`ٮ` contains `بتثني`; the final tooth contains `بتث`, with final `ن -> ں`
and `ي -> ى`. The source's modeled `ٯ` class contains both `ف` and `ق`.
All other inherited groups and singleton identities are preserved.

The closed letters are `ادذرزو`. A letter receives from its predecessor exactly
when that predecessor exists and is not closed. It feeds its successor exactly
when a successor exists and the current letter is not closed. Those two flags
select medial, final, initial or isolated. A closed neighbor therefore changes
context; this is not a context-free character substitution.

`chart` exposes every position table, all 28 actual MOTION dot counts and
above/below/none locations, closed letters, and the inherited articulation
coordinates. It computes the source permutation orders from class factorials:
92160 medially and 4608 for the common refinement across positions. Those are
properties of the declared partition, not language-wide permutation laws.

The packet example is reproduced exactly:

```text
كتب -> كٮٮ
positions: initial, medial, final
domains: ك × بتثني × بتث
count: 1 × 5 × 3 = 15
candidates: كبب كبت كبث كتب كتت كتث كثب كثت كثث كنب كنت كنث كيب كيت كيث
Hartley: log2(15) = 3.9068905956085187 (binary64 approximation)
```

The second packet example `كتم -> كٮم` has five fillings. `كتب -> كتم`
changes the final rasm: it is not an iʿjām-only substitution. The source's
zero-based point 15 class contains both `ب` and `م`; `ف` shares their zone
but has a different point. These are properties of the named 17-point chart.
No contemporary acoustic measurement or semantic consequence is inferred.

## Inversion and constraints

`invert` requires a position for every skeleton slot. It reconstructs each
position's fiber and verifies that the supplied positions are consistent with
whole-word joining and boundaries. A singleton word cannot claim a medial
position. Each retained fiber has uniform joining behavior, so one representative
per fiber is sufficient for this consistency check.

The result contains all symbolic domains, the exact product size, a bounded
candidate list, enumerated count and a `complete` flag. Candidate order follows
the original class order and Cartesian product. At most 4096 candidates can be
requested, default 256. Enumeration uses a bounded prefix; if the exact count
exceeds the cap, the report is `RESOURCE_LIMIT`, not a complete inverse claim.
For ten tooth letters, the total is 5,859,375 even when only five are enumerated.

`constraints` is an array aligned with slots. Each entry is null or contains
`letters` (a subset of RSA28), `dots` (`count` and `position`), or both.
Restrictions intersect the domain. For `كٮٮ`, selecting two dots above in
the middle slot leaves `كتب`, `كتت`, `كتث`; additionally binding the final
slot to one dot below leaves `كتب`.

An empty domain is the explicit bottom of the constraint product. A contradictory
letter/dot restriction returns zero candidates and `INCONCLUSIVE`, with
`interpretation: inconsistent-with-declared-constraints`. Hartley is null at
zero. The report explicitly makes no manuscript-damage claim. Counts are
orthographically admissible consonant fillings, not dictionary coverage,
historical readings, probabilities or intended ambiguity. Shannon entropy is
always null because no probability model was supplied or justified.

## Surface preservation, explicit folding and recovery

`project` retains the original text, exact UTF-8 hexadecimal bytes, ordered
codepoints, SHA-256, and a separately identified NFC view. Projection operates
on the original codepoint order, not silently on NFC.

Default `orthography: base28` admits the 28 source letters, the eight ordinary
vowel/tanwin/shadda/sukun marks, and tatweel after an admitted base. Marks and
tatweel are omitted from the skeleton with codepoint-indexed loss records.
Hamza variants, tāʾ marbūṭa, alif maqṣūra, structural combining marks, unknown
characters, separators and leading marks refuse. This one-word API deliberately
does not reproduce the upstream parser's silent dropping of unknown characters.

Explicit `orthography: source-fold/0.1` applies exactly the fetched variant table:
`أ إ آ ٱ ء -> ا`, `ؤ -> و`, `ئ ى -> ي`, `ة -> ه`. It admits the source's
15-character TASHKIL set, records every folded/omitted surface and retains its
original codepoints. This is a lossy lookup projection with
`semantic_equivalence_claim: false`; it is not a phonemic or lexical equivalence.
For example, precomposed `أ` and decomposed `أ` can have the same NFC view and
skeleton while retaining different original hashes and different recovery data.

`side_data` retains **the complete original codepoint sequence**, its digest,
chart and profile. This intentionally straightforward witness is not a
compression claim. `recover` reconstructs text from that sequence, re-projects
it under the declared profile, and compares canonical bytes of the entire
projection and side data. Changed dots, positions, loss records, surface
codepoints or digest refuse. Success returns the exact original text and UTF-8
bytes, including mark order and tatweel. Missing side data is not replaced by a
guessed candidate. Digest/reconstruction consistency is not authenticated origin.

## Relation discipline and open gates

`relate` accepts only `requested_relation: chart-comparison`, the default. It
returns separate rasm equality, per-slot articulation point/zone comparisons,
the original surfaces and projections. Different base lengths explicitly have
no implemented slot alignment. Output keeps `semantic_relationship: UNPROVED`,
`historical_relationship: UNVERIFIED`, and `executable: false` even for a positive
chart match. Asking it to certify a cognate or other historical relation refuses.

This is a scoped contribution to PIA-127. Independent dictionary attestations,
contradictory historical sources, varieties/epochs, etymological promotion,
translation/cognacy/borrowing/calque adjudication and full export validation are
not implemented. PIA-128's full durable command/evidence integration and formal
acceptance remain for the commissioning coordinator. Neither a passing finite
kernel nor the new upstream byte custody changes mission acceptance.

## Resource and verification record

Input limits precede copying/hashing: JSON depth 16, 20,000 nodes, 4096 entries
per collection, 8192 characters per JSON string, 131072 total string bytes,
and 256-bit integers. The interface is discrete and refuses floating-point
input. Projection further bounds a word to 1024 raw codepoints, 4096 UTF-8
bytes and 64 base letters. Candidate work is O(64 × candidate_limit); exact
product counts fit within the declared finite letter bound. No external
dictionary or unbounded search is involved.

Implementation began only after release 1.2 commit `83906c7` was frozen. Initial
test-first execution used a missing-implementation fallback; after correcting
three test assertions that dereferenced absent results, the red run executed
16 tests and recorded 30 expected failure assertions. Implementation then passed
all 16. Additional source-custody and canonical-surface distinction checks bring
the final focused suite to **18 passing tests**:

```bash
/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -p test_rasm.py -v
```

The suite contains hand-declared packet candidates, positional examples,
dot/letter contradictions, literal cardinality answers, exact recovery,
tampering, bounds, unsupported surfaces and relation refusals. It also compares
140 words (all 28 letters in five neighbor contexts) against the actual retained
Python prototype. That differential check establishes source agreement; it is
not independent historical or linguistic validation. Dot-table agreement checks
all 28 rows against the preserved upstream MOTION table, and all seven source
pins plus the three Git blob identities are rehashed.

The original retained 30-test rasm suite was freshly run under the same runtime
and passed. A 105-call malformed parameter matrix returned structured finite
JSON without exceptions. No whole-project suite was run during concurrent
release work. For a local example:

```python
import json
from pathlib import Path
from polyia.rasm import run_rasm

parameters = json.loads(Path("examples/rasm/packet-example.json").read_text())
print(json.dumps(run_rasm(parameters), ensure_ascii=False, indent=2))
```

## Source registry admission during commissioning

The three selected upstream files have now been independently rehashed as Git blobs and SHA-256 objects, copied under immutable blob-addressed `sources/additional/ARABIC_TIMELESS/` paths, and entered in `registry/sources.json`. The initial pending status above records the handoff history. The provenance file links each example copy to its admitted canonical path and source ID. This is selected-file custody, not a claim to have mirrored the entire additional repository. Runtime source pins now use those canonical paths. Membership-only chart sets and the final-position table are explicit literal data for the executing-source pin contract; the scientific tables and outputs are unchanged.
