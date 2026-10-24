"""TRE/TREE v0.1: a bounded, deterministic, replayable structure+resource kernel.

Research model. It is NOT a renderer, physics engine, ecological plant model, or OS.
No external dependencies. Hashes commit to canonical snapshots; they are not pointers.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from json import dumps
from math import cos, sin, pi
from typing import Any


def encode(value: Any) -> bytes:
    return dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(tag: str, value: Any) -> str:
    return sha256(tag.encode('ascii') + b'\x00' + encode(value)).hexdigest()


class Rejection(ValueError):
    """Rejected transition with an explicit structural or resource witness."""
    pass


@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    parent: str | None
    ordinal: int
    xyz: tuple[float, float, float]


@dataclass(frozen=True)
class Coupling:
    provider: str
    consumer: str
    witness: str
    kind: str = 'resource_support'


@dataclass(frozen=True)
class Event:
    version: int
    action: str
    target: str
    source: str
    witness: str
    before: str
    after: str


class TreeMachine:
    """A trunk with separately rooted root/shoot trees + cross-tree dependencies.

    Virtual accounting units are *not* physical units. One soil intake provides
    one water unit; leaf production provides one carbon unit; structure growth
    has declared unit costs. Growth rules are inventions to test mechanics.
    """
    KINDS = {'trunk','root','shoot','leaf','fruit'}
    PARENTS = {'root': {'trunk','root'}, 'shoot': {'trunk','shoot'},
               'leaf': {'shoot'}, 'fruit': {'leaf'}}
    COSTS = {'root': (1,0), 'shoot': (1,1), 'leaf': (1,1), 'fruit': (1,1)}

    def __init__(self, seed: str = 'TREE/0.1', carbon: int = 6, water: int = 4):
        if not isinstance(seed,str) or not seed or len(seed)>256:
            raise Rejection('seed must be a nonempty <=256-char string')
        if type(carbon) is not int or type(water) is not int or carbon<0 or water<0:
            raise Rejection('resources must be nonnegative integers')
        self.seed=seed
        self.nodes: dict[str,Node]={
          't0':Node('t0','trunk',None,0,(0.0,0.0,0.0)),
          'r0':Node('r0','root','t0',0,(0.0,0.0,-1.0)),
          's0':Node('s0','shoot','t0',1,(0.0,0.0,1.0)),
        }
        self.couplings: list[Coupling]=[]
        self.events: list[Event]=[]
        self.version=0
        self.carbon=carbon
        self.water=water
        self.total_carbon_in=carbon
        self.total_water_in=water
        self.used_carbon=0
        self.used_water=0

    def state(self) -> dict[str,Any]:
        return {'seed':self.seed,'version':self.version,
                'nodes':[asdict(self.nodes[i]) for i in sorted(self.nodes)],
                'couplings':[asdict(c) for c in self.couplings],
                'resources':{'carbon':self.carbon,'water':self.water,
                             'total_carbon_in':self.total_carbon_in,
                             'total_water_in':self.total_water_in,
                             'used_carbon':self.used_carbon,'used_water':self.used_water}}

    def content_id(self) -> str:
        return 'sha256:'+digest('TREE/STATE/0.1',self.state())

    def _position(self, parent: Node, ordinal: int, child_kind: str):
        # An adjustable heuristic, not a scientific claim about Fibonacci growth.
        angle=ordinal * (pi * (3.0 - 5.0**0.5))
        radial=0.65 if child_kind in {'leaf','fruit'} else 0.35
        sign=-1.0 if child_kind == 'root' else 1.0
        return (round(parent.xyz[0]+radial*cos(angle),6),
                round(parent.xyz[1]+radial*sin(angle),6),
                round(parent.xyz[2]+sign*.8,6))

    def grow(self, kind: str, parent: str, *, provider: str | None = None,
             expected_version: int | None = None) -> Node:
        if expected_version is not None and expected_version != self.version:
            raise Rejection('version-conflict: expected_version not current')
        if kind not in self.PARENTS:
            raise Rejection('negative-grammar: unsupported growth kind')
        par=self.nodes.get(parent)
        if par is None or par.kind not in self.PARENTS[kind]:
            raise Rejection('negative-grammar: inadmissible parent or missing node')
        if kind in {'leaf','fruit'}:
            if provider not in self.nodes or self.nodes[provider].kind != 'root':
                raise Rejection('missing-witness: leaf or fruit needs existing root provider')
        elif provider is not None:
            raise Rejection('negative-grammar: provider not allowed for branch/root growth')
        c,w=self.COSTS[kind]
        if self.carbon < c or self.water < w:
            raise Rejection('resource-bound: insufficient carbon or water')
        ordinal=sum(1 for n in self.nodes.values() if n.parent==parent)
        ident=f'{kind[0]}{self.version+1}'
        if ident in self.nodes:
            # For fruit/root ID collisions under single-character prefixes, refuse rather than silently overwrite.
            raise Rejection('identity-collision')
        child=Node(ident,kind,parent,ordinal,self._position(par,ordinal,kind))
        before=self.content_id()
        self.nodes[ident]=child
        witness=digest('TREE/GROW-WITNESS/0.1',{'kind':kind,'parent':parent,'provider':provider,
                                             'child':asdict(child),'expected_version':self.version})
        if provider:
            self.couplings.append(Coupling(provider,ident,witness))
        self.carbon-=c; self.water-=w
        self.used_carbon+=c; self.used_water+=w
        self.version+=1
        after=self.content_id()
        self.events.append(Event(self.version,'grow',ident,parent,witness,before,after))
        self.validate()
        return child

    def absorb(self, root: str, water: int = 1, expected_version: int|None=None) -> None:
        if expected_version is not None and expected_version != self.version:
            raise Rejection('version-conflict')
        if root not in self.nodes or self.nodes[root].kind != 'root' or type(water) is not int or water<1 or water>100:
            raise Rejection('absorption invalid')
        before=self.content_id()
        witness=digest('TREE/ABSORB',{'root':root,'water':water,'version':self.version})
        self.water+=water;self.total_water_in+=water;self.version+=1
        self.events.append(Event(self.version,'absorb',root,root,witness,before,self.content_id()))
        self.validate()

    def photosynthesize(self, leaf: str, carbon: int=1, expected_version:int|None=None) -> None:
        if expected_version is not None and expected_version!=self.version:
            raise Rejection('version-conflict')
        if leaf not in self.nodes or self.nodes[leaf].kind!='leaf' or type(carbon) is not int or carbon<1 or carbon>100:
            raise Rejection('photosynthesis invalid')
        before=self.content_id()
        witness=digest('TREE/PHOTO',{'leaf':leaf,'carbon':carbon,'version':self.version})
        self.carbon+=carbon;self.total_carbon_in+=carbon;self.version+=1
        self.events.append(Event(self.version,'photosynthesize',leaf,leaf,witness,before,self.content_id()))
        self.validate()

    def validate(self) -> bool:
        if self.carbon<0 or self.water<0:
            raise AssertionError('negative resource balance')
        if self.carbon+self.used_carbon!=self.total_carbon_in or self.water+self.used_water!=self.total_water_in:
            raise AssertionError('resource accounting does not balance')
        assert self.nodes['t0'].parent is None
        for n in self.nodes.values():
            if n.id == 't0':continue
            assert n.kind in self.PARENTS and n.parent in self.nodes
            assert self.nodes[n.parent].kind in self.PARENTS[n.kind]
            seen=set();p=n.id
            while p is not None:
                if p in seen: raise AssertionError('cycle in structural tree')
                seen.add(p);p=self.nodes[p].parent
        for c in self.couplings:
            if self.nodes[c.provider].kind!='root' or self.nodes[c.consumer].kind not in {'leaf','fruit'}:
                raise AssertionError('typed coupling violation')
        assert self.version == len(self.events)
        return True

    def topology(self) -> dict[str,Any]:
        levels={}
        for n in self.nodes.values():
            d=0;p=n.parent
            while p is not None:
                d+=1;p=self.nodes[p].parent
            levels[n.id]=d
        return {'structural_nodes':len(self.nodes),'cross_couplings':len(self.couplings),
                'maximum_depth':max(levels.values()),'children':{
                    i:sorted(n.id for n in self.nodes.values() if n.parent==i)
                    for i in sorted(self.nodes)},'content_id':self.content_id()}


def run_fixture(seed='TEST') -> dict[str,Any]:
    m=TreeMachine(seed=seed)
    root=m.grow('root','r0')
    branch=m.grow('shoot','s0')
    leaf1=m.grow('leaf',branch.id,provider=root.id)
    m.absorb(root.id)
    m.photosynthesize(leaf1.id)
    leaf2=m.grow('leaf',branch.id,provider='r0')
    fruit=m.grow('fruit',leaf1.id,provider=root.id)
    assert len([x for x in m.nodes.values() if x.parent==branch.id])==2
    return {'kind':'TRE/TREE/research-fixture','state':m.state(),
            'topology':m.topology(), 'events':[asdict(e) for e in m.events],
            'fruit':fruit.id,'invariants_ok':m.validate()}
