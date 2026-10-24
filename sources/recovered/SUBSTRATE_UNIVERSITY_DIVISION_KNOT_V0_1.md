# SUBSTRATE UNIVERSITY — DIVISION KNOT / v0.1

**Status:** architectural proposal, not a deployed or proven system. **Date:** 21 October 2026. **Founding research collaborators:** Abed Kadan and 7u (AI collaborator). **Scope:** reorganization of the admitted Substrate University academic corpus; no GitHub changes have been made as part of this proposal.

## 1. Founding principle

A division is a *navigation lens* over structures, not the parent or owner of a subject. A topic is a learning unit; a subject is an identity-bearing conceptual domain; an object, morphism, formal theory, claim, conjecture, pattern, experiment, or evidence record may exist independently of either. The **Division Knot**, abbreviated `DK0`, is the initial nomenclature/identity/typing construction that lets these objects form qualified relationships and tested compositions without forcing them into a single tree.

Do not introduce `DK0` as a seventh division. Retain the public atrium's six physical doors as interfaces into different slices of the same atlas. Preserve all existing 62 topic identifiers until explicitly reconciled against the earlier, unverified 49-subject / nine-pillar map. The nine In-Grammar pillars and the CLOCK9 research engine are conceptually distinct; neither count is a number of university divisions.

## 2. Verified current baseline

Repository: https://github.com/akadaan310/abedkadaancom (default `claude/new-session-xd8auu`, as read on 2026-10-21). The root README reports a browser-native React/Vite/Three.js university with six divisions, 62 curriculum entries, six executable exhibits, a contextual glossary, an arithmetic gate, a CGT book reader, and local book composition. `src/content/types.ts` currently defines `Topic.division: DivisionId` (single mandatory division). `src/content/registry.ts` hardcodes per-division curriculum arrays. `src/content/glossary.ts` already provides senses and computational bridges, which should be the migration seed. `src/math/bridgeGrammar.ts` already distinguishes syntactic admissibility from semantic realizability.

Related project: https://github.com/akadaan310/clock9 currently has a terse README only. The separate archived research blueprint `RESEARCH_BLUEPRINT(1).md` describes a runnable, non-neural TypeScript proof-of-mechanism, not a proven LLM acceleration system. CLOCK9's known event sequence is `context → draft → admission → compile → promote → witness`, and its nine-pillar association comes from In-Grammar's representational research vocabulary; these must not be conflated. The standalone `anwaa` repo is a zero-dependency Canvas2D physics/interaction engine focused on celestial scenes; it is not the yet-to-be-specified full physical-world renderer.

The governing university constitution excludes retired subjects and the cross-session AI identity lane from the public university. Do not reintroduce excluded topics in a migration. The constitution identifies the six collections as provisional and allows cross-membership.

## 3. Minimal formal object

Define an **attributed typed incidence hypergraph**

`H = (V, E, τV, τE, incidence, roles, provenance, constraints, time)`.

- `V`: stable identity-bearing nodes, independent of academic placement.
- `E`: relationships of any admitted arity, including ordinary binary edges, multi-participant hyperedges, and explicit non-relations.
- `τV`, `τE`: schema-versioned types. The same spelling can have several domain-specific senses.
- `incidence`, `roles`: directed/role-labelled participants (e.g., domain, codomain, operation, witness).
- `provenance`: sources, authorship, software version, test witness and epistemic state; inspired by W3C PROV, not claimed to be a complete PROV implementation.
- `constraints`: preconditions and forbidden compositions, not merely graphic annotations.
- `time`: validity ranges, supersession and revisions.

A graph is a useful projection of H, but *not the entire ontology*. One graph edge cannot faithfully encode all n-ary relations, differing meanings, qualified negative claims and context-specific evidence.

### Ontic sorts

Use a discriminated union for `DivisionView`, `Subject`, `Topic`, `TermSense`, `Theory`, `FormalObject`, `Structure`, `Operation`, `Morphism`, `Claim`, `Problem`, `Evidence`, `Experiment`, `Implementation`, `Representation`, `Artifact`, `Pattern`, and `BoundaryCandidate`. `Class` must be typed by sense (`equivalence-class`, `proper-class` [if formally applicable], `OO-class`, `category-of-objects`, `design-pattern-classification`); a shared English term is not an identity proof. Mathematical categories are first-class objects only where objects, hom-sets and composition/identity axioms are actually specified.

### Edge and hyperedge vocabulary

Admit `MEMBER_OF_VIEW`, `PART_OF`, `PREREQUISITE`, `INSTANCE_OF`, `IMPLEMENTS`, `DEFINES`, `DERIVES`, `PROVES`, `REFUTES`, `MAPS_TO`, `ISOMORPHISM`, `ANALOGOUS_UNDER`, `GENERATES`, `PRESERVES`, `COLLAPSES`, `CONTRADICTS`, `INCOMPATIBLE_UNDER`, `EXCLUDED_BY_SCOPE`, `NO_ADMISSIBLE_MAP_UNDER`, `UNKNOWN`, `SUPERSEDES` and `CO_PARTICIPATES`. `UNKNOWN` is not a negative assertion. `INCOMPATIBLE_UNDER` requires explicit conditions and a witness or a scope rule. Relations with arity >2 must use named roles, not coerced pairwise edges.

### Relation magnitude (do not confuse units)

Store separately:

- `coupling`: effect/sensitivity of a structural dependency if a measurable operator exists;
- `semanticAffinity`: bounded qualitative or empirically calibrated similarity;
- `confidence`: evidence strength supporting a claim;
- `rigidity`: whether a relation is necessary, optional, contingent, or violated by perturbation;
- `polarity`: positive relationship or explicitly scoped prohibition;
- `context`, `validAt`, `witnessIds`: qualifications.

A tight/loose string is a visualization for one or more declared measures; *string tension is not a universal mathematical magnitude*. Do not convert a lack of evidence into a zero-strength or negative edge.

## 4. From field map to topology

Let `S` be an admitted universe of subjects/constructs. Each academic division offers a **view** `U_i ⊆ S`; overlapping views are allowed. The six view sets alone are not automatically a topology. For the `U_i` cover, build its **nerve** `N(U)`: there is a simplex on `{i0,...,ik}` exactly when the common intersection of these selected subsets is nonempty. This represents overlap among divisions. Claims that the nerve preserves the homotopy type of an underlying space require a topology and additional good-cover hypotheses; do not assert them by appearance.

For computational attachment, define an incidence complex and, where useful, a **presheaf/cellular sheaf** assigning typed local data to nodes/cells with restriction maps. A global section is a compatible assignment across overlapping local contexts. An obstruction to gluing is a useful way to represent apparently connected subjects whose definitions cannot be consistently combined. Do not call any arbitrary hypergraph a sheaf without defining stalks, maps and consistency conditions.

A **ring-form constellation** can mean a cyclic pathway (a closed walk) between topics/divisions, or a feedback loop. In a simple undirected graph, a simple cycle has at least three distinct vertices. This is *not* by itself an algebraic ring. The algebraic definition of a ring requires addition and multiplication with specified axioms; only apply the word in that sense when those operations are defined. An isolated, open-chain, forest, star or acyclic relationship system is as admissible as a cycle; no artificially closed path should be invented to make a drawing attractive.

A **knot** is used as a house name for a cross-domain qualification/entanglement object, not as a claim about tame knots in ambient three-space. If actual knot invariants are invoked later, define an embedding and equivalence moves first.

## 5. Exact mathematical example: image, not a photo

Let `A: ℚ² → ℚ²`, `A(x,y)=(x,0)`. Then:

- `im(A) = {(x,0) : x∈ℚ}` (horizontal 1-dimensional subspace);
- `ker(A) = {(0,y) : y∈ℚ}` (vertical 1-dimensional subspace);
- `rank(A) + nullity(A) = 1 + 1 = 2`.

The term-sense `image:linear-map` belongs to a Geometry view, a linear-algebra topic, and a possible course on information-preserving representations. The term-sense `image:photography` denotes a picture or sampled camera output. There is a demonstrable *MAPS_TO/ANALOGOUS_UNDER* bridge only once the camera projection and sampling map are explicitly defined. Shared spelling alone is not a canonical map. In category-theoretic context, factorization through `im(f)` requires the ambient category and choice of subobjects; not every category admits images.

Likewise, pitch classes modulo 12 form the additive cyclic group ℤ/12ℤ; they do not magically become an algebraic ring unless multiplication is supplied and used. `group` in algebra, an OO group of classes, and a human group are separate senses.

## 6. CLOCK9 participant role

CLOCK9 may propose typed candidate edges, programs or reversible macros from admitted context. It must not create authoritative ontology by generation. A possible pipeline is:

`ContextSlice → CandidateRelation → TypeCheck → AdmissibilityCheck → Resolve/Compute → IndependentWitness → Promote-or-Quarantine`.

This is a *new planned adapter* to the documented CLOCK9 prototype, not a claim that `clock9` currently does graph reasoning or verifies category-theoretic statements. The nine In-Grammar pillars provide an optional annotation system for linguistic/operational representation, while CLOCK9 event ordering acts as an execution mechanism, not a governing numerical principle or a physics clock.

## 7. Nomenclature and extra-nomens

Each term has a `canonicalId`, label, context-qualified senses, admissible grammar, source status, version and provenance. Define `extraNomens` as a *boundary hypothesis pool*: alternative names, generative analogies, unresolved embeddings, conjectured correspondences and as-yet-untyped operators surrounding admitted core nomenclature. Promotion requires a type declaration, conditions, examples, counterexamples where relevant, source/proof/test witness and human authorization for public claims. Quarantined terms may inform exploration but do not become established academic facts merely by frequent occurrence in LLM output.

Use status axes rather than one boolean: established / house construction / conjecture / application / mythology is the existing public scheme; additionally store verified, proposed, disputed, refuted and superseded as **evidence state**, not synonyms for those epistemic labels.

## 8. Implementation contract: additive migration

**Phase A — read-only audit:** freeze IDs of the six division doors and 62 topics. Export the old 49-subject/nine-pillar index, if recoverable, to a reconciliation sheet; do not silently replace either corpus. Identify explicit retired material.

**Phase B — normalized ontology:** add `src/ontology/schema.ts`, `nodes.ts`, `relations.ts`, `senses.ts`, `sources.ts`, `validators.ts`, `projections.ts` and `tests`. The original `Topic.division` can temporarily remain for backwards-compatible routes; introduce `memberships: DivisionId[]` and use an adapter. Make the canonical node ID independent of a primary division.

**Phase C — semantics:** validate relation arities, typed domain/codomain, prerequisite cycles, source references, forbidden operations, recorded negative constraints, scope and time. A forbidden edge and an unknown edge must yield different diagnoses. Derived edges require explicit rules and witnesses; do not infer transitivity for relations that are not transitive.

**Phase D — atlas projections:** add independently inspectable views: division cover and nerve; typed hypergraph; constraint/negative-space overlay; mathematical morphism diagrams; optional sheaf-consistency map where rigorously defined; chronology and provenance. The existing six-door campus remains the main physical interface. Preserve text-only accessible navigation on Android.

**Phase E — CLOCK9 research adapter:** allow pure proposed candidates on a bounded ontology DSL; independent verification before any promotion; log rejection reasons. Keep all side effects explicitly gated. Measure accuracy, latency and resource use; do not call a toy prototype a production LLM speedup.

**Phase F — new physics/world-engine admission:** accept forthcoming world-physics concepts as typed candidate families with their own claims, equations, empirical assumptions, conservation laws, numerical solvers, rendering maps, errors, benchmarks and provenance. Do not conflate an engine's simulated forces with a physically verified law.

## 9. Acceptance tests

1. The six doors, 62 topic IDs, source paths, CGT book and existing exhibits remain usable after migration.
2. A topic can appear under two divisions while retaining a single canonical ID and history.
3. An `EXCLUDED_BY_SCOPE` relation cannot be mistaken for an unknown/untyped edge; absent edges are not treated as negative findings.
4. Linear-map `image` has exact image and kernel witnesses; `photo image` is linked only with a declared camera model.
5. A deliberately ambiguous `class`, `group`, `field`, `ring`, `image` or `kernel` term resolves by typed contextual sense or asks for disambiguation.
6. Nerve faces exist exactly for verified nonempty intersections of division view sets; topological equivalence is not asserted without hypotheses.
7. A composed mapping is rejected if domains/codomains mismatch, even when the endpoint labels look semantically related.
8. A CLOCK9 suggestion without independent proof/test remains a suggestion. An executable witness can be independently replayed.
9. Attribution, epistemic category, evidence status and licensing survive transformations and exported artefacts.
10. No excluded retired research category is reintroduced to the public university by ontology expansion.

## 10. Sources inspected

- [University root README](https://github.com/akadaan310/abedkadaancom/blob/claude/new-session-xd8auu/README.md)
- [Existing topic/type schema](https://github.com/akadaan310/abedkadaancom/blob/claude/new-session-xd8auu/src/content/types.ts)
- [Six-division registry](https://github.com/akadaan310/abedkadaancom/blob/claude/new-session-xd8auu/src/content/registry.ts)
- [Contextual glossary](https://github.com/akadaan310/abedkadaancom/blob/claude/new-session-xd8auu/src/content/glossary.ts)
- [Bridge Grammar](https://github.com/akadaan310/abedkadaancom/blob/claude/new-session-xd8auu/src/math/bridgeGrammar.ts)
- [University rebuild record](https://github.com/akadaan310/abedkadaancom/blob/claude/new-session-xd8auu/docs/UNIVERSITY_REBUILD.md)
- [CLOCK9 repo](https://github.com/akadaan310/clock9)
- [Anwaa physics-interaction repo](https://github.com/akadaan310/anwaa)
- [nLab: image in category theory](https://ncatlab.org/nlab/show/image)
- [Justin Curry: Sheaves, Cosheaves and Applications](https://arxiv.org/abs/1303.3255)
- [W3C PROV provenance overview](https://www.w3.org/TR/prov-overview/)

**Explicitly not done:** no GitHub commit, pull request, deployed alteration, full browser runtime test, or proof that the proposed ontology already exists.
