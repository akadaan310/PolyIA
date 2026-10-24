"""E05  Mathematics as grammars.  Engines: ucg.calc / ucg.integrate / ucg.structures.
Witness: sympy (independent CAS), OEIS constants (transcribed), empirical convergence, known homology."""
import sys, os, json, random, time, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from fractions import Fraction as Q, Fraction
from ucg import proleptic as P
from ucg.calc import *
from ucg.integrate import Integrator
from ucg import structures as S
import sympy as sp
xs = sp.Symbol("x", positive=True)
def to_sp(e):
    h = e[0]
    if h == "x": return xs
    if h == "c": return sp.Rational(e[1].numerator, e[1].denominator)
    if h == "+": return sp.Add(*[to_sp(a) for a in e[1:]])
    if h == "*": return sp.Mul(*[to_sp(a) for a in e[1:]])
    if h == "^": return sp.Pow(to_sp(e[1]), sp.Rational(e[2].numerator, e[2].denominator))
    return {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp, "ln": sp.log, "atan": sp.atan, "asin": sp.asin}[h](to_sp(e[1]))
def num_eq(a, b, pts=(0.31, 0.62, 0.93, 1.27)):
    fa, fb = sp.lambdify(xs, a, "math"), sp.lambdify(xs, b, "math")
    for p in pts:
        try:
            u, v = float(fa(p)), float(fb(p))
        except Exception: continue
        if not (math.isfinite(u) and math.isfinite(v)): continue
        if abs(u - v) > 1e-7 * max(1, abs(u)): return False
    return True
R = random.Random(2026)
def rand_expr(d=3):
    if d == 0 or R.random() < 0.25:
        return R.choice([X, X, C(R.randint(1, 5)), mul(C(R.randint(1, 3)), X)])
    k = R.choice(["+", "*", "^", "sin", "cos", "exp", "ln", "atan", "tan"])
    if k == "+": return add(rand_expr(d - 1), rand_expr(d - 1))
    if k == "*": return mul(rand_expr(d - 1), rand_expr(d - 1))
    if k == "^": return pw(rand_expr(d - 1), R.choice([2, 3, -1, Q(1, 2)]))
    return f(k, rand_expr(d - 1))
out = {}
# ---------------- 1. differentiation grammar vs sympy
corpus = [rand_expr() for _ in range(400)]
ours = [D(e) for e in corpus]
P.seal("E05_diff", [repr(o) for o in ours], "rewrite rules D:{x,const,linearity,product,power+chain,f+chain}", reads=["expression corpus (generated)"])
agree = sum(num_eq(sp.diff(to_sp(e), xs), to_sp(o)) for e, o in zip(corpus, ours))
out["differentiation"] = {"n": len(corpus), "agree_with_sympy": agree}
P.witness("E05_diff", "sympy.diff", sp.__version__.encode(), out["differentiation"]); print("diff:", out["differentiation"])
# ---------------- 2. D-orbit classes and characteristic words
LIB = {"sin x": f("sin", X), "cos x": f("cos", X), "e^x": f("exp", X), "x^3": pw(X, 3), "x^5-x": add(pw(X, 5), mul(C(-1), X)), "e^x sin x": mul(f("exp", X), f("sin", X)),
       "x^2 e^x": mul(pw(X, 2), f("exp", X)), "x e^(2x) cos x": mul(X, f("exp", mul(C(2), X)), f("cos", X)), "e^x+e^-x": add(f("exp", X), f("exp", mul(C(-1), X))),
       "sin(2x)+cos(3x)": add(f("sin", mul(C(2), X)), f("cos", mul(C(3), X))), "ln x": f("ln", X), "tan x": f("tan", X), "sin(x^2)": f("sin", pw(X, 2)),
       "atan x": f("atan", X), "1/x": pw(X, -1), "sqrt x": pw(X, Q(1, 2))}
cls = {}
for k, e in LIB.items():
    oc = orbit_class(e); r, word, _ = d_orbit_rank(e, 8)
    cls[k] = {"orbit": oc, "char_word": word}
P.seal("E05_orbits", cls, "D-orbit classification + annihilator from finite span", reads=["function library"])
Dsym = lambda g, n: sp.diff(g, xs, n)
wit_ok = 0; wit_n = 0
for k, v in cls.items():
    if v["char_word"]:
        g = to_sp(LIB[k]); w = [sp.nsimplify(c) for c in v["char_word"]]
        expr = sum(w[i] * Dsym(g, i) for i in range(len(w)))
        wit_n += 1; wit_ok += sp.simplify(sp.expand(expr)) == 0
out["orbits"] = {"classes": {k: v["orbit"]["class"] for k, v in cls.items()}, "char_words": {k: v["char_word"] for k, v in cls.items() if v["char_word"]},
                 "annihilators_verified_by_sympy": f"{wit_ok}/{wit_n}"}
P.witness("E05_orbits", "sympy symbolic annihilation", sp.__version__.encode(), out["orbits"]); print("orbits:", out["orbits"])
# ---------------- 3. integration machines
I = Integrator(depth=7)
TEXTBOOK = {"x^4": pw(X, 4), "1/x": pw(X, -1), "sqrt x": pw(X, Q(1, 2)), "e^x": f("exp", X), "sin x": f("sin", X), "cos x": f("cos", X), "tan x": f("tan", X),
  "sec^2 x": pw(f("cos", X), -2), "1/(1+x^2)": pw(add(C(1), pw(X, 2)), -1), "3x^2+2x+1": add(mul(C(3), pw(X, 2)), mul(C(2), X), C(1)),
  "2x cos(x^2)": mul(C(2), X, f("cos", pw(X, 2))), "x e^(x^2)": mul(X, f("exp", pw(X, 2))), "cos x e^(sin x)": mul(f("cos", X), f("exp", f("sin", X))),
  "x/(1+x^2)": mul(X, pw(add(C(1), pw(X, 2)), -1)), "ln(x)/x": mul(f("ln", X), pw(X, -1)), "sin x cos x": mul(f("sin", X), f("cos", X)),
  "x e^x": mul(X, f("exp", X)), "x sin x": mul(X, f("sin", X)), "x^2 cos x": mul(pw(X, 2), f("cos", X)), "ln x": f("ln", X), "x ln x": mul(X, f("ln", X)),
  "atan x": f("atan", X), "e^x sin x": mul(f("exp", X), f("sin", X)), "e^x cos x": mul(f("exp", X), f("cos", X)), "1/(x^2-1)": pw(add(pw(X, 2), C(-1)), -1),
  "1/(x^2+4)": pw(add(pw(X, 2), C(4)), -1), "1/(x(x+1))": pw(mul(X, add(X, C(1))), -1), "(2x+3)/(x^2+3x+2)": mul(add(mul(C(2), X), C(3)), pw(add(pw(X, 2), mul(C(3), X), C(2)), -1)),
  "x^3 e^x": mul(pw(X, 3), f("exp", X)), "sin^2 x cos x": mul(pw(f("sin", X), 2), f("cos", X))}
NONELEM = {"e^(-x^2)": f("exp", mul(C(-1), pw(X, 2))), "sin(x)/x": mul(f("sin", X), pw(X, -1)), "e^x/x": mul(f("exp", X), pw(X, -1)), "1/ln x": pw(f("ln", X), -1), "sin(x^2)": f("sin", pw(X, 2))}
GEN = []
while len(GEN) < 150:
    F_ = rand_expr(2)
    if all(n[0] != "x" for n in walk(F_)): continue
    GEN.append(D(F_))
def run_set(S_):
    res = {}
    for k, e in S_.items():
        t0 = time.time(); r = I.run(e); dt = time.time() - t0
        res[k] = {"ok": r["ok"], "result": repr(r.get("result")), "states": len(r["trace"]), "methods": sorted({s.split(":")[0].split("->")[0] for s in r["trace"] if s[0].isupper() and s not in ("CLASSIFY", "EMIT")}), "sec": round(dt, 4)}
    return res
tb, ne, gen = run_set(TEXTBOOK), run_set(NONELEM), run_set({f"g{i}": e for i, e in enumerate(GEN)})
P.seal("E05_integration", {"textbook": tb, "nonelementary": ne, "generated": gen}, "state machines TABLE/LINEARITY/USUB/PARTS/PARTIAL_FRACTIONS + VERIFY", reads=["integrands only"])
def sympy_check(S_, res):
    ok = 0; base = 0; base_time = 0.0
    for k, e in S_.items():
        if res[k]["ok"]:
            ok += num_eq(sp.diff(to_sp(eval(res[k]["result"])), xs), to_sp(e))
        t0 = time.time()
        try:
            r = sp.integrate(to_sp(e), xs)
            special = any(fn in str(r) for fn in ("erf", "Si", "Ei", "li", "fresnel", "Integral", "Ci", "gamma"))
            base += (not special)
        except Exception:
            special = True
        base_time += time.time() - t0
    return ok, base, round(base_time, 2)
def classify(e):
    heads = {n[0] for n in walk(e)}
    tr = heads & {"sin", "cos", "tan", "atan", "asin"}; ex = heads & {"exp", "ln"}
    return "algebraic" if not tr and not ex else ("trig" if tr and not ex else ("exp/log" if ex and not tr else "mixed"))
rep = {}
for name, S_, res in [("textbook", TEXTBOOK, tb), ("nonelementary", NONELEM, ne), ("generated", {f"g{i}": e for i, e in enumerate(GEN)}, gen)]:
    v, base, bt = sympy_check(S_, res)
    by = {}
    for k, e in S_.items():
        c = classify(e); by.setdefault(c, [0, 0, 0]); by[c][0] += 1; by[c][1] += res[k]["ok"]; by[c][2] += res[k]["states"]
    rep[name] = {"n": len(S_), "ours_solved": sum(r["ok"] for r in res.values()), "ours_verified_by_sympy": v, "sympy_elementary_answers": base,
                 "sympy_seconds": bt, "ours_seconds": round(sum(r["sec"] for r in res.values()), 3),
                 "by_function_class": {c: {"n": a, "solved": b, "mean_states": round(s / a, 1)} for c, (a, b, s) in by.items()},
                 "unsolved": [k for k, r in res.items() if not r["ok"]][:20]}
from collections import Counter
rep["method_usage_textbook"] = Counter(m for r in tb.values() if r["ok"] for m in r["methods"])
out["integration"] = rep
P.witness("E05_integration", "sympy.integrate + sympy.diff", sp.__version__.encode(), rep); print("integration:", json.dumps(rep, indent=0, default=str)[:3000])
# ---------------- 4. Butcher trees
trees = S.rooted_trees(7)
bt = {k: S.tree_order(*v)[0] for k, v in S.TABLEAUX.items()}
P.seal("E05_butcher", {"tree_counts": [len(trees[n]) for n in range(1, 8)], "orders": bt}, "Butcher order conditions Phi(t)=1/gamma(t)", reads=["tableaux"])
emp = {k: S.empirical_order(*v)[0] for k, v in S.TABLEAUX.items()}
out["butcher"] = {"A000081": [1, 1, 2, 4, 9, 20, 48], "ours": [len(trees[n]) for n in range(1, 8)], "predicted_order": bt, "empirical_slope": emp,
                  "agree": all(abs(bt[k] - emp[k]) < 0.25 for k in bt)}
P.witness("E05_butcher", "empirical convergence on y'=y cos x + OEIS A000081", json.dumps(emp).encode(), out["butcher"]); print("butcher:", out["butcher"])
# ---------------- 5. groups (grammar extension driven by gaps)
A000001 = [1, 1, 1, 2, 1, 2, 1, 5, 2, 2, 1, 5, 1, 2, 1]
stages = {}
for name, prods in [("G0 cyclic,direct,cyclic-semidirect", ("cyclic", "direct", "semidirect")), ("G1 +dicyclic", ("cyclic", "direct", "semidirect", "dicyclic")),
                    ("G2 +general semidirect", ("cyclic", "direct", "semidirect", "dicyclic", "semidirect_general"))]:
    c, found = S.generate_groups(15, prods)
    P.seal(f"E05_groups_{name[:2]}", c, name, reads=["productions only"])
    stages[name] = {"counts": c, "gaps_at": [n + 1 for n in range(15) if c[n] != A000001[n]], "all_tables_are_groups": all(G.is_group() for G in found.values())}
    P.witness(f"E05_groups_{name[:2]}", "OEIS A000001 (transcribed)", json.dumps(A000001).encode(), stages[name])
out["groups"] = {"A000001": A000001, "stages": stages}; print("groups:", stages)
# ---------------- 6. homology
KNOWN = {"S2": ((1, 0, 1), (1, 0, 1), 2), "T2": ((1, 2, 1), (1, 2, 1), 0), "RP2": ((1, 0, 0), (1, 1, 1), 1), "Klein": ((1, 1, 0), (1, 2, 1), 0)}
cx = {"S2": S.SPHERE, "T2": S.torus(), "RP2": S.RP2, "Klein": S.klein()}
pred = {k: {"Q": S.betti(v)[0], "F2": S.betti(v, 2)[0], "chi": S.betti(v)[1], "dd0": S.betti(v)[2], "closed_surface": S.is_closed_surface(v)} for k, v in cx.items()}
P.seal("E05_homology", pred, "boundary matrices, ranks over Q and F2", reads=["triangulations"])
out["homology"] = {k: {**pred[k], "matches_known": (tuple(pred[k]["Q"]), tuple(pred[k]["F2"]), pred[k]["chi"]) == KNOWN[k]} for k in pred}
P.witness("E05_homology", "standard homology of surfaces (textbook)", json.dumps(KNOWN).encode(), out["homology"]); print("homology:", out["homology"])
# ---------------- 7. linear systems: the two failures
cases = {"unique": ([[2, 1], [1, 3]], [3, 5]), "kernel failure": ([[1, 2], [2, 4]], [3, 6]), "image failure": ([[1, 2], [2, 4]], [3, 7])}
out["linear"] = {k: S.solve_linear(*v)[0] for k, v in cases.items()}
print("linear:", out["linear"])
json.dump(out, open("results/e05.json", "w"), indent=1, default=str)
print("ledger verifies:", P.verify())
