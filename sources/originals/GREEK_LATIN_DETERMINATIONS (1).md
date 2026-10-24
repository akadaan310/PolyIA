# Determinations II — The Greek and Latin Computational Grammars

*A companion analysis to the WAZNOMIA header. Arabic was determined from its own
machines; here Greek and Latin receive the same treatment, each on its own terms —
followed by the divine names, and a survey of the other systems that feed
scientific nomenclature.*

---

## Part I — Greek: the composing system

Arabic interleaves root and pattern inside one word. Greek does something else, and
the difference is the first thing to determine about it: **Greek composes.** A stem
carries the core event; a closed inventory of prefixes binds before it, a closed
inventory of suffixes binds after it, and the whole compound stays legible — each
piece keeps its own meaning, and the name is the sum of its pieces' functions.

### The στοιχεῖον

Greek's minimal unit does double duty in a way no other system's does:
**στοιχεῖον** means *a letter of the alphabet* and *an element of nature* — the
same word, because Greek thought of both as *one item in an ordered row* (στοῖχος,
a rank, a file of soldiers). The letters are elements; the elements are letters.
Every later "element" in science — Euclid's Στοιχεῖα, the chemical elements —
inherits this determination: *a minimal unit that stands in a series.*

### The stem carries aspect

The Greek verb does not have one stem with endings. It has **stem-operators**:
present stem (the event unfolding), aorist stem (the event as a point), perfect
stem (the event completed, its state persisting), future stem (the event
projected). Aspect is computed in the stem itself, before any ending binds.
Computationally: the stem is a function of the event's *temporal shape*, and the
endings then bind person, number, voice, mood. Two operator layers, in sequence —
stem first, agreement second.

### The cases are relation tags

Five cases, each a typed edge between a noun and its governor:

| Case | Tag | Function |
|---|---|---|
| Nominative | SUBJECT | the one the sentence is about |
| Genitive | OF | source, possession, partition — the *from/of* edge |
| Dative | TO/FOR | recipient, instrument, location — the *to/with* edge |
| Accusative | TARGET | the object reached by the verb's action |
| Vocative | ADDRESS | the one spoken *to* — the call edge |

A Greek sentence is a small typed graph: verbs govern nouns, and the case ending
on each noun declares the type of its edge. This is why Greek word order can be
free — the typing travels on the words, not on their positions.

### The prefix operators

| Operator | Delta | Example |
|---|---|---|
| σύν- (syn-) | together | synthesis — a putting-together |
| ἀντί- (anti-) | against, facing | antithesis; also *in place of* |
| ἀνά- (ana-) | up, back, again | analysis — a loosening-up/back |
| κατά- (kata-) | down | catastrophe — a turning-down |
| ὑπέρ- (hyper-) | over, beyond | hyperbole — a throwing-beyond |
| ὑπό- (hypo-) | under | hypothesis — a placing-under |
| μετά- (meta-) | across, after, among | metaphor — a carrying-across |
| πρό- (pro-) | before, forward | problem — a thing thrown forward |
| ἀ-/ἀν- (a-/an-) | not (privative) | atom — the *un*-cuttable; anonymous |
| δυσ- (dys-) | badly, hard | dyslexia — the bad-reading |
| εὖ- (eu-) | well | eulogy — the good-account |

### The suffix operators

| Operator | Makes | Example |
|---|---|---|
| -σις (-sis) | the *process* | analysis, synthesis, crisis, thesis |
| -μα (-ma) | the *result* | theorem (thing beheld), problem, system, drama (thing done) |
| -τής/-τωρ (-tēs/-tōr) | the *agent* | poet (maker), critic (judge), rhetor |
| -τρον (-tron) | the *instrument* | thermometer — the heat-measurer |
| -ικός (-ikos) | *pertaining to* — the science-adjective | physics, mathematics, logic |
| -εῖον (-eion) | the *place of* | museum — place of the Muses; lyceum |
| -ία (-ia) | the *abstract condition* | philosophy → philosophia; astronomy → astronomia |

Read the table as a machine: -sis freezes an event as a process-noun, -ma as its
product. A Greek science-name is usually an -ikos adjective over one of these,
with "art" or "knowledge" understood: ἡ φυσικὴ (τέχνη) — *the natural art*.

### Determinations: the sciences in Greek

- **Mathematics** — μαθηματική, from μάθημα, *what is learned* (μανθάνειν, to
  learn). The science is named *the learnables*: knowledge defined by
  teachability.
- **Geometry** — γεωμετρία: γῆ (earth) + μετρεῖν (to measure). *Earth-measuring* —
  the surveyor's art of the Nile fields, abstracted.
- **Physics** — φυσική, from φύσις, *nature as growth* (φύειν, to grow, to bring
  forth). Physics is the study of things that unfold from themselves.
- **Astronomy vs astrology** — ἀστρονομία (ἄστρον star + νόμος law/arrangement:
  *the law of the stars*) against ἀστρολογία (λόγος: *the account of the stars*).
  The -nomia/-logia split is the determination: one claims law, the other only
  discourse. The same split runs through geology, biology, theology.
- **Philosophy** — φιλοσοφία: *the love of wisdom* — a disposition, not a domain;
  the only great science named for an affect.
- **Arithmetic** — ἀριθμητική, from ἀριθμός, number — itself from the root of
  *fitting together, counting off in order*.
- **Music** — μουσική: *the (art) of the Muses* — named for its patrons, not its
  material.
- **Chemistry** — χημεία, and its road is the long one: most plausibly from
  Egyptian *km.t*, the Black Land, through Greek χημεία into Arabic **الكيمياء**
  (*al-kīmiyāʾ*), and back into Latin as *alchimia*. The word for the most Greek
  of sciences reached Europe wearing an Arabic article.

### Determinations: the divine names in Greek

- **Zeus** — Ζεύς, genitive Διός: two stems for one god, and the alternation is
  the determination. Both descend from Proto-Indo-European **\*dyēus**, *the
  shining sky, the day* — the nominative from \*dyēus, the oblique from \*diwós,
  the *w* surviving in the genitive like a fossil in the paradigm. Zeus is *the
  bright sky* declined.
- **Hermes** — Ἑρμῆς. The traditional and still most-supported derivation: from
  **ἕρμα** (*herma*), a heap of stones, a cairn — the boundary-piles and
  road-markers that became the squared pillars (herms) set at thresholds and
  crossroads. The god of travelers, boundaries, crossings, and heralds would be
  named *the one of the stone-heaps*. Grade: **inferred** — anciently believed,
  linguistically plausible, not proven; a pre-Greek origin has also been argued.
- **The Muses** — Μοῦσαι, from the PIE root **\*men-**, *to think*. The same root
  generates: *mania* (thinking gone wild), *mnēmē* (memory; Mnemosyne is Memory
  herself, mother of the Muses), *amnesia* (a-mnēsia — the not-remembering),
  *mnemonic*, Latin *mens* (mind), *monitor* (the warner), and — through
  Sanskrit — *mantra*. One root: the entire nomenclature of mind, memory, and
  inspiration is its orbit.
- **Athena, Apollo** — recorded honestly as **undetermined**: both names resist
  Indo-European derivation and are widely held to be pre-Greek inheritances.
  A determination system that cannot say *unresolved* is not a determination
  system.

---

## Part II — Latin: the orbiting system

Latin neither interleaves nor merely composes. Latin **orbits**: a verbal root at
the center, prefix operators fixing its trajectory, suffix operators fixing its
role, and around the whole grammar the declension and conjugation *tables* —
complete paradigm grids in which every cell is a state and every state has a form.
Latin is the most *tabular* of the three: its teaching tradition could print the
language as grids, because the language substantially *is* grids.

### The prefix operators are spatial logic

One root, **portāre** (to carry), determined six ways by its bound operator:
**im**port (carry in), **ex**port (carry out), **trans**port (carry across),
**sup**port (carry from beneath), **re**port (carry back), **de**port (carry
away). The same machine runs on **ferre** (to bear): *transfer* (bear across),
*refer* (bear back), *differ* (bear apart — whence *difference*), *infer* (bear
in), *offer* (bear toward), *prefer* (bear before). The prefix is an operator
over trajectories; the root supplies only the act. Spatial first, then
metaphorical — every abstract Latin compound is a path drawn first in space.

### The suffix operators

| Operator | Makes | Example |
|---|---|---|
| -tio/-sio | the *process* | computatio, functio, structio's kin |
| -tor | the *agent* | calculator, generator, actor |
| -tura/-tus | the *result-state* | structura — the built condition |
| -tas | the *quality* | veritas (truth-ness), libertas |
| -bilis | *capable-of being* V-ed | legibilis — readable |
| -culus/-ula | the *diminutive* | particula — the little part (→ *particle*) |
| -osus | *full of* | verbosus — full of words |
| -ium/-ia | the *abstract/system* | imperium; scientia |

### Six cases: one more edge than Greek

Latin keeps the Greek five and adds the **ablative** — the *from/with/by* edge,
the instrument-and-source relation that Greek folds into its dative. A case
system is an inventory of typed relations; Latin's inventory has six members,
and every noun phrase in the language is typed by one of them.

### Determinations: the sciences and the instruments in Latin

- **Science itself** — *scientia*, from *scīre*, to know — from PIE **\*skey-**,
  *to cut, to separate*. Knowing is *distinguishing*: the same root gives
  *scissors*, Greek σχίζειν (to split → *schism*, *schizophrenia*), and *nice*
  (from *nescius*, not-knowing — the word slid from ignorant to precise to
  pleasant). Determination: the European word for knowledge names an act of
  **cutting apart**.
- **Medicine** — *medicīna*, from *medērī*, to heal, to attend.
- **Agriculture** — *ager* (field) + *cultūra* (the tending, from *colere*, to
  cultivate, to dwell, to honor — the root that also yields *cult* and
  *culture*: tending a field and tending a god are one verb).
- **Calculus** — *a little pebble*: the counting-stone, matter before
  abstraction. **Digit** — *digitus*, the finger: the machine age counts in
  fingers. **Data** — *the given things*.
- **Integer** — *in-* (not) + *tangere* (to touch): the untouched, the whole.
- **Binomial nomenclature** — Linnaeus's two-name addressing: *genus* +
  *species-epithet*, a two-level address over the tree of life, issued in Latin
  precisely because Latin was the closed, finished system — determinations
  stable because the language no longer moves. The header's closure member,
  enacted as policy by an entire science.

### Determinations: the divine names in Latin

- **Jupiter** — *Iuppiter*, from **Dyēus ph₂tḗr** — *Sky Father*. This is the
  same determination as Greek **Zeus patēr** and Sanskrit **Dyáuṣ pitā́**: one
  Proto-Indo-European name, three daughter languages, three surviving forms.
  The strongest cross-language determination in this document, and it is
  **established**: comparative grammar recovers it the way the fibre analysis
  recovers a root.
- **Deus, divine** — from PIE **\*deiwós**, *the shining one, the celestial* —
  the \*dyew- root again: day, deity, Diana, and (through Germanic) *Tiw*,
  preserved in *Tuesday*. The Latin word for a god is a determination: *the one
  who shines by day*.
- **Mercury** — *Mercurius*, traditionally from **merx** (merchandise):
  the merchant's god, *commerce* wearing a divine name. Grade: **inferred**.
- **Venus** — from PIE **\*wen-**, *to desire, to strive for*: the same root as
  *win*, *wish*, *venerate*, Sanskrit *van-* — desire as a root generating
  gods and games alike. Grade: **established** as a root family.
- **Mars, Saturn** — **undetermined** on present evidence (Mars from older
  *Mavors*, possibly Italic; Saturn possibly Etruscan). Recorded as such.

---

## Part III — The Egyptian names, and the Idris convergence

Egyptian writes consonants and leaves the vowels unrecorded; its divine names
reach us as skeletons — determinations from a rasm, graded accordingly.

- **Thoth** — Egyptian **Ḏḥwty** (Djehuty), Greek Θώθ. The name's derivation is
  **unresolved**: a long-standing proposal reads it as *the ibis-like one*,
  after his sacred bird. What is established is his portfolio: reckoning,
  writing, measure, the moon's count — the god *of* the alphabet and the
  calendar, patron of every determination in this document's sense.
- **Ptah** — **Ptḥ**, of Memphis. Derivation **unresolved**. His theology is
  not: in the Memphite account, Ptah creates **by the heart and by the
  tongue** — the heart conceives the thing, the tongue utters its name, and
  by the utterance it is. The ancient world's own theory that *naming computes
  the world*: determination as ontology, three thousand years before the
  formalism.
- **Idris** — إدريس. Three links, graded separately:
  1. *The name in the Qur'an*: a prophet, "a man of truth" (19:56).
  2. *The traditional gloss*: classical commentary derives his name from
     **كثرة الدراسة** — the abundance of his studying the books — a
     determination from درس (to study). Grade: **traditional**.
  3. *The identification*: medieval Arabic Hermetic literature identifies
     Idris with **Hermes** — and through Hermes with Thoth — the
     thrice-identified figure (Idris = Enoch = Hermes Trismegistus), and the
     tradition adds that Idris was **the first to write with the pen**.
     Grade: **traditional, attested in the sources**.
  The convergence is the data: three civilizations, asked who invented
  writing and measure, answer with one figure wearing three names — a
  boundary-stone god (Hermes of the ἕρμα), an ibis scribe (Thoth), and a
  student (Idris, the much-studying). Whether the figure is one is a question
  of theology and history; that the *function* is one — writing, reckoning,
  measure — is a determination this system can make.

## Part IV — The other nomenclature systems, briefly

The rooted-language architecture is not unique to the three classical tongues.
Four more systems feed scientific nomenclature, each with a different machine:

- **Sanskrit, and Pāṇini's machine.** The *Aṣṭādhyāyī* (c. 4th century BCE) is
  the most computational grammar of the ancient world: 3,959 sūtras — rules,
  metarules, and an algebra of markers — generating the language from ~2,000
  listed roots (*dhātu*) bound by suffix operators (*pratyaya*). The
  architecture is ṣarf's twin, independently built. Determinations: **yoga**,
  from *yuj*, to yoke; **karma**, from *kṛ*, to do, to make; **mantra** —
  *man* (think) + **-tra**, the *instrument* suffix: an *instrument of
  thought*. That -tra is the same inherited operator as Greek -τρον and Latin
  -trum: three systems running one shared library, forked from a common stock.
- **The sine string.** Sanskrit **jyā** (bowstring) → its synonym *jīvā* →
  transliterated into Arabic as **جِيب** (*jīb*), read by the Latin translators
  as **جَيْب** (*jayb* — a fold, a bosom, a bay) → rendered *sinus*, Latin for
  fold/bay. The name of the most-used function in mathematics is a translation
  chain with one famous loss event in the middle: a determination that can
  only be recovered by accounting the loss, link by link.
- **Hebrew** — Arabic's sister inside the Semitic family: the triliteral
  architecture is shared inheritance, not borrowing. **כָּתַב** (*katav*, he
  wrote) is كتب letter for letter. Determinations across the family are
  cognate determinations — the fibre includes both languages.
- **Chinese** — a different machine entirely: characters compose a *semantic
  radical* (the class) with a *phonetic component* (the sound hint) —
  determination by class + approximation, not root + operator. When Western
  science arrived, Meiji Japan coined its nomenclature inside this machine —
  **哲学** (*philosophy*, coined by Nishi Amane), **科学** (*science*) — and the
  coinages flowed back into Chinese: nomenclature determined eastward, then
  re-imported.

## Part V — What the three systems share, restated for nomenclature

1. **Science-names are nominalizations.** -sis/-ma, -tio/-tas, the masdar:
   every tradition builds its sciences out of verbs frozen into things. The
   inventory of a science's names is a fossil record of its operations.
2. **Operators are inherited, forked, and traded.** PIE *-tro-* (instrument)
   runs in three systems; the Arabic article *al-* rides inside *algebra,
   alcohol, alkali, alchemy* into every European language — a prefix operator
   smuggled inside loanwords, still marking its origin.
3. **Determinations split where worlds split.** The atom is a mote in Arabic,
   an uncuttable in Greek; the catalyst urges in Arabic and loosens in Greek.
   The splits are the frontier map of the concepts themselves.
4. **Transmission is lossy, and the loss is data.** Sine's fold, chemistry's
   Arabic article, zero's two Latin coats (zephirum, cifra): a name's chain
   of custody is part of its determination, and the chain must be accounted —
   never silently normalized away.
5. **Unresolved is a determination.** Athena, Mars, Thoth, Ptah: the honest
   output is *unresolved, on present evidence* — a fibre with no surviving
   member, recorded as such, awaiting a better inventory.

*— Determinations II. Companion to the WAZNOMIA header; grades follow the
header's discipline: established, inferred, proposed, traditional, unresolved.*
