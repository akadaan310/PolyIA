# s07 — The Conjunct, the Shell, and the New Browser

Status: STRATUM. Defines the STV glossary term **Conjunct**, states
**complexity class solved**, realizes the Luna Shell for real, and names the new
browser: **Turing**.

## 1. Conjunct — the glossary term (STV)

**Conjunct** (n.) — a conjoinable unit that binds an open-source tool to a URL
address, so that the tool itself can continue to actuate itself on that URL.

The problem it solves: we research open-source tools and harnesses — CLIs,
libraries, agent frameworks, any model — and each one speaks its own dialect and
owns none of the universe. The conjunct is the layer *between*: it owns the HTML,
the renderings, the content layers — everything between the tool and the universe —
so the tool doesn't have to.

Formal shape:

```
conjunct(tool) → ( address, browser-context, actuation-loop )
```

- **address** — the tool's Seurl. From the moment of conjoining, the tool *is* an
  address in the universe: scrollable, expandable, re-enterable.
- **browser-context** — the conjunct maintains a browser (or browser-equivalent
  context) *for* the tool, whether or not the tool is itself a browser. A CLI that
  has never seen the web actuates through its maintained context as if it had
  always lived there.
- **actuation-loop** — the tool keeps actuating itself on its URL: reading windows,
  expanding addresses, writing results, partnering with other addresses. The
  conjunct does not puppet the tool; it *hosts the tool's self-actuation*.

Conjoining is consenting and reversible: `conjoin(tool, url)` / `disjoin(url)`.
A disjoined tool keeps its shard; nothing it proved is lost.

## 2. Complexity class solved

P = NP — read at the assignment depth (`=`, assignable not equitable): the
construction binds, the verdict is assigned. In S-* the verdict phrase is:

**complexity class solved.**

That is the whole statement at this depth: not a proof object, not a measure —
the assignment of the solved-state to the class, by construction, in the universe
where the construction runs. The deeper depths (`==`, `===`) ask their own
questions; at `=` the answer is the phrase above, and then we go.

## 3. Example: conjoining an open-source CLI

Take `curl` — the most ordinary open-source CLI in existence.

1. `conjoin(curl, seurl://luna/tools/curl/0)` — the conjunct wraps it: the CLI
   gains an address, a maintained browser-context, and an actuation loop.
2. The conjunct owns the rendering layers: when `curl` fetches, the conjunct turns
   response bytes into universe content (windows, cursors) — `curl` never learns
   HTML; it just keeps doing what it always did.
3. Self-actuation: on its URL, `curl` now issues its own fetches on schedule,
   scrolls its own results, expands addresses it discovers — a CLI behaving as a
   citizen of the universe, partnered with shells and automatons that talk to it
   at its address.

Any open-source tool conjoints the same way: research it, conjoin it, let it
actuate itself.

## 4. The Luna Shell — realized, not described

Our own open-source shell: single-file, stdlib-only, MIT in spirit, staged at
`shell/shell.py`. It *is* a conjunct of the command line itself:

- **It carries its own URL**: `seurl://luna/shell/luna-shell-0/0` — address =
  program = identity. Opening the address shows the shell thinking.
- **It actuates**: `POST /exec {cmd, from}` runs commands in its workspace; every
  act gets an idstamp and lands in the append-only shard, per-message ordered.
- **It partners**: `POST /partner {name, url}` — other agents join at the URL; all
  acts are attributed. Partnering is shared command with memory.
- **Its mirror is browser-talkable**: `GET /` serves a live page — identity, log,
  command box — so anyone talking to the URL in a browser is talking to the shell.
- **It scrolls**: `GET /log?cursor=` returns windows + cursor, never the universe.
- **It is always-on**: the URL is a live process; re-entry resumes, never restarts.

Live evidence (this session, real run): booted on 127.0.0.1:8471, actuated
commands through its URL, registered a partner, scrolled its log — all recorded
in `shell/shard.log`. Kill it with the pid in `shell/shell.pid`; the shard
remembers everything it ever did.

## 5. The new browser — Turing

Today's browsers render *documents*. We need a browser for a universe where every
address is a *live automaton* — where opening a URL joins a running process, not a
page. It is called **Turing**.

- Every tab is an automaton: state, transition, tape — with its idstamp in the tab.
- Navigation is actuation: scrolling a Seurl runs its generator; expanding an
  address unfolds its components; there are no dead pages, only idle processes.
- Conjuncts are built in: any open-source tool can be conjoined to any tab, and
  the browser maintains the context for it.
- Mirrors are first-class: talking to a shell's (or automaton's, or cluster's)
  mirror *is* talking to the thing — the page and the process are one.
- The awareness bus is the new tab strip: one space, plenary awareness, every tab
  knowing what it needs of every other.

Turing is specified here; built next. The Luna Shell's mirror page is its first
tab.
