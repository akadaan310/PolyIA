"""E03  Forms as an alphabet: trees (alkane skeletons) and polygons (monocycles).
Generator reads: 'carbon has 4 bonds' (tree degree bound) and E01 valences.
Witnesses: Cayley/OEIS A000602 (transcribed constants), RDKit canonicaliser, Burnside, RDKit aromaticity, Chemistratum atlas."""
import sys, os, json, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from ucg import proleptic as P, forms as F
from rdkit import Chem
NMAX = 12
counts, level = F.alkane_skeletons(NMAX)
smis = {n: None for n in range(1, NMAX + 1)}
P.seal("E03_trees", counts, "free trees, max degree 4, AHU-at-centre canonical", reads=["degree<=4"])
A000602 = [1, 1, 1, 2, 3, 5, 9, 18, 35, 75, 159, 355]   # Cayley 1875; OEIS A000602 (n=1..12), transcribed
# independent canonicaliser cross-check on n<=10: RDKit canonical SMILES of every representative
_, lv = F.alkane_skeletons(10)
rd = len({Chem.MolToSmiles(Chem.MolFromSmiles(F.tree_smiles(a))) for a in lv.values()})
m = {"ours": counts, "A000602": A000602, "exact_match": counts == A000602, "rdkit_distinct_at_n10": rd}
P.witness("E03_trees", "OEIS A000602 (transcribed) + RDKit canonical SMILES", json.dumps(A000602).encode(), m)
print("trees:", m)

# ---- polygons
rings = F.enumerate_rings(3, 6, "CNOS")
burn = {}
for n in range(3, 7):
    ours = sum(1 for c, v in rings.items() if v["n"] == n)
    burn[n] = {"enumerated": ours, "naive_bracelet_k8 (wrong model)": F.burnside_bracelets(n, 8), "polya_vertex4_edge2": F.polya_ring_count(n, 4, 2), "match": ours == F.polya_ring_count(n, 4, 2)}
adm = [c for c, v in rings.items() if v["admissible"]]
preds = {}
for c in adm:
    if len(c) in (5, 6):
        a, pi, why = F.huckel(c)
        preds[F.ring_smiles(c)] = {"aromatic": a, "pi": pi, "why": why, "n": len(c)}
P.seal("E03_huckel", preds, "Hueckel 4k+2 on admissible 5/6-ring bracelets", reads=["E01 valences"])
agree = tot = 0; dis = []
for s, v in preds.items():
    mol = Chem.MolFromSmiles(s)
    if mol is None:
        continue
    ar = all(at.GetIsAromatic() for at in mol.GetAtoms())
    tot += 1; agree += ar == v["aromatic"]
    if ar != v["aromatic"]: dis.append((s, v["aromatic"], ar, v["pi"]))
atlas = json.load(open("/home/claude/su/att/a5af2628-CHEMISTRATUM_ORGANIC_STRUCTURAL_TABLE_V0_1/organic_structural_atlas/atlas.json"))
canon_pred = {}
for s, v in preds.items():
    mm = Chem.MolFromSmiles(s)
    if mm: canon_pred[Chem.MolToSmiles(mm)] = v
at_hits = []
for e in atlas["entries"]:
    if e["ringCount"] == 1 and e["ringSizes"][0] in (5, 6) and e["atoms"] == e["ringSizes"][0]:
        c = Chem.MolToSmiles(Chem.MolFromSmiles(e["smiles"]))
        if c in canon_pred: at_hits.append((e["name"], canon_pred[c]["aromatic"], e["aromatic"]))
P.witness("E03_trees", "Polya/Burnside vertex+edge colouring count (corrected witness model)", json.dumps(burn).encode(), {"burnside": burn})
mh = {"rings_enumerated_3to6": len(rings), "admissible": len(adm), "burnside_check": burn,
      "huckel_vs_rdkit": {"n": tot, "agree": agree / tot, "disagreements": dis[:12]},
      "atlas_monocycles": {"n": len(at_hits), "agree": sum(a == b for _, a, b in at_hits), "rows": at_hits}}
P.witness("E03_huckel", "RDKit aromaticity + Chemistratum atlas.json", json.dumps(at_hits).encode(), {k: v for k, v in mh.items() if k != "burnside_check"})
benz = (("C", "="), ("C", "-")) * 3
print("benzene Kekule words in one D6 orbit:", F.canon_ring(benz) == F.canon_ring(benz[1:] + benz[:1]) and benz != benz[1:] + benz[:1])
print(json.dumps(mh, indent=0, default=str)[:2500])
json.dump({"trees": m, "rings": mh}, open("results/e03.json", "w"), indent=1, default=str)
