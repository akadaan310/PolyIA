"""E04  Nomenclature grammars: systematic element names; alkane names <-> structures."""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from ucg import proleptic as P, forms as F, nomen as N
from rdkit import Chem
# (a) element names
pred = {Z: (N.element_name(Z), N.element_symbol(Z)) for Z in range(104, 121)}
P.seal("E04_elements", pred, "IUPAC 1978 root grammar", reads=["digits of Z"])
HIST = {104: "unnilquadium", 105: "unnilpentium", 106: "unnilhexium", 107: "unnilseptium", 108: "unniloctium", 109: "unnilennium",
        110: "ununnilium", 111: "unununium", 112: "ununbium", 113: "ununtrium", 114: "ununquadium", 115: "ununpentium",
        116: "ununhexium", 117: "ununseptium", 118: "ununoctium", 119: "ununennium", 120: "unbinilium"}   # historical placeholders [K]
SYMS = {112: "Uub", 118: "Uuo", 114: "Uuq", 119: "Uue", 120: "Ubn"}
ok = sum(pred[z][0] == HIST[z] for z in HIST); oks = sum(pred[z][1] == SYMS[z] for z in SYMS)
rt = all(N.parse_element_name(N.element_name(z)) == z for z in range(1, 1000))
inj = len({N.element_name(z) for z in range(1, 1000)}) == 999
m1 = {"names_match": f"{ok}/{len(HIST)}", "symbols_match": f"{oks}/{len(SYMS)}", "roundtrip_Z_1_999": rt, "injective_1_999": inj,
      "mismatches": [(z, pred[z][0], HIST[z]) for z in HIST if pred[z][0] != HIST[z]]}
P.witness("E04_elements", "IUPAC 1978 placeholder names (transcribed)", json.dumps(HIST).encode(), m1)
print("elements:", m1)
# (b) alkanes C1..C8: generate names for every enumerated tree, then witness against textbook names
_, = [None]
names = {}
for n in range(1, 9):
    _, lv = F.alkane_skeletons(n)
    for adj in lv.values():
        names[N.name_alkane(adj)] = Chem.MolToSmiles(Chem.MolFromSmiles(F.tree_smiles(adj)))
P.seal("E04_alkanes", sorted(names), "IUPAC P-44 subset: longest chain, most substituents, lowest locants, alphabetical", reads=["E03 trees"])
TEXT = """methane ethane propane butane 2-methylpropane pentane 2-methylbutane 2,2-dimethylpropane
hexane 2-methylpentane 3-methylpentane 2,2-dimethylbutane 2,3-dimethylbutane
heptane 2-methylhexane 3-methylhexane 2,2-dimethylpentane 2,3-dimethylpentane 2,4-dimethylpentane 3,3-dimethylpentane 3-ethylpentane 2,2,3-trimethylbutane
octane 2-methylheptane 3-methylheptane 4-methylheptane 3-ethylhexane 2,2-dimethylhexane 2,3-dimethylhexane 2,4-dimethylhexane 2,5-dimethylhexane
3,3-dimethylhexane 3,4-dimethylhexane 3-ethyl-2-methylpentane 3-ethyl-3-methylpentane 2,2,3-trimethylpentane 2,2,4-trimethylpentane
2,3,3-trimethylpentane 2,3,4-trimethylpentane 2,2,3,3-tetramethylbutane""".split()
ours, txt = set(names), set(TEXT)
# inverse grammar: parse every textbook name -> structure -> must equal the structure we named
parse_ok = 0; parse_bad = []
for t in TEXT:
    try:
        adj = N.parse_alkane(t)
        s = Chem.MolToSmiles(Chem.MolFromSmiles(F.tree_smiles(adj)))
        if names.get(t) == s: parse_ok += 1
        else: parse_bad.append((t, s, names.get(t)))
    except Exception as e:
        parse_bad.append((t, str(e)))
refusals = {}
for bad in ["2-ethylpentane", "1-methylbutane", "2,2,2-trimethylpropane", "3-methylfooane", "2,3-dimethylpentane"]:
    try:
        canon = N.name_alkane(N.parse_alkane(bad))
        refusals[bad] = "admissible, normal form" if canon == bad else f"admissible but not normal form -> {canon}"
    except Exception as e: refusals[bad] = str(e)
m2 = {"generated": len(ours), "textbook": len(txt), "exact_set_match": ours == txt, "only_ours": sorted(ours - txt), "only_textbook": sorted(txt - ours),
      "parse_roundtrip": f"{parse_ok}/{len(TEXT)}", "parse_failures": parse_bad, "refusal_probe": refusals}
P.witness("E04_alkanes", "textbook IUPAC names C1-C8 (transcribed)", json.dumps(TEXT).encode(), m2)
print("alkanes:", json.dumps(m2, indent=0))
json.dump({"elements": m1, "alkanes": m2, "morpheme_origins": N.ORIGIN}, open("results/e04.json", "w"), indent=1)
