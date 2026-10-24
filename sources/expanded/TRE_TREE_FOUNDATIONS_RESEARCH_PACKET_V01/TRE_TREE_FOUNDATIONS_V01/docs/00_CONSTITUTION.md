# TRE/TREE Constitutional Ontology

## 0. Governing object

**TREE** is the formal substrate of branching systems. **TRE** is the eventual True Real Engine built on its contracts. **HOMELESS** is an optional downstream consumer; it does not define the foundations. Dark remains the existing portable engine track. No current rendering backend is mandated by this research document.

A tree analogy is productive only if its relationships are typed. Biological roots and crowns comprise **two networks with coupled fluxes**. A single rooted computer-science tree is insufficient to express resource-to-output feedback. This distinction is structural, not supernatural.

## 1. Formal tuple

Define `T = (V, E_s, E_c, τ, X, R, A, δ, I, P, W)` where:

- `V`: finite set of typed and addressable nodes.
- `E_s ⊆ V×V`: **structural parent-child** arcs; each nontrunk node has exactly one structural parent. The projection is a rooted arborescence.
- `E_c ⊆ V×V×Relation×Witness`: **coupling edges** (root→leaf support, leaf→growth resource, compilation dependencies, etc.). This graph may contain cycles and is **not** a tree.
- `τ: V→{trunk,root,shoot,leaf,fruit,...}`: extensible type classifier.
- `X`: a well-defined state space, containing geometry, control state, resources, virtual clocks, and policy.
- `R`: finite typed virtual resource ledger (units and interpretation must be declared).
- `A`: admitted operation alphabet (grow, attach, detach, query, compile, render, tick, absorb, ...).
- `δ: X×A ⇀ X`: **partial transition** defined only for admitted operations.
- `I`: invariants (acyclic `E_s`, parent typing, resource bounds, capabilities, read-only source).
- `P`: provenance and hashed source/artifact relationship records.
- `W`: checkable witnesses/counterexample certificates.

Admissibility: `Admit(x,a) = type_ok ∧ invariant_preserved ∧ policy_ok ∧ resources_available ∧ evidence_present`. Only when it holds may `δ(x,a)` be evaluated. A candidate is not a successful transition merely because an LLM proposed it.

**Computational fruit** is not identical to a terminal node: it is a **verified, portable, self-describing artifact** generated from the tree, such as a compiled program, mesh, scene, shader graph, simulation snapshot, proof, or executable model. One leaf can generate many fruits; one fruit can be reused as a seed for another TREE instance.

**Computational seed** is the minimum immutable, versioned record required to reconstruct a valid instance (grammar ID, config/state origin, corpus commitments, operator set, RNG seed if any, execution model). A seed's hash does not contain the objects it identifies; missing objects must be retrieved separately.

## 2. Growth and sibling example

The test fixture starts with trunk `t0`, root `r0`, shoot `s0`. It:

1. Grows a new root `r1` under `r0`.
2. Grows a shoot `s2` under `s0`.
3. Grows leaf `l3` under `s2`, witnessed by `r1`.
4. Records root absorption and leaf carbon acquisition (virtual accounting units).
5. Grows leaf `l6` under `s2`, witnessed by `r0`. `l3` and `l6` are now siblings.
6. Grows fruit `f7` under `l3`, witnessed by `r1`.

The structure is replayable and validated. **Resource support** does not make `r1` a structural ancestor of `l3`; support is a typed coupling edge. This is the critical formal separation the natural tree metaphor reveals.

## 3. Operators as a grammar

```ebnf
operation ::= grow_root | grow_shoot | grow_leaf | grow_fruit
            | absorb | photosynthesize | checkpoint | inspect ;
grow_root ::= "grow-root" root_id ;
grow_shoot ::= "grow-shoot" shoot_id ;
grow_leaf ::= "grow-leaf" shoot_id "supported-by" root_id ;
grow_fruit ::= "grow-fruit" leaf_id "supported-by" root_id ;
```

This is an illustrative **surface contract**, not a parser of these exact strings. The Python model realizes analogous typed method calls. A future `.p9` grammar and bytecode backend must compile the operations without reducing the operational semantics to JSON data interpretation. JSON schemas are for interoperability and tests only.

## 4. Division mapping

| University research division | TRE responsibility |
|---|---|
| I — Foundations of Computation | State-transition semantics, cost profiles, grammar admissibility, formal verification |
| II — Relational & Generative Mathematics | Alphabet towers, TREE morphology, fold/unfold, graphs, Ingrammatica, witnessed bridges |
| III — Programmable Computational Languages | Native compiled notation, PURL/SEURL address protocols, CPU/VM operations |
| IV — Geometry, Physics & Representation | Scene transformations, collision geometry, render passes, image/kernel semantics |
| V — Acoustic & Generative Sciences | Signal transforms, scheduled audio, animation-to-sound coupling |
| VI — Computational Worlds & Emergence | Dynamics, environments, procedural worlds, agents, causal simulations |
| IX / Infinity | Cross-division meta-maps pending author research; do **not** invent VII/VIII or turn IX into a literal campus door |

CGT's operational grammar `(Σ, A, ⟦·⟧, L)` describes legal moves on a structure. Grammar in Numbers distinguishes values from numerals, encodings, and executing machine states. TREE uses both distinctions: a content hash is a *representation*, not the semantic value, and a legal word need not be realizable on the current state.

## 5. Claims not allowed

- O(1) random access to any object by virtue of Merkle hashing; expected hash-table lookup and Merkle proof cost are separate.
- Tree growth universally follows Fibonacci ratios; golden angles can be an optional heuristic, measured against alternatives.
- A grammar proves a source's physical or biological semantics merely through structural similarity.
- A process container or WebAssembly sandbox is a replacement for the GPU driver, kernel, or operating system.
- Structural replay plus SHA-256 implies secure signed provenance; trusted roots/signatures are future mechanisms.
- A root/leaf correspondence is evidence of real plant physiology absent controlled empirical measurements.
