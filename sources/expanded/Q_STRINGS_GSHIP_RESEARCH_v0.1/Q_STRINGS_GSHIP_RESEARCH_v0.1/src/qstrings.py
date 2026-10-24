"""Q-Strings 0.1: classical, typed, hash-addressable G-ship relations.

Research prototype. 'quantum' is a domain-specific analogy, not physical quantum computation.
The SHA-256 digest is a content identifier, never a reversible encoding or execution permission.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from typing import Callable
import hashlib, json


def canonical_bytes(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def cid(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class QString:
    src: str
    dst: str
    rel: str
    grammar: str
    scope: str = 'default'
    level: int = 0
    witness: str = ''
    status: str = 'house'
    version: int = 1

    def __post_init__(self) -> None:
        if not (self.src and self.dst and self.rel and self.grammar and self.scope):
            raise ValueError('empty required field')
        if self.level < 0 or self.version != 1:
            raise ValueError('invalid level or unsupported version')
        if self.status not in {'house','established','hypothesis','refuted','stipulated'}:
            raise ValueError('invalid epistemic status')

    def serial(self) -> bytes:
        return canonical_bytes(asdict(self))

    @property
    def digest(self) -> str:
        return cid(self.serial())

    @property
    def address(self) -> str:
        # Namespace and typed ports remain in the *stored payload*. The address is an opaque ID.
        return 'qstr:v1:' + self.digest


@dataclass(frozen=True)
class Rule:
    symbol: str
    from_sort: str
    to_sort: str
    grammar: str
    predicate: Callable[[QString], bool] | None = None


class GrammarError(ValueError):
    pass


class QStore:
    def __init__(self):
        self.records: dict[str, bytes] = {}
        self.decoded: dict[str, QString] = {}
        self.pairs: dict[tuple[str,str,str], list[str]] = defaultdict(list)
        self.outgoing: dict[tuple[str,str], list[str]] = defaultdict(list)
        self.incoming: dict[tuple[str,str], list[str]] = defaultdict(list)
        self.grammars: dict[str, list[str]] = defaultdict(list)
        self.node_sort: dict[str, str] = {}
        self.rules: dict[tuple[str,str], Rule] = {}

    def sort(self, node: str, sort: str) -> None:
        if node in self.node_sort and self.node_sort[node] != sort:
            raise GrammarError('node sort conflict')
        self.node_sort[node] = sort

    def rule(self, r: Rule) -> None:
        key=(r.grammar,r.symbol)
        if key in self.rules and self.rules[key] != r:
            raise GrammarError('cannot alter an existing operation contract in place; version the grammar')
        self.rules[key] = r

    def insert(self, q: QString) -> str:
        key = (q.grammar, q.rel)
        if key not in self.rules:
            raise GrammarError('unknown registered operation')
        rule = self.rules[key]
        if self.node_sort.get(q.src) != rule.from_sort or self.node_sort.get(q.dst) != rule.to_sort:
            raise GrammarError('type mismatch')
        if rule.predicate and not rule.predicate(q):
            raise GrammarError('admission predicate refused')
        digest = q.digest
        if digest in self.records:
            if self.records[digest] != q.serial():
                raise ValueError('hash collision or conflicting canonical payload')
            return q.address
        self.records[digest] = q.serial()
        self.decoded[digest] = q
        self.pairs[q.src, q.dst, q.rel].append(digest)
        self.outgoing[q.src, q.rel].append(digest)
        self.incoming[q.dst, q.rel].append(digest)
        self.grammars[q.grammar].append(digest)
        return q.address

    def get(self, address: str) -> QString:
        if not address.startswith('qstr:v1:'):
            raise ValueError('unrecognized address')
        digest = address[len('qstr:v1:'):]
        if digest not in self.records or cid(self.records[digest]) != digest:
            raise KeyError('missing or corrupted content')
        return QString(**json.loads(self.records[digest]))

    def lookup(self, src: str, dst: str, rel: str) -> list[QString]:
        return [self.decoded[d] for d in self.pairs.get((src,dst,rel), ())]

    def has(self, src: str, dst: str, rel: str) -> bool:
        return bool(self.pairs.get((src,dst,rel)))

    def traverse(self, src: str, rel: str) -> list[QString]:
        return [self.decoded[d] for d in self.outgoing.get((src,rel), ())]

    def verified_path(self, src: str, dst: str, word: tuple[str,...], grammar: str,
                      allowed_status: frozenset[str] = frozenset({'established','house','stipulated'})) -> list[QString] | None:
        # Exact label sequence: bounded product traversal, preserves concrete edge witnesses.
        frontier: dict[str,list[QString]] = {src:[]}
        for symbol in word:
            if (grammar,symbol) not in self.rules:
                raise GrammarError('word has unknown symbol')
            next_frontier = {}
            for node, witness in frontier.items():
                for q in self.traverse(node, symbol):
                    if q.grammar == grammar and q.status in allowed_status and q.dst not in next_frontier:
                        next_frontier[q.dst] = witness + [q]
            frontier=next_frontier
            if not frontier:
                return None
        return frontier.get(dst)

    def bounded_reachability(self, src: str, target: str, labels: set[str], grammar: str,
                             max_steps: int,
                             allowed_status: frozenset[str] = frozenset({'established','house','stipulated'})) -> list[QString] | None:
        """BFS shortest witness using parent pointers. O(V+E) for fixed label set, with indexed outgoing postings."""
        if max_steps < 0:
            raise ValueError('negative max_steps')
        que=deque([src]); visited={src}; depth={src:0}; parent:dict[str,tuple[str,QString]]={}
        while que:
            node=que.popleft()
            if node == target:
                result=[]
                while node != src:
                    prev,q=parent[node]
                    result.append(q); node=prev
                return list(reversed(result))
            if depth[node] >= max_steps:
                continue
            for symbol in sorted(labels):
                for q in self.traverse(node,symbol):
                    if q.grammar != grammar or q.status not in allowed_status: continue
                    if q.dst not in visited:
                        visited.add(q.dst)
                        depth[q.dst]=depth[node]+1
                        parent[q.dst]=(node,q)
                        que.append(q.dst)
        return None


def compose(a: QString,b: QString,store: QStore) -> tuple[str,str] | None:
    """G-ship composition is positional and typed; returns a labelled-path pair, not a new inferred physical fact."""
    if a.dst != b.src or a.grammar != b.grammar:
        return None
    if store.node_sort.get(a.dst) is None:
        return None
    return (a.src, b.dst)


# Retain original bytes in registry: programmable content-address rather than impossible hash inversion.
def wire_roundtrip(src: str,dst: str,rel: str,grammar='gship') -> tuple[QString,QString]:
    store=QStore()
    store.sort(src,'Node'); store.sort(dst,'Node')
    store.rule(Rule(rel,'Node','Node',grammar))
    original=QString(src,dst,rel,grammar)
    addr=store.insert(original)
    return original, store.get(addr)
