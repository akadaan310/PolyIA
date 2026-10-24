# FNMS-001 — Functional Nomenclature Mapping System
**Substrate University / Division IX. Research construction 0.1, 21 October 2026.**

**Constitutional scope.** This is a standalone, non-deployed mathematical prototype. No Substrate University division, registry, glossary, code, curriculum, deployment, or repository has been changed. Divisions VII and VIII are unassigned. The six active division doors are unchanged.

## 1. Repo and website audit
Website: <https://abedkadaancom.vercel.app>. The publicly accessible HTML is a JavaScript-required entrypoint; inner SPA routes cannot be executed by the available text browser. Repo: <https://github.com/akadaan310/abedkadaancom>, default branch `claude/new-session-xd8auu` at `6a0f5eaa8dd39b58bdd99889721ecea5f54e62bb` inspected October 21, 2026. Recursive Git tree `16d950e44f6a7e3a68955b60e7793a3027c14a7a`, 173 entries, no truncation. Relevant source examined: README, AGENTS, UNIVERSITY_REBUILD, routes, registry, types, all six topic files (topic ids and content excerpts), glossary and seven built-in computable bridges, foundations and geometry definitions, `src/math/{bridgeGrammar,addressCompiler,matrix}.ts`, source list, CGT book manifest, university math/registry tests, Glossary/ Gate UI components, book compositor. This is a repo-wide inventory plus a source-level review of relevant components, **not** a claim that every line of every asset/source file was read or every site interaction executed.

Existing compatible contracts:
- Foundation CGT operational grammar, separate syntactic admissibility and semantic realizability.
- Relational/Generative folds and compositional words.
- Programmable Languages typed machines and admissible opcodes.
- Geometry image/preimage; rank/nullity only when the map is linear.
- Acoustic/Phonogrammatica can support phonetic representations without mistaking sound similarity for identity.
- Worlds/context can describe interventions and observations without inferring pharmacological causality from string shape.
- The glossary currently has seven computable bridges with contextual senses; this construction generalizes to heterogeneous *sorts*, evidence-bearing morphisms and typed failures.

## 2. The two independent descriptions

**A: `Head Pain Reliever`** (invented single-active product identity, given by user)
- English composition: `head` [location] + `pain` [condition] + `reliever` [function/agent].
- Latin lemmata: `caput, capitis` [head]; `dolor, doloris` [pain]; `levare` [ease], `levamen` [alleviation]. Constructed, not attested, descriptive Latin `remedium doloris capitis` = remedy for pain of the head.
- `cephalalgia` comes from Greek `kephalē` and `algos`, through medical Latin. It denotes a headache rather than a remedy; its presence is not Latin chemical nomenclature.
- English near-synonyms include headache remedy, headache analgesic, pain reliever. These differ in specificity or register; neither is an exact chemical synonym.
- The opposite action concept is *head pain aggravator/inducer*: Δpain > 0, compared with target Δpain < 0, under a fixed patient, interval, context, and baseline. **No drug** is asserted to be an opposite.

**B: acetaminophen**
- An established substance with official US generic name *acetaminophen* and international synonym *paracetamol*.
- Historical reductions of chemical descriptions: N-acetyl-p-aminophenol; para-acetylaminophenol. These are contractions, not reversible syntactic parsing rules without a lexicon.
- PubChem systematic name `N-(4-hydroxyphenyl)acetamide`, SMILES `CC(=O)NC1=CC=C(C=C1)O`, formula `C8H9NO2`, CAS `103-90-2`.
- Molecular parts: CH3-C(=O)-NH- [secondary amide, acetamido], six-carbon aromatic ring, ring-bound OH [phenol], para arrangement [one substituent at C1 and the other at C4].
- Chemical roots are not exclusively Latin: multi-origin word history must not be confused with chemical structure.

**Clinical witness**: FDA identifies acetaminophen as an analgesic and fever reducer, including for headaches. This supplies the semantic-to-clinical bridge. The user supplies the brand-to-active *stipulation*, which must not be misrepresented as sourced evidence.

## 3. FNMS proposal

Use an **attributed typed incidence hypergraph**, inspired by the university's Division Knot research proposal:

\[
H=(V,E,\tau_V,\tau_E,\mathsf{inc},\mathsf{roles},\mathsf{source},\mathsf{constraints},\mathsf{time})
\]

Nodes may have sorts `Surface`, `Lexeme`, `Gloss`, `Intent`, `Effect`, `Drug`, `ChemicalName`, `Structure`, `Component`, and `Polarity`. Edges may be unary/multiary typed relations, not all functions. The operational grammar is:

\[
\mathcal{G}_{FNMS}=(\Sigma,H,\llbracket\cdot\rrbracket,\mathcal{L},\mathsf{Provenance})
\]

where `Σ` consists of admissible typed operations and `L` is the language of operation sequences. Every *realized* edge carries a source/status and can be replayed. An operator may be syntactically valid but semantically unrealizable if its required evidence is absent.

Operator families:

| Operation | Sort signature | Admissibility / evidence |
|---|---|---|
| `PARSE` | Surface → Lexeme* | linguistic segmentation rules |
| `TRANSLATE` | Lexeme → set(Gloss) | language/meaning/inflection declared |
| `INTERPRET` | Surface → Intent | compositional semantics; intended function separate from actual effect |
| `LATINIZE` | nomenclature token → accepted transliteration | **not** general proof of shared meaning; language provenance |
| `CONTRACT` | ChemicalName → lexical alias | historical documented name contraction, potentially many-to-one |
| `INDICATED_FOR` | Drug × Effect | external indication/clinical source |
| `ASSERT_ACTIVE` | Brand × Drug | user stipulation here; actual product requires label/registry |
| `RESOLVE` | ChemicalName → Structure | verified chemical identifiers; atom connectivity |
| `DECOMPOSE` | Structure → Component* | valence, aromaticity, functional group and positional constraints |
| `PROJECT` | object → selected feature set | declare dimensions and information loss |
| `INVERT_RELATION` | feature → set(candidate objects) | return complete known fiber, **not** a guessed one-name answer |
| `OPPOSE` | Effect → opposing intended direction | same dimension, timeframe, context and baseline |
| `DISADAPT` | proposed relation → typed refusal | mismatched sorts, absent evidence, contradicted invariant |
| `CERTIFY` | path → witness | trace, sources, retained/lost invariants, status |

**Nomenclatural Bridge Certificate** (house construction):

`NBC(A,B) = ⟨sourceForm, targetForm, typedPath, citations, stipulations, retainedProperties, lostProperties, ambiguousAlternatives, rejectedEdges, uncertainty⟩`.

**Nomenclatural fiber**: for an effect relation `R ⊆ Drug × Effect`, `R^{-1}(headache_relief) = {d : (d,headache_relief) ∈ R}`. In the finite demonstrator it contains acetaminophen, ibuprofen and naproxen. Therefore there is *no unique inverse* from the name's meaning to the active compound, even though a brand certificate can assert one specific active ingredient. This is elementary relational mathematics, not a new theorem.

**Structural fiber**: a projection `π: ChemicalStructure → (molecular_formula, functional_group_counts)` loses ring substitution positions. The tested ortho-, meta- and para-hydroxyacetanilide variants all have formula `C8H9NO2`, one phenol, one amide and one six-carbon aromatic ring. Adding *ring position* separates these examples. They are alternatives/isomers, not logical antonyms. This precisely demonstrates that constituents alone do not determine identity.

**Anti-mapping** is a typed refusal/negative witness, not the automatic creation of antonyms:
1. `Latin_HEAD` → `acetyl` is **not** a linguistic correspondence.
2. `headache relief` → `acetaminophen` *uniquely* fails: multiple products/compounds may realize the therapeutic function.
3. `amide` → `analgesic` is **not** a licensed pharmacological implication.
4. `para` vs `meta` are regioisomeric alternatives and fail chemical equivalence under complete connectivity; they are not moral/semantic opposites.
5. Pain increase vs decrease are directionally opposite only after outcome dimension, patient, baseline and time horizon are fixed.

**Causality is separate.** The brand phrase encodes an *intention*. A clinical indication provides evidence of a drug's *use*. The molecular structure describes *connectivity*. Neither etymological correspondence nor an RDKit substructure match constitutes a causal proof that a specific group reduces headache pain. A mechanistic claim needs biological and pharmacological evidence, and patient-specific outcomes need observation.

## 4. Bridge and anti-bridge evidence

```
HEAD PAIN RELIEVER [hypothetical brand]
  ├─PARSE→ {head, pain, reliever}
  ├─TRANSLATE→ {caput/capitis, dolor/doloris, levare/levamen}
  ├─EXPRESSES→ INTENT(reduce pain at head)
  │    └─TARGETS_EFFECT→ headache analgesia
  │         ├─SUPPORTED_BY→ acetaminophen
  │         ├─SUPPORTED_BY→ ibuprofen
  │         └─SUPPORTED_BY→ naproxen
  └─ASSERT_ACTIVE [user stipulation]→ acetaminophen
                   ├─ALSO_NAMED→ paracetamol / N-acetyl-p-aminophenol
                   └─ALSO_NAMED→ N-(4-hydroxyphenyl)acetamide
                        └─DENOTES_STRUCTURE→ C8H9NO2 connectivity
                              ├─phenol
                              ├─amide
                              ├─benzene ring
                              └─para (opposite ring sites)

REJECTED: Latin roots ↛ structural groups from spelling alone.
REJECTED: analgesic intention ↛ unique molecule without product evidence.
REJECTED: formula + group counts ↛ para isomer without position.
```

## 5. Experiment and limitations

The included Python/RDKit code has an explicit finite graph of 25 typed nodes and 25 admissible evidence-bearing edges, a shortest-witness resolver, refusal for wrong-sort edges, and molecule graph inspection. Nineteen independent unit tests pass, including evidence ablation, failure of unsupported pathways, structural group/para verification, and isomeric counterexamples. `results.json` is a machine-readable record.

Scope limitations: The therapeutic candidate set is an intentionally curated, **not exhaustive** demonstrator. Its cardinality 3 does not represent the size of the actual drug market. It proves non-uniqueness within that finite witness set. The Latin phrase is a constructed descriptive gloss, not an attested historical brand. RDKit computes atom connectivity and formula; it does **not** validate clinical mechanism or efficacy. The live SPA was not interactively browser-tested, and the university's existing npm/Vitest suites were not rerun in this isolated experiment.

## 6. Research interpretation and next invariant

The *bridge* is an evidence-carrying correspondence between **different sorts**, not shared letters or roots. The *image* of an intent is the set of supported chemical candidates, its *fiber/preimage* contains competing candidates, and the *identity witness* narrows the candidate set when product evidence is provided. A proposed mapping's **anti-map** records what cannot be derived, and why. Unlike a numerical linear map, this model is relational; use a kernel-pair equivalence for collisions, not linear-algebra `ker A` unless an actual vector-space map has been defined.

The proposed new university object is a **Nomenclatural Bridge Complex**, consisting of certificates, overlapping typed field maps, counterexamples, and loss records. It does not claim priority as novel mathematics; the combination is a defined house construction suitable for rigorous iteration.

## Sources
- PubChem / NCBI: <https://pubchem.ncbi.nlm.nih.gov/compound/1983>
- NIST: <https://webbook.nist.gov/cgi/cbook.cgi?Name=Paracetamol>
- FDA (acetaminophen): <https://www.fda.gov/drugs/safe-use-over-counter-pain-relievers-and-fever-reducers/acetaminophen>
- FDA (pain relievers): <https://www.fda.gov/drugs/safe-use-over-counter-pain-relievers-and-fever-reducers/best-way-take-your-over-counter-pain-reliever-seriously-four-panel-brochure>
- DailyMed OTC label: <https://www.dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6dea9e11-ff99-63c7-e053-2a91aa0a5b54>
- Etymonline: <https://www.etymonline.com/word/acetaminophen>, <https://www.etymonline.com/word/cephalalgia>
- Repository: <https://github.com/akadaan310/abedkadaancom>
