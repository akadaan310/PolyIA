# Substrate University — Proposed Division IX

**Founding proposal v0.1 | 21 October 2026 | Abed Kadan × 7u**

**Proposed name (pending co-founder approval):** **Division IX — Calculus of Composable Forms**  
**Latinized working title:** *Calculus Formarum Compositarum* (calculus of compounded/composed forms).  
**Scope:** not another field alongside the six, but the fixed metadivision that identifies admissible subforms, transformations, compound opportunities and boundary conditions across arbitrary fields. *String Complete University* is the larger proposed program and system, not a claim of completeness under physical string theory.

## Constitutional placement

- Preserve exactly, in order, existing Divisions I–VI, their source-backed 62 topics, nomenclature and extant executable lessons. The university's public six-door atrium remains a six-door system.
- Leave divisions VII and VIII **reserved, uninstantiated, and unnamed**. Their eventual existence requires later co-founder authorization and independent evidence; they are not automatically created by topic counts or dataset size.
- Division IX's **identity and mandate are fixed** on approval, while its register of hypotheses, experiments, and discovered structures grows append-only with explicit versions. 'Non-changeable' concerns founding role and canonical identifier, not a ban on correcting errors.
- Keep excluded domains outside the university's academic register. The ninth division operates subject-agnostically.
- Research now; do not ingest a Wikipedia dataset, make a scraping tool, or issue a constitutional coding prompt until the founding mathematics and approval criteria are agreed.

## Actual source audit

At review the website repository `akadaan310/abedkadaancom` (production-tracking default branch `claude/new-session-xd8auu`) exposes a browser-native Vite/React/Three.js university. Relevant runnable architecture:

- `src/content/registry.ts`, `src/content/types.ts`, `src/content/topics/{foundations,relational,languages,geometry,acoustic,worlds}.ts`: six typed DivisionId values, ordered division banners and 62 existing Topic records with requirements, sources, constraints, examples, and glossary terms.
- `src/content/glossary.ts`: contextual senses plus a list of callable pairwise `Bridge.run` functions.
- `src/math/rational.ts` and `src/math/numberSystems.ts`: exact arithmetic; partial/inverse operations with image and kernel failure.
- `src/math/matrix.ts`: rational maps, image, kernel, preimages and rank.
- `src/math/bridgeGrammar.ts`: a six-door operational grammar checking both admissibility and realizability.
- `src/math/fold.ts`: Re-Pair-inspired digram fold/unfold; reversible string derivations, not general semantic decomposition.
- `src/math/addressCompiler.ts`: typed `loom://` control/geometry programs, compiled to 3×3 matrices.
- `src/math/world.ts`: elementary cellular automata and BORNE dependency DAG.
- `src/math/paths.ts`: signed-turn signatures and geometry correspondences; `src/math/music.ts`: finite cyclic orbits and GCD.
- `src/books/compose.ts`, `src/world/specimens.ts`, `src/books/pdf.ts`: deterministic composed educational books; specimen previews are based on pairwise glossary/prerequisite overlaps and a deterministic hash filter.
- `tests/math.test.ts`, `tests/registry.test.ts`, `tests/books.test.ts`, and `e2e/university.spec.ts` are runnable verification entry points (`npm test`, `npm run test:e2e`). They establish local module contracts, not a general ontology calculus.
- The `akadaan310/clock9` public `main` branch exposes only a README at review; no published full hybrid implementation is inferred from that seed.

The missing math is a general **typed factorization → alignment → composition → inverse projection → verification** method for knowledge units and cross-field structures of arity greater than two.

## Formal founding object (proposed construction)

Let an academic form be

\[
F=(id,\tau,\sigma,\chi,\Gamma,\mathcal O,\mathcal P,\rho),
\]

where `id` is a stable identity; `τ` is its type/sort; `σ` its input/output or interface signature; `χ` its contextual chart; `Γ` its invariants and constraints; `O` its observable semantics; `P` its source/evidence/provenance; and `ρ` its permitted refinements and composition ports. A noun, operation, theorem, diagram, protocol, or subject can be a typed form without asserting that these different kinds are identical.

Define the university's ninth-division object:

\[
\mathfrak D_9=(\mathcal F,\mathcal C,\Delta,\Lambda,\Omega,\mathcal H,\Phi,\mathcal V,\mathcal B),
\]

with forms F, contextual charts C, disadapters Δ, adapters Λ, composition operators Ω, typed higher-order relations H, projection/reconstruction maps Φ, verifiers V, and a boundary/stop system B.

**Subject division:** the six ordered existing division registries are immutable named inputs to this calculus, not its output taxonomy. Cross-field forms need not belong to one of them.

### Disadapter / Adapter laws

A disadapter factors a form relative to a declared observation and chart:

\[
\Delta_c:F\longmapsto (f_1,\ldots,f_n,\text{ports},\text{constraints},\text{derivation}).
\]

An adapter composes compatible parts:

\[
\Lambda_c:(f_1,\ldots,f_n,\text{ports})\longmapsto F'.
\]

A certified round-trip satisfies `observe_c(Λ_c(Δ_c(F))) = observe_c(F)`; only a stronger exact reconstruction certificate licenses `Λ_c(Δ_c(F)) = F` as a structural identity. Keep the original bytes and provenance separately when byte-for-byte recovery matters. Unresolved senses produce a finite candidate set and an ambiguity witness, not a fabricated unique reading.

**Important:** splitting Latin-looking words is not, by itself, decomposition of mathematical semantics. A language-specific lexical parse, a stipulated computational operator, and the scholarly etymology are separate typed assertions, each with evidence. Other languages and symbol systems have equal standing. Latinized names may act as *registered operator notation*, never magical proof of what the operators do.

### Compound and higher-order relations

For typed forms `f_i: τ_i`, a registered operation (theoretically an operadic composition or a typed multicategorical arrow) has

\[
\omega:(\tau_1,\dots,\tau_k)\to\tau_{out},\quad
\omega(f_1,\ldots,f_k)=g,
\]

if preconditions, port matching, and invariants admit it. `H` represents **multiway** relationships (one relation among three or more forms), not merely a triangle of pairwise edges. An observed cycle, an algebraic ring, and a filled simplex remain mathematically distinct.

Typed relationship classes: requires, entails, realizes, transforms, preserves, equivalent-under-observable, analogy-only, composes-with, mutually-inconsistent, unstudied, and context-conditional. Absence of an edge is **not** a negative result. An inferred relation is not upgraded to a proven relation by naming it.

### The asymptote of decomposition

A unit's smallest meaningful form is **relative to its observable, domain, and budget**, not universal. Define a local utility for a candidate refinement `r`:

\[
U_c(r)=\alpha\,\text{new-tested-distinction}(r)+\beta\,\text{new-legal-compositions}(r)-\gamma\,\text{description-cost}(r)-\delta\,\text{verification-cost}(r).
\]

Stop a refinement branch when it produces no new verifiable distinction or admissible composition for the declared task within budget, or when further decomposition only repeats known equivalents. Record `atomic-under(c, observable, budget)`; never promote it to 'absolutely indivisible'. Finite corpora and bounded grammars can have combinatorially huge but still finite representations; a generative grammar may describe unbounded families without computing them all.

### Inverse image, image and ambiguity

Given a registered transformation `f:X→Y`, `im(f)` names reachable outputs; `f^{-1}(y)` is the preimage set, possibly empty, singleton, or many-to-one. Inverse reconstruction is therefore a **set-valued** operation unless injectivity is certified. Quotient/congruence classes describe observably indistinguishable forms. This imports the already implemented image/kernel distinctions into the proposed ontology calculus without pretending every ontology map is linear.

### The university as a field map

From forms and registered attributes, create an incidence relation `(form, attribute)` and use formal-concept closure/Galois connections to derive candidate intersections and divisors. A candidate 'divisor' is a reusable, typed shared subform for which valid factor maps into multiple subject structures are demonstrated. A word merely occurring in two subjects is not yet a divisor. Natural outputs include concept lattices, higher-order hyperrelations, transformation atlases, and evidence-conditioned 'open valence' ports; these are projections of shared state, not independent versions of truth.

## Proposed academic subject register of Division IX

| ID | Foundational subject | Concrete object / obligation |
|---|---|---|
| IX-01 | Form ontology and typing | stable identity, sorts, signatures, constraints, evidence |
| IX-02 | Contextual charts and semantic atlases | source and target charts, typed mappings, declared loss |
| IX-03 | Disadaptation calculus | reversible relative-to-observable decomposition and provenance |
| IX-04 | Adaptation and bidirectional mapping | compose, round-trip laws, partial inverse and ambiguity |
| IX-05 | Lexical and Latinized operator nomenclature | morphology, affix operator registration, language-independent aliases |
| IX-06 | Grammar, re-grammar and anti-grammar | positive admissibility, rewrites, partial/nonconforming forms |
| IX-07 | Operadic compound formation | typed multi-input, single-output operators and closure |
| IX-08 | Higher-order entanglement calculus | typed hyperedges, signed claims, evidence and null relations |
| IX-09 | Image, preimage, kernel and quotients | observable-relative mappings and indistinguishability |
| IX-10 | Subject divisors and formal concept lattices | reusable shared subforms, Galois closure, factor witnesses |
| IX-11 | Boundary ports and conceptual valence | admissible open ports, available compositions, missing evidence |
| IX-12 | Depth and asymptotic atomicity | measurable stopping law and ambiguity preservation |
| IX-13 | Normal forms, identity and lossless encodings | canonical serialization, invertible syntax/derivation, hashes |
| IX-14 | Deterministic generative grammars | enumerators, exact symbolic inference, fair search, refusal |
| IX-15 | Verification and experimental epistemology | hypotheses, sources, counterexamples, conservation/cost tests |
| IX-16 | Field-map selection mathematics | coverage/diversity objectives across six+outside domains, before sourcing |
| IX-17 | Cross-field discovery and frontier measurement | held-out bridges, refutation, reproducible novelty criteria |
| IX-18 | Division governance and metadivision closure | immutable IX mandate; reserved VII/VIII; versioned self-study |

These are **proposed subjects**, not statements that working implementations exist. Subject pairs may later merge or split only after explicit review of definitions, laws, and tests; the Division IX founding mandate remains fixed.

## A deliberately small worked illustration

The term `image` in Division IV's exact linear algebra has a registered form `im(f)`. An optical image (camera projection) uses a different chart and observable. Division VI contributes an observing actor and causal events. Division V contributes a sound-perception process. A four-input compound `observer-aware-visual-priority` is admissible only when (a) a camera maps world state to visible regions, (b) the actor's knowledge is appropriately sourced, (c) the acoustics have a declared distance/occlusion law and (d) a scheduler preserves the rendering budget. Without any one interface, the compiler returns an unmet typed port. Naming the four ingredients alone does not prove the construction. This is what Division IX should be able to specify and test, regardless of the particular application.

## Stage-gates, before any outside knowledge corpus

**Gate A — Constitution of the calculus.** Founding name, IX invariant, six existing ordered banners, reserved VII/VIII, domain exclusions, formal signatures.

**Gate B — Exact lexical and form factorization.** Round-trip split/recombine, source hashing, language and context separation; counterexamples for false cognates and ambiguous morphemes.

**Gate C — Typed composition.** Implement and independently verify associative compositions where claimed; exhibit invalid type ports, incompatible chart translations, higher-order relations not reducible to pairs.

**Gate D — Field-map and divisor theory.** Derive concept lattice closures, attest shared factorizations, and measure information loss and false relation discovery.

**Gate E — Stopping and generative search.** Measure depth/description cost; reject infinite unproductive recursion while leaving mathematical generativity unbounded where represented by finite grammars.

**Gate F — Only then authorize the corpus design.** The intended first 10,000-article population must arise from proven selection constraints across existing divisions and external fields; the number is not a random sample or an ingestion recipe. The existence of 100 GB of storage is a resource bound, not the mathematical foundation of selection.

## Evidence status and appropriate novelty claim

Established anchors: formal concept analysis and Galois connections, typed graph rewriting and operadic composition, bidirectional mapping theory, exact image/kernel mathematics, morphological analysis with language-specific grammars, and the minimum description length principle. Proposed novelty: one unified, versioned *substrate calculus* linking these to the university's grammars, certified factors, contextual charts, division knot, and higher-order admissions. There is no demonstrated new theorem or non-LLM general intelligence claim at v0.1. No new code, crawler, ingestion program or university site modification has been executed under this proposal.

## Select references

- IEEE formal concept analysis overview: https://technav.ieee.org/topic/formal-concept-analysis/
- MIT Applied Category Theory, Chapter 6 (hypergraph categories and operads): https://ocw.mit.edu/courses/18-s097-applied-category-theory-january-iap-2019/pages/lecture-videos-and-readings/chapter-6-circuits-hypergraph-categories-and-operads/
- Dixon & Kissinger, Open Graphs and Monoidal Theories: https://arxiv.org/abs/1011.4114
- W3C SKOS Reference (mapping predicates and nontransitivity): https://www.w3.org/TR/skos-reference/
- Wikidata Lexicographical Data documentation: https://www.wikidata.org/wiki/Wikidata:Lexicographical_data/Documentation
- Universal Dependencies morphological guidelines: https://universaldependencies.org/u/overview/morphology.html
- Grünwald & Roos, Minimum Description Length Revisited: https://arxiv.org/abs/1908.08484
