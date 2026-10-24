# Typed API

`packages/snad-core/src/types.ts` is the authoritative contract. `snad-core` has no runtime dependencies and runs in Node and browsers. Build with `npm run build:core`; import the built workspace package or install its generated npm tarball.

| API | Contract and interpretation |
| --- | --- |
| `adaptDialogue(turns, source?)` | Supplied text/identity/features/timestamps become independent input units. Absent identities remain unknown. |
| `adaptQuran(record)` | Canonical locus, exact source text and whitespace spans. Optional aligned morphology stays separately attributed. |
| `quranLocus(surah, ayah)` / `parseLocus(id)` | Validate canonical 114-surah domain and exact ayah ranges. No aliases outside the corpus. |
| `analyze(input, {quoteCues?})` | Pure analysis producing units, transitions, frames, provenance and an uncertainty ledger. |
| `analyzeStream(asyncInputs, options?)` | Async generator over independent analyses; stream your source without retaining all analyses. |
| `serialize(analysis)` / `deserialize(json)` | Versioned portable `snad/1` analysis; runtime validation rejects malformed objects. |
| `structuralSignature(analysis)` | A defined lossy feature/transition signature; equivalence under it is not semantic equivalence. |
| `perturb(input, {kind, seed})` | Copy plus deterministic `drop-features`, `reverse-units`, or `mask-speakers`; source remains unchanged. |
| `transitionMorphism(t)`, `identity(endpoint)`, `compose(...morphisms)` | Typed directed path composition; endpoints must agree. Finite law checks are in tests. |
| `mineMotifs(analyses, width?)` | Counts contiguous transition-label sequences; frequency does not establish discourse meaning. |
| `induceGrammar(analyses)` / `acceptsGrammar(grammar, analysis)` | Builds and queries a deterministic prefix-trie automaton that accepts exactly the observed transition-label sequences. This is an empirical finite-language baseline with no claim of semantic validity or generalization. |
| `topology(units, transitions)` | Basic graph counts, weak components and cycle rank; ordered token chains inherently impose much of this structure. |

Input sources carry stable IDs, origin URI, revision and license. Units carry source spans, optional `Features`, `Attribution`, `Evidence`, and `Timestamp`. Features distinguish person, number, tense and aspect. Attribution distinguishes speaker, addressee, referents, narrator and frame. Evidence status is one of `observed`, `derived`, `hypothesis`, `interpretation`.

`Transition.kinds` states which available fields changed; `lexicalContinuity` is a surface comparison and `attributionChange` compares annotated attribution fields. `confidence` means **uncalibrated evidence quality**, never a probability that the interpretation is true. Unknown identity values do not become known through repetition.

Source orthography is not normalized in storage. The QAC projection uses an explicitly versioned comparison key solely to check alignment. Conflicting segment features and unmatched word surfaces are recorded separately; they are not silently converted into known token features. See `data/quran.morphology.provenance.json` for the exact rule.

Extend adapters by implementing `LanguageAdapter<T> = { id: string; adapt(value: T): DiscourseInput }`. A future NOOR × ITACHI importer can supply original timestamp text, units, uncertainty and explicit consent/source references through the general adapter. No private transcript is included in this repository.
