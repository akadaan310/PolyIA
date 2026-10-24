"""Typed computational corpus envelopes and cross-domain bridge admission.

Proof of structure, not proof of natural-language/physical correctness.
"""
from dataclasses import dataclass, asdict
from typing import Any
from .core import digest, Rejection

@dataclass(frozen=True)
class CorpusContract:
    domain: str
    version: str
    grammar: tuple[str,...]
    license: str
    source: str
    object_type: str

class CorpusForge:
    def __init__(self):
        self.contracts:dict[str,CorpusContract]={}
        self.objects:dict[str,dict[str,Any]]={}
        self.by_domain:dict[str,set[str]]={}
        self.bridges:dict[tuple[str,str],dict[str,str]]={}

    def register(self,c:CorpusContract):
        if not all(isinstance(x,str) and x.strip() for x in (c.domain,c.version,c.license,c.source,c.object_type)):
            raise Rejection('contract fields cannot be empty')
        if not c.grammar or len(set(c.grammar))!=len(c.grammar) or any(not x.strip() for x in c.grammar):
            raise Rejection('grammar must be declared before any ingestion')
        if c.domain in self.contracts:
            raise Rejection('immutable domain contract: version using a new domain ID')
        self.contracts[c.domain]=c;self.by_domain[c.domain]=set()

    def ingest(self,domain:str,record:dict[str,Any]):
        c=self.contracts.get(domain)
        if c is None:raise Rejection('no grammar/contract: cannot ingest')
        if set(record)!=set(c.grammar):
            raise Rejection('negative grammar: record violates declared exact keys')
        if any(not isinstance(record[k],str) or not record[k].strip() for k in c.grammar):
            raise Rejection('record fields must be nonempty strings')
        obj={'contract':asdict(c),'record':record}
        cid='sha256:'+digest('TRE/CORPUS/OBJECT/0.1',obj)
        if cid not in self.objects:self.objects[cid]=obj
        self.by_domain[domain].add(cid)
        return cid

    def declare_bridge(self,src:str,dst:str, mapping:dict[str,str]):
        if src not in self.contracts or dst not in self.contracts:
            raise Rejection('bridge requires two registered source contracts')
        if not mapping or not set(mapping)<=set(self.contracts[src].grammar):
            raise Rejection('bridge source keys not in grammar')
        if any(v not in self.contracts[dst].grammar for v in mapping.values()) or len(set(mapping.values()))!=len(mapping):
            raise Rejection('bridge destination mismatch / many-to-one unadmitted')
        self.bridges[(src,dst)]=dict(mapping)

    def bridge(self,cid:str,dst:str):
        if cid not in self.objects:raise Rejection('source not present')
        src=self.objects[cid]['contract']['domain']
        mapping=self.bridges.get((src,dst))
        if not mapping:raise Rejection('no admitted bridge')
        record=self.objects[cid]['record']
        translated={dst_k:record[src_k] for src_k,dst_k in mapping.items()}
        missing=set(self.contracts[dst].grammar)-set(translated)
        if missing:raise Rejection('partial bridge: target requires additional fields')
        return self.ingest(dst,translated)

    def manifest(self)->dict[str,Any]:
        return {'contracts':{k:asdict(v) for k,v in sorted(self.contracts.items())},
                'object_count':len(self.objects),
                'scoped_counts':{k:len(v) for k,v in sorted(self.by_domain.items())},
                'bridge_count':len(self.bridges)}
