"""Minimal typed content-addressed graph with independently checked child links.

It's a CGIT research fixture, NOT Git protocol implementation, and doesn't
purport to make Merkle membership proofs O(1).
"""
from copy import deepcopy
from .core import digest, Rejection

class ObjectGraph:
    def __init__(self):self._blobs:dict[str,dict]={}

    def put(self,kind:str,payload:dict,children:tuple[str,...]=())->str:
        if kind not in {'source','grammar','tree','commit','artifact'}:
            raise Rejection('unrecognized object kind')
        if not isinstance(payload,dict) or not isinstance(children,tuple):
            raise Rejection('bad object shape')
        if any(c not in self._blobs for c in children):
            raise Rejection('referenced child must exist (no cycles on insertion)')
        obj={'kind':kind,'payload':deepcopy(payload),'children':list(children)}
        cid='sha256:'+digest('TRE/CGIT/OBJECT/0.1',obj)
        self._blobs[cid]=obj
        return cid

    def get(self,cid:str)->dict:
        if cid not in self._blobs:raise Rejection('content id unknown')
        return deepcopy(self._blobs[cid])

    def verify(self,cid:str)->bool:
        if cid not in self._blobs:return False
        visited=set();todo=[cid]
        while todo:
            h=todo.pop()
            if h in visited:continue
            obj=self._blobs.get(h)
            if obj is None:return False
            if 'sha256:'+digest('TRE/CGIT/OBJECT/0.1',obj)!=h:return False
            visited.add(h);todo.extend(obj['children'])
        return True

    def count(self)->int:return len(self._blobs)
