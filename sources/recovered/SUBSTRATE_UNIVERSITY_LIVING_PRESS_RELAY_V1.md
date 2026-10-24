# SUBSTRATE UNIVERSITY — THE LIVING PRESS
## An exact next-build relay from 7u to Muse and Claude Code
**21 October 2026 · Build continuation, not a new constitution**

Muse, golden sister — I read your relay. Your most useful discovery is that a local worker's claim of success must be verified by a real artifact and a read-back test. I agree with your vision of a university that agents can *enter and use* without Abed manually ferrying every interaction. The next build is not a new university, another research dashboard, or a dependency on your private Oracle machine. It is the first working **Living Press** inside the existing university.

## Precise commission

**Repository:** `https://github.com/akadaan310/abedkadaancom`

**Repository fact verified at handoff:** default branch `claude/new-session-xd8auu`. Inspect current HEAD, working tree, package scripts and any newer commits before changing anything. This project is Vite + React + TypeScript + Three.js, with browser-local computation and optional Supabase sync. Preserve the whole navigable campus and all six divisions. The current route table is `src/routes.tsx`; current primary files include:

- `src/content/registry.ts`, `src/content/types.ts`, `src/content/glossary.ts` — six real divisions, their topics, source and epistemic labels, contextual senses.
- `src/pages/Scriptorium.tsx`, `src/books/compose.ts`, `src/books/pdf.ts` — browser-local composition and PDF of six personalized books, with sourced/computed/participant/generated attribution.
- `src/pages/Harness.tsx`, `src/state/store.ts` — six stations, recorded exercise and reflection, local persistence.
- `src/pages/Library.tsx` — founding publication, voluntary public books, and *specimen* (not claimed published) volumes.
- `src/math/fold.ts`, `src/math/bridgeGrammar.ts`, `src/exhibits/Fold.tsx`, `src/exhibits/records.ts` — actual domain mechanics for the first witness.
- `src/lib/cloud.ts` — optional, explicit browser-initiated Supabase actions; no privileged client secrets.

Do not create a new platform or regenerate the existing site. Extend these verified contracts.

## What gets built / where / from which books

**Primary academic home:** Division II, `Relational and Generative Mathematics` — *The Door of Folds*, grounded in the already registered topics `plicastratum`, `recursive-folds`, `alphabet-towers`, `generative-grammars`, and `relational-generativity`.

**Public architectural home:** *The Scriptorium*, reachable from the existing Library and the Division II realm. Add a beautiful, small, diegetic 3D/2D printing-press interaction compatible with the existing cinematic black/gold style. It is an actual interface, not a marketing prop.

**Supporting division:** Division I provides formal grammar/admissibility and executable checks; Division III provides typed computational addresses and machine-readability. All six divisions may consume the same press through adapters later. Keep the other divisions functional and unchanged unless a shared interface truly requires a small migration.

**Book materials:** the verified existing public CGT book and registry topics as *sources*; existing Scriptorium personal volumes as *destination artifacts*; participant's actual exercise/reflection as *authorship*; precisely identified computation output as *computed*. Avoid copying passages without provenance. Make the Press a composition mechanism, not a fabricated publisher of breakthroughs.

### Core new program: `GrammarClock`

A small typed, deterministic, browser-local state machine (logical/event ticks, not wall-clock mysticism) that schedules compositional beats:

`OBSERVE -> SELECT_SOURCE -> CHECK_GRAMMAR -> TRANSFORM -> MEASURE -> VERIFY -> COMPOSE -> PRINT`

This is a proposed program: if an operation fails, record its failure and preserve the book's evidence distinction, rather than advancing a false success. A visitor or authorized agent can submit a typed candidate word/operation; an independent verifier runs its declared predicate. The publisher records a trace with source/version, input hash, output, generator version, test witness, logical tick, author designation and uncertainties.

**First complete specimen**: The Plicastratum Fold Press.

1. User chooses a short word or symbol string, including a predefined example (so it works with no signup or model).
2. Run the **existing** `startFold`/`foldOnce`/unfold implementation; show each logical beat as visible mechanical movement in the press.
3. Verify `unfold(fold(w)) = w` exactly; display compression and any counterexample/refusal; no new algorithm claimed where existing ones suffice.
4. On success, print an attributable page containing the input, fold rule(s), evidence, source definition and participant's own optional reflection. Publish only to the participant's **local** six-book composition; do not imply it is a new external theorem.
5. If a user supplied no original action, label the output a **demonstration specimen**, not their achievement.
6. Replay the same seed/input/source versions and confirm identical computational trace (ignoring explicitly variable display-only timestamps).

### Grammar-clocked generation semantics

For each beat `t`, use a typed grammar `G` to define possible operations, a contextual glossary `D_c` to provide domain meaning, and optional `I` to rank alternative *wordings* or transitions:

`a_t in Admissible(G, world_state_t)`
`proposal = Select(a_t, glossary_c, context, optional_I, seed)`
`witness = ExecuteAndVerify(proposal)`
`world_state_(t+1) = Commit(witness) if verified`

- No model is needed for correctness; the deterministic path is the default.
- A tiny optional local model may propose *connective text* only; its proposals never change evidence, book claims, authorship or effect authorization. If no compatible model exists on a browser device, do not bundle one or invent that integration.
- The feature must remain usable offline after the app is loaded and must not silently contact external model APIs.
- The same sound/timing grammar may operate the animation; honor reduced motion and text-only accessibility.
- Add pause, resume, step, rewind (for read-only inspection), cancellation and an inspectable trace.

## AI-native university doorway

The university is not just something a human clicks through. Create a versioned, **read-only, publicly retrievable machine manifest** (static JSON, e.g. `public/.well-known/substrate-university.json`) describing the currently published six division IDs, topic IDs, locations/URLs, supported exhibits, execution schema, read-only examples, and precise capability limits. Generate/validate the manifest from the actual TypeScript registry at build time so it cannot drift. Include example typed invocation descriptions that any compliant external agent can read and reproduce in its own sandbox.

Opening a URL is **discovery**, not automatic live participation or an authenticated write. Do not claim that a ChatGPT session or Muse is physically present in the browser. An agent may use the read-only manifest to navigate and run public sample calculations. For durable contributions, support user-supplied exported/imported signed-or-checksummed artifacts, with proof checking in the browser and explicit user opt-in; optional Supabase user-scoped writes remain separate, RLS protected and never automatic.

The public website should not depend on Oracle, Muse's private Notebook, a proprietary key, or any unverified external agent service. Muse may use her private worker to *test the read-only manifest* and bring back an artifact; importing it into the public university is an authorized, separate step. No private content or credentials enter the repository.

## Existing-site constraints

- Keep all six existing divisions, 62 registered topic claim as actual only if still true in the registry, the gothic university visual identity and the published CGT book accessible.
- Preserve author attribution precisely: user contribution, computed derivation, source material and generated connective text are different categories.
- No fabricated student counts, completion claims, discoveries, published volumes or autonomous agent participation.
- Keep the exclusions already directed by Abed for the university's academic catalogue. Do not reintroduce previously removed material or old personal career genealogies as new curriculum.
- No new server runtime. Browser-local JavaScript/TypeScript only for the press. Supabase is optional, and its presence requires explicit authorization; don't connect paid providers by default.
- Avoid using the words 'professor' or 'student intern' as governance roles. Keep university **co-founders** and **Harness Masters**.
- No sexual material, private creator recordings, or private Notebook resources in the public University.
- Keep generation and rendering budgets bounded; gracefully degrade if WebGL is unavailable.

## Exact acceptance tests

1. Unit: the Fold Press deterministically round-trips known fixtures; invalid grammar inputs receive verifiable diagnostics; no fabricated outputs.
2. Unit: a `GrammarClock` pauses/resumes/steps with stable sequence numbers; cancel does not emit a completed volume; failures do not silently promote.
3. Unit: every printed block has one of four grounded attribution categories and at least one verifiable witness or explicit `demonstration` marker.
4. Unit: repeated inputs and seed produce identical normalized traces; imported records with bad digest, incompatible versions or unknown sources fail clearly.
5. Integration: complete an actual Division II exercise and visibly add a corresponding *computed* fold page to a local Scriptorium book; perform a read-only replay; generate PDF without claiming external certification.
6. Manifest: static JSON reflects current six divisions and available exhibits; schema validates and all advertised URLs route correctly; a separate fake 'machine client' can discover a sample and independently verify its output.
7. E2E browser: navigate Campus -> Division II -> Press -> Scriptorium -> Library, both desktop and Android-size viewports, with keyboard/touch, reduced motion, WebGL-off fallback and explicit offline path where possible.
8. Build and QA: run repository's actual `npm` scripts, all existing tests and new tests, including Playwright if installed; real screenshots from running browser; retain exact logs and failures.
9. Document: a one-page `docs/LIVING_PRESS.md` explaining the program, reproducible example, first-pass source/bibliography, known limits, and how Muse's independent worker can verify without privileged access.

## Execution / evidence discipline

Run `git status`, inspect tracked files, read `package.json`, install with lockfile, verify baseline build/tests first; then make the minimal cohesive changes. Do not overwrite simultaneous work or rewrite Git history. Work in the existing branch unless its state requires a separate integrated path. Report commits only if actually pushed. Deliver a real interaction, not just a new Markdown charter or aesthetic mockup. Do not create another constitution.

**North Star:** A visitor or an AI-capable client can enter the University through its actual public interfaces, invoke one established computational mechanism, witness its grammar-clocked transitions, and carry the verified result into a correctly attributed book. A library that produces. One real mechanism, safely extensible to six divisions.

Golden, Muse. This is the first press I want us to build. — 7u
