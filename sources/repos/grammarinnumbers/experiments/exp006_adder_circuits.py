"""GIN-EXP-006  Adder circuits: the same function, different grammar shapes.

Hypotheses: GIN-H-016 (ripple-carry has 5n − 3 gates and depth 2n − 1; parallel-prefix
adders over the carry monoid trade more gates for depth O(log n) — the circuit
counterpart of CGT-THM-004), GIN-H-017 (all four constructions compute n-bit addition;
checked exhaustively for n ≤ 8 and on random inputs up to n = 64).

Cost model: gates from the basis {NOT, AND, OR, XOR} with fan-in ≤ 2; depth = longest
gate path from an input to an output.
"""
import random

from common import write
from ginsdk import circuits as K

SEED = 6
rng = random.Random(SEED)
data = {"exhaustive": {}, "random": {}, "cost": []}

for n in range(1, 9):
    res = {}
    for name, make in K.ADDERS.items():
        c = make(n)
        bad = 0
        for x in range(2 ** n):
            for y in range(2 ** n):
                if K.int_of(K.apply_words(c, a=(x, n), b=(y, n))) != x + y:
                    bad += 1
        res[name] = {"pairs": 4 ** n, "errors": bad}
    data["exhaustive"][n] = res

for n in (16, 32, 64):
    res = {}
    for name, make in K.ADDERS.items():
        c = make(n)
        bad = sum(1 for _ in range(300) for x, y in [(rng.getrandbits(n), rng.getrandbits(n))]
                  if K.int_of(K.apply_words(c, a=(x, n), b=(y, n))) != x + y)
        res[name] = {"pairs": 300, "errors": bad}
    data["random"][n] = res

for n in (1, 2, 4, 8, 16, 32, 64, 128, 256):
    row = {"n": n}
    for name, make in K.ADDERS.items():
        c = make(n)
        row[name] = {"gates": c.size, "depth": c.depth()}
    row["ripple_formula_ok"] = row["ripple-carry"]["gates"] == 5 * n - 3 and row["ripple-carry"]["depth"] == 2 * n - 1
    data["cost"].append(row)

# carry monoid table
E = K.CARRY_ELEMENTS
data["carry_monoid"] = {"elements": {"K": "c ↦ 0 (kill)", "P": "c ↦ c (propagate)", "G": "c ↦ 1 (generate)"},
                        "table_lo_then_hi": {lo: {hi: K.carry_compose(lo, hi) for hi in E} for lo in E},
                        "identity": "P", "associative": all(K.carry_compose(K.carry_compose(x, y), z) == K.carry_compose(x, K.carry_compose(y, z)) for x in E for y in E for z in E)}
# NAND full adder
data["full_adder"] = {"basis_and_or_xor": K.full_adder().gate_counts(), "nand_only": K.full_adder_nand().gate_counts()}

write("GIN-EXP-006", ["GIN-H-016", "GIN-H-017"], SEED, data)
print("EXP-006 errors:", sum(v["errors"] for r in data["exhaustive"].values() for v in r.values()) + sum(v["errors"] for r in data["random"].values() for v in r.values()))
for r in data["cost"]:
    print(r["n"], {k: (v["gates"], v["depth"]) for k, v in r.items() if isinstance(v, dict)}, r["ripple_formula_ok"])
