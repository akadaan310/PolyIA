"""Codex harness: authenticated local stage advancement by evidence-checked receipts.
Never performs git pushes or modifies external repositories.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json,hashlib

STAGES=('PREFLIGHT','INVENTORY','EXTRACT','CLASSIFY','FORMALIZE','IMPLEMENT','VERIFY','ASSEMBLE','BENCHMARK','RELEASE_CANDIDATE')
EVIDENCE=('environment-audit','source-ledger','candidate-inventory','typed-contracts','law-and-negative-tests','unit-test-report','integration-and-roundtrip','benchmark-and-counterexamples','release-gate')

class HarnessError(ValueError):pass

def init(base:Path)->dict:
    base.mkdir(parents=True,exist_ok=True)
    state=base/'harness_state.json'
    if state.exists():raise HarnessError('state already exists: refusing overwrite')
    obj={'stage':STAGES[0],'seq':0,'last_hash':'GENESIS','events':[]}
    state.write_text(json.dumps(obj,sort_keys=True,indent=2))
    return obj

def load(base:Path)->dict:
    return json.loads((base/'harness_state.json').read_text())

def advance(base:Path,receipt:dict)->dict:
    old=load(base)
    if old['stage']==STAGES[-1]:raise HarnessError('terminal state')
    idx=STAGES.index(old['stage']); req=EVIDENCE[idx]
    if receipt.get('kind')!=req or receipt.get('passed') is not True:
        raise HarnessError(f'cannot advance: require passing {req}')
    if not isinstance(receipt.get('sha256'),str) or len(receipt['sha256'])!=64 or any(c not in '0123456789abcdef' for c in receipt['sha256']):
        raise HarnessError('require valid evidence content SHA-256')
    # This is a digest-format-only gate; production must also verify the actual file bytes and signatures.
    nxt=STAGES[idx+1]
    evt={'seq':old['seq']+1,'from':old['stage'],'to':nxt,'receipt':receipt,'parent':old['last_hash']}
    h=hashlib.sha256(json.dumps(evt,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    evt['event_hash']=h
    new={'stage':nxt,'seq':old['seq']+1,'last_hash':h,'events':old['events']+[evt]}
    temp=base/'harness_state.tmp';temp.write_text(json.dumps(new,sort_keys=True,indent=2));temp.replace(base/'harness_state.json')
    return new

def verify(base:Path)->bool:
    data=load(base);old='GENESIS'
    for i,event in enumerate(data['events']):
        if event['parent']!=old or event['seq']!=i+1:return False
        e=dict(event);h=e.pop('event_hash',None)
        if hashlib.sha256(json.dumps(e,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=h:return False
        old=h
    return data['last_hash']==old and data['seq']==len(data['events']) and data['stage']==STAGES[data['seq']]
