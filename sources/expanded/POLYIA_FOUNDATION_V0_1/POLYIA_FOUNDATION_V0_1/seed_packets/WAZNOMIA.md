# WAZNOMIA — الوزنوميا

## A Computational Header: The Science of Functional Nomenclature Determination

*Header document. The science is stated here in general form; its determinations are
worked on the nomenclature of mathematics, chemistry, and computation.*

---

### The claim

A scientific name is not a label. It is a **computation that has been frozen into a word**.

Every technical term in the three rooted languages of science — Arabic, Greek, and Latin —
was *derived*: a root carrying a core event, passed through an operator that reshaped its
function, and fixed as a noun that a science could build on. Because the derivation was
mechanical, it is **reversible**. Given the name, the function can be recovered. Given the
function, candidate names can be derived. This bidirectionality is the science:

- **Nomenclature determination** — from a name, recover its root, its operator, and the
  *pure function* the name performs, stripped of the domain it happens to serve.
- **Functional determination** — from a pure function, derive the names that the three
  traditions give it or would give it, and measure their agreement.

The science is named from Arabic **وَزْن (wazn)** — one word that already means a
morphological *pattern*, a prosodic *meter*, and a *weight*: the template, the rhythm,
and the measure of a word in a single term. No word in Greek or Latin covers all three.
That fact is the first determination of this document.

### Why Arabic is the keystone

In Greek and Latin, the operator machinery is real but *distributed* — spread across
prefix tables, suffix tables, and paradigm tables that must be carried alongside the word.
In Arabic, the machinery is **interleaved into the word itself**: the root consonants and
the pattern occupy the same letters, simultaneously visible. The computation a name
performs can be read off its surface. Arabic is therefore the **reference
implementation** of the rooted-language architecture: the determination key against
which the other two systems are calibrated.

---

## 1. The Arabic representation

Arabic's classical sciences are five running machines, each already a computational
representation:

**الصرف — morphology as transducers.** A finite inventory of patterns (الأوزان) acts on a
finite space of roots. Each pattern is a function with a semantic delta:

| Pattern | Machine action | Delta |
|---|---|---|
| II فعّل | doubling the middle radical | intensify / make-causative |
| III فاعل | engaging a counterpart | mutual action, sustained attempt |
| IV أفعل | prefixing the causative hamza | push the event onto an object |
| V تفعّل | reflexive of II | gradual self-becoming |
| VI تفاعل | reciprocal of III | symmetry, mutual relation, sharing |
| VII انفعل | inchoative prefix | undergo, be entered into the state |
| VIII افتعل | reflexive with effort | do for oneself, draw off with striving |
| X استفعل | seeking prefix | request the act, deem something so |

The inventory — verb forms, participles, verbal nouns, and their sisters, forty and more —
is *closed and enumerable*. That is what makes Arabic morphology a machine and not a habit.

**النحو — syntax as an operator algebra.** The عوامل (governors) are operators that bind
dependents and determine their case-endings; الإعراب is a type system written on the ends
of words. Computational form: a dependency grammar with typed, governed edges.

**العروض — prosody as a regular language.** Meters are sequences over a small alphabet of
prosodic units (أسباب، أوتاد، فواصل) composed into feet (تفعيلات), composed into بحور.
Al-Khalil's five circles *generate* the meter space by rotation — a cyclic combinatorial
generator. The زحافات and علل are licensed rewrite rules over the pattern strings.
Scansion is parsing; meter identification is language recognition.

**البلاغة — rhetoric as an operation library.** البديع is string and phonetic operations
(الجناس: permutation and edit classes; السجع: terminal-rhyme constraint; الطباق: antonym
pairing — a negation edge). البيان is mapping operations: التشبيه is a four-place relation
(mapped, mapped-to, instrument, ground); الاستعارة is cross-domain transfer with the
source suppressed. المعاني, crowned by al-Jurjani's نظم, is compositionality: meaning
computed from grammatical relations, not from word lists.

**المعاجم — lexicography as root-keyed indexing.** The classical dictionaries are hash
structures keyed by root: address first, definitions after.

## 2. Determinations — the Arabic key at work

*Basic mathematics.* **كسر** (fraction) is the masdar of كسر — *a breaking*. **معادلة**
(equation) is Form III of عدل — *a balancing between two sides*: the mutual pattern for a
mutual act. **جذر** (root, of a number and of a word) is one word in both sciences.
**أوّلي** (prime) is *the first ones*.

*Advanced mathematics.* **تشاكل** (isomorphism) is Form VI of شكل — *mutual form*.
**تكامل** (the integral) is Form VI of كمل — *mutual completion*. **تماثل** (symmetry) is
Form VI of مثل — *mutual likeness*. One law falls out of the table unforced: **wherever
the concept is relational, Arabic reaches for Form VI.** تفاعل is the relational operator
of its nomenclature. **اشتقاق** (derivation) is the Form VIII verbal noun of شقّ — *a
drawing-off by effort*. **دالّة** (function) is the participle of دلّ — *the indicator*:
a function is that which points from input to output. **الجبر** (algebra) is *restoration*
— the setting of what was broken, which is why the science of equations carries a
bone-setter's name into every language on earth, Arabic's gift traveling under its own word.

*Basic chemistry.* **جُزَيء** (molecule) is the diminutive of جزء — *a little part*.
**حَمْض** (acid) names the sour taste — a property, directly. **عنصر** (element) is a
gathering-root word: the constituent stock.

*Advanced chemistry.* A **covalent** bond in Arabic is **رابطة تساهمية** — the bond of
*mutual sharing*, Form VI again: two atoms sharing, named by the reciprocal pattern.
**محفِّز** (catalyst) is the Form II participle of حفز — *the inciter, the one who urges
on*: the intensive pattern for the agent that drives a reaction without being consumed.
**التشكّل** (conformation) is Form V of شكل — *gradual self-forming*: the molecule
settling among its arrangements, named as a becoming.

*Basic computation.* **متغيِّر** (variable) is the Form V participle of غيّر — *that which
keeps changing itself*, reflexive pattern for a reflexive thing. **حلقة** (loop) is a ring.
**مصفوفة** (array, matrix) is the passive participle of صفّ — *rows set in ranks*.

*Advanced computation.* The compiler in Arabic is **المُصَرِّف** — *the Ṣarf-machine
itself*: that which conjugates a source text through its forms, named after morphology
outright. **تزامن** (concurrency) is Form VI of زمن — *mutual timing*, the reciprocal
pattern for processes that must share time. **العودية** (recursion) names *the returning*.
**بصمة** (hash, in modern usage: بصمة رقمية) is *a fingerprint* — identity by impression.

## 3. The Greek representation, on its own terms

Greek does not interleave. Greek **composes**: a stem carries the core, and a closed
machinery of prefixes and suffixes — its own operator inventory — binds before and after.

- **στοιχεῖον (stoikheion)** means both *a letter of the alphabet* and *an element of
  nature* — one word: the corpus line and the constituent of matter. Greek begins the
  science of names by identifying the minimal unit of writing with the minimal unit of
  the world.
- **The suffix operators.** Greek carries its أوزان-analogue at the word's end:
  **-σις** (*-sis*) makes the *process* (analysis, synthesis, crisis);
  **-μα** (*-ma*) makes the *result* (theorem — the thing beheld; problem — the thing
  thrown forward; system — the thing set standing);
  **-τήρ / -τωρ** makes the *agent*; **-τρον** makes the *instrument* (θερμόμετρον,
  the heat-measurer); **-ικός** makes *pertaining-to* — the adjective operator,
  whence the names of whole sciences.
- **The prefix operators.** σύν- (together), ἀντί- (against), ἀνά- (up, back),
  κατά- (down), ὑπέρ- (over), ὑπό- (under), μετά- (across, after), πρό- (before,
  forward). A Greek compound is a *composed function*: τηλε-σκόπος — *far-watcher*;
  μικρο-σκόπος — *small-watcher*. The instrument names of science are Greek
  compositions, each one legible: say what it does, in pieces, and the name assembles.
- **Aspect.** The Greek verb stem itself carries temporal operators — present stem,
  aorist stem, perfect stem — duration, event, and completed-state encoded in the stem,
  a pattern-system inside the verb.

Determinations from Greek: **θεώρημα** (theorem) — *a thing beheld*; **σύστημα**
(system) — *a standing-together*; **κρίσις** (crisis) — *a separating, a deciding*;
**μέθοδος** (method) — *the way after, the way along*; **ἄτομος** (atom) — *the
uncuttable*, a privative operator (ἀ-, *not*) bound to a cutting root (τέμνειν, *to
cut*): the atom is defined by a forbidden operation. **τόπος + λόγος** (topology) —
*place + account*: the account of place, named by its subject and its activity.

## 4. The Latin representation, on its own terms

Latin does not interleave either. Latin **orbits**: a verbal root at the center, prefix
operators fixing its direction, suffix operators fixing its role, and around the whole
system the declension and conjugation tables — complete paradigm grids in which every
cell is a state and every state has a form.

- **The prefix operators are spatial logic.** In *portāre* — *to carry* — one root
  serves a family determined entirely by its bound operator: **im**-port (carry in),
  **ex**-port (carry out), **trans**-port (carry across), **sup**-port (carry from
  beneath), **re**-port (carry back), **de**-port (carry away). The prefix is an
  operator over trajectories; the root supplies the act.
- **The suffix operators.** **-tio / -sio** makes the *process* (computatio,
  functio); **-tor** makes the *agent* (calculator, generator); **-tura / -tus**
  makes the *result and state* (structura — the built thing, as a condition).
  These are Latin's pattern-operators, corresponding function for function to
  Greek -sis / -tēr and Arabic's فاعل / فعالة / مصدر machinery.
- **The tables.** Five declensions, four conjugations: finite, complete, enumerable.
  Latin's grammar is a set of state tables so regular that its teaching tradition
  could print the entire language as grids — a closed system, and therefore fully
  computable.

Determinations from Latin: **computāre** — *com-* (together) + *putāre* (to reckon,
originally to prune): computation is *a reckoning-together*. **Integer** — *in-* (not)
+ *tangere* (to touch): the integer is *the untouched, the whole*. **Fractio** —
from *frangere*, *to break*: the fraction is a breaking — Latin and Arabic كسر
agree exactly, two traditions, one determination. **Radix** — *root*; the √ sign is
its letter, and the mathematical *radical* is the root-word wearing a suffix.
**Calculus** — *a little pebble*: the counting token, matter before abstraction.
**Digit** — *digitus*, the finger: counting on the hand, preserved in every digital
machine. **Data** — *the given things*, neuter participles, handed over as-is.
**Structūra** — from *struere*, to build in layers: structure is building, frozen
by -tura into a state.

## 5. Comparative determinations — where the traditions split

The science's sharpest instrument is disagreement. One referent, three determinations:

| Referent | Arabic | Greek | Latin | What the split shows |
|---|---|---|---|---|
| Atom | ذرّة — *a mote, a mote of dust in light* | ἄτομος — *the uncuttable* | (via Greek) | Arabic names it by **smallness**; Greek by a **forbidden operation** |
| Fraction | كسر — *a breaking* | κλάσμα — *a broken piece* | fractio — *a breaking* | All three: **breaking**. The determination is stable across traditions |
| Covalent bond | رابطة تساهمية — *mutual sharing* (VI) | — | con-valentia — *strength together* | The reciprocal function surfaces in both machineries — Arabic pattern, Latin prefix |
| Catalyst | محفّز — *the inciter* (II) | κατάλυσις — *a loosening down* | — | Arabic names the **urging**; Greek the **loosening**. Two functions, one substance: the frontier of the concept |
| Recursion | العودية — *the returning* | — | re-cursus — *a running back* | **Return**, agreed twice independently |
| Compiler | المُصَرِّف — *the conjugator* | — | compilator — *the one who heaps together* | Arabic names the **morphology**; Latin the **gathering** |
| Matrix | مصفوفة — *rows in ranks* | — | matrix — *the mother, the womb* | Arabic names the **arrangement**; Latin the **source** |

Where the three agree, the determination is bedrock. Where they split, the concept
itself has more than one pure function — and the split is a map of the frontier,
legible only because all three systems are determinate.

## 6. The common grammar of the three

Measured across Arabic, Greek, and Latin, the shared architecture has seven members:

1. **Root + operator.** Every name is a core event bound by an operator. The three
   differ only in where the operator sits: interleaved (Arabic), composed before and
   after (Greek), orbiting with tables (Latin).
2. **Closed operator inventories.** Each system's operators are finite and enumerable
   — the أوزان, the Greek suffix/prefix machines, the Latin prefix/suffix sets.
   Finitude is what makes determination *decidable*.
3. **Nominalization.** Each system owns operators that freeze events into objects —
   المصدر, -σις / -μα, -tio / -tura. The sciences are built from nominalized verbs;
   this is the universal construction move of technical nomenclature.
4. **The reciprocal.** Each marks mutual action explicitly: تفاعل (VI), σύν- … -σις,
   con- … -tio. Relational concepts receive relational patterns in all three.
5. **Compositionality.** Meaning is computed from structure. Arabic's نظم, Greek's
   σύνταξις, Latin's compositio are one theorem stated by three grammatical
   traditions a world apart.
6. **Bidirectional determination.** In all three, name → function and function → name
   are both mechanical passes. A nomenclature is a *code*, not a custom.
7. **Closure.** All three are finished systems — classical, complete, fully described
   by their own grammarians. Only closed systems can be computed end to end. The
   science exists because its three languages are complete.

## 7. The determination procedure

1. **Parse.** Segment the name into root and operator under each candidate system.
2. **Decompose.** Record the etymons: form, language, gloss, and the operator's delta.
3. **Extract.** State the pure function as a domain-free signature — a verb phrase
   with its arguments: *sharing (mutual, of strength)*; *returning (of a process,
   to its origin)*.
4. **Cross-map.** Derive the same function in the other two systems; measure
   agreement.
5. **Verify by regeneration.** Re-derive the name from the function. If the name
   cannot be regenerated, the determination is wrong or the term is a loan —
   transliterations (الطوبولوجيا) are marked as what they are: names that chose
   travel over derivation.
6. **Grade.** Every determination carries its grade: **established** (attested in the
   tradition's own sources), **inferred** (derived by the procedure, awaiting
   attestation), **proposed** (a new derivation offered by the science).

A determination is a computation. Where the computation is shown, the claim can be
checked; where it cannot be checked, it is not yet part of the science.

---
---
