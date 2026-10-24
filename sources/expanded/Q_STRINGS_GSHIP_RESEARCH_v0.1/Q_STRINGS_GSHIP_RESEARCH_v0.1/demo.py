"""Demonstrate the Q-String address as an accessor to a typed grammar record, not a reversible hash."""
from src.qstrings import QStore,QString,Rule
import json
s=QStore()
for node in ['A','B','C']:
    s.sort(node,'Node')
s.rule(Rule('next','Node','Node','list'))
s.rule(Rule('prev','Node','Node','list'))
a=QString('A','B','next','list',witness='defined-list-A-B')
b=QString('B','C','next','list',witness='defined-list-B-C')
addr1=s.insert(a);addr2=s.insert(b)
print(json.dumps({
  'qaddresses':[addr1,addr2],
  'roundtrip_exact':s.get(addr1)==a,
  'pair_exists':s.has('A','B','next'),
  'path_word':['next','next'],
  'path_witnesses':[q.witness for q in s.verified_path('A','C',('next','next'),'list')],
  'bogus_shortcut':s.verified_path('A','C',('next',),'list') is None,
  'note':'SHA-256 is not inverted: canonical payload was retained in an external store.'
},indent=2))
