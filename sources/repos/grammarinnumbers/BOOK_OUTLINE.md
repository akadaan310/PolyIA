# Book Outline

**Title:** *Grammar in Numbers*
**Subtitle:** *Arithmetic, Number Theory, and the Computational Grammar of Number*
**Founding Principal Researcher:** Abed Kadaan
**Relationship:** a specialized frontier volume of the Computational Grammar Theory program; independently buildable; links to CGT but does not depend on it.

Alternative subtitles considered: *What 0, 1, 2, 3 Compute*; *The Admissibility of Arithmetic*; *Arithmetic as a Computational Language*. The working subtitle is kept because it names all three subjects.

## How the research changed the mandate's outline

The mandate's fourteen-part outline was a good starting point. The evidence of session 1 changed it in four ways:

1. **"Numerals as programs" became its own part** (II), between "What is a number?" and arithmetic. The digit-grammar view (numerals = operation expressions, addresses, compilation, compression) is what connects GiN to CGT most precisely, and it is needed before 1 + 1 = 10₂ can be explained.
2. **"Division as a converse" is the spine of Parts III–IV.** The image/kernel theorem (GIN-THM-001) organizes subtraction, division, roots, logarithms, modular inverses and the CRT; division by zero is its most important instance rather than a separate topic.
3. **"Extending the grammar" gets a chapter** (10) of its own, built around the extension trilemma (GIN-THM-004) and the pair theorem (GIN-THM-006).
4. **Mandate Parts IX (number systems), X (number theory) and XI (algorithms) were merged** into Parts VI–VII, because the research found the algorithms to be the clearest presentation of the number theory as transition systems.

## Structure (as built in `book/content/book.json`)

### Part I — What Is a Number?
1. Number, Numeral, Digit, Machine — the four layers.
2. The Smallest Grammar: 0 → 1 → 2 → 3 → 4 — successor, segments, `0{1,2,3}4`.
3. Recursion, Induction and the Least Fixed Point — Peano, primitive recursion with counted cost, Church numerals, three senses of fixed point.

### Part II — Numerals as Programs
4. Positional Notation as an Operational Grammar — digit grammars, canonical numerals, zero's empty address, bijective notation, the CGT heap.
5. 1 + 1 = 10₂: Value and Representation — binary, carries, the cost of the successor, two's complement as 2-adic, periodic expansions.

### Part III — Arithmetic as Transition
6. Addition and Subtraction — five readings of 1 + 1; 0 − 1 and the construction of ℤ.
7. Multiplication — 2 × 3 vs 3 × 2; why ×0 gives 0 (four derivations); numerals as straight-line programs; why multiplication is not finite-state.
8. Division as a Converse — 6 / 3 six ways; the image/kernel theorem; division in ℤ/n.

### Part IV — The Boundary of Zero
9. The Grammar of Division by Zero — 1/0 vs 0/0 vs 0/1; the x/0, 0/x table; symbolic vs numeric; limits.
10. Extending the Grammar: What Gives Way — no ring inverts 0; the trilemma; fractions as pairs and the null pair; IEEE, meadows, wheels; Brahmagupta.
11. The Grammar of Zero and One — zero vs NULL, NaN, empty, false, undefined; one as identity and generator.

### Part V — Machines That Compute Arithmetic
12. From Symbol to Instruction — lexing to `idiv`; seven toolchains measured; undefined behaviour and the optimizer.
13. Finite Width and Floating Point — overflow policies; IEEE 754; flags; representation boundaries; a simulator checked against hardware.
14. Arithmetic Circuits — gates, adders, the carry monoid, prefix adders, multiplier, divider, and what a divider does with 0.

### Part VI — Number Systems as Grammars
15. ℕ, ℤ, ℚ, ℝ, ℂ, ℤ/n, ℤ_p — closure, identities, inverses, order, representations; repairs and admissibility closures.

### Part VII — Number Theory and Its Algorithms
16. Divisibility and Euclid — the Euclid system, Lamé, Bézout, average steps.
17. Congruences and the Chinese Remainder Theorem — ℤ/n, inverses, CRT and linear Diophantine equations as converse problems.
18. Exponentiation and Primality — the exponent program; Fermat and its counterexamples; Miller–Rabin; sieves; Pollard rho.

### Part VIII — The Cost of Arithmetic
19. Bit Complexity — unit cost vs bit cost; measured exponents; numeral evaluation shapes; the CPython conversion limit.

### Part IX — Arithmetic, Computation and CGT
20. What Is the Computational Grammar of Number? — the answer of session 1; the CGT concept map; the honest frontier.
21. Open Problems.

### Appendices
A. Notation and conventions. B. Reproducibility, the SDK and the laboratory.

## The laboratory (website)
- **Arithmetic Lab** — expression → tokens, parse tree, layered outcome, converse equation, steps, representation, cost, in any of 20+ domains; validated against SDK fixtures.
- **Machine Lab** — one expression across all domains, side by side.
- **Zero Explorer** — the line y = b·c against y = a: one intersection, none, or all; and the ℤ/n multiplication grid.
- **Successor & Numeral Lab** — `a{I}b` parser, transition diagram, numerals of n in unary, bijective, binary, decimal, balanced ternary; compilation.
- **Carry Lab** — K/P/G per position, carries, ripple vs prefix composition.
- **Circuit Lab** — toggleable full adder and 4-bit ripple adder.
- **Float Lab** — IEEE fields, exact value, neighbours, ulp for binary16/32/64.
- **Pairs Lab** — projective arithmetic on pairs; the null pair.
- **Euclid and Exponent Labs** — traces with invariants.
