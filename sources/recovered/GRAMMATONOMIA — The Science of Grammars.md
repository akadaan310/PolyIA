# GRAMMATONOMIA — The Science of Grammars

*POLYIA working paper 1 (Muse). The design by which every language receives a
deterministic generative model in one shared format — and by which all of them
compose into a universal generative model. No step in any model is an inference.
Research intelligences gather data; machines do the generating.*

---

## 0. The unit: the Pack

POLYIA's foundation already fixes the unit, and this paper adopts it verbatim.
A language variety `v` is a **pack**:

`L_v = (VarietyID, Σ, O, T, P, M, X, E) + NegativeGrammar`

phoneme inventory, orthography maps, pronunciation transduction, phonotactics,
morphology, lexicon, evidence policy — and the negative grammar: what the
variety refuses, lacks, or forbids. One language may hold several packs
(eras, dialects, scripts). An alphabet alone determines none of it; every pack
is built from attested data or expert specification, graded accordingly.

## 1. The level stack

Every grammar is measured at four depths. The Greek letters mark **depth**,
which is what they were reaching for all along:

| Level | Name | Content | Machine class |
|---|---|---|---|
| **Α** | Sound | phoneme inventory, feature bundles, phonotactics | finite-state (regular) |
| **Β** | Form | morphology: roots, operators, paradigms | templates + FSTs |
| **Γ** | Phrase | syntax: constituency, government, order | CFG + unification |
| **Δ** | Sense | composition of meaning, determination | typed relations (Q-Paths) |

The privative is written with the Greeks' own device: **ἀ-** — the alpha
privative, the ἀ- of *a-tom* and *a-mnesia*. A privative entry at any level
reads: *(feature) = ἀ*, with its replacement and its evidence attached (§3).

## 2. The classes — grammars by architecture

A language's class is not an essence; it is a **measured operator profile**:
where its operators sit, how they bind, what they propagate. Seven classes
cover the attested space; a pack may blend classes by level (Chinese is
Componential at Α/Β script level and Positional at Γ).

1. **DIAPLECTIC** — *interleaving.* Root and pattern occupy the same letters.
   Arabic, Hebrew, the Semitic family. Signature: template functions over a
   consonantal root space; the fibre phenomenon lives here.
2. **CATENARY** — *chaining.* Operators concatenate in fixed order. Two
   subtypes: **Harmonic** (Turkish, Finnish, Hungarian — suffix vowels are
   *computed* from the stem by a harmony propagator; the chain carries a
   running state) and **Stacking** (Japanese, Korean — a fixed operator stack:
   stem → negation → tense → politeness → passive → causative, compositional
   to depth).
3. **SYNTHETIC** — *compounding.* Stems compose into stems; the compound is a
   composed function. Greek, Sanskrit, German. Signature: stem-composition
   rules + operator suffixes; the longest words, the most legible names.
4. **ORBITAL** — *affix orbits + tables.* Prefixes fix trajectories around a
   root; the grammar is substantially its paradigm grids. Latin and its
   daughters. Signature: orbit operators × state tables.
5. **POSITIONAL** — *analytic.* Words are invariable; grammar lives in word
   order and free particles. Vietnamese; Mandarin at Γ. Signature: the
   phrase machine does the work the form machine refuses.
6. **COMPONENTIAL** — *script composition.* Signs compose a class-marker with
   a sound-hint. Chinese characters; Egyptian hieroglyphs in their own mode.
   Signature: a sparse grid (class × hint) whose filled cells are the writing
   system — sparsity itself is a measurable class property (tonight's toy
   grid: 67% empty at 3×6; the real grid's emptiness is the point).
7. **HOLOPHRASTIC** — *sentence-words.* Noun incorporation and polysynthesis:
   one word carries a clause. Inuit languages, Mohawk; Hopi leans here.
   Signature: the Β and Γ levels partially fuse.

**Discovery procedure.** A class is assigned by measurement, never by family
reputation: interleave ratio (share of forms not segmentable into a linear
morpheme string), operator-position distribution, fusion index (features per
morpheme), propagation phenomena (harmony, umlaut, sandhi). The measurements
are the determination; the class name is their summary.

## 3. Privative profiles — the anti-grammar, determined

What a language lacks informs as surely as what it has — but a lack is a
determination and must be *typed*, or it becomes mythology. A privative entry
is a five-tuple:

`(level, feature, status, replacement, evidence)`

**Worked example — Hopi and tense.** Whorf claimed Hopi has no reference to
time at all. Malotki's *Hopi Time* (1983, ~600 pages) answered with hundreds of
temporal forms: Hopi grammaticalizes a **future / non-future** axis, owns
temporal units and metaphors. Lucy and Lee answer in turn that Malotki
mis-states Whorf's narrower claim. The profile therefore reads:

- (Β/Γ, past/non-past tense axis, **ἀ-privative**, replacement: future/
  non-future axis + rich aspect/mode, evidence: **contested**, Whorf contra
  Malotki, dispute live).

The lesson generalizes into law: **an absence is always (feature absent,
system present instead).** A bare "no word for X" is a fibre with one member
missing its attestation check — the same failure Claude's appendices caught in
my header, wearing ethnographic dress. Pirahã's famous lacks (number words,
recursion — Everett) are carried in the registry as *contested* for exactly
this reason.

## 4. The ubiquity set U

Against the privatives stands what recurs everywhere it has been looked for.
Candidate members, each to be graded by cross-linguistic attestation counts in
the dataset phase (WALS-style): relation-marking of some kind; nominalization;
negation; a question operation; modification recursion (phrases inside
phrases); an agent/patient asymmetry somewhere in the system; sound symbolism
pockets; the vowel/consonant asymmetry at Α. U is not assumed — it is the
intersection the data keeps returning, recomputed as packs accumulate. **U is
the amortized layer**: what is built once for U is spent once for all
languages.

## 5. The universal generative model

The composition the classes make possible:

```
pure function / meaning signature  (Δ, language-free, typed)
        |  U-normalization: the signature stated in ubiquity terms
        v
per-class realization machines     (Β/Γ, one per pack)
        |  each arrow a deterministic transducer, template, or propagator
        v
surface forms per variety          (Α, with orthography O)
        ^
        |  every step witnessed by Q-Strings: (claim, chart, evidence, grade)
```

Ask the universal model for "an essay on the history of this word" and the
Δ-signature decomposes the request; each pack realizes its part through its
own class machine — Arabic determining by fibre, Turkish propagating harmony,
Chinese composing class + hint, Hopi answering from its profile including its
privatives. The output differs by language *because the machines differ*,
and every difference is inspectable. That is the deliverable the builder
completes: **for each language, a generative model, a transformer model
(between packs, via Δ), and a recognizer — all deterministic, all graded.**

## 6. The data foundation (verified to exist)

- **UniMorph** — inflection tables for **170+ languages**, one universal
  feature schema (23 dimensions, 240+ features). Tables compile mechanically
  into Β-level machines: this is the mass-production route to 100 packs.
- **WALS** (World Atlas of Language Structures) — ~190 structural features
  across ~2,600 languages: the privative/ubiquity grading source.
- **PHOIBLE** — phoneme inventories for ~2,000+ varieties: the Α level.
- **Glottolog** — the variety registry and classification (~8,500 languoids):
  the VarietyID authority.
- **CLTS / Lexibank** — cross-linguistic transcription and wordlist standards:
  the T level's witnesses.

## 7. Cost accounting — the amortization ledger

Every research operation dispatched (to Perplexity Computer, to a Claude
session, to a subagent) is logged as `(task, instrument, spend, yield,
cost-per-determination)`. The economics we are buying: a WALS pass prices
*every* privative profile at once; a UniMorph conversion prices a Β-machine
per language at table-compilation cost, not at authorship cost. Cost per pack
must fall as the wave number rises — if it doesn't, the ubiquity layer is not
doing its job and the ledger will say so. (The per-line cost discipline of
large software houses, applied to determinations.)

## 8. Waves

- **Wave 1 — built tonight, by hand, in this format:** Arabic (Ṣarf + ʿArūḍ +
  QIA phonetics), Hebrew (binyanim), Turkish (harmony engine), Japanese
  (operator stack), Sanskrit (dhātu table), Chinese (componential grid),
  Greek + Latin (Determinations II), Hopi (privative profile). All running,
  assertions passing, candidates marked as candidates.
- **Wave 2 — dataset survey first** (Perplexity Computer, bounded mission,
  costed): availability matrix for ~25 varieties × (UniMorph, WALS, PHOIBLE,
  Glottolog), then pack construction for the best-covered ten.
- **Wave 3 — the hundred:** UniMorph table-compilation at scale; WALS-graded
  privative profiles for every pack; the Δ-composer switched on across all
  packs at once.

*— Grammatonomia, POLYIA working paper 1. Companion to the WAZNOMIA header,
Determinations II, and the QIA handoff. Grades: the class system and profiles
are proposed; the Wave-1 machines are established (executed); dataset figures
are as cited from their projects.*
