"""GIN-EXP-009  Euclid's algorithm as a transition system.

Hypotheses: GIN-H-022 (Lamé: the smallest pair needing k division steps is
(F_{k+2}, F_{k+1}), so steps ≤ log_φ(a) + O(1)), GIN-H-023 (Heilbronn/Dixon/Porter:
for fixed n the average number of steps over 1 ≤ m < n coprime to n is
(12 ln 2/π²) ln n + C_P + o(1), with Porter's constant C_P ≈ 1.4670780794),
GIN-H-024 (the extended-Euclid coefficients satisfy |s| ≤ b/(2g) and |t| ≤ a/(2g)).

Cost model: one step = one division with remainder.
"""
import math
import random

from common import write
from ginsdk import numbertheory as T

data = {}
N = 1200
first = {}
maxsteps = 0
hist = {}
for a in range(1, N + 1):
    for b in range(1, a):
        k = T.euclid_steps(a, b)
        hist[k] = hist.get(k, 0) + 1
        if k not in first:
            first[k] = (a, b)
        maxsteps = max(maxsteps, k)
lame = {k: {"smallest_pair": first[k], "fibonacci_pair": T.lame_worst_pair(k), "match": first[k] == T.lame_worst_pair(k)} for k in sorted(first)}
phi = (1 + 5 ** 0.5) / 2
data["lame"] = {"N": N, "max_steps": maxsteps, "bound_log_phi_N": round(math.log(N, phi), 3), "smallest_pairs": lame,
                "all_match": all(v["match"] for v in lame.values()), "histogram": dict(sorted(hist.items()))}

# Porter's constant check: tau(n) for primes n
porter = 1.4670780794
c = 12 * math.log(2) / math.pi ** 2
rows = []
for n in (1009, 10007, 100003, 1000003):
    tot = sum(T.euclid_steps(n, m) for m in range(1, n))
    tau = tot / (n - 1)
    pred = c * math.log(n) + porter
    rows.append({"n": n, "average_steps": round(tau, 6), "prediction": round(pred, 6), "difference": round(tau - pred, 6)})
data["average_steps_prime_n"] = {"coefficient_12ln2_over_pi2": round(c, 10), "porter_constant": porter, "rows": rows}

# Bezout coefficient bounds
rng = random.Random(9)
viol = 0
for _ in range(20000):
    a, b = rng.randint(1, 10 ** 12), rng.randint(1, 10 ** 12)
    g, s, t = T.bezout(a, b)
    if a != b and (abs(s) > b // (2 * g) + (b // g == 1) or abs(t) > a // (2 * g) + (a // g == 1)):
        viol += 1
data["bezout_bounds"] = {"samples": 20000, "violations": viol}

# binary gcd moves versus Euclid steps on random 64-bit pairs
mv, st = 0, 0
for _ in range(5000):
    a, b = rng.getrandbits(64) | 1, rng.getrandbits(64) | 1
    _, moves = T.binary_gcd_trace(a, b)
    mv += sum(1 for m in moves if m == "subtract")
    st += T.euclid_steps(a, b)
data["binary_vs_euclid_64bit"] = {"mean_subtractions_binary": mv / 5000, "mean_divisions_euclid": st / 5000}

write("GIN-EXP-009", ["GIN-H-022", "GIN-H-023", "GIN-H-024"], 9, data)
print("EXP-009", data["lame"]["all_match"], data["lame"]["max_steps"], rows, viol, data["binary_vs_euclid_64bit"])
