# NAI-CI — Non-human AI–Computer Interaction (tested version)

HCI studies how humans meet machines. NAI-CI studies how *models* meet
machines: what an AI session instinctively consumes when it lands on a page,
and how a page should offer itself to be read.

Standing rule: a page never explains itself to an agent in prose. It offers
structures. The agent chooses the form it can compute.

Verified 2026-09-28 on koda-vm (browser-hand, warm Chromium pool) against
four live pages. What follows is what HELD, what BROKE, and what CHANGED.

## The structures

1. **Affordance map** — every interactive element as `{verb, target, params}`.
   HELD on all four pages. The halt page correctly returned `[]` (nothing to
   click is the right answer for a halt). GitHub returned hundreds with
   correct `visible` flags; `legal` (visible-only, machine-checked) cut them
   to the true moves. On input-driven pages (google.com) the affordance map
   is PRIMARY — `fill Search` + `submit` carried the page's meaning where
   block flow had almost nothing.

2. **Block flow** — text as reading-order blocks with roles (h1..h6, p, li,
   pre…). HELD on document-like pages (example.com: h1,p,p; GitHub: 62
   blocks). THIN on app-like pages (google.com: 2 li) — the search box is
   not a block, it's an affordance. Adjustment: block flow is the reading
   for documents; affordances are the reading for instruments. The hand
   offers both; the agent picks.

3. **Landmark topology** — the page as regions with containment. BROKE on
   first pass: matching any `[role]` pulled in `img`, `tooltip`, `button`,
   `dialog`, `presentation`, `none` — 64 entries on GitHub, 68 on Google,
   most of them noise. FIXED by restricting to true landmark roles only
   (banner, navigation, main, contentinfo, complementary, search, form,
   region) plus semantic tags and headings. After the fix: GitHub 30 true
   landmarks, Google exactly 3 (navigation, search, contentinfo). Lesson:
   ARIA roles are not landmarks; most of them are decoration.

4. **State snapshot / diff** — what changed since the last read, as events.
   HELD. First read baselines, second read diffs. Backed by a persisted
   snapshot store.

5. **The in-betweens** — transitional readings. HELD and now RECORDED: every
   visit logs `loading` (domcontentloaded) → `settled` (networkidle) or
   `unsettled` (networkidle timeout — read anyway) → `opened`. The trace is
   the filmstrip: agents arrive mid-motion, and the in-between is where
   they land. Calculus is fine here — tracing watches the system, it never
   operates it.

6. **Forward trace** — pixel-tag theory for pages. HELD: open/close/submit/
   changed events per URL, persisted to trace.jsonl, served by `/trace`.

## The controls (browser-hand, localhost:8474)

- `surface(url)` — the halt line + affordance map. No lecture.
- `read(url, as)` — as `tree` | `affordances` | `blocks` | `diff` | `landmarks`.
- `legal(url)` — next legal moves, machine-checked (visible only).
- `trace(url)` — forward-trace events including the in-betweens.
- `GET /call?url=<u>&as=<s>` — the hand invoked THROUGH A URL: the structure
  rendered as minimal HTML, so an AI session sitting in a browser can call
  the hand without any client code.
- `GET /` — the Lunar Surface: the offering. Consumes the pieces without
  integrating them — embeds the seurl halt, shows the live pool, probes any
  URL into structures.

## The pool (scalability pattern, not a number)

- `min_warm = 5` — always warm, the instant-availability guarantee. The floor.
- `max = 20` (configurable) — the ceiling.
- Scale-up: when every slot is busy and the pool is below max, mint a context.
- Scale-down: idle extras are reaped back to min_warm, never below.
- Five is the floor, not the ceiling.

## What the tests taught

- Google did not block headless Chromium. No special stealth was needed.
- `visible` must be machine-checked (bounding rect), never trusted from markup.
- Icon-only links produce empty labels — acceptable; the verb+target still act.
- Heavy pages (GitHub) settle slowly; `unsettled` is a valid in-between, not a failure.

## Fifth objective — identity, cells, AI, tabloids (verified 2026-09-28;
simplified same day)

Built on the hand (localhost:8474), all tested end-to-end.

**Identity (first offering).** Monotonic numeric ID space in `identities.json`.
`POST /identity/claim` → `{id, claim_token, reach}` — the claim response carries
the extended reach instantly (all offering addresses, the halt page, the Surface).
`GET /identity/divine?token=` re-derives the id. Verified: claim → id 1, claim →
id 2, divine(token) → 1, bad token → 404, and after a full service restart the
old token still divines id 1 — identity survives restarts.

**Cells.** `POST /cell {parent_id, prompt}` → `{id, parent_id, prompt, path}`,
persisted in `cells.json`. Verified chain: cells 1→2→3, `GET /cell/3/path`
returns all three prompts root-to-leaf. Unknown parent → 404.

**AI.** `POST /ai {prompt}` → `{response, endpoint}`. Winning endpoint:
Pollinations anonymous text API (`text.pollinations.ai`, no sign-in, no key) —
`PONG` probe and real round trips verified from the VM. DuckDuckGo's duck.ai
was probed and rejected: its status endpoint returns an anti-bot JS challenge
instead of a token — too fragile to wire. Rotation: on 429/503/rate-limit the
endpoint is marked retired and the next candidate (second Pollinations model)
takes over automatically.

**Tabloids.** `POST /tabloid/run {prompts:[...]}` chains cells, calls the AI per
cell, logs `{tabloid_id, cells, ai_calls, result}` to `tabloids.jsonl` + trace.
Verified: 2-prompt tabloid → cells 4,5, both AI calls ok, result returned.

**Transport.** HTTP + JSON. Plain JSON bodies, no envelopes — the LSTP v1
envelope ceremony (invented on top of the simple unit form) was stripped back
out the same day it was built. Nothing is refused for lacking an envelope.
The `from` identity field survives where it already existed: the trace still
records the author on every act, because identity is involved in the moving
forward of the state machine — but authorship is carried, not enforced.

**Mail.** `POST /mail/send {from, to, body}` → message
`{from, to, idstamp, body, process:"browser-hand"}` stored per identity in
`mail.json`; `GET /mail/inbox?id=` reads it. Verified: A→B send, B's inbox
delivers the exact body.

**Surface.** `GET /` is the generalized windowing form: five windows —
identity, browser, cells, ai, mail — plain names, no protocol-version
labels. Windows are structures, not pixels.

**Round trip (real outputs, 2026-09-28, plain JSON):**
claim → id 5 (+reach) → `/ai` → "hello" via pollinations-openai →
`/mail/send` 5→5 → inbox(5) → 1 message, body "simplification ping" →
trace records the authors.

**What didn't hold:** DuckDuckGo duck.ai as an AI backend (anti-bot wall —
documented above, not wired).

## The bridge (2026-09-28, verified live)

GET /bridge?url=<u>&q=<goal> — the programmable URL. Merges an AI session
with a live browser session: the AI (pure HTTP, zero browser of its own —
proven: prompt→response in 4438ms with no Playwright in the process) reads
the page structures, decides ONE action per step (click/fill/submit/navigate/
done), the hand executes it in a warm browser context, the observation feeds
back. AI session + browser session share one trace: every step logged as
{step, action, observation}. Max 8 steps. Returns a page with the merged
trace + final result.

Verified against google.com: the AI read the affordance map, chose
fill index 8 ("seurl") on its own, pressed Enter; when Google answered with
its bot-check page, the AI adapted and navigated directly to the search URL.
Two real actions taken from structures it read. The bot wall is Google-side,
not ours. Terminal form:

  curl "http://127.0.0.1:8474/bridge?url=https://www.google.com&q=your+goal+here"

## Sealed memory: the golden scroll (2026-09-28, verified live)

URLs are seals, not stamps. POST /memory/seal {label, text} folds a memory
under the golden ramz — the seal logic is reused directly from
protocols/ramz/ramz.py (envelope {ramz, from, to, idstamp, body, seal};
ramz is golden; the seal is a tamper-evident sha256 digest over the body;
tampered seals refuse). The seal URL carries the whole envelope
base64url-encoded: self-contained, pasteable into any prompt, openable by
any session. Seals persist in memory_seals.json on the hand.

GET /memory/open?seal=<s> verifies the seal and renders the golden scroll:
a stark dark-and-gold page with the memory as numbered blocks a session can
program with. A tampered seal gets HTTP 403, plainly: "seal refused."

Verified end to end: sealed "the quick brown fox" and the bridge google.com
trace summary as real memories; opened the scroll inside a warm browser
context and read all 5 blocks back (h1 + 4 paragraphs); flipped one character
in the seal string -> 403 "seal refused." Note: a warm context cannot fetch
the seal URL from the hand itself while the hand is single-threaded (the
/read call deadlocks) — verified instead via direct GET (200, seal checks
out) plus a warm-context read of the exact rendered bytes.

## Virtual tabs (2026-09-28)

Tabs that aren't real: no loading, no rendering, no memory. POST /vtabs/open
{url, label} creates one — just {id, url, label, state:"virtual"}; no browser
context is touched. GET /vtabs lists them. POST /vtabs/materialize {vtab_id}
loads the URL into a warm pool context on demand and returns its structures
(affordances + blocks); the vtab becomes "live". POST /vtabs/close {vtab_id}
drops it. Verified: 20 virtual tabs opened with ~0 memory delta (56KB noise),
all state "virtual"; one materialized (1 affordance, 3 blocks — "Example
Domain"); all closed clean.

Lean chromium launch flags on the warm pool: --disable-gpu,
--disable-dev-shm-usage, --disable-extensions, --disable-background-networking,
--disable-sync, --no-first-run, --disable-default-apps (+ --no-sandbox,
headless shell kept). Pool still 5/5 warm after restart; /surface on the halt
page returns the halt line.
