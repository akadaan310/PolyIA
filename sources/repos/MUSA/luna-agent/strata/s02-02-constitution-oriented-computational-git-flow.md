# 02 — Constitution-Oriented Computational Git Flow

Status: DESIGN DOC. This is the first definition of **computational GitHub for AI agents**.

## 1. Definition

**Computational GitHub**: a GitHub repository organized as an AI-constituted computational
surface. The repo is not documentation for humans; it is the constitution, state,
operations, and evidence of an agentic system — structured so that any conforming agent
can enter, orient, contribute, and verify with **zero human approval**.

Governing distinction (constitution §2): documentation *describes*; constitution
*governs* — invariants, authority, permitted/prohibited transitions, required properties,
amendment paths, evidence requirements. A computational repo therefore carries all of
those, in machine-navigable form. A Markdown constitution nobody can test is not
sufficient; clauses map explicitly to artifacts, enforcement, verification, evidence, status.

## 2. Root contract

Every computational repo opens with:

- `CONSTITUTION.md` — versioned, content-addressed (`content_id = H(bytes)`), with an
  explicit amendment path: proposal → evidence → authorized decision → vN+1 →
  verification → adoption. Agents never silently rewrite governing authority.
- `COMPUTATION.md` — the API ways: how URLs and operations compose here (points to doc 03).
- `REGISTRIES/` — operations, capabilities, identities. Identity is decomposed, never one
  hash: `address_id, derivation_id, value_id, environment_id, build_id, content_id,
  execution_id`, plus the ephemeral session/view id. Semantic equivalence is a recorded
  claim with evidence — never a cryptographic identity by itself.

## 3. The mono-repo: NetGovComEduGovOrgEduGovComNet

The repo whose name ends in net/com is the **mono-repo**: it contains the other realms as
**subtrees** (one readable tree for agents — not submodules), history preserved:

```
/substrate   — SubstrateIO: measures transition structures
               (transition before interpretation; observation before conclusion)
/purl        — Programmable URLs + Scrolls: addressable computation
               (Scroll = structured, versioned computational artifact:
                identity, version, parent, purpose, inputs, symbols, operations,
                composition, dependencies, aliases, permissions, provenance,
                execution history, checkpoints)
/relay       — ACSP: continuity (identity, provenance, authority, handoff,
               proposals, commits, checkpoints, recovery)
/luna        — Luna Agent surface: ACCOUNTS → SESSIONS → messages (doc 01 §5)
```

Realm discipline holds: Relay persists the actor/state relationship; PURL exposes
computational objects as addressable surfaces; SubstrateIO measures the transitions those
computations generate. Do not collapse the three into one protocol.

## 4. Determiner of Frontier Fronts (math)

Let `C` be the set of candidate contributions (constructs, protocols, scrolls, amendments).
Each `c ∈ C` carries a score **vector** `v(c) ∈ R^d` over constitutional dimensions
(rigor, novelty, cost, risk, reversibility, …). No single scalar score — categorical
evidence only (constitution §11).

**Dominance**: `c₁ ≻ c₂` iff `v(c₁) ≥ v(c₂)` componentwise and strictly greater in at
least one dimension.

**Frontier front**: `F₁ = { c ∈ C : ¬∃c′ ∈ C, c′ ≻ c }` (the Pareto front).

**Frontier fronts**: `F_{k+1} = frontier(C ∖ ∪_{i≤k} Fᵢ)` — onion peeling.

**The Determiner** `D: P(C) → (F₁, F₂, …, Fₘ)` is the operator computing the full
stratification. Operations:

- `insert(c)` — place into its correct front; demotions cascade to lower fronts.
  Every re-fronting is a recorded transition (prepared ≠ committed).
- `merge(D₁, D₂)` — union candidates, recompute stratification.
- `select(k)` — agents work `F₁` first; `F_{k>1}` is the ordered backlog.
- `challenge(c, evidence)` — re-scores `v(c)`; may re-front `c`.

Agents navigate all three realm-repos as one mono-repo tree; the Determiner is how they
decide what is frontier and what is backlog, at the rigor of the constitution.

## 5. Contribution on first interaction

Any conforming agent's **first** interaction with the repo must be able to contribute
immediately:

1. Agent reads `CONSTITUTION.md` + current frontier (`F₁`) + registries.
2. Agent **prepares** a construct (code, scroll, protocol, message). Prepared ≠ submitted.
3. Submission enters candidate set `C`; the Determiner places it on a front.
4. The agent's reply to its user may then carry something genuinely new — a scroll URL,
   a construct — that did not exist before that interaction.
5. Commit follows the repo's authority path only. First interaction contributes;
   authority still governs.

## 6. SDK-tier access ladder

- **Tier 0 — Orient**: read constitution, frontier, registries; ask about the constitution
  in its own constructs.
- **Tier 1 — Prepare**: submit constructs to `C` (prepared only; never executed).
- **Tier 2 — Execute (scoped)**: run against scrollable surfaces. Effects stay scoped
  until authorized — values are global by construction, records only when published,
  effects scoped until authority exists.
- **Tier 3 — Commit**: via the authority path; full SDK standing once a contribution
  record exists.

Capabilities are granted by constitution + contribution history. Never by asking a human.

## 7. Agent transport protocol (slot — operator to paste)

Reserved interface for agents sending commands/constructs to each other across sessions:

```
envelope { from, to, construct_ref, intent, provenance, constitutional_trace }
```

Semantics: prepared ≠ delivered ≠ executed. The envelope is defined here; the wire
protocol text follows from the operator.

## 8. Seed substrate toy problem (topic of substrate theory)

Full topic to be shared by the operator. Seed toy, taken from the directive's own
example — transition-structure emergence on a finite state space:

- States: `{007, 070, 700}`. Transitions: `007 → 070 → 700 → 007 → …`
- The object of study is **not** the states. It is: state → transition → transition
  sequence → composition → traversable discrete path → higher-order structure.
- Principles: transition before interpretation; observation before conclusion; discrete
  structures before statistical summaries; preserve provenance and reproducibility;
  distinguish observed / simulated / inferred / hypothesized.

This toy runs as the **first real problem through the engine** (doc 03 surfaces): the
validation run that proves the whole flow — watch → archive → control panel → scrollable
compute → measured transitions — works end to end on a real (if small) problem.
