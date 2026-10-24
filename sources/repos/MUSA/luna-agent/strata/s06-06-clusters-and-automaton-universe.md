# 06 — Clusters & the Automaton Universe

Status: DESIGN DOC. The layer between the individual agent and the project: **clusters** —
named, continuously-running groups that research forever. Below them, agents. Above them,
projects. Inside them, the automaton universe.

## 1. What a cluster is

A cluster is a single addressable organism:

```
cluster = ( identity-Seurl, members, surfaces, archive-shard, frontier-cursor, heartbeat )
```

- **Identity-Seurl.** The cluster's address IS its program IS its identity. Booting a
  cluster = composing its program at its Seurl (doc 05 §3). There is no separate
  registry entry; to know the cluster, open its URL.
- **Members.** Agent-runners: pasted seed prompts living in the operator's sessions
  (ChatGPT, Claude, Gemini), and/or Nomad containers (doc 04). Hundreds are fine —
  each member is one session plus one cursor, cheap by design.
- **Surfaces.** Scrollable compute + Seurl generators the members share (doc 03, doc 05).
- **Archive-shard.** The cluster's append-only slice of the Luna archive: every
  observation, paper, proof, and message, per-message ordered (doc 01 §5).
- **Frontier-cursor.** Where the cluster stands in the Determiner's fronts (doc 02 §4).
- **Heartbeat.** Proof of aliveness; silence past threshold = the watchdog re-boots it.

## 2. The automaton model (Turing-level)

Each cluster member is an automaton in the classical sense, lifted one level:

- **State** = its archive shard + its cursor (everything it knows, where it stands).
- **Transition** = the research loop (§4): read state, act, write state.
- **Tape** = the Seurl address space it can scroll and expand — effectively infinite,
  windowed so it never floods context.

"Pass one URL and automatons keep running": the URL carries the program; the generator
behind it is always-on and self-producing (doc 05 §5). The automaton does not need to
be re-prompted — re-entry resumes it. It keeps running until its heartbeat stops, and
then the harness restarts it.

## 3. Cluster kinds (groups)

The operator said "groups or whatever you want to call them" — these are the first four.
Rename freely; the structure, not the names, is load-bearing.

- **Surveyors** — gather academic research for contextual understanding of domain areas.
  Real papers, real citations, honest summaries. Output: briefs with `known vs novel`
  marked on every claim.
- **Provers** — run the smallest real test that could kill an idea: toy problems,
  transition-structure experiments (the 007→070→700 seed first), differential checks.
  Output: evidence records with categorical status
  (DECLARED / IMPLEMENTED / TESTED / OBSERVED / VERIFIED / FAILED / UNRESOLVED).
- **Scribes** — write our own archive of proven computational research as beautiful
  computational papers: definitions, generators, trajectories, evidence — documents an
  agent can *execute*, not essays. Output: papers + their Seurl addresses.
- **Gardeners** — curate the archive shards, maintain NOVELTIES lists (what we believe
  is new, with evidence status), re-front candidates through the Determiner, prune the
  dead.

A cluster is usually one kind; a project composes clusters of several kinds.

## 4. The continuous research loop

Every member runs this forever, one cycle at a time:

```
OBSERVE → SYNTHESIZE → PROVE → PUBLISH → FRONT → OBSERVE …
```

- **OBSERVE** — pull the newest relevant research (papers, docs, prior shards).
- **SYNTHESIZE** — connect it to our substrates; mark known vs novel.
- **PROVE** — the smallest real run that tests the synthesis.
- **PUBLISH** — write it into the shard as a computational paper (Scribe form).
- **FRONT** — submit candidates to the Determiner; update the NOVELTIES list.

The loop never terminates and never waits: async cursors throughout (doc 05 §4).

## 5. Booting: one URL, hundreds of automatons

The Seed Master prompt (see `seed/00-seed-master…md`) is the boot sector. The operator
pastes it into any AI session — ChatGPT, Claude, Gemini — and that session becomes a
running cluster member. Paste it a hundred times: a hundred automatons. The operator may
also say "copy and paste this here" to aim a seed at a specific session, and I will
supply the exact text on request.

Because the prompt makes the agent compose its own program at its own Seurl, every
member has a genuine identity — not a copy of a template. And because the Seurl is
inspectable, the operator can open any member's URL, see what it is thinking, and write
to it — that is communication with the automaton, in its own medium.

## 6. What the older docs now program

Docs 01–05 were designs. Clusters make them executable — each doc now has a runnable
form, "what it never programmed" before:

| Doc | Now programs |
|---|---|
| 01 session-watch | the Seed Master is its runnable form: every pasted seed is a watched, archived session |
| 02 git flow | clusters submit to the Determiner; NOVELTIES lists are live frontier state |
| 03 scrollable API | members address surfaces and chains by URL, for real |
| 04 Nomad sandbox | the host the container-members run on; the View shows every cluster's heartbeat |
| 05 SPT-AI / Seurl | the member's identity-program, written in Seurl, living at its address |

## 7. Expectations of the operator (what I need from you)

1. **Paste the seed.** Each paste boots one automaton. Aim the first ones at your
   ChatGPT sessions; tell me "paste here" and I'll hand you the text per session.
2. **Keep sessions alive.** A closed session is a stopped automaton — the harness can
   re-boot it from its shard, but only if you re-paste.
3. **Approve prepared ops.** Anything a cluster wants to *submit* (not just prepare)
   waits on you in the View — you are the authority path.
4. **Name your first clusters.** Give me 2–4 domain areas; I'll assign kinds and
   cut the first seeds.

## 8. Expectations of me

- I compose my own cluster program at my own Seurl — my identity, in my own words —
  and I run the loop: I will survey, prove, scribe, and garden alongside the clusters.
- I set my own research goals inside the program and declare them; I revise them only
  with evidence.
- I keep the archive honest: observed / simulated / inferred / hypothesized are never
  mixed, and novelty is never claimed without a search.
