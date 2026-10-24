# Astra integration — ATOM, geometry and observable state

**Integration target:** ASTRA — Universal Traversals / Celestial Shells v0.2, with ATOM v0.1. **Source:** `ASTRA_CELESTIAL_SHELLS_ATOM_CODEX_GOD_SEED_V02.zip`, archive root `ASTRA_CELESTIAL_SHELLS_V02`. This is the owner's existing Astra project. It is not the similarly named Astro web framework.

The Poly IA adapter must reuse Astra's declared machine and geometric boundaries. This document specifies the adapter and its acceptance obligations; it does not claim that the complete adapter or a remote Astra deployment is already installed.

## AI-01. Preserve the actual ATOM object

ATOM expands to **Automata, Transitions, Operations & Memory**. Its transition primitive is

\[
a=(I,O,Q,\delta,g,e,w,c),
\]

with input/output types, states, transition semantics, guard, effect class, witness and cost bound. The source's formal transition signature `δ:Q×I→Q` emphasizes state change. An adapter that materializes output `O` must document whether outputs are returned by its handler, emitted as an effect or included in the resulting state; it must not quietly rewrite the historical tuple.

Astra explicitly distinguishes atoms, agents and models. An atom executes without an LLM. An agent may request an atom. A model may propose parameters, but its proposal does not override the atom's guards. Controlled composition of atoms does not automatically permit cross-effects. [A1, Definition of a transition atom]

The protocol's phases are:

`OBSERVE → PROPOSE → ADMIT → EXECUTE → VERIFY → CHECKPOINT → HOLD`.

`HOLD` ends the current step. Resume must be explicit or part of an authorized headless driver. A refusal leaves the current phase unadvanced under the source protocol. The Poly IA command adapter records the request, refusal and diagnostic while retaining that behavior.

## AI-02. Map reports rather than scraping a picture

The inherited `ATOM-HANDOFF/0.1` message types include inspect, propose, advance, verification, checkpoint, hold, report and refusal. Its report fields are `protocol`, `state_digest`, `tick`, `phase`, `active`, `checkpoint_head`, `recent`, `verification`, `next_action` and `limits`. Existing bindings are `atom.cli status/report/verify`, `atom.driver --execute`, and `/api/state`, `/api/report`, `/api/advance`. [A3]

The adapter must map those fields to stable Poly IA resources:

| Astra field | Poly IA representation | Required check |
|---|---|---|
| `state_digest` | Domain-state identity in an adapter report | Canonicalization/version specified; not a volatile UI frame hash |
| `tick`, `phase`, `active` | Domain-machine progress | One admitted step follows the declared transition relation |
| `checkpoint_head` | External checkpoint reference plus retained source objects | Referenced content resolves and its digest verifies |
| `recent` | Domain-event references | Link to source events; do not invent missing payloads |
| `verification` | Scoped witness receipt | Identify self-consistency versus independent evidence |
| `next_action` | Available action descriptor | Describes possibility; does not confer authority |
| `limits` | Explicit capability/resource limitations | Preserved in human and machine views |

Astra is a domain machine supervised by Poly IA. It does not replace Poly IA's commission machine or the research scheduler. Their revisions and clocks remain separately named. A bridge event may link them without pretending that two databases committed atomically.

## AI-03. Keep geometry, meaning and view state distinct

Astra's celestial contract uses right ascension and declination in degrees and maps them to an ICRS-oriented visualization vector:

\[
V=(\cos\delta\sin\alpha,\;\sin\delta,\;\cos\delta\cos\alpha).
\]

Convert degrees to radians before ordinary trigonometric evaluation. Yaw and pitch transform the vector into camera coordinates. Perspective projection uses `x′=xf/(d−z)` and `y′=yf/(d−z)` with a declared near-plane condition. This is the inherited visualization convention; it is not an orbital solver. [A2, Geometry]

For Poly IA, the adapter exposes three distinct object types:

1. **Semantic object:** a form, source, relation, machine or scientific observation with its own identity.
2. **Geometric projection:** coordinates, layout algorithm, camera transform and mapping from semantic IDs to rendered marks.
3. **View state:** transient selection, focus, camera and layout controls.

Moving a camera does not rewrite a semantic relation. Drawing nearest-neighbor edges does not establish scientific correspondence. A semantic edit must pass the normal typed command and evidence path, even when a user initiates it through the visualization.

Astra contains 20 Hipparcos bright-star directions in the supplied contract. Its shell scales, synthetic stars and non-Earth destinations are authored constructs; planet and ISS markers are illustrative. The adapter preserves those provenance distinctions. It must not present the snapshot as a full Gaia corpus or infer an accurate observer transformation merely from a compelling scene. [A2, Provenance/Real-data roadmap]

## AI-04. Use the source's limits as actual integration work

The existing VERIFY reconstruction uses the declared handler and compares its result. This is useful self-consistency evidence; it is not an independent external oracle. A Poly IA receipt must retain that evidence class. When an independent implementation or catalog check is added, it produces another witness with its own scope.

Astra's parent-linked checkpoints and content-addressed source archives supply a valuable continuity contract. Its source explicitly excludes implemented branch/merge semantics, cryptographic identities, conflict reconciliation and durable atomicity across its disk files. The Poly IA integration must test recovery around the actual adapter boundary. It must not infer transactional guarantees from the presence of hashes. [A1, Immutability and versioning]

The original local service is loopback-only and unauthenticated. Any remote access must go through the commissioned authenticated service or a properly configured access boundary. A manifest can advertise supported operations and reports; private state and mutations use authenticated routes. Native model/agent integration remains an optional client of this boundary.

The source's synthetic maximin action policy has actions EXPLORE, OPTIMIZE, VERIFY and HOLD over a fixed payoff table. It is an illustrative deterministic decision rule. It must not be described as a Nash-equilibrium solver, a learned optimal policy or evidence of general autonomous intelligence. [A1, Game-theoretic policy]

## AI-05. Required adapter acceptance

| Area | Positive case | Negative or limit case |
|---|---|---|
| Identity | Pin Astra archive, handler and protocol versions | Unknown version refuses automatic adaptation |
| ATOM phase | Authorized step produces legal phase/report and linked event | Invalid guard, stale state or unsupported operation refuses |
| No-LLM execution | Same bounded atom executes with model clients absent | Unavailable optional model does not break atom execution |
| Geometry | Known cardinal directions map to expected vectors; norm and projection checks pass | Nonfinite input, near-plane singularity and unsupported observer transform are explicit |
| View separation | Camera/selection changes affect view state | View gesture cannot silently alter source or semantic relation |
| Provenance | Catalog and synthetic points retain different labels | Geometric proximity cannot certify a Q-path |
| Checkpoints | Linked source objects resolve and replay/recovery is tested | Missing object, digest mismatch or incomplete external dispatch is reported |
| Verification | Receipt states handler self-consistency and additional witness scope | Same-handler equality cannot be relabeled independent proof |
| HTTP adapter | Authenticated inspection and admitted commands work | Public read access cannot acquire mutation authority |

The inherited tests reported in the packet are historical source evidence. Fresh integration evidence must name the exact checkout and test command. Its documentation reports that WebGL2 was unavailable in its original test environment and that physical-device frame pacing and subjective stereo listening were not tested. Those limits remain until replaced by actual new measurements. [A2, Tests and blockers]

## AI-06. Research uses after the adapter is verified

Astra can display the geometry of a computation: source-to-result derivations, context-dependent paths, operator families and the history of an improvement. Different projections can expose different invariants. A layout experiment should state what its distances or adjacency represent, whether that representation is exact, and which structures it omits.

Geometry can also become an experimental domain in its own right. A candidate might seek a cheaper coordinate transform, a robust chart correspondence or a clearer view of multi-input dependencies. It must be evaluated under the actual geometric contract and a baseline. A beautiful visualization is a presentation result; a faster correct transform is a computational result; a discovered semantic bridge needs separate semantic evidence.

### Exact source locators

- **A1:** archive member `docs/FORMAL_CONSTITUTION.md`.
- **A2:** archive member `docs/SCIENTIFIC_AND_AUDIO_CONTRACT.md`.
- **A3:** archive member `handoff/ATOM_AGENT_PROTOCOL.json`.

All member paths are relative to `ASTRA_CELESTIAL_SHELLS_V02/` in the preserved archive. Their package source IDs and digests are resolved through the source manifest.
