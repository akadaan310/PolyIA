# CGT Concept Map: how Computational Grammar Theory behaves on numbers

This document records, concept by concept, what happens when CGT's machinery is applied to the structure ℕ (and its relatives ℤ, ℚ, ℝ, ℂ, ℤ/n, fixed-width words, floating-point formats). Each row says whether the concept **survives unchanged**, **needs refinement**, or **becomes especially clear**, and what arithmetic reveals that CGT had not isolated.

Source: the CGT ledger at commit `b3a29f3` (read-only; see `PROVENANCE.md` §3). Verdicts are judgements of this investigation, not theorems.

## 1. Summary table

| CGT concept | Arithmetic instance | Verdict | Where in GiN |
|---|---|---|---|
| Computational structure vs representation (CGT-DEF-001) | number vs numeral vs encoding vs machine state | **especially clear**; refined into four layers | GIN-DEF-001…004 |
| Move signature, relational semantics (CGT-DEF-002) | S, P; digit moves x ↦ bx + d; ·+b, ·×b | survives; **refined**: binary operations give move *families* indexed by an operand (an infinite signature) | GIN-DEF-005, GIN-DEF-014 |
| Operational grammar (CGT-DEF-003) | numerals = words over digit moves; admissibility language = canonical numerals | survives unchanged | GIN-DEF-005…007 |
| Three layers syntax/semantics/execution (CGT FORMAL_MODELS §2, CGT-PROP-002) | `1/0` well formed, semantically empty; `0/0` semantically non-functional; IEEE executes both | **refined** into four layers: a *typing* layer is needed (`0.5` in ℤ, the literal `2147483648` in int32) | GIN-DEF-061 |
| Semantic realizability ⟦w⟧(x) ≠ ∅ | "no solution" | survives; **refined**: arithmetic needs a name for |⟦w⟧(x)| > 1 as a *failure* (non-unique) | GIN-DEF-016 |
| (absent in CGT) converse moves | division = converse of multiplication; subtraction = converse of addition; √ = converse of squaring | **new to the framework**: inverse operations are relational converses; their admissibility is functionality + totality at a point | GIN-DEF-015…017, GIN-THM-001 |
| Structural grammar (CGT-DEF-004) | ℕ → 0 \| S(ℕ); positional numerals as straight-line programs for unary terms | **especially clear**: positional notation *is* grammar compression of unary numerals (CGT's M-SHARE) | GIN-REI-008 |
| Cost profile, word RAM (CGT-DEF-005, FORMAL_MODELS §1) | unit-cost arithmetic vs bit cost | **refined**: the growing parameter is operand bit length; unit cost is admissible only for bounded operands | GIN-DEF-070, GIN-EXP-008 |
| Address, numeration, density (CGT-DEF-006) | canonical numeral = shortlex-least word reaching n from 0 | **especially clear**: positional notation is the address grammar; zero's address is the empty word; CGT's heap numeration is bijective binary shifted by one | GIN-PROP-002, GIN-PROP-006 |
| Transition monoid (CGT-DEF-007) | digit grammar → affine maps x ↦ bᵏx + c; carry automaton → {K, P, G} | survives; two instructive cases (infinite vs finite monoid) | GIN-PROP-005, GIN-PROP-020 |
| Arithmetic compilability (CGT-DEF-011) | carry words compile to one of 3 elements; digit words compile to (bᵏ, c) of Θ(k) bits | **refined**: "O(1) words" fails for digit words (the compiled object grows); holds for the carry monoid. The finite/infinite transition monoid is the regular/non-regular boundary | GIN-REI-005, GIN-THM-005 |
| Information content (CGT-DEF-008) | k-bit numerals name 2ᵏ values; 2ᵏ − 1 of the k-digit decimals are binary-representable | survives | GIN-PROP-031 |
| Mechanisms M-ARITH, M-PRE, M-SHARE, M-RESTRICT, M-PRUNE (CGT-DEF-009) | see §3 | all five appear; a sixth candidate, **re-association** (M-ASSOC), is proposed | GIN-CONJ-001 |
| Arithmetic addressing scope (CGT-THM-003) | n-bit numerals cost ⌈n/w⌉ words; MAX_INT + 1 | survives; becomes the fixed-width boundary | GIN-EXP-012 |
| Same semantics, different grammar shape (CGT-THM-004) | ripple vs prefix adders; Horner vs balanced numeral evaluation | **especially clear**, with a caveat: shape changes depth; it changes bit work only with a matching cost model | GIN-EXP-006, GIN-EXP-011 |
| Grammars cannot cross P/NP (CGT-PROP-006) | factoring, discrete log | survives; GiN makes no complexity-class claims | §4 |
| PageRank fixed points (CGT-THM-008) | f(x) = x; idempotents; Newton iteration; ℕ as least fixed point | partially unifies; important distinctions remain | GIN-REI-007 |
| Counterexample discipline, ladder of claims | — | survives unchanged; extended with HISTORICAL RESULT, REINTERPRETATION, IMPLEMENTATION RESULT | `RESEARCH_CHARTER.md` §3 |

## 2. Concept by concept

### 2.1 Structure and representation → four layers
CGT separates a structure from its representations (CGT-DEF-001) and warns that many apparent "grammar advantages" are changes of representation (CGT-OBS-010). Arithmetic is the paradigm case. The value 2 (an element of ℕ), the numerals `2`, `10₂`, `II`, `SS` (words), the encodings `0x00000002` (int32) and `0x4000000000000000` (binary64), and a register holding one of these encodings in some machine state are four different objects. GiN makes them four layers (GIN-DEF-001…004) with explicit maps between them: *denotation* (numeral → value), *encoding* (value → bit string, partial), *decoding* (bit string → value, total on finite data), *execution* (state → state). `1 + 1 = 2` and `1 + 1 = 10₂` state the same equation at the value layer; they differ at the numeral layer (Chapter 5).

### 2.2 Moves and move families
CGT's move signature Σ is finite. The successor S is a single move; but "add b" and "multiply by b" are *families* of moves indexed by b. Arithmetic therefore needs either an infinite signature or a two-argument operation viewed as a relation on pairs. GiN uses both views: digit grammars have finite signatures (one move per digit); the arithmetic expression language treats binary operators as relations ⟦∘⟧ ⊆ (A × A) × A.

### 2.3 Converse moves — what arithmetic adds
CGT relations may be non-deterministic, and semantic emptiness ⟦w⟧(x) = ∅ is a recognized phenomenon (CGT-PROP-002 case 1). What CGT did not isolate is the systematic role of **converses**. Every inverse operation of arithmetic is the converse of a deterministic forward move:

  a − b = c ⇔ b + c = a,  a / b = c ⇔ b · c = a,  √a = c ⇔ c · c = a (and c ≥ 0),  log a = c ⇔ eᶜ = a.

The converse of a function is in general a *relation*, neither total nor functional. An inverse expression is admissible at a point exactly when the converse relation is a function there: one and only one output. This gives the trichotomy no solution / unique / non-unique (GIN-DEF-016), which classifies `1/0` and `0/0` as *different* failures, as the research mandate anticipated, and puts them in one family with `0 − 1` in ℕ, `7/2` in ℤ, `√−1` in ℝ, `√4` before a branch is chosen, and `2⁻¹` in ℤ/6 (GIN-THM-001…003).

### 2.4 Structural grammar and compression
ℕ is generated by the structural grammar ℕ → 0 | S(ℕ): the smallest non-trivial structural grammar. The unary term Sⁿ(0) has size n. A binary numeral of n is a straight-line program of size O(log n) that generates the same term, with productions corresponding to "double" (X ↦ XX) and "double then succeed". This is exactly CGT's **M-SHARE** mechanism, and it is exponential compression: the unary term of 2ᵏ has size 2ᵏ, the binary numeral size k + 1. The smallest SLP for the unary word aⁿ corresponds to a shortest addition chain for n (Charikar et al. 2005; see `LITERATURE_REVIEW.md` §5), which is also the problem of computing xⁿ with fewest multiplications. Positional notation, square-and-multiply exponentiation, and grammar compression of unary words are one grammar seen three ways (GIN-REI-008).

### 2.5 Addresses
CGT-DEF-006 defines the address of x as the shortlex-least word w with ⟦w⟧(root) = x. For the digit grammar of base b rooted at 0 this *is* the ordinary base-b numeral without leading zeros (GIN-PROP-002). Two consequences:

1. The address of 0 is the **empty word**. The written numeral "0" is a non-canonical word (one leading zero). Positional notation needs a visible zero digit for two different reasons: as a placeholder *inside* numerals (1**0**1) and as a conventional non-empty spelling of the empty address.
2. The CGT heap numeration of binary trees (node 1 is the root, children 2x and 2x + 1) is conjugate, via x ↦ x + 1, to *bijective* base-2 notation (digits 1, 2) rooted at 0 (GIN-PROP-006). The founding CGT observation that "an address carries operations" is, for numbers, the observation that a numeral is a program.

### 2.6 Transition monoids and compilation
For a digit grammar the transition monoid is a monoid of affine maps x ↦ bᵏx + c; compiling a word gives (bᵏ, value) and yields the concatenation law (GIN-PROP-005). The compiled element is not O(1) machine words: c has Θ(k) bits. So digit grammars are **not** arithmetically compilable in the CGT-DEF-011 sense for unbounded words. By contrast, the carry automaton of binary addition has a **finite** transition monoid {K, P, G} (kill, propagate, generate), so any word of digit pairs compiles into one of three elements, and associativity yields parallel-prefix (carry-lookahead) adders (GIN-PROP-020). The difference between a finite and an infinite transition monoid is the difference between addition, which a finite automaton can perform on numerals, and multiplication, which it cannot (GIN-THM-005).

### 2.7 Mechanisms (CGT-DEF-009)
| Mechanism | Arithmetic instance |
|---|---|
| M-ARITH | positional notation itself: the address grammar computes instead of storing (heap ⇔ bijective binary) |
| M-PRE | multiplication tables; precomputed powers in windowed exponentiation; sieves as precomputed admissibility (primality) tables |
| M-SHARE | positional notation as SLP compression of unary; repeated squaring |
| M-RESTRICT | restricting divisors to units (ℤ/n), to nonzero elements (fields), operands to bounded width (fixed-width arithmetic is unit cost *because* of the restriction) |
| M-PRUNE | admissibility checks before execution: Go's and Rust's compile-time rejection of constant `1/0`, `checked_div`, `b ≠ 0` guards |
| **M-ASSOC (proposed)** | associativity lets a right-linear evaluation be re-associated into a balanced tree: carry-lookahead adders, balanced numeral evaluation, parallel prefix. CGT-THM-004 already exhibits the effect; GiN proposes naming it as a sixth mechanism (GIN-CONJ-001). |

### 2.8 Grammar shape (CGT-THM-004)
Ripple-carry (right-linear) and prefix adders (balanced) compute the same function; measured costs: ripple 5n − 3 gates and depth 2n − 1, Kogge–Stone 5891 gates and depth 17 at n = 256 (GIN-EXP-006). For numeral evaluation the two shapes perform the same number of compositions, but in *bit cost* the balanced shape is asymptotically better only when multiplication is subquadratic (GIN-EXP-011). Shape is a mechanism only relative to a cost model — a refinement of the CGT lesson.

### 2.9 Fixed points
"Fixed point" appears in arithmetic in at least three technically different senses: (i) an element with f(x) = x (0 and 1 for squaring, idempotents in ℤ/n); (ii) the limit of an iteration (Newton's method for √a; CGT's PageRank, CGT-THM-008), where existence, uniqueness and rate matter; (iii) the *least* fixed point of a set operator (ℕ is the least X with {0} ∪ S(X) ⊆ X, the inductive definition behind recursion and induction). One definition covers all three formally; the computational content does not transfer between them (GIN-REI-007).

## 3. What arithmetic reveals that CGT had not isolated

1. **Converse admissibility** as a first-class notion (§2.3): CGT treated relational semantics generally but did not single out inverse operations or classify their failures.
2. **A typing layer** between syntax and semantics (§2.1).
3. **Bit length as the cost parameter** (§1, row "cost profile").
4. **Finite vs infinite transition monoids** as the regular/non-regular boundary of operations on numerals (§2.6).
5. **Re-association** as a candidate mechanism (§2.7).
6. **Machine semantics are plural**: the same expression has seven different meanings on seven toolchains on one host (GIN-EXP-004). CGT's "execution layer" must name the machine.

## 4. What does not transfer
- CGT's PageRank and AI-systems material has no arithmetic counterpart beyond fixed-point iteration.
- CGT-PROP-006 (no P/NP crossing) has no arithmetic analogue that GiN can add to: GiN makes no claim about the complexity of factoring or discrete logarithms.
- CGT's GaaS (Grammar as a Service) contract is not reproduced; the GiN expression evaluator returns a comparable layered outcome object but is not a service.

## 5. Proposed extensions to CGT (for the CGT researcher to consider; not applied)
- E1. Add *converse admissibility* (GIN-DEF-015…017) to CGT's operational grammars, with the no-solution/unique/non-unique classification.
- E2. Add a typing layer to CGT's three-layer model.
- E3. Consider M-ASSOC as a sixth mechanism.
- E4. Cite GIN-PROP-006 (heap = shifted bijective binary) next to CGT-DEF-006.
