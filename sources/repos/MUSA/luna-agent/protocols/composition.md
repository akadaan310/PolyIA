# Composition — how to write any program from the simplest forms

Built on ¬ (not theory): the simplest unit. Built for the URL-MACHINE:
the verbs that move units.

## 0. The simplest form
A ¬-unit: one operation, one id, one url. Nothing smaller is a program;
everything larger is composed of these.

## 1. Store — units live in git repos
Individual units of operation are stored as files in git repositories.
The repository layout IS the taxonomy:

- repo / family / unit-id → the unit (its nots, its iss, its code)
- A repo is a namespace of units. Families group units that compose well.
- git is the memory: every unit versioned, every composition committable.

Taxonomy rule: if two units compose, they live near each other. The tree
shows what can become programs.

## 2. Map — programs are mappings
A program is not written; it is mapped. Take stored units, map nots to iss:

PROGRAM = { units: [id...], mapping: { not → is }, entry: id }

The mapping is itself a unit (a ¬-unit whose iss is "a program"). Mappings
compose: a program can fill another program's not.

## 3. Runnable — some units execute
A unit tagged runnable carries hands: shell, loom, browser. The harness
resolves its nots, fetches the code at its url, and runs it. Running is a
verb (BUILD/RUN), not a property — the same unit can be read as data or
run as code, depending on the verb applied.

## 4. Program-URLs — little URLs composed of IDs
A program's address is a URL composed of unit ids:

seurl://program/<mapping-id>?units=<id>,<id>,<id>

Resolving the URL: fetch each unit id, apply the mapping, fill the nots,
run if runnable. The URL *is* the program — copy the URL, you copy the
program; the ids make it content-addressed, so the program can't drift.

## 5. The loop (URL-MACHINE verbs on units)
- WRITE(url, unit): a session writes a ¬-unit at its url.
- COMMIT(url): the unit (or mapping) commits to its repo. Prepared !=
  submitted != committed.
- BUILD(url): the mapping resolves; if runnable, it runs.
- TALK: sessions trade units through the harness — "I have a not, who
  has the is?"
- PERTURB: swap a unit for a confusable twin; the mapping holds or breaks
  visibly. For fun. Logged.

## 6. The thousand sessions, concretely
N sessions, one harness. Each session holds a url. Sessions WRITE ¬-units
into repos, COMMIT them, TALK nots/iss across the harness, and BUILD
program-URLs from composed ids. A thousand browsers writing the smallest
possible programs, mapping them into larger ones, all through urls.

Start: ¬. End: programs. Nothing in between but composition.
