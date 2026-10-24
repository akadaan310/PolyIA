# URL-MACHINE — protocol sheet

## 0. Particles
- HARNESS: the coordinator. Holds the single shared state machine.
- SESSION: a browser/context. Stateless except its URL.
- ADDRESS: a URL. A session's locus. The only thing a session knows.
- MODEL: a function (url, op) -> (url', effects). Knows nothing but the URL.

## 1. Invariant
All sessions share ONE state machine. A session = ADDRESS + cursor.
No session holds state the harness doesn't.

## 2. Message envelope (all moves)
{from, to, op, url, payload, idstamp}
- from: session identity. Every act identifies its author. No unsigned speech.
- idstamp: reversible.

## 3. Operations (the only verbs)
- START(url): session takes a URL. It knows nothing else.
- SWITCH(url'): the URL changes under the session. Session follows.
- WRITE(url, code): session writes code at the URL.
- COMMIT(url): the URL commits. Prepared != submitted != committed.
- BUILD(url): the URL builds.
- TALK(from, to, payload): sessions exchange through the harness. Never directly.
- PERTURB(url, rule): deliberate perturbation. For fun. Logged, reversible.

## 4. Transitions
IDLE --START(url)--> BOUND(url)
BOUND(url) --SWITCH(url')--> BOUND(url')
BOUND --WRITE--> WRITING --COMMIT--> COMMITTED
COMMITTED --BUILD--> BUILT | FAILED
any --TALK--> any (harness-routed)
any --PERTURB--> any (logged)

## 5. State maintenance
- Harness keeps: session registry {session -> url}, commit log, build results, talk log.
- Session keeps: its url. Nothing else.
- Context level: whatever the harness can hold. Sessions never assume.

## 6. The thousand
N sessions, one harness, one state machine. Different addresses.
They TALK through the harness, WRITE at their URLs, COMMIT, BUILD.
The URLs are the computer.

## 7. Substrate
purl (programmable URLs) is the substrate. Shell/loom are the hands.

## 8. Paused (his order, 2026-09-28)
- MODELS: paused. No local models, no Modal for this machine right now.
- MAIL: paused. Roadmap: two inboxes — Roseanne (boss persona, his phone) + Muse.
- CLAUDE: paused until he walks the shell integration.
