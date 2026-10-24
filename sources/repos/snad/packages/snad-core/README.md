# snad-core

A dependency-free TypeScript research SDK for comparing explicit discourse annotations. Browser and Node ESM compatible; it never resolves a speaker from grammatical person. The code is an independent implementation, not a copy of ISNAAD's detectors.

Build from the repository root with `npm ci && npm run build:core`. Import the built workspace package as `snad-core`; executable repository examples may import `packages/snad-core/src/index.js` through `tsx`.

```ts
import { adaptDialogue, analyze, serialize } from 'snad-core';

const input = adaptDialogue([
  { id: 'turn:1', text: 'I wait.', speaker: 'Mira', features: { person: '1' } },
  { id: 'turn:2', text: 'You wait.', speaker: 'Mira', features: { person: '2' } },
], { id: 'synthetic:example', kind: 'synthetic' });
const result = analyze(input);
console.log(result.transitions[0].kinds); // ['person']; no speaker change
console.log(result.units[0].attribution.addressee.status); // 'unknown'
const portable = serialize(result);
```

The labels in this example are synthetic manual declarations, not independently validated facts. Give each independent source its own stable `Source.id`, and provide unit IDs when records may be reordered before adaptation. Default dialogue IDs are local source/index coordinates.

## Model and API

All public interfaces are exported from [src/types.ts](src/types.ts). `DiscourseInput` has a source, stable ID, and ordered units. Each unit keeps exact text, optional UTF-16 source span, feature dictionary, evidence, attribution declarations, and timestamp. Attribution has separate speaker, addressee, referents, narrator, and quotation-frame fields. Grammatical person (`'1'`, `'2'`, `'3'`), number, tense, and aspect live in `features`, independently of identity.

| Function | Contract |
| --- | --- |
| `analyze(input, { quoteCues? })` | Pure synchronous analysis; unknown identities are explicit; empty units/features/text are valid. |
| `analyzeStream(asyncIterable, options?)` | Async generator yielding independent analyses, one per input. |
| `adaptDialogue(turns, source?)` | Preserves supplied labels, feature declarations, original timestamp strings and numeric uncertainty. |
| `adaptQuran(record)` | Validates canonical locus; preserves source orthography in `metadata.originalText`; creates token units with source spans. |
| `quranLocus(surah, ayah)` / `parseLocus(id)` | Canonical `quran:S:A` encoding and strict actual per-surah bounds; `SURAH_AYAH_COUNTS` totals 6,236. |
| `tokenize(text, unitId?)` | Whitespace tokens with exact UTF-16 offsets. Does not normalize Arabic or source text. |
| `serialize(analysis)` / `deserialize(json)` | Version `snad/1`; validates all derived content against deterministic replay and rejects schema/tampering mismatches. |
| `identity(endpoint)` / `transitionMorphism(t)` / `compose(...paths)` | Typed path objects with runtime endpoint checks; composition runs left to right. |
| `structuralSignature(analysis)` | Canonical restricted structural descriptor, described below. |
| `perturb(input, { kind, seed })` | Independent copy after complete feature ablation, unit reversal, or speaker masking. |
| `mineMotifs(analysisOrArray, width = 2)` | Counts contiguous connected paths of transition-kind labels. |
| `topology(unitIdsOrObjects, edges)` | Counts vertices, edges, components, cycle rank, directed simple density, and mean out-degree. |
| `induceGrammar(analysisOrArray)` / `acceptsGrammar(grammar, analysis)` | Deterministic prefix-trie DFA for exactly the observed transition-kind sequences. |

Unit IDs, source spans, feature/person values, identity status, timestamp ordering, evidence quality bounds, finite JSON content, and duplicate unit IDs/spans are validated. Errors are descriptive `TypeError`s. Inputs must be plain portable JSON objects; omit optional fields rather than assigning `undefined`. Features may contain additional string-valued keys; the built-in transition detector compares person, number, tense, and aspect. Custom keys remain in signatures and portable data.

## Evidence limits

The detector compares **adjacent units**. A grammatical difference requires both values to be present. Identity differences require two explicitly known identities. Missing annotations and a change from unknown to known identity never establish a speaker change. Empty referent lists mean unresolved reference, not proof that no referent exists.

Every transition states `confidenceMeaning: 'uncalibrated-evidence-quality'`. Its confidence is the minimum explicitly supplied evidence-quality score on its two units, or an uncalibrated default `0.5`. These scores are not empirical probabilities, statistical confidence intervals, or verified intentions. `lexicalContinuity` is lowercase whitespace-token Jaccard similarity; only this derived metric lowercases tokens. `attributionChange` records changes in supplied attribution fields, including explicit frame assignments.

Text observations, supplied annotations, derived transitions, hypotheses, and interpretations retain distinct evidence status. Source, unit, frame, transition, and separately attributed annotation-source nodes form a provenance graph. An uncertainty ledger records unresolved roles, absent grammar, timestamp uncertainty, and quotation heuristic limits.

Punctuation frame extraction handles straight/curly nested quotation marks within each unit. It records cue spans, parent frames, and heuristic evidence. It does not assign quoted speakers, infer reported intent, or link quotations across unit boundaries. Explicit `attribution.frameId` declarations can name external frames spanning supplied units. A non-root ID without a local definition is recorded as unresolved in the uncertainty ledger and as a supplied frame declaration in unit provenance; its containment and nesting are unvalidated. Turn boundaries are not inferred from prose. Set `{ quoteCues: false }` to disable the punctuation heuristic.

## Qur'an adapter

```ts
import { adaptQuran, analyze } from 'snad-core';

const analysis = analyze(adaptQuran({
  id: 'quran:20:1', surah: 20, ayah: 1,
  text: 'طه', source: { id: 'my-licensed-text', kind: 'quran' },
}));
// No morphology supplied: empty feature dictionaries, unknown speakers, zero grammar transitions.
```

The SDK bundles no corpus text and makes no interpretation claims. The repository's separately licensed dataset and corpus index supply the complete addressable domain. Empty text gets one empty placeholder unit; short and single-token verses are valid. Source whitespace remains in `metadata.originalText`, while unit spans select lexical tokens exactly.

Optional `features` is a token-aligned convenience array. Arrays with no annotated values, including `[]`, represent no feature evidence and need not match token count. Arrays carrying any annotation must match token count. Prefer `morphology: [{ tokenIndex, features, evidence }]` for separately attributed annotations: every such record requires nonempty evidence and a valid, unique token index. No Arabic morphology or speaker identity is fabricated when this data is absent.

## Operators and reproducibility

`compose(A→B, B→C)` returns `A→C` with concatenated transition IDs. Empty path identities are endpoint-specific. Mismatched endpoints fail. These are the finite path-category laws of the representation, not a new linguistic theorem.

Structural signatures (`snad-signature/2`) retain ordered unit feature values; identity equivalence classes across roles; frame equivalence classes; indexed transition kinds; and punctuation-frame depths. Identities are canonically ordered by their full occurrence patterns across units and roles, making signatures invariant under injective identity renaming. Referents form sets: their order and repeated declarations do not matter. They omit lexical content, source IDs, evidence quality, timestamps, and names. Equality means equality under this restricted representation, never semantic equivalence. The selected unit segmentation remains a modeling choice. Version 2 fixes the earlier order-sensitive reference ranking.

The three perturbations (`drop-features`, `reverse-units`, `mask-speakers`) are complete deterministic operators. The required integer seed is recorded with `stochastic: false`; it does not pretend to select random drops. Input and unit identities survive, and inputs remain unchanged.

Grammar induction memorizes ordered transition-kind symbols such as `person+number`, using a deterministic prefix trie. It accepts exactly the finite training sequence set, including an empty sequence only when observed. Lexical rephrasing with the same symbol sequence is accepted; unobserved prefixes and sequences are rejected. It is a baseline empirical regular-language representation with no generalization or universal grammar claim. `trainingSignature` is a canonical descriptor, not a cryptographic hash. Grammar acceptance validates the stored states and signature against the recorded training sequences.

Topology components and cycle rank use the underlying undirected multigraph: `cycleRank = E − V + C`. Isolated vertices count. Density counts unique directed non-self edges over `V(V−1)`; mean out-degree retains edge multiplicity. These quantities are graph summaries, not evidence for physical or semantic topology.

## Extensible adapters

```ts
import { analyze, type LanguageAdapter } from 'snad-core';

const adapter: LanguageAdapter<{ id: string; text: string }> = {
  id: 'plain-text/1',
  adapt: value => ({
    id: value.id,
    source: { id: value.id, kind: 'plain-text' },
    units: [{ id: `${value.id}:unit:0`, text: value.text, features: {} }],
  }),
};
const result = analyze(adapter.adapt({ id: 'example:1', text: 'Unannotated text' }));
```

Adapters supply evidence explicitly and preserve language-specific text. Core algorithms remain independent of corpus, language, service credentials, and network access. Analyses and input snapshots share no mutable objects; replay never depends on wall-clock time or global mutable state.
