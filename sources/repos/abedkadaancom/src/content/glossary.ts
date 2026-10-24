// The glossary as a contextual semantic field: a graph of terms, each with one
// or more senses attributed to a domain, cross-links, and computable bridges
// between senses where an exact computation connects them.

import type { DivisionId, Epistemic } from './types';
import { analyse, mat, fmtVec } from '../math/matrix';
import { SYSTEMS } from '../math/numberSystems';
import { analyseInterval, PITCH_NAMES } from '../math/music';
import { startFold, foldAll } from '../math/fold';
import { project } from '../math/paths';

export type Domain = DivisionId | 'campus' | 'observatory' | 'everyday';

export const DOMAIN_LABELS: Record<Domain, string> = {
  foundations: 'Foundations of Computation',
  relational: 'Relational & Generative Mathematics',
  languages: 'Programmable Languages',
  geometry: 'Geometry & Representation',
  acoustic: 'Acoustic Sciences',
  worlds: 'Computational Worlds',
  campus: 'Campus (the university itself)',
  observatory: 'The Observatory',
  everyday: 'Everyday usage',
};

export interface Sense {
  domain: Domain;
  text: string;
  status: Epistemic;
  topic?: string;
}

export interface Term {
  id: string;
  term: string;
  senses: Sense[];
  related: string[];
  bridges?: string[];
}

export interface Bridge {
  id: string;
  title: string;
  between: [Domain, Domain];
  explanation: string;
  inputLabel: string;
  defaultInput: string;
  run(input: string): string[];
}

const s = (domain: Domain, text: string, status: Epistemic = 'established', topic?: string): Sense => ({ domain, text, status, topic });

export const TERMS: Term[] = [
  { id: 'image', term: 'image', related: ['kernel', 'preimage', 'projection', 'rank', 'Imagistratum'], bridges: ['image-camera', 'image-zenith'], senses: [
    s('geometry', 'The set of outputs a map can reach: im f = {f(x)}. For a matrix, its column space.', 'established', 'image-kernel'),
    s('foundations', 'For c ↦ b·c, the image is the set of a for which a / b has at least one answer. 1/0 fails because 1 ∉ im(c ↦ 0·c).', 'house', 'numerical-grammars'),
    s('everyday', 'A picture or photograph: in mathematical terms, the image of a scene under a camera map, then sampled into pixels.', 'established', 'computational-photography'),
    s('observatory', 'A sky chart is the image of the celestial sphere under a projection onto the page or screen; the zenith map has the whole sky as its image.', 'established', 'celestial-geometry'),
  ] },
  { id: 'kernel', term: 'kernel', related: ['image', 'preimage', 'rank', 'quotient'], bridges: ['kernel-division'], senses: [
    s('geometry', 'ker A = {x : Ax = 0}: everything a linear map sends to zero, and so everything it forgets.', 'established', 'image-kernel'),
    s('foundations', 'For c ↦ b·c, the kernel decides uniqueness: if it is larger than {0}, a / b has many answers or none. 0/0 is a kernel failure.', 'house', 'numerical-grammars'),
    s('acoustic', 'The frequencies a sampling process cannot distinguish from others: aliasing is the sampling map’s kernel at work.', 'established', 'sound-signals'),
    s('everyday', 'In image processing, a “kernel” is also the small matrix of weights in a convolution filter. That is a different, unrelated sense.', 'established', 'computational-photography'),
  ] },
  { id: 'preimage', term: 'preimage', related: ['image', 'kernel'], senses: [
    s('geometry', 'f⁻¹(y) = {x : f(x) = y}. For a linear map: empty, one point, or x₀ + ker A.', 'established', 'image-kernel'),
    s('observatory', 'The preimage of one pixel of a sky photograph is a ray: every star along that line of sight.', 'established', 'projective-camera'),
  ] },
  { id: 'projection', term: 'projection', related: ['image', 'kernel', 'chart', 'substrate'], bridges: ['projection-chart'], senses: [
    s('geometry', 'A linear map P with P² = P; its kernel is what it forgets.', 'established', 'rank-nullity'),
    s('observatory', 'A map projection: a chart from the sphere to the plane, with declared distortions.', 'established', 'chart-correspondences'),
    s('foundations', 'In SubstrateIO, a map from a state space to a representation space, studied for what it preserves and identifies.', 'house', 'substrate-theory'),
  ] },
  { id: 'rank', term: 'rank', related: ['image', 'kernel'], senses: [
    s('geometry', 'dim im A: the number of independent directions that survive a linear map.', 'established', 'rank-nullity'),
    s('everyday', 'A position in an ordering. PageRank (CGT Chapters 15–16) is a ranking computed from a stationary distribution, not a matrix rank.', 'established'),
  ] },
  { id: 'Imagistratum', term: 'Imagistratum', related: ['image', 'kernel', 'projection'], senses: [s('geometry', 'The layered record of images and growing kernels along a chain of maps.', 'house', 'imagistratum')] },
  { id: 'grammar', term: 'grammar', related: ['word', 'admissibility', 'derivation', 'parser'], senses: [
    s('relational', 'A finite set of rewriting rules generating a language (Chomsky).', 'established', 'generative-grammars'),
    s('foundations', 'An operational grammar G = (Σ, 𝔄, ⟦·⟧, ℒ): the moves a structure admits, with their meaning and an admissibility language.', 'house', 'operational-grammar'),
    s('acoustic', 'In Phonogrammatica, rules for how acoustic events may follow and overlap.', 'house', 'phonogrammatica'),
    s('worlds', 'The lexical grammar from which campus residents compose their lines.', 'house', 'agent-grammars'),
  ] },
  { id: 'word', term: 'word', related: ['alphabet', 'monoid', 'path'], senses: [
    s('relational', 'A finite sequence of letters; the elements of the free monoid Σ*.', 'established', 'alphabets-words'),
    s('foundations', 'An operation expression: a sequence of moves to be checked and resolved.', 'house', 'operational-grammar'),
    s('observatory', 'A path word: the sequence of quantized turns along a street.', 'house', 'curvature'),
  ] },
  { id: 'fold', term: 'fold', related: ['Plicastratum', 'recursion', 'grammar'], bridges: ['fold-fold'], senses: [
    s('relational', 'Plicastratum fold: replace a repeated digram by a new glyph and record the rule. Unfold reverses it exactly.', 'house', 'plicastratum'),
    s('relational', 'Functional-programming fold (catamorphism): consume a list by replacing its constructors with a function and a value.', 'established', 'recursive-folds'),
    s('everyday', 'A crease: bending a surface onto itself. Paper folding preserves lengths; Plicastratum folding preserves the word.', 'established'),
  ] },
  { id: 'Plicastratum', term: 'Plicastratum', related: ['fold', 'alphabet tower'], senses: [s('relational', 'The stratified sequence of words and rules produced by successive folds.', 'house', 'plicastratum')] },
  { id: 'address', term: 'address', related: ['numeral', 'operation', 'channel'], bridges: ['address-heap'], senses: [
    s('languages', 'A URI: a word in the RFC 3986 grammar locating a resource.', 'established', 'uri-grammar'),
    s('languages', 'A grammatical address: the shortlex-least move word reaching an element from a root (CGT-DEF-006).', 'house', 'addressable-forms'),
    s('observatory', 'A postal address, which a geocoder may turn into approximate coordinates (with stated provider and precision).', 'established'),
  ] },
  { id: 'transition', term: 'transition', related: ['state', 'run', 'machine'], senses: [
    s('foundations', 'A labelled step s —a→ t of a transition system.', 'established', 'transition-systems'),
    s('foundations', 'In SubstrateIO, a state transformation whose trace is recorded and projected.', 'house', 'substrate-theory'),
    s('campus', 'A scene transition: the camera’s move between campus locations, with optional sound damping.', 'mythology'),
  ] },
  { id: 'state', term: 'state', related: ['transition', 'machine'], senses: [
    s('foundations', 'An element of a transition system’s state set.', 'established', 'transition-systems'),
    s('languages', 'The current node of a typed machine, which determines which operations are admissible.', 'established', 'typed-machines'),
  ] },
  { id: 'path', term: 'path', related: ['word', 'graph', 'signature', 'topology'], senses: [
    s('foundations', 'A walk with no repeated vertex.', 'established', 'graph-theory'),
    s('observatory', 'A street path: a polyline from map data, read as a word of turns.', 'established', 'curvature'),
    s('geometry', 'A continuous map [0, 1] → X; two with the same ends may or may not be homotopic.', 'established', 'topology'),
  ] },
  { id: 'signature', term: 'signature', related: ['path', 'word'], senses: [
    s('observatory', 'A path signature: turn word, relative segment lengths and junction degrees of a street path.', 'house', 'curvature'),
    s('foundations', 'A move signature: the alphabet Σ of an operational grammar.', 'established', 'operational-grammar'),
    s('languages', 'A type signature: the argument and result types of an operation.', 'established', 'types-as-admissibility'),
  ] },
  { id: 'orbit', term: 'orbit', related: ['interval', 'generator', 'closure'], bridges: ['orbit-interval'], senses: [
    s('acoustic', 'The pitch classes visited by repeatedly stepping by one interval; 12 / gcd(12, k) of them.', 'established', 'interval-geometry'),
    s('relational', 'The set {gⁿ·x} reached by a group element acting repeatedly: the closure of a seed under one relation.', 'established', 'relational-generativity'),
    s('observatory', 'The path of a body around another under gravity. Unrelated to the group-theory sense except in name.', 'established'),
  ] },
  { id: 'interval', term: 'interval', related: ['pitch', 'orbit', 'ratio'], senses: [
    s('acoustic', 'The distance between two pitches: a frequency ratio, or k semitones in ℤ/12.', 'established', 'interval-geometry'),
    s('everyday', 'A set of real numbers between two endpoints, such as [0, 1].', 'established'),
  ] },
  { id: 'phase', term: 'phase', related: ['signal', 'interval'], senses: [
    s('acoustic', 'Where in its cycle a sinusoid is: an element of ℝ/2πℤ.', 'established', 'phase'),
    s('observatory', 'The Moon’s phase: its ecliptic longitude minus the Sun’s, 0° new, 180° full.', 'established'),
  ] },
  { id: 'frame', term: 'frame', related: ['tensor', 'zenith'], senses: [
    s('geometry', 'A choice of basis and origin; coordinates are relative to it.', 'established', 'spatial-tensors'),
    s('observatory', 'A celestial reference frame: J2000 equatorial, equator of date, or the observer’s horizon.', 'established', 'celestial-geometry'),
    s('acoustic', 'One window of samples in a short-time Fourier transform.', 'established', 'time-frequency'),
  ] },
  { id: 'chart', term: 'chart', related: ['projection', 'map'], senses: [
    s('geometry', 'A homeomorphism from part of a surface to part of the plane.', 'established', 'chart-correspondences'),
    s('observatory', 'A star chart: the sky drawn under a declared projection.', 'established', 'celestial-geometry'),
  ] },
  { id: 'map', term: 'map', related: ['chart', 'path', 'graph'], senses: [
    s('geometry', 'A function between sets or spaces.', 'established', 'image-kernel'),
    s('worlds', 'A world map: a graph of places and weighted routes.', 'established', 'maps-navigation'),
  ] },
  { id: 'constellation', term: 'constellation', related: ['portal', 'zenith'], senses: [
    s('observatory', 'One of the 88 IAU regions of the sky. Real, conventional, and not computed here.', 'established', 'celestial-geometry'),
    s('campus', 'A campus constellation: an authored line drawn between real stars to mark a computed correspondence (for example, the zenith stars of two linked places). It is fiction drawn on real positions.', 'mythology'),
  ] },
  { id: 'portal', term: 'portal', related: ['constellation', 'path', 'topology'], senses: [
    s('campus', 'A fictional doorway in the courtyard that appears when two path signatures correspond. It visualizes a computation; it is not a claim of physical connection.', 'mythology', 'topology'),
  ] },
  { id: 'zenith', term: 'zenith', related: ['frame', 'constellation'], bridges: ['image-zenith'], senses: [s('observatory', 'The point straight overhead: δ = latitude, α = local sidereal time.', 'established', 'celestial-geometry')] },
  { id: 'Matrix Loom', term: 'Matrix Loom', related: ['matrix', 'compilation', 'composition'], senses: [s('languages', 'An assignment of matrices to operations so that a program weaves into one product.', 'house', 'matrix-loom')] },
  { id: 'World Loom', term: 'World Loom', related: ['rule', 'seed', 'automaton'], senses: [s('worlds', 'A world generated row by row by a local rule from a seed, with a reading map to features.', 'house', 'world-loom')] },
  { id: 'Ingrammatica', term: 'Ingrammatica', related: ['admissibility', 'grammar'], senses: [s('relational', 'The study of the words a grammar rejects, and of their minimal certificates of rejection.', 'house', 'ingrammatica')] },
  { id: 'Phonogrammatica', term: 'Phonogrammatica', related: ['grammar', 'spectrum'], senses: [s('acoustic', 'An operational grammar of acoustic events on the time–frequency plane.', 'house', 'phonogrammatica')] },
  { id: 'BORNE', term: 'BORNE', related: ['DAG', 'causal'], senses: [s('worlds', 'Birth dependencies between world facts, forming a DAG.', 'house', 'borne')] },
  { id: 'DAG', term: 'DAG', related: ['BORNE', 'graph'], senses: [s('worlds', 'A directed acyclic graph; it admits a topological order.', 'established', 'borne')] },
  { id: 'causal', term: 'causal', related: ['BORNE', 'DAG'], senses: [s('worlds', 'Concerning cause and effect; a causal graph encodes assumptions as a DAG (Pearl).', 'established', 'borne')] },
  { id: 'GLM', term: 'GLM', related: ['LGM'], senses: [s('worlds', 'Gaming Language Model: a language model used inside a game.', 'house', 'glm-lgm')] },
  { id: 'LGM', term: 'LGM', related: ['GLM', 'grammar'], senses: [s('worlds', 'Language Gaming Model: a game whose rules are a grammar.', 'house', 'glm-lgm')] },
  { id: 'admissibility', term: 'admissibility', related: ['realizability', 'grammar', 'Ingrammatica'], senses: [
    s('foundations', 'Membership of a word in the admissibility language ℒ, independent of the structure.', 'house', 'operational-grammar'),
    s('languages', 'Type-correctness: whether an operation is allowed in the current state or type context.', 'established', 'types-as-admissibility'),
  ] },
  { id: 'realizability', term: 'realizability', related: ['admissibility', 'semantics'], senses: [s('foundations', 'A word is realizable at x when its relational meaning from x is non-empty.', 'house', 'operational-grammar')] },
  { id: 'semantics', term: 'semantics', related: ['realizability', 'grammar'], senses: [s('foundations', 'What an expression denotes in a structure, kept separate from its syntax and its cost.', 'established', 'operational-grammar')] },
  { id: 'admission', term: 'admission', related: ['witness', 'admissibility'], senses: [s('relational', 'Constructive admission: membership established together with a checkable witness.', 'house', 'constructive-admission')] },
  { id: 'witness', term: 'witness', related: ['admission'], senses: [s('relational', 'Data that certifies a claim and can be checked independently, e.g. a factorization.', 'established', 'constructive-admission')] },
  { id: 'agent', term: 'agent', related: ['simulation', 'emergence'], senses: [s('worlds', 'An entity with state, perception and a policy for its next action.', 'established', 'agent-grammars')] },
  { id: 'alphabet', term: 'alphabet', related: ['word', 'alphabet tower'], senses: [s('relational', 'A finite non-empty set of symbols.', 'established', 'alphabets-words')] },
  { id: 'alphabet tower', term: 'alphabet tower', related: ['alphabet', 'Plicastratum'], senses: [s('relational', 'A sequence of alphabets with expansion maps from each level to words of the level below.', 'house', 'alphabet-towers')] },
  { id: 'automaton', term: 'automaton', related: ['regular language', 'state'], senses: [
    s('foundations', 'A finite-state machine that accepts or rejects words.', 'established', 'finite-automata'),
    s('worlds', 'A cellular automaton: a grid of cells updated by a local rule.', 'established', 'cellular-automata'),
  ] },
  { id: 'channel', term: 'channel', related: ['operation', 'address'], senses: [
    s('languages', 'An operation channel: a path for typed operations from a finite vocabulary.', 'house', 'seurl'),
    s('acoustic', 'An audio channel: one signal of a multichannel recording (left, right).', 'established'),
  ] },
  { id: 'closure', term: 'closure', related: ['generator', 'orbit'], senses: [s('relational', 'The smallest set containing a seed and closed under given operations.', 'established', 'relational-generativity')] },
  { id: 'compilation', term: 'compilation', related: ['Matrix Loom', 'composition', 'monoid'], senses: [s('languages', 'Turning a word of operations into one constant-size operation with the same meaning.', 'house', 'compilation')] },
  { id: 'complexity', term: 'complexity', related: ['cost'], senses: [s('foundations', 'The resources an algorithm or problem needs, as a function of input size, on a stated machine model.', 'established', 'complexity')] },
  { id: 'composition', term: 'composition', related: ['monoid', 'Matrix Loom'], senses: [s('languages', 'Applying one operation after another: (g ∘ f)(x) = g(f(x)). Associative, generally not commutative.', 'established', 'symbolic-composition'), s('acoustic', 'A piece of music; generative composition makes one from rules.', 'established', 'generative-composition')] },
  { id: 'cost', term: 'cost', related: ['complexity'], senses: [s('foundations', 'A cost profile: build time, space, query time, update time and output size, on a stated machine.', 'house', 'complexity')] },
  { id: 'curvature', term: 'curvature', related: ['path', 'signature'], senses: [s('geometry', 'How fast a curve turns; for a polyline, its signed turn angles.', 'established', 'curvature')] },
  { id: 'degree', term: 'degree', related: ['graph'], senses: [s('foundations', 'The number of edges at a vertex.', 'established', 'graph-theory'), s('everyday', 'A unit of angle, 1/360 of a turn.', 'established')] },
  { id: 'derivation', term: 'derivation', related: ['grammar', 'witness'], senses: [s('relational', 'A sequence of rewrites from the start symbol to a word.', 'established', 'generative-grammars')] },
  { id: 'emergence', term: 'emergence', related: ['agent', 'simulation'], senses: [s('worlds', 'A population-level pattern not encoded in any single agent’s rule.', 'established', 'simulated-populations')] },
  { id: 'equivalence class', term: 'equivalence class', related: ['quotient', 'kernel'], senses: [s('foundations', 'The set of elements equivalent to a given one; classes partition the set.', 'established', 'equivalence-classes')] },
  { id: 'frequency', term: 'frequency', related: ['pitch', 'spectrum'], senses: [s('acoustic', 'Cycles per second (Hz) of a periodic signal.', 'established', 'pitch-frequency')] },
  { id: 'generator', term: 'generator', related: ['closure', 'orbit', 'seed'], senses: [s('relational', 'An element from which a structure is reached by its operations.', 'established', 'relational-generativity'), s('worlds', 'A seeded pseudo-random number generator.', 'established', 'procedural-environments')] },
  { id: 'graph', term: 'graph', related: ['path', 'degree', 'DAG'], senses: [s('foundations', 'Vertices and edges.', 'established', 'graph-theory')] },
  { id: 'machine', term: 'machine', related: ['state', 'automaton'], senses: [s('languages', 'A typed machine: a state machine that refuses inadmissible operations.', 'established', 'typed-machines'), s('foundations', 'A machine model (word RAM) against which costs are stated.', 'established', 'complexity')] },
  { id: 'matrix', term: 'matrix', related: ['image', 'kernel', 'Matrix Loom'], senses: [s('geometry', 'A rectangular array representing a linear map in chosen bases.', 'established', 'image-kernel')] },
  { id: 'mode', term: 'mode', related: ['rotation'], senses: [s('acoustic', 'A rotation of a scale’s step pattern.', 'established', 'modal-cyclic')] },
  { id: 'monoid', term: 'monoid', related: ['word', 'composition'], senses: [s('relational', 'A set with an associative operation and identity; Σ* is the free one.', 'established', 'alphabets-words')] },
  { id: 'numeral', term: 'numeral', related: ['address', 'word'], senses: [s('foundations', 'A word over digits denoting a value; in a digit grammar, a program x ↦ b·x + d.', 'house', 'numerical-grammars')] },
  { id: 'operation', term: 'operation', related: ['channel', 'transition'], senses: [s('languages', 'A named, typed action on a resource, admissible in some states.', 'established', 'purl')] },
  { id: 'parser', term: 'parser', related: ['grammar'], senses: [s('languages', 'A program that decides membership in a grammar’s language and builds a parse tree.', 'established', 'grammars-as-programs')] },
  { id: 'perturbation', term: 'perturbation', related: ['kernel'], senses: [s('foundations', 'A small change to an input or state, studied for how it propagates.', 'established', 'perturbation')] },
  { id: 'pitch', term: 'pitch', related: ['frequency', 'interval'], senses: [s('acoustic', 'The perceived height of a sound; for pitch classes, an element of ℤ/12.', 'established', 'pitch-frequency')] },
  { id: 'procedural', term: 'procedural', related: ['seed'], senses: [s('worlds', 'Generated by an algorithm rather than authored by hand.', 'established', 'procedural-environments')] },
  { id: 'provenance', term: 'provenance', related: ['witness'], senses: [s('languages', 'The recorded origin and history of a resource or claim.', 'established', 'purl')] },
  { id: 'quotient', term: 'quotient', related: ['equivalence class', 'kernel'], senses: [s('foundations', 'The set of equivalence classes; also the answer c of a / b when it is unique.', 'established', 'equivalence-classes')] },
  { id: 'ratio', term: 'ratio', related: ['interval'], senses: [s('acoustic', 'A frequency ratio such as 3/2 for a just perfect fifth.', 'established', 'tuning')] },
  { id: 'recursion', term: 'recursion', related: ['fold'], senses: [s('relational', 'Definition of a function by its values on smaller arguments.', 'established', 'recursive-folds')] },
  { id: 'regular language', term: 'regular language', related: ['automaton'], senses: [s('foundations', 'A language accepted by some finite automaton.', 'established', 'finite-automata')] },
  { id: 'rendering', term: 'rendering', related: ['image'], senses: [s('geometry', 'Computing an image of a scene by approximating the rendering equation.', 'established', 'rendering-mathematics')] },
  { id: 'rewriting', term: 'rewriting', related: ['grammar'], senses: [s('relational', 'Replacing a part of a word or graph according to a rule.', 'established', 'compositional-forms')] },
  { id: 'rotation', term: 'rotation', related: ['mode', 'matrix'], senses: [s('relational', 'Moving a word’s first letter to the end.', 'established', 'modal-cyclic'), s('geometry', 'An orthogonal map with determinant 1.', 'established', 'spatial-tensors')] },
  { id: 'rule', term: 'rule', related: ['World Loom', 'automaton'], senses: [s('worlds', 'A cellular automaton’s local update, numbered 0–255.', 'established', 'cellular-automata')] },
  { id: 'run', term: 'run', related: ['transition'], senses: [s('foundations', 'A sequence of states following a word’s transitions.', 'established', 'transition-systems')] },
  { id: 'sampling', term: 'sampling', related: ['signal', 'kernel'], senses: [s('acoustic', 'Recording a signal’s value at regular times.', 'established', 'sound-signals')] },
  { id: 'seed', term: 'seed', related: ['generator', 'World Loom'], senses: [s('worlds', 'The initial value of a generator or the first row of a loom.', 'established', 'world-loom')] },
  { id: 'signal', term: 'signal', related: ['sampling'], senses: [s('acoustic', 'A function of time, e.g. pressure.', 'established', 'sound-signals')] },
  { id: 'simulation', term: 'simulation', related: ['world model'], senses: [s('worlds', 'Executing a model. Its results are SIMULATED, not OBSERVED.', 'established', 'world-models')] },
  { id: 'spectrum', term: 'spectrum', related: ['frequency'], senses: [s('acoustic', 'The amplitudes and phases of a signal’s sinusoidal components.', 'established', 'fourier')] },
  { id: 'substrate', term: 'substrate', related: ['transition', 'projection'], senses: [s('foundations', 'A state space with its transitions, as studied by SubstrateIO.', 'house', 'substrate-theory')] },
  { id: 'synthesis', term: 'synthesis', related: ['spectrum'], senses: [s('acoustic', 'Generating sound from a model.', 'established', 'synthesis')] },
  { id: 'tensor', term: 'tensor', related: ['frame'], senses: [s('geometry', 'An object whose coordinates change by a fixed rule under change of frame.', 'established', 'spatial-tensors')] },
  { id: 'topology', term: 'topology', related: ['path', 'portal'], senses: [s('geometry', 'The study of properties preserved by continuous deformation.', 'established', 'topology')] },
  { id: 'type', term: 'type', related: ['admissibility'], senses: [s('languages', 'A classification of phrases by the values they compute.', 'established', 'types-as-admissibility')] },
  { id: 'window', term: 'window', related: ['frame', 'spectrum'], senses: [s('acoustic', 'A tapering function selecting a short segment of a signal.', 'established', 'time-frequency')] },
  { id: 'world model', term: 'world model', related: ['simulation'], senses: [s('worlds', 'A model predicting how a world changes under actions.', 'established', 'world-models')] },
  { id: 'harness', term: 'harness', related: ['Harness Master', 'Harnesser'], senses: [
    s('campus', 'The One-Day Harness: a guided, self-paced day across the six divisions that ends in six personal volumes. Not a degree or credential.', 'mythology'),
    s('everyday', 'In software, a test harness: code that runs other code under controlled conditions.', 'established'),
  ] },
  { id: 'Harness Master', term: 'Harness Master', related: ['harness', 'Harnesser'], senses: [s('campus', 'The university’s guide role: an instructor-guide who helps a visitor learn and make something. Campus HMs are fictional characters; human HM sessions are requests, not bookings.', 'mythology')] },
  { id: 'Harnesser', term: 'Harnesser', related: ['harness', 'Harness Master'], senses: [s('campus', 'A visitor who has entered the harness. A participatory role, not a rank.', 'mythology')] },
  { id: 'specimen volume', term: 'specimen volume', related: ['procedural'], senses: [s('campus', 'A generated preview book in the Library, combining real registry topics. Labelled “Specimen Volume / Preview”; never a participant’s book.', 'mythology')] },
  { id: 'Haq Roots', term: 'Haq Roots', related: [], senses: [s('campus', 'The university’s invented name for its theme, “the root of truth”. A brand name; no linguistic derivation is claimed.', 'mythology')] },
];

export const BRIDGES: Bridge[] = [
  {
    id: 'image-camera',
    title: 'Linear image ↔ photograph',
    between: ['geometry', 'everyday'],
    explanation: 'A pinhole camera with P = [I | 0] sends a homogeneous point (X, Y, Z, 1) to (X, Y, Z) ≃ (X/Z, Y/Z). Its kernel is the camera centre (0, 0, 0, 1). Enter a 3D point.',
    inputLabel: 'X, Y, Z',
    defaultInput: '2, 1, 4',
    run(input) {
      const [X, Y, Z] = input.split(',').map((v) => Number(v.trim()));
      if (![X, Y, Z].every((v) => Number.isFinite(v))) return ['Enter three numbers.'];
      const A = analyse(mat([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]));
      const lines = [`rank P = ${A.rank}; ker P = span{(${fmtVec(A.kernel[0]!)})}: the camera centre has no image.`];
      if (Z === 0) lines.push('Z = 0: the point lies on the camera’s principal plane; its image is a point at infinity (x, y, 0).');
      else lines.push(`image point: (${X! / Z!}, ${Y! / Z!}) on the sensor plane. Every point λ·(${X}, ${Y}, ${Z}) shares it: the preimage of this pixel is a ray.`);
      return lines;
    },
  },
  {
    id: 'image-zenith',
    title: 'Image ↔ sky: the zenith map',
    between: ['geometry', 'observatory'],
    explanation: 'Z(φ, λ, t) = (LST, φ). Its image is the whole celestial sphere over a day; at a fixed instant, latitude φ sets the zenith declination exactly. Enter a latitude.',
    inputLabel: 'latitude (°)',
    defaultInput: '51.48',
    run(input) {
      const lat = Number(input);
      if (!Number.isFinite(lat) || lat < -90 || lat > 90) return ['Latitude must be between −90 and 90.'];
      return [`zenith declination δ = ${lat.toFixed(2)}°`, 'zenith right ascension = local sidereal time (needs longitude and time; see the Observatory).', 'declared loss: height, terrain, and which of the many places along a latitude circle produced it.'];
    },
  },
  {
    id: 'kernel-division',
    title: 'Kernel ↔ division by zero',
    between: ['geometry', 'foundations'],
    explanation: 'Multiplication by b in ℤ/6 is a linear-like map c ↦ b·c. Its kernel decides whether a / b is unique. Enter b in 0…5.',
    inputLabel: 'b',
    defaultInput: '2',
    run(input) {
      const sys = SYSTEMS.Z6;
      const b = sys.parse(input);
      if (b === null) return ['Enter an integer.'];
      const m = sys.multiplicationMap(b);
      return [`image of c ↦ ${b}·c: ${m.image}`, `kernel: ${m.kernel}`, m.injective ? 'injective: every a in the image has a unique quotient a / b.' : `not injective: a / ${b} is either impossible (a outside the image) or has ${m.kernelSet!.length} answers.`];
    },
  },
  {
    id: 'orbit-interval',
    title: 'Group orbit ↔ musical interval',
    between: ['relational', 'acoustic'],
    explanation: 'The orbit of C under +k in ℤ/12. Enter k.',
    inputLabel: 'k (semitones)',
    defaultInput: '7',
    run(input) {
      const k = Number(input);
      if (!Number.isInteger(k)) return ['Enter an integer.'];
      const a = analyseInterval(k);
      return [`${a.name}: orbit ${a.orbit.map((p) => PITCH_NAMES[p]).join(' → ')} (${a.orbitLength} classes)`, `gcd(12, ${a.k}) = ${a.gcd}; star polygon ${a.starPolygon}`];
    },
  },
  {
    id: 'fold-fold',
    title: 'Plicastratum fold ↔ functional fold',
    between: ['relational', 'relational'],
    explanation: 'Two senses of fold on one digit word: the functional fold computes its value (Horner); the Plicastratum fold compresses its symbols. Enter decimal digits.',
    inputLabel: 'digits',
    defaultInput: '121212',
    run(input) {
      const d = input.replace(/\D/g, '');
      if (!d) return ['Enter some digits.'];
      const value = [...d].reduce((x, c) => x * 10n + BigInt(c), 0n);
      const f = foldAll(startFold(d));
      return [`functional fold (λx d. 10x + d): ${value}`, `Plicastratum fold: ${f.rules.map((r) => `${r.glyph} → ${r.left}${r.right}`).join(', ') || '(single symbol)'}; root ${f.current.join('')}`, 'One fold consumes the word into a value; the other keeps the word, reorganized.'];
    },
  },
  {
    id: 'address-heap',
    title: 'URL path ↔ grammatical address',
    between: ['languages', 'languages'],
    explanation: 'Read a path of L and R segments as a binary-tree address; the heap numeration computes its node number. Enter e.g. /R/L/R.',
    inputLabel: 'path',
    defaultInput: '/R/L/R',
    run(input) {
      const segs = input.split('/').filter(Boolean).map((x) => x.toUpperCase());
      if (segs.some((x) => x !== 'L' && x !== 'R')) return ['Use only L and R segments.'];
      const bits = segs.map((x) => (x === 'L' ? '0' : '1')).join('');
      const n = parseInt('1' + bits, 2);
      return [`address word ${bits || 'ε'}; heap number int("1${bits}", 2) = ${n}`, `parent ${Math.floor(n / 2)}, children ${2 * n} and ${2 * n + 1}: navigation is arithmetic.`];
    },
  },
  {
    id: 'projection-chart',
    title: 'Linear projection ↔ map projection',
    between: ['geometry', 'observatory'],
    explanation: 'The equirectangular chart is linear in (λ, φ) once the scale cos φ₀ is fixed. Enter two lon,lat points to get local metre offsets.',
    inputLabel: 'lon1,lat1; lon2,lat2',
    defaultInput: '-0.0015,51.4778; 0.0005,51.4769',
    run(input) {
      const pts = input.split(';').map((p) => p.split(',').map((v) => Number(v.trim())) as [number, number]);
      if (pts.length !== 2 || pts.flat().some((v) => !Number.isFinite(v))) return ['Enter two points as lon,lat; lon,lat.'];
      const [a, b] = project(pts);
      const dx = b![0] - a![0];
      const dy = b![1] - a![1];
      return [`offset: ${dx.toFixed(1)} m east, ${dy.toFixed(1)} m north; distance ${Math.hypot(dx, dy).toFixed(1)} m`, 'declared loss: curvature of the Earth (negligible under a few km) and height.'];
    },
  },
];

const termIndex = new Map(TERMS.map((t) => [t.id.toLowerCase(), t]));
export function findTerm(id: string): Term | undefined {
  return termIndex.get(id.toLowerCase());
}
export function bridge(id: string): Bridge | undefined {
  return BRIDGES.find((b) => b.id === id);
}
export function termSlug(id: string): string {
  return encodeURIComponent(id.toLowerCase().replace(/\s+/g, '-'));
}
export function termFromSlug(slug: string): Term | undefined {
  const k = decodeURIComponent(slug).replace(/-/g, ' ').toLowerCase();
  return TERMS.find((t) => t.id.toLowerCase() === k);
}
