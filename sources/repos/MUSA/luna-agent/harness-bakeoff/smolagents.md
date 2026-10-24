# smolagents (HuggingFace) — brief

- Repo: https://github.com/huggingface/smolagents · Apache-2.0 · ~27.5k stars
- What it is: ~1,000 lines of Python. The agent acts by writing Python code
  (`CodeAgent`); each step runs, the observation feeds back, it iterates.
- Why it's on the list: the smallest real harness here, and its hooks map
  almost 1:1 onto the stop mechanics.

## Cancel its situation

No example agents, no Hub demos. One `CodeAgent`, one task: the problem in
`../README.md`.

## Where the stop mechanics hook in

| Stop mechanic | smolagents hook |
|---|---|
| Record before/after/tick on every action | `step_callbacks` — fires every step; write the transition to the URL store here |
| Pre-execution gate | custom `PythonExecutor` — inspect code before it runs |
| Completion gate (compile-and-run or it isn't done) | `final_answer_checks` — return False until the program compiles and runs |
| Plan the construct first | `planning_interval` — explicit plan step before execution |
| URL state store | a tool the agent can write to, or the callback writes directly |

## Provider

Model-agnostic: LiteLLM, Ollama (local), or Google (Gemini) via LiteLLM.
