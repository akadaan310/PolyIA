# Biological Tree Growth as Computable Research

## 1. Separate growth processes

**Observed biology:** trees have distinct growth organs, source–sink transport, competition for water/light, environmental adaptation, and species-specific phyllotaxis. **Proposed TREE research:** use biological *architecture* as a family of algorithms, not as a universal mathematical law.

| Research family | Model | Testable TRE adaptation |
|---|---|---|
| Context-free L-system | Symbols rewrite into branches/turtle commands | Deterministic morphology generation; complexity by derivation round |
| Parametric/context-sensitive L-system | Growth rule depends on age, neighbors and resource state | Typed `δ(state, growth_rule)` with bounded preconditions |
| Space colonization (Runions–Lane–Prusinkiewicz, 2007) | Attraction points and nearest-branch guidance | Branch steering toward frontier/targets; negative controls with uniform points |
| Multiscale Tree Graph (OpenAlea MTG) | Organs, axes and plant components at different scales | TREE hierarchy with cross-granularity projections and explicit flattening loss |
| Source–sink/resource allocation | Carbon/light/nutrients distributed among organs | Coupled root→shoot and leaf→resource network; flux conservation audit |
| Phyllotaxis | Angular/sequence placement models | Golden angle **one candidate** among fixed, random and environment-conditioned angle rules |

Sources: Runions et al. (2007) DOI:10.2312/NPH/NPH07/063-070; Prusinkiewicz & Lindenmayer (1990), *The Algorithmic Beauty of Plants*; OpenAlea MTG docs; Lacointe (2000), DOI:10.1051/forest:2000139; GreenLab (2024), DOI:10.34133/plantphenomics.0118.

## 2. Local transition relation

Let `s_t=(structural_graph, coupling_graph, resources, environment, clock)`.

An action `grow(parent, kind, provider)` is admissible iff:

- The parent's node type supports the proposed child (`τ`).
- No structural cycle or duplicate identity arises.
- Root or other resource provider exists, is authorized, and is witnessed where required.
- Resource debit satisfies nonnegative constraints.
- The operation preserves declared index, geometry, and journal invariants.

Then `s_{t+1}=δ(s_t,a)`. Environmental feedback can be introduced as `a = policy(observe(environment_t, s_t))`. A self-generated action **must not** evade type or physical guards.

**Unit conservation (current fixture):** `available_C + spent_C = introduced_C`, analogously for `W`. These are virtual integer test units only; real carbon/water simulation needs unit dimensions, photosynthetic rates, respiration, transport, soil physics and external data. The existing simulation does not approximate any species.

## 3. Mappings and contractions

A branch addition `G_t → G_{t+1}` adds a vertex and one structural parent edge, and possibly a coupling edge plus witness. In a binary tree a second child creates a sibling; biological root/shoot networks and TREE need **variable arity**. A `collapse` maps a subtree to a compact macro node with an inverse witness or recorded information loss. A `split`/`graft`/`migrate` is not automatically admissible: root ownership, resource edges, provenance and spatial constraints must be re-evaluated.

Roots and leaves exchange causal influences in the **coupling graph**, so the full system is generally not a tree, even when its structural projection is. Do not use a tree algorithm to silently discard cross-coupling cycles.

## 4. Prespecified experiments

1. **Controlled siblings:** two leaves of one shoot, each with different root support; prove uniqueness, no unintended parent changes.
2. **Metamorphic replay:** identical grammar/config/seed yields byte-identical state snapshots; altered seed changes commitment but not required structural invariants.
3. **Conservation:** all authorized fluxes preserve a declared budget equation; inject resource underflow and require refusal.
4. **Structure vs environment:** compare Fibonacci/angle, space-colonization and uniform branch positioning using identical budgets; measure branching density, occupied volume, collision count and memory.
5. **Multiscale projection:** derive coarse tree representation and quantify reconstruction error; annotate loss, never imply perfect reversibility.
6. **Species calibration:** only after selecting real observation datasets, fit/bound parameters, test held-out trees; cross-species extrapolation must be assessed.
7. **Compositionality:** compile/instantiate one TREE growth rule in different scopes without copying hidden state.

## 5. Present experimental status

`tre/core.py` demonstrates #1–3 only using an invented virtual resource grammar and a heuristic golden-angle placement. It has not executed actual space-colonization, physiological calibration, GPU-rendered growth, FEM, rigid-body simulation, or ecological validation. Those are **planned** experiments, not completed results.
