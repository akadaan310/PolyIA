"""Integration methods as typed state machines.

Each method is a machine  M = (states, guard, transform, recurse, verify)  with states
    INTAKE -> CLASSIFY -> {TABLE, LINEARITY, USUB, PARTS, PARTIAL_FRACTIONS} -> RECURSE -> VERIFY -> EMIT | REFUSE
The VERIFY state is the same for every method: differentiate the result with calc.D and
compare to the integrand on generic points.  A result that fails VERIFY is never emitted.
REFUSE is a first-class outcome with a reason ('no production applies', 'depth budget',
'known non-elementary form').  Every run returns its trace (the word of states visited).
"""
from __future__ import annotations

from fractions import Fraction as Q

from .calc import C, D, X, add, ev, f, mul, pw, same, simp, split_coeff, walk

LIATE = {"ln": 0, "atan": 1, "asin": 1, "alg": 2, "sin": 3, "cos": 3, "tan": 3, "exp": 4}


def is_const(e):
    return all(n[0] != "x" for n in walk(e))


def factors(e):
    return list(e[1:]) if e[0] == "*" else [e]


class Refuse(Exception):
    pass


class Integrator:
    def __init__(self, depth=6):
        self.depth = depth

    def integrate(self, e, trace=None, depth=0, seen=None):
        t = trace if trace is not None else []
        seen = seen if seen is not None else []
        e = simp(e)
        if depth > self.depth:
            t.append("REFUSE:depth")
            raise Refuse("depth budget exceeded")
        t.append("CLASSIFY")
        for name, method in (("TABLE", self.table), ("LINEARITY", self.linearity), ("USUB", self.usub),
                             ("PARTIAL_FRACTIONS", self.partial_fractions), ("PARTS", self.parts)):
            try:
                r = method(e, t, depth, seen)
            except Refuse:
                continue
            except (ZeroDivisionError, ValueError, OverflowError, RecursionError) as ex:
                t.append(f"{name}:ERROR({type(ex).__name__})")  # a method that faults refuses; recorded
                continue
            if r is not None:
                t.append(f"{name}->VERIFY")
                if same(D(r), e):
                    t.append("EMIT")
                    return r
                t.append(f"{name}:VERIFY_FAILED")
        t.append("REFUSE:no production applies")
        raise Refuse("no production applies")

    def run(self, e):
        tr = []
        try:
            r = self.integrate(e, tr)
            return {"ok": True, "result": r, "trace": tr}
        except Refuse as ex:
            return {"ok": False, "reason": str(ex), "trace": tr}

    # ---------------- TABLE: the alphabet of known antiderivatives
    def table(self, e, t, depth, seen):
        k, b = split_coeff(e)
        if is_const(e):
            return mul(e, X)
        if b == X:
            return mul(C(k / 2), pw(X, 2))
        if b[0] == "^" and b[1] == X:
            n = b[2]
            if n == -1:
                return mul(C(k), f("ln", X))
            return mul(C(k / (n + 1)), pw(X, n + 1))
        if b[0] in ("sin", "cos", "exp", "tan") and b[1] == X:
            r = {"sin": mul(C(-1), f("cos", X)), "cos": f("sin", X), "exp": f("exp", X),
                 "tan": mul(C(-1), f("ln", f("cos", X)))}[b[0]]
            return mul(C(k), r)
        if b == pw(f("cos", X), -2):
            return mul(C(k), f("tan", X))
        if b == pw(add(C(1), pw(X, 2)), -1):
            return mul(C(k), f("atan", X))
        if b == pw(add(C(1), mul(C(-1), pw(X, 2))), Q(-1, 2)):
            return mul(C(k), f("asin", X))
        return None

    # ---------------- LINEARITY
    def linearity(self, e, t, depth, seen):
        if e[0] == "+":
            t.append("LINEARITY:split")
            return add(*[self.integrate(a, t, depth + 1, seen) for a in e[1:]])
        k, b = split_coeff(e)
        if k != 1:
            return mul(C(k), self.integrate(b, t, depth + 1, seen))
        return None

    # ---------------- U-SUBSTITUTION: integrand = F(g) * c*g'
    def usub(self, e, t, depth, seen):
        fs = factors(e)
        cands = []
        for i, fac in enumerate(fs):
            inner = None
            if fac[0] in ("sin", "cos", "exp", "tan", "ln", "atan") and fac[1] != X:
                inner = fac[1]
            elif fac[0] == "^" and fac[1] != X and not is_const(fac[1]):
                inner = fac[1]
            if inner is not None:
                cands.append((i, fac, inner))
        for i, fac, g in cands:
            rest = mul(*(fs[:i] + fs[i + 1:])) if len(fs) > 1 else C(1)
            dg = D(g)
            if same(dg, C(0)):
                continue
            try:
                ratio = [ev(rest, p) / ev(dg, p) for p in (0.37, 0.81, 1.29)]
            except ZeroDivisionError:
                continue
            if max(ratio) - min(ratio) > 1e-9 * max(1, abs(ratio[0])):
                continue
            k = Q(ratio[0]).limit_denominator(1000)
            # integrate F(u) in the variable u, then substitute u = g
            Fu = substitute(fac, g, X)
            t.append(f"USUB:u={short(g)}")
            inner_res = self.integrate(Fu, t, depth + 1, seen)
            return mul(C(k), substitute(inner_res, X, g))
        return None

    # ---------------- INTEGRATION BY PARTS with LIATE and cycle closing
    def parts(self, e, t, depth, seen):
        fs = factors(e)
        if len(fs) == 1:
            if fs[0][0] in ("ln", "atan", "asin") and fs[0][1] == X:
                fs = [fs[0], C(1)]
            else:
                return None
        def rank(fac):
            if fac[0] in LIATE:
                return LIATE[fac[0]]
            return LIATE["alg"]
        k, _ = split_coeff(e)
        fs = [a for a in fs if a[0] != "c"]
        if len(fs) == 1:
            fs.append(C(1))
        fs.sort(key=rank)
        u, dv = fs[0], mul(*fs[1:])
        t.append(f"PARTS:u={short(u)}")
        v = self.integrate(dv, t, depth + 1, seen)
        rest = mul(C(-1), v, D(u))
        # cycle closing: if the new integrand is c * (an integrand already on this path), solve I = A + c I
        for orig in [e] + seen:
            try:
                ratio = [ev(rest, p) / ev(orig, p) for p in (0.43, 0.97, 1.31)]
            except ZeroDivisionError:
                continue
            if max(ratio) - min(ratio) < 1e-9 * max(1, abs(ratio[0])) and orig is e:
                c = Q(ratio[0]).limit_denominator(1000)
                if c != 1:
                    t.append("PARTS:cycle-closed")
                    return mul(C(k / (1 - c)), mul(u, v))
        if len(seen) < 3:
            for orig in seen:
                pass
        A = mul(u, v)
        try:
            inner = self._parts_inner(rest, t, depth, seen + [e], e, A, k)
            return inner
        except Refuse:
            raise

    def _parts_inner(self, rest, t, depth, seen, e, A, k):
        # second-level cycle (e.g. e^x sin x): try one more parts step and look for c*e
        k2, b2 = split_coeff(simp(rest))
        try:
            R = self.integrate(rest, t, depth + 1, seen)
            return mul(C(k), add(A, R))
        except Refuse:
            pass
        fs = [a for a in factors(b2) if a[0] != "c"]
        if len(fs) >= 2:
            fs.sort(key=lambda fac: LIATE.get(fac[0], 2))
            u2, dv2 = fs[0], mul(*fs[1:])
            v2 = self.integrate(dv2, t, depth + 1, seen)
            rest2 = mul(C(-k2), v2, D(u2))
            ratio = [ev(rest2, p) / ev(e, p) for p in (0.43, 0.97, 1.31)]
            if max(ratio) - min(ratio) < 1e-9 * max(1, abs(ratio[0])):
                c = Q(ratio[0]).limit_denominator(1000)
                if c == 1:
                    raise Refuse("kernel failure: cycle I = A + I has no solution for I")
                t.append("PARTS:cycle-closed(2)")
                return mul(C(k / (1 - c)), add(A, mul(C(k2), u2, v2)))
        raise Refuse("parts did not terminate within the grammar")

    # ---------------- PARTIAL FRACTIONS for p(x)/q(x) with distinct rational roots of q
    def partial_fractions(self, e, t, depth, seen):
        num, den = rational_parts(e)
        if den is None:
            return None
        qcoef = poly_coeffs(den)
        pcoef = poly_coeffs(num)
        if qcoef is None or pcoef is None or len(qcoef) < 3:
            return None
        roots = rational_roots(qcoef)
        if len(roots) != len(qcoef) - 1 or len(set(roots)) != len(roots):
            if len(qcoef) == 3 and len(roots) == 0:
                return self._quadratic_irreducible(pcoef, qcoef, t)
            return None
        if len(pcoef) >= len(qcoef):
            return None  # improper: polynomial division not in this machine (declared)
        dq = [i * c for i, c in enumerate(qcoef)][1:]
        terms = []
        for r in roots:
            A = peval(pcoef, r) / peval(dq, r)      # cover-up (residue) rule
            terms.append(mul(C(A), f("ln", add(X, C(-r)))))
        t.append(f"PARTIAL_FRACTIONS:roots={','.join(map(str, roots))}")
        return add(*terms)

    def _quadratic_irreducible(self, pcoef, qcoef, t):
        c0, c1, c2 = qcoef
        if len(pcoef) != 1 or c1 != 0 or c0 / c2 <= 0:
            return None
        a2 = c0 / c2
        a = Q(float(a2) ** 0.5).limit_denominator(10**6)
        if a * a != a2:
            return None
        t.append("PARTIAL_FRACTIONS:atan")
        return mul(C(pcoef[0] / c2 / a), f("atan", mul(C(1 / a), X)))


def short(e):
    from .calc import show
    s = show(e)
    return s if len(s) < 24 else s[:21] + "..."


def substitute(e, old, new):
    if e == old:
        return new
    if e[0] in ("x", "c"):
        return e
    if e[0] == "^":
        return simp(("^", substitute(e[1], old, new), e[2]))
    return simp((e[0],) + tuple(substitute(a, old, new) for a in e[1:]))


# ---------------- polynomial helpers (exact rationals)
def poly_coeffs(e):
    """Coefficients [c0, c1, ...] if e is a polynomial in x with rational coefficients."""
    e = simp(e)
    if e[0] == "c":
        return [e[1]]
    if e == X:
        return [Q(0), Q(1)]
    if e[0] == "^" and e[1] == X and e[2].denominator == 1 and e[2] > 0:
        return [Q(0)] * int(e[2]) + [Q(1)]
    if e[0] == "*":
        out = [Q(1)]
        for a in e[1:]:
            pa = poly_coeffs(a)
            if pa is None:
                return None
            out = pmul(out, pa)
        return out
    if e[0] == "+":
        out = [Q(0)]
        for a in e[1:]:
            pa = poly_coeffs(a)
            if pa is None:
                return None
            out = padd(out, pa)
        return out
    return None


def pmul(a, b):
    r = [Q(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] += x * y
    return r


def padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


def peval(c, x):
    return sum(ci * x ** i for i, ci in enumerate(c))


def rational_parts(e):
    fs = factors(simp(e))
    num, den = [], []
    for a in fs:
        if a[0] == "^" and a[2] == -1:
            den.append(a[1])
        else:
            num.append(a)
    if not den:
        return None, None
    return (mul(*num) if num else C(1)), mul(*den)


def rational_roots(c):
    """Rational root theorem [K]: roots p/q with p | c0, q | cn."""
    from math import gcd
    c = list(c)
    while c and c[-1] == 0:
        c.pop()
    L = 1
    for v in c:
        L = L * v.denominator // gcd(L, v.denominator)
    ic = [int(v * L) for v in c]
    if ic[0] == 0:
        rest = rational_roots([Q(v) for v in ic[1:]])
        return [Q(0)] + rest
    def divs(n):
        n = abs(n)
        return [d for d in range(1, n + 1) if n % d == 0]
    roots = set()
    for p in divs(ic[0]):
        for q in divs(ic[-1]):
            for s in (1, -1):
                r = Q(s * p, q)
                if peval([Q(v) for v in ic], r) == 0:
                    roots.add(r)
    return sorted(roots)
