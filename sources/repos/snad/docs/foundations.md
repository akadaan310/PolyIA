# Candidate mathematical foundations: source audit and limits

SNAD adopts established formal tools for explicit, testable discourse representations. It treats the three requested repositories as candidate implementations and research programs. None supplies independent evidence that a grammatical tag identifies a speaker or that a structural pattern has a theological meaning. This audit supports engineering choices and a narrow set of executable reconstructions; it makes no novelty claim.

## Actual repositories inspected

The owner repository listing was inspected through GitHub's authenticated read API. These were the exact matching repositories and commits checked out for source reading:

| Requested foundation | Repository and pinned commit | Actual code inspected | Useful scope |
|---|---|---|---|
| Computational Grammar Theory | [`akadaan310/computationalgrammartheory`](https://github.com/akadaan310/computationalgrammartheory/tree/bfe32fc37f7fa61d50da50ecd2aa7fa97c0dd5a1), `bfe32fc37f7fa61d50da50ecd2aa7fa97c0dd5a1` | `sdk/src/cgtsdk/grammar.py`, `automata.py`, `algorithms/automata.py`, `structures/graphs.py` | Separate admissible operation syntax, reference semantics and counted execution; regular-language-constrained graph reachability |
| Grammar in Numbers | [`akadaan310/grammarinnumbers`](https://github.com/akadaan310/grammarinnumbers/tree/2a94f8a6be686078a9dad88863be9aafc5e6379b), `2a94f8a6be686078a9dad88863be9aafc5e6379b` | `sdk/src/ginsdk/numerals.py`, `converse.py`, `expr.py` | Explicit domains, transition composition, and solution-set cardinality for partial/inverse operations |
| SubstrateIO | [`akadaan310/substrateIO`](https://github.com/akadaan310/substrateIO/tree/7ace119a544fc736f0d4ec1d72cded9dad0a83e3), `7ace119a544fc736f0d4ec1d72cded9dad0a83e3` | `substrate/core.py`, `graph.py`, `trace.py`, `projection.py`, `epistemic.py` | Explicit state/transition/event distinctions, projection compatibility, observational equivalence and evidence-status guards |

Each repository's literature review was also inspected. Their own reviews explicitly distinguish established mathematics, candidate presentations, unverified metadata and unread primary literature. Those caveats survive here. No LICENSE file was found in the tracked trees at these commits. SNAD cites the inspected ideas and executes read-only comparisons; it does not copy their implementation or claim a redistribution grant.

`evidence/foundations-audit.json` records per-file SHA-256 hashes and immutable source links. The sources remain read-only optional research inputs; the generic SDK runs independently.

### What the implementations actually do

CGT's `OperationalGrammar` checks an expression against an operation signature and optional DFA. It separately evaluates abstract reference semantics and counted concrete execution. `product_reach` searches a graph × automaton product. Its path closure code performs fixed-point reachability; these are computational constructions, not corpus-specific speaker inference.

GiN's digit grammar maps a digit `d` to the affine operation `x ↦ bx+d`. `Affine.then` composes those maps in execution order. `converse.py` distinguishes zero, one and multiple solutions instead of coercing them into a bare error. This is useful discipline for unresolved attribution, but an arithmetic affine map is not automatically a meaningful model of arbitrary discourse. A numeric signature must name its encoding, domain, collisions and retained observable.

SubstrateIO represents finite maps explicitly, computes functional-graph structure and general directed-graph SCCs, and records logical step indices separately from wall-clock execution time. Its `compatibility` test checks whether equal projected states stay equal after one transition. Its partition refinement finds a congruence relative to a specified observable. Its evidence guards prevent simulated/model executions from being promoted to physical observations; passing a guard does not prove a claim true.

## Typed transitions and composition

A useful abstract state is a tuple `(speaker, addressee, referents, narrator, frame, grammaticalFeatures, evidence)`. Unknown identity is a represented value. Grammatical person and actor identity occupy different fields. A reported utterance can change the active frame without resolving the identity of its speaker.

A directed transition from state `A` to state `B` is an edge `A → B` carrying its evidence and source locus. A path is composable with another path only when its endpoint equals the other's starting point under the explicitly chosen state equality. Empty paths provide identities; path concatenation is associative. These are the standard laws of the free path category of a directed graph. Calling a path a morphism adds no new theorem. If an implementation uses only IDs for endpoint equality, its law is an ID-level statement and says nothing by itself about discourse-reference equivalence.

Projection `P` from rich states to a smaller signature can support deterministic context transfer only if its chosen observable survives. For a transition function `f`, an induced function on projected states exists exactly when `P(x)=P(y)` implies `P(f(x))=P(f(y))`. This is the familiar congruence condition. The executable counterexample below demonstrates why equal signatures alone are insufficient. A proposed functor additionally has to preserve identities and composition; a visual resemblance or a function named `compose` does not establish those laws. Nondeterministic or uncertain analyses require relations or sets of possible states, and their equivalence criterion must be specified separately.

Nested quotation benefits from explicit frame ancestry and a stack discipline. A bounded frame-depth heuristic is a finite instrument. Unbounded matching quotation nesting needs a stronger account than an unqualified finite-state claim. Visibly pushdown languages provide relevant prior art when the input alphabet reliably identifies calls and returns. Whether a natural-language cue actually opens or closes a frame remains an empirical annotation question. [Alur and Madhusudan's author-hosted paper](https://www.cis.upenn.edu/~alur/Stoc04.pdf) gives the formal-language setting.

## Literature comparison

The following primary sources were checked at the publisher, standards body or author-hosted location. Abstract/metadata consultation is indicated explicitly; it is not a claim to have verified every proof.

| SNAD concern | Established source | Implication and reading limit |
|---|---|---|
| Grammar-associated semantic attributes | [Knuth, *Semantics of context-free languages* (1968)](https://link.springer.com/article/10.1007/BF01692511) | Attribute grammars already attach semantic information to grammatical derivations. Publisher metadata/abstract checked; complete proof audit not performed. |
| Formal-language restrictions on graph paths | [Barrett, Jacob and Marathe, *Formal-Language-Constrained Path Problems* (2000)](https://epubs.siam.org/doi/10.1137/S0097539798337716) | Constrained paths and graph × automaton reasoning are established. Publisher abstract/metadata checked. Bounds for walks must not be silently transferred to simple paths. |
| Typed attributed graph transformation | [Ehrig, Ehrig, Prange and Taentzer, *Fundamental Theory for Typed Attributed Graphs and Graph Transformation based on Adhesive HLR Categories* (2006)](https://journals.sagepub.com/doi/10.3233/FUN-2006-74103) | Typed graph rewriting has substantial prior theory. Publisher abstract/metadata checked. SNAD does not claim to implement double-pushout rewriting merely because it can edit a graph. |
| Category and functor laws | [Mac Lane, *Categories for the Working Mathematician*, publisher record](https://link.springer.com/book/10.1007/978-1-4757-4721-8) | Composition/identity preservation is an established mathematical obligation. Publisher description checked; no complete book proof audit. |
| Nested calls and returns | [Alur and Madhusudan, *Visibly Pushdown Languages* (2004)](https://www.cis.upenn.edu/~alur/Stoc04.pdf) | Structured nesting has an established automata model; discourse cue adequacy is a separate question. Author-hosted abstract/model context consulted. |
| Source, derivation and responsibility | [W3C, *PROV-DM*, Recommendation 30 April 2013](https://www.w3.org/TR/2013/REC-prov-dm-20130430/) | Entity/activity/agent and derivation distinctions support interoperable provenance. Core overview and record structure read. A local JSON evidence graph is not automatically PROV-conformant. |

These are comparison points, not evidence of a new grammar theory. Full primary-source proof comparison, external linguistic evaluation, and a systematic novelty search remain open work.

## Independent executable reconstructions

Run `python scripts/check-foundations.py --references ../references` with the three repositories checked out at the commits above. The script rejects another revision, imports source without writing bytecode or changing the checkouts, and records results in `evidence/foundations-audit.json`.

1. **Regular path query:** a four-vertex labelled graph under language `a b` yields only vertex `2`. Independently enumerated walks agree with CGT's product search. The search explores 3 product states, within the 12-state product bound.
2. **Numeric composition:** 675 checks compare GiN affine composition against an independently coded Horner evaluation, across all binary words of lengths 0–3 and three starting values. Converse classification also returns no solution for `1/0`, multiple solutions for `0/0`, and a unique solution for `6/3` over its stated rational domain.
3. **Projection counterexample and refinement:** with `f=[0,1,1,3]` and `P(x)=x mod 2`, states `0` and `2` have equal projections but their next projections are `0` and `1`. SubstrateIO correctly rejects compatibility and refines the partition. Its XOR transition encoding also reconstructs a five-state example when the initial state is retained.

These checks are small computational reproductions, with explicit baselines and a negative case. They do not constitute general proofs or evidence of semantic correctness on Qur'anic text.

## Research boundaries

Surface lexical continuity and attribution change form two separate axes. Their joint value can be an operational feature; it cannot validate a speaker intention. Likewise, matching numerical signatures establishes equality under that feature map only. A pair can share a coarse person/number contour while differing in frame depth, narrator, unresolved identity, source reliability or reference history.

Future proposed operators should supply their domain/codomain, partiality, identity/composition laws, preserved observables, provenance behavior, counterexamples and a comparison with a simpler baseline. For grammar induction, reported sample sizes must distinguish available text, usable features, evaluated transitions and manually validated labels. The complete corpus remains addressable when feature alignment fails. General dialogue fixtures must preserve original timestamps and uncertainty rather than borrowing corpus-specific assumptions.
