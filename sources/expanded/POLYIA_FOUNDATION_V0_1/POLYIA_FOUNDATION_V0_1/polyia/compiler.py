"""Typed backward-chaining composer. Rejects multiple providers, cycles and unmet interfaces."""
from dataclasses import dataclass
from .registry import Atom,ATOMS,CAPABILITY_OUTPUT
from .lang import Commission,CompileError
import hashlib

@dataclass(frozen=True)
class Plan:
    steps:tuple[Atom,...]
    types:tuple[str,...]
    requirements:tuple[str,...]
    digest:str

class CompositionError(CompileError):pass

def compose(c:Commission, available:tuple[Atom,...]=ATOMS, input_types=frozenset({'TaskText'}))->Plan:
    # A zero-implementation-dependency composition: ports join only on types.
    if 'invent-cognates' not in c.deny and 'guess-etymology' not in c.deny:
        raise CompositionError('missing mandatory deny invent-cognates or guess-etymology')
    if c.evidence=='attested' and any(a.evidence!='attested' for a in available):
        # Only reject selected fixture atoms later, allowing future real data adapters.
        pass
    providers={}
    for a in available:
        if a.cost<0:raise CompositionError('negative cost')
        for t in a.outputs:providers.setdefault(t,[]).append(a)
    want=[CAPABILITY_OUTPUT.get(x) for x in c.capabilities]
    if any(x is None for x in want):raise CompositionError('unknown requested capability')
    steps=[];done=set(input_types);visiting=set(); chosen={}
    def satisfy(t):
        if t in done:return
        if t in visiting:raise CompositionError('cycle detected at '+t)
        opts=providers.get(t,[])
        if len(opts)!=1:raise CompositionError(f'expected one provider for {t}; got {len(opts)}')
        a=opts[0]
        if c.evidence=='attested' and a.evidence!='attested':raise CompositionError('attested evidence absent for '+a.id)
        visiting.add(t)
        for inp in a.inputs:satisfy(inp)
        visiting.remove(t)
        if a.id not in chosen:
            chosen[a.id]=a;steps.append(a)
            done.update(a.outputs)
    for t in want:satisfy(t)
    if sum(x.cost for x in steps)>c.budget:raise CompositionError('composition exceeds budget')
    digest=hashlib.sha256((c.source+'|'+','.join(a.id for a in steps)).encode()).hexdigest()
    return Plan(tuple(steps),tuple(sorted(done)),c.capabilities,digest)
