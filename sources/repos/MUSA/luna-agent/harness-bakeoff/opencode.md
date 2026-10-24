# OpenCode (Anomaly) — brief

- Repo: https://github.com/anomalyco/opencode (npm: opencode-ai) · MIT ·
  ~206k stars, the most-starred open-source coding agent
- What it is: terminal agent. Plan → act → verify loop: reads files, edits,
  runs shell, feeds compiler/linter diagnostics back, iterates. 75+ model
  providers, LSP integration, plan mode, sessions on disk, `/undo` via git.
- Why it's on the list: the most capable open harness; its verify step is
  already shaped like a completion gate.

## Cancel its situation

No starter prompts, no TUI touring. Headless (`opencode serve` / `run`), one
session, one task: the problem in `../README.md`. Plan mode first — the
construct gets designed before anything is edited.

## Where the stop mechanics hook in

- **Before/after/tick**: wrap its tool calls (read/edit/bash) so every action
  logs a transition to the URL store. Sessions already persist on disk —
  mirror the transition record there.
- **Completion gate**: its verify step becomes the compile-and-run gate. The
  session may not close while the program doesn't compile and run.
- **The bus**: shareable sessions — every session link is an inspectable
  record of what the agent did and why.
- **URL state store**: a project-local command the agent must call after each
  action, writing the transition to `seurl://…`.

## Provider

75+ providers including Google (Gemini) and Ollama (local). Bring your own
key or run local — the agent itself costs nothing.
