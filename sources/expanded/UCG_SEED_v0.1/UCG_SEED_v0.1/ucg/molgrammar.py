"""Covalent word grammar: a word is a connected bond-multigraph on heavy letters whose
bond-order sum at each letter is an admissible valence (E01), hydrogens fill the rest.

This is the GDB idea (Fink & Reymond 2005-2007; Ruddigkeit et al. 2012 [K]) rebuilt
minimally: enumerate graphs, keep the valence-admissible ones.  Canonicalisation uses
RDKit only as a *normaliser* of the written form (declared); the grammar itself is here.
"""
from __future__ import annotations
import itertools
from rdkit import Chem
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")
from . import elements as E

SYM = {6: "C", 7: "N", 8: "O", 9: "F"}


def enumerate_words(letters=(6, 7, 8, 9), max_heavy=4, primary_only=True):
    out = {}
    for n in range(1, max_heavy + 1):
        pairs = list(itertools.combinations(range(n), 2))
        for atoms in itertools.combinations_with_replacement(letters, n):
            vmax = [E.valences(z)[0] if primary_only else max(E.valences(z)) for z in atoms]
            for orders in itertools.product(range(4), repeat=len(pairs)):
                deg = [0] * n
                adj = [[] for _ in range(n)]
                for (i, j), o in zip(pairs, orders):
                    if o:
                        deg[i] += o; deg[j] += o; adj[i].append(j); adj[j].append(i)
                if any(d > v for d, v in zip(deg, vmax)):
                    continue
                # connected?
                seen, st = {0}, [0]
                while st:
                    u = st.pop()
                    for w in adj[u]:
                        if w not in seen:
                            seen.add(w); st.append(w)
                if len(seen) != n:
                    continue
                rw = Chem.RWMol()
                for z in atoms:
                    a = Chem.Atom(z); a.SetNoImplicit(False); rw.AddAtom(a)
                bt = {1: Chem.BondType.SINGLE, 2: Chem.BondType.DOUBLE, 3: Chem.BondType.TRIPLE}
                for (i, j), o in zip(pairs, orders):
                    if o:
                        rw.AddBond(i, j, bt[o])
                try:
                    m = rw.GetMol(); Chem.SanitizeMol(m)
                    smi = Chem.MolToSmiles(m)
                except Exception:
                    continue
                out[smi] = {"heavy": n, "letters": "".join(SYM[z] for z in atoms),
                            "bonds": [(i, j, o) for (i, j), o in zip(pairs, orders) if o]}
    return out


def features(smi: str) -> dict:
    """Structural motifs used to mine the in-grammar (what the witness refuses)."""
    m = Chem.MolFromSmiles(smi)
    f = set()
    ri = m.GetRingInfo()
    for r in ri.AtomRings():
        f.add(f"ring{len(r)}")
    for b in m.GetBonds():
        a, c = sorted([b.GetBeginAtom().GetSymbol(), b.GetEndAtom().GetSymbol()])
        o = {1.0: "-", 2.0: "=", 3.0: "#", 1.5: ":"}[b.GetBondTypeAsDouble()]
        if a != "C" or c != "C":
            f.add(f"{a}{o}{c}")
        if o in "=#" and b.IsInRing():
            f.add(f"ring{o}")
    for a in m.GetAtoms():
        bo = sorted(b.GetBondTypeAsDouble() for b in a.GetBonds())
        if bo.count(2.0) >= 2:
            f.add("cumulene(=X=)")
        if 3.0 in bo and a.IsInRing():
            f.add("ring-triple")
    return {"motifs": sorted(f)}
