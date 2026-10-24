"""PHONEX/0.1 offline reference: indexed, prefix-only phonetic *candidate* discovery.
All fixture pronunciations are invented for testing, NOT linguistic attestations.
No network, native external dependencies, or etymology inference.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from typing import Any
import hashlib
import json
import math

@dataclass(frozen=True)
class Form:
    id: str
    language: str
    script: str
    surface: str
    segments: tuple[str, ...]
    gloss: str
    pronunciation_status: str = "illustrative_only"
    semantic_status: str = "illustrative_only"
    source: str = "TEST_FIXTURE_NOT_ATTESTED"
    dialect: str = "unspecified"
    version: str = "toy-v1"

    def canonical(self) -> dict[str, Any]:
        return {"id": self.id, "language": self.language, "script": self.script,
                "surface": self.surface, "segments": list(self.segments),
                "gloss": self.gloss, "pronunciation_status": self.pronunciation_status,
                "semantic_status": self.semantic_status, "source": self.source,
                "dialect": self.dialect, "version": self.version}

# A deliberately small, model-defined feature table for TESTING, not IPA's full inventory.
# Format: place, manner, voice, secondary articulation, vowel-kind.
FEAT: dict[str, tuple[str, str, str, str, str]] = {
    "t": ("alveolar","stop","-","plain","C"),
    "tˤ": ("alveolar","stop","-","emphatic","C"),
    "d": ("alveolar","stop","+","plain","C"),
    "p": ("bilabial","stop","-","plain","C"),
    "b": ("bilabial","stop","+","plain","C"),
    "m": ("bilabial","nasal","+","plain","C"),
    "l": ("alveolar","lateral","+","plain","C"),
    "ɹ": ("postalveolar","approximant","+","plain","C"),
    "ʒ": ("postalveolar","fricative","+","plain","C"),
    "d͡ʒ": ("postalveolar","affricate","+","plain","C"),
    "f": ("labiodental","fricative","-","plain","C"),
    "ɡ": ("velar","stop","+","plain","C"),
    "j": ("palatal","approximant","+","plain","C"),
    "a": ("open","vowel","+","plain","V"),
    "i": ("close-front","vowel","+","plain","V"),
    "u": ("close-back","vowel","+","plain","V"),
    "uː": ("close-back-long","vowel","+","plain","V"),
    "o": ("mid-back","vowel","+","plain","V"),
    "ɔ": ("open-mid-back","vowel","+","plain","V"),
    "ɒ": ("open-back","vowel","+","plain","V"),
    "ə": ("central","vowel","+","plain","V"),
}
WEIGHTS=(0.38, 0.24, 0.15, 0.18, 0.05)

def segment_distance(a: str, b: str) -> float:
    if a == b:
        return 0.0
    if a not in FEAT or b not in FEAT:
        return 1.0
    return sum(w for x, y, w in zip(FEAT[a], FEAT[b], WEIGHTS) if x != y)


def phonetic_prefix_distance(query: tuple[str, ...], candidate: tuple[str, ...],
                             max_suffix_slack: int=2, min_coverage: float=0.8) -> tuple[float,int] | None:
    """Align the ENTIRE query against an INITIAL candidate prefix. No arbitrary substring hits.
    End index j in candidate may vary to accommodate insertions/deletions.
    Simple O(len(query) * min(len(candidate),len(query)+slack)) dynamic programming.
    """
    if not query or not candidate:
        return None
    m=len(query)
    limit=min(len(candidate), m + max_suffix_slack)
    prev=[float(j) for j in range(limit+1)]
    for i,a in enumerate(query, start=1):
        cur=[float(i)] + [0.0]*limit
        for j in range(1,limit+1):
            b=candidate[j-1]
            cur[j]=min(prev[j]+1.0,cur[j-1]+1.0,prev[j-1]+segment_distance(a,b))
        prev=cur
    left=max(1, math.ceil(m*min_coverage))
    if left>limit:
        return None
    cost,end=min((prev[j],j) for j in range(left,limit+1))
    return (round(cost/max(m,end),6),end)


def first_family(sound:str)->str:
    feat=FEAT.get(sound)
    return f"{feat[0]}:{feat[1]}:{feat[4]}" if feat else f"unmapped:{sound}"

class Atlas:
    def __init__(self, records:list[Form]):
        self.forms={f.id:f for f in records}
        if len(self.forms)!=len(records):
            raise ValueError('IDs must be unique')
        self.first=defaultdict(list)
        self.prefix=defaultdict(list)
        for f in records:
            if not f.segments:
                raise ValueError('empty segments: '+f.id)
            self.first[first_family(f.segments[0])].append(f.id)
            for n in range(1, min(len(f.segments),4)+1):
                self.prefix[f.segments[:n]].append(f.id)

    def match(self, query:tuple[str,...], limit:int=12, budget:float=0.42,
              near_first:bool=True)->dict[str,Any]:
        if not query:
            raise ValueError('nonempty query required')
        # No single index can guarantee finding all phonetic-near candidates.
        # This deliberately bounded first-segment candidate generator is documented as incomplete.
        ids=set(self.first[first_family(query[0])])
        if near_first:
            for sound in FEAT:
                if segment_distance(query[0],sound)<=0.19:
                    ids.update(self.first[first_family(sound)])
        rows=[]
        for id in sorted(ids):
            f=self.forms[id]
            p=phonetic_prefix_distance(query,f.segments)
            if p is None or p[0]>budget:
                continue
            score,end=p
            rows.append({"id":f.id,"surface":f.surface,"language":f.language,
                         "matched_prefix":" ".join(f.segments[:end]),
                         "distance":score,"gloss":f.gloss,"evidence":f.pronunciation_status,
                         "status":"PHONETIC_CANDIDATE_ONLY", "source":f.source})
        rows.sort(key=lambda x:(x['distance'],x['language'],x['id']))
        return {"query_segments":list(query),"matches":rows[:limit],
                "candidate_pool_size":len(ids),"algorithm":"bounded_first_segment_plus_weighted_prefix_DP",
                "completeness":"INCOMPLETE_APPROXIMATE_CANDIDATE_GENERATOR",
                "historical_inference":False, "semantic_inference":False}


def qstring_id(record:dict[str,Any])->str:
    raw=json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
    return 'qstr:v1:'+hashlib.sha256(raw).hexdigest()


def forms_from_jsonl(path:str)->list[Form]:
    arr=[]
    with open(path,encoding='utf8') as fh:
        for line in fh:
            if line.strip():
                data=json.loads(line)
                data['segments']=tuple(data['segments'])
                arr.append(Form(**data))
    return arr


def sample()->list[Form]:
    return [
        Form('eng-topology','eng','Latn','topology',('t','ə','p','ɒ','l','ə','d͡ʒ','i'),'topology'),
        Form('arb-topologia-ta','arb','Arab','طوبولوجيا',('tˤ','u','b','u','l','u','d͡ʒ','i','j','a'),'topology'),
        Form('arb-topologia-t','arb','Arab','توبولوجيا',('t','u','b','u','l','u','d͡ʒ','i','j','a'),'topology'),
        Form('fra-topologie','fra','Latn','topologie',('t','ɔ','p','ɔ','l','ɔ','ʒ','i'),'topology'),
        Form('eng-topography','eng','Latn','topography',('t','ə','p','ɒ','ɡ','ɹ','ə','f','i'),'topography'),
        Form('eng-prototype','eng','Latn','prototype',('p','ɹ','o','t','o','t','i','p'),'prototype'),
        Form('toy-homophone','zzz','Latn','tapa',('t','ə','p','ɒ'),'unrelated hypothetical meaning'),
    ]

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='PHONEX reference: toy phonetic prefix matcher; NOT an attested corpus')
    p.add_argument('command',choices=['demo','match'])
    p.add_argument('--segments',default='t ə p ɒ l',help='space-separated IPA segments, e.g. "t ə p ɒ l"')
    p.add_argument('--jsonl',help='user-supplied JSONL with Form fields')
    p.add_argument('--budget',type=float,default=0.42)
    args=p.parse_args()
    corpus=forms_from_jsonl(args.jsonl) if args.jsonl else sample()
    atlas=Atlas(corpus)
    print(json.dumps({"warning":"Sample data are illustrative, not linguistic attestations", 
                      "result":atlas.match(tuple(args.segments.split()),budget=args.budget)},
                     ensure_ascii=False,indent=2))
