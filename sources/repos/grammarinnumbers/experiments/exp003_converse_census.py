"""GIN-EXP-003  Converse admissibility: a census of division and its relatives.

Hypotheses: GIN-H-008 (division failures split into exactly two kinds — no solution
and non-unique — and in a commutative ring the solution set of b·c = a is empty or a
coset of Ann(b)), GIN-H-009 (in Z/n the share of pairs (a, b) with a unique quotient
is φ(n)/n), GIN-H-010 (the same expression fails at different layers in different
domains).

Everything is exhaustive or exact; no randomness.
"""
import math

from common import write
from ginsdk import converse as C
from ginsdk import expr as E
from ginsdk import numbertheory as T

data = {}

# 1. Z/n census
rows = []
violations = 0
for n in range(1, 65):
    counts = {"no-solution": 0, "unique": 0, "non-unique": 0}
    for b in range(n):
        ann = len(C.annihilator_mod(b, n))
        for a in range(n):
            sols = [c for c in range(n) if b * c % n == a]
            k = C.classify(sols)
            counts[k] += 1
            if sols and len(sols) != ann:
                violations += 1
    phi = T.phi(n) if n > 1 else 1
    solvable_formula = sum(n // math.gcd(b, n) for b in range(n))
    rows.append({"n": n, **counts, "pairs": n * n, "unique_share": round(counts["unique"] / (n * n), 6),
                 "phi_over_n": round(phi / n, 6), "solvable": counts["unique"] + counts["non-unique"],
                 "solvable_formula_sum_n_over_gcd": solvable_formula})
data["zmod_census"] = {"rows": rows, "coset_size_violations": violations,
                       "unique_share_equals_phi_over_n": all(abs(r["unique_share"] - r["phi_over_n"]) < 1e-9 for r in rows),
                       "solvable_matches_formula": all(r["solvable"] == r["solvable_formula_sum_n_over_gcd"] for r in rows)}

# 2. the meaning table of the canonical expressions across domains
exprs = ["6 / 3", "0 / 1", "1 / 0", "0 / 0", "-1 / 0", "1 / -0", "7 / 2", "0 - 1", "2 / 4", "sqrt(-1)", "0^0", "0^-1",
         "2147483647 + 1", "(-2147483647 - 1) / -1"]
doms = ["N", "Z", "Q", "C", "Z/6", "Z/7", "binary64", "Python", "JS BigInt", "int32 x86-64", "int32 AArch64",
        "int32 RISC-V", "int32 C", "int32 Java", "int32 Rust (debug)"]
table = {}
for e in exprs:
    table[e] = {}
    for d in doms:
        o = E.evaluate(e, d)
        table[e][d] = {"status": o.status, "layer": o.layer, "display": o.display, "flags": o.flags,
                       "reason": o.reason[:200]}
data["meaning_table"] = {"domains": doms, "table": table}

# 3. x/0 and 0/x families, exact and symbolic
fam = {}
for x in (-2, -1, 0, 1, 3):
    fam[f"x={x}"] = {"x / 0": E.evaluate("x / 0", "Q", {"x": x}).status, "0 / x": E.evaluate("0 / x", "Q", {"x": x}).status,
                     "x / x": E.evaluate("x / x", "Q", {"x": x}).status}
for e in ("x / 0", "0 / x", "x / x", "(x^2 - 1) / (x - 1)", "1 / (x^2 + 1)", "x / (x - x)"):
    o = E.evaluate(e, "symbolic")
    fam[f"symbolic {e}"] = {"status": o.status, "display": o.display, "representation": o.representation, "reason": o.reason}
# binary64 approach to 0 from both sides
appr = []
for k in (1, 10, 100, 300, 320, 330):
    for s in ("", "-"):
        q = "0." + "0" * (k - 1) + "1"           # the decimal 10^-k, rounded to binary64 by the parser
        o = E.evaluate(f"1 / ({s}{q})", "binary64")
        x = f"{s}10^-{k}"
        appr.append({"x": x, "1/x": o.display, "flags": o.flags})
fam["binary64_one_over_x_toward_0"] = appr
data["families"] = fam

# 4. other converse problems
other = {}
for a in (4, 2, 0, -1, -4):
    other[f"sqrt({a})"] = {c: C.square_root(a, c).kind for c in ("N", "Q", "R", "C")}
for a in (1, 0, -1):
    other[f"log({a})"] = {c: C.logarithm(a, c).kind for c in ("R", "C")}
for (b, n) in ((3, 7), (2, 6), (5, 12), (4, 12)):
    other[f"inverse of {b} mod {n}"] = C.modular_inverse(b, n).kind
data["other_converse"] = other

write("GIN-EXP-003", ["GIN-H-008", "GIN-H-009", "GIN-H-010"], None, data)
print("EXP-003 done: violations", violations, data["zmod_census"]["unique_share_equals_phi_over_n"], data["zmod_census"]["solvable_matches_formula"])
