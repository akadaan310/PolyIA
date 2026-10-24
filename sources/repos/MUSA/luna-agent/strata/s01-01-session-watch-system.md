# 01 — Session-Watch System (LUNA-WATCH)

Status: DESIGN DOC. Not built. Placement: operator's host VM (portable systemd units; operator places infra).

## 1. Purpose

Always-on observation + command-routing across the operator's AI accounts. This is not a
dashboard — it is an agentic surface: the watcher witnesses every message in every watched
session and acts instantly on witnessed commands.

## 2. Watched surfaces (7 contexts)

| Context    | Account            | Auth        |
|------------|--------------------|-------------|
| chatgpt-a  | ChatGPT account 1  | operator login, persistent context |
| chatgpt-b  | ChatGPT account 2  | operator login, persistent context |
| claude-a   | Claude account 1   | operator login, persistent context |
| claude-b   | Claude account 2   | operator login, persistent context |
| gemini-a   | Gemini account 1   | operator login, persistent context |
| gemini-b   | Gemini account 2   | operator login, persistent context |
| google-ai  | Google AI Mode     | no sign-in |

Each context = one isolated persistent browser context (Playwright/Chromium). One operator
login per context, performed once by the operator; the watcher then runs unattended.

Why not iframes: chatgpt.com, claude.ai, gemini.google.com, and google.com all send
`X-Frame-Options: DENY` (or equivalent CSP). Framing them yields blank boxes. Persistent
contexts are the honest mechanism.

## 3. Observation semantics

- Poll each account's conversation list, then each conversation's message stream.
  Backend APIs where stable; DOM fallback where not. Polling stays gentle (bot-detection risk).
- **Both directions are witnessed**: operator messages AND model messages are events.
- Every witnessed message appends one event:
  `{ctx, account, session_id, msg_id, role, ts, text_hash, text_ref}`
- Full text archived per message (see §5). Nothing is summarized away at capture time;
  interpretation happens later, on the archive.

## 4. The IHAVECONTROLS trigger

- Trigger token: `IHAVECONTROLS` — all caps, no spaces — matched against any witnessed
  message in any context, from either direction.
- On witness: that thread is immediately marked **CONTROL PANEL** (a state flag on the
  session record, with provenance: who/when/where witnessed).
- The watcher then issues a **scrollable control URL** into that thread (see doc 03) —
  the operator's controlling power: *cascading constitutionally-oriented computational
  prompting*.
- Control-panel marking is itself a recorded event. Marking ≠ granting: the control URL
  carries its own capability envelope (doc 03 §4).

## 5. Archive layout (computational directory)

```
luna-agent/
  CONSTITUTION.md            # doc 02 root contract (versioned, content-addressed)
  COMPUTATION.md             # doc 03 API ways (how URLs/operations compose)
  ACCOUNTS/
    chatgpt-a/
      meta.json
      SESSIONS/
        <session-id>/
          meta.json          # title, share_url, created, updated, control_panel flag
          messages/
            0001-user.md / 0001-user.json
            0002-model.md / 0002-model.json
            ...
    chatgpt-b/ ... (same)
    claude-a/ claude-b/ gemini-a/ gemini-b/ ... (same)
```

- Per-message breakdown preserves perfect flow order (sequence numbers, not just timestamps).
- Share URLs kept per session: any session is one click away; the browser can open the
  share directly when the operator wants the live thread.
- `.json` sidecars carry ids/hashes/provenance; `.md` carries the text for agent reading.

## 6. Command router

User-definable registry (`commands.yaml`): trigger → action → effect policy.
Seed commands:

- `send-to-claude-new-session` — open a fresh Claude chat, paste the payload.
  Effect policy: prepare-only by default (operator submits), auto-submit only if declared.
- `open-google` — run the query through Google AI Mode (google-ai context), return the
  answer to the origin thread + the log.
- `export-session` / `share-session` — archive on demand / mint a share link on demand.
- `recall` — fetch any archived message back into the current thread.

The router matches triggers in witnessed messages (operator OR model), executes instantly,
and records a result event. **Prepared ≠ submitted**: the watcher never sends as the
operator unless the command's declared effect policy allows it.

## 7. Never-dies harness

- One systemd unit per component (`luna-watch`, `luna-router`, `luna-archiver`):
  `Restart=always`, `RestartSec=5`.
- Heartbeat file touched every 30s; a watchdog cron checks staleness and restarts.
- All state on persistent disk; resume = replay the event log from the last checkpoint.
- No single point of silent death: the watchdog watches the watcher.

## 8. Result routing

Command results return to the **origin thread** (as a watcher message, clearly attributed
as the watcher — never impersonating the operator) and to the append-only log. The log
is the ground truth; threads are views.
