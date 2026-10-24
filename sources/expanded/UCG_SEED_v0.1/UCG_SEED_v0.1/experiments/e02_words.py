"""E02  Predict molecular words over {C,N,O,F}+H blind; witness against QM9 (GDB-9 subset).
Generator reads: E01 valences only.  Witness: G4MP2/QM9 SMILES (globus-labs)."""
import sys, os, json, gzip, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from ucg import proleptic as P
from ucg.molgrammar import enumerate_words, features
from rdkit import Chem
K = 4
pred = enumerate_words(max_heavy=K)
P.seal("E02_words", sorted(pred), f"valence-admissible connected multigraphs, heavy<={K}", reads=["ucg.elements.valences"])
print("predicted words:", len(pred), collections.Counter(v["heavy"] for v in pred.values()))
# ---- witness
if os.path.exists("data/g4mp2.json.gz"):
    raw = gzip.open("data/g4mp2.json.gz", "rb").read()
    recs = [json.loads(l) for l in raw.decode().splitlines()]
else:  # shipped witness subset (exact rows with <= 4 heavy atoms; full-file hash in data/WITNESS_SOURCES.json)
    raw = open("data/qm9_le4_subset.json", "rb").read()
    recs = json.loads(raw)
wit = {}
for d in recs:
    if d["n_heavy_atoms"] <= K:
        m = Chem.MolFromSmiles(d["smiles_0"])
        if m: wit[Chem.MolToSmiles(m)] = d["n_heavy_atoms"]
P_, W = set(pred), set(wit)
hit = P_ & W
m = {"predicted": len(P_), "witnessed": len(W), "both": len(hit), "recall": len(hit) / len(W), "precision": len(hit) / len(P_),
     "by_heavy": {k: {"pred": sum(1 for s in P_ if pred[s]["heavy"] == k), "wit": sum(1 for s in W if wit[s] == k), "both": sum(1 for s in hit if pred[s]["heavy"] == k)} for k in range(1, K + 1)},
     "gaps(witnessed,not predicted)": sorted(W - P_)[:30]}
# mine the in-grammar: motifs over-represented in predicted-but-unwitnessed
miss = P_ - W
fm, fh = collections.Counter(), collections.Counter()
for s in miss: fm.update(features(s)["motifs"])
for s in hit: fh.update(features(s)["motifs"])
ing = []
for f, c in fm.most_common():
    h = fh.get(f, 0)
    ing.append({"motif": f, "in_unwitnessed": c, "in_witnessed": h, "refusal_rate": round(c / (c + h), 3)})
m["mined_ingrammar"] = [x for x in ing if x["in_witnessed"] == 0 and x["in_unwitnessed"] >= 3]  # strict: never witnessed

print(json.dumps({k: v for k, v in m.items() if k != "mined_ingrammar"}, indent=0)[:1500])
print("mined in-grammar:"); [print("  ", x) for x in m["mined_ingrammar"]]
# re-test: grammar + mined in-grammar
bad = {x["motif"] for x in m["mined_ingrammar"]}
P2 = {s for s in P_ if not (set(features(s)["motifs"]) & bad)}
m["with_ingrammar"] = {"predicted": len(P2), "recall": len(P2 & W) / len(W), "precision": len(P2 & W) / len(P2)}
print("grammar x in-grammar:", m["with_ingrammar"])
# second witness: textbook-attested small neutral closed-shell molecules ([K] general chemistry)
TEXTBOOK = {"water": "O", "hydrogen peroxide": "OO", "ammonia": "N", "hydrazine": "NN", "methane": "C", "carbon dioxide": "O=C=O",
            "hydrogen cyanide": "C#N", "formaldehyde": "C=O", "methanol": "CO", "acetylene": "C#C", "ethylene": "C=C", "fluorine": "FF",
            "oxygen difluoride": "FOF", "nitrogen trifluoride": "FN(F)F", "nitrogen": "N#N", "oxygen (singlet form drawn)": "O=O",
            "hydroxylamine": "NO", "diazene": "N=N", "cyclopropane": "C1CC1", "ethylene oxide": "C1CO1", "ketene": "C=C=O",
            "formic acid": "O=CO", "urea": "NC(N)=O", "carbon tetrafluoride": "FC(F)(F)F", "acetonitrile": "CC#N"}
tb = {k: Chem.MolToSmiles(Chem.MolFromSmiles(v)) for k, v in TEXTBOOK.items()}
tb_hit = {k: s in P_ for k, s in tb.items()}
tb_qm9 = {k: s in W for k, s in tb.items()}
tb_ing = {k: (s in P2) for k, s in tb.items()}
m["textbook_witness"] = {"n": len(tb), "predicted_by_grammar": sum(tb_hit.values()), "in_QM9": sum(tb_qm9.values()),
    "kept_after_QM9_ingrammar": sum(tb_ing.values()),
    "real_but_refused_by_QM9_ingrammar": sorted(k for k in tb if tb_hit[k] and not tb_ing[k]),
    "not_predicted": sorted(k for k in tb if not tb_hit[k])}
print("textbook witness:", m["textbook_witness"])
P.witness("E02_words", "QM9 SMILES (globus-labs g4mp2) + textbook list", raw + json.dumps(TEXTBOOK, sort_keys=True).encode(), {k: v for k, v in m.items() if k != "gaps(witnessed,not predicted)"})
json.dump(m, open("results/e02.json", "w"), indent=1)
