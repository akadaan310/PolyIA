# Q-STRINGS / 0.1 — The Quantified Grammar of Relations

**Research memorandum for Abed Kadan × 7u · 23 October 2026**  
**Program:** Substrate University / G-ships / Division ∞ / FNMS / proposed Division IX / QIA  
**Status:** proposed classical data structure plus a tested Python proof-of-concept. No verified novel complexity breakthrough, physical quantum behavior, string-theory proof, or production claims.

## 0. Research decision

Preserve **G-ships** (grammar of ships): a directed labelled multigraph `H=(V,E,Σ,τ)` where an ordinary relational string is `e=(source,target,label,type)` and the reading of a composable path forms a word in `Σ*`. Extend rather than rename this historical meaning. Preserve both CGT gates: (a) syntactic admissibility, and (b) semantic realizability, with separately metered execution complexity. Do not repeat the earlier JSON/JASON-interpreter architecture: new grammar should compile to typed native IR/bytecode (the current Python is a **reference semantic oracle**, not the desired production compiler). Hash lookup is not Merkle proof, hashing is not semantic decoding, and an address is not authorization.

The name **Q-String** means *a quantifiable, typed, grammar-bearing relational incidence with a content identity, plural metadata strands and compiled operations*. It does not mean a physically vibrating string, physical entanglement, or a qubit. **Q-Index** is the collection of indexes and materialized views allowing particular queries over Q-Strings, and **Q-Address** is a stable, self-identifying reference. **Q-Ship** is a port-checked composition of G-ship edges / Q-Strings. **Q-Closure** denotes coverage and boundary witnessing, not a mathematically complete universe.

## 1. Etymology and mathematical discipline

`quantus, quanta, quantum` is a Latin interrogative/correlative adjective (*how great, how much*). `quantum` is the neuter form also used substantively for an amount; `quantitas` is quantity. The English scientific borrowing narrowed into specialized quantization and quantum theory. Cite Lewis & Short via Logeion https://logeion.uchicago.edu/quantus and Online Etymology Dictionary https://www.etymonline.com/word/quantum.

**Keep five namespaces separate**:

| Namespace | Historical or formal source | House operator inspired by it (NOT etymological identity) |
|---|---|---|
| Latin *quantus/quantum* | Quantity/how great | `quantify(obj, measure, context) -> measured_form` |
| Latin *quantitas* | Quantity/extent | `measure(relation, dimension, witness) -> quantity` |
| Latin *nexus*, *relatio*, *filum* | Connection/relation/thread, separately attested Latin words | `link`, `relate`, `thread` are **new operators**, not decomposition of the word quantum |
| Latin *incertitudo*, *mensura*, *observatio* | Uncertainty, measurement, observation | `ambiguity`, `measure`, `observe`; proposed nomenclature, no Heisenberg-law transfer |
| Modern quantum science | States, operators, quantization, amplitude, probability, uncertainty, entanglement | Only import an equation when its types, assumptions, observable, algebra, and proof contract are explicitly supplied |

Do **not** split `quantum` as if `quan + tum` were two independent Latin physics functions. Its productive ancient morphological analysis is as the neuter inflection of *quantus*, with other cases/genders and historical lexical uses; a software decomposition and an etymological derivation are different objects.

**Latin-form annotations** may be recorded as `attested classical`, `postclassical`, `constructed house neologism`, or `borrowed science`; never blend them. We propose technical names *filum quantificatum* (quantified thread), *nexus operabilis* (operable connection) and *grammatica relationum* (grammar of relations) as **constructed Latin phrases**, not quotations or certified classical technical terms. Latinized naming has no privileged place over Arabic or any other written language in QIA.

### 1.1 What we can legitimately borrow from quantum theory

Real quantum theory uses states such as `|ψ⟩ = Σ_i α_i |i⟩` in a Hilbert space with complex amplitudes obeying `Σ_i |α_i|²=1`, linear operators, and measurement probability `P(i)=|α_i|²`. A mixture of many ordinary candidate graphs is *not* automatically a quantum superposition. Physical entanglement means that a composite quantum state cannot be factored into a product of its subsystems' states; it does not mean that all vertices are directly connected by edges. The uncertainty relation `Δx Δp ≥ ℏ/2` concerns particular noncommuting observables, not an inherent cost of hash lookup. Sources: https://quantum.cloud.ibm.com/learning/en/modules/quantum-mechanics/superposition-with-qiskit and https://quantum.cloud.ibm.com/learning/en/courses/use-a-qc-today/quantum-mechanics-basics.

The **quantum-inspired** research directions that are legitimate but *unproved advantageous* are: (i) maintaining a space of candidate relational configurations, (ii) weighting alternatives and projecting them under observations, (iii) algebraic matrix / tensor representations of higher-order incidence, (iv) recording indistinguishable equivalence classes relative to observations, and (v) optional complex-amplitude interference ONLY if an actual linear-algebra semantics is defined, tested and kept separate from probabilities/evidence. Classical code implementing these concepts remains classical computation.

### 1.2 New, provable information-resolution bound (not Heisenberg)

Suppose a discrete random variable `X` encodes an original relational object and `A=h(X)` is its `b`-bit digest. Because `I(X;A) ≤ H(A) ≤ b`, **`H(X|A) ≥ H(X)-b`**. For a finite source set of size `N > 2^b`, pigeonhole requires at least two originals to share some digest. These are standard information-theoretic facts, not new theorems; their application is important: if the system must recover the exact original from its digest in all cases, it must store or transmit additional information, or constrain the original set to an injectively coded dictionary. Collision-resistant SHA-256 does not solve information loss.

**Our house Q-ambiguity principle:** every inverse query must either return a unique witnessed original, a candidate fiber, or a refusal identifying what information was lost. A mathematically arbitrary hash string cannot yield the original record and its grammar rules without an external index/program registry.

### 1.3 The precise quantization analogue

For a known real-valued scalar `x`, a fixed step `δ>0`, and nearest-integer rounding, `Q_δ(x)=δ · round(x/δ)` produces a representationally quantized value with absolute rounding error at most `δ/2` (ignoring overflow, ties, floating-point implementation details). This elementary mathematical quantization is **not** a claim that the underlying quantity consists of physically discrete quantum particles. QIA can use it to define a reproducible resolution parameter on an observational chart and a result type `Quantized<Value,δ>`.

For an actual quantum model, Hermitian observables satisfy the Robertson uncertainty inequality `ΔA ΔB ≥ 1/2 |⟨[A,B]⟩|`, with the familiar position/momentum `Δx Δp ≥ ℏ/2` as a special case. This differs categorically from the information-resolution bound above. A classical index and a quantum observable are not exchangeable types.

## 2. A progressive computational curriculum (with exact limits)

Let `n` be collection size, `V` graph vertices, `E` graph edges, `d(u)` out-degree, `L` token/key length, `B` B-tree branching factor, `k` number of returned results. Model the requested operations; do not compare unlike workloads.

| Data form | Native relationship/address | Query | Expected/worst time as appropriate | Storage | Q-String encoding/adaptor |
|---|---|---|---|---|---|
| Scalar, fixed-width integer | typed single value / register | read value | `O(1)` in RAM model | `O(1)` | zero-edge node form + an explicit type and named value |
| Dense array | base + element offset | index `i` | `O(1)` | `O(n)` | `at(A,i,x)`; **keep contiguous array native** |
| Variable-width text | encoded bytes / offsets | parse/compare key | often `O(L)` | `O(L)` | canonical bytes plus language/version |
| Singly linked list | `next(u,v)` | successor `O(1)`, find by position `O(n)` | as stated | `O(n)` | one directed `next` edge; no miraculous random-access speedup |
| Doubly linked list | `next`, `prev` | neighboring node `O(1)` | per step | `O(n)` | inverse under consistent doubly-linked constraints |
| Circular list | `next` cycle | successor `O(1)` | traversal `O(n)` | `O(n)` | cyclic invariant / closure witness |
| Hash table | hash bucket/probe | membership | `O(1)` expected under good hashes; `O(n)` worst collision | `O(n)` | identity or typed-pair index |
| BST unbalanced | ordered child edges | find/insert | `O(n)` worst | `O(n)` | ordered edge + comparison constraints |
| AVL tree | ordered child edges + balance | find/insert/remove | `O(log n)` worst | `O(n)` | rotation operators preserving BST invariants |
| Splay tree | self-adjusting rotations | operations | `O(log n)` amortized, possibly `O(n)` one operation | `O(n)` | history-sensitive transformation relation |
| B-tree/B+ tree | multiway ordered separator ranges | search | `O(log_B n)` blocks; often `O(log n)` comparisons | `O(n)` | indexed range/ports, native node pages |
| Trie/radix | symbol-prefix child edges | string lookup | `O(L)` (representation-dependent) | workload-dependent | grammar/alphabet-tower transition paths |
| Graph, adjacency list | indexed neighbors of `u` | neighbor scan or BFS | edge test `O(d(u))` without nested index; BFS `O(V+E)` | `O(V+E)` | G-ship indexed outgoing/incoming |
| Graph, adjacency matrix | `A[u,v]` cell | edge test | `O(1)` | `O(V²)` | native dense representation when suitable |
| Hypergraph | incidence between ports and hyperedges | port/hyperedge neighborhood | at least proportional to enumerated result and relevant incidences | `O(total incidence)` | Division ∞ multi-input/multi-output Q-bundles |
| Tensor network | contraction graph of tensors | contracted output | structure-dependent; may be exponential in width/contract order | structure-dependent | optional solver; never a generic speedup claim |

*Key caveats:* hashing or comparing non-fixed-length keys can itself cost `O(L)`; hash-table *access* being expected O(1) says nothing about traversing k results (`Ω(k)`), reconstructing ancestors, shortest paths, global graph constraints, or nonlocal physics simulation. An ordinary direct `dict[(src,dst,label)]` already indexes edge existence in expected O(1). The Q-String proposal cannot claim invention of that established index.

## 3. The formal Q-String data structure

A minimal pairwise quantified relation is:

`q=(src,dst,relation,grammar,scope,level,witness,status,version)`.

Its upgraded higher-arity **Q-Bundle** follows Division ∞:

`h=(inputs:[(port_i,id_i,sort_i)], outputs:[(port_j,id_j,sort_j)], strands:[(claim,chart,evidence,status,invariants,loss)])`.

No flattening of port order or distinct evidence strands. A candidate underdetermined mapping is not silently upgraded to an admitted edge. Reifying a Q-String as a higher-level node permits relations between relations (e.g., `contradicts`, `depends_on`, `revises`); stratify meta-levels and forbid unbounded self-authentication.

The full **Q-String system** is a layered indexed structure:

`𝒬S=(V, Q, H, 𝒢, 𝒪, 𝓘, 𝓟, 𝓒, 𝓥, 𝓑)`

- `V`: typed entities, subjects, variables, atoms, function parameters, observations, rules;
- `Q`: stored pairwise relation records with immutable content identities;
- `H`: n-ary multi-strand hyperrelations (Division ∞);
- `𝒢`: typed grammars, DFAs, or constrained path languages (G-ships and CGT);
- `𝒪`: compiled registered operators, with pure reads vs guarded side effects;
- `𝓘`: indexes (by CID, ordered port tuple, endpoint pair/type, grammar, outgoing, incoming, temporal/provenance, optional range);
- `𝓟`: explicit provenance and proof/refutation references;
- `𝓒`: charts/observations/scope and identity interpretation;
- `𝓥`: verifiers, admission, round-trip and invariants;
- `𝓑`: budgets, index construction costs, freshness/version and boundary obligations.

**TWO IDENTITIES ARE NECESSARY:** `entity_id` identifies an entity across evolving versions; `content_cid=SHA-256(canonical_wire_record)` identifies exact immutable bytes (modulo explicit canonical encoding). A versioned mutable entity references the current content CID through a time-specific mapping. A relation between two nodes is neither the same as one of the nodes nor guaranteed unique: the same pair can have multiple directions, relationship types, provenance records, statuses, and scopes.

### 3.1 Q-addresses and reversibility

Prototype `qstr:v1:<64 hexadecimal digest>`. Dereferencing is `store[digest] -> canonical bytes -> checked typed record`, not inverse hashing. A richer proposed portable address can be `qstr://<scope>/<grammar>/<relation-role>/<source>/<target>?cid=<digest>&v=1`; this is a **parseable locator envelope** plus a content digest, not a cryptographic hash encoding all readable fields. Parse/unparse must be roundtrip tested with escaping and canonical version rules. Future PURL can be a program at such an address, SEURL an operation channel, SubstrateIO the execution/projection trace, and CLOCK9 an admission/witness workflow; their distinct semantic obligations must survive compilation.

Proposed operation capability descriptor (NOT authority by the URI itself):

`qop=(qaddr,program_id,operator,signature,preconditions,effects,version,proof_policy)`.

`qaddr` resolves immutable data, `program_id` resolves independently versioned compiled bytecode, typed `operator` chooses an authorized entrypoint, `preconditions` are checked and `effects` require version guard and separate capability. The SHA digest never *runs* a function. A reversible operation `f^{-1}` may be advertised only with an inverse certificate and a unique effective decoder; a projection can instead expose the set-valued preimage/fiber.

### 3.2 Self-indexing, not self-oracular

New relational forms can **declare** materializable query patterns at compile time:

```
relation next(src:Node,dst:Node) pure;
index next(src,dst);      // expected O(1) exact membership via hash
index next(src);          // O(1) locate a posting list; O(k) enumerate k successors
rule path(x,z) :- next(x,y), next(y,z);  // join cost, NOT O(1) universally
operator attach_next(x,y) effects(write) guard(no_other_successor(x));
```

This is a grammar for a data structure **and** for its query plan, not a prediction in a raw hash digest. Exact incidence registration and an incremental materialization engine can avoid repeated whole-graph scans where future workloads justify the additional space. Typed relation rules can compile to Datalog-style joins or automata-product traversal; Soufflé is an independent known baseline (https://souffle-lang.org/datalog-language).

### 3.3 Classical relational algebra and operations

- Selection: `σ_pred(R)` filters admitted relation records.
- Join: `R ⋈_{R.dst=S.src} S` forms a path of length two only where ports agree and types permit.
- Projection: `π_(src,dst)(R)` forgets labels, grammar, evidence, etc. Its preimage is a **fiber**, not guaranteed unique.
- Closure: reflexive/transitive closures have appropriate graph complexity or materialization cost; do not infer logical closure by mere word proximity.
- Boolean relation multiplication: `(A∘B)_(i,k) = ∨_j (A_(i,j) ∧ B_(j,k))` for a binary reachability relation; using another semiring changes semantics and computational cost.
- Indexed path grammar: graph state × grammar/DFA state. For a DFA with `|S|` states, build/search a product on the fly. Costs depend on `|S|`, edges visited, indexing, and cardinalities, not a hash-key constant.

## 4. Grammar shapes and adaptors to *every data-structure family*

Not all data structures should be stored physically as graphs. Q-Strings provide a **common semantic address and operator contract** while preserving efficient native execution substrates. Require both an encoder `E_T : T -> QView(T)` and a decoder `D_T` or loss certificate. For a lossless adapter relative to an observable `O`, verify `O(D_T(E_T(x)))=O(x)`; otherwise report lost observables and inverse fibers.

Examples:

- Array `arr[3]=17` → `has_slot(array_id,3,17)`; native array remains O(1) index access.
- List `A → B → C → A` → G-ship `next` edges; verified cycle length 3; cannot claim a null terminator.
- AVL node → `left`, `right`, `balance_factor`, numeric ordering invariant; compiler must check rotations on mutation.
- Hash bucket → `bucket_for(key,b)` plus `lookup_program` but never infer a key from a digest.
- Graph → one Q-String per typed edge and multiple values per endpoint pair.
- Hypergraph → `QBundle` with explicit ordered ports; needed when a reaction or operator consumes three operands simultaneously.
- Streaming sensor → chunked samples, clock, provenance, transforms, and windows; avoid modeling each sample as a heavyweight heap object at scale.
- Physical state → chart, units, law, timestep and numerical error; a relation label does not imply the laws have been simulated.

Proposed reusable internal structures:

1. **Q-Strand:** separate evidence/semantic/status claim on one typed incidence.
2. **Q-Bundle:** typed hyperedge with multiple input/output roles.
3. **Q-Tower:** versioned reversible (where provable) encodings from bytes → symbols → grammar → typed relations → operations → plans.
4. **Q-Materialization:** cached query view and explicit invalidation lineage.
5. **Q-Frontier:** unfilled typed port; unknown and disproved relations have different states.
6. **Q-Closure Certificate:** verifies that every *required* in-scope port is satisfied, refused, or explicitly externalized.

## 5. What 'fully connected' can mean, precisely

**Graph connected:** every relevant pair of vertices has *some path* in the undirected projection of the in-scope graph. This is much weaker than *complete graph* (edge between every pair), and neither proves physical interactions. **Constraint closure:** every required port has compatible realizing incidence, with evidence or a declared boundary. **Physical closure:** a modeled subsystem has explicitly accounted external inputs and boundary conditions; an atom in the physical world is an open system when it interacts with radiation, neighboring matter, measurement equipment, etc. Physical string theory does not establish a complete network of computational data-structure edges inside every atom.

Define **string-complete under scope** `(M,S,O,B)` iff:

1. each entity and relevant phenomenon in scope `S` has a typed model/identity;
2. every required observable `O` is computed or intentionally approximated with a stated error budget;
3. every required interaction port is linked to a verified law, a verifiable refusal, or an explicitly declared external boundary;
4. provenance, units, causality and compatibility constraints pass verification;
5. a checker emits a finite witness or an exact counterexample to the declared bounded claim.

This is a proposed *testable specification completeness* condition, **not** new NP-completeness, an exhaustive physical theory, or omniscient simulation. Connectivity across many domains may be asserted through well-typed multiway incidences rather than pairwise cliques.

### 5.1 The atom toy (correct physical interpretation)

An ordinary hydrogen atom contains one proton and one electron (for protium) with quantum electromagnetic interactions; an ordinary atom is not recursively made of muons, and quarks are constituents of nucleons. CERN overview: https://home.cern/science/physics/subatomic-particles/ . Model `hydrogen = (nuclear state, electronic state, interactions, external boundary)`; do **not** force classical point-orbit interpretations or an unmeasured quark-level internal solver. Port samples:

```
Atom.H
  nuclear_component: ProtonModel        [typed membership]
  electronic_component: ElectronModel   [typed membership]
  dynamics: HamiltonianModel            [scientific law contract]
  electromagnetic_environment: External [boundary]
  observed_spectrum: MeasurementRule     [observable, error]
```

One graph path through a nucleus is a representational link, not a derivation from first-principles quantum chromodynamics. A heavier nucleus or molecule requires a different physical model; use a typed adapter, not a relabelled relation.

## 6. Applying Q-Strings to QIA and the Substrate University

Existing six **registered** academic divisions stay in order (10+10+10+12+10+10=62). This is a program overlay, not a new public division or proof that all 62 Q-theories have been solved:

| Division | Native substrate | New Q-String research work item | Verification |
|---|---|---|---|
| I — Foundations of Computation | LTS, finite automata, admissibility, operational grammar, complexity | G-ship paths/product DFAs, proofs of admissibility vs realizability, complexity contracts | reachability/proof trace and asymptotic benchmarks |
| II — Relational and Generative Mathematics | alphabets, Plicastratum, towers, compositional rules | typed Q-Tower, Q-Bundles, relation grammar composition, controlled inverse | reversible codec/adapters where provable; negative controls |
| III — Programmable Computational Languages | PURL, SEURL, typed machines, address compiler | parseable programmable envelope, registered bytecode operator, provenance-aware effect semantics | compiler/VM tests, capability/version guard, reproducible replay |
| IV — Geometry, Physics, Representation | projection, image/kernel, camera, topology, tensors | charted physics ports, observation-relative fibers, spatial boundary obligations | units, projection loss, physics integrator comparisons |
| V — Acoustic and Generative Sciences | sampling, Fourier, phase, synthesis | typed signal flow, partial inversion, FFT pipeline and acoustic event G-ships | sample-rate bounds, spectral reconstruction loss and timing |
| VI — Computational Worlds and Emergence | CA, BORNE, agents, environment/causal models | state/event DAG, generative world compiler and budgeted materialization | determinism, event replay, conservation where relevant |

Division ∞ retains its original `EFC` typed hyperedges, evidence strands and binary fidelity. Proposed Division IX retains its disadapter/adapter round-trip laws and *atomic-under-observable-and-budget* principle. QIA has an explicit typed-contract home for each of its 62 theoretical records, but a future source scan must verify titles/IDs/epistemic statuses before committing schema changes.

## 7. Research plan for a compiled engine

**Stage A — formal language and codecs.** Define EBNF, escaping/versioned typed IR, canonical byte representation, collision defense, signed witnesses, roundtrip and failure rules. Separate `entity_id`, `expression_id`, `content_id`, `execution_id`.

**Stage B — registries/indices.** Implement index choices: `(src,dst,relation)`, `(src,relation)`, `(dst,relation)`, `grammar`, `kind`, and proven-query materializations. Test hash collision behavior and deletion/index invalidation. O(1) requires fixed-size RAM-model keys or explicit `O(L)` canonicalization cost.

**Stage C — relational VM.** Typed bytecode, guards, pure query operations vs effects requiring capabilities, path-DFA product, joins, n-ary hyperedge composition, independent reference semantics. Reject undefined operations and type mismatches; never execute strings carried by data as code.

**Stage D — integration.** Source-backed adapters to PURL/SEURL/SubstrateIO and the six university registry categories. No modifications to the university's original six doors or reservable VII/VIII. Use Division ∞ and IX as separately scoped source documents.

**Stage E — benchmarks.** Compare adjacency lists, explicit tuple-hash index, matrix for dense graphs, CSR/CSC compact representation, RDF-style indexes, and Q-String compiler. Workloads: exact membership (present/absent), enumerating neighbors, typed multi-join, proof retrieval, bounded regex path, adversarial collision, update/invalidation and persistence; report memory, build time, p50/p95/p99, cold/warm, throughput, correctness, and witness costs. Use C++ or Rust later for meaningful systems claims. This Python implementation is only an initial controlled check.

**Stage F — application.** Declare leaf in world scene: leaf mechanical state/mesh, branch attachment, forces, radiance representation, sound response, observer/camera, timing. Compile only operations verified in target solver. No fake Unreal/GTA asset compatibility or unimplemented all-scale physics.

## 8. Experiments and adverse findings in this packet

The current Python proof-of-concept includes: immutable SHA-256 content IDs; canonical JSON; a typed rule registry; pair/forward/reverse/grammar indices; witnessed exact-word G-ship paths; bounded BFS with parent pointers; explicit refusal; and a classically indexed Q-String store. The witness traversal excludes `hypothesis` and `refuted` records by default; admission of `house` or `stipulated` edges is conditional on the chosen test chart and does not constitute external scientific verification. Executed tests are in `results/test_results.txt`, benchmark observations in `results/benchmark.json`.

**Important limitations**: no automatic grammar discovery from a digest, no physical quantum operations, no Q-Bundle implementation yet, no compiled bytecode, no algebraic optimizer, no on-disk/lock-free representation, no adversarial cryptographic security proof, no collision-resistant multi-device synchronization, and no demonstrated asymptotic improvement over ordinary hash indexing. Test counterexamples cover grammar refusal and tampered data, but not the entire universe of edge cases. The *intellectual gain* is an integrated typed, indexed, verifiable, programmable **semantic contract**, not magic constant-time all-graph traversal.

## 9. Research novelty assessment

Potentially substantive and worth testing: a **single typed grammar whose declarations simultaneously generate: canonical relational encoding, query indexes, native operator contracts, inverse/ambiguity witnesses, and a programmatically auditable boundary-completeness certificate**. Each component has established predecessors (Datalog, graph databases, hash-consing, content addressing, type systems, multi-relational/hypergraph IR, formal concept analysis, query planners). Novelty can only be assessed against prior implementations and published literature; a working integration is not automatically a new theorem, nor an inherent computational speedup. Benchmark differentiated workloads and publish failure cases.

## 10. Source references

- Existing sources attached by researcher: FNMS-001 ZIP, Division Infinity ZIP, Division IX proposal, QIA foundational packet and 62-theory atlas; G-ship definitions in existing `FORMAL_SUBSTRATE.md` (Library).
- Substrate University live code registry: https://github.com/akadaan310/abedkadaancom/tree/claude/new-session-xd8auu/src/content and particularly `registry.ts` and `types.ts`.
- Dictionary: https://logeion.uchicago.edu/quantus ; https://www.etymonline.com/word/quantum
- W3C thesaurus predicate differences: https://www.w3.org/TR/skos-reference/
- Python hash complexity assumptions: https://wiki.python.org/python/language/TimeComplexity.html
- Static minimal perfect hashing: https://www.sciencedirect.com/science/article/abs/pii/S0020025509005271
- Typed Datalog compiled relations: https://souffle-lang.org/datalog-language
- IBM on amplitude/superposition/interference: https://quantum.cloud.ibm.com/learning/en/modules/quantum-mechanics/superposition-with-qiskit
- CERN subatomic particles: https://home.cern/science/physics/subatomic-particles/

---
**Acceptance status for v0.1:** formal construction proposed; 19 Python tests passing; three controlled benchmark scales executed; **no claim** of novel asymptotic complexity or physical quantum/string-theory demonstration.
