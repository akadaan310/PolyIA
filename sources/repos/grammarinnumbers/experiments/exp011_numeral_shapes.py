"""GIN-EXP-011  Reading a numeral: Horner (right-linear) versus balanced composition.

Hypotheses: GIN-H-029 (both shapes evaluate a k-digit decimal numeral with k − 1
affine compositions, but the balanced shape has depth ⌈log₂ k⌉ instead of k),
GIN-H-030 (in bit cost the shape alone gains nothing — both are Θ(k²) with schoolbook
multiplication — and the balanced shape becomes subquadratic only when paired with a
subquadratic multiplication, here Karatsuba): reshaping is a mechanism only together
with a cost model that rewards it.

Cost model: ginsdk.bigint limb operations, k = 32-bit limbs.
"""
import random
import sys

from common import write
from ginsdk import bigint as B
from ginsdk import numerals as N
from ginsdk.cost import Cost

rng = random.Random(11)
# CPython ≥ 3.11 caps int<->decimal-string conversion at 4300 digits because the
# conversion is quadratic (a denial-of-service vector, CVE-2020-10735) — the very cost
# measured here.  The cap is lifted only to build the reference value.
DEFAULT_CAP = sys.get_int_max_str_digits()
sys.set_int_max_str_digits(0)


def horner(digits, c):
    acc = []
    ten = [10]
    for d in digits:
        acc = B.mul_school(acc, ten, c)
        acc = B.add(acc, B.from_int(d), c) if d else acc
    return acc


def balanced(digits, c, mul):
    # leaves: (10^1, d); compose pairs (A1, C1) then (A2, C2) -> (A1*A2, C1*A2 + C2)
    maps = [([10], B.from_int(d)) for d in digits]
    while len(maps) > 1:
        nxt = []
        for i in range(0, len(maps) - 1, 2):
            (a1, c1), (a2, c2) = maps[i], maps[i + 1]
            nxt.append((mul(a1, a2, c), B.add(mul(c1, a2, c), c2, c)))
        if len(maps) % 2:
            nxt.append(maps[-1])
        maps = nxt
    return maps[0][1]


rows = []
for k in (64, 128, 256, 512, 1024, 2048, 4096, 8192):
    digits = [rng.randrange(1, 10)] + [rng.randrange(10) for _ in range(k - 1)]
    val = int("".join(map(str, digits)))
    r = {"digits": k}
    for name, fn in (("horner", lambda c: horner(digits, c)),
                     ("balanced_schoolbook", lambda c: balanced(digits, c, B.mul_school)),
                     ("balanced_karatsuba", lambda c: balanced(digits, c, B.mul_karatsuba))):
        c = Cost()
        out = fn(c)
        assert B.to_int(out) == val
        r[name] = B.word_ops(c)
    cc = Cost()
    N.parallel_value(N.DECIMAL, digits, cc)
    r["compositions_balanced"] = cc["compose"]
    r["depth_balanced"] = cc["depth"]
    r["depth_horner"] = k
    rows.append(r)

import math
def slope(key):
    return [round(math.log2(b[key] / a[key]), 3) for a, b in zip(rows, rows[1:])]
data = {"cpython_default_int_max_str_digits": DEFAULT_CAP, "rows": rows, "loglog_slopes": {k: slope(k) for k in ("horner", "balanced_schoolbook", "balanced_karatsuba")}}
write("GIN-EXP-011", ["GIN-H-029", "GIN-H-030"], 11, data)
for k, v in data["loglog_slopes"].items():
    print(k, v)
print(rows[-1])
