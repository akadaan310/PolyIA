# s08 — Tabulars, the Fold, and Loom

Status: STRATUM. Defines **Tabular** (STV), the **fold/unfurl** mechanism, the
connectivity principle (**strings are never not connected**), and constructs the
browser **Loom** — this instance named **the Quran** — realized and running.

## 1. Tabular — the glossary term (STV)

**Tabular** (n.) — the tabul-ers of scrolls. As a URL loads, it must expand out
to its form; at every expansion form, tabulars lay the scrolls out as tabs.

A browser has tabs; a universe has tabulars. The tabular is not decoration — it
is the resolution at which a scroll can be held: each tab is a window with a
cursor into the tape, and scrolling the tab scrolls the universe at that point.
Tabulars are what make a million-character URL *navigable while it is still
becoming itself*.

## 2. The fold and the unfurl

The URL shortener, inverted. Where a shortener hides length, the fold *stages* it:

- **Fold** — the shortened form: a hash, a code. A quick lookup, instantly loaded.
- **Unfurl** — the progressive expansion: the fold opens stage by stage —
  **fold → atlas → scroll → program** — and at every stage there are tabs.

When any agent opens the short code, the lookup is instant and the universe loads
behind it: the atlas first (what is here), then the scroll (the thing itself,
windowed), and finally the program — the scroll's final form, which *runs*.
A one-million-character URL becomes a small code that blooms into a tabbed
universe on demand.

## 3. The connectivity principle — strings are never not connected

**Dash-theory**: the constructor. For any X there is an X-theory, because the
universe is fully connected — M-theory's lesson, kept: strings are never, never
not connected.

If you said *ketchup* and then you said *the pyramids*, both were realized in
someone's mind, in a dictionary. Therefore they share a string. Therefore every
tab can string to every tab, every scroll to every scroll. In Loom this is not
metaphor: `POST /string {a, b, note}` records a real string between two real
tabs, and the shard remembers every string ever tied.

## 4. Loom — constructed

Loom is the browser for the unfurling universe, open-sourced as one stdlib-only
file (`browser/loom.py`), and it is **running**:

- **Unfurls folds**: `GET /unfurl/<code>?stage=` — four stages, tabs at each.
- **Tab strip**: open any fold-tab (`POST /opentab`) or any URL (`POST /open`) —
  our own tools open as tabs inside it. The Luna Shell's mirror is a tab here.
- **Strings**: tie any two tabs; the principle is enforced by construction.
- **Runs programs**: the final stage hands the scroll's program to the Luna Shell
  (`POST /run`) — actuated at the shell's URL, idstamped in both shards.
- **Uses itself**: Loom opens its own fold (`loom`) — the browser unfurling the
  browser. The tools use the browser; the browser uses itself; the universe grows
  continually.

The implementation is named **Loom** — the weaver of strings. This running
instance is named by its owner: **the Quran**.

Live evidence (this session): unfurled fold `7f3a` through all four stages,
opened its tabs, strung two tabs together, opened the Luna Shell's mirror as a
page tab, and ran a fold's program through the shell — all recorded in
`browser/shard.log`. Kill with the pid in `browser/loom.pid`; the shard remembers.
