# Candidate atom atlas for exactly 62 University topics

**Critical:** this is a proposal mapping the current source-backed 62 topic identifiers to candidate capability interfaces. It is NOT 62 built atoms or 62 verified theories. Source topic identities remain owned by Substrate University; Q-theories remain proposed overlays. Every `compiled_target` is taken from the previously authored QIA atlas and must be verified or rejected by Codex.

| Division | Topic ID | Subject | Proposed typed signature | Proposed backend |
|---|---|---|---|---|
| I | `transition-systems` | Transition systems | `State×Label->StateRelation` | `transition-engine` |
| I | `finite-automata` | Finite-state machines | `FiniteState×Symbol->FiniteState` | `dfa` |
| I | `operational-grammar` | Computational Grammar Theory | `OperationWord×Context->Admissibility×Realizability×Cost` | `typed-grammar` |
| I | `admissibility` | Admissibility | `Graph×Automaton->ProductGraph` | `product-automaton` |
| I | `substrate-theory` | Substrate Theory | `State×Perturbation->Observation` | `state-projection` |
| I | `perturbation` | Perturbation mathematics | `State×Delta->ChangedState` | `sensitivity` |
| I | `equivalence-classes` | Equivalence classes | `Carrier×Equivalence->Quotient` | `quotient-index` |
| I | `numerical-grammars` | Numerical grammars | `Numeral×Operator->PartialResult` | `arithmetic-ir` |
| I | `graph-theory` | Graph theory | `Vertices×Edges->Walks` | `graph-query` |
| I | `complexity` | Complexity | `Algorithm×InputFamily->CostBound` | `cost-model` |
| II | `alphabets-words` | Alphabets and words | `Alphabet->FreeMonoid` | `string-ir` |
| II | `generative-grammars` | Grammatical generation | `Grammar×Seed->Derivation` | `rewrite-engine` |
| II | `plicastratum` | Plicastratum | `Word×FoldRules->CompressedWord` | `reversible-fold` |
| II | `alphabet-towers` | Structured alphabets | `AlphabetLevel×Morphisms->RepresentationTower` | `tower-ir` |
| II | `ingrammatica` | Ingrammatica | `Grammar×RejectedWord->RefusalWitness` | `negative-parser` |
| II | `constructive-admission` | Constructive admission | `Candidate×ConstraintSet->Admission` | `constraint-solver` |
| II | `relational-generativity` | Relational Generativity | `Seed×Relations->ReachabilityClosure` | `fixed-point-engine` |
| II | `modal-cyclic` | Cyclic mathematics | `Modulus×Generator->Orbit` | `modular-orbit` |
| II | `recursive-folds` | Recursive folds and unfolding | `Algebra×RecursiveStructure->Fold` | `recursive-compiler` |
| II | `compositional-forms` | Compositional forms | `TypedPorts×RewriteRule->Composite` | `operad-ir` |
| III | `uri-grammar` | Addresses | `URIText->ParsedAddress` | `uri-parser` |
| III | `purl` | PURL | `Address×TypedOperation->ProgramAddress` | `purl-compiler` |
| III | `seurl` | SEURL | `Channel×Transition->ExecutableCommunication` | `seurl-runtime` |
| III | `typed-machines` | Typed machines | `State×Event×Guard->Transition` | `statechart` |
| III | `types-as-admissibility` | Type systems | `Expression×TypeEnv->Judgement` | `typechecker` |
| III | `compilation` | Compilation | `TypedAST->ExecutableOperator` | `backend-generator` |
| III | `matrix-loom` | Matrix Loom | `TypedMatrixWord->MatrixProduct` | `linear-compiler` |
| III | `addressable-forms` | Addressable computational forms | `Root×OperationalWord->Address` | `address-index` |
| III | `grammars-as-programs` | Grammars as programs | `TokenStream×Grammar->ParseForest` | `parser` |
| III | `symbolic-composition` | Symbolic composition | `TransformationWord->CompositeTransformation` | `transition-monoid` |
| IV | `image-kernel` | Images and kernels | `Map×Element->ImageFiber` | `fiber-solver` |
| IV | `imagistratum` | Imagistratum | `ProjectionChain->InformationLossTower` | `projection-ledger` |
| IV | `rank-nullity` | Projection loss | `LinearMap->Rank×Nullity` | `linear-algebra` |
| IV | `projective-camera` | Projective geometry | `Point3×Camera->PixelOrUndefined` | `camera-projection` |
| IV | `topology` | Topology | `Space×Topology->OpenSets` | `topology-checker` |
| IV | `curvature` | Differential geometry | `ParametricCurve->Curvature` | `geometry-kernel` |
| IV | `spatial-tensors` | Spatial tensors | `Tensor×FrameChange->TensorComponents` | `tensor-backend` |
| IV | `computational-photography` | Computational photography | `RadianceField×CameraSensor->SampledImage` | `renderer-ir` |
| IV | `celestial-geometry` | Celestial geometry | `Ephemeris×Frame×Time->Coordinates` | `celestial-transform` |
| IV | `chart-correspondences` | Charts | `CoordinateCharts×Overlap->TransitionMap` | `atlas-solver` |
| IV | `rendering-mathematics` | Rendering mathematics | `Geometry×BRDF×Lighting->RadianceEstimate` | `render-graph` |
| IV | `invisible-sensing` | AWRM / invisible sensing | `Measurements×ForwardModel->LatentStateSet` | `inverse-sensing` |
| V | `sound-signals` | Sound and sampling | `Waveform×SampleRate->Samples` | `audio-sampler` |
| V | `pitch-frequency` | Pitch | `Frequency->LogPitch` | `pitch-map` |
| V | `interval-geometry` | Interval geometry | `PitchClass×Step->Orbit` | `pitch-orbit` |
| V | `tuning` | Tuning | `Ratio×TuningSystem->Frequency` | `tuning-map` |
| V | `fourier` | Spectral processing | `FiniteSignal->Spectrum` | `fft` |
| V | `time-frequency` | Time–frequency representations | `Waveform×Window×Hop->STFT` | `stft` |
| V | `synthesis` | Sound synthesis | `Oscillators×Parameters->Waveform` | `audio-synth` |
| V | `phase` | Phase processing | `ComplexAmplitude×Time->Phase` | `phase-operator` |
| V | `phonogrammatica` | Phonogrammatica | `AcousticEvents×Grammar->AdmissibleSoundForms` | `acoustic-grammar` |
| V | `generative-composition` | Generative composition | `MusicalGrammar×Seed->EventSequence` | `music-scheduler` |
| VI | `cellular-automata` | Cellular automata | `LocalRule×Neighborhood->NextCell` | `ca-kernel` |
| VI | `world-loom` | World Loom | `Seed×LocalRules->WorldRows` | `world-generator` |
| VI | `agent-grammars` | Agent grammars | `AgentState×Perception×Policy->Action` | `agent-runtime` |
| VI | `procedural-environments` | Procedural environments | `WorldGrammar×Seed->SceneGraph` | `scene-generator` |
| VI | `world-models` | Generative world models | `State×Action×Model->PredictedStateDistribution` | `predictive-model` |
| VI | `glm-lgm` | Gaming Language Models and Language Gaming Models | `GameGrammar×LanguageState->GameAction` | `game-language-runtime` |
| VI | `borne` | BORNE causal dependencies | `DependencyDAG×FactSet->EnabledEvents` | `dependency-scheduler` |
| VI | `maps-navigation` | World maps and navigation | `Map×CostMetric->Route` | `routing` |
| VI | `simulated-populations` | Simulated populations | `AgentPopulation×Rules->PopulationTrajectory` | `population-simulator` |
| VI | `homeless-dark` | HOMELESS / Dark | `GameScenario×ValidatedRules->SimulationPlan` | `scene-ir` |

## Materialization rule

Each candidate atom is only promoted after its *specific source implementation* is located, imported through approved license and adapter, its type/effect/loss contract established, and independent tests are produced. Generic capability descriptions are not executable implementations.
