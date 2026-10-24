# Computational Corpuses, CGIT, PURL and Bridges

## 1. Computational corpus as a versioned universe

A computational corpus isn't just files. Define a contract:

`C = (domain, version, source, license, alphabet, grammar, record_types, normalizers, negative_grammar, addresses, operations, provenance, tests)`.

The grammar and source/legal preconditions **must be registered before ingestion**. A content ID commits to canonical bytes **and** the provenance envelope, not to human meaning. A corpus can be physics source, shader code, botany papers, game assets, or programming documentation. Each contains different source record types and needs a typed bridge before being combined.

Required two-layer addressing:

- **Content** `CID = SHA256(domain_separator || canonical_bytes)`; canonicalization/version is part of the typed contract.
- **Position** `(corpus_id, revision, file_or_verse_or_frame, start, end, position_encoding)`; hash lookup is not an explanation of source position.

Canonicalization is dangerous when applied to bytes that must be unmodified (scriptural corpora, executable source, signed archives). Preserve original bytes and their independent digest; treat normalized/search views as **new derived artifacts** with explicit loss/preservation reports.

## 2. CGIT source/derivation model

A useful CGIT commit is `commit(root_of_objects, parent_commit_ids, operation_trace, environment, policy, witness)`. Distinguish **Git compatibility** (Git's actual serialized object hashes/parents) from **CGIT-like research records** (our typed object graph). Their hashes are not interchangeable. An import adapter can preserve upstream Git commit IDs separately.

`tre/cgit.py` implements typed hash-addressed object insertion and graph-verification only. It does not implement Git packs, Merkle membership proofs, branches, trees according to Git format, distributed signatures, or authenticated object retrieval. Cryptographic digest references require a *trusted root* to attest completeness/authenticity.

Existing CGIT/PURL research directions include derivations, equivalence, proofs, lineage, typed operations, and immutable history; an operation such as a source-to-scene compiler should record its source fixture, corpus revision, grammar revision, output, and verifier verdict. Two transitions commute only when `f(g(S)) = g(f(S))` holds under identical preconditions and an explicit equivalence relation.

## 3. PURL / SEURL boundary

- PURL = addressable state and operations (`GET` = read only, mutations through capability-checked methods).
- SEURL = agent-facing affordance/landmark/state-diff projection.
- TREE = typed structural object + execution semantics.
- CGIT = immutable provenance and transition history.

Do not convert read access to authority. No bearer secrets in URLs. A host renderer can expose a scene's inspectable PURL even when no editing right exists. Recording which operation is *possible* does not authorize performing it.

## 4. Bridges and grammar-ships

`B : (source_type, source_schema, target_type, target_schema, policy) ⇀ (transformed_value, witness)`.

A bridge is partial and effect-typed. The `tre/corpus.py` fixture admits one-to-one field maps only when all required destination fields are supplied. **It does not infer semantics** from matching strings. Future bridges can be many-to-one if supplied with a declared loss model and a tested inverse/quotient relation.

A cross-corpus program should be able to traverse a typed grammar-ship chain:

`NaturalLanguage → SceneConstraints → GeometryGrammar → RenderGraph → GPUBackend → MeasuredFrames`.

Each arrow is an independent compiled/admitted module with provenance; micro-specialists can propose nodes/edges but **must not grant new capabilities**. Corpus merge does not imply model merge. When a bridge fails, record the smallest incompatible type, rule, missing license/source, or absent witness as an Ingrammatica certificate.

## 5. Cost profile

`T_total = T_ingest + T_parse + T_index + T_compile + Σ T_query + Σ T_update + T_verify + T_output`.

Expected O(1) in-memory hash lookup assumes a populated bounded-load map; reading bytes costs at least output length, and cold storage incurs I/O. Membership in a balanced binary Merkle tree normally needs O(log n) proof data; recomputing its root from all leaves costs O(n) hashes; a persistent Merkle DAG reduces incremental copying as a function of changed paths. Real engine performance depends on memory locality, shader compilation, GPU synchronization, collisions and frame budgets.
