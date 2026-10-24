"""Arithmetic circuits as grammars of wires and gates (GIN-DEF-040 … GIN-DEF-044).

A *circuit* is a directed acyclic graph whose sources are input wires (and the
constants 0, 1) and whose internal nodes are gates from a fixed basis.  Its
admissibility conditions are syntactic: every gate input is an existing wire, and
wires are defined before use (acyclicity).  Its semantics is the Boolean function
computed; its cost profile is (gate count, depth).

The module builds the classical arithmetic circuits:

* half and full adders (also a NAND-only full adder);
* ripple-carry, Sklansky, Kogge–Stone and Brent–Kung adders — the last three are
  *parallel prefix* adders over the carry monoid {K, P, G} (GIN-PROP-020);
* two's-complement subtractor, array multiplier, and a restoring array divider,
  whose behaviour on a zero divisor is analysed in GIN-PROP-023.

Everything is verified exhaustively for small widths in the tests and in GIN-EXP-006/007.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

BASIS = {
    "NOT": lambda a: 1 - a,
    "AND": lambda a, b: a & b,
    "OR": lambda a, b: a | b,
    "XOR": lambda a, b: a ^ b,
    "NAND": lambda a, b: 1 - (a & b),
}


@dataclass
class Circuit:
    name: str
    inputs: list[str] = field(default_factory=list)
    gates: list[tuple[str, str, tuple[str, ...]]] = field(default_factory=list)  # (out, type, ins)
    outputs: list[str] = field(default_factory=list)
    _n: int = 0

    # -- construction -----------------------------------------------------------
    def input(self, name: str) -> str:
        self.inputs.append(name)
        return name

    def gate(self, kind: str, *ins: str) -> str:
        if kind not in BASIS:
            raise ValueError(f"gate {kind} not in basis")
        known = set(self.inputs) | {g[0] for g in self.gates} | {"0", "1"}
        for w in ins:
            if w not in known:
                raise ValueError(f"inadmissible connection: wire {w!r} is not defined before gate {kind}")
        self._n += 1
        out = f"w{self._n}"
        self.gates.append((out, kind, tuple(ins)))
        return out

    # -- semantics ------------------------------------------------------------------
    def evaluate(self, assignment: dict[str, int]) -> dict[str, int]:
        val = {"0": 0, "1": 1, **assignment}
        for out, kind, ins in self.gates:
            val[out] = BASIS[kind](*(val[i] for i in ins))
        return val

    def run(self, assignment: dict[str, int]) -> list[int]:
        v = self.evaluate(assignment)
        return [v[o] for o in self.outputs]

    # -- cost ----------------------------------------------------------------------------
    @property
    def size(self) -> int:
        return len(self.gates)

    def depth(self) -> int:
        d = {w: 0 for w in self.inputs + ["0", "1"]}
        for out, _kind, ins in self.gates:
            d[out] = 1 + max(d[i] for i in ins)
        return max((d[o] for o in self.outputs), default=0)

    def gate_counts(self) -> dict[str, int]:
        c: dict[str, int] = {}
        for _o, k, _i in self.gates:
            c[k] = c.get(k, 0) + 1
        return c


# ---------------------------------------------------------------------------
# helpers to drive multi-bit circuits with integers
# ---------------------------------------------------------------------------
def bits_of(x: int, n: int) -> list[int]:
    """Little-endian bits of x mod 2^n."""
    return [(x >> i) & 1 for i in range(n)]


def int_of(bits: Sequence[int]) -> int:
    return sum(b << i for i, b in enumerate(bits))


def apply_words(c: Circuit, **words: tuple[int, int]) -> list[int]:
    """Drive inputs named like a0..a{n-1} from integer words: apply_words(c, a=(x, n), b=(y, n))."""
    asg: dict[str, int] = {}
    for name, (x, n) in words.items():
        for i, bit in enumerate(bits_of(x, n)):
            asg[f"{name}{i}"] = bit
    return c.run(asg)


# ---------------------------------------------------------------------------
# adders
# ---------------------------------------------------------------------------
def half_adder() -> Circuit:
    c = Circuit("half adder")
    a, b = c.input("a"), c.input("b")
    s = c.gate("XOR", a, b)
    k = c.gate("AND", a, b)
    c.outputs = [s, k]          # sum, carry
    return c


def _full_adder_into(c: Circuit, a: str, b: str, cin: str) -> tuple[str, str]:
    p = c.gate("XOR", a, b)
    s = c.gate("XOR", p, cin)
    g = c.gate("AND", a, b)
    t = c.gate("AND", p, cin)
    cout = c.gate("OR", g, t)
    return s, cout


def full_adder() -> Circuit:
    c = Circuit("full adder")
    a, b, cin = c.input("a"), c.input("b"), c.input("cin")
    s, cout = _full_adder_into(c, a, b, cin)
    c.outputs = [s, cout]
    return c


def full_adder_nand() -> Circuit:
    """The classical 9-gate NAND-only full adder."""
    c = Circuit("full adder (NAND only)")
    a, b, cin = c.input("a"), c.input("b"), c.input("cin")
    n1 = c.gate("NAND", a, b)
    n2 = c.gate("NAND", a, n1)
    n3 = c.gate("NAND", b, n1)
    x = c.gate("NAND", n2, n3)          # a XOR b
    n5 = c.gate("NAND", x, cin)
    n6 = c.gate("NAND", x, n5)
    n7 = c.gate("NAND", cin, n5)
    s = c.gate("NAND", n6, n7)          # x XOR cin
    cout = c.gate("NAND", n5, n1)       # (a AND b) OR (x AND cin)
    c.outputs = [s, cout]
    return c


def ripple_adder(n: int, with_cin: bool = False) -> Circuit:
    """n-bit ripple-carry adder: outputs s0..s{n-1}, carry-out (n+1 output bits)."""
    c = Circuit(f"{n}-bit ripple-carry adder")
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    carry = c.input("cin") if with_cin else "0"
    outs = []
    for i in range(n):
        if carry == "0":                       # first stage without carry-in is a half adder
            s = c.gate("XOR", a[i], b[i])
            carry = c.gate("AND", a[i], b[i])
        else:
            s, carry = _full_adder_into(c, a[i], b[i], carry)
        outs.append(s)
    c.outputs = outs + [carry]
    return c


def _prefix_adder(n: int, network: str) -> Circuit:
    """Parallel-prefix adder. Generate/propagate pairs are combined with the carry
    operator (g, p) ∘ (g', p') = (g ∨ (p ∧ g'), p ∧ p'), which is composition in the
    carry monoid {K, P, G} (GIN-PROP-020)."""
    c = Circuit(f"{n}-bit {network} adder")
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    g = [c.gate("AND", a[i], b[i]) for i in range(n)]
    p = [c.gate("XOR", a[i], b[i]) for i in range(n)]
    G, P = list(g), list(p)          # G[i], P[i] describe the span currently ending at i

    def combine(hi: int, lo_G: str, lo_P: str, need_p: bool) -> tuple[str, str]:
        t = c.gate("AND", P[hi], lo_G)
        ng = c.gate("OR", G[hi], t)
        np_ = c.gate("AND", P[hi], lo_P) if need_p else P[hi]
        return ng, np_

    if network == "Kogge–Stone":
        d = 1
        while d < n:
            newG, newP = list(G), list(P)
            for i in range(d, n):
                newG[i], newP[i] = combine(i, G[i - d], P[i - d], need_p=i >= 2 * d)
            G, P = newG, newP
            d *= 2
    elif network == "Sklansky":
        d = 1
        while d < n:
            newG, newP = list(G), list(P)
            for i in range(n):
                if (i // d) % 2 == 1:
                    j = (i // d) * d - 1      # last index of the left neighbouring block
                    newG[i], newP[i] = combine(i, G[j], P[j], need_p=(i // (2 * d)) * 2 * d > 0)
            G, P = newG, newP
            d *= 2
    elif network == "Brent–Kung":
        # up-sweep
        d = 1
        while 2 * d <= n:
            for i in range(2 * d - 1, n, 2 * d):
                G[i], P[i] = combine(i, G[i - d], P[i - d], need_p=i - 2 * d + 1 > 0)
            d *= 2
        # down-sweep
        d //= 2
        while d >= 1:
            for i in range(3 * d - 1, n, 2 * d):
                G[i], P[i] = combine(i, G[i - d], P[i - d], need_p=False)
            d //= 2
    else:
        raise ValueError(network)
    # carries: c_{i+1} = G[i]; c_0 = 0
    s = [p[0]] + [c.gate("XOR", p[i], G[i - 1]) for i in range(1, n)]
    c.outputs = s + [G[n - 1]]
    return c


def kogge_stone_adder(n: int) -> Circuit:
    return _prefix_adder(n, "Kogge–Stone")


def sklansky_adder(n: int) -> Circuit:
    return _prefix_adder(n, "Sklansky")


def brent_kung_adder(n: int) -> Circuit:
    return _prefix_adder(n, "Brent–Kung")


ADDERS = {"ripple-carry": ripple_adder, "Sklansky": sklansky_adder,
          "Kogge–Stone": kogge_stone_adder, "Brent–Kung": brent_kung_adder}


# ---------------------------------------------------------------------------
# the carry monoid
# ---------------------------------------------------------------------------
CARRY_ELEMENTS = ("K", "P", "G")       # kill (c ↦ 0), propagate (c ↦ c), generate (c ↦ 1)
_CARRY_FN = {"K": (0, 0), "P": (0, 1), "G": (1, 1)}   # images of carry-in 0 and 1


def carry_class(a_bit: int, b_bit: int) -> str:
    """The transition of the carry automaton on the digit pair (a_bit, b_bit)."""
    return {0: "K", 1: "P", 2: "G"}[a_bit + b_bit]


def carry_compose(lo: str, hi: str) -> str:
    """Effect of position ``lo`` followed by the more significant position ``hi``."""
    f, g = _CARRY_FN[lo], _CARRY_FN[hi]
    h = (g[f[0]], g[f[1]])
    return {v: k for k, v in _CARRY_FN.items()}[h]


def carries(x: int, y: int, n: int) -> list[int]:
    """Carry into each position 0..n (sequential reference semantics)."""
    out, c = [0], 0
    for i in range(n):
        c = 1 if ((x >> i & 1) + (y >> i & 1) + c) >= 2 else 0
        out.append(c)
    return out


def longest_carry_chain(x: int, y: int, n: int) -> int:
    """Length of the longest run of positions a carry travels through (generate + propagates)."""
    best = run = 0
    for i in range(n):
        k = carry_class(x >> i & 1, y >> i & 1)
        if k == "G":
            run = 1
        elif k == "P" and run:
            run += 1
        else:
            run = 0
        best = max(best, run)
    return best


# ---------------------------------------------------------------------------
# subtraction, multiplication, division
# ---------------------------------------------------------------------------
def subtractor(n: int) -> Circuit:
    """a − b mod 2^n as a + ¬b + 1 (ripple). Output n bits and a 'no-borrow' bit (= a ≥ b)."""
    c = Circuit(f"{n}-bit two's-complement subtractor")
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    carry = "1"
    outs = []
    for i in range(n):
        nb = c.gate("NOT", b[i])
        s, carry = _full_adder_into(c, a[i], nb, carry)
        outs.append(s)
    c.outputs = outs + [carry]
    return c


def array_multiplier(n: int) -> Circuit:
    """n×n → 2n-bit unsigned multiplier: AND partial products summed by ripple rows."""
    c = Circuit(f"{n}×{n} array multiplier")
    a = [c.input(f"a{i}") for i in range(n)]
    b = [c.input(f"b{i}") for i in range(n)]
    acc = ["0"] * (2 * n)
    for j in range(n):
        pp = ["0"] * j + [c.gate("AND", a[i], b[j]) for i in range(n)] + ["0"] * (n - j)
        carry = "0"
        new = []
        for k in range(2 * n):
            x, y = acc[k], pp[k]
            if x == "0" and y == "0" and carry == "0":
                new.append("0")
                continue
            terms = [t for t in (x, y, carry) if t != "0"]
            if len(terms) == 1:
                new.append(terms[0]); carry = "0"
            elif len(terms) == 2:
                new.append(c.gate("XOR", *terms)); carry = c.gate("AND", *terms)
            else:
                s, carry = _full_adder_into(c, x, y, carry)
                new.append(s)
        acc = new
    c.outputs = acc
    return c


def restoring_divider(n: int) -> Circuit:
    """n-bit unsigned restoring array divider: outputs q0..q{n-1}, r0..r{n-1}.

    Row i (from the most significant dividend bit down) shifts the partial remainder,
    brings in the next dividend bit, subtracts the divisor (n+1-bit ripple
    subtractor), and selects the difference when no borrow occurs.  Nothing in the
    circuit tests the divisor for zero: see GIN-PROP-023 for what it computes then.
    """
    c = Circuit(f"{n}-bit restoring divider")
    a = [c.input(f"a{i}") for i in range(n)]
    d = [c.input(f"b{i}") for i in range(n)]
    R = ["0"] * n                      # partial remainder, little-endian, n bits
    q = ["0"] * n
    for i in range(n - 1, -1, -1):
        T = [a[i]] + R                 # (R << 1) | a_i, n+1 bits
        D = d + ["0"]
        carry = "1"
        diff = []
        for k in range(n + 1):
            nb = c.gate("NOT", D[k])
            s, carry = _full_adder_into(c, T[k], nb, carry)
            diff.append(s)
        ok = carry                      # 1 iff T ≥ D (no borrow)
        q[i] = ok
        nok = c.gate("NOT", ok)
        newR = []
        for k in range(n):
            x = c.gate("AND", ok, diff[k])
            y = c.gate("AND", nok, T[k])
            newR.append(c.gate("OR", x, y))
        R = newR
    c.outputs = q + R
    return c


def run_divider(c: Circuit, n: int, x: int, y: int) -> tuple[int, int]:
    out = apply_words(c, a=(x, n), b=(y, n))
    return int_of(out[:n]), int_of(out[n:])
