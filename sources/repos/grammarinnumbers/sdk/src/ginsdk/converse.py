"""Inverse operations as converse relations (GIN-DEF-015 … GIN-DEF-017).

An inverse operation is a *question about a forward operation*.  Writing ⊙ for a
forward operation, the converse problem at (a, b) is

    Sol(a, b) = { c : b ⊙ c = a }.

Division asks a question of multiplication (b·c = a), subtraction asks one of
addition (b + c = a), the square root asks one of squaring (c·c = a), the
logarithm one of exponentiation, the modular inverse one of multiplication mod n.

The *admissibility* of the inverse expression is read off the solution set:

    |Sol| = 0      →  NO SOLUTION   (e.g. 1/0, 0 − 1 in N, √−1 in R, 7/2 in Z)
    |Sol| = 1      →  ADMISSIBLE    (e.g. 6/3, 0/1, 3 − 1)
    |Sol| > 1      →  NOT UNIQUE    (e.g. 0/0, √4 before choosing a branch, 2/2 in Z/6... )

Every function here returns a :class:`SolutionSet` that states the equation, the
solutions (enumerated, or described exactly for infinite carriers) and the
classification.  Nothing returns a bare "undefined".
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, Iterable

NONE, UNIQUE, MULTIPLE = "no-solution", "unique", "non-unique"


@dataclass
class SolutionSet:
    """The solution set of a converse problem, with an exact description."""

    equation: str                    # e.g. "0 · c = 1"
    carrier: str                     # e.g. "Q"
    kind: str                        # NONE | UNIQUE | MULTIPLE
    solutions: list = field(default_factory=list)   # enumerated solutions (possibly a sample)
    size: int | float | str = 0      # exact size: int, math.inf, or a description like "|F|"
    description: str = ""            # exact description, e.g. "every c in Q", "c ≡ 2 (mod 3)"
    reason: str = ""                 # which condition decides the classification

    @property
    def value(self):
        if self.kind != UNIQUE:
            raise ValueError(f"{self.equation} has {self.kind} in {self.carrier}")
        return self.solutions[0]

    def summary(self) -> str:
        if self.kind == UNIQUE:
            return f"{self.equation} in {self.carrier}: unique solution c = {self.solutions[0]}"
        if self.kind == NONE:
            return f"{self.equation} in {self.carrier}: no solution — {self.reason}"
        return f"{self.equation} in {self.carrier}: {self.description} — {self.reason}"


def classify(sols: list) -> str:
    return NONE if not sols else UNIQUE if len(sols) == 1 else MULTIPLE


# ---------------------------------------------------------------------------
# finite carriers: exhaustive
# ---------------------------------------------------------------------------
def converse_finite(op: Callable, carrier: Iterable, a, b, symbol: str = "⊙", name: str = "S") -> SolutionSet:
    """Sol(a, b) = {c ∈ carrier : op(b, c) == a}, by exhaustion."""
    carrier = list(carrier)
    sols = [c for c in carrier if op(b, c) == a]
    kind = classify(sols)
    eq = f"{b} {symbol} c = {a}"
    reason = {NONE: f"no element c of {name} satisfies it",
              UNIQUE: "exactly one element satisfies it",
              MULTIPLE: f"{len(sols)} elements satisfy it"}[kind]
    return SolutionSet(eq, name, kind, sols, len(sols), f"c ∈ {{{', '.join(map(str, sols))}}}", reason)


def divide_mod(a: int, b: int, n: int) -> SolutionSet:
    """Sol(a, b) = {c ∈ Z/n : b·c ≡ a}. Closed form (GIN-THM-002):

    empty iff gcd(b, n) ∤ a; otherwise exactly g = gcd(b, n) solutions, forming the
    coset c₀ + (n/g)·Z/n = c₀ + Ann(b).
    """
    a %= n
    b %= n
    g = math.gcd(b, n)
    eq = f"{b} · c ≡ {a} (mod {n})"
    if a % g:
        return SolutionSet(eq, f"Z/{n}", NONE, [], 0, "∅", f"gcd({b}, {n}) = {g} does not divide {a}")
    step = n // g
    if b == 0:
        sols = list(range(n))
    else:
        c0 = (a // g) * pow(b // g, -1, step) % step
        sols = [c0 + k * step for k in range(g)]
    kind = classify(sols)
    if kind == UNIQUE:
        return SolutionSet(eq, f"Z/{n}", UNIQUE, sols, 1, f"c = {sols[0]}", f"gcd({b}, {n}) = 1, so {b} is a unit")
    return SolutionSet(eq, f"Z/{n}", MULTIPLE, sols, g, f"c ∈ {{{', '.join(map(str, sols))}}} = {sols[0]} + Ann({b})",
                       f"gcd({b}, {n}) = {g} divides {a}; the {g} solutions differ by elements annihilated by {b}")


def annihilator_mod(b: int, n: int) -> list[int]:
    return [c for c in range(n) if (b * c) % n == 0]


# ---------------------------------------------------------------------------
# infinite carriers: exact descriptions
# ---------------------------------------------------------------------------
def divide(a, b, carrier: str = "Q") -> SolutionSet:
    """Sol(a, b) = {c : b·c = a} in N, Z, Q (exact), or R (stated exactly for rational input)."""
    a, b = Fraction(a), Fraction(b)
    eq = f"{_fmt(b)} · c = {_fmt(a)}"
    if b == 0:
        if a == 0:
            return SolutionSet(eq, carrier, MULTIPLE, [0, 1, 2], math.inf, f"every c in {carrier}",
                               "0 · c = 0 holds for every c: the equation does not determine c")
        return SolutionSet(eq, carrier, NONE, [], 0, "∅",
                           f"0 · c = 0 for every c, so 0 · c = {_fmt(a)} would require 0 = {_fmt(a)}")
    c = a / b
    if carrier in ("N", "Z"):
        if c.denominator != 1:
            return SolutionSet(eq, carrier, NONE, [], 0, "∅",
                               f"the only rational solution, {_fmt(c)}, is not an integer ({_fmt(b)} does not divide {_fmt(a)})")
        if carrier == "N" and (c < 0 or a < 0 or b < 0):
            return SolutionSet(eq, carrier, NONE, [], 0, "∅", f"the only integer solution, {_fmt(c)}, is not a natural number")
    return SolutionSet(eq, carrier, UNIQUE, [_num(c)], 1, f"c = {_fmt(c)}",
                       f"{_fmt(b)} ≠ 0, and multiplication by a nonzero element is injective")


def subtract(a, b, carrier: str = "Z") -> SolutionSet:
    """Sol(a, b) = {c : b + c = a}."""
    a, b = Fraction(a), Fraction(b)
    eq = f"{_fmt(b)} + c = {_fmt(a)}"
    c = a - b
    if carrier == "N" and c < 0:
        return SolutionSet(eq, carrier, NONE, [], 0, "∅",
                           f"b + c ≥ b = {_fmt(b)} > {_fmt(a)} for every natural c (the only integer solution {_fmt(c)} is negative)")
    if carrier in ("N", "Z") and c.denominator != 1:
        return SolutionSet(eq, carrier, NONE, [], 0, "∅", "operands are not integers")
    return SolutionSet(eq, carrier, UNIQUE, [_num(c)], 1, f"c = {_fmt(c)}", "addition is cancellative")


def square_root(a, carrier: str = "R") -> SolutionSet:
    """Sol(a) = {c : c·c = a} for rational a, in Q, R or C (exact descriptions)."""
    a = Fraction(a)
    eq = f"c · c = {_fmt(a)}"
    if a == 0:
        return SolutionSet(eq, carrier, UNIQUE, [0], 1, "c = 0", "only 0 squares to 0 (no zero divisors)")
    root = _exact_sqrt(abs(a))
    if carrier in ("N", "Z", "Q"):
        if a < 0:
            return SolutionSet(eq, carrier, NONE, [], 0, "∅", f"squares are ≥ 0 in an ordered field; {_fmt(a)} < 0")
        if root is None:
            return SolutionSet(eq, carrier, NONE, [], 0, "∅", f"{_fmt(a)} is not the square of a rational (its root is irrational)")
        if carrier == "N":
            return SolutionSet(eq, carrier, UNIQUE, [_num(root)], 1, f"c = {_fmt(root)}", "the negative root is not in N")
        return SolutionSet(eq, carrier, MULTIPLE, [_num(root), _num(-root)], 2, f"c ∈ {{{_fmt(root)}, {_fmt(-root)}}}",
                           "two square roots; a principal branch must be chosen to make √ a function")
    r_txt = _fmt(root) if root is not None else f"√{_fmt(abs(a))}"
    if carrier == "R":
        if a < 0:
            return SolutionSet(eq, carrier, NONE, [], 0, "∅", "c·c ≥ 0 for every real c")
        return SolutionSet(eq, carrier, MULTIPLE, [r_txt, "-" + r_txt], 2, f"c ∈ {{{r_txt}, −{r_txt}}}",
                           "two real square roots; the principal branch √ selects the nonnegative one")
    if carrier == "C":
        t = r_txt + ("i" if a < 0 else "")
        return SolutionSet(eq, carrier, MULTIPLE, [t, "-" + t], 2, f"c ∈ {{{t}, −{t}}}",
                           "every nonzero complex number has exactly two square roots")
    raise ValueError(carrier)


def logarithm(a, carrier: str = "R") -> SolutionSet:
    """Sol(a) = {c : e^c = a}. In R: unique iff a > 0. In C: none for a = 0, else infinitely many."""
    a = Fraction(a)
    eq = f"e^c = {_fmt(a)}"
    if a == 0:
        return SolutionSet(eq, carrier, NONE, [], 0, "∅", "e^c ≠ 0 for every c (exp has no zero, in R or in C)")
    if carrier == "R":
        if a < 0:
            return SolutionSet(eq, carrier, NONE, [], 0, "∅", "e^c > 0 for every real c")
        return SolutionSet(eq, carrier, UNIQUE, [f"ln {_fmt(a)}"], 1, f"c = ln {_fmt(a)}", "exp is a bijection R → (0, ∞)")
    if carrier == "C":
        return SolutionSet(eq, carrier, MULTIPLE, [f"Ln {_fmt(a)} + 2πik"], math.inf, f"c = Ln {_fmt(a)} + 2πik, k ∈ Z",
                           "exp is periodic with period 2πi; a branch of log must be chosen")
    raise ValueError(carrier)


def modular_inverse(b: int, n: int) -> SolutionSet:
    s = divide_mod(1, b, n)
    s.equation = f"{b % n} · c ≡ 1 (mod {n})"
    return s


def _exact_sqrt(q: Fraction) -> Fraction | None:
    p, r = q.numerator, q.denominator
    sp, sr = math.isqrt(p), math.isqrt(r)
    return Fraction(sp, sr) if sp * sp == p and sr * sr == r else None


def _num(q: Fraction):
    return q.numerator if q.denominator == 1 else q


def _fmt(q) -> str:
    q = Fraction(q)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


# ---------------------------------------------------------------------------
# the field-of-fractions view: why no extension of a ring can invert 0
# ---------------------------------------------------------------------------
def zero_inverse_collapses(carrier_elems: list, add, mul, zero, one) -> bool:
    """Check GIN-THM-003 on a finite ring: if some z satisfies 0·z = 1 then 1 = 0.

    Returns True iff the ring has an element z with mul(zero, z) == one, which (by the
    theorem) happens only in the zero ring.
    """
    return any(mul(zero, z) == one for z in carrier_elems)


# ---------------------------------------------------------------------------
# fractions as pairs: why 1/0 can be adjoined as one point and 0/0 cannot
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Pair:
    """A formal quotient a/b of integers: the converse problem 'b·c = a' kept as data.

    Two pairs are *related* when a·d = b·c (cross-multiplication).  On Z × (Z∖{0}) this
    is the equivalence that defines Q.  On Z² ∖ {(0, 0)} it is still an equivalence, and
    all pairs (a, 0) form a single class ∞: the projective line Q ∪ {∞}.  The pair (0, 0)
    is related to every pair, which breaks transitivity (GIN-THM-006).
    """

    a: int
    b: int

    @property
    def kind(self) -> str:
        if self.a == 0 and self.b == 0:
            return "null"
        return "infinity" if self.b == 0 else "finite"

    def normal(self) -> "Pair":
        """Canonical representative: lowest terms, positive denominator; ∞ as (1, 0)."""
        if self.kind == "null":
            return self
        if self.b == 0:
            return Pair(1, 0)
        g = math.gcd(self.a, self.b)
        a, b = self.a // g, self.b // g
        return Pair(-a, -b) if b < 0 else Pair(a, b)

    def __str__(self) -> str:
        n = self.normal()
        if n.kind == "null":
            return "(0, 0)"
        if n.kind == "infinity":
            return "∞"
        return str(n.a) if n.b == 1 else f"{n.a}/{n.b}"


def related(p: Pair, q: Pair) -> bool:
    return p.a * q.b == p.b * q.a


def pair_add(p: Pair, q: Pair) -> Pair:
    return Pair(p.a * q.b + q.a * p.b, p.b * q.b)


def pair_neg(p: Pair) -> Pair:
    return Pair(-p.a, p.b)


def pair_sub(p: Pair, q: Pair) -> Pair:
    return pair_add(p, pair_neg(q))


def pair_mul(p: Pair, q: Pair) -> Pair:
    return Pair(p.a * q.a, p.b * q.b)


def pair_div(p: Pair, q: Pair) -> Pair:
    return Pair(p.a * q.b, p.b * q.a)


def pair_of(x) -> Pair:
    """Embed an integer or Fraction, or the string '∞'."""
    if x == "∞":
        return Pair(1, 0)
    x = Fraction(x)
    return Pair(x.numerator, x.denominator)
