"""Source-reconciled 62-record Q-theory overlay. Does not modify the university registry."""
import json,pathlib
D={
'I|Foundations of Computation': '''transition-systems|Transition systems|established|State×Label->StateRelation|typed transitions compose|transition-engine
finite-automata|Finite-state machines|established|FiniteState×Symbol->FiniteState|acceptance agrees with DFA run|dfa
operational-grammar|Computational Grammar Theory|house|OperationWord×Context->Admissibility×Realizability×Cost|syntax and execution are separated|typed-grammar
admissibility|Admissibility|established|Graph×Automaton->ProductGraph|valid walks correspond to product paths|product-automaton
substrate-theory|Substrate Theory|house|State×Perturbation->Observation|declared observables preserved if claimed|state-projection
perturbation|Perturbation mathematics|established|State×Delta->ChangedState|bounded perturbation and sensitivity law stated|sensitivity
 equivalence-classes|Equivalence classes|established|Carrier×Equivalence->Quotient|reflexive symmetric transitive|quotient-index
numerical-grammars|Numerical grammars|house|Numeral×Operator->PartialResult|undefined operands have refusal witnesses|arithmetic-ir
graph-theory|Graph theory|established|Vertices×Edges->Walks|incidence and reachability preserved|graph-query
complexity|Complexity|established|Algorithm×InputFamily->CostBound|asymptotic model explicitly stated|cost-model''',
'II|Relational and Generative Mathematics': '''alphabets-words|Alphabets and words|established|Alphabet->FreeMonoid|concatenation associative with empty word|string-ir
generative-grammars|Grammatical generation|established|Grammar×Seed->Derivation|every output has derivation tree|rewrite-engine
plicastratum|Plicastratum|house|Word×FoldRules->CompressedWord|decode(encode(w))=w|reversible-fold
alphabet-towers|Structured alphabets|house|AlphabetLevel×Morphisms->RepresentationTower|explicit translation diagram|tower-ir
ingrammatica|Ingrammatica|house|Grammar×RejectedWord->RefusalWitness|minimal violation justified|negative-parser
constructive-admission|Constructive admission|house|Candidate×ConstraintSet->Admission|accepted objects satisfy constraints|constraint-solver
relational-generativity|Relational Generativity|house|Seed×Relations->ReachabilityClosure|closure is rule-derived only|fixed-point-engine
modal-cyclic|Cyclic mathematics|established|Modulus×Generator->Orbit|orbit length n/gcd(n,k)|modular-orbit
recursive-folds|Recursive folds and unfolding|established|Algebra×RecursiveStructure->Fold|catamorphism law under stated algebra|recursive-compiler
compositional-forms|Compositional forms|established|TypedPorts×RewriteRule->Composite|boundary ports remain well-typed|operad-ir''',
'III|Programmable Computational Languages': '''uri-grammar|Addresses|established|URIText->ParsedAddress|roundtrip subject to normalized/non-normalized codec|uri-parser
purl|PURL|house|Address×TypedOperation->ProgramAddress|addressed operation dispatch typed|purl-compiler
seurl|SEURL|house|Channel×Transition->ExecutableCommunication|channel contract preserved|seurl-runtime
typed-machines|Typed machines|established|State×Event×Guard->Transition|only guarded transitions fire|statechart
types-as-admissibility|Type systems|established|Expression×TypeEnv->Judgement|preservation or explicit rejection|typechecker
compilation|Compilation|house|TypedAST->ExecutableOperator|semantics-preservation test required|backend-generator
matrix-loom|Matrix Loom|house|TypedMatrixWord->MatrixProduct|composition ordering checked|linear-compiler
addressable-forms|Addressable computational forms|house|Root×OperationalWord->Address|resolve(address) witnesses target|address-index
grammars-as-programs|Grammars as programs|established|TokenStream×Grammar->ParseForest|every parse has grammar derivation|parser
symbolic-composition|Symbolic composition|established|TransformationWord->CompositeTransformation|associativity where defined|transition-monoid''',
'IV|Geometry, Physics, and Representation': '''image-kernel|Images and kernels|established|Map×Element->ImageFiber|preimages computed over declared domain|fiber-solver
imagistratum|Imagistratum|house|ProjectionChain->InformationLossTower|all projections carry loss disclosures|projection-ledger
rank-nullity|Projection loss|established|LinearMap->Rank×Nullity|rank+nullity=dim(domain)|linear-algebra
projective-camera|Projective geometry|established|Point3×Camera->PixelOrUndefined|projective normalization with visible-domain guard|camera-projection
topology|Topology|established|Space×Topology->OpenSets|open-set axioms verified|topology-checker
curvature|Differential geometry|established|ParametricCurve->Curvature|coordinate invariance where claimed|geometry-kernel
spatial-tensors|Spatial tensors|established|Tensor×FrameChange->TensorComponents|transformation law respects variance|tensor-backend
computational-photography|Computational photography|established|RadianceField×CameraSensor->SampledImage|exposure/sampling error disclosed|renderer-ir
celestial-geometry|Celestial geometry|established|Ephemeris×Frame×Time->Coordinates|frame/time specification explicit|celestial-transform
chart-correspondences|Charts|established|CoordinateCharts×Overlap->TransitionMap|overlap chart maps compose|atlas-solver
rendering-mathematics|Rendering mathematics|established|Geometry×BRDF×Lighting->RadianceEstimate|energy constraints and error budget stated|render-graph
invisible-sensing|AWRM / invisible sensing|application|Measurements×ForwardModel->LatentStateSet|ambiguity and uncertainty retained|inverse-sensing''',
'V|Acoustic and Generative Sciences': '''sound-signals|Sound and sampling|established|Waveform×SampleRate->Samples|Nyquist assumptions and aliasing recorded|audio-sampler
pitch-frequency|Pitch|established|Frequency->LogPitch|positive frequency domain enforced|pitch-map
interval-geometry|Interval geometry|established|PitchClass×Step->Orbit|cyclic modular invariant|pitch-orbit
tuning|Tuning|established|Ratio×TuningSystem->Frequency|frequency ratios traceable|tuning-map
fourier|Spectral processing|established|FiniteSignal->Spectrum|inverse DFT roundtrip under convention|fft
 time-frequency|Time–frequency representations|established|Waveform×Window×Hop->STFT|window/hop reconstruction assumptions explicit|stft
synthesis|Sound synthesis|established|Oscillators×Parameters->Waveform|sample-rate and amplitude bounds|audio-synth
phase|Phase processing|established|ComplexAmplitude×Time->Phase|phase modulo 2pi|phase-operator
phonogrammatica|Phonogrammatica|house|AcousticEvents×Grammar->AdmissibleSoundForms|time-frequency admissibility checked|acoustic-grammar
generative-composition|Generative composition|established|MusicalGrammar×Seed->EventSequence|timing and scale constraints checked|music-scheduler''',
'VI|Computational Worlds and Emergence': '''cellular-automata|Cellular automata|established|LocalRule×Neighborhood->NextCell|locality and rule determinism if asserted|ca-kernel
world-loom|World Loom|house|Seed×LocalRules->WorldRows|every emitted row derives from previous|world-generator
agent-grammars|Agent grammars|established|AgentState×Perception×Policy->Action|action guards and traceability|agent-runtime
procedural-environments|Procedural environments|established|WorldGrammar×Seed->SceneGraph|scene satisfies authored generation constraints|scene-generator
world-models|Generative world models|established|State×Action×Model->PredictedStateDistribution|uncertainty calibrated on benchmark|predictive-model
glm-lgm|Gaming Language Models and Language Gaming Models|house|GameGrammar×LanguageState->GameAction|typed surface/game distinction|game-language-runtime
borne|BORNE causal dependencies|house|DependencyDAG×FactSet->EnabledEvents|causal/dependency prerequisites non-cyclic when asserted|dependency-scheduler
maps-navigation|World maps and navigation|established|Map×CostMetric->Route|routing cost nonnegative for Dijkstra|routing
simulated-populations|Simulated populations|established|AgentPopulation×Rules->PopulationTrajectory|statistical conclusions separated from individual simulation|population-simulator
homeless-dark|HOMELESS / Dark|application|GameScenario×ValidatedRules->SimulationPlan|application claims require validation|scene-ir'''
}
records=[]
for k,v in D.items():
 no,division=k.split('|')
 for raw in v.splitlines():
  cols=raw.strip().split('|')
  assert len(cols)==6,(k,cols)
  tid,subject,status,signature,invariant,target=cols
  records.append({'q_theory_id':f'QIA-{no}-{tid}','source_topic_id':tid,'source_division':no,'source_division_name':division,'source_subject':subject,'source_status':status,'qia_status':'proposed typed overlay, not source theorem','signature':signature,'invariant_or_refusal':invariant,'compiled_target':target,'representation_layers':['exact-serialization','source-form','typed-semantics','proof-or-counterexample'],'field_family':{'I':'transition and proof field','II':'generativity and composition field','III':'address and compilation field','IV':'geometry and physical representation field','V':'signal and harmonic field','VI':'world and causal dynamics field'}[no]})
assert len(records)==62,len(records)
assert len(set(r['source_topic_id'] for r in records))==62
p=pathlib.Path(__file__).parent/'schemas'/'Q_THEORIES_62.json'
p.write_text(json.dumps({'schema':'QIA/QTHEORY/0.1','source_repository':'https://github.com/akadaan310/abedkadaancom','source_ref':'claude/new-session-xd8auu','generated_from':'source-verified topics registry (2026-10-21)','status':'proposed QIA research overlay, not university mutation','total':62,'theories':records},indent=2,ensure_ascii=False)+'\n')
print('Generated',len(records),'records:',p)
