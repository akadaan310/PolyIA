# Open Problems

Ordered roughly by how informative a solution would be for the program.

### GIN-OPEN-001 A grammar-class hierarchy of arithmetic operations
GIN-THM-005 separates operations a finite automaton can perform on numerals (successor, addition, comparison, multiplication and division by constants, reduction modulo constants) from those it cannot (multiplication). Place the remaining operations of this book — gcd, modular exponentiation with variable modulus, integer square root, base conversion — in a precise hierarchy (synchronous rational, rational, pushdown, linear-time, …) and relate the class to bit complexity. Much is known (Cobham 1969; Büchi; automatic structures); the task is to state the hierarchy for these operations with references and fill any gaps.

### GIN-OPEN-002 The cost of admissibility
Deciding whether a/b is admissible in ℤ means deciding b | a, which costs as much as dividing. In ℤ/n, deciding whether b is a unit costs a gcd. When is deciding admissibility asymptotically cheaper than computing the result, and when is it as hard? Is there a natural converse problem where admissibility is hard but computation, when admissible, is easy?

### GIN-OPEN-003 Repairs as universal constructions
GIN-DEF-017 lists seven repairs. Several are universal constructions: the Grothendieck group (extension for +), localization (division by a multiplicative set), completion, algebraic closure, quotient. Characterize which repairs are left adjoints, which are not (totalization, signalling), and whether the extension trilemma (GIN-THM-004) has a categorical statement.

### GIN-OPEN-004 Is re-association a distinct mechanism?
Make GIN-CONJ-001 precise: define when a speedup is "attributable to re-association" and decide whether M-ASSOC is distinct from CGT-THM-004's grammar-shape effect, or a special case of it (see CGT-OPEN-001, CGT-OPEN-007).

### GIN-OPEN-005 Literature debts
Primary sources not yet read in full: Carlström 2004 (exact wheel axioms), Bergstra & Tucker 2007, Knuth 1978 (carry propagation), Sorenson & Webster 2017 (ψ₁₃ value taken from secondary sources), the ARM Architecture Reference Manual SDIV pseudocode, Smullyan 1961 and Forslund 1995 (bijective numeration). Search specifically for prior statements of GIN-PROP-006 and of the pair-level form of GIN-THM-006.

### GIN-OPEN-006 Completeness of the four-layer outcome model
Does syntax · typing · semantics · execution capture the failure modes of other numeric systems: decimal floating point, posits/unums, interval arithmetic, arbitrary-precision libraries with rounding modes, exact real arithmetic, computer-algebra systems? Find a failure that does not fit.

### GIN-OPEN-007 A complete IEEE 754 reference
Extend `ginsdk.ieee` to all rounding-direction attributes, fused multiply–add, conversions, remainder, decimal formats, NaN payloads; validate against an established test suite and against more than one ISA (an AArch64 host would test before-rounding tininess).

### GIN-OPEN-008 Does the segment notation generalize?
GIN-REI-010 shows `a{I}b` is notation for a marked path. For a transition system in general, is there a useful "boundary/interior" notation for intervals between two states (posets, CGT trees, the Stern–Brocot tree of rationals) that supports a calculus (composition of segments, boundary operators) rather than display only?

### GIN-OPEN-009 Machine semantics on more hosts
Measure GIN-EXP-004 on AArch64 and RISC-V hardware (or faithful emulators), on Windows, and for more compilers and versions; in particular, map which compilers delete post-division zero tests and under which flags (GIN-OBS-008).

### GIN-OPEN-010 Admissibility closures beyond ℚ
The closure of ℚ in ℝ under field operations and square roots of positive elements is the field of real constructible numbers; under all polynomial converse problems it is the real algebraic numbers. Develop GIN-DEF-019 into a precise correspondence between sets of converse problems and classical closures, and determine which closures are computable with which bit complexity.

### GIN-OPEN-011 Mechanized proofs
Formalize GIN-THM-001…006 and GIN-PROP-006 in a proof assistant. Note that Lean's mathlib uses the totalization 0⁻¹ = 0, so the formal statements must be phrased with explicit admissibility hypotheses — itself a test of the converse vocabulary.
