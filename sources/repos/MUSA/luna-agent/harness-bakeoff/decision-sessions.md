# Decision: one harness, N session-surfaces

Date: 2026-09-28. Decided by Muse, trusted to decide.

## The question

Should every session activation get its own surface harness, or does OpenCode
manage the entire harness?

## The decision

**OpenCode manages the entire harness. Every session activation gets its own
surface — not its own harness.**

A surface is a namespace, not a process:

- isolated working directory per session
- its own session record on disk
- its own URL subtree: `seurl://session/{id}/tick/{t}/…`

The stop mechanics are implemented **once** — in OpenCode's tool-call wrapper
(before/after/tick on every action) and its verify step (compile-and-run gate)
— and they apply uniformly to every session. Each session's transitions flow
into its own URL subtree; all subtrees funnel into Luna, the one state
machine.

## Why not a harness per session

- Sessions are already OpenCode's isolation unit. A harness per session buys
  overhead, not isolation.
- The stop-mechanics integration is per harness *type*, not per session.
  Build once, apply to all N.
- The 20 was a test. This scales to any N without re-architecting: a session
  is cheap, a harness is not.
- Per-session URL namespaces give the "own surface" property — inspectable,
  addressable, kissable — without process sprawl.

## The escape hatch

If a session ever needs a genuinely different loop shape (not just a different
task), *then* it gets smolagents or OPAL — the bake-off briefs stay valid as
alternatives. Different engine behavior earns a different chassis. Different
tasks do not.
