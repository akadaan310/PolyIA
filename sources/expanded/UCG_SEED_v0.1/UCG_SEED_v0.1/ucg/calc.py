"""Calculus as grammar: expressions are words, differentiation is a rewrite system,
integration methods are state machines.  Our engine; sympy only witnesses.

Expression alphabet (prefix trees):
    ('x',)  ('c', Fraction)  ('+', a, b, ...)  ('*', a, b, ...)  ('^', a, Fraction)
    ('sin', a) ('cos', a) ('tan', a) ('exp', a) ('ln', a) ('atan', a) ('asin', a)
Every differentiation step records the production used (linearity, product, chain,
power, exp, ln, sin, cos, ...), so a derivative comes with its derivation word.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction as Q

X = ("x",)


def C(v):
    return ("c", Q(v))


def add(*a):
    return simp(("+",) + a)


def mul(*a):
    return simp(("*",) + a)


def pw(a, n):
    return simp(("^", a, Q(n)))


def f(name, a):
    return (name, a)


FUNS = {"sin", "cos", "tan", "exp", "ln", "atan", "asin"}


# ------------------------------------------------------------------ simplifier (normal form, partial)
def simp(e):
    h = e[0]
    if h in ("x", "c"):
        return e
    if h in FUNS:
        a = simp(e[1])
        if a[0] == "c":
            if h == "exp" and a[1] == 0:
                return C(1)
            if h in ("sin", "tan", "atan", "asin") and a[1] == 0:
                return C(0)
            if h == "cos" and a[1] == 0:
                return C(1)
            if h == "ln" and a[1] == 1:
                return C(0)
        if h == "ln" and a[0] == "exp":
            return a[1]
        if h == "exp" and a[0] == "ln":
            return a[1]
        return (h, a)
    if h == "^":
        b, n = simp(e[1]), e[2]
        if n == 0:
            return C(1)
        if n == 1:
            return b
        if b[0] == "c" and (n.denominator == 1 or b[1] >= 0):
            if b[1] == 0 and n < 0:
                return ("^", b, n)
            v = float(b[1]) ** float(n)
            return C(Q(v).limit_denominator(10**9)) if n.denominator != 1 else C(b[1] ** int(n))
        if b[0] == "^":
            return simp(("^", b[1], b[2] * n))
        return ("^", b, n)
    args = []
    for a in e[1:]:
        a = simp(a)
        if a[0] == h:
            args += list(a[1:])
        else:
            args.append(a)
    if h == "+":
        const = sum((a[1] for a in args if a[0] == "c"), Q(0))
        rest = [a for a in args if a[0] != "c"]
        # collect like terms: k*t
        terms = {}
        order = []
        for a in rest:
            k, t = split_coeff(a)
            key = repr(t)
            if key not in terms:
                terms[key] = [Q(0), t]
                order.append(key)
            terms[key][0] += k
        out = []
        for key in order:
            k, t = terms[key]
            if k == 0:
                continue
            out.append(t if k == 1 else (("*", C(k), t) if t[0] != "*" else ("*", C(k)) + t[1:]))
        if const != 0:
            out.append(C(const))
        if not out:
            return C(0)
        return out[0] if len(out) == 1 else ("+",) + tuple(sorted(out, key=repr))
    if h == "*":
        const = Q(1)
        powers = {}
        order = []
        for a in args:
            if a[0] == "c":
                const *= a[1]
                continue
            base, n = (a[1], a[2]) if a[0] == "^" else (a, Q(1))
            key = repr(base)
            if key not in powers:
                powers[key] = [base, Q(0)]
                order.append(key)
            powers[key][1] += n
        if const == 0:
            return C(0)
        out = []
        for key in order:
            base, n = powers[key]
            if n == 0:
                continue
            out.append(base if n == 1 else ("^", base, n))
        if not out:
            return C(const)
        out = sorted(out, key=repr)
        if const != 1:
            out = [C(const)] + out
        return out[0] if len(out) == 1 else ("*",) + tuple(out)
    raise ValueError(f"unknown head {h}")


def split_coeff(e):
    if e[0] == "*" and e[1][0] == "c":
        rest = e[2:]
        return e[1][1], rest[0] if len(rest) == 1 else ("*",) + rest
    if e[0] == "c":
        return e[1], C(1)
    return Q(1), e


# ------------------------------------------------------------------ evaluation & identity witness
def ev(e, x):
    h = e[0]
    if h == "x":
        return x
    if h == "c":
        return float(e[1])
    if h == "+":
        return sum(ev(a, x) for a in e[1:])
    if h == "*":
        p = 1.0
        for a in e[1:]:
            p *= ev(a, x)
        return p
    if h == "^":
        b = ev(e[1], x)
        if b < 0 and e[2].denominator != 1:
            raise ValueError("outside the real domain")
        return b ** float(e[2])
    a = ev(e[1], x)
    return {"sin": math.sin, "cos": math.cos, "tan": math.tan, "exp": math.exp, "ln": math.log, "atan": math.atan, "asin": math.asin}[h](a)


PTS = [0.31, 0.47, 0.73, 0.91, 1.13, 1.37, 1.61, 1.79]


def same(a, b, pts=PTS, tol=1e-7):
    """Randomised identity test (Schwartz-Zippel style for analytic functions): agree at
    several generic points.  A witness, not a proof; failures are definitive."""
    for p in pts:
        try:
            u, v = ev(a, p), ev(b, p)
        except (ValueError, ZeroDivisionError, OverflowError):
            continue
        if not math.isfinite(u) or not math.isfinite(v):
            continue
        if abs(u - v) > tol * max(1.0, abs(u), abs(v)):
            return False
    return True


def show(e):
    h = e[0]
    if h == "x":
        return "x"
    if h == "c":
        v = e[1]
        return str(v.numerator) if v.denominator == 1 else f"({v})"
    if h == "+":
        return "(" + " + ".join(show(a) for a in e[1:]) + ")"
    if h == "*":
        return "*".join(show(a) for a in e[1:])
    if h == "^":
        n = e[2]
        return f"{show(e[1])}^{n if n.denominator == 1 else '(' + str(n) + ')'}"
    return f"{h}({show(e[1])})"


# ------------------------------------------------------------------ differentiation: a rewrite system
def D(e, trace=None):
    t = trace if trace is not None else []
    h = e[0]
    if h == "x":
        t.append("D:x")
        return C(1)
    if h == "c":
        t.append("D:const")
        return C(0)
    if h == "+":
        t.append("D:linearity")
        return add(*[D(a, t) for a in e[1:]])
    if h == "*":
        t.append("D:product")
        terms = []
        for i in range(1, len(e)):
            terms.append(mul(*(e[1:i] + (D(e[i], t),) + e[i + 1:])))
        return add(*terms)
    if h == "^":
        t.append("D:power+chain")
        return mul(C(e[2]), pw(e[1], e[2] - 1), D(e[1], t))
    a = e[1]
    da = D(a, t)
    t.append(f"D:{h}+chain")
    outer = {"sin": lambda: f("cos", a), "cos": lambda: mul(C(-1), f("sin", a)), "tan": lambda: pw(f("cos", a), -2),
             "exp": lambda: f("exp", a), "ln": lambda: pw(a, -1), "atan": lambda: pw(add(C(1), pw(a, 2)), -1),
             "asin": lambda: pw(add(C(1), mul(C(-1), pw(a, 2))), Q(-1, 2))}[h]()
    return mul(outer, da)


def trig_closure_words(e):
    return {n for n in walk(e) if n[0] in FUNS}


def walk(e):
    yield e
    if e[0] not in ("x", "c"):
        for a in e[1:]:
            if isinstance(a, tuple):
                yield from walk(a)


# ------------------------------------------------------------------ D-orbits and characteristic words
def d_orbit_rank(e, kmax=10, pts=None):
    """Dimension of span{f, Df, D^2 f, ...} measured on sample points; if finite (< kmax),
    return the monic annihilating polynomial  D^r + c_{r-1} D^{r-1} + ... + c_0  (the
    function's characteristic word).  Exponential polynomials are exactly the functions
    with a finite D-orbit span [K: linear ODEs with constant coefficients]."""
    import numpy as np
    pts = pts or [0.1 + 0.137 * i for i in range(24)]
    derivs = [e]
    for _ in range(kmax):
        derivs.append(D(derivs[-1]))
    M = np.array([[ev(d, p) for p in pts] for d in derivs])
    fresh = [0.23 + 0.211 * i for i in range(16)]
    Mf = np.array([[ev(d, p) for p in fresh] for d in derivs])
    for r in range(1, kmax + 1):
        A = M[:r].T
        b = -M[r]
        c, res, rk, _ = np.linalg.lstsq(A, b, rcond=None)
        if np.linalg.norm(A @ c - b) < 1e-8 * max(1, np.linalg.norm(b)):
            cr = np.round(c, 6)
            # out-of-sample witness: the same rational-looking relation must hold at fresh points
            lhs = Mf[:r].T @ cr + Mf[r]
            if np.linalg.norm(lhs) < 1e-6 * max(1, np.linalg.norm(Mf[r])) and np.allclose(cr, np.round(cr, 3), atol=1e-6):
                return r, [float(v) + 0.0 for v in cr] + [1.0], derivs
    return None, None, derivs


def orbit_class(e, kmax=10):
    derivs = [e]
    for k in range(1, kmax + 1):
        derivs.append(D(derivs[-1]))
        d = derivs[-1]
        if d == C(0) or same(d, C(0)):
            return {"class": "nilpotent (severed)", "index": k}
        for j in range(k):
            if same(d, derivs[j]):
                return {"class": "periodic (complete)", "period": k - j, "enters_at": j}
        for j in range(k):
            try:
                r = ev(d, 0.77) / ev(derivs[j], 0.77)
            except ZeroDivisionError:
                continue
            if abs(r) > 1e-9 and same(d, mul(C(Q(r).limit_denominator(1000)), derivs[j])):
                sc = Q(r).limit_denominator(1000)
                out = {"class": "projectively periodic", "period": k - j, "scalar": str(sc)}
                if sc == -1:
                    out["true_period"] = 2 * (k - j)
                return out
    r, word, _ = d_orbit_rank(e, kmax)
    size = len(repr(derivs[-1]))
    return {"class": "drifting (open)" if r is None else f"finite span r={r}", "growth": size // max(1, len(repr(e)))}
