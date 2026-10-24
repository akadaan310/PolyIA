"""GIN-EXP-001  Numerals as operation expressions; the successor grammar.

Hypotheses: GIN-H-001 (numeral ≠ number: the numeral→value map is surjective but
not injective exactly because of leading zeros), GIN-H-002 (zero's canonical
numeral is the empty word), GIN-H-003 (bijective notation removes the
non-injectivity), GIN-H-004 (the CGT heap grammar is bijective binary, shifted),
GIN-H-005 (unary/Peano arithmetic costs time linear in the *value*).

Cost model: one ``rule`` per primitive-recursion equation applied (Peano); one
bit operation per bit position (schoolbook binary addition).
"""
from common import write, Timer
from ginsdk import numerals as N, peano as P
from ginsdk.cost import Cost

data = {}

# 1. non-injectivity profile: words of length ≤ L denoting n
L = 8
prof = {}
for b in (2, 3, 10):
    g = N.standard(b)
    rows = []
    for n in range(0, 30):
        words = g.words_denoting(n, L) if b < 10 else g.words_denoting(n, 4)
        canon = g.address(n)
        Lb = L if b < 10 else 4
        rows.append({"n": n, "canonical": g.render(canon), "words": len(words),
                     "formula_L_minus_len_plus_1": Lb - len(canon) + 1})
    prof[f"standard base {b}"] = {"max_length": L if b < 10 else 4, "rows": rows,
                                   "all_match_formula": all(r["words"] == r["formula_L_minus_len_plus_1"] for r in rows)}
data["non_injectivity"] = prof

# 2. bijective numeration is a bijection between words and N
bij = {}
for b, Lmax in ((1, 20), (2, 14), (3, 9), (10, 5)):
    g = N.bijective(b)
    values = set()
    layer = [()]
    total = 1
    values.add(0)
    collisions = 0
    for _ in range(Lmax):
        layer = [w + (d,) for w in layer for d in g.digits]
        for w in layer:
            v = g.denote(w)
            if v in values:
                collisions += 1
            values.add(v)
        total += len(layer)
    covered = max(values) + 1 == len(values)
    bij[f"bijective base {b}"] = {"max_length": Lmax, "words": total, "distinct_values": len(values),
                                   "collisions": collisions, "values_form_initial_segment": covered, "max_value": max(values)}
data["bijective"] = bij

# 3. heap conjugacy (GIN-PROP-006)
Nmax = 200_000
bad = sum(1 for n in range(Nmax) if N.bijective2_as_heap(n) != N.heap_word(n + 1))
data["heap_conjugacy"] = {"checked_n_below": Nmax, "mismatches": bad,
                          "examples": {n: {"bijective2": N.bijective(2).render(N.bijective(2).address(n)), "heap_of_n_plus_1": N.heap_word(n + 1)} for n in range(0, 9)}}

# 4. two's complement = truncated 2-adic expansion (GIN-PROP-008)
mism = 0
for w in (4, 8, 16):
    for n in range(-(1 << (w - 1)), 1 << (w - 1)):
        if N.twos_complement_from_2adic(n, w) != format(n & ((1 << w) - 1), f"0{w}b"):
            mism += 1
digits, status = N.BINARY.expand(-1, 64)
data["twos_complement"] = {"widths": [4, 8, 16], "mismatches": mism, "expansion_of_minus_1_status": status,
                           "expansion_of_minus_5": "".join(map(str, reversed(N.BINARY.expand(-5)[0]))) + " (then repeats)"}

# 5. Peano (unary) arithmetic: cost linear in values = exponential in numeral length
rows = []
for k in range(1, 21):
    n = 2 ** k - 1
    c = Cost()
    P.add(n, n, c)
    cm = Cost()
    if k <= 10:
        P.mul(n, n, cm)
    rows.append({"bits": k, "n": n, "peano_add_rules": c["rule"], "binary_add_bit_ops": k + 1,
                 "peano_mul_rules": cm["rule"] if k <= 10 else None, "binary_school_mul_bit_ops": k * k})
data["unary_vs_binary_cost"] = rows

# 6. address lengths
lens = []
for b in (2, 3, 10):
    g, h = N.standard(b), N.bijective(b)
    lens.append({"base": b, "max_len_standard_1999": len(g.address(1999)), "max_len_bijective_1999": len(h.address(1999))})
data["address_lengths"] = lens

write("GIN-EXP-001", ["GIN-H-001", "GIN-H-002", "GIN-H-003", "GIN-H-004", "GIN-H-005"], None, data)
print("EXP-001 done:", {k: (v["all_match_formula"] if isinstance(v, dict) and "all_match_formula" in v else "") for k, v in prof.items()},
      "heap mismatches", bad, "2c mismatches", mism)
