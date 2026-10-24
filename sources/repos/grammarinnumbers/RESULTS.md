# Results Ledger

Every entry carries one category from the ladder of claims (`RESEARCH_CHARTER.md` §3), a status, and a relationship to prior work. **"Proved here"** means the proof below was written by the session-1 collaborator and the exact statement is checked exhaustively on small cases by `experiments/check_theorems.py` (results in `experiments/results/checks.json`). No proof has been externally reviewed. **Nearly everything here is classical or elementary.** The default assumption for any arithmetic fact is that it is known; novelty is discussed in §G.

Notation: `DEFINITIONS.md`. b = base, D = digit set, val = value of a numeral, addr = canonical numeral, Sol = solution set of a converse problem, Ann(b) = {t : bt = 0}.

---

## A. Numerals and the successor grammar

### GIN-PROP-001 Numeral ≠ number: the value map and its non-injectivity *(Proposition; classical, proof written here)*
For standard base b ≥ 2 the value map val: {0,…,b−1}* → ℕ is surjective, and val(u) = val(v) iff u and v differ only by leading zeros. Consequently exactly L − |addr(n)| + 1 words of length ≤ L denote n (for |addr(n)| ≤ L).

*Proof.* Leading zeros do not change the value because ⟦0⟧(0) = b·0 + 0 = 0, so ⟦0w⟧(0) = ⟦w⟧(0). Conversely let u, v be words without leading zeros and val(u) = val(v) = n. If n = 0 both are empty (a non-empty word without leading zero has value ≥ b^{|w|−1} ≥ 1). Otherwise b^{|u|−1} ≤ n < b^{|u|} and likewise for v, so |u| = |v|; the last digits are both the residue n mod b, and removing them leaves words of equal value (n − d)/b; induct on length. Surjectivity: the residue algorithm d = n mod b, n ← (n − d)/b strictly decreases n > 0 and stops at 0. ∎

*Check.* All 6,303 pairs of words up to length 5 (b = 2) and 3 (b = 3, 4). *Experiment.* GIN-EXP-001.

### GIN-PROP-002 Zero's canonical numeral is the empty word *(Proposition; elementary; a REINTERPRETATION of CGT-DEF-006)*
In every digit grammar, addr(0) = ε. In standard base b the words denoting 0 are exactly ε, 0, 00, 000, …; the numeral "0" is the shortest *non-empty* one, i.e. a conventional non-canonical spelling.

*Proof.* ε is the shortlex-least word and ⟦ε⟧(0) = 0. The second claim is GIN-PROP-001 with n = 0. ∎

*Meaning.* The zero digit plays two roles that the grammar separates: a **placeholder** inside numerals (1**0**1 ≠ 11) and a **spelling** of the empty address. Bijective notation (GIN-PROP-004) needs neither: it has no zero digit and writes 0 as ε.

### GIN-PROP-003 The cost of Peano arithmetic *(Proposition; elementary, proved here)*
Under the primitive-recursive definitions of GIN-DEF-010, add(m, n) uses exactly n + 1 rule applications and mul(m, n) uses exactly mn + 2n + 1. Hence on inputs whose binary numerals have k bits, unary addition costs Θ(2ᵏ) rule applications against Θ(k) bit operations for binary addition: exponential in the length of the numeral.

*Proof.* add: one rule per S peeled from n plus the base rule. mul: by induction; mul(m, 0) costs 1; mul(m, S n) costs 1 + (mn + 2n + 1) + (m + 1) = m(n+1) + 2(n+1) + 1, using the add cost with second argument m. ∎

*Check.* m, n < 12. *Experiment.* GIN-EXP-001 table (n = 2¹⁹ − 1: 524,288 rules vs 20 bit operations).

### GIN-PROP-004 Residue digit systems; bijective numeration *(Proposition; classical: Smullyan 1961 "k-adic", Forslund 1995; proof written here)*
Let b ≥ 2 and let D be a complete residue system mod b (or b = 1, D = {1}).
1. If a word w denotes n, its last digit is the unique d ∈ D with d ≡ n (mod b) and its prefix denotes (n − d)/b. So the words denoting n are determined by the residue algorithm up to prefixes that denote 0.
2. **Standard** (D = {0,…,b−1}) and **balanced ternary** (b = 3, D = {−1, 0, 1}): every n ∈ ℕ (resp. ℤ) has a canonical numeral and the words denoting n are exactly 0ᵏ·addr(n).
3. **Bijective** (D = {1,…,b}): val is a bijection D* → ℕ.

*Proof.* (1) val(w'd) = b·val(w') + d. (2) The residue algorithm terminates: for standard digits as in GIN-PROP-001; for balanced ternary |(n − d)/3| ≤ (|n| + 1)/3 < |n| for |n| ≥ 1. A prefix denoting 0 must end in the digit ≡ 0, which is 0, and recursively consists of zeros. (3) Every non-empty word of positive digits has positive value, so only ε denotes 0; for n ≥ 1 the algorithm gives n ↦ (n − d)/b < n with d ∈ {1,…,b}, so it terminates, and by (1) the word is unique. ∎

*Check.* Bijective bases 1, 2, 3, 5 exhaustively by length (all values distinct and forming an initial segment of ℕ). *Experiment.* GIN-EXP-001.

*Counterexample to dropping the hypothesis.* b = 2, D = {−1, 2} is a complete residue system but the non-empty word (−1)(2) denotes 0, so uniqueness fails. Ordinary binary does not terminate on negative numbers: GIN-PROP-008.

### GIN-PROP-005 Compilation and the concatenation law *(Proposition; classical, restated as a CGT-DEF-007 transition monoid)*
For a digit grammar (b, D) and words u, v: ⟦w⟧ = (x ↦ b^{|w|}x + val(w)), hence ⟦uv⟧ = ⟦v⟧ ∘ ⟦u⟧ and val(uv) = val(u)·b^{|v|} + val(v). The transition monoid is {x ↦ bᵏx + c}.

*Proof.* Induction on |w| using (x ↦ b x + d) ∘ (x ↦ bᵏx + c) = x ↦ b^{k+1}x + (bc + d). ∎

*Remark (CGT-DEF-011).* The compiled element (b^{|w|}, val(w)) has Θ(|w|) bits, so digit grammars are **not** arithmetically compilable in CGT's O(1)-word sense for unbounded words. Contrast GIN-PROP-020.

### GIN-PROP-006 CGT's heap numeration is bijective binary, shifted by one *(Proposition; elementary, proved here; likely folklore, novelty unverified)*
Let φ(x) = x + 1. The bijective base-2 grammar (digits 1, 2; moves x ↦ 2x+1, x ↦ 2x+2; root 0) is conjugate by φ to the CGT heap grammar on binary trees (moves L: y ↦ 2y, R: y ↦ 2y + 1; root 1): φ ∘ ⟦1⟧ = L ∘ φ and φ ∘ ⟦2⟧ = R ∘ φ. Consequently the bijective base-2 numeral of n, with 1 ↦ L and 2 ↦ R, is the CGT heap address of node n + 1, i.e. the binary numeral of n + 1 with its leading 1 removed.

*Proof.* (2x + 1) + 1 = 2(x + 1) and (2x + 2) + 1 = 2(x + 1) + 1. By induction on words, φ ∘ ⟦w⟧ = ⟦h(w)⟧ ∘ φ with h(1) = L, h(2) = R; evaluate at 0. Both addresses are unique words (GIN-PROP-004(3); the heap address of m ≥ 1 is unique), so they correspond. ∎

*Check.* n < 300,000. *Meaning.* The address insight that motivated CGT (an address carries operations; CGT-DEF-006, CGT-THM-003, CGT-THM-006) is, for numbers, positional notation itself.

### GIN-PROP-007 Positional numerals are straight-line programs for unary terms *(Proposition; classical: addition chains, Knuth TAOCP vol. 2 §4.6.3; SLPs, Charikar et al. 2005)*
For n ≥ 1 with binary numeral of length k and popcount ν, the unary word Sⁿ (equivalently aⁿ) is generated by a straight-line program with k + ν − 1 ≤ 2k − 1 productions: A₁ → a, and for each later bit a doubling production A → A′A′ followed, for bit 1, by A → A′a. This program has exactly the shape of the exponent program for xⁿ (GIN-PROP-041): k − 1 squarings and ν − 1 multiplications. Conversely an SLP of size m for aⁿ yields an addition chain for n of length at most m (literature).

*Proof.* Horner's rule for the binary numeral: reading bit β maps the current length ℓ to 2ℓ + β; doubling is concatenation of the word with itself, the bit 1 appends one letter. Count the productions. ∎

*Meaning.* Positional notation is CGT's M-SHARE mechanism applied to the successor grammar: exponential compression of unary numerals (GIN-REI-008).

### GIN-PROP-008 Two's complement is the truncated 2-adic expansion *(Proposition; classical; proof written here)*
For every integer n and width w, the first w digits d₀, …, d_{w−1} of the base-2 residue expansion of n (d = x mod 2, x ← (x − d)/2) are the bits of n mod 2ʷ — the w-bit two's-complement encoding when −2^{w−1} ≤ n < 2^{w−1}. For n < 0 the expansion never terminates: the state reaches −1, a fixed point of x ↦ (x − 1)/2, after which every digit is 1. The infinite word …111d_{j}…d₀ is the 2-adic expansion of n.

*Proof.* After w steps n = Σ_{i<w} dᵢ2ⁱ + 2ʷx_w, so Σ dᵢ2ⁱ ≡ n (mod 2ʷ) and lies in [0, 2ʷ). For x < 0, x ↦ ⌊x/2⌋ is non-decreasing toward −1 and fixes −1, where the digit is 1. ∎

*Check.* All representable n for widths 1–12. *Meaning.* The grammar of standard binary *cannot* reach negative numbers in finitely many moves; the hardware's answer, fixed width, is a quotient (GIN-DEF-017, repair 4) that keeps only the first w moves.

### GIN-PROP-009 Long division is a finite transition system *(Proposition; classical)*
Expanding p/q (0 ≤ p < q, lowest terms) in base b runs the transition system on remainders r ↦ (b·r) mod q, emitting digit ⌊b·r/q⌋. The expansion terminates iff every prime factor of q divides b; otherwise it is eventually periodic, with period at most q − 1.

*Proof.* The state space {0,…,q−1} is finite, so the trajectory is eventually periodic; it reaches 0 iff p/q = m/bᵏ for some k iff q | bᵏ (lowest terms) iff the primes of q divide b. ∎

*Check.* Bases 2, 3, 10, 12, denominators < 200. *Example.* 1/3 = 0.(3) in base 10 and 0.(01) in base 2; 1/10 = 0.0(0011) in base 2 — which is why 0.1 is not a binary64 number (GIN-PROP-031).

### GIN-PROP-010 The cost of the successor in binary *(Proposition; the binary counter is textbook (CLRS §17.1); closed form proved here)*
Counting from 0 to N in binary flips exactly 2N − popcount(N) bits. The successor therefore costs 2 bit flips amortized and ⌊log₂ N⌋ + 1 in the worst case (at N = 2ᵏ − 1 → 2ᵏ).

*Proof.* The increment x → x + 1 turns the t(x) trailing ones into zeros and one zero into a one: it flips t(x) + 1 bits and changes the popcount by 1 − t(x). Summing over x = 0,…,N−1: flips = Σ(t + 1) = Σ(2 − (1 − t)) = 2N − (popcount(N) − popcount(0)). ∎

*Check.* N ≤ 65,536; GIN-EXP-002 to 131,072 (amortized 2.0000, worst 18).

## B. The segment notation 0{1,2,3}4

### GIN-REI-010 Verdict on the segment notation *(Reinterpretation; notation proposed by A. Kadaan, formalized in GIN-DEF-012)*
Formalized, `a{I}b` denotes the segment [a, b] of the successor transition system with boundary {a, b} outside the braces and interior I inside. The notation has **formal value** in three precise senses: (i) it is *checkable* — it carries redundant information (I is determined by a and b), so ill-formed instances such as `0{1,3}4` are detectable, with a diagnosis (`ginsdk.peano.parse_segment`); (ii) it *displays* the transition-system distinction between boundary points (one admissible move: S at a, P at b) and interior points (both moves admissible); (iii) it generalizes to any transition system as "endpoints plus the points strictly between them along a path". It has **no new mathematical content**: as a set it is the closed interval [a, b], and as a structure it is the path graph on b − a + 1 vertices with marked endpoints. It is notation, not theory.

## C. Converses: division, zero and admissibility

### GIN-THM-001 The structure of a converse in a commutative ring *(Theorem; standard algebra, proof written here)*
Let R be a commutative ring and a, b ∈ R. The solution set Sol(a, b) = {c ∈ R : bc = a} is either empty or a coset c₀ + Ann(b). Hence:
1. **image condition**: Sol(a, b) ≠ ∅ iff a ∈ bR;
2. **kernel condition**: when non-empty, |Sol(a, b)| = |Ann(b)|; the quotient is unique iff Ann(b) = {0}.

*Proof.* If c₀ ∈ Sol then bc = a ⇔ b(c − c₀) = 0 ⇔ c − c₀ ∈ Ann(b). ∎

*Check.* 30 finite commutative rings (ℤ/n for n ≤ 24, five products ℤ/m × ℤ/k, and 𝔽₂[x]/(x³)), all 5,737 pairs (a, b). The same statement holds for any homomorphism of abelian groups (solution sets of linear equations are empty or cosets of the kernel).

### GIN-COR-001 Why 1/0 and 0/0 fail differently, and why 0/1 = 0 *(Corollary; standard)*
In a field F (and in ℤ, ℚ, ℝ, ℂ):
- b ≠ 0: Ann(b) = {0} and bF = F, so a/b is admissible for every a. In particular **0/1 = 0**: the image condition holds because 0 ∈ 1·F, and the kernel condition holds because 1 is a unit; the unique solution of 1·c = 0 is c = 0.
- **1/0**: 0·F = {0} (GIN-PROP-012), so the image condition fails: 0·c = 1 has **no solution** (it would require 0 = 1). An *image failure*.
- **0/0**: the image condition holds (0 ∈ 0·F), but Ann(0) = F, so **every** c solves 0·c = 0. A *kernel failure*: not "no answer" but "no single answer".
- **x/0 for symbolic x**: no solution where x ≠ 0, every c where x = 0 — a case split that symbolic simplification must not erase (GIN-PROP-014).

*Remark.* In the zero ring {0} (where 1 = 0) the quotient 0/0 is admissible and equals 0; this is the only ring in which division by zero is admissible (GIN-THM-003).

### GIN-THM-002 Division in ℤ/n *(Theorem; standard number theory, proof written here)*
In ℤ/n with g = gcd(b, n): Sol(a, b) ≠ ∅ iff g | a, and then |Sol(a, b)| = g, the solutions forming c₀ + (n/g)ℤ/n. Exactly n·φ(n) of the n² pairs (a, b) have a unique quotient, and Σ_{b=0}^{n−1} n/gcd(b, n) are solvable.

*Proof.* By Bézout, bℤ/n = gℤ/n, which gives the image condition. bt ≡ 0 (mod n) iff (n/g) | (b/g)t iff (n/g) | t, since gcd(b/g, n/g) = 1; so Ann(b) = (n/g)ℤ/n has g elements. A unique quotient requires g = 1 (b a unit), and then all n values of a work: n·φ(n) pairs. For each b, the solvable a are the n/g multiples of g. ∎

*Check.* n ≤ 60 exhaustively; GIN-EXP-003 to n = 64 (0 violations; unique share = φ(n)/n).

### GIN-THM-003 No non-trivial ring can invert zero *(Theorem; standard)*
If R is a ring with 1 in which 0·z = 1 for some z, then R = {0}.

*Proof.* 0·z = 0 (GIN-PROP-012(i)), so 1 = 0, and every x = x·1 = x·0 = 0. ∎

*Check.* ℤ/n, n < 60: an inverse of 0 exists only for n = 1.

### GIN-THM-004 The extension trilemma for 1/0 *(Reinterpretation: a synthesis of cited facts; the trilemma formulation is GiN's)*
By GIN-THM-003, any system that gives `1/0` a value must give up at least one of: **(A)** the ring laws that force 0·c = 0 (distributivity with additive inverses), **(B)** the *converse reading* of division (that a/b denotes a c with b·c = a), or **(C)** 0 ≠ 1. Every system in the literature and in hardware takes route A, B, or *signals* instead of answering:

| System | 1/0 | 0/0 | Route | What gives way |
|---|---|---|---|---|
| ℚ, ℝ, ℂ (fields) | no solution | non-unique | restriction | division is defined only for b ≠ 0 |
| projective line ℚ ∪ {∞}, Riemann sphere ℂ ∪ {∞} | ∞ | undefined | A | 0·∞, ∞ ± ∞, ∞/∞, 0/0 undefined; no field structure; no order (GIN-THM-006) |
| extended reals ℝ ∪ {±∞} | usually undefined (a/±∞ = 0 is defined) | undefined | A | 0·(±∞) and ∞ − ∞ undefined; ±∞ are not field elements |
| IEEE 754 floating point | ±∞, flag divideByZero (sign from the operands, including the sign of zero) | NaN, flag invalid | B | 0 × ∞ = NaN, so ∞ is not a solution of 0 × c = 1 (GIN-PROP-015); NaN ≠ NaN |
| meadows (Bergstra & Tucker 2007) | 0 | 0 | B | x·x⁻¹ = 1 only for x ≠ 0; ring axioms kept |
| Lean's mathlib (0⁻¹ = 0) | 0 | 0 | B | theorems such as a·a⁻¹ = 1 carry the hypothesis a ≠ 0 |
| wheels (Carlström 2004) | /0, a distinguished element | ⊥ (absorbing) | A | 0·x = 0 fails in general; distributivity weakened to (x+y)z + 0z = xz + yz |
| AArch64 SDIV/UDIV | 0, no signal | 0 | B (totalization) | the result is not a quotient of anything |
| RISC-V DIV/DIVU | −1 / 2ʷ − 1, remainder = dividend | same | B (totalization) | as above; matches the natural output of a restoring divider (GIN-PROP-023) |
| x86-64 IDIV, Java, Rust, Go, Python, JS BigInt | trap / exception / panic | same | signal | no value is produced |
| ISO C | undefined behaviour | same | none | the program has no meaning (GIN-OBS-008) |
| limits | lim_{x→0±} 1/x = ±∞ (not a real limit) | lim f/g depends on f and g | — | a question about *functions*, not numbers |

Facts about meadows, wheels and mathlib are taken from the cited sources and secondary literature (`LITERATURE_REVIEW.md` §7); hardware and language behaviour is measured (GIN-EXP-004) or cited to specifications (`MACHINE_MODEL.md`).

### GIN-THM-006 Fractions as pairs: ∞ can be adjoined, 0/0 cannot *(Theorem; elementary, proved here; the projective line is classical, and keeping (0,0) as an absorbing element is Carlström's wheel of fractions; novelty of the pair-level statement unverified)*
On ℤ² let (a, b) ~ (c, d) iff ad = bc, and define (a,b) + (c,d) = (ad + bc, bd), (a,b)·(c,d) = (ac, bd), (a,b)/(c,d) = (ad, bc).
1. ~ is reflexive and symmetric on ℤ². On ℤ² ∖ {(0,0)} it is an equivalence relation whose classes are the lines through the origin: the projective line ℚ ∪ {∞}, where ∞ is the single class of all (a, 0), a ≠ 0. On ℤ × (ℤ ∖ {0}) the classes are ℚ.
2. (0, 0) is related to **every** pair, so on ℤ² transitivity fails: (1,0) ~ (0,0) ~ (0,1) but (1,0) ≁ (0,1). Admitting "0/0" as a pair would identify everything.
3. The operations are well defined on classes (scaling an operand by k ≠ 0 scales the result by k), with result the null pair (0,0) exactly in the cases ∞ + ∞ (hence ∞ − ∞, since −∞ = ∞ here), 0 · ∞, 0/0 and ∞/∞; every other combination of elements of ℚ ∪ {∞} is defined. In particular **1/0 = ∞**, x/0 = ∞ for x ≠ 0, 1/∞ = 0, 0/∞ = 0.

So in the arithmetic of pairs, **every indeterminate form computes the same object — the null pair — and the null pair is exactly the one pair that cannot be an element**.

*Proof.* (1) Reflexivity and symmetry are immediate. Transitivity for p ~ q ~ r with q ≠ (0,0): if q = (c, d) with d ≠ 0, then ad = bc and cf = de give adf = bcf = bde, so d(af − be) = 0 and af = be. If d = 0 then c ≠ 0; ad = bc gives b = 0, and cf = de gives f = 0, so af = 0 = be. A pair is ~ to (1, 0) iff its second entry is 0. (2) a·0 = 0·b. (3) Each operation multiplies componentwise by k when one operand is scaled by k, so classes go to classes and the null pair to itself. Null sum: bd = 0 and ad + bc = 0; if b = 0 then a ≠ 0 forces d = 0, i.e. both are ∞ (and then the first entry is 0 automatically); symmetrically if d = 0. Null product: ac = 0 and bd = 0 with neither operand null: one factor has first entry 0 (it is 0) and the other second entry 0 (it is ∞). Null quotient: ad = 0 and bc = 0: either a = c = 0 (0/0) or b = d = 0 (∞/∞) — the mixed cases would make an operand null. ∎

*Check.* All pairs in [−4, 4]², 19,200 operations, including well-definedness under scaling.

### GIN-PROP-011 0/1 = 0 as a complete case study *(Proposition; trivial; included for the narrative)*
See GIN-COR-001. The contrast with 1/0 is not a swap of the symbols 0 and 1 but a change of *which side* zero is on: a zero numerator tests the image condition with the always-present element 0 ∈ bR; a zero denominator shrinks the image to {0} and the kernel to everything.

### GIN-PROP-012 Why 0·a = 0, derived four ways *(Proposition; classical; multi-framework presentation is GiN's)*
1. **Ring axioms.** 0a = (0 + 0)a = 0a + 0a; adding −(0a) gives 0a = 0. Uses distributivity *and* additive inverses (cancellation). In a semiring without cancellation, 0·a = 0 does not follow and is taken as an axiom (absorption).
2. **Peano recursion.** a·0 = 0 is the base equation of mul. 0·a = 0 by induction on a: 0·0 = 0, 0·S(a) = 0·a + 0 = 0 + 0 = 0.
3. **Cardinality.** |∅ × A| = |∅| = 0 because there are no pairs with a first component from ∅.
4. **Repeated addition.** a·0 is the sum of zero copies of a: the empty sum, which is the additive identity 0.

### GIN-PROP-013 Why 2 × 3 = 3 × 2 *(Proposition; classical)*
2 + 2 + 2 and 3 + 3 are different words (different derivations) with the same value. Two proofs that they must agree: (i) induction on the Peano definitions (lemmas S(m)·n = m·n + n and m·n = n·m); (ii) the bijection (x, y) ↦ (y, x) between A × B and B × A, so |A|·|B| = |B|·|A|. The equality is a theorem about the semantics, not a fact visible in the syntax.

### GIN-PROP-014 Symbolic simplification is not evaluation *(Proposition; elementary)*
In the field ℚ(x) of rational functions, x/x = 1 is an identity. As an expression evaluated at points of ℚ, x/x is admissible exactly on ℚ ∖ {0}, and at 0 it is the kernel failure 0/0. Cancelling a common factor g preserves values on {g ≠ 0} and silently enlarges the domain; a correct simplifier must record g ≠ 0 as a side condition. Likewise (x² − 1)/(x − 1) = x + 1 only on x ≠ 1.

*Implementation.* `ginsdk.expr` (domain `symbolic`) keeps every divisor's condition before cancellation and reports the failure at each excluded point (GIN-EXP-003).

### GIN-PROP-015 IEEE division by zero is not the converse of IEEE multiplication *(Proposition; elementary consequence of IEEE 754)*
For finite nonzero x, IEEE 754 gives x/(±0) = ±∞ with divideByZero, and 0/0 = NaN with invalid. But 0 × (±∞) = NaN (invalid), and 0 × c = ±0 for finite c, so no IEEE datum c satisfies 0 ⊗ c = 1. IEEE's ±∞ is a limit-motivated value whose sign records the side from which the zero was approached (the sign of zero; Kahan 1987), not a solution of the converse problem.

*Check.* Four formats, both signs; hardware agreement GIN-IMP-001.

### GIN-PROP-016 Truncated subtraction is a totalization, not a converse *(Proposition; trivial)*
m ∸ n = max(m − n, 0) is total on ℕ and agrees with subtraction where subtraction is admissible, but 0 ∸ 1 = 0 is not a solution of 1 + c = 0. Monus is repair 5 (totalization), exactly like `x / 0 = 0` in meadows.

### GIN-PROP-017 The admissibility closures of ℕ *(Proposition; classical constructions restated)*
ℤ is the Grothendieck group of (ℕ, +): pairs (a, b) modulo (a, b) ~ (c, d) iff a + d = b + c, so the element "a − b" *is* the unanswered converse problem kept as data. ℚ is the same construction for multiplication on ℤ × (ℤ ∖ {0}) (GIN-THM-006). In each case the new carrier is the admissibility closure (GIN-DEF-019) for the converse in question, and the exclusion of the zero denominator is forced (GIN-THM-006(2)).

### GIN-HIST-001 Brahmagupta's rules for zero (628 CE) *(Historical result; via secondary sources)*
In the *Brāhmasphuṭasiddhānta* Brahmagupta defined zero as the result of subtracting a number from itself and gave arithmetic rules for zero, including 0/0 = 0; for a nonzero number divided by zero he described a fraction with zero denominator. Bhāskara II later called a quantity with zero divisor *khahara*. (MacTutor; Plofker 2009.)

*GiN's reading (interpretation).* By GIN-COR-001, 0/0 = 0 is not *derivable*: every c solves 0·c = 0. But 0/0 = 0 is a consistent *selection* — the same totalization that meadows and Lean's mathlib adopt (GIN-THM-004). The modern objection is that it cannot be the converse answer, not that it is inconsistent.

## D. Representation, circuits and machines

### GIN-PROP-020 The carry monoid and carry-lookahead *(Proposition; known in substance: Ladner & Fischer 1980, Brent & Kung 1982; CGT reading is GiN's)*
The carry automaton of binary addition has transition monoid {K, P, G} (GIN-DEF-041), with composition "low position, then high position": the result is the high element if it is K or G, and the low element if the high element is P. P is the identity, and every element is idempotent. The carry into position i + 1 is the image of the input carry under the composite of positions 0…i. Since the composition is associative, all carries are prefix products and can be computed by any parallel-prefix network, in depth O(log n).

*Proof.* Direct from the three maps K = const 0, P = id, G = const 1 on {0, 1}. ∎ *Check.* Associativity and identity exhaustively; prefix products vs sequential carries on 500 random additions (tests); prefix adders exhaustively for n ≤ 8 (GIN-EXP-006).

*CGT reading (GIN-REI-005).* Any word of digit pairs compiles to one of three elements: the carry automaton is **arithmetically compilable** in the sense of CGT-DEF-011, and carry-lookahead is that compilation computed in parallel.

### GIN-PROP-021 Ripple-carry cost *(Proposition; elementary, for the construction in `ginsdk.circuits`)*
The n-bit ripple-carry adder (half adder at position 0, full adders XOR/XOR/AND/AND/OR above) has exactly 5n − 3 gates and depth 2n − 1.

*Proof.* 2 + 5(n − 1) gates. The carry out of position 0 has depth 1 and each full adder adds 2 (AND then OR) to the carry path, so the carry out of position n − 1 has depth 2n − 1; sum bits have depth ≤ 2n − 2. ∎ *Check.* n < 200.

### GIN-PROP-023 A divider that never tests the divisor returns all ones *(Proposition; proved here; consistent with the RISC-V specification's stated rationale)*
The n-bit restoring array divider of `ginsdk.circuits` (no test of the divisor anywhere in the circuit) outputs quotient 2ⁿ − 1 and remainder equal to the dividend when the divisor is 0. These are exactly the DIVU/REMU results the RISC-V M extension specifies.

*Proof.* Row i computes T = 2R + aᵢ and keeps T − D if T ≥ D. With D = 0, T ≥ D always, so every quotient bit is 1, and R ← T, so after the row for bit i, R = ⌊a/2ⁱ⌋ < 2^{n−i} ≤ 2ⁿ (the n-bit register suffices); after the last row R = a. ∎

*Check.* n ≤ 6, all dividends; GIN-EXP-007. *Prior work.* The RISC-V specification explains its choice by the simplicity of divider circuitry ("the natural result for simple unsigned divider implementations"); GiN supplies a proof and a gate-level check for one such implementation, not a new fact.

### GIN-THM-005 Addition is finite-state; multiplication is not *(Theorem; known: Büchi 1960; Hodgson 1983; Khoussainov & Nerode 1995; Blumensath & Grädel 2000; Gödel 1931; Church 1936)*
Fix a base b ≥ 2 and read numerals least significant digit first, padded to equal length. (1) The graph of addition {(x, y, x + y)} is recognized by a synchronous finite automaton (the carry automaton), so (ℕ, +) is an automatic structure. (2) The graph of multiplication is not synchronous rational in any presentation in which addition is: otherwise (ℕ, +, ×) would be automatic, every automatic structure has a decidable first-order theory, and the first-order theory of (ℕ, +, ×) is undecidable.

*Classical refinements.* Multiplication by a fixed constant k is finite-state (the carry is bounded by k); remainder modulo a fixed m, read most significant digit first, is finite-state (states = residues, GIN-PROP-009); hence divisibility by m is a regular language in every base.

*Meaning.* The successor, addition, comparison, multiplication by constants and reduction modulo constants live in the class of **regular** operational grammars over numerals; general multiplication does not. The finite carry monoid of GIN-PROP-020 is the algebraic face of (1).

### GIN-PROP-030 The least unrepresentable integer *(Proposition; classical)*
In a binary floating-point format with precision p and emax ≥ p, every integer 0 … 2ᵖ is representable and 2ᵖ + 1 is not.

*Proof.* An integer m < 2ᵖ is m·2⁰ with an integer significand below 2ᵖ; 2ᵖ = 2^{p−1}·2. The numeral of 2ᵖ + 1 is 10…01 with p + 1 significant bits. ∎ *Check / experiment.* Found by search for all four formats (GIN-EXP-012): 17, 2049, 16,777,217, 9,007,199,254,740,993.

### GIN-PROP-031 Which decimals are binary floating-point numbers *(Proposition; elementary, proved here)*
A decimal d/10ᵏ (1 ≤ d < 10ᵏ) is exactly representable in a binary format with p ≥ k and enough exponent range iff 5ᵏ | d. Exactly 2ᵏ − 1 of the 10ᵏ − 1 k-digit decimals are representable.

*Proof.* In lowest terms the denominator is 2ⁱ5ʲ, and a binary fraction must have j = 0, i.e. 5ᵏ | d; then d/10ᵏ = m/2ᵏ with m < 2ᵏ ≤ 2ᵖ. The multiples of 5ᵏ below 10ᵏ = 2ᵏ5ᵏ number 2ᵏ − 1. ∎ *Check.* k ≤ 5 in binary64 (1, 3, 7, 15, 31).

### GIN-PROP-032 Floating-point addition is commutative but not associative *(Proposition; classical)*
Commutativity holds because each sum is the correctly rounded exact sum, which is commutative. Associativity fails: (0.1 + 0.1) + 0.4 = 0.6000000000000001 but 0.1 + (0.1 + 0.4) = 0.6 in binary64. Of the 729 triples of one-digit tenths, 242 are non-associative (GIN-EXP-012).

### GIN-IMP-001 The IEEE simulator agrees with this CPU, results and flags *(Implementation result)*
On x86-64 (SSE scalar arithmetic, gcc 13.3, fenv.h), `ginsdk.ieee` reproduces the hardware's results bit for bit (NaNs compared as NaNs) and all five exception flags on 40,300 binary32 and 40,300 binary64 cases (+, −, ×, ÷, √; random patterns, special values, subnormals, and a targeted tininess family), **after** modelling signaling NaNs (GIN-REJ-002). Scope: one host, one rounding attribute.

### GIN-IMP-002 Machine models agree with measurement *(Implementation result)*
All 14 behaviours of `ginsdk.machine` that can be measured on the host (x86 traps for x/0 and INT_MIN/−1, truncation, Java, Rust debug and release, Go, Python, JS BigInt) agree with real executions (GIN-EXP-004). The AArch64 and RISC-V models are specification models only.

### GIN-IMP-003 Circuits and limb arithmetic are correct on their test domains *(Implementation result)*
All adders exhaustively for n ≤ 8 and randomly to n = 64; multiplier, subtractor and divider exhaustively for n ≤ 6; limb arithmetic against Python `int` on thousands of random operands with limb sizes 8, 16, 32.

## E. Number theory as transition systems

### GIN-PROP-040 Euclid's system and Lamé's bound *(Historical result: Euclid, *Elements* VII.1–2; Lamé 1844)*
The Euclid system (GIN-DEF-050) preserves gcd, terminates because the second component strictly decreases, and the smallest pair a > b > 0 needing k division steps is (F_{k+2}, F_{k+1}). Hence the number of steps is at most log_φ(a) + O(1).

*Check.* All pairs below 700 (step counts 1…13). *Experiment.* GIN-EXP-009: all pairs below 1,200.

### GIN-PROP-041 The exponent's numeral is the program *(Proposition; classical: Knuth TAOCP vol. 2 §4.6.3)*
Left-to-right binary exponentiation runs the exponent program (GIN-DEF-052): ⌊log₂ e⌋ squarings and popcount(e) − 1 multiplications; reading the move word back (M and SM ↦ 1, S ↦ 0) recovers the binary numeral of e. These counts coincide with the production counts of GIN-PROP-007.

*Check.* e < 5,000.

### GIN-PROP-042 The Chinese remainder theorem as a converse problem *(Proposition; classical)*
The system x ≡ rᵢ (mod mᵢ) asks for the converse of x ↦ (x mod mᵢ)ᵢ. The kernel modulo L = lcm(mᵢ) is trivial, so the system is never non-unique mod L; the image condition is pairwise compatibility rᵢ ≡ rⱼ (mod gcd(mᵢ, mⱼ)). The solution set is ∅ or a single residue class mod L.

*Check.* Two moduli below 16, all residues.

### GIN-PROP-043 Primality tests as admissibility checks, and their counterexamples *(Proposition; classical: Fermat; Korselt 1899; Alford, Granville & Pomerance 1994; Miller 1976; Rabin 1980; Sorenson & Webster 2017)*
Fermat's test a^{n−1} ≡ 1 (mod n) is necessary for primality but not sufficient: 341 = 11·31 passes base 2; Carmichael numbers (Korselt: squarefree composite with p − 1 | n − 1 for all p | n) pass every coprime base, and there are infinitely many. The strong (Miller–Rabin) test with the first 13 prime bases is deterministic below ψ₁₃ = 3,317,044,064,679,887,385,961,981.

*Experiment.* GIN-EXP-010 reproduces the published counts below 10⁶: 245 base-2 Fermat pseudoprimes, 46 strong base-2 pseudoprimes, 43 Carmichael numbers; Miller–Rabin agrees with the sieve on every n ≤ 10⁶.

## F. Empirical observations

| ID | Observation | Experiment |
|---|---|---|
| GIN-OBS-001 | Peano addition of n = 2¹⁹ − 1 to itself takes 524,288 rule applications; binary addition 20 bit operations. | EXP-001 |
| GIN-OBS-002 | Mean longest carry chain for random n-bit additions is log₂ n − c with c between 0.66 and 0.84 for n = 4 … 4096; consistent with log₂ n + O(1) (Burks, Goldstine & von Neumann 1946; Knuth 1978). The constant depends on how a chain is counted. | EXP-002 |
| GIN-OBS-003 | The meaning table: `1/0` has 7 distinct outcomes across 15 domains (no solution, ∞, exception, trap, 0, −1, undefined). | EXP-003 |
| GIN-OBS-004 | Constant `1/0` is a compile-time error in Go and Rust, a warning then SIGFPE in C (gcc), and compiles silently then throws ArithmeticException in Java: the same sentence fails at different layers. | EXP-004 |
| GIN-OBS-005 | Go returns −2³¹ for int32 −2³¹/−1 without a panic; Rust panics in both debug and release; x86 C traps; Java returns −2³¹. | EXP-004 |
| GIN-OBS-006 | Python raises ZeroDivisionError for 1.0/0.0, where IEEE 754 (and C, Java, Go, JS) return +∞. | EXP-004 |
| GIN-OBS-007 | The same `a / b` selects `idivl` (x86-64), `sdiv` (AArch64) and `divw` (RISC-V) for int, and `divsd`, `fdiv`, `fdiv.d` for double (clang 18 -O2). | EXP-004 |
| GIN-OBS-008 | In `int q = a / b; if (b == 0) return -1; return q;`, clang 18 at -O2/-O3 **deletes** the zero test (the division already made b = 0 undefined), while gcc 13.3 at -O2 **keeps** it (test + cmove). | EXP-004 |
| GIN-OBS-009 | This x86-64 host detects floating-point tininess **after rounding**: in a targeted family of 300 products just below the smallest normal number, the after-rounding model matches all hardware underflow flags and the before-rounding model mismatches 158 (binary32) / 159 (binary64). | EXP-005 |
| GIN-OBS-010 | Measured log–log slopes of 32-bit limb operations at 16,384 bits: add 1.0, schoolbook mul 2.0, Karatsuba 1.604 (→ log₂ 3 ≈ 1.585), division 1.996; Euclid gcd ≈ 2; modular exponentiation ≈ 2.9 (→ 3). | EXP-008 |
| GIN-OBS-011 | Average Euclid steps for prime n equal (12 ln 2/π²) ln n + Porter's constant − 1.000 ± 0.009 for n = 1009 … 1,000,003; the −1 is the counting convention (Porter's τₙ includes the initial step m mod n with m < n). | EXP-009 |
| GIN-OBS-012 | Pollard rho needs about 0.9–1.13·√p steps to find a prime factor p (20 trials each, p of 10–26 bits). | EXP-010 |
| GIN-OBS-013 | Numeral evaluation: Horner and balanced-schoolbook both have slope → 2 (balanced ≈ 6.7× fewer limb operations at 8,192 digits); balanced-Karatsuba has slope → 1.594. | EXP-011 |
| GIN-OBS-014 | CPython ≥ 3.11 refuses int↔decimal-string conversion beyond 4,300 digits by default, because the conversion is quadratic and was a denial-of-service vector (CVE-2020-10735): a runtime system that treats a cost boundary as an admissibility boundary. | EXP-011 |
| GIN-OBS-015 | Harmonic sum H₂₀₀₀₀ in binary32: forward 10.480757, backward 10.480734, correctly rounded exact 10.480728 (backward error ≈ 5× smaller). | EXP-012 |
| GIN-OBS-016 | 1/x in binary64 for x = 10⁻³²⁰ (subnormal) gives +∞ with *overflow*; for x = 10⁻³³⁰ (which rounds to +0 when parsed) it gives +∞ with *divideByZero*. | EXP-003 |

## G. Frontier assessment (honest)

What session 1 has produced, measured against the mandate's list:

- **A pedagogical and computational framework: yes.** Arithmetic is presented as CGT operational grammars with a four-layer outcome model, an executable SDK, a 20-domain evaluator and cross-validated machine models.
- **A useful unification: partly.** The converse-admissibility reading (GIN-THM-001, COR-001) puts `1/0`, `0/0`, `0 − 1` in ℕ, `7/2` in ℤ, `√−1`, modular inverses and CRT into one image/kernel classification. This is standard linear algebra and ring theory; the unification is in the presentation, and its pedagogical value is the claim, not its mathematical novelty. The extension trilemma (GIN-THM-004) organizes known systems by *which law gives way*.
- **New formal definitions: yes, provisional.** Converse admissibility, the repair taxonomy, admissibility closure, the four-layer outcome. Their usefulness beyond exposition is untested.
- **New algorithms, complexity results or lower bounds: no.** Every algorithm and bound here is classical; measured costs match the textbook exponents.
- **New computational representations: no.** (Bijective numeration, 2-adic two's complement and the projective line are classical.)
- **New insights into machine arithmetic: modest, empirical.** The measured divergence of seven toolchains on one host, the gcc/clang difference on the post-division zero test, the empirical determination of the host's tininess detection, and the observation that RISC-V's choice is what a test-free restoring divider computes are useful, reproducible facts; none is a theorem.
- **Genuinely novel mathematical results: none established.** The most likely candidates for statements not found in the reviewed literature are GIN-PROP-006 (heap ↔ shifted bijective binary) and the pair-level formulation of GIN-THM-006 (every indeterminate form is the null pair); both are elementary and probably folklore. Their novelty is **unverified**, and no claim of priority is made.

## H. Reinterpretations

| ID | Reinterpretation |
|---|---|
| GIN-REI-001 | Number vs numeral is CGT's semantics vs syntax: a numeral is an operation expression, its value the denotation at 0. |
| GIN-REI-002 | A canonical numeral is a CGT grammatical address; zero's address is the empty word. |
| GIN-REI-003 | Inverse operations are converse relations; "undefined" splits into image failure (no solution) and kernel failure (non-unique). |
| GIN-REI-004 | The constructions ℕ → ℤ → ℚ are admissibility repairs that keep the unanswered converse problem as data (GIN-PROP-017). |
| GIN-REI-005 | Carry-lookahead is CGT arithmetic compilation (CGT-DEF-011) of the carry automaton; ripple vs prefix is CGT-THM-004's shape trade-off. |
| GIN-REI-006 | The exponent's numeral is a program (GIN-PROP-041); Church numerals are numbers as iterators (GIN-DEF-013). |
| GIN-REI-007 | "Fixed point" has three technically distinct arithmetic senses — an element with f(x) = x (0 and 1 for squaring; idempotents e² = e in ℤ/n), the limit of an iteration (Newton's method for √a; CGT's PageRank), and the least fixed point of a set operator (ℕ is the least X ⊇ {0} ∪ S(X)) — unified in definition only. |
| GIN-REI-008 | Positional notation is CGT's M-SHARE (grammar compression) applied to unary numerals (GIN-PROP-007). |
| GIN-REI-009 | Long division is a finite transition system on remainders; periodic decimals are its cycles (GIN-PROP-009). |
| GIN-REI-010 | The segment notation a{I}b is formal notation for a marked path, without new content (§B). |

## I. Conjecture

### GIN-CONJ-001 Re-association as a mechanism *(Conjecture / methodological proposal)*
CGT's five mechanisms (CGT-DEF-009) should be extended by **M-ASSOC**: when a computation is a product in an associative operation, re-associating a right-linear evaluation into a balanced tree trades work for depth (prefix adders, balanced numeral evaluation, parallel prefix, repeated squaring), and changes *bit* work only together with a cost model that rewards balanced operands (GIN-OBS-013). Status: the examples are classical; whether M-ASSOC is genuinely distinct from CGT-THM-004's grammar-shape effect, or merely names it, is open (GIN-OPEN-004).

## J. Corrections made during session 1
| ID | Correction |
|---|---|
| C-001 | The first evaluator treated exponents as elements of ℤ/n, so 0^−1 in ℤ/6 evaluated as 0⁵ = 0. Exponents are now integers acting on the domain (GIN-NEG-013). |
| C-002 | The IEEE simulator first treated all NaNs as quiet; GIN-EXP-005 found 101 flag mismatches, all on signaling-NaN operands. Signaling NaNs are now modelled (GIN-REJ-002). |
| C-003 | The simulator's docstring first claimed AArch64 detects tininess after rounding; this was unverified and is removed. The x86-64 claim is now measured (GIN-OBS-009). |
