# Grammar in Ciphers — Formal Research Ledger v0.1

## Status and definitions

This is a **new mathematical and literary research program**, not an established decryption of the Qur'an, nor a claim about authorial intent, historical identities, or new canonical Qur'anic readings. Textually grounded observations are distinguished from generated symbolic readings called **جمالة الصفر (jamālat aṣ-ṣifr)**. Quranic verses are never modified.

- **C** = the 14-symbol cipher alphabet: `ا ح ر س ص ط ع ق ك ل م ن ه ي`.
- **I** = the 14-symbol in-cipher alphabet, the complement in the *28-base-letter* Arabic inventory: `ب ت ث ج خ د ذ ز ش ض ظ غ ف و`.
- **A = C ⊔ I**, `C ∩ I = ∅`, `|A| = 28`. The sets are partitions of **base letters**, not of Unicode code points, phonemes, roots or graphemes; all require separate maps.
- **Sites S**: 29 ordered surah openings (indexed positions, **not** 29 different cipher letters).
- **Units U**: 30 verse-situated opening expressions, including `42:1=حم` and `42:2=عسق` as separate expressions. `|U|=30`.
- **Types T**: 14 distinct verse-unit sequences; 78 letter-token occurrences across the 30 units. Note the conventional surah-level combined form `حم عسق` is one of 14 surah-level configurations; do not conflate the two grouping schemes.
- **Occurrence**: one ordered `(sura, aya, offset, layer)` record with a canonical source and a normalization profile.
- **Composition**: concatenate cipher letters; does not, by itself, generate a semantic interpretation.
- **In-cipher**: the 14 complementary base letters, not 'meaninglessness' or 'inorganic', and not an implicit absence from the body of the Quran.
- **Grammar / in-grammar / anti-grammar**: distinct *house-defined* grammars; in-grammar means internal complement and is not automatically equivalent to formal-language complementation `Σ* ∖ L(G)`. Anti-grammar additionally requires a declared negation, constraint, or counter-construction semantics.

## Proposed computable apparatus

Let `Σ28=C ⊔ I`, `V` be a typed carrier of Qur'anic locations, graphemes, lexemes, lemmas, morphological features, entities, conceptual landmarks, and ordinal positions; `E` a typed, provenance-bearing edge set. `G=(Σ,V,⟦·⟧,L)` is an operational grammar under CGT-DEF-003. A `bridge` is a path whose every edge carries location, operation, evidence type, confidence, and counterexamples; cross-domain transitions are separate from claims of same identity.

Let `u=(site,sura,ayah,word-span,graphemes)` be a verse-level unit; `normalize_p(raw)` is a *versioned* representation map. **Never edit the source string in place.**

Candidate operators:

| Operator | Input -> output | Rule / falsifier | Status |
|---|---|---|---|
| `SUBSTITUTE(i,a→b)` | `يس -> طس` | Position-sensitive letter replacement `ي -> ط` at position 1; test presence in inventory; *ya* is an author-instituted equality/substitution marker, not normal Arabic identity | Author convention |
| `EXTEND(suffix)` | `طس -> طسم` | Append م to unit, independently witnessed at 26:1 and 28:1; no historical derivation implied | Text-verified morphology of strings |
| `SHARE(letter)` | `يس ~ عسق` | Intersection contains س; quantify specificity against 14-type baseline | Observation |
| `SECOND_AYAH` | `حم | عسق` | Ordered two-verse sequence only at 42:1–2 among inventory | Observation |
| `COUNT_FORWARD` | `3->4; 5->6; 7->8` | Count youths and ordinal of dog as **statements reported in 18:22**, not established youth headcount | Textual enumerations |
| `COUNT_REVERSE` | `8->7; 6->5; 4->3` | Reverse the reported (youths,dog-position) pairs; an invertible indexing operation, not a new Qur'anic claim | Author operation |
| `INSERT_THIRD(t1,t2,tm)` | `(t1,t2) -> (t1,tm,t2)` | Require explicit t1<tm<t2; synthetically illustrate 'third between two dates'; 36:14 gives no calendar dating | Counterfactual simulation |
| `CIPHER_MASK` | token -> `{C,I,other}^n` | Binary base-letter partition; preserve hamza, ة, alif and article analyses separately | Deterministic |
| `FOLD/UNFOLD` | path -> abbreviated plate -> path | require inverse round trip for lossless form | CGT/University analogy |
| `PROJECTION/IMAGE/KERNEL` | graph -> projection and lost info | prove which details erased (identity vs shared lexeme), never invert a lossy map as fact | Standard math packaging |
| `TOWER/HUWAMIM` | 40..46 and 42:2 | 7 repeated حم sites, one secondary عسق; tower is a visual graph, no claim physical 7-story tower | Observation + metaphor |
| `PLACE/HABITAT` | ant/bee/youth -> spatial motif | distinguish valley, home, mountain, cave, city, Egypt, land; not all same place or geological claim | Author bridge |
| `SOURCE_COMPARE` | canon / qiraat variant | compare with explicit text edition, narration, verse numbering and source | Philology |

### Letter-boundary audit (base-letter normalizer only)

- `النمل → ا ل ن م ل` = entirely **C**, referenced 27:18.
- `النحل → ا ل ن ح ل` = entirely **C**, referenced 16:68.
- `صنع → ص ن ع` = entirely **C**, referenced 27:88.
- `الفتية → ا ل ف ت ي ة` = **C/C/I/I/C/orthographic-extra** under strict 28-letter inventory (do not convert `ة` silently).
- `صنوان → ص ن و ا ن` includes **I** letter `و`; 13:4.
- `الجبال → ا ل ج ب ا ل` crosses C/I; 16:68.
- Note: the article `الـ` is composed of cipher letters and can strongly inflate the rate of cipher-only tokens. Compare both with and without proclitic segmentation. A label `cipher-only` is orthographic, not a semantic or statistical finding.

## Canonical count invariants

`|S|=29`, `|U|=30`, `|T|=14`, `|C|=14`, `|I|=14`, `C∩I=∅`, `C∪I=Σ28`, `sum(len(u) for u in U)=78`, `count_Sin=5`, `Sin_ayah1=4`, `Sin_ayah2=1`, `Hawamim=7`, `42:2=عسق`, and `42:1=حم`.

The five **Sin** appearances are `26:1 طسم`, `27:1 طس`, `28:1 طسم`, `36:1 يس`, `42:2 عسق`. Thus there are **four distinct Sin-bearing unit types**, five instances, **four first-verse** appearances, **one second-verse** appearance; mixing these denominators creates false assertions.

## Interpretive cautions

1. `36:14` messengers in a town and `18:13–22` youths are different narratives. The bridge is enumeration / speech grammar, not factual identity. The third messenger's historical date is not specified. The '36 and 18 eras' example is *invented illustration* only.
2. `18:18` says the dog was at the threshold, and "if you looked upon them" refers to the youths. **Do not state the youths were literally invisible**. The dog-as-observable-marker theory is an author-proposed perspective model.
3. `18:19` includes both a question of **duration** (`كم لبثتم`) and the response `ربكم أعلم بما لبثتم`; replacing duration with location as the verse's literal meaning is incorrect. A separate spatial interpretation can be explored and labelled.
4. `18:22` explicitly reports opinions: 3+4, 5+6 and 7+8; it does **not** establish an actual final headcount. Its phrase `ما يعلمهم إلا قليل` cautions about certainty.
5. `15:87` 'seven oft-repeated' is **not** established by the passage as a direct reference to Hawamim 40–46. Keep as a numerical comparison only.
6. `6:143–144` references eight pairs among livestock, not the dog or youths; an 8-bridge is an abstract ordinal coincidence until strengthened.
7. 42:2 is a standalone verse of letters in the Hafs/Kufan division used by the repository. Preserve numbering scheme metadata across qiraat.
8. The text of any given ayah must be obtained verbatim from the locked canonical source, not from transcription or from this ledger's shorthand.
9. `صفر` as a cipher/equality research motif is a protected author term. Similarity to 'cipher' does not establish an etymology for scriptural words, and `جِمالَتٌ صُفْر` at 77:33 is a color/imagery verse, not a code manifesto.
10. Distinguish **co-occurrence, lexical overlap, conceptual analogy, inferential claim, and editorial conjecture**. Unrelated locations and figures must not be unified without evidence.

## Three explicit evaluation baselines

1. **Lexical masks**: observed cipher-only fraction among Qur'an words, controlling for word length, stopwords/articles, tokenization, and letter frequencies; compare Monte Carlo samples preserving letter unigrams and empirical word lengths; report effect sizes and uncertainty.
2. **Verse network**: topology measured against degree-preserving rewired graphs and lexeme-frequency-matched edge controls. Correct for searching thousands of candidates; hold out predetermined surahs to test generalization.
3. **Generative transitions**: build a full typed operator grammar then measure novel, valid (inventory-attested), and false-positive transitions; compare to random substitutions and untyped adjacency baselines. Every alleged discovery must survive canonical text verification and an adversarial counterexample search.

## Provenance / coverage

Every record stores `claim_id, source_repo, repo_ref, canonical_edition, sura, ayah, token_offsets, normalization_profile, claim_class, rule_id, text_witness, derivation, baseline, falsifier, limitations, human_review_status`. The full Qur'an coverage ledger is one row per canonical ayah (expected Kufan 6236; recompute from the loaded corpus, never hardcode blindly); **no auto-generated connection is a theological reading by default**.
