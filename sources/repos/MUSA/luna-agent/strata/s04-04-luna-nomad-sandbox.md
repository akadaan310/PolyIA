# 04 — Luna Nomad: the agnostic Luna sandbox

Status: DESIGN DOC. Name: **Luna Nomad**. The portable runtime for the whole Luna program
(docs 01–03). Agnostic by construction: it can live anywhere, and the death of any one
host is a non-event.

## 1. Agnostic by construction

- **One image, any host.** The sandbox ships as a container image (`luna/nomad`). It runs
  on koda-vm, on the Oracle ARM worker, on a laptop, on a phone terminal — anywhere a
  container runs. No host-specific paths, no host-specific users, no snowflake servers.
- **State is a volume, not a host.** All durable state (event log, archive, checkpoints,
  vault) lives on an external volume. The container is disposable; the volume is the
  system.
- **Config is environment, not files.** Host, ports, profiles, and capability flags
  arrive as environment variables. Same image, different env, different home.
- **Death of a VM = redeploy.** If a host goes down: attach the latest volume snapshot
  (or replay from the last checkpoint) on any other host, run one command
  (`nomad up`), and the system resumes by replaying the event log from its checkpoint.
  Nothing that matters lived on the dead host.
- **Secrets never in the image.** Tokens and logins are operator-supplied at deploy
  time and live only in the volume's vault. The image is publishable; the volume never is.

## 2. What runs inside

One composed unit, four services (doc 01 §7 + doc 03):

```
nomad/
  watcher    — the 7-context observation layer (doc 01)
  router     — command registry + IHAVECONTROLS handling (docs 01, 03)
  archiver   — per-message archive into the Luna tree (doc 01 §5)
  surfaces   — the scrollable API + surface-compute server (doc 03)
```

Each service is independently restartable; the watchdog from doc 01 §7 supervises all four.

## 3. The front-facing View (not a dashboard)

The operator asked for a front-facing view — explicitly not a dashboard. Difference: a
dashboard reports status; **the View advertises what the human counterpart can do** and
offers each move as a one-tap action. Phone-first, one continuous scroll (the interface
itself honors the scrollable motif).

Sections, in order:

1. **Right now** — live windows, not dumps: what each watched context is doing, latest
   witnessed events, control-panel threads flagged. Cursors, not full histories.
2. **Your moves** — the human capability list, each a one-tap action:
   - log in / refresh a watched account (the 7 contexts authenticate in the human's
     hands — takeover or QR; the sandbox never sees passwords, only resulting sessions)
   - approve or decline a *prepared* operation (prepared ≠ submitted — the human is the
     authority path; doc 02 §5)
   - issue `IHAVECONTROLS` into any thread (summons the scrollable control URL)
   - browse the archive: account → session → message, with share links one tap away
   - spin surfaces / run a cascade (doc 03)
   - see the Determiner's current frontier (doc 02 §4): what is frontier, what is backlog
3. **Approvals** — everything waiting on the human, oldest first, each showing its
   constitutional trace (which clauses it was checked against).
4. **Archive** — search across every session and message ever witnessed.

The View never impersonates the human and never acts without the human where the
effect policy says the human decides.

## 4. Account login design

The 7 contexts need the operator's logins. The sandbox never asks for passwords in
chat and never stores them: the View hands the human a login task per context (browser
takeover or QR scan on the phone), the resulting session lands in the vault volume.
Refresh is the same flow, on expiry. This is the one human ritual the system cannot
do for itself, and the design says so openly.

## 5. Android app (explicitly NOT yet)

The operator deferred the Android app. It is not designed here beyond its slot: the
View is already phone-first, so the future app is a thin wrapper — the View plus push
for approvals and `IHAVECONTROLS` witnesses. When the operator says go, the app wraps
what already exists; nothing is rebuilt.

## 6. Failure posture

| Failure | Response |
|---|---|
| Host VM dies | Redeploy image on any host, attach volume snapshot, replay from checkpoint |
| A service crashes | systemd restart + watchdog (doc 01 §7) |
| A watched site changes its DOM/API | Backend-API-first with DOM fallback; watcher degrades to slower polling, never silent |
| Session token expires | View flags the context; human re-logs-in in one tap |
| Volume snapshot stale | Event log is append-only; worst case replays from the last good checkpoint |
