# POLYIA Interchange Contract PIC/0.2 — proposal, not yet implemented

## 1. Objects and identities

`Alphabet` := typed set (or effectively generated family) of terminals or structured cells with declared equivalence and coordinates. Not necessarily phonetic or linear.

`Grammar` := `(syntax, admit, refusal, denotationDomain, scope, version)`; `admit` may be partial/undecidable for a general formalism and therefore needs a restricted executable fragment or a bounded `UNKNOWN` status.

`Machine` := `M=(S,E,I,O,δ,λ,s₀,Inv,Ref,Eff,Budget)` where `δ⊆S×E×S` is transition relation, `λ` maps admitted transition histories to typed outputs, `Inv` preservation obligations, `Ref` typed refusals (including budget and missing evidence), `Eff` authorized effects. Infinite state spaces and symbolic states are allowed. A machine must declare its termination/replay conditions rather than inherit them from this signature.

`Pack` := versioned contextual bundle of grammars, corpora, transducers, evidence and negative grammars scoped to a `VarietyID` or scientific domain. Multiple packs may coexist for one language or subject.

`Evidence` := `(claim, method, source, locator, source_hash, witness_kind, witnessed_under, independence, scope, status)`; `confidence` and `semantic distance` are distinct quantities. Raw test success ≠ formal proof. A source's own results are not an independent witness.

`CapabilityAtom` := `(id,version,Input,Output,MachineOrGrammar,Effects,Constraints,Cost,Provenance,Tests,Reproducibility,Dependencies)`.

`GenerationReceipt` := `(artifact, typed_derivation, source_versions, grammar_versions, machine_trace, invariant_checks, refusals, unresolved, replay_manifest, hash)`.

## 2. Compositional laws

For `A : X ↝ Y` and `B : Y' ↝ Z`, `B∘A` is admitted only with an explicit, checked adapter `a:Y→Y'`; neither identical names nor shared phonetic resemblance suffice. Side effects compose only if permission policies and sequencing rules admit them. Partial composition returns explicit refusal or an unresolved port, not a fabricated filler.

**Identity:** for admitted type X, identity machine `id_X` must satisfy `id_Y∘A ≈ A ≈ A∘id_X` under a *specified observable equivalence*, not necessarily byte identity.

**Associativity:** for admitted A,B,C, `C∘(B∘A) ≈ (C∘B)∘A` must be shown, including effects and errors. If not, the compiler must preserve grouping and register a non-associative composition formalism.

**Parallel:** independent machines may compose as synchronous product, asynchronous communicating actors, or monoidal tensor only after the scheduling semantics and memory-consistency model are chosen. Fork/join and feedback are NOT generic graph cycles; cycles must establish a guarded fixed-point/termination/fairness contract.

**Negative grammar:** `refutes(x)`, `not_admissible_under(x, scope)`, `not_observed_in_dataset(x)` and `unknown(x)` are four different outcomes. A dataset-derived absence has source-scope and cannot become a universal impossibility rule.

**Invariance:** a generator `V_θ` is admissible for required invariants Inv iff each tested output satisfies `∀i∈Inv, i(V_θ(x))=i(x)` under specified scope. Lexical changes preserving sense require sense evidence; spelling changes are not enough.

**Loss:** each projection `p:X→Y` stores the preimage ambiguity or non-recovery condition. `H(X|p(X))` requires a declared distribution; `log₂(|fibre|)` is a combinatorial bound under equiprobable candidates, not automatically empirical entropy.

## 3. Metageneration (source → compiler + machine)

A `GrammarCard` is accepted only if its grammar formalism, semantics, operand types, witnesses and effects are specified. `Genesis(Card)` produces `(recognizer, generator, typed_IR, optional compiler_lowering, machine_definition, proof_obligations, witnesses)`.

The output of a **generator of generators** is NOT certified merely by emitting source code. Require:

1. Compilation/source checks; types, effects, negative grammar, and valid ports.
2. Interpreter-versus-compiled observational equivalence on declared domain.
3. Adversarial failure cases; budget-safe refusal and exact required invariant checks.
4. Differential baseline against a human-written/scientific reference where legal.
5. Replay from pinned input hashes, seeds and grammar versions.
6. Independent witness or proof where a scientific correctness claim is made.

## 4. Proposed integrated generative stack

`requested_problem → typed_intake → domain/variety identity → sourced lexical and structural cards → negative grammar → semantic planning → bounded automata/transducer/rewriter composition → output surface realizer (optional small ML as proposal) → verifier → state-carried generation receipt`.

The source renderer may return original language/English/other forms while retaining all input-language evidence. It does NOT gain truth from phonetic correspondence, Latin/Greek etymology, Arabic rasm similarity, or metaphors borrowed from quantum mechanics.

## 5. First machine compatibility checks

- A word from an Indigenous language with no official orthography must allow an IPA/phonological record without inventing a writing alphabet.
- A polysemous Arabic root must return multiple qualified senses rather than a single assured Latinized pure function.
- A scientific symbol `O` (oxygen) is not a word-level phonetic transcript.
- An IUPAC name and molecular graph have an explicitly scoped bidirectional parser/generator; different valid names can map to the same structure.
- A Petri net or asynchronous actor system is not incorrectly coerced to a one-tape sequential DFA.
- A generated essay may legitimately state three topics are incomparable; it may still contrast them with cited facts.
- A linguistic pack’s `privative` feature carries `absent/replaced/contested/unknown` status and evidence, never inferred from missing data.
