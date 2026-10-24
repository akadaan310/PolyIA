"""E01  The periodic table as a computed alphabet.
Generator reads: Z only (1..118).  Witnesses: printed table (Bowserinator JSON), RDKit valence lists."""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from ucg import elements as E, proleptic as P

# ---- generate & seal (no witness bytes read yet)
pred = {Z: {"position": E.position(Z), "config": E.config_word(Z), "valences": E.valences(Z), "ion": E.ionic_charge(Z)} for Z in range(1, 119)}
P.seal("E01_alphabet", pred, "aufbau(Madelung) -> position -> valence", reads=["Z in 1..118"])

# ---- witness 1: the printed periodic table
raw = open("data/periodic.json", "rb").read()
T = {e["number"]: e for e in json.loads(raw)["elements"]}
pos_ok = per_ok = blk_ok = 0; grp_n = grp_ok = 0; conf_ok = 0; conf_miss = []
for Z in range(1, 119):
    p, t = pred[Z]["position"], T[Z]
    per_ok += p["period"] == t["period"]
    blk_ok += p["block"] == t["block"]
    if t["block"] in "spd" and t["group"] not in (None, 3) or (t["block"] == "d"):
        grp_n += 1; grp_ok += p["group"] == t["group"]
    w = " ".join(x for x in t["electron_configuration"].split() if not x.startswith("["))
    tw = sorted(t["electron_configuration"].split())
    if sorted(pred[Z]["config"].split()) == tw: conf_ok += 1
    else: conf_miss.append((t["symbol"], pred[Z]["config"], t["electron_configuration"]))
m1 = {"period": per_ok / 118, "block": blk_ok / 118, "group_spd": grp_ok / grp_n, "config_exact": conf_ok / 118, "config_exceptions": [c[0] for c in conf_miss]}
P.witness("E01_alphabet", "Bowserinator/Periodic-Table-JSON", raw, m1)
print(json.dumps(m1, indent=0)[:900])
# ---- witness 2: RDKit curated valence lists (main group, Z<=54)
from rdkit import Chem
pt = Chem.GetPeriodicTable()
rows = []
for Z in range(1, 55):
    if pred[Z]["position"]["block"] not in "sp": continue
    s = pt.GetElementSymbol(Z); rd = [v for v in pt.GetValenceList(Z) if v >= 0]
    rows.append((s, pred[Z]["valences"], rd, pred[Z]["valences"][0] == rd[0], set(rd) <= set(pred[Z]["valences"])))
m2 = {"n": len(rows), "primary_valence_agrees": sum(r[3] for r in rows) / len(rows), "rdkit_set_within_predicted": sum(r[4] for r in rows) / len(rows),
      "disagreements": [(r[0], r[1], r[2]) for r in rows if not (r[3] and r[4])]}
P.witness("E01_alphabet", "rdkit.Chem.GetPeriodicTable().GetValenceList", json.dumps([r[:3] for r in rows]).encode(), m2)
print(json.dumps(m2, indent=0))
json.dump({"alphabet": m1, "valence": m2, "config_misses": conf_miss}, open("results/e01.json", "w"), indent=1)
