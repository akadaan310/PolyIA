"""GIN-EXP-002  The cost of the successor in binary; carry chains.

Hypotheses: GIN-H-006 (counting from 0 to N in binary flips exactly 2N − popcount(N)
bits — the successor is amortized O(1) but worst-case Θ(log N)), GIN-H-007 (the
longest carry chain when adding two uniformly random n-bit numbers is about
log₂ n on average — Burks, Goldstine & von Neumann 1946).

Cost model: one ``flip`` per bit that changes in an increment.
"""
import math
import random

from common import write
from ginsdk import circuits as K

SEED = 20261008
data = {}

# 1. exact flip counts for all N ≤ 2^17
Nmax = 1 << 17
flips = 0
mismatch = 0
worst = 0
for x in range(Nmax):
    t = ((x ^ (x + 1)).bit_count())          # bits changed by x -> x+1
    flips += t
    worst = max(worst, t)
    N = x + 1
    if flips != 2 * N - N.bit_count():
        mismatch += 1
data["increment_flips"] = {"N_max": Nmax, "mismatches_with_2N_minus_popcount": mismatch,
                           "total_flips_to_N_max": flips, "amortized_flips_per_increment": flips / Nmax,
                           "worst_single_increment": worst,
                           "table": [{"k": k, "N": 2 ** k - 1, "flips": 2 * (2 ** k - 1) - k} for k in range(1, 11)]}

# 2. longest carry chain for random n-bit additions
rng = random.Random(SEED)
rows = []
for n in (4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096):
    samples = 3000 if n <= 1024 else 1000
    tot = 0
    mx = 0
    for _ in range(samples):
        x, y = rng.getrandbits(n), rng.getrandbits(n)
        L = K.longest_carry_chain(x, y, n)
        tot += L
        mx = max(mx, L)
    mean = tot / samples
    rows.append({"n": n, "samples": samples, "mean_longest_chain": round(mean, 4), "log2_n": round(math.log2(n), 4),
                 "mean_minus_log2_n": round(mean - math.log2(n), 4), "max_observed": mx})
data["carry_chains"] = rows

# 3. carry-class (K/P/G) frequencies for uniform digit pairs: 1/4, 1/2, 1/4
cnt = {"K": 0, "P": 0, "G": 0}
for _ in range(200_000):
    cnt[K.carry_class(rng.getrandbits(1), rng.getrandbits(1))] += 1
data["carry_class_frequencies"] = {k: round(v / 200_000, 4) for k, v in cnt.items()}

write("GIN-EXP-002", ["GIN-H-006", "GIN-H-007"], SEED, data)
print("EXP-002 done: flip mismatches", mismatch, "carry chain rows", [(r["n"], r["mean_minus_log2_n"]) for r in rows])
