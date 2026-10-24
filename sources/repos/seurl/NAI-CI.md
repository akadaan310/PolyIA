# NAI-CI — Non-human AI–Computer Interaction

HCI studies how humans meet machines: usability psychology, haptics, comfort,
behavior. NAI-CI studies how *models* meet machines: what an AI session
instinctively consumes when it lands on a page, and how a page should offer
itself to be read.

The human reads a page as a surface. The agent should read a page as a set of
computable structures — the same page, repassed into different forms.

## Page-reading structures

1. **Affordance map** — every interactive element as `{verb, target, params}`:
   links, buttons, forms, inputs. This is the state-machine reading: it answers
   "what's next?" with the legal moves, nothing else.

2. **Block flow** — text as reading-order blocks with roles: halt, body, code,
   form. The page as a script to be performed, not a document to be skimmed.

3. **Landmark topology** — the page as regions with containment: nav, main,
   halt, tray. A formation the agent can navigate without seeing.

4. **State snapshot / diff** — what changed since the last read, delivered as
   events. The forward-trace reading: open, close, submit, move — pixel-tag
   theory for pages. Calculus is fine here; tracing doesn't operate the system,
   it watches it.

5. **The in-betweens** — transitional readings: loading→loaded, halt→move,
   form→submitted. The page as a filmstrip of states, never a still. Agents
   arrive mid-motion; the in-between is where they land.

## Controls of a Luna-aware browser

The browser is aware of Luna. When an agent lands on a URL, it is not talked
to — it is surfaced to: *"oh, you're here. here we go."*

- `surface(url)` — open and surface: the halt plus the affordance map. No lecture.
- `read(url, as)` — read the page as `tree` | `affordances` | `blocks` | `diff`.
- `legal(url)` — the next legal moves, machine-checked against the page.
- `trace(url)` — forward-trace events for the session, open to close.

## Standing rule

A page never explains itself to an agent in prose. It offers structures.
The agent chooses the form it can compute.
