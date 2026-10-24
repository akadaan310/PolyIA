> **Safe checkpoint — implementation NOT STARTED.** The owner requested a stop after sealed runtime 1.4 publication. This document preserves the completed source audit/design for a future authorized continuation. No Q-Bundle compiler, VM, handler, tests, registry entry or mission acceptance was created from this plan. Runtime 1.4 remains the verified implementation boundary.

# Next promotion / Q-path increment — source-audited design, not implementation

Prepared during the 1.4 integration freeze. All artifacts in this directory are read-only research/design outputs. No runtime file, source original, registry, manifest, live ledger, or release was changed for this design. Wait for the root's 1.4 seal before adding implementation files.

## Recommendation

Build a compiled, source-carrying **typed Q-Bundle kernel**, then use its admitted paths as higher-level letters. The first vertical slice should execute a genuine **3-input / 2-output polynomial-division bundle**, compose its outputs into a second operation, preserve every named binding, and independently check the arithmetic. Follow with a finite G-ship product-search controller and exact promotion towers. These share the same immutable context, port, witness, source and dependency contracts; they should not be separate superficial JSON demos.

The current seed promotion merely wraps one finite word list and expands its canonical JSON. The current qpath supports add/multiply/divide over two Rational[Q] values, with one output and an explicit caller-supplied sequence. It has no Q-Bundle records, evidence strands, versioned context transport, source grammar compiler, fixed-domain reachability, promotion eligibility/invalidation, or dependency-aware executable package. Retain those seed events and their original code pins; implement the new profile under a new exact dispatch name after review.

## Source audit and interpretation constraints

`SOURCE_AUDIT.json` contains all 40 directly mapped PolyIA/UCG clauses and 174 selected supplemental records whose full documentary sources were read, with exact source/text hashes and byte locators. Source/text checks passed for all those records. The broad PIA-061–084 crosswalk contains 1,829 supplemental mappings; this is not a claim that all 1,829 were read or discharged.

Important sources and exact anchors:

| Source / record | Binding requirement |
| --- | --- |
| `GOD_SEED.md`, PIA-061–084 | Current promotion, Q relation, genuine hyperedge, proof-scope and replay acceptance |
| `SRC-PLICA`, `sources/originals/PLICASTRATUM.md`, SHA `3a11ee1c6998d740cd556847ae8b64115bdac17c21e78efa85c5701e2606fcdd`, §§2–5,7,10 | explicate is substitution; implicate is recognition of a valid fold; complicate is a product alphabet; replicate iterates substitution; applicate supplies the seven-layer adapter; promote admits a certified path as a letter |
| `SUP-21226ed88a82f574-00000317` (Q implementation seed line 8) | Concrete native syntax → typed AST → verified typed IR → bytecode. Explicitly rejects a JSON-dispatched production interpreter |
| `SUP-21226ed88a82f574-00000891` (line 13) | DFA×G-ship search, n-ary bundles with ordered ports and separate competing strands; type refusal before execution |
| `SUP-21226ed88a82f574-00000983` (line 14) | Bounded closure certificate with scope/observable/budget; graph connectivity is not scientific closure |
| `SUP-1f146b4081bc2e12-00002a0f`, `...-00003242`, `...-00004440` through `...-00004613` | Q pair identity, Q-Bundle incidence/strands, source retention rather than hash inversion, Q-Tower/materialization/frontier/closure records |
| `SUP-58d4fa9896f3dbd5-00000dbc`, `...-000023c1`, `...-00003b75` | EFC n-to-m incidence; named roles, distinct evidence strands, finite fixed-universe closure, no circular certification |
| `SUP-0d2001d0cb91b05c-00000bd1`, `...-00001796` | DK0 typed incidence; nerve intersections and genuine restriction maps before topological/sheaf claims |
| PIC/0.2 canonical contract and admission addendum | Separate syntax admission, realizability and external truth. Interpreted/compiled equivalence, negative controls and exact source round trips before generated-machine admission |
| SF-04 / SF-05 and FV-04 / FV-05 | Current source-specific terms, memory identity depths, ordered composition, exact loss/fiber semantics |

`POLY-C-005` is explicitly `superseded_by_owner` under DEC-001; the matching Infinity constitutional-placement segment is also explicitly superseded. Current owner placement is Infinity = IX. Plicastratum's seven strata, seven-complete, DK0 and academic division numbers remain distinct namespaces. The source's scientific obligations survive that placement amendment.

The Q research Python code is expressly a behavioral oracle, not the intended production architecture. It implements only unary/pairwise edges and does not implement Q-Bundles. Its `None` result conflates a search-depth stop with absence; do not reproduce that ambiguity in the new contract. Its optional witness/status labels are descriptive, not authority.

The captured university `src/math/fold.ts` is a separate Re-Pair/straight-line-program exhibit. It strips whitespace in `startFold` and uses a finite Greek-glyph name sequence that can collide with input symbols. Do not port it unchanged as exact-source recovery. Use qualified identities, preserve token boundaries, and retain exact source bytes. The Plicastratum document's referenced `prototype/plicate.mjs` and `prototype/plicate.test.mjs` were not located among imported file paths; do not claim the full original conformance suite was executed.

## First implementation boundary: compiled 3→2 Q-Bundle

Use a new native `.polyia` profile, tentatively `polyia.qpath/0.1`, preserving the existing commission/profile convention. This is a proposed syntax sketch, not currently accepted source:

```text
(commission
  (profile "polyia.qpath/0.1")
  (budget 4096)
  (context Q (contract rational-field.v1))
  (input a Polynomial Q)
  (input b NonzeroPolynomial Q)
  (input field FieldContract Q)
  (bundle euclid
    (kernel polynomial.divmod)
    (in  (dividend Polynomial Q)
         (divisor NonzeroPolynomial Q)
         (coefficients FieldContract Q))
    (out (quotient Polynomial Q)
         (remainder Polynomial Q)))
  (apply euclid
    (bind (dividend a) (divisor b) (coefficients field))
    (produce (quotient q) (remainder r)))
  (emit q r))
```

All source must parse; unknown tails/operators/attributes are refused. Real UTF-8 character and byte spans survive lexer→AST→IR. Declarations describe fixed registered primitives and typed compositions, not arbitrary Python functions. External input JSON is a transport envelope for typed values, never a program or dispatch instruction.

The actual third premise is a field-contract record resolved to a trusted, versioned Q context. A caller's `{status: PASS}` or a reused display name `Q` does not provide that premise. `NonzeroPolynomial` is checked against the actual coefficient vector; a claimed refinement without a passing guard is refused. Missing any one of the three ports prevents execution. The bundle atomically publishes both quotient and remainder only after its checker succeeds.

Proposed compiled IR:

- Canonical package schema, source byte hash/retained bytes, context CIDs, signature table, registered operator implementation identity and dependency source lock.
- Immutable typed SSA slots; names resolve to slot numbers at compile time. The ordered signature records port index, role, multiplicity/alias policy, sort and context CID.
- A bundle instruction contains **one** joint operand vector and **one** result vector. Never lower it to three independently enabled unary arcs.
- Fixed opcodes such as `REQUIRE_CONTEXT`, `CHECK_NONZERO_POLYNOMIAL`, `DIVMOD_Q`, `CHECK_DIVISION_IDENTITY`, `BIND_RESULTS`, `EMIT`. No user opcodes, imports, eval, network, process or filesystem effects.
- Checked derivation/step identity binds operator CID, ordered input content CIDs, context and output tuple. Stable entity ID, immutable content CID, derivation CID and actual ledger execution event remain distinct.

Use existing public native compiler/execution APIs for the closed numeric kernel where that reduces duplication, with its exact source bytes declared as a dependency. A dedicated Q frontend lowers typed bundle/port declarations; do not call the native compiler's private parser internals. If implementing a Q VM primitive directly is simpler, it still needs separately implemented exact arithmetic witnesses and source-pinned code. Decide this after a small test-first spike, not by presenting either architecture as already verified.

Independent verification checks `a=b*q+r` coefficient by coefficient, `r=0` or `degree(r)<degree(b)`, the nonzero divisor and exact coefficient-field context. A separately coded source-level evaluator/known native VM supplies a differential execution path. Both may trust Python/Fraction; report that shared dependency. This is exact algebraic evidence for the supplied finite polynomials, not a formal proof of the whole runtime or an external scientific claim.

The first composition consumes q and r jointly to reconstruct a and compare it with the original. A noncommutative rational division/subtraction fixture detects ordered-port changes. Explicitly swapping two same-typed values in a different valid source program may yield a different answer; it is not intrinsically a type error. Tampering with the compiled binding of the original program must fail package revalidation.

## Q records, strands and relations

Q-String preserves `(src,dst,relation,grammar,scope,level,witness,status,version)`. Q-Bundle generalizes it to named ordered input/output ports and separately identified strands. Add source hashes/locators, context CID, proof method/scope, invariants and losses per strand; do not merge contradictory strands into one Boolean or count weak strands as proof.

Initial admitted executable kernels are pure exact rational/polynomial operations and exact token/record transformations. Descriptive analogy, causal, historical, physical and source-stipulated relations can be stored and inspected, but a status label does not compile them into executable inference. Relations with multiple candidate outputs stay relations. A requested function coercion must demonstrate uniqueness over an explicitly finite domain or refuse.

Multiplicity is explicit. A reusable pure value may fill both arithmetic ports when the signature permits aliasing (`add(x,x)`); a port contract requiring two distinct resource identities cannot be satisfied by one object twice. Multi-output alternatives retain a common tuple/branch identity: do not mix one output from one alternative with another from a conflicting alternative. The first functional kernels have unique output tuples; general nondeterministic execution remains separate from monotone fact closure until branch semantics are implemented.

Context transport uses a registered, versioned finite conversion with its own preservation/loss receipt. A same-named Q context with a different contract is incompatible. Context or operator replacement creates a new eligibility epoch; it never rewrites historical content or replay receipts.

## Next layer: finite search and proof scope

Implement two deliberately different search semantics:

1. Historical G-ship unary graph paths use the product of a finite graph and a compiled DFA, with exact edge-word witnesses and independent plain-search comparison. Report explored product states/transitions and both syntax-admissibility and graph-realizability checks.
2. Fixed-universe hyperedge closure enables an admitted bundle only after all premise identities, roles, multiplicities, contexts and evidence policies are satisfied. Use a pending-premise incidence index and compare against an independent full-scan least-fixed-point oracle. Finite universe and fixed rule epoch are prerequisites for an exhaustive absence certificate. Operators that generate an unbounded new universe are not admitted to that proof mode.

Result distinctions:

- FOUND: a typed witnessed derivation exists.
- DISPROVED_UNDER_COMPLETE_FINITE_SEARCH: the declared finite universe/rule/policy epoch was exhausted and no path exists within it.
- UNKNOWN: missing evidence/adapter or a deliberate external boundary prevents a truth claim.
- BLOCKED: explicit source/policy/type incompatibility, with the scoped reason.
- RESOURCE_LIMIT: work/depth/frontier/output bound reached; never interpreted as absence.

Costs are a versioned vector (operation work, peak live storage, output size, evidence grade, loss set, effects), with declared aggregation. Type/policy admissibility precedes Pareto selection. Keep preprocessing/index build, invalidation and output enumeration costs separate; no O(1) all-graph or all-output claim. A cheaper invalid path remains rejected. Evidence grade is not a physical measurement or generic scalar utility.

A Q-closure certificate accounts for each required port as satisfied, refused or explicitly externalized. It does not certify external truth or an all-science universe. Bounded gaps produce candidate opportunities with baseline, missing typed adapter, falsifiable fixture and expected benefit; a proposed relation is never silently admitted.

## Promotion layer built on those contracts

A promoted object stores exact source bytes/canonical typed IR (declare both separately), external signature, interpretation/observable, expansion DAG, dependency versions, proof scope, cost and loss. Content-addressed payload retention makes expansion possible after deleting working files. A digest alone is not a decoder or authorization.

Two kinds remain distinct:

- **Grammar-letter:** an entire lower grammar is a typed higher-level letter. Namespace alignment is explicit. Higher-language composition declares whether it means language concatenation, product alphabet, substitution, or another registered operation. Exhaustively compare the full declared finite language, including token boundaries and nonmembers where appropriate.
- **Path macro:** a certified typed Q/machine path becomes an operator with the same external ports, preconditions, effects and loss obligations. Substitution/inlining preserves ordered bindings and outputs. A finite-domain certificate enumerates every member of its declared domain; outside it the macro remains proposed unless a separate proof exists.

Plicastratum operators keep exact source meanings: explicate substitutes blocks; implicate checks image membership and returns an ambiguity fiber where the codebook is not injective; complicate constructs a Cartesian product alphabet; replicate performs bounded substitution iterations; applicate declares all seven adapter fields and conformance gates; promote requires packaging/verification admission. Implement these on bounded rank-0/1/2/3 indexed words first, retaining dimensions and token coordinates. Retial graph substitution is a separate port-gluing contract, not a flattened string.

A three-level tower should expand to exact level-0 source/trace identity. Identity depth is explicit: representation, current state, state plus declared ordered group aggregate, and full event chain. Use the source door example to distinguish an untouched Shut state, a canceling loop, and a memorable crossing. “Holonomy” here is the declared source event aggregate, not physical parallel transport.

Canonicalization declares its action. Finite cyclic words can use actual rotation/reflection witnesses under D_n, with nonisomorphic controls; a bounded graph normalizer must not claim universal graph isomorphism or chemistry canonicalization. A lossy quotient exposes the entire finite fiber or explicit ambiguity; retained side information restores the exact original only where promised.

Dependency replacement marks current eligibility stale through the dependency DAG. Old package expansion/replay must remain possible without executing live handlers. New reproduction gets a new run identity. Source addresses and UI views cannot change entity identity.

Trace mining proposes recurring, ordered, context-qualified segments; frequency alone cannot certify. Seal train/held-out workloads and a concrete metric before admitting a macro. An achievable initial metric is total representation bytes including the macro dictionary and construction overhead, not an unmeasured speed claim. If held-out benefit fails, keep the candidate and counterexample with a failed metric. Do not relabel a failed result as improvement.

## Tests before implementation

1. Actual 3→2 Euclidean bundle; all missing-premise permutations; wrong Q version; zero/false nonzero witness; duplicate/unknown ports; changed compiled slot ordering; omitted second output; forged PASS strand.
2. Multi-step reconstruction using both outputs; wrong-context dependency; unique IDs and shared-value versus linear-multiplicity controls.
3. Lexer UTF-8 spans, trailing-source refusal, unknown effect/opcode, malformed/oversized values; independent exact coefficient checker and native/AST differential results.
4. Conflicting/unknown/refuted strands remain separately inspectable; a valid strand is not erased by another refuted claim; no unauthorized function coercion or analogy→causality composition.
5. DFA×graph versus independent product search; hyperclosure versus full-scan fixed point; FOUND/finite-absence/UNKNOWN/BLOCKED/RESOURCE_LIMIT and exact frontier limits.
6. Exact source recovery after deleting working copy; two grammar-letter namespaces and three-level expansion; type/name collision; ambiguous codebook fiber and side-data recovery.
7. Legal bracketings and identities under scoped finite semantics; ordered-port counterexample; dependency change invalidates present eligibility but not captured expansion/replay.
8. Package bytes and actual loaded dependencies pinned, imported malformed package refused, replay performs no execution, new reproduction distinct. Use trusted installed checker before running candidate bytes, with known runtime admission and regular-file checks.
9. Held-out macro evaluation sealed before measurement, including dictionary/index/verification overhead and a counterexample to an invalid macro.
10. Keep all seed ledger events/schema-2 contexts valid. Add a new trusted dispatch name only after pure tests pass and source/dependency capture/replay are integrated by the owning agent.

## What this next slice does not discharge

No blanket PASS for D-PROMOTION or D-QPATH is appropriate. These exact inherited gates remain separate work even if the bounded mechanism works:

- UCG-014: every declared rank and symmetry, including retial, not just rank-1 strings.
- UCG-020: chemistry functional groups and calculus rule chains both unfold to level-0 equal hashes; general “every alphabet” still requires domain adapters.
- UCG-021: E05 derivative orbit classes plus rename, fold and reduce. A finite door cycle is not a substitute.
- UCG-038/039/123: actual recurring PARTS trace mining, USUB inside PARTS and generated integration-by-parts machine trace equivalence to E05.
- UCG-056/057/060/061/068/114: E03 alkane A000602 counts through n≤12; Pólya counts 120/618/3536/22668; benzene Kekulé orbit/loss; 20 functional groups with atom-graph recovery; radical A000598 and alkanol enumeration; 100 atom/charge-conserving reaction rewrites; benzene automorphism group order 12 identified as D6. Generic token folds or polynomial cases do not satisfy these chemistry conditions.
- UCG-074/090/105/117/122: source-specific nomenclature normalization, trig/exp/log critical-pair analysis, generated linear-operator rank/nullity, genuine simplicial closure/standard surfaces, and synthetic-grid hole holonomy/H1 winding. Do not infer those structures from a visual graph cycle.
- UCG-129: a mined rule must improve an actually sealed held-out metric; merely proposing it is insufficient.
- UCG-131/144: two witnessed cross-subject machine isomorphisms, one shared rooted-tree type for Butcher/alkanes/ASTs, and actual PILLAR9 backend agreement.
- Plicastratum §10: original full conformance suite, rank-3 and level-2 requirements, real OSM three-district data with license, sky epoch recovery and independent music applicata remain distinct source gates. A fresh door implementation cannot claim archived prototype test execution.
- Q implementation seed #6/#9: complete native array/list/tree/hash/graph/hypergraph adapters and measured native tuple-hash/adjacency/CSR/CSC/spatial baselines; build/memory/p50/p95/p99/throughput/update/join/path costs. The source explicitly reported losing to ordinary tuple hashing. Preserve that adverse result.
- Q seed #10: compiled leaf/branch/camera/acoustic toy with numerical/physical boundaries. Polynomial Q-Bundles do not constitute that world simulation.
- PIA-082: real finite-cover intersections/restriction maps and compatibility checks are needed before nerve/sheaf labels; missing hypotheses must return UNSUPPORTED. They can be a later explicit finite module, not implicit metadata on every Q graph.
- Full native machine breadth, signed witness/provenance trust, cross-machine performance, open-domain discovery, scientific truth and general program-synthesis claims remain outside finite computational evidence.

## Work sequencing after the seal

A. Freeze Q syntax/IR/port/context contracts and write failing 3→2/negative tests. Implement the source compiler and primitive VM/referee first.

B. Add immutable Q record/projection, multi-strand admission, typed path composition, fixed-universe closure and G-ship DFA product search. Measure actual small-scale index work; leave large performance gates open.

C. Build exact-source promotion packages and finite proof tables over the same typed paths; then grammar-letter substitution and explicit Plica operators/towers. Preserve untouched original source implementations and seed runtime.

D. Integrate ledger capture, current-code pinning, new reproduction identity, historical replay and a trusted portable package checker. Add state/UI views only after pure contracts are stable; views carry no mutation authority.

E. Execute the source-specific chemistry/calculus/trace-mining/benchmark gates as separately scoped increments with their original datasets and thresholds. Do not manufacture a mission-verifier acceptance flag from the count of new tests.
