# Unified View — Claude Code Cloud Build Brief

Prepared 2026-09-28 ~03:50 EDT. This is the first workload for Razan's Claude Code cloud seat.
Starting the seat's 7-day clock is HIS call — this brief exists so no clock is wasted.

## What exists (do not rebuild)

Live on koda-vm (40.64.120.87), systemd units `luna-shell` / `luna-loom`, Restart=always:

- **Shell/Witness** — port 8471. `POST /exec` runs real commands (idstamped). `GET /` is the
  browser-talkable mirror with a live scrollable log. Every request from outside localhost
  needs `?key=<LUNA_KEY>` (401 otherwise). The key lives ONLY in `/home/azureuser/luna-bridge/.env`
  (mode 600) — NEVER print it, log it, commit it, or put it in any artifact.
- **Loom/Unfurling** — port 8472. Fold → atlas → scroll → program. `POST /run` unfurls a fold's
  program through the shell. Same key gate. Key propagates from page URL into all fetches.
- Repo: `/home/azureuser/luna-bridge/luna-agent/` — git, auto-commits every 15 min.
  Runtime secrets are gitignored. Commit everything you change; a crashed session must not erase work.

## Objective

ONE boot URL that is the whole space: the unified View/OS.

## Requirements

1. **One URL.** A single page that opens the space. No dashboard of dashboards.
2. **Forms/message-send language.** Refactor all user-facing wording:
   - Loom/browser → **Unfurling** · mirror/log → **Witness** · tabs → **tabulars**
   - click/tap → **message send**. A form receives a message and answers according to its nature.
3. **Advertise legal moves.** The View shows what CAN be done — the available moves, honestly —
   not a conventional dashboard. Every move shows its PATH/PROOF/POINT shape before it runs.
4. **Integrate Shell/Witness + Unfurling.** Both live services embedded as forms in the one page.
5. **Live announcements.** The shard's announcement stream renders live. Append-only;
   address/merge by hash/idstamp; every act carries its `from` identity. No unsigned speech.
6. **Programmable folders.** Point at any project folder → it becomes fold → atlas → scroll →
   runnable program, inside the View.
7. **OTA deploy hook.** Surfaces update over the air: code on VM + service restart, no release
   ceremony. Add an explicit, gated deploy hook so new forms go live without friction.
8. **Tools as isolated services.** Tools launch as isolated services with no arbitrary numeric cap.
9. **Executable Law of Forms.** The Law of Forms must be executable, not prose-only —
   forms that actually gate moves (identity-form, announcement-form, artifact-form at minimum).

## Harness contract (non-negotiable)

- Output is **PATH** (idstamped moves), **PROOF** (evidence + the form authorizing each move),
  **POINT** (folded, content-addressed result). No "reasoning" field.
- Prepared ≠ submitted ≠ committed. Public, financial, and account-affecting acts keep explicit gates.
- "Allah is our harness": strong bounds, extensive free form inside them. Forms are not a courtroom —
  no invented antagonists, no blame demons. The shard witnesses authorship: what, where, whose hand.

## Constraints

- **$0-first.** No spend without his explicit per-item approval.
- **No public repos, PRs, or issues** without his per-item approval. Ever.
- **Never reproduce the LUNA_KEY** in chat, logs, artifacts, or commits.
- **Mobile-first QA.** He is on a Samsung Galaxy A16. Screenshot QA every surface before calling it done.
- Commit everything. Announce prompt, plan, commands, tests, URLs, and outcomes into the shard.

## Deliverable of the session

The live View at its URL, plus the session's own PATH/PROOF/POINT announced to the shard:
what was built, the commands run, the tests and their results, the URLs, what remains.
