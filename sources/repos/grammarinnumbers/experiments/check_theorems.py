"""Exhaustive small-case checks of every exact formula stated in RESULTS.md.

These checks guard against mis-stated theorems.  They are not proofs.  Each check
names the ledger identifier it tests; the script exits non-zero on any failure.
"""
import itertools
import math
import sys
from fractions import Fraction

from common import write
from ginsdk import circuits as K, converse as C, ieee as I, numbertheory as T, numerals as N, peano as P
from ginsdk.cost import Cost

results = {}


def check(ident, fn):
    try:
        detail = fn()
        results[ident] = {"ok": True, "detail": detail}
    except AssertionError as e:
        results[ident] = {"ok": False, "detail": str(e)}


def prop001():
    """Standard base b: two words have the same value iff they differ only by leading zeros."""
    n = 0
    for b in (2, 3, 4):
        g = N.standard(b)
        words = [w for L in range(0, 6 if b == 2 else 4) for w in itertools.product(range(b), repeat=L)]
        strip = lambda w: tuple(itertools.dropwhile(lambda d: d == 0, w))
        for u, v in itertools.combinations(words, 2):
            assert (g.denote(u) == g.denote(v)) == (strip(u) == strip(v)), (b, u, v)
            n += 1
    return f"{n} word pairs"


def prop002():
    for b in range(2, 17):
        assert N.standard(b).address(0) == ()
        assert N.standard(b).words_denoting(0, 3) == [(), (0,), (0, 0), (0, 0, 0)]
    return "bases 2..16"


def prop003():
    for m in range(12):
        for n in range(12):
            c = Cost(); P.add(m, n, c); assert c["rule"] == n + 1
            c = Cost(); P.mul(m, n, c); assert c["rule"] == m * n + 2 * n + 1
    return "m, n < 12"


def prop004():
    for b in (1, 2, 3, 5):
        g = N.bijective(b)
        L = {1: 15, 2: 10, 3: 6, 5: 4}[b]
        vals = [g.denote(w) for k in range(L + 1) for w in itertools.product(g.digits, repeat=k)]
        assert len(vals) == len(set(vals)) and sorted(vals) == list(range(len(vals))), b
    for g in (N.standard(2), N.standard(10), N.BALANCED_TERNARY):
        for n in range(-200 if g is N.BALANCED_TERNARY else 0, 2000):
            w = g.address(n)
            assert g.denote(w) == n and (not w or w[0] != 0)
    return "bijective bases 1,2,3,5 exhaustive by length; residue algorithm on 3 grammars"


def prop005():
    g = N.standard(7)
    for u in itertools.product(range(7), repeat=3):
        for v in itertools.product(range(7), repeat=2):
            assert g.denote(u + v) == g.denote(u) * 7 ** 2 + g.denote(v)
            f = g.compile(u + v)
            assert (f.a, f.c) == (7 ** 5, g.denote(u + v))
    return "base 7, |u| = 3, |v| = 2"


def prop006():
    for n in range(0, 300_000):
        assert N.bijective2_as_heap(n) == N.heap_word(n + 1)
    return "n < 300000"


def prop008():
    for w in range(1, 13):
        for n in range(-(1 << (w - 1)), 1 << (w - 1)):
            assert N.twos_complement_from_2adic(n, w) == format(n & ((1 << w) - 1), f"0{w}b")
    return "widths 1..12, all representable n"


def prop009():
    for b in (2, 3, 10, 12):
        for q in range(1, 200):
            for p in range(0, q):
                x = Fraction(p, q)
                s = N.periodic_expansion(x, b)
                terminates = "(" not in s
                d = x.denominator
                for pr in (2, 3, 5, 7, 11, 13, 17, 19):
                    if b % pr == 0:
                        while d % pr == 0:
                            d //= pr
                assert terminates == (d == 1), (b, x, s)
    return "bases 2,3,10,12, denominators < 200"


def prop010():
    flips = 0
    for x in range(1 << 16):
        flips += (x ^ (x + 1)).bit_count()
        N_ = x + 1
        assert flips == 2 * N_ - N_.bit_count()
    return "N ≤ 65536"


def thm001():
    """Commutative rings: Sol(a, b) is empty or a coset of Ann(b). Checked on Z/n, Z/m × Z/k, F2[x]/(x^3)."""
    rings = []
    for n in range(1, 25):
        rings.append((f"Z/{n}", list(range(n)), lambda x, y, n=n: x * y % n, lambda x, y, n=n: (x + y) % n, lambda x, n=n: (-x) % n))
    for m, k in ((2, 2), (2, 3), (2, 4), (3, 3), (4, 6)):
        el = [(x, y) for x in range(m) for y in range(k)]
        rings.append((f"Z/{m}×Z/{k}", el, lambda a, b, m=m, k=k: (a[0] * b[0] % m, a[1] * b[1] % k),
                      lambda a, b, m=m, k=k: ((a[0] + b[0]) % m, (a[1] + b[1]) % k), lambda a, m=m, k=k: ((-a[0]) % m, (-a[1]) % k)))
    def pmul(a, b):  # F2[x]/(x^3), elements as 3-bit ints
        r = 0
        for i in range(3):
            if b >> i & 1:
                r ^= a << i
        return r & 7
    rings.append(("F2[x]/(x^3)", list(range(8)), pmul, lambda a, b: a ^ b, lambda a: a))
    count = 0
    for name, el, mul, add, neg in rings:
        for b in el:
            ann = [c for c in el if mul(b, c) == el[0]]
            for a in el:
                sols = [c for c in el if mul(b, c) == a]
                if sols:
                    coset = sorted(add(sols[0], t) for t in ann)
                    assert sorted(sols) == coset, (name, a, b)
                count += 1
    return f"{len(rings)} rings, {count} pairs"


def thm002():
    for n in range(1, 61):
        uniq = solv = 0
        for b in range(n):
            g = math.gcd(b, n)
            for a in range(n):
                s = C.divide_mod(a, b, n)
                assert len(s.solutions) == (g if a % g == 0 else 0)
                uniq += s.kind == C.UNIQUE
                solv += bool(s.solutions)
        phi = T.phi(n) if n > 1 else 1
        assert uniq == n * phi and solv == sum(n // math.gcd(b, n) for b in range(n)), n
    return "n ≤ 60"


def thm003():
    for n in range(1, 60):
        assert C.zero_inverse_collapses(list(range(n)), None, lambda x, y, n=n: x * y % n, 0, 1 % n) == (n == 1)
    return "Z/n, n < 60"


def thm006():
    """Pairs (a, b) with cross-multiplication: equivalence exactly off (0, 0); null results = indeterminate forms."""
    R = range(-4, 5)
    P = [C.Pair(a, b) for a in R for b in R]
    nonnull = [p for p in P if p.kind != "null"]
    for p in P:
        assert C.related(p, p)
        for q in P:
            assert C.related(p, q) == C.related(q, p)
    for p in nonnull:
        for q in nonnull:
            if C.related(p, q):
                for r in nonnull:
                    if C.related(q, r):
                        assert C.related(p, r), (p, q, r)
    null = C.Pair(0, 0)
    assert all(C.related(null, q) for q in P)
    assert not C.related(C.Pair(1, 0), C.Pair(0, 1))
    # classes of b = 0 pairs collapse to one point
    assert all(C.related(C.Pair(a, 0), C.Pair(1, 0)) for a in R if a)
    ops = {"+": C.pair_add, "*": C.pair_mul, "/": C.pair_div}
    n = 0
    for p in nonnull:
        for q in nonnull:
            for name, f in ops.items():
                r = f(p, q)
                pk, qk = p.kind, q.kind
                zero = lambda x: x.kind == "finite" and x.a == 0
                expected_null = {"+": pk == qk == "infinity",
                                 "*": (zero(p) and qk == "infinity") or (pk == "infinity" and zero(q)),
                                 "/": (zero(p) and zero(q)) or (pk == qk == "infinity")}[name]
                assert (r.kind == "null") == expected_null, (p, name, q, r)
                for k in (2, -3):           # well defined on classes: scaling p scales the result
                    r2 = f(C.Pair(k * p.a, k * p.b), q)
                    assert (r2.a, r2.b) == (k * r.a, k * r.b)
                n += 1
    return f"pairs in [-4, 4]², {n} operations"


def prop015():
    for fmt in (I.MINI8, I.BINARY16, I.BINARY32, I.BINARY64):
        z = I.FP(fmt, "finite")
        for s in (0, 1):
            inf = I.FP(fmt, "inf", s)
            r, fl = I.mul(z, inf)
            assert r.is_nan and fl == {"invalid"}
            one = I.from_int(1, fmt)[0]
            q, fl = I.div(one, I.FP(fmt, "finite", s))
            assert q.is_inf and q.sign == s and fl == {"divideByZero"}
    return "four formats, both signs"


def prop021():
    for n in range(1, 200):
        c = K.ripple_adder(n)
        assert (c.size, c.depth()) == (5 * n - 3, 2 * n - 1) if n > 1 else (c.size, c.depth()) == (2, 1)
    return "n < 200"


def prop023():
    for n in range(1, 7):
        d = K.restoring_divider(n)
        for x in range(2 ** n):
            assert K.run_divider(d, n, x, 0) == (2 ** n - 1, x)
    return "n ≤ 6, all dividends"


def prop030():
    for fmt in (I.MINI8, I.BINARY16):
        n = 1
        while I.from_int(n, fmt)[0].value() == n:
            n += 1
        assert n == 2 ** fmt.p + 1
    for fmt in (I.BINARY32, I.BINARY64):
        assert I.from_int(2 ** fmt.p, fmt)[0].value() == 2 ** fmt.p
        assert I.from_int(2 ** fmt.p + 1, fmt)[0].value() != 2 ** fmt.p + 1
        assert all(I.from_int(2 ** fmt.p - k, fmt)[0].value() == 2 ** fmt.p - k for k in range(1, 3000))
    return "full search for p = 4, 11; boundary windows for p = 24, 53"


def prop031():
    for k in range(1, 6):
        cnt = sum(1 for d in range(1, 10 ** k) if "inexact" not in I.round_exact(I.BINARY64, Fraction(d, 10 ** k))[1])
        assert cnt == 2 ** k - 1, (k, cnt)
    return "k ≤ 5"


def prop040():
    best = {}
    for a in range(1, 700):
        for b in range(1, a):
            best.setdefault(T.euclid_steps(a, b), (a, b))
    for k, pair in best.items():
        assert pair == T.lame_worst_pair(k)
    return f"all pairs below 700, step counts 1..{max(best)}"


def prop041():
    for e in range(0, 5000):
        v, rows = T.powmod_trace(3, e, 10 ** 9 + 7)
        assert v == pow(3, e, 10 ** 9 + 7)
        c = T.powmod_count(e)
        if e:
            assert c == {"square": e.bit_length() - 1, "multiply": bin(e).count("1") - 1}
            assert "".join("1" if r[1] in ("M", "SM") else "0" for r in rows) == bin(e)[2:]
    return "e < 5000; the bit string of e is recovered from the move word"


def prop042():
    for m1 in range(1, 16):
        for m2 in range(1, 16):
            for r1 in range(m1):
                for r2 in range(m2):
                    L = math.lcm(m1, m2)
                    brute = [x for x in range(L) if x % m1 == r1 and x % m2 == r2]
                    got = T.crt([r1, r2], [m1, m2])
                    compat = (r1 - r2) % math.gcd(m1, m2) == 0
                    assert (got is not None) == compat == bool(brute)
                    assert brute == ([] if got is None else [got[0]])
    return "moduli < 16"


for ident, fn in [("GIN-PROP-001", prop001), ("GIN-PROP-002", prop002), ("GIN-PROP-003", prop003), ("GIN-PROP-004", prop004),
                  ("GIN-PROP-005", prop005), ("GIN-PROP-006", prop006), ("GIN-PROP-008", prop008), ("GIN-PROP-009", prop009),
                  ("GIN-PROP-010", prop010), ("GIN-THM-001", thm001), ("GIN-THM-002", thm002), ("GIN-THM-003", thm003), ("GIN-THM-006", thm006),
                  ("GIN-PROP-015", prop015), ("GIN-PROP-021", prop021), ("GIN-PROP-023", prop023), ("GIN-PROP-030", prop030),
                  ("GIN-PROP-031", prop031), ("GIN-PROP-040", prop040), ("GIN-PROP-041", prop041), ("GIN-PROP-042", prop042)]:
    check(ident, fn)
    print(f"{ident}: {'ok' if results[ident]['ok'] else 'FAIL'} — {results[ident]['detail']}")

write("GIN-CHECKS", [], None, results)
sys.exit(0 if all(r["ok"] for r in results.values()) else 1)
