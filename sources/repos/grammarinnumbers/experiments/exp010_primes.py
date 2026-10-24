"""GIN-EXP-010  Primality: admissibility tests and their counterexamples.

Hypotheses: GIN-H-025 (Fermat's test to base 2 admits composites — pseudoprimes —
and Carmichael numbers defeat every coprime base; the counts below 10^6 are the
published ones: 245 base-2 pseudoprimes, 46 strong base-2 pseudoprimes, 43
Carmichael numbers), GIN-H-026 (the deterministic Miller–Rabin base set agrees with
the sieve on every n ≤ 10^6), GIN-H-027 (the sieve performs ~ n ln ln n crossings;
trial division costs ~ √n divisions for a prime n), GIN-H-028 (Pollard rho finds a
factor p after ~ √p steps).
"""
import math
import random

from common import write
from ginsdk import numbertheory as T
from ginsdk.cost import Cost

LIMIT = 10 ** 6
data = {}
c = Cost()
primes = T.sieve(LIMIT, c)
pset = set(primes)
data["sieve"] = {"limit": LIMIT, "primes": len(primes), "crossings": c["cross"],
                 "n_lnln_n": round(LIMIT * math.log(math.log(LIMIT))), "ratio": round(c["cross"] / (LIMIT * math.log(math.log(LIMIT))), 4)}

psp2, spsp2, carm = [], [], []
mr_disagree = 0
for n in range(3, LIMIT + 1, 2):
    isp = n in pset
    if T.is_prime(n) != isp:
        mr_disagree += 1
    if not isp:
        if T.fermat_test(n, 2):
            psp2.append(n)
            if T.strong_probable_prime(n, 2):
                spsp2.append(n)
# Carmichael numbers via Korselt (odd composite, squarefree, p−1 | n−1)
spf = list(range(LIMIT + 1))
for p in range(2, int(LIMIT ** 0.5) + 1):
    if spf[p] == p:
        for q in range(p * p, LIMIT + 1, p):
            if spf[q] == q:
                spf[q] = p
for n in range(3, LIMIT + 1, 2):
    if spf[n] == n:
        continue
    m, ok, k = n, True, 0
    while m > 1:
        p = spf[m]
        m //= p
        k += 1
        if m % p == 0 or (n - 1) % (p - 1):
            ok = False
            break
    if ok and k >= 2:
        carm.append(n)
data["pseudoprimes_below_1e6"] = {"fermat_base2": len(psp2), "strong_base2": len(spsp2), "carmichael": len(carm),
                                  "first_fermat_base2": psp2[:10], "first_strong_base2": spsp2[:10], "first_carmichael": carm[:10],
                                  "published": {"fermat_base2": 245, "strong_base2": 46, "carmichael": 43}}
data["miller_rabin_vs_sieve"] = {"checked_odd_n_up_to": LIMIT, "disagreements": mr_disagree}

# trial division cost on primes
rows = []
for k in (10, 14, 18, 22, 26, 30):
    n = next(x for x in range(2 ** k + 1, 2 ** (k + 1)) if T.is_prime(x))
    cc = Cost()
    T.is_prime_trial(n, cc)
    rows.append({"bits": k + 1, "prime": n, "divisions": cc["division"], "sqrt_n_over_2": round(math.isqrt(n) / 2)})
data["trial_division"] = rows

# Pollard rho steps vs sqrt(p)
rng = random.Random(10)
rr = []
for k in (10, 14, 18, 22, 26):
    tot, ratio = 0, 0.0
    for _ in range(20):
        while True:
            p = rng.randrange(2 ** (k - 1), 2 ** k) | 1
            if T.is_prime(p):
                break
        while True:
            q = rng.randrange(2 ** 40, 2 ** 41) | 1
            if T.is_prime(q):
                break
        cc = Cost()
        f = None
        cst = 1
        while f is None:
            f = T.pollard_rho(p * q, cst, cc)
            cst += 1
        tot += cc["step"]
        ratio += cc["step"] / math.sqrt(p)
    rr.append({"p_bits": k, "mean_steps": round(tot / 20, 1), "mean_steps_over_sqrt_p": round(ratio / 20, 3)})
data["pollard_rho"] = rr
write("GIN-EXP-010", ["GIN-H-025", "GIN-H-026", "GIN-H-027", "GIN-H-028"], 10, data)
print("EXP-010", data["sieve"], data["pseudoprimes_below_1e6"]["fermat_base2"], data["pseudoprimes_below_1e6"]["strong_base2"],
      data["pseudoprimes_below_1e6"]["carmichael"], mr_disagree, rows, rr)
