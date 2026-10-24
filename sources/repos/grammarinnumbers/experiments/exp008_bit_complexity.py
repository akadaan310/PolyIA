"""GIN-EXP-008  Bit complexity of arithmetic: unit cost is a fiction for growing operands.

Hypotheses: GIN-H-020 (counted 32-bit word operations grow linearly in the bit length
for +, −, comparison; quadratically for schoolbook × and long division; as n^1.585
for Karatsuba; quadratically for Euclid's gcd; cubically for modular exponentiation
with an L-bit exponent), GIN-H-021 (Python's built-in int shows the same ordering in
wall-clock time — secondary evidence only).

Cost model: ginsdk.bigint counts limb operations (add/sub-with-carry, limb product,
two-by-one-limb quotient estimate, limb comparison) on k = 32-bit limbs.
"""
import math
import random
import time

from common import write
from ginsdk import bigint as B
from ginsdk.cost import Cost

SEED = 8
rng = random.Random(SEED)


def rand_bits(L):
    return rng.getrandbits(L) | (1 << (L - 1))


def ops(fn):
    c = Cost()
    fn(c)
    return B.word_ops(c)


rows = []
for L in (64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384):
    a, b = rand_bits(L), rand_bits(L)
    A, Bv = B.from_int(a), B.from_int(b)
    big, BIG = rand_bits(2 * L), None
    BIG = B.from_int(big)
    r = {"bits": L, "limbs": len(A)}
    r["add"] = ops(lambda c: B.add(A, Bv, c))
    r["sub"] = ops(lambda c: B.sub(*(sorted([A, Bv], key=B.to_int, reverse=True)), c))
    r["compare_equal"] = ops(lambda c: B.compare(A, list(A), c))
    r["mul_schoolbook"] = ops(lambda c: B.mul_school(A, Bv, c))
    r["mul_karatsuba"] = ops(lambda c: B.mul_karatsuba(A, Bv, c))
    r["divmod_2L_by_L"] = ops(lambda c: B.divmod_limbs(BIG, Bv, c))
    if L <= 4096:
        r["gcd_euclid"] = ops(lambda c: B.gcd_euclid(A, Bv, c))
        r["gcd_binary"] = ops(lambda c: B.gcd_binary(a, b, c))
    if L <= 512:
        m = rand_bits(L) | 1
        r["powmod_L_bit_exponent"] = ops(lambda c: B.powmod(a, b, m, c))
    # secondary: CPython int wall clock (median of 5)
    def t(f, reps):
        best = []
        for _ in range(5):
            t0 = time.perf_counter()
            for _ in range(reps):
                f()
            best.append((time.perf_counter() - t0) / reps)
        return sorted(best)[2]
    r["cpython_mul_s"] = t(lambda: a * b, 200)
    r["cpython_divmod_s"] = t(lambda: divmod(big, b), 200)
    rows.append(r)


def slopes(key):
    pts = [(r["bits"], r[key]) for r in rows if r.get(key)]
    return [round(math.log2(y2 / y1) / math.log2(x2 / x1), 3) for (x1, y1), (x2, y2) in zip(pts, pts[1:])]


keys = ["add", "sub", "compare_equal", "mul_schoolbook", "mul_karatsuba", "divmod_2L_by_L", "gcd_euclid", "gcd_binary", "powmod_L_bit_exponent"]
data = {"limb_bits": B.K, "rows": rows, "loglog_slopes": {k: slopes(k) for k in keys},
        "karatsuba_vs_school_at_max": round(rows[-1]["mul_schoolbook"] / rows[-1]["mul_karatsuba"], 3)}
write("GIN-EXP-008", ["GIN-H-020", "GIN-H-021"], SEED, data)
for k, v in data["loglog_slopes"].items():
    print(f"{k:24s}", v)
