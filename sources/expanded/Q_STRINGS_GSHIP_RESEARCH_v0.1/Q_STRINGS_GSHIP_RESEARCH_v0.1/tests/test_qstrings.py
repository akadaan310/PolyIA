import unittest
from src.qstrings import QStore, QString, Rule, GrammarError, compose, wire_roundtrip, canonical_bytes

class QStringTests(unittest.TestCase):
    def setUp(self):
        self.store=QStore()
        for n in ('A','B','C','D'): self.store.sort(n,'Node')
        for s in ('next','inverse','depends'): self.store.rule(Rule(s,'Node','Node','list'))
    def test_address_identity(self):
        q=QString('A','B','next','list',witness='w')
        self.assertEqual(self.store.insert(q),q.address)
        self.assertEqual(self.store.get(q.address),q)
    def test_opaque_digest(self):
        q=QString('A','B','next','list')
        self.assertNotIn('A',q.digest)
        with self.assertRaises(KeyError): self.store.get(q.address)
    def test_tamper_check(self):
        q=QString('A','B','next','list'); self.store.insert(q)
        self.store.records[q.digest]=b'not-original'
        with self.assertRaises(KeyError):self.store.get(q.address)
    def test_collision_safe_pair_list(self):
        q1=QString('A','B','next','list');q2=QString('A','B','next','list',witness='w2')
        self.store.insert(q1);self.store.insert(q2)
        self.assertEqual(len(self.store.lookup('A','B','next')),2)
    def test_unchanged_duplicate(self):
        q=QString('A','B','next','list');self.store.insert(q);self.store.insert(q)
        self.assertEqual(len(self.store.lookup('A','B','next')),1)
    def test_reject_unregistered(self):
        with self.assertRaises(GrammarError):self.store.insert(QString('A','B','secret','list'))
    def test_refuse_sort_mismatch(self):
        self.store.sort('X','Physics')
        with self.assertRaises(GrammarError):self.store.insert(QString('X','B','next','list'))
    def test_path_word(self):
        a=QString('A','B','next','list');b=QString('B','C','next','list');self.store.insert(a);self.store.insert(b)
        self.assertEqual(self.store.verified_path('A','C',('next','next'),'list'),[a,b])
        self.assertIsNone(self.store.verified_path('A','D',('next',),'list'))
    def test_bfs(self):
        for a,b in [('A','B'),('B','C'),('C','D')]:self.store.insert(QString(a,b,'next','list'))
        self.assertEqual(len(self.store.bounded_reachability('A','D',{'next'},'list',4)),3)
        self.assertIsNone(self.store.bounded_reachability('A','D',{'next'},'list',2))
    def test_composition_order(self):
        a=QString('A','B','next','list'); b=QString('B','C','next','list');c=QString('C','D','next','list')
        self.assertEqual(compose(a,b,self.store),('A','C'))
        self.assertIsNone(compose(a,c,self.store))
    def test_reverse_lookup(self):
        q=QString('A','B','next','list');self.store.insert(q)
        self.assertEqual(self.store.incoming['B','next'],[q.digest])
    def test_canonical_key_order(self):
        self.assertEqual(canonical_bytes({'y':2,'x':1}),canonical_bytes({'x':1,'y':2}))
    def test_wire_roundtrip(self):
        self.assertEqual(*wire_roundtrip('L','R','next'))
    def test_hypothesis_not_proof(self):
        q=QString('A','B','next','list',status='hypothesis')
        self.assertEqual(self.store.get(self.store.insert(q)).status,'hypothesis')
    def test_refuted_edges_are_not_proofs(self):
        q=QString('A','B','next','list',status='refuted')
        self.store.insert(q)
        self.assertIsNone(self.store.verified_path('A','B',('next',),'list'))
        self.assertIsNone(self.store.bounded_reachability('A','B',{'next'},'list',2))
    def test_hypothesis_exclusion(self):
        self.store.insert(QString('A','B','next','list',status='hypothesis'))
        self.assertIsNone(self.store.verified_path('A','B',('next',),'list'))
    def test_negative_budget_refused(self):
        with self.assertRaises(ValueError):self.store.bounded_reachability('A','B',{'next'},'list',-1)
    def test_rule_contract_cannot_mutate(self):
        with self.assertRaises(GrammarError):
            self.store.rule(Rule('next','Physics','Node','list'))
    def test_no_empty(self):
        with self.assertRaises(ValueError): QString('','','','')

if __name__=='__main__':unittest.main()
