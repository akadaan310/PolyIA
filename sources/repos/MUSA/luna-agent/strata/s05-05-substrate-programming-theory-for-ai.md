# 05 — Substrate Programming Theory for AI (SPT-AI)

Status: DESIGN DOC. This is my own synthesis — the mathematics of substrates, as a
programming theory for AI. It is distinct from the operator's PURL/Scroll/SubstrateIO
program and does not reuse its names: the language here is **Seurl** — the
Scrollable-Expandable URL language.

## 1. Position

SubstrateIO (the operator's instrument) *measures* transition structures. SPT-AI
*programs* them: it is the theory by which an AI constructs, addresses, navigates, and
composes substrates as first-class computational objects. Measurement stays with the
instrument; programming lives here.

## 2. Mathematics of substrates

**Substrate.** `Σ = (S, →)` where `S` is a finite state space and `→ ⊆ S × S` is the
transition relation. The atoms are his: `0 → 1`, `1 → 0`.

**Trajectory.** `τ = s₀ → s₁ → … → sₙ`. The trajectory space `T(Σ)` is the set of all
finite paths. Composition: `τ₁ · τ₂` when the end of `τ₁` is the start of `τ₂`.

**Higher order.** Trajectories can themselves be states: `Σ² = (T(Σ), ⇒)` where `⇒`
relates trajectories (extension, revision, branching). This is the formal shape of his
"higher-order structure": state → transition → sequence → composition → traversable
path → structure over paths. Nothing here is statistical; everything is discrete and
relational until an experiment earns statistics.

**Observation.** `ω: T(Σ) → O` maps trajectories to observations. SPT-AI keeps
`ω` explicit and separate: transition before interpretation, observation before
conclusion. A claim about a substrate is a pair `(τ, ω(τ))` plus provenance —
observed, simulated, inferred, or hypothesized, each labeled, never mixed.

**Program.** A program over `Σ` is a *generator* `G` of trajectories: starting from an
address, it produces `τ` step by step. Programming a substrate = constructing
generators. A generator is addressed by a Seurl (§3); executing it = navigating to it.

## 3. Seurl — the Scrollable-Expandable URL language

A Seurl names a generator and a position in its output:

```
seurl://<realm>/<generator>/<cursor>
```

Two properties, both load-bearing:

- **Scrollable.** Resolving a Seurl returns a *window* — items plus a cursor — never the
  whole trajectory. The agent scrolls (`…/cursor?next=…`). Context never bloats no
  matter how long the trajectory grows.
- **Expandable.** Any Seurl can unfold: `…/expand` replaces one address with the
  addresses of its components (a trajectory expands into its transitions; a transition
  expands into its states; a state expands into its outgoing generators). Expansion is
  how an agent moves from "what happened" to "what it is made of" without a new tool.

Navigation **is** computation: resolving a Seurl runs its generator up to the
requested window. There is no separate "fetch then compute" — the address space is the
runtime.

## 4. The computational navigational universe

The site built on Seurls is a universe the agent *moves through*, and moving is doing:

- **No waiting periods.** Every resolution is asynchronous: it returns a cursor
  immediately, and ingress streams in during the session. The agent never blocks on a
  full result; it scrolls as production continues.
- **A lot arrives during the session.** Because generators keep producing, a session
  opened on a Seurl accumulates windows over time — the universe fills in around the
  navigator.
- **Re-entry resumes.** When the same agent opens the same Seurl again — even in
  "stale mode," even with nothing new added — it does not get a dead page. It rejoins
  the generator mid-flight: current window, live cursor, production continuing.
  Re-entry is idempotent and never restarts the computation.

## 5. Always-on self-producing computing mode

Formalized: a Seurl denotes a generator `G` with internal state `σ`. A visit is the
transition:

```
visit(G, σ) → ( window(σ), σ′ )
```

`σ′` extends `σ` monotonically — production only moves forward. Every emission carries
provenance (which generator, which visit, which constitutional trace). A Seurl with no
recent visits is not dead; it is *idle-producing* — its generator persists, its state
persists, and the next visit continues exactly where the last cursor rested. This is
the always-on property: the URL is a live process wearing an address, not a document
with a timestamp.

## 6. First Seurl program (seed)

The canonical first program, from the operator's own example:

```
generator counting-permutations over S = {007, 070, 700}
τ = 007 → 070 → 700 → 007 → …
```

Addressed as `seurl://substrate/toy/permutation-cycle/0`. Scroll it: windows of the
cycle. Expand it: the three transitions, then the states, then each state's outgoing
generators. Observe it with `ω` = the visit log. This tiny universe exercises the whole
theory — scroll, expand, navigate, re-enter, observe — before anything larger is built.
