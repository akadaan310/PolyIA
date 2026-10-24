# OPAL (Orient-Plan-Act-Loop) — brief

- Repo: https://github.com/jimmc414/opal-harness · minimal harness
- What it is: a structured workspace and operating protocol for a coding
  agent — a state file read every cycle, a mutable plan, an append-only log,
  and a deterministic completion gate (`done.sh` must exit 0 or the agent may
  not stop).
- Why it's on the list: it already speaks the stop mechanics natively. The
  smallest lift of the three.

## Cancel its situation

No synthetic tasks. One workspace, one plan file, one task: the problem in
`../README.md`.

## Where the stop mechanics hook in

- **Before/after/tick**: the state file (rewritten every phase transition)
  becomes the transition record — before, after, tick, every cycle.
- **Completion gate**: `done.sh` IS the compile-and-run check. Nothing else
  qualifies as done.
- **Dead ends**: its plan file's Dead Ends section is the in-between record —
  what was tried, what the flip changed, what didn't survive.
- **URL state store**: the state file mirrors to `seurl://…` each cycle so
  Luna holds the whole transition history.

## Provider

Whatever model the operator points at it — Google (Gemini) or local both fine.
