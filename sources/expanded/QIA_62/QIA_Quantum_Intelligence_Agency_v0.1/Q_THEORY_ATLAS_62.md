# QIA/0.1 — All 62 Individual Q-Theory Contracts

**Source:** Substrate University source-verified registry, six active divisions; all Q-theory operators and targets below are **proposals**, not source-asserted capabilities. The original source statuses are preserved.

## Division I — Foundations of Computation (10)

### QI.01 — Transition systems (`transition-systems`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `State×Label->StateRelation`.
- **Invariant or refusal condition:** typed transitions compose.
- **Proposed compilation target:** `transition-engine`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.02 — Finite-state machines (`finite-automata`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `FiniteState×Symbol->FiniteState`.
- **Invariant or refusal condition:** acceptance agrees with DFA run.
- **Proposed compilation target:** `dfa`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.03 — Computational Grammar Theory (`operational-grammar`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `OperationWord×Context->Admissibility×Realizability×Cost`.
- **Invariant or refusal condition:** syntax and execution are separated.
- **Proposed compilation target:** `typed-grammar`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.04 — Admissibility (`admissibility`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Graph×Automaton->ProductGraph`.
- **Invariant or refusal condition:** valid walks correspond to product paths.
- **Proposed compilation target:** `product-automaton`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.05 — Substrate Theory (`substrate-theory`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `State×Perturbation->Observation`.
- **Invariant or refusal condition:** declared observables preserved if claimed.
- **Proposed compilation target:** `state-projection`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.06 — Perturbation mathematics (`perturbation`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `State×Delta->ChangedState`.
- **Invariant or refusal condition:** bounded perturbation and sensitivity law stated.
- **Proposed compilation target:** `sensitivity`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.07 — Equivalence classes (`equivalence-classes`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Carrier×Equivalence->Quotient`.
- **Invariant or refusal condition:** reflexive symmetric transitive.
- **Proposed compilation target:** `quotient-index`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.08 — Numerical grammars (`numerical-grammars`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Numeral×Operator->PartialResult`.
- **Invariant or refusal condition:** undefined operands have refusal witnesses.
- **Proposed compilation target:** `arithmetic-ir`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.09 — Graph theory (`graph-theory`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Vertices×Edges->Walks`.
- **Invariant or refusal condition:** incidence and reachability preserved.
- **Proposed compilation target:** `graph-query`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QI.10 — Complexity (`complexity`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Algorithm×InputFamily->CostBound`.
- **Invariant or refusal condition:** asymptotic model explicitly stated.
- **Proposed compilation target:** `cost-model`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

## Division II — Relational and Generative Mathematics (10)

### QII.01 — Alphabets and words (`alphabets-words`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Alphabet->FreeMonoid`.
- **Invariant or refusal condition:** concatenation associative with empty word.
- **Proposed compilation target:** `string-ir`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.02 — Grammatical generation (`generative-grammars`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Grammar×Seed->Derivation`.
- **Invariant or refusal condition:** every output has derivation tree.
- **Proposed compilation target:** `rewrite-engine`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.03 — Plicastratum (`plicastratum`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Word×FoldRules->CompressedWord`.
- **Invariant or refusal condition:** decode(encode(w))=w.
- **Proposed compilation target:** `reversible-fold`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.04 — Structured alphabets (`alphabet-towers`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `AlphabetLevel×Morphisms->RepresentationTower`.
- **Invariant or refusal condition:** explicit translation diagram.
- **Proposed compilation target:** `tower-ir`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.05 — Ingrammatica (`ingrammatica`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Grammar×RejectedWord->RefusalWitness`.
- **Invariant or refusal condition:** minimal violation justified.
- **Proposed compilation target:** `negative-parser`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.06 — Constructive admission (`constructive-admission`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Candidate×ConstraintSet->Admission`.
- **Invariant or refusal condition:** accepted objects satisfy constraints.
- **Proposed compilation target:** `constraint-solver`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.07 — Relational Generativity (`relational-generativity`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Seed×Relations->ReachabilityClosure`.
- **Invariant or refusal condition:** closure is rule-derived only.
- **Proposed compilation target:** `fixed-point-engine`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.08 — Cyclic mathematics (`modal-cyclic`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Modulus×Generator->Orbit`.
- **Invariant or refusal condition:** orbit length n/gcd(n,k).
- **Proposed compilation target:** `modular-orbit`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.09 — Recursive folds and unfolding (`recursive-folds`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Algebra×RecursiveStructure->Fold`.
- **Invariant or refusal condition:** catamorphism law under stated algebra.
- **Proposed compilation target:** `recursive-compiler`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QII.10 — Compositional forms (`compositional-forms`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `TypedPorts×RewriteRule->Composite`.
- **Invariant or refusal condition:** boundary ports remain well-typed.
- **Proposed compilation target:** `operad-ir`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

## Division III — Programmable Computational Languages (10)

### QIII.01 — Addresses (`uri-grammar`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `URIText->ParsedAddress`.
- **Invariant or refusal condition:** roundtrip subject to normalized/non-normalized codec.
- **Proposed compilation target:** `uri-parser`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.02 — PURL (`purl`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Address×TypedOperation->ProgramAddress`.
- **Invariant or refusal condition:** addressed operation dispatch typed.
- **Proposed compilation target:** `purl-compiler`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.03 — SEURL (`seurl`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Channel×Transition->ExecutableCommunication`.
- **Invariant or refusal condition:** channel contract preserved.
- **Proposed compilation target:** `seurl-runtime`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.04 — Typed machines (`typed-machines`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `State×Event×Guard->Transition`.
- **Invariant or refusal condition:** only guarded transitions fire.
- **Proposed compilation target:** `statechart`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.05 — Type systems (`types-as-admissibility`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Expression×TypeEnv->Judgement`.
- **Invariant or refusal condition:** preservation or explicit rejection.
- **Proposed compilation target:** `typechecker`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.06 — Compilation (`compilation`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `TypedAST->ExecutableOperator`.
- **Invariant or refusal condition:** semantics-preservation test required.
- **Proposed compilation target:** `backend-generator`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.07 — Matrix Loom (`matrix-loom`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `TypedMatrixWord->MatrixProduct`.
- **Invariant or refusal condition:** composition ordering checked.
- **Proposed compilation target:** `linear-compiler`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.08 — Addressable computational forms (`addressable-forms`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Root×OperationalWord->Address`.
- **Invariant or refusal condition:** resolve(address) witnesses target.
- **Proposed compilation target:** `address-index`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.09 — Grammars as programs (`grammars-as-programs`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `TokenStream×Grammar->ParseForest`.
- **Invariant or refusal condition:** every parse has grammar derivation.
- **Proposed compilation target:** `parser`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIII.10 — Symbolic composition (`symbolic-composition`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `TransformationWord->CompositeTransformation`.
- **Invariant or refusal condition:** associativity where defined.
- **Proposed compilation target:** `transition-monoid`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

## Division IV — Geometry, Physics, and Representation (12)

### QIV.01 — Images and kernels (`image-kernel`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Map×Element->ImageFiber`.
- **Invariant or refusal condition:** preimages computed over declared domain.
- **Proposed compilation target:** `fiber-solver`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.02 — Imagistratum (`imagistratum`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `ProjectionChain->InformationLossTower`.
- **Invariant or refusal condition:** all projections carry loss disclosures.
- **Proposed compilation target:** `projection-ledger`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.03 — Projection loss (`rank-nullity`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `LinearMap->Rank×Nullity`.
- **Invariant or refusal condition:** rank+nullity=dim(domain).
- **Proposed compilation target:** `linear-algebra`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.04 — Projective geometry (`projective-camera`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Point3×Camera->PixelOrUndefined`.
- **Invariant or refusal condition:** projective normalization with visible-domain guard.
- **Proposed compilation target:** `camera-projection`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.05 — Topology (`topology`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Space×Topology->OpenSets`.
- **Invariant or refusal condition:** open-set axioms verified.
- **Proposed compilation target:** `topology-checker`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.06 — Differential geometry (`curvature`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `ParametricCurve->Curvature`.
- **Invariant or refusal condition:** coordinate invariance where claimed.
- **Proposed compilation target:** `geometry-kernel`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.07 — Spatial tensors (`spatial-tensors`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Tensor×FrameChange->TensorComponents`.
- **Invariant or refusal condition:** transformation law respects variance.
- **Proposed compilation target:** `tensor-backend`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.08 — Computational photography (`computational-photography`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `RadianceField×CameraSensor->SampledImage`.
- **Invariant or refusal condition:** exposure/sampling error disclosed.
- **Proposed compilation target:** `renderer-ir`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.09 — Celestial geometry (`celestial-geometry`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Ephemeris×Frame×Time->Coordinates`.
- **Invariant or refusal condition:** frame/time specification explicit.
- **Proposed compilation target:** `celestial-transform`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.10 — Charts (`chart-correspondences`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `CoordinateCharts×Overlap->TransitionMap`.
- **Invariant or refusal condition:** overlap chart maps compose.
- **Proposed compilation target:** `atlas-solver`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.11 — Rendering mathematics (`rendering-mathematics`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Geometry×BRDF×Lighting->RadianceEstimate`.
- **Invariant or refusal condition:** energy constraints and error budget stated.
- **Proposed compilation target:** `render-graph`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QIV.12 — AWRM / invisible sensing (`invisible-sensing`)

- **Source status:** `application`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Measurements×ForwardModel->LatentStateSet`.
- **Invariant or refusal condition:** ambiguity and uncertainty retained.
- **Proposed compilation target:** `inverse-sensing`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

## Division V — Acoustic and Generative Sciences (10)

### QV.01 — Sound and sampling (`sound-signals`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Waveform×SampleRate->Samples`.
- **Invariant or refusal condition:** Nyquist assumptions and aliasing recorded.
- **Proposed compilation target:** `audio-sampler`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.02 — Pitch (`pitch-frequency`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Frequency->LogPitch`.
- **Invariant or refusal condition:** positive frequency domain enforced.
- **Proposed compilation target:** `pitch-map`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.03 — Interval geometry (`interval-geometry`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `PitchClass×Step->Orbit`.
- **Invariant or refusal condition:** cyclic modular invariant.
- **Proposed compilation target:** `pitch-orbit`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.04 — Tuning (`tuning`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Ratio×TuningSystem->Frequency`.
- **Invariant or refusal condition:** frequency ratios traceable.
- **Proposed compilation target:** `tuning-map`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.05 — Spectral processing (`fourier`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `FiniteSignal->Spectrum`.
- **Invariant or refusal condition:** inverse DFT roundtrip under convention.
- **Proposed compilation target:** `fft`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.06 — Time–frequency representations (`time-frequency`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Waveform×Window×Hop->STFT`.
- **Invariant or refusal condition:** window/hop reconstruction assumptions explicit.
- **Proposed compilation target:** `stft`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.07 — Sound synthesis (`synthesis`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Oscillators×Parameters->Waveform`.
- **Invariant or refusal condition:** sample-rate and amplitude bounds.
- **Proposed compilation target:** `audio-synth`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.08 — Phase processing (`phase`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `ComplexAmplitude×Time->Phase`.
- **Invariant or refusal condition:** phase modulo 2pi.
- **Proposed compilation target:** `phase-operator`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.09 — Phonogrammatica (`phonogrammatica`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `AcousticEvents×Grammar->AdmissibleSoundForms`.
- **Invariant or refusal condition:** time-frequency admissibility checked.
- **Proposed compilation target:** `acoustic-grammar`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QV.10 — Generative composition (`generative-composition`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `MusicalGrammar×Seed->EventSequence`.
- **Invariant or refusal condition:** timing and scale constraints checked.
- **Proposed compilation target:** `music-scheduler`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

## Division VI — Computational Worlds and Emergence (10)

### QVI.01 — Cellular automata (`cellular-automata`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `LocalRule×Neighborhood->NextCell`.
- **Invariant or refusal condition:** locality and rule determinism if asserted.
- **Proposed compilation target:** `ca-kernel`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.02 — World Loom (`world-loom`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Seed×LocalRules->WorldRows`.
- **Invariant or refusal condition:** every emitted row derives from previous.
- **Proposed compilation target:** `world-generator`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.03 — Agent grammars (`agent-grammars`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `AgentState×Perception×Policy->Action`.
- **Invariant or refusal condition:** action guards and traceability.
- **Proposed compilation target:** `agent-runtime`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.04 — Procedural environments (`procedural-environments`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `WorldGrammar×Seed->SceneGraph`.
- **Invariant or refusal condition:** scene satisfies authored generation constraints.
- **Proposed compilation target:** `scene-generator`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.05 — Generative world models (`world-models`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `State×Action×Model->PredictedStateDistribution`.
- **Invariant or refusal condition:** uncertainty calibrated on benchmark.
- **Proposed compilation target:** `predictive-model`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.06 — Gaming Language Models and Language Gaming Models (`glm-lgm`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `GameGrammar×LanguageState->GameAction`.
- **Invariant or refusal condition:** typed surface/game distinction.
- **Proposed compilation target:** `game-language-runtime`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.07 — BORNE causal dependencies (`borne`)

- **Source status:** `house`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `DependencyDAG×FactSet->EnabledEvents`.
- **Invariant or refusal condition:** causal/dependency prerequisites non-cyclic when asserted.
- **Proposed compilation target:** `dependency-scheduler`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.08 — World maps and navigation (`maps-navigation`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `Map×CostMetric->Route`.
- **Invariant or refusal condition:** routing cost nonnegative for Dijkstra.
- **Proposed compilation target:** `routing`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.09 — Simulated populations (`simulated-populations`)

- **Source status:** `established`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `AgentPopulation×Rules->PopulationTrajectory`.
- **Invariant or refusal condition:** statistical conclusions separated from individual simulation.
- **Proposed compilation target:** `population-simulator`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

### QVI.10 — HOMELESS / Dark (`homeless-dark`)

- **Source status:** `application`; QIA overlay status: `proposed`.
- **Sort/operation signature:** `GameScenario×ValidatedRules->SimulationPlan`.
- **Invariant or refusal condition:** application claims require validation.
- **Proposed compilation target:** `scene-ir`.
- **Q-unit factorization:** exact identity record → contextual type/sort and admitted input ports → operation law → witnessed output → measurement/exception; each refinement relative to observables and budget.
- **Verification stage:** needs an independently checked operator example and at least one rejection/counterexample before being promoted beyond proposed.

