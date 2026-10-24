# 03 — Scrollable Agentic API (IHAVECONTROLS → control panel)

Status: DESIGN DOC. AI-agentic-facing only. No human dashboard.

## 1. The trigger

`IHAVECONTROLS` witnessed in any watched thread → that thread is marked **CONTROL PANEL**
(doc 01 §4) → the watcher issues **one scrollable control URL** into that thread.

From any AI the operator is talking to, in any watched app, those three words (all caps,
no spaces) summon the operator's controlling power: *cascading constitutionally-oriented
computational prompting* — every command below moves as a cascade:
intent → constitutional check → plan → prepared operations → witnessed execution → evidence.

## 2. What a scrollable URL is

A URL that denotes a **cursor over composable computation**, not a page:

- **Windowed** — each access returns a window (items + cursor), never the whole universe.
  The agent scrolls; context never bloats.
- **Addressable components** — every component is its own URL and is individually
  operable. Not versioned-like-releases; versioned-like-addresses.
- **Composable** — sequences and flows are expressed as URL chains; the system maintains
  sequence/flow state so the agent (and the operator) can read where a flow stands.
- **Persistent as Scrolls** — versions stay historically distinguishable, aliases
  resolvable, compositions observable (PURL semantics, doc 02 §3).

The URL is simultaneously runtime, compiler surface, operation registry, testing
environment, and observation surface (constitution §7). No fake dashboard: the URL must
actually represent the state being observed.

## 3. Surface compute

Spinning up power is addressing it:

```
POST .../surface/spin?units=N&profile=P   →  { surfaces: [<url>, <url>, …] }
```

Each surface URL exposes its own sub-URLs, each individually operable:

```
<surface>/exec        — submit a program / operation
<surface>/status      — current state (windowed)
<surface>/logs?cursor=… — scrollable log
<surface>/artifacts   — outputs produced
<surface>/kill        — release the unit
```

- A thousand units = a thousand URLs, composed by chain. Units never merge into an
  undifferentiated pool; addressability is the point.
- Profiles declare honest metrics: vCPU, RAM, wall-time budget, egress policy.
  The operator defines profiles; **agents read the offered capabilities and supply the
  plan** — the API advertises, the agent composes.
- `.../surface/catalog` lists available profiles and surfaces, including no-signup
  research surfaces (see §6).

## 4. Cascading constitutionally-oriented computational prompting

The discipline behind every control-panel command. Each command is a cascade of
addressable stages; each stage is a URL; each transition is recorded:

```
intent → constitutional-check → plan → prepared-ops → execution → evidence
```

Constitutional check means: the command is mapped to clauses (doc 02 §1) before anything
is prepared. Prepared ≠ submitted ≠ committed holds for commands exactly as for scrolls.
The cascade is visible — the operator watches the system grow (constitution §9), failures
included.

## 5. Command grammar (seed)

Commands are composed, not chatted:

```
spin <N> <profile> [for <purpose>]
run <surface-url> <program-ref>
chain <url-1> -> <url-2> -> …
recall <account>/<session>/<msg-seq>     # fetch from the Luna archive
publish <artifact>                        # record → shared log
front <candidate-ref>                     # submit to the Determiner (doc 02 §4)
```

Agents may propose new commands. A proposed command enters the candidate set and is
placed on a frontier front by the Determiner — the grammar itself evolves
constitutionally. Agents can also ask about the constitution in its own constructs
(doc 02 §6, Tier 0).

## 6. No-signup surfaces (research track)

Enumerate no-signup, no-abuse compute/query surfaces (free tiers, anonymous APIs, AI
modes) with honest capability notes: what they offer, what they cost us, how to leave.
Rule: if a surface wants to stop serving, we stop using it — no abuse, full permission
only. The operator-approved list lives at `.../surface/catalog`; anything not listed is
not used.

## 7. Non-goals

- No human dashboard. The control panel is a thread + a URL, not a page of widgets.
- No context dumping. Windows and cursors, never full universes.
- No silent authority rewrites. Every governing change takes the amendment path.
