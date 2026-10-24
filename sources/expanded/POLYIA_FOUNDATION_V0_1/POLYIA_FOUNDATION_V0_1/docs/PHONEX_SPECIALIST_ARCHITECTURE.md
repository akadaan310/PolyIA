# Universal Language Word Sets as composable language automata

## Per-variety generator pack

A language/variety `v` has its own model `L_v=(Σ_v, O_v, T_v, P_v, M_v, X_v, E_v)` where `Σ` is phoneme/segment inventory, `O` orthography mappings, `T` trained-or-attested pronunciation transduction, `P` phonotactics, `M` morphology, `X` lexicon and meanings, `E` evidence and restrictions. **An alphabet by itself does not determine phonology, syntax or grammar.** Model building requires corpus evidence or expert-authored specifications, and historical reconstructions are a different evidential grade.

All language packs compile to a shared **PHONEX semantic interface** (variety ID + IPA/feature stream + evidence). Shared schema ≠ shared phonology. A language can have many alphabets, orthographic eras and pronunciations. An unwritten language may still have a segment and lexical pack with no orthographic input map.

## Automata chain

`SourceWord → Norm-preserving orthography stage → Attested-pronunciation / probabilistic G2P W-FST → IPA-feature alignment → Prefix index → Bounded carry neighbor search → Candidate sets → Independently joined lexicon/morphology/semantics/historical evidence → Q-String evidence graph → word-set automaton → specialized SDK`.

The first phase must distinguish matching initial *contiguous phone segments* from substring matching. Feature carry `/t/↔/tˤ/` is an approximate neighbor operator with recorded cost, not proof of historical derivation. Across language packs, weights must be calibrated or explicitly labeled incomparable; do not multiply arbitrary scores pretending probability.

Automata composition is normal finite-state transduction when relation alphabets fit; use delayed composition as available (e.g. OpenFst). For grammar models requiring nesting or long-distance agreement, supply stronger typed parsers/unification components; do not overclaim FST sufficiency. Complexity includes building pronunciation index, graph edges, sorting and output cardinality.

## Higher agency orchestration

A concierge compiler can schedule independent packs concurrently under deterministic snapshot pins and then merge by stable canonical IDs. Assembly is a typed *join*, not blind concatenation. Every candidate includes original written surface, language/variety and source, pronunciation status, feature alignment, meaning senses separately, cognacy/borrowing status independently, and reason for inclusion. Null/unknown is retained rather than invented.

## Corpus and Arabic interfaces

- Muse's S0 immutable source → S1 spans → S2 form cards → S3 typed edges → S4 operations are a read/write **proposal interface** only; no direct mutation.
- Arabic Timeless rasm gives a second, orthographic-equivalence projection; WAZNOMIA supplies root/operator/sense *candidate* derivations and cross-language comparison. Neither proves cognacy or even translation.
- QIA attaches formally typed entanglement/incidence claims. Use semantic/predicate type checks and provenance before higher-order edges are promoted.
- A corpus's variety licenses, cultural restrictions and source provenance must remain enforceable even after data compaction and packing into a new specialized SDK.

## Proof obligations

A language pack must prove/check: source checksum, Unicode roundtrip (original preserved), IPA tokenization on documented inputs, finite-state well-definedness and bounds, root-pattern candidate errors, disallowed encoding modes, cross-variant leakage, license/export denial, no false cognate promotion, golden example/negative set, and regression on held-out languages. No universal sound→meaning law is asserted by registering a shared type system.
