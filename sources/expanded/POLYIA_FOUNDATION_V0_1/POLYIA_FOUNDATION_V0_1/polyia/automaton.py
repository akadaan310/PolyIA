"""Compile a typed plan into a self-contained proof-carrying automaton artifact."""
from dataclasses import asdict
from .compiler import Plan
from .lang import Commission
import hashlib,json,html


def make_artifact(c:Commission, plan:Plan)->dict:
    states=['START']+[f'S{i+1}_{a.id.split("@")[0].replace(".","_")}' for i,a in enumerate(plan.steps)]+['ACCEPT']
    edges=[]
    for i,a in enumerate(plan.steps):
        edges.append({'from':states[i],'to':states[i+1], 'via':a.id,'requires':list(a.inputs),'ensures':list(a.outputs), 'evidence':a.evidence})
    edges.append({'from':states[-2],'to':'ACCEPT','via':'admission','requires':list(plan.requirements),'ensures':['machine-artifact'],'evidence':'structural-only'})
    payload={'format':'POLYIA-AUTOMATON/0.1','task':c.task,'source':c.source,'profile':'fixture-research','states':states,'start':'START','accept':['ACCEPT'],'transitions':edges,'capabilities':list(c.capabilities),'denials':list(c.deny),'plan_hash':plan.digest,'guards':['no unattested claims','no effects','bounded plan','typed ports'],'observed_results':None}
    payload['artifact_hash']=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    return payload

def to_dot(artifact:dict)->str:
    q=lambda x:'"'+x.replace('\\','\\\\').replace('"','\\"')+'"'
    lines=['digraph POLYIA {','  rankdir=LR;']
    for x in artifact['states']:
        lines.append(f'  {q(x)} [shape={"doublecircle" if x=="ACCEPT" else "ellipse"}];')
    for e in artifact['transitions']:
        lines.append(f'  {q(e["from"])} -> {q(e["to"])} [label={q(e["via"])}];')
    lines.append('}')
    return '\n'.join(lines)+'\n'

def to_html(artifact:dict)->str:
    # Static local human-facing machine map. No remote resources or browser scripting.
    items=''.join('<li><strong>'+html.escape(e['via'])+'</strong> — '+html.escape(e['from'])+' → '+html.escape(e['to'])+'</li>' for e in artifact['transitions'])
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>POLYIA Automaton</title><body><h1>'+html.escape(artifact['task'])+'</h1><p>Fixture only; no actual multilingual lookup</p><ol>'+items+'</ol><code>'+artifact['artifact_hash']+'</code></body></html>\n'
