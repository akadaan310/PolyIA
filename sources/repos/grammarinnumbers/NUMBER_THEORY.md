# Number Theory as Transition Systems

Only after arithmetic has been developed structurally does GiN turn to number theory. For each topic: the grammar (states and moves), the invariant, what is preserved, what is expensive, and which representation makes it efficient. Results: `RESULTS.md` §E; experiments GIN-EXP-009, 010.

| Topic | States | Legal moves | Invariant / preserved | Expensive | Efficient representation |
|---|---|---|---|---|---|
| divisibility b \| a | — | the converse problem bc = a (image condition) | — | as costly as one division (GIN-OPEN-002) | any; mod m is finite-state MSB-first |
| gcd (Euclid) | (a, b) | (a, b) → (b, a mod b) if b ≠ 0 | gcd(a, b) | Θ(L²) bit ops; ≤ log_φ a steps (Lamé) | positional; binary gcd uses shifts |
| Bézout | rows (r, s, t) | r_{i+1} = r_{i−1} − qᵢrᵢ (same for s, t) | rᵢ = sᵢa + tᵢb | coefficient growth bounded by b/(2g) | — |
| lcm | — | lcm = \|ab\|/gcd | — | one gcd | — |
| modular arithmetic ℤ/n | residues | +, −, × mod n; / when admissible | the residue class | division needs a gcd | residues 0 … n−1 |
| congruences, CRT | residue tuples | converse of x ↦ (x mod mᵢ) | — | pairwise gcds | mixed radix |
| prime factorization | multisets of primes | split a composite | the product | best known methods are super-polynomial in L | factor lists |
| fundamental theorem of arithmetic | — | — | uniqueness of factorization in ℤ (a unique-normal-form property of the multiplicative grammar) | — | — |
| primality: trial division | candidate divisors | d ← d + 2 while d² ≤ n | — | ≈ √n/2 divisions (exponential in L) | — |
| primality: sieve | a bit array | cross out multiples | — | ~ n ln ln n crossings | precomputation (CGT M-PRE) |
| Fermat / Miller–Rabin | witnesses a | modular exponentiation | — | O(L³) bit ops per base, schoolbook | exponent program (GIN-PROP-041) |
| modular exponentiation | accumulator | S (square) / SM (square, multiply) per exponent bit | acc = x^{prefix of e} | ⌊log₂ e⌋ squarings, popcount − 1 multiplications | binary (or windowed) exponent |
| Pollard rho | (x, y) | x ← f(x), y ← f(f(y)) | — | ~ √p steps for the smallest factor p | Floyd cycle detection |
| arithmetic functions φ, μ, σ | — | from the factorization | multiplicativity | factoring | factor lists |
| recurrence sequences (Fibonacci) | (F_k, F_{k+1}) | (x, y) → (y, x + y) | — | the worst case of Euclid (Lamé) | matrix powers by the exponent program |
| Diophantine ax + by = c | — | converse of (x, y) ↦ ax + by | — | one extended gcd | solvable iff gcd(a, b) \| c; solutions form a coset of the kernel {(bt/g, −at/g)} — GIN-THM-001 again |

## Counterexamples
Fermat pseudoprimes (341 base 2), Carmichael numbers (561; 43 below 10⁶), strong pseudoprimes (2047 base 2; 46 below 10⁶): admissibility tests that admit composites (GIN-NEG-002).

## Does CGT reveal useful structural decompositions?
Three, none of them new algorithms: (1) the **image/kernel** reading unifies division, modular inverses, linear Diophantine equations and the CRT (GIN-THM-001, PROP-042); (2) the **exponent program** shows square-and-multiply, addition chains and SLP compression of unary numerals as one object (GIN-PROP-007, 041); (3) the **finite transition system on remainders** explains periodic expansions and divisibility automata (GIN-PROP-009, THM-005). No improvement over classical algorithms was found or claimed.
