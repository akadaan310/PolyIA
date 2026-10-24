"""Timeless Rasm-State / Q-String reference prototype v0.1.

Toy formal model based on Arabic Timeless code. No semantic inference from dots.
No phonon/physical quantum mechanics. No tajwid recitation engine.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import log2, factorial
from typing import Iterable
import hashlib, json, unicodedata

HIJAI = tuple('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
CLASS_MEDIAL = {
    'ٮ': 'بتثني', 'ح': 'جحخ', 'د': 'دذ', 'ر': 'رز', 'س': 'سش',
    'ص': 'صض', 'ط': 'طظ', 'ع': 'عغ', 'ٯ': 'فق',
    'ا':'ا', 'ك':'ك', 'ل':'ل', 'م':'م', 'ه':'ه', 'و':'و'
}
CLASS_FINAL = {**CLASS_MEDIAL, 'ٮ': 'بتث', 'ں':'ن', 'ى':'ي'}
CLOSED = frozenset('ادذرزو')
# 17 classical positions/5 zones; missing hamza in source 28-letter model is explicit.
POINTS = ('jawf','halq','halq','halq', 'lisan','lisan','lisan','lisan','lisan',
          'lisan','lisan','lisan','lisan','lisan','shafatan','shafatan','khayshum')
POINT = {
    'ا':0,'ه':1,'ع':2,'ح':2,'غ':3,'خ':3, 'ق':4,'ك':5,
    'ج':6,'ش':6,'ي':6,'ض':7,'ل':8,'ن':9,'ر':10,
    'ط':11,'د':11,'ت':11,'ص':12,'ز':12,'س':12,'ظ':13,'ذ':13,'ث':13,
    'ف':14,'ب':15,'م':15,'و':15
}
# Traditional sifa inventory used as FEATURES, not a contemporary acoustic measurement.
HAMS = frozenset('فحثهشخصسكت')
SHIDDAH = frozenset('ءأجدقطبكت') - {'أ'}
JAHR = frozenset(HIJAI) | {'ء'}
JAHR -= HAMS
QALQALA = frozenset('قطبجد')
# This is deliberately a small attested-seed example, not a lexical ontology.
ATTESTED_SEED = {'كتب': {'root':'كتب','gloss':'write; inscribe'},
                 'كتم': {'root':'كتم','gloss':'conceal; suppress'},
                 'كبت': {'root':'كبت','gloss':'suppress; repress'},
                 'كتبة': {'root':'كتب','gloss':'scribes (plural noun)'},
                 'كتاب': {'root':'كتب','gloss':'book'},
                 'مكتوب': {'root':'كتب','gloss':'written'} }

def positions(letters:str)->tuple[str,...]:
    ps=[]
    for i,c in enumerate(letters):
        back=i>0 and letters[i-1] not in CLOSED
        front=i<len(letters)-1 and c not in CLOSED
        ps.append('medial' if back and front else 'final' if back else 'initial' if front else 'isolated')
    return tuple(ps)

def skeleton(letters:str)->str:
    if not all(ch in HIJAI for ch in letters):
        raise ValueError('This minimal 28-letter model requires plain source-base letters; keep variants separately.')
    out=[]
    for c,p in zip(letters,positions(letters)):
        table = CLASS_FINAL if p in ('final','isolated') else CLASS_MEDIAL
        matches=[glyph for glyph,group in table.items() if c in group]
        if len(matches)!=1:raise ValueError(f'ambiguous inventory entry {c}: {matches}')
        out.append(matches[0])
    return ''.join(out)

def domains(letters:str)->tuple[str,...]:
    out=[]
    for c,p in zip(letters,positions(letters)):
        table=CLASS_FINAL if p in ('final','isolated') else CLASS_MEDIAL
        out.append(next(group for group in table.values() if c in group))
    return tuple(out)

def candidates(letters:str,limit:int=100_000)->list[str]:
    ds=domains(letters)
    if degree(letters)>limit:raise ValueError('Enumeration exceeds explicit limit; use symbolic product')
    return [''.join(xs) for xs in product(*ds)]

def degree(letters:str)->int:
    a=1
    for d in domains(letters):a*=len(d)
    return a

def hartley(letters:str)->float:
    return log2(degree(letters))

def partition_order(table:dict[str,str])->int:
    result=1
    for c in table.values():result*=factorial(len(c))
    return result

def classical_features(letter:str)->dict:
    if letter not in HIJAI and letter!='ء':raise ValueError('unknown letter')
    result={'jahr':letter in JAHR, 'hams':letter in HAMS,
            'shiddah':letter in SHIDDAH, 'qalqala_inventory':letter in QALQALA}
    if letter in POINT:
        result['articulation_point']=POINT[letter]
        result['articulation_zone']=POINTS[POINT[letter]]
    elif letter == 'ء':
        result['articulation_point']='deep-throat (hamza; not in 28-letter prototype)'
        result['articulation_zone']='halq'
    return result

def phonetic_relation(a:str,b:str)->dict:
    af,bf=classical_features(a),classical_features(b)
    return {'a':a,'b':b,'same_zone':af['articulation_zone']==bf['articulation_zone'],
            'same_point':af['articulation_point']==bf['articulation_point'],
            'contrasts':{k:[af[k],bf[k]] for k in ('jahr','hams','shiddah','qalqala_inventory') if af[k]!=bf[k]}}

def dotted_related(a:str,b:str)->bool:
    return len(a)==len(b) and skeleton(a)==skeleton(b)

def lattice_meet(a:list[set[str]],b:list[set[str]])->list[set[str]]:
    """Meet in the COMPLETE constraint lattice; empty component yields bottom (contradiction)."""
    if len(a)!=len(b):raise ValueError('incompatible slots')
    return [x&y for x,y in zip(a,b)]

def lattice_join(a:list[set[str]],b:list[set[str]])->list[set[str]]:
    if len(a)!=len(b):raise ValueError('incompatible slots')
    return [x|y for x,y in zip(a,b)]

def entropy(probabilities:Iterable[float])->float:
    p=list(probabilities)
    if not p or any(x<0 for x in p) or abs(sum(p)-1)>1e-8:
        raise ValueError('probabilities must be nonnegative and sum to 1')
    return -sum(x*log2(x) for x in p if x)

@dataclass(frozen=True)
class QuantumString:
    source:str
    target:str
    relation:str
    grammar:str
    chart:str
    evidence_status:str
    source_reference:str
    version:int=1
    def serialize(self)->str:
        return json.dumps(self.__dict__,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    def address(self)->str:
        return 'qstr:v1:'+hashlib.sha256(self.serialize().encode('utf-8')).hexdigest()
    def executable(self)->bool:
        return self.evidence_status=='verified' and bool(self.source_reference)


def word_report(letters:str)->dict:
    if letters not in ATTESTED_SEED:kind='unattested-in-seed'
    else:kind='attested-seed'
    return {'surface':letters,'source_status':kind,'rasm':skeleton(letters),
            'position':positions(letters),'domains':domains(letters),
            'orthographic_degree':degree(letters),'hartley_bits':hartley(letters),
            'candidate_spellings':candidates(letters),
            'lexical_seed_candidates':[w for w in candidates(letters) if w in ATTESTED_SEED]}
