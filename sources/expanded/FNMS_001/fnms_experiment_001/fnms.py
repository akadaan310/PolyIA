"""Substrate University / Division IX -- FNMS experiment 001.
No changes to the University repository. This finite, proof-carrying
model separates expression, therapeutic indication, asserted product identity,
and chemical structure. It does not infer pharmacology from spelling.
Dependencies: Python 3.10+, RDKit (for structural tests).
Sources:
- https://pubchem.ncbi.nlm.nih.gov/compound/1983
- https://www.fda.gov/drugs/safe-use-over-counter-pain-relievers-and-fever-reducers/acetaminophen
- https://www.dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6dea9e11-ff99-63c7-e053-2a91aa0a5b54
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import deque
from typing import Literal
import json
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Descriptors

SMILES = 'CC(=O)NC1=CC=C(C=C1)O'
PUBCHEM = 'https://pubchem.ncbi.nlm.nih.gov/compound/1983'
FDA = 'https://www.fda.gov/drugs/safe-use-over-counter-pain-relievers-and-fever-reducers/acetaminophen'
MOCK = 'user-stipulated hypothetical single-active-ingredient product'
Type = Literal['surface','lexeme','gloss','intent','effect','drug','chemical_name','structure','component','polarity']

@dataclass(frozen=True)
class Node:
    id: str
    type: Type
    description: str

@dataclass(frozen=True)
class Edge:
    source: str
    op: str
    target: str
    status: str
    evidence: str

@dataclass
class Graph:
    nodes: dict[str,Node]
    edges: list[Edge]

    def edge(self, src: str, op: str, dst: str, status: str, evidence: str):
        assert src in self.nodes and dst in self.nodes, 'undefined endpoint'
        assert op in ADMISSIBLE and (self.nodes[src].type,self.nodes[dst].type) in ADMISSIBLE[op], f'ill-typed {op}'
        self.edges.append(Edge(src,op,dst,status,evidence))

    def walk(self, src: str, dst: str, admitted_ops: frozenset[str]):
        """Find shortest typed witness path. Each edge has an evidence label."""
        q=deque([(src,[])]); seen={src}
        while q:
            at,path=q.popleft()
            if at==dst: return path
            for e in self.edges:
                if e.source==at and e.op in admitted_ops and e.target not in seen:
                    seen.add(e.target); q.append((e.target,path+[e]))
        return None

    def targets(self, src: str, op: str):
        return sorted(e.target for e in self.edges if e.source==src and e.op==op)

ADMISSIBLE = {
 'parses_to': {('surface','lexeme')},
 'translated_as': {('lexeme','gloss'),('surface','gloss')},
 'expresses': {('surface','intent'),('gloss','intent')},
 'targets_effect': {('intent','effect')},
 'supported_by': {('effect','drug')},
 'asserted_active': {('surface','drug')},
 'also_named': {('drug','chemical_name')},
 'denotes_structure': {('chemical_name','structure')},
 'has_component': {('structure','component')},
 'has_polarity': {('intent','polarity')},
}

def build_graph():
    entries=[
     ('brand','surface','Head Pain Reliever (hypothetical brand)'),
     ('head','lexeme','English head; place/anatomical site'),
     ('pain','lexeme','English pain; undesirable state'),
     ('reliever','lexeme','English reliever; intended agent or function'),
     ('latin_head','gloss','caput, gen. capitis (Latin head)'),
     ('latin_pain','gloss','dolor, gen. doloris (Latin pain)'),
     ('latin_relief','gloss','levamen / levare (Latin relief / to alleviate)'),
     ('latin_phrase','gloss','remedium doloris capitis (constructed Latin descriptive gloss)'),
     ('greek_headache','gloss','cephalalgia (Latinized Greek headache, NOT classical Latin roots)'),
     ('intention','intent','reduce pain located at the head'),
     ('negative_intention','intent','increase pain located at the head'),
     ('analgesia','effect','analgesic treatment of headache'),
     ('acetaminophen','drug','generic active substance acetaminophen'),
     ('ibuprofen','drug','generic active substance ibuprofen'),
     ('naproxen','drug','generic active substance naproxen'),
     ('iupac','chemical_name','N-(4-hydroxyphenyl)acetamide'),
     ('apan','chemical_name','N-acetyl-p-aminophenol, historical structural synonym'),
     ('paracetamol','chemical_name','paracetamol, INN / geographic synonym'),
     ('structure','structure','CC(=O)NC1=CC=C(C=C1)O'),
     ('phenol','component','phenol: ring-bound OH'),
     ('amide','component','secondary acetamide: CH3-C(=O)-NH-Ar'),
     ('benzene','component','six-membered aromatic carbon ring'),
     ('para','component','1,4 positions on ring, 3 ring bonds apart'),
     ('relief','polarity','negative change in pain magnitude'),
     ('aggravation','polarity','positive change in pain magnitude'),
    ]
    g=Graph({k:Node(k,t,d) for k,t,d in entries},[])
    for part in ('head','pain','reliever'):
        g.edge('brand','parses_to',part,'constructed','English compound morphology')
    for src,dst in [('head','latin_head'),('pain','latin_pain'),('reliever','latin_relief')]:
        g.edge(src,'translated_as',dst,'known','Latin dictionary equivalents; not drug names')
    g.edge('brand','translated_as','latin_phrase','constructed','grammatical gloss; not an attested brand name')
    g.edge('brand','translated_as','greek_headache','partial','head pain only; reliever function absent')
    g.edge('brand','expresses','intention','constructed','composition of head + pain + reliever')
    g.edge('latin_phrase','expresses','intention','constructed','translation preserves the intended use')
    g.edge('intention','targets_effect','analgesia','constructed','headache relief is the target')
    for drug,proof in [('acetaminophen',FDA),('ibuprofen',FDA),('naproxen',FDA)]:
        g.edge('analgesia','supported_by',drug,'external-source',proof)
    g.edge('brand','asserted_active','acetaminophen','stipulated',MOCK)
    for name in ('iupac','apan','paracetamol'):
        g.edge('acetaminophen','also_named',name,'external-source',PUBCHEM)
    g.edge('iupac','denotes_structure','structure','external-source',PUBCHEM)
    for part in ('phenol','amide','benzene','para'):
        g.edge('structure','has_component',part,'computed','RDKit graph analysis / established structural descriptors')
    g.edge('intention','has_polarity','relief','constructed','decrease pain intensity relative to baseline')
    g.edge('negative_intention','has_polarity','aggravation','constructed','increase pain intensity relative to baseline')
    return g

def inspect_molecule(smiles=SMILES):
    m=Chem.MolFromSmiles(smiles)
    if m is None: raise ValueError('invalid SMILES')
    aromatic_rings=[tuple(r) for r in m.GetRingInfo().AtomRings() if len(r)==6 and all(m.GetAtomWithIdx(i).GetIsAromatic() for i in r)]
    phenolic=Chem.MolFromSmarts('[c]-[OX2H]')
    amide=Chem.MolFromSmarts('[NX3][CX3](=[OX1])[#6]')
    phenol_hits=m.GetSubstructMatches(phenolic)
    amide_hits=m.GetSubstructMatches(amide)
    # Substituents attach at ring carbon bonded to OH oxygen and ring carbon bonded to amide nitrogen.
    rings=[]
    for ring in aromatic_rings:
        oxy_sites=[]; amide_sites=[]
        for ix in ring:
            a=m.GetAtomWithIdx(ix)
            for n in a.GetNeighbors():
                if n.GetIdx() in ring: continue
                if n.GetSymbol()=='O' and n.GetTotalNumHs()>0: oxy_sites.append(ix)
                if n.GetSymbol()=='N' and any(n.GetIdx()==hit[0] for hit in amide_hits): amide_sites.append(ix)
        for a in oxy_sites:
            for b in amide_sites:
                length=len(Chem.GetShortestPath(m,a,b))-1
                rings.append({'ring_bonds_between_substituents':length,'relative_position':{1:'ortho',2:'meta',3:'para'}.get(length)})
    return {'formula':rdMolDescriptors.CalcMolFormula(m),
            'mass_g_mol':round(Descriptors.MolWt(m),3),
            'heavy_atoms':m.GetNumHeavyAtoms(),
            'phenol_matches':len(phenol_hits), 'amide_matches':len(amide_hits),
            'aromatic_six_rings':len(aromatic_rings), 'regiochemistry':rings}

def run():
    g=build_graph()
    semantic_path=g.walk('brand','acetaminophen',frozenset({'expresses','targets_effect','supported_by'}))
    asserted_path=g.walk('brand','acetaminophen',frozenset({'asserted_active'}))
    wrong_etym_path=g.walk('latin_phrase','iupac',frozenset({'translated_as','also_named','denotes_structure'}))
    by_intent=g.targets('analgesia','supported_by')
    structural=inspect_molecule()
    return {
      'experiment':'FNMS-001',
      'site_divisions_modified':False,
      'nodes':len(g.nodes),'typed_edges':len(g.edges),
      'normalized_intent':'reduce pain located at the head',
      'latin_constructed':'remedium doloris capitis',
      'greek_via_medical_latin':'cephalalgia (names headache, not the reliever)',
      'semantic_candidate_set':by_intent,
      'semantic_fiber_cardinality':len(by_intent),
      'unique_from_intent_alone':len(by_intent)==1,
      'semantic_witness':[asdict(e) for e in (semantic_path or [])],
      'asserted_identity_witness':[asdict(e) for e in (asserted_path or [])],
      'lexical_to_chemical_identity_without_evidence':wrong_etym_path is not None,
      'acetaminophen_synonyms':g.targets('acetaminophen','also_named'),
      'chemical_components':g.targets('structure','has_component'),
      'chemical_validation':structural,
      'opposition':{'reliever':'delta pain < 0','aggravator':'delta pain > 0',
                    'mutually_exclusive_under_same_baseline_observation':True},
      'non_antonyms':['para vs meta: constitutional isomer alternatives, not logical opposites',
                      'amide vs amine: different chemical classifications, not antonyms',
                      'head vs acetyl: differently typed, not lexical equivalents'],
    }

if __name__=='__main__': print(json.dumps(run(),indent=2,ensure_ascii=False))
