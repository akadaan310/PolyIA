# Definitions (provisional, session 1)

Each definition is marked *[standard]* (an established notion restated), *[GiN, provisional]* (introduced by this investigation) or *[GiN naming of standard notion]*. Existing terms are not redefined when an existing term does the job. CGT identifiers refer to the parent corpus (read-only).

---

## A. The four layers

### GIN-DEF-001 Number (value) *[standard]*
A **natural number** is an element of a *successor algebra* (ℕ, 0, S): a set with a distinguished element 0 and an injective map S with 0 ∉ S(ℕ), such that every subset containing 0 and closed under S is all of ℕ (Dedekind 1888; Peano 1889). Any two such algebras are uniquely isomorphic, so "the" natural numbers are well defined up to unique isomorphism. Integers, rationals, reals and complex numbers are defined from ℕ by standard constructions (GIN-DEF-020). A *value* is an element of one of these structures. Values are not strings and have no digits.

### GIN-DEF-002 Numeral *[standard; GiN packaging]*
A **numeral** is a word over a finite digit alphabet, read in a *numeral system* that assigns it a value (GIN-DEF-005). `2`, `10₂`, `II`, `SS`, `0010` are numerals. A **digit** is a letter of a numeral alphabet; a digit is a symbol, not a number, even when a numeral of length one denotes the same value as its only digit.

### GIN-DEF-003 Encoding *[standard]*
An **encoding** of a set V of values in a format F is a partial injective map enc: V ⇀ {0,1}^w together with a total decoding map dec from bit strings to V ∪ S_F, where S_F is a set of *special data* that are not values (for IEEE 754: ±∞, NaN; the sign of zero is extra information). Examples: w-bit two's complement encodes [−2^{w−1}, 2^{w−1}); IEEE binary64 encodes a finite set of dyadic rationals.

### GIN-DEF-004 Machine state *[standard]*
A **machine state** is an assignment of bit strings to registers and memory together with status information (flags, pending exceptions, the trap state). An **instruction** is a partial map on states. The *execution* of an expression is a sequence of instructions; its *outcome* is either a final state from which a value is decoded, or a trap/exception state.

> **The four layers.** value (DEF-001) · numeral (DEF-002) · encoding (DEF-003) · machine state (DEF-004). Maps between them: denotation (numeral → value), encoding (value ⇀ bits), decoding (bits → value or special datum), execution (state → state). A claim about arithmetic names its layer. "1 + 1 = 2" is a statement about values; "1 + 1 = 10₂" is the same statement with the right-hand side written in a different numeral system; "`0x7FFFFFFF + 1` is `0x80000000`" is a statement about encodings under wraparound.

## B. Numerals as operation expressions

### GIN-DEF-005 Digit grammar *[GiN, provisional; positional notation is classical]*
A **digit grammar** is a pair (b, D) with base b ≥ 1 and a finite digit set D ⊂ ℤ. It is a CGT operational grammar (CGT-DEF-003) on the carrier ℤ with one move per digit,

  ⟦d⟧ : x ↦ b·x + d  (d ∈ D),

start point 0, and admissibility language D* (or a sublanguage, GIN-DEF-007). Instances: *standard base b* (b ≥ 2, D = {0,…,b−1}); *bijective base b* (D = {1,…,b}; b = 1 is unary, whose single move is the successor S); *balanced ternary* (b = 3, D = {−1, 0, 1}); redundant systems (e.g. b = 2, D = {0, 1, 2}).

### GIN-DEF-006 Value of a numeral *[standard]*
The **value** of a word w = d₁d₂…d_k (most significant digit first) is val(w) = ⟦w⟧(0) = Σᵢ dᵢ b^{k−i}. Evaluating ⟦w⟧ left to right is Horner's rule.

### GIN-DEF-007 Canonical numeral (address) *[GiN naming of standard notion; specialization of CGT-DEF-006]*
The **canonical numeral** addr(n) of a value n is the shortlex-least word w with ⟦w⟧(0) = n, when one exists. For standard base b it is the usual numeral without leading zeros, and addr(0) = ε, the empty word.

### GIN-DEF-008 Affine transition monoid *[standard; CGT-DEF-007 instance]*
The transition monoid of a digit grammar is the set of maps ⟦w⟧ = (x ↦ b^{|w|}x + val(w)), w ∈ D*, under composition. A word **compiles** to the pair (b^{|w|}, val(w)).

## C. The successor grammar

### GIN-DEF-009 Successor grammar *[standard]*
The structural grammar ℕ → 0 | S(ℕ) generates the *successor terms* 0, S(0), S(S(0)), …; its unique model is the successor algebra (GIN-DEF-001). A successor term is a unary numeral (bijective base 1).

### GIN-DEF-010 Primitive recursion on the successor grammar *[standard]*
add(m, 0) = m, add(m, S n) = S(add(m, n)); mul(m, 0) = 0, mul(m, S n) = add(mul(m, n), m); pow(m, 0) = S 0, pow(m, S n) = mul(pow(m, n), m); pred(0) = 0, pred(S n) = n; monus(m, 0) = m, monus(m, S n) = pred(monus(m, n)). Cost is counted in **rule applications** (one per equation used).

### GIN-DEF-011 Successor transition system *[GiN naming of standard notion]*
T_ℕ is the labelled transition system on ℕ with move S (total) and its converse P (defined on ℕ ∖ {0}). The **boundary** of a subset X ⊆ ℕ in T_ℕ is the set of x ∈ X at which S or P leads out of X or is undefined.

### GIN-DEF-012 Segment and the notation a{I}b *[GiN, provisional; notation proposed by A. Kadaan]*
For integers a < b, the **segment** [a, b] of T_ℕ (or T_ℤ) is the transition system on {a, …, b} with S defined on a … b−1 and P on a+1 … b. Its *boundary* is {a, b} (each has exactly one admissible move) and its *interior* is {a+1, …, b−1} (both moves admissible). The notation **a{i₁, …, i_k}b** is *well formed* iff a < b and (i₁, …, i_k) = (a+1, …, b−1); it then denotes the segment [a, b] with its boundary written outside the braces and its interior inside. Thus `0{1,2,3}4` denotes [0, 4]; `3{}4` denotes the segment with empty interior; `0{1,3}4` and `4{}4` are ill formed.

### GIN-DEF-013 Church numeral *[standard]*
The Church numeral of n is the higher-order function f ↦ fⁿ (Church 1941): a number *as* an iterator. It is the successor grammar read as a program.

## D. Operations and admissibility

### GIN-DEF-014 Operation grammar *[GiN, provisional]*
A binary operation ∘ on a carrier A induces the relation ⟦∘⟧ ⊆ (A × A) × A, {((a, b), a ∘ b)}, and, for each b, the move ⟦∘b⟧ : a ↦ a ∘ b. An operation is **closed** (total) on A if a ∘ b ∈ A for all a, b ∈ A.

### GIN-DEF-015 Converse problem *[GiN, provisional; relational converse is standard]*
For a forward operation ∘ the **converse problem** at (a, b) is

  Sol∘(a, b) = { c ∈ A : b ∘ c = a }.

Division asks Sol×(a, b); subtraction asks Sol₊(a, b); the square root asks Sol(a) = {c : c·c = a}; the logarithm asks {c : eᶜ = a}; the modular inverse asks Sol×(1, b) in ℤ/n.

### GIN-DEF-016 Converse admissibility *[GiN, provisional]*
An inverse expression is
- **inadmissible: no solution** if Sol = ∅;
- **admissible** if |Sol| = 1, and then denotes the unique solution;
- **inadmissible: non-unique** if |Sol| ≥ 2.

A **branch** (principal value, selection) is a choice function on non-unique solution sets that turns a non-unique converse into a function (e.g. √ selects the nonnegative root).

### GIN-DEF-017 Repairs of inadmissibility *[GiN, provisional classification]*
Ways in which a mathematical or computational system gives an inadmissible expression a value:
1. **Extension** — enlarge the carrier so that Sol becomes non-empty (ℕ → ℤ for subtraction, ℤ → ℚ for division by nonzero, ℝ → ℂ for √ of negatives, ℝ → ℝ ∪ {∞} for 1/0).
2. **Selection** — choose an element of a non-unique Sol (principal branches; Euclidean quotient with remainder conditions).
3. **Restriction** — remove the bad inputs from the domain (b ≠ 0; units only).
4. **Quotient** — identify elements so that the operation becomes total (ℤ → ℤ/2ʷ makes 0 − 1 = 2ʷ − 1).
5. **Totalization** — define a value by convention without claiming it solves the converse problem (meadows and proof assistants: x/0 := 0; AArch64 integer division by zero returns 0; RISC-V returns −1).
6. **Absorption** — adjoin a special element that absorbs further operations (NaN; the wheel element ⊥; Option/Result types).
7. **Signal** — refuse to produce a value and transfer control (hardware trap, exception, panic, compile-time error).

Each repair changes the grammar; GIN-THM-004 records *which* law each one gives up.

### GIN-DEF-018 Closure of a domain *[standard]*
A domain is **closed** under an inverse operation if the operation is admissible at every point. ℤ is closed under subtraction; ℚ ∖ {0} under division; ℤ/p (p prime) under division by nonzero elements.

### GIN-DEF-019 Admissibility closure *[GiN, provisional]*
Given a carrier A ⊆ U inside a larger structure U and a set of converse problems, the **admissibility closure** of A is the least B with A ⊆ B ⊆ U such that every converse problem with data in B that has a solution in U has one in B. Examples: the closure of ℕ in ℚ under subtraction is ℤ; the closure of ℤ in ℂ under division by nonzero elements is ℚ; the closure of ℚ in ℝ under field operations and square roots of positive elements is the field of real constructible numbers (see GIN-OPEN-010).

### GIN-DEF-020 Number system as grammar *[GiN packaging of standard notions]*
A number system is presented as a tuple (carrier, operations, admissibility of each inverse, identities, order, topology where relevant, representations). `NUMBER_GRAMMAR.md` §4 gives the table for ℕ, ℤ, ℚ, ℝ, ℂ, ℤ/n, ℤ_p, fixed-width words and IEEE formats.

## E. Floating point and machine models

### GIN-DEF-030 IEEE binary format *[standard: IEEE 754-2019]*
A format with precision p (significand bits including the hidden bit) and maximum exponent emax = 2^{e−1} − 1 for e exponent bits; emin = 1 − emax. Finite data are ±m·2^{q} with integers 0 ≤ m < 2^p and q ≥ emin − p + 1, plus ±∞ and NaN.

### GIN-DEF-031 Correct rounding *[standard]*
An operation is **correctly rounded** if its result is the exact real result rounded once to the format (here: to nearest, ties to even). IEEE 754 requires this of +, −, ×, ÷, √ and fused multiply–add.

### GIN-DEF-032 Exception flags *[standard]*
invalid (no useful real result: 0/0, ∞ − ∞, 0 × ∞, √(negative), operations on signaling NaNs), divideByZero (exact infinite result from finite operands: x/0 with x ≠ 0 finite), overflow, underflow (tiny and inexact under default handling), inexact.

### GIN-DEF-033 Integer machine model *[GiN packaging]*
A triple (width w, overflow policy ∈ {wrap, saturate, trap, undefined}, division semantics) where division semantics fixes the results or signals for x/0 and for −2^{w−1}/(−1). `MACHINE_MODEL.md` lists the models for x86-64, AArch64, RISC-V, ISO C, Java, Rust, Go, Python and JavaScript.

## F. Circuits

### GIN-DEF-040 Circuit *[standard]*
A directed acyclic graph whose sources are input wires and constants and whose internal nodes are gates from a basis (here {NOT, AND, OR, XOR} with fan-in ≤ 2, or {NAND}). *Admissibility* is syntactic: each gate input is a previously defined wire. *Semantics*: the Boolean function computed. *Cost*: (size = number of gates, depth = longest input–output path).

### GIN-DEF-041 Carry automaton and carry monoid *[standard idea; GiN naming]*
Binary addition read least significant digit first is a two-state transducer whose state is the carry. On a digit pair (aᵢ, bᵢ) its transition is a map on {0, 1}: **K** (kill, c ↦ 0) for (0, 0), **P** (propagate, c ↦ c) for (0, 1) and (1, 0), **G** (generate, c ↦ 1) for (1, 1). The **carry monoid** is {K, P, G} under composition.

### GIN-DEF-042 Prefix adder *[standard]*
An adder that computes all carries as prefix compositions in the carry monoid with a parallel-prefix network (Sklansky 1960; Kogge & Stone 1973; Ladner & Fischer 1980; Brent & Kung 1982).

## G. Number theory as transition systems

### GIN-DEF-050 Euclid system *[standard]*
States (a, b) ∈ ℕ²; move (a, b) → (b, a mod b) admissible iff b ≠ 0; invariant gcd(a, b); terminal states (g, 0).

### GIN-DEF-051 Bézout rows *[standard]*
Rows (rᵢ, sᵢ, tᵢ) with r₀ = a, r₁ = b, r_{i+1} = r_{i−1} − qᵢ rᵢ (same for s, t), invariant rᵢ = sᵢ a + tᵢ b.

### GIN-DEF-052 Exponent program *[standard; GiN naming]*
For e ≥ 1 with binary numeral 1β, the **exponent program** is the word over {M, S, SM} that starts with M (load the base) and maps each later bit 0 ↦ S (square), 1 ↦ SM (square, then multiply). Running it computes xᵉ (left-to-right binary exponentiation).

### GIN-DEF-053 Congruence system *[standard]*
A system x ≡ rᵢ (mod mᵢ) is a converse problem for the map x ↦ (x mod m₁, …, x mod m_k); its solution set is ∅ or one residue class mod lcm(mᵢ).

## H. Arithmetic as a language

### GIN-DEF-060 Arithmetic expression language *[GiN, provisional]*
Tokens: numerals (decimal integers and decimal fractions; `0b…` and `…₂` binary; `0x…` hexadecimal), the variable x, operators + − × / // mod ^, parentheses, functions sqrt and gcd. Grammar (precedence low to high): additive, multiplicative, unary minus, power (right-associative). Implemented in `ginsdk.expr`.

### GIN-DEF-061 Four evaluation layers *[GiN, provisional; refines CGT's three layers]*
1. **syntax** — is the string a sentence of the grammar?
2. **typing** — does every literal and variable denote an element of the chosen domain?
3. **semantics** — does every operation have exactly one result (GIN-DEF-016)?
4. **execution** — what does the chosen machine model do (overflow, rounding, traps, exceptions, undefined behaviour, flags)?

### GIN-DEF-062 Outcome *[GiN, provisional]*
The result of evaluating an expression in a domain: a status (value, special datum, no-solution, non-unique, not-in-domain, unsupported, overflow, trap, exception, undefined, syntax-error), the layer at which evaluation stopped, a reason, the converse equation where relevant, flags, the step trace, the parse tree, the representation of the result, and a cost estimate. No outcome is a bare "error".

## I. Cost

### GIN-DEF-070 Bit-cost model *[standard]*
Operands are measured by bit length L. A *word operation* acts on w-bit limbs (here w = 32): add/subtract-with-carry, limb product, two-by-one-limb quotient estimate, limb comparison. Unit-cost arithmetic is used only for operands of bounded length, and the bound is stated.
