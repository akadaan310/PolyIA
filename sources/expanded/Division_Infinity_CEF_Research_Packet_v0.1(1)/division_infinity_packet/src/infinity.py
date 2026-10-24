"""Division ∞ — Calculus of Entangled Forms (house research prototype).

A tiny, deterministic, dependency-free implementation of *typed, directed,
multistrand incidence hypergraphs*, faithful text-to-bits mappings, and
explicit proof/status-aware forward reachability. Not a semantic oracle.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Iterable
import hashlib
import json
import re
import unicodedata

STATUSES = frozenset({'established','derived','stipulated','hypothesis','rejected'})


def utf8_bits(value: str) -> str:
    """Bitstring of the EXACT input's UTF-8 bytes, including spaces."""
    return ''.join(f'{byte:08b}' for byte in value.encode('utf-8'))


def bits_utf8(bits: str) -> str:
    if len(bits) % 8 or set(bits) - {'0','1'}:
        raise ValueError('UTF-8 bitstring requires 8-bit octets of 0s/1s')
    return bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8)).decode('utf-8')


def binary_record(value: str) -> dict[str,Any]:
    """UTF-8 exact encoding + code-point and whitespace-aware projections.

    The codepoints array is NOT a grapheme-cluster segmentation; a multi-codepoint
    displayed grapheme can appear as multiple entries. No normalization is hidden.
    """
    tokens = [{'text':m.group(0), 'start':m.start(), 'end':m.end(),
               'kind':'whitespace' if m.group(0).isspace() else 'nonwhitespace',
               'bits':utf8_bits(m.group(0))} for m in re.finditer(r'\s+|\S+',value)]
    codepoints = [{'char':c,'unicode':f'U+{ord(c):04X}',
                   'scalar_21_bits':f'{ord(c):021b}',
                   'utf8_bits':utf8_bits(c)} for c in value]
    bits = utf8_bits(value)
    assert bits == ''.join(item['utf8_bits'] for item in codepoints)
    assert bits == ''.join(item['bits'] for item in tokens)
    return {'surface':value,'text_units':'Unicode code points',
            'encoding':'UTF-8','normalization':'none','utf8_bits':bits,
            'octets':len(bits)//8,'codepoints':codepoints,'segments':tokens,
            'sha256_utf8':hashlib.sha256(value.encode('utf-8')).hexdigest(),
            'NFC':unicodedata.normalize('NFC',value),
            'NFC_changes_original':unicodedata.normalize('NFC',value)!=value}


def canonical_record_bits(data: Any) -> dict[str,str]:
    """Every JSON-serializable form gets a specified binary serialization."""
    s=json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return {'canonical_json':s,'utf8_bits':utf8_bits(s),'encoding':'JSON(sorted keys,compact)+UTF-8'}


@dataclass(frozen=True)
class Form:
    id: str
    sort: str
    value: str
    namespace: str
    context: str = ''
    epistemic: str = 'house'


@dataclass(frozen=True)
class Operator:
    name: str
    input_sorts: tuple[str,...]
    output_sorts: tuple[str,...]
    contract: str
    loss: str = 'not assessed'


@dataclass(frozen=True)
class Strand:
    operator: str
    status: str
    evidence: str
    context: str = ''

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError('unknown evidential status')
        if not self.evidence:
            raise ValueError('an entanglement strand needs evidence/stipulation identifier')


@dataclass(frozen=True)
class Entanglement:
    id: str
    inputs: tuple[str,...]
    outputs: tuple[str,...]
    strands: tuple[Strand,...]
    # The ordered input/output port tuples support arities other than 1→1.
    # Hyperedge incidence is the primitive; pairwise adjacency is a projection.


class RejectedBridge(ValueError):
    pass


class InfinityComplex:
    def __init__(self):
        self.forms:dict[str,Form]={}
        self.operators:dict[str,Operator]={}
        self.entanglements:dict[str,Entanglement]={}

    def add_form(self, form:Form):
        if form.id in self.forms:
            raise ValueError('duplicate form id')
        self.forms[form.id]=form

    def register(self, op:Operator):
        if op.name in self.operators:
            raise ValueError('duplicate operator')
        self.operators[op.name]=op

    def add_entanglement(self, ent:Entanglement):
        if ent.id in self.entanglements:
            raise RejectedBridge('duplicate entanglement id')
        if not ent.strands:
            raise RejectedBridge('unlabeled entanglement prohibited')
        try:
            inputs=tuple(self.forms[i].sort for i in ent.inputs)
            outputs=tuple(self.forms[i].sort for i in ent.outputs)
        except KeyError as e:
            raise RejectedBridge(f'unknown form {e}') from e
        if not ent.inputs and not ent.outputs:
            raise RejectedBridge('entanglement needs at least one port')
        for strand in ent.strands:
            if strand.operator not in self.operators:
                raise RejectedBridge(f'unknown operator {strand.operator}')
            op=self.operators[strand.operator]
            if (inputs,outputs)!=(op.input_sorts,op.output_sorts):
                raise RejectedBridge(f'{op.name}: expected {op.input_sorts}->{op.output_sorts}; got {inputs}->{outputs}')
        self.entanglements[ent.id]=ent

    def reachable(self, seeds:Iterable[str], allowed=frozenset({'established','derived'})):
        """Least fixed point. All input ports are required for a hyperedge to fire.

        IMPORTANT: 'reachable' is derivation over REGISTERED assertions, not
        real-world truth or arbitrary semantic reasoning.
        """
        have=set(seeds)
        if have-set(self.forms):
            raise KeyError(f'unknown seeds: {have-set(self.forms)}')
        witnesses:dict[str,list[str]]={x:[] for x in have}
        changed=True
        while changed:
            changed=False
            for ent in self.entanglements.values():
                if set(ent.inputs)<=have and any(s.status in allowed for s in ent.strands):
                    for dest in ent.outputs:
                        if dest not in have:
                            have.add(dest)
                            witnesses[dest]=list(ent.inputs)+[ent.id]
                            changed=True
        return have,witnesses

    def fiber(self, op_name:str, target_id:str, allowed=frozenset({'established','derived'})):
        """Registered immediate source TUPLES for target; not a global inverse."""
        return [e.inputs for e in self.entanglements.values()
                if target_id in e.outputs and any(s.operator==op_name and s.status in allowed for s in e.strands)]

    def reify_entanglement(self, ent_id:str, form_id:str|None=None)->Form:
        """Promote a hyperedge to a typed form for higher-order relations."""
        ent=self.entanglements[ent_id]
        f=Form(form_id or f'edge:{ent_id}', 'Entanglement',
               json.dumps(asdict(ent),sort_keys=True,ensure_ascii=False),
               'meta/incidence', context='CEFC/0.1')
        self.add_form(f)
        return f

    def finite_projection_fibers(self, projection:dict[str,str])->dict[str,list[str]]:
        """Partition known form identifiers by a declared, possibly lossy feature."""
        if set(projection)-set(self.forms):
            raise KeyError('projection includes unknown form')
        fibers:dict[str,list[str]]={}
        for fid, feature in projection.items():
            fibers.setdefault(feature,[]).append(fid)
        return fibers

    def certificate(self, ent_id:str)->dict[str,Any]:
        e=self.entanglements[ent_id]
        return {'id':e.id,'arity':{'inputs':len(e.inputs),'outputs':len(e.outputs)},
                'input_forms':[asdict(self.forms[x]) for x in e.inputs],
                'output_forms':[asdict(self.forms[x]) for x in e.outputs],
                'strands':[asdict(s) for s in e.strands],
                'serialized_binary':canonical_record_bits(asdict(e)),
                'contracts':[asdict(self.operators[s.operator]) for s in e.strands]}

    def snapshot(self)->dict[str,Any]:
        return {'schema':'CEFC/0.1','forms':[{**asdict(x),
                          'value_utf8_bits':utf8_bits(x.value),
                          'record_binary':canonical_record_bits(asdict(x))}
                          for x in self.forms.values()],
                'operators':[asdict(x) for x in self.operators.values()],
                'entanglements':[self.certificate(k) for k in self.entanglements]}


def abstract_demonstrator()->InfinityComplex:
    """Domain-neutral demo: placeholders only; no drugs or medical assumptions."""
    x=InfinityComplex()
    for f in [
        Form('n','Text','FORM α  B','surface'),
        Form('b','Bits',utf8_bits('FORM α  B'),'encoding/utf-8'),
        Form('c','Concept','K','ontology/A'),
        Form('a','Concept','A','ontology/A'),
        Form('d','Concept','D','ontology/B'),
        Form('w','Concept','W','ontology/compound'),
        Form('h','Concept','H','ontology/compound'),
        Form('p','Attribute','feature-p','predicate-space'),
    ]: x.add_form(f)
    for op in [
        Operator('ENCODE_UTF8',('Text',),('Bits',),'exact bytes; preserve spaces and case','none'),
        Operator('DENOTES',('Text',),('Concept',),'requires lexicon or grounded source; not inferred from bytes','meaning may be context dependent'),
        Operator('SYNONYM',('Concept',),('Concept',),'sense-specific correspondence, not identity','possible loss of register/scope'),
        Operator('SHARES_PROPERTY',('Concept','Concept','Attribute'),('Concept',),'3-input typed construction; all three ports needed','new proposition not automatically valid'),
        Operator('REINTERPRET',('Concept',),('Concept',),'explicit context-changing interpretation','may lose properties'),
    ]: x.register(op)
    for e in [
        Entanglement('ent-encode',('n',),('b',),(Strand('ENCODE_UTF8','established','Python UTF-8 codec; exact byte witness'),)),
        Entanglement('ent-denote',('n',),('c',),(Strand('DENOTES','stipulated','Example token assignment only'),)),
        Entanglement('ent-reinterpret',('a',),('d',),(
            Strand('REINTERPRET','established','Example formal interpretation A→D, axiom A1',context='model M'),
            Strand('REINTERPRET','hypothesis','Unverified alternative interpretation H1',context='model N'),)),
        Entanglement('ent-three',('a','d','p'),('w',),(Strand('SHARES_PROPERTY','derived','Formal derivation-rule witness demo/1',context='formal system F'),)),
        Entanglement('ent-unknown',('c',),('h',),(Strand('SYNONYM','hypothesis','Unverified similarity hypothesis'),)),
    ]: x.add_entanglement(e)
    return x


if __name__=='__main__':
    g=abstract_demonstrator()
    print(json.dumps({'unicode':binary_record('FORM α  B'),
                      'closure_without_third_port':sorted(g.reachable(['a','d'])[0]),
                      'closure_with_third_port':sorted(g.reachable(['a','d','p'])[0]),
                      'multistrand_certificate':g.certificate('ent-reinterpret'),
                      'edges':len(g.entanglements)},ensure_ascii=False,indent=2))
