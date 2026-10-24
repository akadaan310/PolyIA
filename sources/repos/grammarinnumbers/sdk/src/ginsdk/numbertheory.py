"""Number theory as transition systems (GIN-DEF-050 … GIN-DEF-056).

Each classical algorithm is presented as a grammar of states and moves with an
explicit invariant, and every run can return its full *trace*:

* Euclid:            (a, b) → (b, a mod b),           invariant gcd(a, b)
* extended Euclid:   (r, s, t) rows,                  invariant r = s·a₀ + t·b₀ (Bézout)
* binary gcd:        moves halve / subtract,           invariant gcd up to a power of 2
* exponentiation:    the exponent's binary numeral is the program: 1 ↦ "square, multiply",
                     0 ↦ "square" (GIN-PROP-041)
* CRT:               a converse problem whose solution set is ∅ or one residue class

Primality: trial division, the sieve of Eratosthenes, the Fermat test (with its
counterexamples) and Miller–Rabin with a deterministic base set.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .cost import Cost, charge


# ---------------------------------------------------------------------------
# Euclid
# ---------------------------------------------------------------------------
def euclid_trace(a: int, b: int, cost: Cost | None = None) -> list[tuple[int, int, int]]:
    """Run (a, b) → (b, a mod b) until b = 0. Returns rows (a, b, q) with a = q·b + (a mod b).

    The number of rows is the number of division steps.
    """
    rows = []
    while b:
        q, r = divmod(a, b)
        charge(cost, "division")
        rows.append((a, b, q))
        a, b = b, r
    return rows


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def euclid_steps(a: int, b: int) -> int:
    n = 0
    while b:
        a, b = b, a % b
        n += 1
    return n


@dataclass
class BezoutRow:
    r: int
    s: int
    t: int
    q: int | None = None


def extended_euclid_trace(a: int, b: int) -> list[BezoutRow]:
    """Rows (r_i, s_i, t_i) with the invariant r_i = s_i·a + t_i·b checked at every step."""
    rows = [BezoutRow(a, 1, 0), BezoutRow(b, 0, 1)]
    while rows[-1].r != 0:
        x, y = rows[-2], rows[-1]
        q = x.r // y.r
        y.q = q
        new = BezoutRow(x.r - q * y.r, x.s - q * y.s, x.t - q * y.t)
        assert new.r == new.s * a + new.t * b, "Bézout invariant violated"
        rows.append(new)
    return rows


def bezout(a: int, b: int) -> tuple[int, int, int]:
    """(g, s, t) with g = gcd(a, b) = s·a + t·b."""
    rows = extended_euclid_trace(a, b)
    last = rows[-2]
    return last.r, last.s, last.t


def fibonacci(n: int) -> int:
    x, y = 0, 1
    for _ in range(n):
        x, y = y, x + y
    return x


def lame_worst_pair(steps: int) -> tuple[int, int]:
    """The smallest pair (a, b), a > b, needing ``steps`` division steps: (F_{steps+2}, F_{steps+1})."""
    return fibonacci(steps + 2), fibonacci(steps + 1)


def binary_gcd_trace(a: int, b: int) -> tuple[int, list[str]]:
    """Stein's algorithm with a trace of moves."""
    moves: list[str] = []
    if a == 0 or b == 0:
        return a | b, moves
    k = 0
    while (a | b) & 1 == 0:
        a >>= 1; b >>= 1; k += 1
        moves.append("halve both")
    while a & 1 == 0:
        a >>= 1
        moves.append("halve a")
    while b:
        while b & 1 == 0:
            b >>= 1
            moves.append("halve b")
        if a > b:
            a, b = b, a
            moves.append("swap")
        b -= a
        moves.append("subtract")
    return a << k, moves


# ---------------------------------------------------------------------------
# modular arithmetic
# ---------------------------------------------------------------------------
def mod_inverse(a: int, n: int) -> int | None:
    """The unique c with a·c ≡ 1 (mod n), or None if gcd(a, n) ≠ 1 (no solution)."""
    g, s, _ = bezout(a % n, n)
    return s % n if g == 1 else None


def crt(residues: list[int], moduli: list[int]) -> tuple[int, int] | None:
    """Solve x ≡ r_i (mod m_i). Returns (x, lcm) — the solution set is x + lcm·Z — or None.

    Works for non-coprime moduli; the system is solvable iff r_i ≡ r_j (mod gcd(m_i, m_j))
    for all i, j.
    """
    x, m = 0, 1
    for r, n in zip(residues, moduli):
        g, s, _ = bezout(m, n)
        if (r - x) % g:
            return None
        lcm = m // g * n
        x = (x + (r - x) // g * s % (n // g) * m) % lcm
        m = lcm
    return x, m


def powmod_trace(base: int, e: int, m: int) -> tuple[int, list[tuple[str, str, int]]]:
    """Left-to-right binary exponentiation; the exponent's numeral is the program.

    Returns (result, rows) where each row is (bit, moves, accumulator), moves ∈
    {"S", "SM"} (square; square then multiply).  The leading 1 bit is the start move "M".
    """
    rows: list[tuple[str, str, int]] = []
    if e == 0:
        return 1 % m, rows
    bits = bin(e)[2:]
    acc = base % m
    rows.append((bits[0], "M", acc))
    for bit in bits[1:]:
        acc = acc * acc % m
        mv = "S"
        if bit == "1":
            acc = acc * base % m
            mv = "SM"
        rows.append((bit, mv, acc))
    return acc, rows


def powmod_count(e: int) -> dict[str, int]:
    """Squarings and multiplications used by left-to-right binary exponentiation:
    squarings = ⌊log₂ e⌋, multiplications = popcount(e) − 1 (GIN-PROP-041)."""
    if e == 0:
        return {"square": 0, "multiply": 0}
    return {"square": e.bit_length() - 1, "multiply": bin(e).count("1") - 1}


# ---------------------------------------------------------------------------
# primes
# ---------------------------------------------------------------------------
def sieve(n: int, cost: Cost | None = None) -> list[int]:
    """Primes ≤ n by the sieve of Eratosthenes; charges one ``cross`` per crossing-out."""
    if n < 2:
        return []
    is_p = bytearray([1]) * (n + 1)
    is_p[0] = is_p[1] = 0
    for p in range(2, math.isqrt(n) + 1):
        if is_p[p]:
            for q in range(p * p, n + 1, p):
                is_p[q] = 0
                charge(cost, "cross")
    return [i for i in range(n + 1) if is_p[i]]


def is_prime_trial(n: int, cost: Cost | None = None) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        charge(cost, "division")
        return n == 2
    d = 3
    while d * d <= n:
        charge(cost, "division")
        if n % d == 0:
            return False
        d += 2
    return True


def fermat_test(n: int, a: int) -> bool:
    """True iff a^(n−1) ≡ 1 (mod n): 'n is a probable prime to base a'."""
    return pow(a, n - 1, n) == 1


def is_carmichael(n: int) -> bool:
    """Korselt's criterion: n composite, squarefree, and p − 1 | n − 1 for every prime p | n."""
    if n < 3 or n % 2 == 0 or is_prime_trial(n):
        return False
    f = factorize(n)
    return all(e == 1 for e in f.values()) and all((n - 1) % (p - 1) == 0 for p in f)


def strong_probable_prime(n: int, a: int) -> bool:
    """One round of the Miller–Rabin test to base a."""
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2; s += 1
    x = pow(a, d, n)
    if x in (1, n - 1):
        return True
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False


# With the first 13 primes as bases the strong-pseudoprime test is deterministic
# for n < 3 317 044 064 679 887 385 961 981 (Sorenson & Webster 2017).
MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
MR_BOUND = 3_317_044_064_679_887_385_961_981


def is_prime(n: int) -> bool:
    """Deterministic Miller–Rabin for n < MR_BOUND; probabilistic-by-fixed-bases beyond."""
    if n < 2:
        return False
    for p in MR_BASES:
        if n % p == 0:
            return n == p
    return all(strong_probable_prime(n, a) for a in MR_BASES)


def pollard_rho(n: int, c: int = 1, cost: Cost | None = None) -> int | None:
    """Floyd-cycle Pollard rho with f(x) = x² + c. Returns a nontrivial factor or None."""
    if n % 2 == 0:
        return 2
    x = y = 2
    d = 1
    while d == 1:
        x = (x * x + c) % n
        y = (y * y + c) % n
        y = (y * y + c) % n
        charge(cost, "step")
        d = math.gcd(abs(x - y), n)
    return d if d != n else None


def factorize(n: int) -> dict[int, int]:
    """Prime factorization {p: e}. Trial division by small primes, then Pollard rho."""
    if n < 1:
        raise ValueError("factorize needs n ≥ 1")
    f: dict[int, int] = {}
    for p in (2, 3, 5, 7, 11, 13):
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
    stack = [n] if n > 1 else []
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        if is_prime(m):
            f[m] = f.get(m, 0) + 1
            continue
        d = None
        c = 1
        while d is None:
            d = pollard_rho(m, c)
            c += 1
        stack += [d, m // d]
    return dict(sorted(f.items()))


# ---------------------------------------------------------------------------
# arithmetic functions
# ---------------------------------------------------------------------------
def divisors(n: int) -> list[int]:
    small = [d for d in range(1, math.isqrt(n) + 1) if n % d == 0]
    return sorted(set(small + [n // d for d in small]))


def phi(n: int) -> int:
    r = n
    for p in factorize(n):
        r = r // p * (p - 1)
    return r


def mobius(n: int) -> int:
    f = factorize(n)
    if any(e > 1 for e in f.values()):
        return 0
    return -1 if len(f) % 2 else 1


def sigma(n: int) -> int:
    return sum(divisors(n))
