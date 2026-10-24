/** Confidence grades evidence quality; it is never a probability of truth. */
export type EvidenceStatus = 'observed' | 'derived' | 'hypothesis' | 'interpretation';
export interface Evidence { id: string; status: EvidenceStatus; method: string; sourceId: string; note?: string; confidence?: number }
export interface Source { id: string; kind: string; title?: string; uri?: string; license?: string; revision?: string }
export interface Span { start: number; end: number }
export interface Token { id: string; text: string; span: Span }
export interface Features { person?: '1' | '2' | '3'; number?: 'singular' | 'dual' | 'plural'; tense?: string; aspect?: string; [key: string]: string | undefined }
export interface Identity { id: string; label?: string; status: 'known' | 'unknown' }
export interface Attribution { speaker: Identity; addressee: Identity; referents: Identity[]; narrator: Identity; frameId: string }
export interface Timestamp { start?: number; end?: number; uncertainty?: number; unit?: string; original?: string }
export interface InputUnit { id: string; text: string; span?: Span; features?: Features; attribution?: Partial<Attribution>; evidence?: Evidence[]; timestamp?: Timestamp }
export interface QuotationFrame { id: string; parentId: string | null; depth: number; unitId: string; span: Span; cue: string; evidence: Evidence }
export interface DiscourseInput { id: string; source: Source; units: InputUnit[]; metadata?: Record<string, unknown> }
export interface AnalyzedUnit extends InputUnit { tokens: Token[]; features: Features; attribution: Attribution; evidence: Evidence[] }
export type TransitionKind = 'person' | 'number' | 'tense' | 'aspect' | 'speaker' | 'addressee' | 'referents' | 'narrator' | 'frame';
export interface Transition { id: string; from: string; to: string; kinds: TransitionKind[]; evidence: Evidence[]; confidence: number; confidenceMeaning: 'uncalibrated-evidence-quality'; lexicalContinuity: number; attributionChange: boolean }
export interface ProvenanceNode { id: string; kind: 'source' | 'unit' | 'transition' | 'frame'; evidence?: Evidence[] }
export interface ProvenanceEdge { from: string; to: string; relation: 'contains' | 'derived-from' }
export interface ProvenanceGraph { nodes: ProvenanceNode[]; edges: ProvenanceEdge[] }
export interface Topology { vertices: number; edges: number; components: number; cycleRank: number; density: number; meanOutDegree: number }
export interface Analysis { schemaVersion: 'snad/1'; id: string; input: DiscourseInput; units: AnalyzedUnit[]; transitions: Transition[]; frames: QuotationFrame[]; provenance: ProvenanceGraph; topology: Topology; uncertainty: { unitId: string; field: string; reason: string }[]; status: 'analyzed'; methods: string[] }
export interface AnalyzeOptions { quoteCues?: boolean }
export interface DialogueTurn { id?: string; text: string; speaker?: string | Identity; addressee?: string | Identity; referents?: (string | Identity)[]; narrator?: string | Identity; features?: Features; timestamp?: Timestamp; evidence?: Evidence[] }
export interface QuranRecord { id?: string; surah: number; ayah: number; text: string; source?: string | Source; features?: Features[]; morphology?: { tokenIndex: number; features: Features; evidence: Evidence[] }[] }
export interface QuranLocus { id: string; surah: number; ayah: number }
export interface Morphism { from: string; to: string; path: string[] }
export interface Motif { signature: string; count: number; occurrences: { analysisId: string; transitionIds: string[] }[] }
export interface LanguageAdapter<T> { id: string; adapt(value: T): DiscourseInput }
export interface Perturbation { kind: 'drop-features' | 'reverse-units' | 'mask-speakers'; seed: number }
export interface GrammarState { id: string; accepting: boolean; transitions: Record<string, string> }
export interface InducedGrammar { schemaVersion: 'snad-grammar/1'; definition: 'finite-observed-transition-language'; alphabet: string[]; startState: string; states: GrammarState[]; trainingSequences: string[][]; trainingSignature: string }
