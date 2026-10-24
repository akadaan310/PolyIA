"""GIN-EXP-012  Representation boundaries: where a value outruns its representation.

Hypotheses: GIN-H-031 (the least positive integer not representable in an IEEE binary
format of precision p is 2^p + 1), GIN-H-032 (a decimal fraction d/10^k in lowest terms
is exactly representable in binary floating point only if its reduced denominator is a
power of 2; among the 999 three-digit decimals 0.001…0.999 exactly 7 are), GIN-H-033
(floating-point addition is commutative but not associative; the smallest decimal
counterexample with one-digit tenths is found by exhaustive search), GIN-H-034
(summation order changes the computed harmonic sum), GIN-H-035 (MAX + 1 in fixed width
yields MIN under wraparound for every width).
"""
import itertools
from fractions import Fraction

from common import write
from ginsdk import ieee as I
from ginsdk import machine as M

data = {}

# 1. least unrepresentable positive integer, by search (not by formula)
res = {}
for fmt in (I.MINI8, I.BINARY16, I.BINARY32, I.BINARY64):
    # full search from 1 for small formats; for binary32/64, every integer up to 2^16 and a
    # window of 4096 integers below 2^p are checked, then the search continues upward.
    if fmt.p <= 11:
        n, checked = 1, "all integers from 1"
    else:
        assert all(I.from_int(k, fmt)[0].value() == k for k in range(1, 2 ** 16))
        n, checked = 2 ** fmt.p - 4096, "1..2^16 and 2^p-4096 upward"
    while I.from_int(n, fmt)[0].value() == n:
        n += 1
    res[fmt.name] = {"p": fmt.p, "search": checked, "least_unrepresentable_found": n, "2^p+1": 2 ** fmt.p + 1, "match": n == 2 ** fmt.p + 1,
                     "rounds_to": str(I.from_int(n, fmt)[0])}
data["least_unrepresentable_integer"] = res

# 2. exactly representable decimals
rep = []
for k in (1, 2, 3, 4):
    exact = [d for d in range(1, 10 ** k) if "inexact" not in I.round_exact(I.BINARY64, Fraction(d, 10 ** k))[1]]
    pow2 = [d for d in range(1, 10 ** k) if (Fraction(d, 10 ** k).denominator & (Fraction(d, 10 ** k).denominator - 1)) == 0]
    rep.append({"digits": k, "decimals": 10 ** k - 1, "exactly_representable": len(exact), "denominator_power_of_2": len(pow2),
                "same_set": exact == pow2, "examples": [str(Fraction(d, 10 ** k)) for d in exact[:8]]})
data["decimal_representability_binary64"] = rep

# 3. non-associativity: exhaustive over tenths a, b, c in {0.1, …, 0.9}
f = lambda s: I.from_decimal(s)[0]
cex = []
for a, b, c in itertools.product(range(1, 10), repeat=3):
    x, y, z = f(f"0.{a}"), f(f"0.{b}"), f(f"0.{c}")
    l = I.add(I.add(x, y)[0], z)[0]
    r = I.add(x, I.add(y, z)[0])[0]
    if l.bits() != r.bits():
        cex.append({"a": f"0.{a}", "b": f"0.{b}", "c": f"0.{c}", "(a+b)+c": str(l), "a+(b+c)": str(r)})
comm_fail = sum(1 for a, b in itertools.product(range(1, 10), repeat=2)
                if I.add(f(f"0.{a}"), f(f"0.{b}"))[0].bits() != I.add(f(f"0.{b}"), f(f"0.{a}"))[0].bits())
data["associativity"] = {"triples": 729, "counterexamples": len(cex), "first": cex[:5], "commutativity_failures": comm_fail}

# 4. harmonic sum order dependence (binary32 to make the effect visible quickly)
F = I.BINARY32
one = I.from_int(1, F)[0]
terms = [I.div(one, I.from_int(k, F)[0])[0] for k in range(1, 20001)]
fw = I.FP(F, "finite")
for t in terms:
    fw = I.add(fw, t)[0]
bw = I.FP(F, "finite")
for t in reversed(terms):
    bw = I.add(bw, t)[0]
exact = sum(Fraction(1, k) for k in range(1, 20001))
data["harmonic_binary32_n20000"] = {"forward": str(fw), "backward": str(bw), "exact_rounded": str(I.round_exact(F, exact)[0]),
                                    "forward_error": float(fw.value() - exact), "backward_error": float(bw.value() - exact)}

# 5. MAX + 1 across widths and policies
rows = []
for w in (8, 16, 32, 64):
    mx = 2 ** (w - 1) - 1
    rows.append({"width": w, "MAX": mx, "wrap": M.add_fixed(mx, 1, w, "wrap").value, "MIN": -2 ** (w - 1),
                 "saturate": M.add_fixed(mx, 1, w, "saturate").value, "C": M.add_fixed(mx, 1, w, "c-undefined").kind,
                 "checked": M.add_fixed(mx, 1, w, "trap").kind})
data["max_plus_one"] = rows
write("GIN-EXP-012", ["GIN-H-031", "GIN-H-032", "GIN-H-033", "GIN-H-034", "GIN-H-035"], None, data)
print("EXP-012", {k: v["match"] for k, v in res.items()}, [(r["digits"], r["exactly_representable"], r["same_set"]) for r in rep],
      len(cex), cex[:2], comm_fail, data["harmonic_binary32_n20000"])
