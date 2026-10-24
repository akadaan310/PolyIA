"""Numerals as operation expressions (GIN-DEF-005 … GIN-DEF-008).

A *digit grammar* with base b and digit set D has one move per digit,

    d :  x  ↦  b·x + d ,

acting on the integers.  A numeral is a word over D, read most significant
digit first, and its value is the denotation of the word applied to the
start point 0:

    value(d₁ d₂ … d_k) = ⟦d₁ d₂ … d_k⟧(0).

This single definition covers ordinary base-b notation (D = {0,…,b−1}),
bijective base-b notation (D = {1,…,b}), unary/Peano notation (b = 1,
D = {1}, the move is the successor), balanced ternary (b = 3, D = {−1,0,1})
and redundant digit sets.  The *numeral* is syntax; the *number* is its
denotation (GIN-DEF-001/002).

Words compile to affine maps x ↦ a·x + c (the transition monoid of the
grammar is a monoid of affine maps), which gives the concatenation law
value(uv) = value(u)·b^|v| + value(v) and parallel evaluation by
associativity (GIN-PROP-005).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .cost import Cost, charge

Word = tuple  # a tuple of digits, most significant first


# ---------------------------------------------------------------------------
# affine maps: the transition monoid of a digit grammar
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Affine:
    """The map x ↦ a·x + c on the integers."""

    a: int
    c: int

    def __call__(self, x: int) -> int:
        return self.a * x + self.c

    def then(self, other: "Affine") -> "Affine":
        """Sequential composition: first ``self``, then ``other``.

        other(self(x)) = other.a·(a·x + c) + other.c.
        """
        return Affine(other.a * self.a, other.a * self.c + other.c)

    def __repr__(self) -> str:
        return f"x ↦ {self.a}·x + {self.c}"


IDENTITY = Affine(1, 0)

_SYMBOLS = "0123456789abcdefghijklmnopqrstuvwxyz"


class DigitGrammar:
    """A positional numeral grammar (base ``b``, digit set ``digits``).

    Moves act on integers by d : x ↦ b·x + d.  The start point is 0.
    """

    def __init__(self, base: int, digits: Iterable[int], name: str | None = None,
                 symbols: dict[int, str] | None = None) -> None:
        if base < 1:
            raise ValueError("base must be ≥ 1")
        self.base = base
        self.digits = tuple(sorted(set(digits)))
        if not self.digits:
            raise ValueError("digit set must be non-empty")
        self.name = name or f"base {base}, digits {set(self.digits)}"
        if symbols is None:
            symbols = {}
            for d in self.digits:
                if 0 <= d < len(_SYMBOLS):
                    symbols[d] = _SYMBOLS[d]
                elif d == -1:
                    symbols[d] = "T"          # balanced-ternary convention: T = −1
                else:
                    symbols[d] = f"[{d}]"
            if base == 1 and self.digits == (1,):
                symbols = {1: "S"}
        self.symbols = symbols
        self._unsym = {v: k for k, v in symbols.items()}

    # -- the semantics ------------------------------------------------------
    def move(self, d: int) -> Affine:
        if d not in self.digits:
            raise ValueError(f"{d} is not a digit of {self.name}")
        return Affine(self.base, d)

    def denote(self, word: Sequence[int], start: int = 0, cost: Cost | None = None) -> int:
        """Value of ``word`` applied to ``start`` (Horner's rule, left to right).

        Cost: one ``step`` per digit (one move application).
        """
        x = start
        for d in word:
            if d not in self.digits:
                raise ValueError(f"{d!r} is not a digit of {self.name}")
            x = self.base * x + d
            charge(cost, "step")
        return x

    def compile(self, word: Sequence[int]) -> Affine:
        """The affine map denoted by ``word`` (an element of the transition monoid)."""
        f = IDENTITY
        for d in word:
            f = f.then(self.move(d))
        return f

    # -- syntax ----------------------------------------------------------------
    def render(self, word: Sequence[int]) -> str:
        return "".join(self.symbols[d] for d in word) if word else "ε"

    def parse(self, text: str) -> Word:
        if text in ("", "ε"):
            return ()
        try:
            return tuple(self._unsym[ch] for ch in text)
        except KeyError as e:  # pragma: no cover - error path
            raise ValueError(f"symbol {e.args[0]!r} is not a digit of {self.name}") from None

    # -- addresses (canonical numerals) -----------------------------------------
    def is_complete_residue_system(self) -> bool:
        """True iff the digits are pairwise incongruent mod b and cover every residue."""
        b = self.base
        return len(self.digits) == b and len({d % b for d in self.digits}) == b

    def expand(self, n: int, max_digits: int = 10_000) -> tuple[Word, str]:
        """Digit expansion of ``n`` by the residue algorithm, least significant digit first.

        Requires a complete residue system.  Returns (digits_lsb_first, status) where
        status is ``"terminated"`` (a finite numeral was found), ``"periodic"`` (the
        state repeated: the expansion is an infinite, eventually periodic word, as for
        negative integers in ordinary base b, which is their b-adic expansion), or
        ``"cut"`` (``max_digits`` reached).
        """
        if not self.is_complete_residue_system():
            raise ValueError("expand needs a digit set that is a complete residue system mod b")
        b = self.base
        out: list[int] = []
        seen: set[int] = set()
        while n != 0:
            if n in seen:
                return tuple(out), "periodic"
            seen.add(n)
            d = next(dd for dd in self.digits if (n - dd) % b == 0)
            out.append(d)
            n = (n - d) // b
            if len(out) >= max_digits:
                return tuple(out), "cut"
        return tuple(out), "terminated"

    def address(self, n: int) -> Word:
        """The canonical numeral of ``n``: the shortlex-least word w with ⟦w⟧(0) = n.

        For complete residue systems this is computed by the residue algorithm; the
        address of 0 is the **empty word**.  Raises ValueError if no finite numeral
        denotes n (for example −1 in ordinary base 2).
        """
        if self.is_complete_residue_system():
            digits, status = self.expand(n)
            if status != "terminated":
                raise ValueError(f"{n} has no finite numeral in {self.name} ({status} expansion)")
            return tuple(reversed(digits))
        w = self._search_address(n, max_len=64)
        if w is None:
            raise ValueError(f"no numeral of length ≤ 64 denotes {n} in {self.name}")
        return w

    def _search_address(self, n: int, max_len: int) -> Word | None:
        """Shortlex search (used for digit sets that are not residue systems)."""
        frontier = {0: ()}
        if n == 0:
            return ()
        for _ in range(max_len):
            nxt: dict[int, Word] = {}
            for x, w in sorted(frontier.items(), key=lambda kv: kv[1]):
                for d in self.digits:
                    y = self.base * x + d
                    cand = w + (d,)
                    if y not in nxt or cand < nxt[y]:
                        nxt[y] = cand
            if n in nxt:
                return nxt[n]
            # prune values that can no longer reach n (only for nonnegative digit sets)
            if min(self.digits) >= 0 and self.base >= 2:
                nxt = {x: w for x, w in nxt.items() if x <= n}
            frontier = nxt
        return None

    def words_denoting(self, n: int, max_len: int) -> list[Word]:
        """All words of length ≤ max_len whose value is n (exhaustive; small inputs only)."""
        out: list[Word] = []
        layer: list[tuple[int, Word]] = [(0, ())]
        if n == 0:
            out.append(())
        for _ in range(max_len):
            new = []
            for x, w in layer:
                for d in self.digits:
                    y = self.base * x + d
                    new.append((y, w + (d,)))
                    if y == n:
                        out.append(w + (d,))
            layer = new
        return out

    def is_canonical(self, word: Sequence[int]) -> bool:
        try:
            return tuple(word) == self.address(self.denote(word))
        except ValueError:
            return False

    def __repr__(self) -> str:
        return f"DigitGrammar({self.name})"


# Standard instances -----------------------------------------------------------
def standard(b: int) -> DigitGrammar:
    """Ordinary base-b notation: digits 0 … b−1."""
    if b < 2:
        raise ValueError("standard notation needs b ≥ 2")
    return DigitGrammar(b, range(b), name=f"standard base {b}")


def bijective(b: int) -> DigitGrammar:
    """Bijective base-b notation: digits 1 … b (no zero digit). b = 1 is unary."""
    if b == 1:
        return DigitGrammar(1, [1], name="unary (successor)")
    sym = {d: (_SYMBOLS[d] if d < 10 else _SYMBOLS[d]) for d in range(1, b + 1)}
    if b == 10:
        sym[10] = "A"
    return DigitGrammar(b, range(1, b + 1), name=f"bijective base {b}", symbols=sym)


UNARY = bijective(1)
BINARY = standard(2)
DECIMAL = standard(10)
BALANCED_TERNARY = DigitGrammar(3, (-1, 0, 1), name="balanced ternary", symbols={-1: "T", 0: "0", 1: "1"})


# ---------------------------------------------------------------------------
# concatenation, parallel evaluation and the heap correspondence
# ---------------------------------------------------------------------------
def concat_value(g: DigitGrammar, u: Sequence[int], v: Sequence[int]) -> int:
    """value(uv) = value(u)·b^|v| + value(v)  (GIN-PROP-005)."""
    return g.denote(u) * g.base ** len(v) + g.denote(v)


def parallel_value(g: DigitGrammar, word: Sequence[int], cost: Cost | None = None) -> int:
    """Evaluate a numeral by a balanced tree of affine compositions.

    Charges ``compose`` per composition and records the tree ``depth`` (rounds).
    Work is |w| − 1 compositions; depth is ⌈log₂ |w|⌉.  Horner's rule does the same
    number of compositions in depth |w|.  (Bit cost is a different matter: see
    GIN-EXP-011.)
    """
    maps = [g.move(d) for d in word]
    if not maps:
        return 0
    depth = 0
    while len(maps) > 1:
        nxt = []
        for i in range(0, len(maps) - 1, 2):
            nxt.append(maps[i].then(maps[i + 1]))
            charge(cost, "compose")
        if len(maps) % 2:
            nxt.append(maps[-1])
        maps = nxt
        depth += 1
    if cost is not None:
        cost.counts["depth"] = max(cost.counts["depth"], depth)
    return maps[0](0)


def heap_word(n: int) -> str:
    """The CGT heap address of node n ≥ 1: binary of n without its leading 1, as L/R."""
    if n < 1:
        raise ValueError("heap nodes are numbered from 1")
    return bin(n)[3:].replace("0", "L").replace("1", "R")


def bijective2_as_heap(n: int) -> str:
    """Bijective base-2 numeral of n with digit 1 ↦ L and 2 ↦ R.

    GIN-PROP-006: this equals ``heap_word(n + 1)`` for every n ≥ 0; the conjugacy
    x ↦ x + 1 carries the bijective base-2 grammar to the CGT heap grammar.
    """
    w = bijective(2).address(n)
    return "".join("L" if d == 1 else "R" for d in w)


def twos_complement_from_2adic(n: int, width: int) -> str:
    """First ``width`` digits of the base-2 residue expansion of n, as a bit string (MSB first).

    For −2^(width−1) ≤ n < 2^(width−1) this is exactly the two's-complement encoding of n
    (GIN-PROP-008): two's complement is the truncated 2-adic expansion.
    """
    g = BINARY
    digits: list[int] = []
    x = n
    for _ in range(width):
        d = x % 2
        digits.append(d)
        x = (x - d) // 2
    return "".join(str(d) for d in reversed(digits))


# ---------------------------------------------------------------------------
# expansions of rationals: finite, periodic
# ---------------------------------------------------------------------------
def periodic_expansion(q, base: int = 10) -> str:
    """Positional expansion of a rational in ``base`` with the repeating block in parentheses.

    Example: periodic_expansion(Fraction(1, 3), 10) == '0.(3)'; in base 2 it is '0.(01)'.
    The expansion terminates iff every prime factor of the reduced denominator divides
    the base (GIN-PROP-009).
    """
    from fractions import Fraction
    q = Fraction(q)
    sign = "−" if q < 0 else ""
    q = abs(q)
    ip, rem = divmod(q.numerator, q.denominator)
    d = q.denominator
    int_digits = ""
    x = ip
    if x == 0:
        int_digits = "0"
    while x:
        int_digits = _SYMBOLS[x % base] + int_digits
        x //= base
    if rem == 0:
        return sign + int_digits
    seen: dict[int, int] = {}
    frac = []
    while rem and rem not in seen:
        seen[rem] = len(frac)
        rem *= base
        frac.append(_SYMBOLS[rem // d])
        rem %= d
    if rem == 0:
        return f"{sign}{int_digits}." + "".join(frac)
    k = seen[rem]
    return f"{sign}{int_digits}." + "".join(frac[:k]) + "(" + "".join(frac[k:]) + ")"
