"""Arithmetic as a computational language (GIN-DEF-060 … GIN-DEF-066).

An arithmetic expression such as ``1 + 1``, ``6 / 3`` or ``x / 0`` is treated as a
sentence of a small language with four separable layers (GIN-DEF-061):

    syntax      is the string a well-formed expression?        (tokens, parse tree)
    typing      does every literal name an element of the domain?
    semantics   does every operation have exactly one result?   (converse admissibility)
    execution   what does a concrete machine model do?          (overflow, traps, rounding, flags)

``evaluate(text, domain)`` returns an :class:`Outcome` that records the first layer
at which evaluation stops, the reason in precise terms, the full step trace, and a
cost estimate.  It never returns a bare "error".

Domains (``DOMAINS``): exact N, Z, Q, R (rational arithmetic plus flagged
approximations of irrational roots), C, Z/n; IEEE binary64/32/16 and an 8-bit
teaching format (via :mod:`ginsdk.ieee`); 32-bit integer semantics of x86-64,
AArch64, RISC-V, ISO C, Java and Rust (via :mod:`ginsdk.machine`); Python and
JavaScript number semantics; and a symbolic domain with one variable ``x`` that
tracks the conditions under which an expression is defined.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any

from . import converse, ieee, machine
from .converse import MULTIPLE, NONE, UNIQUE

# ---------------------------------------------------------------------------
# syntax: tokens and parse trees
# ---------------------------------------------------------------------------
_TOKEN = re.compile(r"""
    (?P<ws>\s+)
  | (?P<num>0b[01]+|0x[0-9a-fA-F]+|[01]+₂|\d+\.\d*|\.\d+|\d+)
  | (?P<ident>[A-Za-z_][A-Za-z_0-9]*|√)
  | (?P<op>//|\*\*|[-+*/^%(),×·÷−])
""", re.X)

OP_ALIASES = {"×": "*", "·": "*", "÷": "/", "−": "-", "**": "^"}
FUNCS = {"sqrt": 1, "√": 1, "gcd": 2, "mod": None}


@dataclass
class Token:
    kind: str
    text: str
    pos: int


def tokenize(src: str) -> list[Token]:
    out, pos = [], 0
    while pos < len(src):
        m = _TOKEN.match(src, pos)
        if not m:
            raise SyntaxErrorAt(f"unexpected character {src[pos]!r}", pos)
        kind = m.lastgroup
        if kind != "ws":
            text = m.group()
            if kind == "op":
                text = OP_ALIASES.get(text, text)
            if kind == "ident" and text == "mod":
                kind = "op"
            out.append(Token(kind, text, pos))
        pos = m.end()
    out.append(Token("end", "", len(src)))
    return out


class SyntaxErrorAt(Exception):
    def __init__(self, msg: str, pos: int):
        super().__init__(msg)
        self.pos = pos


@dataclass
class Node:
    kind: str                    # 'num' | 'var' | 'neg' | 'bin' | 'call'
    op: str = ""
    children: list["Node"] = field(default_factory=list)
    text: str = ""
    value: Fraction | None = None
    base: int = 10

    def show(self) -> str:
        if self.kind == "num":
            return self.text
        if self.kind == "var":
            return self.text
        if self.kind == "neg":
            return f"(−{self.children[0].show()})"
        if self.kind == "call":
            return f"{self.op}({', '.join(c.show() for c in self.children)})"
        sym = {"*": "×", "/": "/", "//": "//", "%": "%", "mod": "mod", "^": "^", "+": "+", "-": "−"}[self.op]
        return f"({self.children[0].show()} {sym} {self.children[1].show()})"

    def tree(self) -> dict:
        """A JSON-friendly parse tree."""
        label = {"num": self.text, "var": self.text, "neg": "−", "call": self.op}.get(self.kind, self.op)
        return {"label": label, "kind": self.kind, "children": [c.tree() for c in self.children]}


_PREC = {"+": 10, "-": 10, "*": 20, "/": 20, "//": 20, "%": 20, "mod": 20, "^": 40}


class Parser:
    def __init__(self, src: str):
        self.src = src
        self.toks = tokenize(src)
        self.i = 0

    def peek(self) -> Token:
        return self.toks[self.i]

    def next(self) -> Token:
        t = self.toks[self.i]
        self.i += 1
        return t

    def expect(self, text: str) -> None:
        t = self.next()
        if t.text != text:
            raise SyntaxErrorAt(f"expected {text!r} but found {t.text or 'end of input'!r}", t.pos)

    def parse(self) -> Node:
        if self.peek().kind == "end":
            raise SyntaxErrorAt("empty expression", 0)
        n = self.expr(0)
        t = self.peek()
        if t.kind != "end":
            raise SyntaxErrorAt(f"unexpected {t.text!r} after a complete expression", t.pos)
        return n

    def expr(self, min_prec: int) -> Node:
        left = self.unary()
        while True:
            t = self.peek()
            if t.kind != "op" or t.text not in _PREC or _PREC[t.text] < min_prec:
                return left
            op = self.next().text
            prec = _PREC[op]
            right = self.expr(prec if op == "^" else prec + 1)   # ^ is right-associative
            left = Node("bin", op, [left, right])

    def unary(self) -> Node:
        t = self.peek()
        if t.kind == "op" and t.text in "+-":
            self.next()
            operand = self.expr(30)          # binds tighter than × but looser than ^
            return operand if t.text == "+" else Node("neg", "-", [operand])
        return self.atom()

    def atom(self) -> Node:
        t = self.next()
        if t.kind == "num":
            return _number(t)
        if t.kind == "ident":
            if self.peek().text == "(":
                if t.text not in FUNCS or t.text == "mod":
                    raise SyntaxErrorAt(f"unknown function {t.text!r}", t.pos)
                self.next()
                args = [self.expr(0)]
                while self.peek().text == ",":
                    self.next()
                    args.append(self.expr(0))
                self.expect(")")
                name = "sqrt" if t.text == "√" else t.text
                if len(args) != FUNCS[t.text]:
                    raise SyntaxErrorAt(f"{name} takes {FUNCS[t.text]} argument(s)", t.pos)
                return Node("call", name, args)
            if t.text == "√":
                return Node("call", "sqrt", [self.atom()])
            return Node("var", text=t.text)
        if t.text == "(":
            n = self.expr(0)
            self.expect(")")
            return n
        raise SyntaxErrorAt(f"expected a number, variable or '(' but found {t.text or 'end of input'!r}", t.pos)


def _number(t: Token) -> Node:
    s = t.text
    if s.startswith("0b"):
        return Node("num", text=s, value=Fraction(int(s[2:], 2)), base=2)
    if s.endswith("₂"):
        return Node("num", text=s, value=Fraction(int(s[:-1], 2)), base=2)
    if s.startswith("0x"):
        return Node("num", text=s, value=Fraction(int(s[2:], 16)), base=16)
    return Node("num", text=s, value=Fraction(s))


def parse(src: str) -> Node:
    return Parser(src).parse()


# ---------------------------------------------------------------------------
# outcomes
# ---------------------------------------------------------------------------
STATUS_TEXT = {
    "value": "a value",
    "special": "a special datum (not a number in the mathematical sense)",
    "no-solution": "no result: the defining equation has no solution",
    "non-unique": "no single result: the defining equation has more than one solution",
    "not-in-domain": "the operand or literal is outside the domain",
    "unsupported": "the operation is not part of this domain's grammar",
    "overflow": "the result is not representable",
    "trap": "the hardware raises an exception",
    "exception": "the language runtime raises an exception",
    "undefined": "undefined behaviour: the program has no meaning",
    "syntax-error": "the string is not a well-formed expression",
}
LAYER = {"value": None, "special": "execution", "no-solution": "semantics", "non-unique": "semantics",
         "not-in-domain": "typing", "unsupported": "typing", "overflow": "execution", "trap": "execution",
         "exception": "execution", "undefined": "execution", "syntax-error": "syntax"}


@dataclass
class Step:
    op: str
    operands: list[str]
    result: str
    rule: str = ""
    equation: str = ""
    cost: int = 0


@dataclass
class Outcome:
    expression: str
    domain: str
    status: str
    value: Any = None
    display: str = ""
    layer: str | None = None
    reason: str = ""
    equation: str = ""
    solutions: str = ""
    flags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    tree: dict | None = None
    representation: dict = field(default_factory=dict)
    cost: int = 0
    cost_unit: str = ""
    error_pos: int | None = None

    @property
    def ok(self) -> bool:
        return self.status == "value"

    def headline(self) -> str:
        if self.status in ("value", "special"):
            fl = f"  [flags: {', '.join(self.flags)}]" if self.flags else ""
            return f"{self.expression} = {self.display}  in {self.domain}{fl}"
        return f"{self.expression}  in {self.domain}: {self.status} ({self.layer}) — {self.reason}"

    def as_dict(self) -> dict:
        return {"expression": self.expression, "domain": self.domain, "status": self.status,
                "display": self.display, "layer": self.layer, "reason": self.reason, "equation": self.equation,
                "solutions": self.solutions, "flags": sorted(self.flags), "notes": self.notes,
                "steps": [s.__dict__ for s in self.steps], "tree": self.tree,
                "representation": self.representation, "cost": self.cost, "cost_unit": self.cost_unit}


class Stop(Exception):
    """Raised inside evaluation to stop at a layer with a precise reason."""

    def __init__(self, status: str, reason: str, equation: str = "", solutions: str = "", value: Any = None, display: str = ""):
        super().__init__(reason)
        self.status, self.reason, self.equation, self.solutions = status, reason, equation, solutions
        self.value, self.display = value, display


# ---------------------------------------------------------------------------
# domains
# ---------------------------------------------------------------------------
def _f(q: Fraction) -> str:
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def _bits(n: int) -> int:
    return max(1, abs(n).bit_length())


class Domain:
    name = "?"
    unit = "operations"
    description = ""

    def lift(self, node: Node):
        raise NotImplementedError

    def show(self, v) -> str:
        return str(v)

    def representation(self, v) -> dict:
        return {}

    def binary(self, op: str, a, b, ctx: "Context"):
        raise NotImplementedError

    def neg(self, a, ctx: "Context"):
        return self.binary("-", self.zero(), a, ctx)

    def zero(self):
        return 0

    def call(self, fn: str, args: list, ctx: "Context"):
        raise Stop("unsupported", f"{fn} is not an operation of {self.name}")


class Context:
    def __init__(self, domain: Domain, env: dict | None = None):
        self.domain = domain
        self.steps: list[Step] = []
        self.flags: set[str] = set()
        self.notes: list[str] = []
        self.cost = 0
        self.env = env or {}

    def step(self, op: str, operands: list, result, rule: str = "", equation: str = "", cost: int = 1):
        self.cost += cost
        self.steps.append(Step(op, [self.domain.show(x) for x in operands], self.domain.show(result), rule, equation, cost))


# -- exact domains -----------------------------------------------------------------
class Exact(Domain):
    """N, Z, Q with exact rational values. Division is the converse of multiplication."""

    unit = "bit operations (schoolbook model)"

    def __init__(self, name: str):
        self.name = name
        self.description = {"N": "natural numbers 0, 1, 2, … (exact)", "Z": "integers (exact)",
                            "Q": "rational numbers (exact)"}[name]

    def lift(self, node: Node):
        v = node.value
        if self.name in ("N", "Z") and v.denominator != 1:
            raise Stop("not-in-domain", f"the literal {node.text} denotes {_f(v)}, which is not in {self.name}")
        return v

    def show(self, v) -> str:
        return _f(Fraction(v))

    def representation(self, v) -> dict:
        v = Fraction(v)
        rep = {"exact": _f(v)}
        if v.denominator == 1:
            n = v.numerator
            rep["binary"] = ("−" if n < 0 else "") + bin(abs(n))[2:]
            rep["hexadecimal"] = ("−" if n < 0 else "") + hex(abs(n))[2:].upper()
            rep["bit length"] = abs(n).bit_length()
        else:
            from .numerals import periodic_expansion
            rep["decimal"] = periodic_expansion(v, 10)
            rep["binary"] = periodic_expansion(v, 2)
        return rep

    def _check(self, v: Fraction, what: str) -> Fraction:
        if self.name == "N" and v < 0:
            raise Stop("no-solution", f"{what}: the result {_f(v)} is negative, and N has no negative elements")
        return v

    def binary(self, op, a, b, ctx):
        a, b = Fraction(a), Fraction(b)
        cst = _bitcost(op, a, b) if op != "^" else 0
        if op == "+":
            r = a + b
            ctx.step("+", [a, b], r, "addition is total on " + self.name, cost=cst)
            return r
        if op == "-":
            s = converse.subtract(a, b, self.name)
            if s.kind == NONE:
                raise Stop("no-solution", s.reason, s.equation, "∅")
            ctx.step("−", [a, b], s.value, "subtraction: the unique c with b + c = a", s.equation, cst)
            return Fraction(s.value)
        if op == "*":
            r = a * b
            ctx.step("×", [a, b], r, "multiplication is total on " + self.name, cost=cst)
            return r
        if op == "/":
            s = converse.divide(a, b, self.name)
            if s.kind == NONE:
                raise Stop("no-solution", s.reason, s.equation, "∅")
            if s.kind == MULTIPLE:
                raise Stop("non-unique", s.reason, s.equation, s.description)
            ctx.step("/", [a, b], s.value, "division: the unique c with b · c = a", s.equation, cst)
            return Fraction(s.value)
        if op in ("//", "%", "mod"):
            if self.name == "Q":
                raise Stop("unsupported", f"quotient-with-remainder is an operation on integers, not on {self.name}")
            if b == 0:
                raise Stop("no-solution", "Euclidean division needs b ≠ 0: a = q·b + r with 0 ≤ r < |b| has no solution for b = 0",
                           f"{_f(a)} = q · 0 + r, 0 ≤ r < 0", "∅")
            r = a % abs(b)                       # Euclidean remainder, 0 ≤ r < |b|
            q = (a - r) / b
            res = q if op == "//" else r
            self._check(res, "quotient")
            ctx.step(op, [a, b], res, f"Euclidean division: {_f(a)} = {_f(q)}·{_f(b)} + {_f(r)}, 0 ≤ r < |b|",
                     f"{_f(a)} = q · {_f(b)} + r", cst)
            return res
        if op == "^":
            e = int(b)
            if a == 0 and e == 0:
                ctx.notes.append("0^0 = 1 is a convention (the empty product); as a limit form it is indeterminate")
            if e < 0:
                if self.name in ("N", "Z") and abs(a) != 1:
                    raise Stop("no-solution", f"{_f(a)}^{e} = 1/{_f(a)}^{-e} is not in {self.name}")
                if a == 0:
                    raise Stop("no-solution", f"0^{e} = 1/0^{-e} = 1/0: 0 · c = 1 has no solution", "0 · c = 1", "∅")
            r = a ** e
            ctx.step("^", [a, b], r, "repeated multiplication", cost=_bits(a.numerator) * _bits(r.numerator))
            return r
        raise Stop("unsupported", f"operator {op} is not defined in {self.name}")

    def neg(self, a, ctx):
        a = Fraction(a)
        if self.name == "N" and a != 0:
            raise Stop("no-solution", f"−{_f(a)}: the equation {_f(a)} + c = 0 has no solution in N", f"{_f(a)} + c = 0", "∅")
        ctx.step("neg", [a], -a, "additive inverse", f"{_f(a)} + c = 0")
        return -a

    def call(self, fn, args, ctx):
        if fn == "sqrt":
            a = Fraction(args[0])
            s = converse.square_root(a, self.name)
            if s.kind == NONE:
                raise Stop("no-solution", s.reason, s.equation, "∅")
            v = Fraction(s.solutions[0])
            if s.kind == MULTIPLE:
                ctx.notes.append(f"√ is the principal branch: it selects {_f(v)} from {s.description}")
            ctx.step("√", [a], v, "principal square root", s.equation)
            return v
        if fn == "gcd":
            a, b = (Fraction(x) for x in args)
            if a.denominator != 1 or b.denominator != 1:
                raise Stop("not-in-domain", "gcd is defined on integers")
            r = Fraction(math.gcd(a.numerator, b.numerator))
            ctx.step("gcd", [a, b], r, "Euclid's algorithm", cost=_bits(a.numerator) * _bits(b.numerator))
            return r
        return super().call(fn, args, ctx)


def _bitcost(op: str, a: Fraction, b: Fraction) -> int:
    """Schoolbook bit-operation estimate on numerators/denominators (cost model, not a measurement)."""
    ba = _bits(a.numerator) + (_bits(a.denominator) if a.denominator != 1 else 0)
    bb = _bits(b.numerator) + (_bits(b.denominator) if b.denominator != 1 else 0)
    if op in ("+", "-"):
        return max(ba, bb) + 1 if a.denominator == b.denominator == 1 else ba * bb + max(ba, bb)
    return ba * bb


class Real(Exact):
    """R: exact rational arithmetic; irrational square roots are carried as flagged
    40-digit approximations (the exact real is not representable)."""

    def __init__(self):
        self.name = "R"
        self.description = "real numbers (exact on rationals; irrational roots approximated and flagged)"

    def lift(self, node):
        return node.value

    def show(self, v) -> str:
        if isinstance(v, Decimal):
            return f"≈{v:.25g}"
        return _f(Fraction(v))

    def representation(self, v):
        if isinstance(v, Decimal):
            return {"approximation": f"{v:.40g}", "note": "irrational: no finite numeral in any integer base"}
        return super().representation(v)

    def binary(self, op, a, b, ctx):
        if isinstance(a, Decimal) or isinstance(b, Decimal):
            with localcontext() as c:
                c.prec = 40
                da, db = _dec(a), _dec(b)
                if op == "/" and db == 0:
                    raise Stop("no-solution", "division by an exact zero", "0 · c = a", "∅")
                r = {"+": lambda: da + db, "-": lambda: da - db, "*": lambda: da * db, "/": lambda: da / db}.get(op)
                if r is None:
                    raise Stop("unsupported", f"{op} on an approximated real")
                v = r()
                ctx.flags.add("approximate")
                ctx.step(op, [a, b], v, "arithmetic on a 40-digit approximation")
                return v
        return super().binary(op, a, b, ctx)

    def call(self, fn, args, ctx):
        if fn == "sqrt":
            a = args[0]
            if isinstance(a, Decimal):
                if a < 0:
                    raise Stop("no-solution", "c·c ≥ 0 for every real c", f"c · c = {a}", "∅")
                with localcontext() as c:
                    c.prec = 40
                    v = a.sqrt()
                ctx.flags.add("approximate")
                ctx.step("√", [a], v, "principal square root (approximation)")
                return v
            a = Fraction(a)
            s = converse.square_root(a, "R")
            if s.kind == NONE:
                raise Stop("no-solution", s.reason, s.equation, "∅")
            root = converse._exact_sqrt(abs(a))
            if root is not None:
                ctx.notes.append(f"√ is the principal branch: it selects {_f(root)} from {s.description}")
                ctx.step("√", [a], root, "principal square root", s.equation)
                return root
            with localcontext() as c:
                c.prec = 40
                v = Decimal(a.numerator) / Decimal(a.denominator)
                v = v.sqrt()
            ctx.flags.add("approximate")
            ctx.notes.append(f"√{_f(a)} is irrational; the value is a 40-digit approximation of the principal root of {s.equation}")
            ctx.step("√", [a], v, "principal square root (irrational: approximated)", s.equation)
            return v
        return super().call(fn, args, ctx)


def _dec(x) -> Decimal:
    if isinstance(x, Decimal):
        return x
    x = Fraction(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


class Complex(Domain):
    """C with exact Gaussian-rational values (re, im)."""

    name = "C"
    unit = "rational operations"
    description = "complex numbers with rational real and imaginary parts (exact)"

    def lift(self, node):
        return (node.value, Fraction(0))

    def zero(self):
        return (Fraction(0), Fraction(0))

    def show(self, v):
        re_, im = v
        if im == 0:
            return _f(re_)
        i = "i" if abs(im) == 1 else f"{_f(abs(im))}i"
        if re_ == 0:
            return ("−" if im < 0 else "") + i
        return f"{_f(re_)} {'−' if im < 0 else '+'} {i}"

    def binary(self, op, a, b, ctx):
        if op == "^":
            return self._pow(a, b, ctx)
        (p, q), (r, s) = a, b
        if op == "+":
            v = (p + r, q + s)
        elif op == "-":
            v = (p - r, q - s)
        elif op == "*":
            v = (p * r - q * s, p * s + q * r)
        elif op == "/":
            d = r * r + s * s
            if d == 0:
                if p == q == 0:
                    raise Stop("non-unique", "0 · c = 0 holds for every complex c", "0 · c = 0", "every c in C")
                raise Stop("no-solution", f"0 · c = 0 ≠ {self.show(a)} for every complex c: C is a field, so 0 has no inverse",
                           f"0 · c = {self.show(a)}", "∅")
            v = ((p * r + q * s) / d, (q * r - p * s) / d)
        else:
            raise Stop("unsupported", f"{op} is not defined on C")
        ctx.step(op, [a, b], v, "field operation on C")
        return v

    def _pow(self, a, e: int, ctx):
        p, q = a
        if e < 0 and p == q == 0:
            raise Stop("no-solution", f"0^{e} = 1/0^{-e}: 0 · c = 1 has no solution", "0 · c = 1", "∅")
        base = a if e >= 0 else self.binary("/", (Fraction(1), Fraction(0)), a, Context(self))
        v = (Fraction(1), Fraction(0))
        for _ in range(abs(e)):
            v = (v[0] * base[0] - v[1] * base[1], v[0] * base[1] + v[1] * base[0])
        ctx.step("^", [a, (Fraction(e), Fraction(0))], v, "repeated multiplication in C")
        return v

    def call(self, fn, args, ctx):
        if fn == "sqrt":
            re_, im = args[0]
            if im == 0:
                s = converse.square_root(re_, "C")
                root = converse._exact_sqrt(abs(re_))
                if root is None:
                    raise Stop("unsupported", f"√{_f(abs(re_))} is irrational; this exact domain has no representation for it")
                v = (root, Fraction(0)) if re_ >= 0 else (Fraction(0), root)
                if re_ != 0:
                    ctx.notes.append(f"√ is the principal branch: it selects {self.show(v)} from {s.description}")
                ctx.step("√", [args[0]], v, "principal square root", s.equation)
                return v
            raise Stop("unsupported", "square roots of non-real complex numbers are not implemented")
        return super().call(fn, args, ctx)


class ZMod(Domain):
    unit = "modular operations"

    def __init__(self, n: int):
        if n < 1:
            raise ValueError("modulus must be ≥ 1")
        self.n = n
        self.name = f"Z/{n}"
        self.description = f"integers modulo {n}"

    def lift(self, node):
        if node.value.denominator != 1:
            raise Stop("not-in-domain", f"{node.text} is not an integer, so it names no residue class mod {self.n}")
        return node.value.numerator % self.n

    def representation(self, v):
        return {"residue": f"{v} (the class {v} + {self.n}Z)"}

    def binary(self, op, a, b, ctx):
        n = self.n
        if op == "+":
            v = (a + b) % n
        elif op == "-":
            v = (a - b) % n
            ctx.step("−", [a, b], v, f"subtraction mod {n} is always admissible (Z/{n} is a group under +)", f"{b} + c ≡ {a} (mod {n})")
            return v
        elif op == "*":
            v = a * b % n
        elif op == "/":
            s = converse.divide_mod(a, b, n)
            if s.kind == NONE:
                raise Stop("no-solution", s.reason, s.equation, "∅")
            if s.kind == MULTIPLE:
                raise Stop("non-unique", s.reason, s.equation, s.description)
            v = s.value
            ctx.step("/", [a, b], v, f"the unique c with {b}·c ≡ {a} (mod {n})", s.equation)
            return v
        elif op == "^":
            if b < 0:
                inv = converse.divide_mod(1, a, n)
                if inv.kind != UNIQUE:
                    raise Stop("no-solution", f"{a}^{b} needs the inverse of {a} mod {n}: {inv.reason}", inv.equation, "∅")
                v = pow(inv.value, -b, n)
            else:
                v = pow(a, b, n)
        elif op in ("%", "mod"):
            raise Stop("unsupported", f"'mod' is already built into Z/{n}")
        else:
            raise Stop("unsupported", f"{op} is not defined on Z/{n}")
        ctx.step(op, [a, b], v, f"operation mod {n}")
        return v


# -- IEEE ------------------------------------------------------------------------------
class IEEEDomain(Domain):
    unit = "floating-point operations"

    def __init__(self, fmt: ieee.Format, label: str | None = None, python: bool = False):
        self.fmt = fmt
        self.name = label or fmt.name
        self.python = python
        self.description = (f"IEEE 754 {fmt.name}: p = {fmt.p}, emax = {fmt.emax}, round to nearest even"
                            + ("; Python float semantics (division by zero raises)" if python else ""))

    def lift(self, node):
        v, fl = ieee.round_exact(self.fmt, node.value, 0)
        if "inexact" in fl:
            # record the rounding of literals (e.g. 0.1)
            node_note = f"the literal {node.text} is not representable in {self.fmt.name}; it was rounded to {v}"
            self._pending = getattr(self, "_pending", []) + [node_note]
        if v.is_inf:
            self._pending = getattr(self, "_pending", []) + [f"the literal {node.text} overflows {self.fmt.name} to Infinity"]
        return v

    def zero(self):
        return ieee.FP(self.fmt, "finite")

    def show(self, v):
        return str(v)

    def representation(self, v):
        rep = {"datum": str(v), **v.fields()}
        if v.cls == "finite" and v.mag != 0:
            rep["exact value"] = _f(v.value()) if v.value().denominator < 10**12 else f"{float(v.value())!r} (exact binary fraction)"
        return rep

    def binary(self, op, a, b, ctx):
        if op not in ieee.OPS and op != "^":
            raise Stop("unsupported", f"{op} is not an IEEE 754 basic operation")
        if op == "^":
            raise Stop("unsupported", "pow is a library function, not a correctly rounded basic operation")
        if self.python and op == "/" and b.is_zero:
            raise Stop("exception", "ZeroDivisionError: float division by zero (Python checks the divisor before the IEEE operation)")
        v, fl = ieee.OPS[op](a, b)
        ctx.flags |= fl
        rule = "exact result rounded to nearest, ties to even" if "inexact" in fl else "result exactly representable"
        if op == "/" and b.is_zero:
            rule = ("0/0 has no unique solution: IEEE returns NaN and raises invalid" if a.is_zero
                    else "finite/0: IEEE returns a signed infinity and raises divideByZero")
        ctx.step(op, [a, b], v, rule)
        return v

    def neg(self, a, ctx):
        v = ieee.neg(a)
        ctx.step("neg", [a], v, "sign bit flipped (exact)")
        return v

    def call(self, fn, args, ctx):
        if fn == "sqrt":
            v, fl = ieee.sqrt(args[0])
            ctx.flags |= fl
            ctx.step("√", args, v, "correctly rounded square root")
            return v
        return super().call(fn, args, ctx)


# -- 32-bit integer machine models ------------------------------------------------------
class IntModel(Domain):
    unit = "instructions"

    def __init__(self, label: str, div_model, overflow: str, w: int = 32):
        self.name = label
        self.div_model = div_model
        self.overflow = overflow       # 'wrap' | 'trap' | 'c-undefined'
        self.w = w
        self.description = f"{w}-bit two's-complement integers; overflow policy: {overflow}; division: {div_model.__name__}"

    def lift(self, node):
        v = node.value
        if v.denominator != 1:
            raise Stop("not-in-domain", f"{node.text} is not an integer literal")
        n = v.numerator
        if not -(1 << (self.w - 1)) <= n < (1 << (self.w - 1)):
            raise Stop("not-in-domain", f"the literal {n} does not fit in a {self.w}-bit signed integer")
        return n

    def representation(self, v):
        return {"two's complement": format(v & ((1 << self.w) - 1), f"0{self.w}b"), "hex": f"0x{v & ((1 << self.w) - 1):0{self.w // 4}X}"}

    def _ov(self, exact: int, what: str, ctx) -> int:
        o = machine.add_fixed(exact, 0, self.w, self.overflow)
        if o.kind == "value":
            if o.value != exact:
                ctx.flags.add("overflow")
                ctx.notes.append(f"{what} overflowed: exact result {exact} wrapped to {o.value} (arithmetic mod 2^{self.w})")
            return o.value
        if o.kind == "undefined":
            raise Stop("undefined", f"{what} overflows {self.w} bits (exact result {exact}); {o.note}")
        raise Stop("exception", f"{what} overflows {self.w} bits (exact result {exact}): {o.note}")

    def binary(self, op, a, b, ctx):
        if op in ("+", "-", "*"):
            exact = {"+": a + b, "-": a - b, "*": a * b}[op]
            v = self._ov(exact, {"+": "addition", "-": "subtraction", "*": "multiplication"}[op], ctx)
            ctx.step(op, [a, b], v, f"{self.w}-bit {op}")
            return v
        if op in ("/", "%", "//"):
            o = self.div_model(a, b, self.w)
            if o.kind == "value":
                res = o.value if op in ("/", "//") else (o.remainder if o.remainder is not None else a - b * o.value)
                if b == 0:
                    ctx.notes.append(f"{self.name} returns {res} for {a} {op} 0 without any signal ({o.note}); "
                                     "this value is not a solution of 0 · c = " + str(a))
                elif o.note:
                    ctx.notes.append(o.note)
                ctx.step(op, [a, b], res, o.source)
                return res
            raise Stop({"trap": "trap", "exception": "exception", "undefined": "undefined"}[o.kind],
                       f"{o.name}" + (f" — {o.note}" if o.note else "") + f"  [{o.source}]")
        raise Stop("unsupported", f"{op} is not an integer instruction")

    def neg(self, a, ctx):
        v = self._ov(-a, "negation", ctx)
        ctx.step("neg", [a], v, "two's-complement negation")
        return v


class PythonNumbers(Domain):
    """Python 3 semantics: unbounded int; '/' is true division producing a float."""

    name = "Python"
    unit = "operations"
    description = "Python 3: int is unbounded; int / int is a correctly rounded binary64 float; // floors; x/0 raises"

    def lift(self, node):
        if node.value.denominator == 1 and "." not in node.text:
            return node.value.numerator
        v, _ = ieee.round_exact(ieee.BINARY64, node.value)
        return v

    def show(self, v):
        if isinstance(v, int):
            return str(v)
        return repr(ieee.to_float(v))

    def representation(self, v):
        if isinstance(v, int):
            return {"type": "int", "binary": bin(v)}
        return {"type": "float", **v.fields()}

    def _fp(self, x):
        return x if isinstance(x, ieee.FP) else ieee.round_exact(ieee.BINARY64, Fraction(x))[0]

    def binary(self, op, a, b, ctx):
        both_int = isinstance(a, int) and isinstance(b, int)
        if op in ("/", "//", "%"):
            if (b == 0) if isinstance(b, int) else b.is_zero:
                kind = "float division by zero" if op == "/" and not both_int else (
                    "division by zero" if op == "/" else "integer division or modulo by zero" if both_int else "float floor division by zero")
                raise Stop("exception", f"ZeroDivisionError: {kind}")
        if both_int:
            if op == "/":
                v, fl = ieee.round_exact(ieee.BINARY64, Fraction(a, b))
                if v.is_inf:
                    raise Stop("exception", "OverflowError: integer division result too large for a float")
                ctx.notes.append("int / int produces a float: the representation changes from exact integer to binary64")
                ctx.step("/", [a, b], v, "true division, correctly rounded to binary64")
                return v
            if op == "^":
                if b < 0:
                    v, _ = ieee.round_exact(ieee.BINARY64, Fraction(a) ** b) if a else (None, None)
                    if a == 0:
                        raise Stop("exception", "ZeroDivisionError: 0.0 cannot be raised to a negative power")
                    ctx.step("**", [a, b], v, "negative exponent gives a float")
                    return v
                v = a ** b
            else:
                v = {"+": a + b, "-": a - b, "*": a * b, "//": a // b if b else 0, "%": a % b if b else 0}.get(op)
                if v is None:
                    raise Stop("unsupported", f"{op}")
            ctx.step(op, [a, b], v, "unbounded integer arithmetic")
            return v
        fa, fb = self._fp(a), self._fp(b)
        if op in ieee.OPS:
            v, fl = ieee.OPS[op](fa, fb)
            ctx.flags |= fl
            ctx.step(op, [a, b], v, "binary64 arithmetic")
            return v
        raise Stop("unsupported", f"{op} on floats is not modelled")

    def neg(self, a, ctx):
        v = -a if isinstance(a, int) else ieee.neg(a)
        ctx.step("neg", [a], v)
        return v


class JSBigInt(Domain):
    name = "JS BigInt"
    unit = "operations"
    description = "ECMAScript BigInt: unbounded integers; / truncates toward zero; division by 0n throws RangeError"

    def lift(self, node):
        if node.value.denominator != 1:
            raise Stop("not-in-domain", f"{node.text} is not a BigInt literal")
        return node.value.numerator

    def binary(self, op, a, b, ctx):
        if op in ("/", "%"):
            o = machine.div_js_bigint(a, b)
            if o.kind != "value":
                raise Stop("exception", o.name + "  [" + o.source + "]")
            v = o.value if op == "/" else o.remainder
        elif op == "^":
            if b < 0:
                raise Stop("exception", "RangeError: Exponent must be non-negative")
            v = a ** b
        elif op in ("+", "-", "*"):
            v = {"+": a + b, "-": a - b, "*": a * b}[op]
        else:
            raise Stop("unsupported", op)
        ctx.step(op, [a, b], v, "BigInt arithmetic")
        return v

    def neg(self, a, ctx):
        ctx.step("neg", [a], -a)
        return -a


# -- symbolic ---------------------------------------------------------------------------
class Poly:
    """Univariate polynomial in x over Q, coefficients low degree first."""

    def __init__(self, coeffs):
        c = [Fraction(x) for x in coeffs]
        while c and c[-1] == 0:
            c.pop()
        self.c = c

    @staticmethod
    def const(k):
        return Poly([k])

    X = None

    def deg(self):
        return len(self.c) - 1

    def is_zero(self):
        return not self.c

    def __add__(self, o):
        n = max(len(self.c), len(o.c))
        return Poly([(self.c[i] if i < len(self.c) else 0) + (o.c[i] if i < len(o.c) else 0) for i in range(n)])

    def __neg__(self):
        return Poly([-x for x in self.c])

    def __sub__(self, o):
        return self + (-o)

    def __mul__(self, o):
        if self.is_zero() or o.is_zero():
            return Poly([])
        r = [Fraction(0)] * (len(self.c) + len(o.c) - 1)
        for i, x in enumerate(self.c):
            for j, y in enumerate(o.c):
                r[i + j] += x * y
        return Poly(r)

    def divmod(self, o):
        if o.is_zero():
            raise ZeroDivisionError
        q = [Fraction(0)] * max(1, len(self.c) - len(o.c) + 1)
        r = list(self.c)
        while len(r) >= len(o.c) and any(r):
            k = len(r) - len(o.c)
            f = r[-1] / o.c[-1]
            q[k] = f
            for i, y in enumerate(o.c):
                r[i + k] -= f * y
            while r and r[-1] == 0:
                r.pop()
        return Poly(q), Poly(r)

    def monic(self):
        return Poly([x / self.c[-1] for x in self.c]) if self.c else self

    def __call__(self, x):
        v = Fraction(0)
        for coef in reversed(self.c):
            v = v * x + coef
        return v

    def rational_roots(self) -> list[Fraction]:
        if self.is_zero():
            return []
        c = list(self.c)
        roots = []
        # factor out x
        while c and c[0] == 0:
            c.pop(0)
            if Fraction(0) not in roots:
                roots.append(Fraction(0))
        if len(c) <= 1:
            return sorted(roots)
        den = math.lcm(*[x.denominator for x in c])
        ints = [int(x * den) for x in c]
        a0, an = abs(ints[0]), abs(ints[-1])
        cands = {Fraction(s * p, q) for p in _divs(a0) for q in _divs(an) for s in (1, -1)}
        p = Poly(c)
        roots += [r for r in cands if p(r) == 0]
        return sorted(set(roots))

    def __str__(self):
        if not self.c:
            return "0"
        terms = []
        for i in range(len(self.c) - 1, -1, -1):
            k = self.c[i]
            if k == 0:
                continue
            mon = "" if i == 0 else "x" if i == 1 else f"x^{i}"
            coef = _f(abs(k))
            body = coef if i == 0 else (mon if abs(k) == 1 else f"{coef}{mon}")
            terms.append(("−" if k < 0 else "+", body))
        s = ("−" if terms[0][0] == "−" else "") + terms[0][1]
        for sg, b in terms[1:]:
            s += f" {sg} {b}"
        return s


def _divs(n):
    return [d for d in range(1, n + 1) if n % d == 0] if n else [1]


def poly_gcd(a: Poly, b: Poly) -> Poly:
    while not b.is_zero():
        a, b = b, a.divmod(b)[1]
    return a.monic()


@dataclass
class RatFun:
    num: Poly
    den: Poly
    conditions: list = field(default_factory=list)   # polynomials required to be ≠ 0

    def __str__(self):
        if self.den.deg() == 0:
            return str(Poly([x / self.den.c[0] for x in self.num.c]))
        return f"({self.num}) / ({self.den})"


class Symbolic(Domain):
    """Rational functions of one variable x over Q, with definedness conditions.

    Each division records the condition 'divisor ≠ 0' *before* any cancellation, so that
    x/x simplifies to 1 while the domain of definition still excludes x = 0.  Symbolic
    simplification and numerical evaluation are different operations (GIN-PROP-014).
    """

    name = "symbolic"
    unit = "polynomial operations"
    description = "rational functions of x over Q; tracks the conditions under which the expression is defined"

    def lift(self, node):
        if node.kind == "var":
            if node.text != "x":
                raise Stop("not-in-domain", "the symbolic domain has one variable, x")
            return RatFun(Poly([0, 1]), Poly([1]))
        return RatFun(Poly([node.value]), Poly([1]))

    def zero(self):
        return RatFun(Poly([]), Poly([1]))

    def show(self, v):
        return str(v)

    def binary(self, op, a, b, ctx):
        conds = a.conditions + (b.conditions if isinstance(b, RatFun) else [])
        if op == "+":
            r = RatFun(a.num * b.den + b.num * a.den, a.den * b.den, conds)
        elif op == "-":
            r = RatFun(a.num * b.den - b.num * a.den, a.den * b.den, conds)
        elif op == "*":
            r = RatFun(a.num * b.num, a.den * b.den, conds)
        elif op == "/":
            if b.num.is_zero():
                if a.num.is_zero():
                    raise Stop("non-unique", "the divisor is identically 0 and so is the dividend: 0 · c = 0 for every c, at every x",
                               "0 · c = 0", "every c, for every x")
                roots = a.num.rational_roots()
                where = f"; where the dividend {a} vanishes (x ∈ {{{', '.join(map(_f, roots))}}}) the equation becomes 0 · c = 0 and every c solves it" if roots else ""
                raise Stop("no-solution", f"the divisor is identically 0: 0 · c = {a} has no solution at any x where {a} ≠ 0{where}",
                           f"0 · c = {a}", "∅ (no x makes the result unique)")
            conds = conds + [b.num]
            r = RatFun(a.num * b.den, a.den * b.num, conds)
        elif op == "^":
            if b < 0:
                raise Stop("unsupported", "only natural-number exponents in the symbolic domain")
            n, d = Poly([1]), Poly([1])
            for _ in range(b):
                n, d = n * a.num, d * a.den
            r = RatFun(n, d, a.conditions)
        else:
            raise Stop("unsupported", op)
        g = poly_gcd(r.num, r.den) if not r.num.is_zero() else r.den.monic()
        if g.deg() > 0:
            r = RatFun(r.num.divmod(g)[0], r.den.divmod(g)[0], r.conditions)
            ctx.notes.append(f"cancelled the common factor {g}; the condition {g} ≠ 0 is kept")
        if r.num.is_zero():
            r = RatFun(Poly([]), Poly([1]), r.conditions)
        ctx.step(op, [a, b], r, "rational-function arithmetic")
        return r

    def neg(self, a, ctx):
        r = RatFun(-a.num, a.den, a.conditions)
        ctx.step("neg", [a], r)
        return r


# ---------------------------------------------------------------------------
# registry and evaluation
# ---------------------------------------------------------------------------
def _domains() -> dict[str, Domain]:
    d: dict[str, Domain] = {"N": Exact("N"), "Z": Exact("Z"), "Q": Exact("Q"), "R": Real(), "C": Complex()}
    for fmt in (ieee.BINARY64, ieee.BINARY32, ieee.BINARY16, ieee.MINI8):
        d[fmt.name.split(" ")[0]] = IEEEDomain(fmt)
    d["JS Number"] = IEEEDomain(ieee.BINARY64, "JS Number")
    d["Python"] = PythonNumbers()
    d["JS BigInt"] = JSBigInt()
    d["int32 x86-64"] = IntModel("int32 x86-64", machine.div_x86, "wrap")
    d["int32 AArch64"] = IntModel("int32 AArch64", machine.div_aarch64, "wrap")
    d["int32 RISC-V"] = IntModel("int32 RISC-V", machine.div_riscv, "wrap")
    d["int32 C"] = IntModel("int32 C", machine.div_c, "c-undefined")
    d["int32 Java"] = IntModel("int32 Java", machine.div_java, "wrap")
    d["int32 Rust (debug)"] = IntModel("int32 Rust (debug)", machine.div_rust, "trap")
    d["int32 Go"] = IntModel("int32 Go", machine.div_go, "wrap")
    d["symbolic"] = Symbolic()
    return d


DOMAINS = _domains()


def domain(name: str) -> Domain:
    if name in DOMAINS:
        return DOMAINS[name]
    m = re.fullmatch(r"Z/(\d+)", name)
    if m:
        return ZMod(int(m.group(1)))
    raise KeyError(f"unknown domain {name!r}; known: {', '.join(DOMAINS)} and Z/n")


def evaluate(src: str, dom: str | Domain = "Q", env: dict | None = None) -> Outcome:
    """Parse, type, and evaluate ``src`` in a domain. Never raises for bad input."""
    D = domain(dom) if isinstance(dom, str) else dom
    out = Outcome(src, D.name, "value", cost_unit=D.unit)
    try:
        tree = parse(src)
    except SyntaxErrorAt as e:
        out.status, out.layer, out.reason, out.error_pos = "syntax-error", "syntax", str(e), e.pos
        return out
    out.tree = tree.tree()
    ctx = Context(D, env)
    if isinstance(D, IEEEDomain):
        D._pending = []
    try:
        v = _eval(tree, ctx)
        if isinstance(D, IEEEDomain) and D._pending:
            ctx.notes[:0] = D._pending
        out.value = v
        out.display = D.show(v)
        out.representation = D.representation(v)
        if isinstance(v, ieee.FP) and v.cls != "finite":
            out.status = "special"
            out.layer = "execution"
            out.reason = _special_reason(v, ctx)
        if isinstance(v, RatFun):
            out.notes = ctx.notes
            out.representation = _definedness(v, tree)
    except Stop as s:
        out.status, out.reason, out.equation, out.solutions = s.status, s.reason, s.equation, s.solutions
        out.layer = LAYER[s.status]
    out.steps = ctx.steps
    out.flags = sorted(ctx.flags)
    if not isinstance(out.value, RatFun):
        out.notes = ctx.notes
    out.cost = ctx.cost
    return out


def _special_reason(v: ieee.FP, ctx: Context) -> str:
    if v.is_nan:
        return "NaN: the operation has no unique real result (invalid); IEEE 754 returns a datum that is not a number"
    if "divideByZero" in ctx.flags:
        return ("±Infinity from division by zero: no real c satisfies 0 · c = a ≠ 0; IEEE 754 returns the signed infinity "
                "that the limit from the side of the zero's sign would suggest, and raises divideByZero")
    return "±Infinity from overflow: the exact result exceeds the largest finite number of the format"


def _eval(node: Node, ctx: Context):
    D = ctx.domain
    if node.kind == "num":
        return D.lift(node)
    if node.kind == "var":
        if isinstance(D, Symbolic):
            return D.lift(node)
        if node.text in ctx.env:
            sub = Node("num", text=str(ctx.env[node.text]), value=Fraction(ctx.env[node.text]))
            return D.lift(sub)
        raise Stop("not-in-domain", f"the variable {node.text} has no value; give it one, or use the symbolic domain")
    if node.kind == "neg":
        return D.neg(_eval(node.children[0], ctx), ctx)
    if node.kind == "call":
        return D.call(node.op, [_eval(c, ctx) for c in node.children], ctx)
    a = _eval(node.children[0], ctx)
    if node.op == "^":
        # Exponents are not elements of the domain: a^k is the action of an integer k on
        # the domain (repeated multiplication). The exponent is evaluated in exact Z.
        sub = Context(DOMAINS["Z"], ctx.env)
        try:
            k = _eval(node.children[1], sub)
        except Stop as s:
            raise Stop(s.status, "in the exponent: " + s.reason, s.equation, s.solutions)
        if Fraction(k).denominator != 1:
            raise Stop("unsupported", "only integer exponents are part of this grammar (a rational exponent is a root: a converse problem)")
        return D.binary("^", a, int(k), ctx)
    b = _eval(node.children[1], ctx)
    return D.binary(node.op, a, b, ctx)


def _definedness(v: RatFun, tree: Node) -> dict:
    """Describe where a symbolic result is defined, and what fails at excluded points."""
    excluded: list[Fraction] = []
    unresolved = []
    for c in v.conditions:
        rr = c.rational_roots()
        excluded += rr
        rest = c
        for r in rr:
            while rest(r) == 0 and rest.deg() > 0:
                rest = rest.divmod(Poly([-r, 1]))[0]
        if rest.deg() > 0:
            unresolved.append(str(rest))
    excluded = sorted(set(excluded))
    rep = {"simplified": str(v), "conditions": [f"{c} ≠ 0" for c in v.conditions] or ["none"],
           "excluded points": [_f(x) for x in excluded]}
    if unresolved:
        rep["conditions without rational roots"] = [f"{u} ≠ 0" for u in unresolved]
    cases = {}
    for x in excluded:
        o = evaluate_tree(tree, "Q", {"x": x})
        cases[_f(x)] = f"{o.status}: {o.reason}"
    if cases:
        rep["at excluded points (exact Q)"] = cases
    return rep


def evaluate_tree(tree: Node, dom: str, env: dict) -> Outcome:
    D = domain(dom)
    ctx = Context(D, env)
    out = Outcome(tree.show(), D.name, "value")
    try:
        v = _eval(tree, ctx)
        out.value, out.display = v, D.show(v)
    except Stop as s:
        out.status, out.reason, out.layer = s.status, s.reason, LAYER[s.status]
    return out


def compare(src: str, domains: list[str] | None = None) -> list[Outcome]:
    """Evaluate one expression in many domains (the Machine Lab table)."""
    names = domains or ["N", "Z", "Q", "Z/7", "Z/6", "binary64", "Python", "JS BigInt", "int32 x86-64",
                        "int32 AArch64", "int32 RISC-V", "int32 C", "int32 Java", "int32 Rust (debug)"]
    return [evaluate(src, n) for n in names]
