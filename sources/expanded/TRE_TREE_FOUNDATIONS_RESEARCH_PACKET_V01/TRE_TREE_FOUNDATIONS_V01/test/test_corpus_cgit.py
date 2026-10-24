import unittest
from tre.core import Rejection
from tre.corpus import CorpusContract, CorpusForge
from tre.cgit import ObjectGraph

class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.f=CorpusForge()
        self.a=CorpusContract('roots','1',('name','meaning'),'CC0','fixture:roots','term')
        self.b=CorpusContract('leaves','1',('label','meaning'),'CC0','fixture:leaves','term')
    def test_grammar_before_ingestion(self):
        with self.assertRaises(Rejection):self.f.ingest('roots',{'name':'x'})
    def test_inexact_shape_rejected(self):
        self.f.register(self.a)
        with self.assertRaises(Rejection):self.f.ingest('roots',{'name':'root'})
    def test_deduplicate(self):
        self.f.register(self.a);a=self.f.ingest('roots',{'name':'root','meaning':'support'});b=self.f.ingest('roots',{'meaning':'support','name':'root'});self.assertEqual(a,b);self.assertEqual(self.f.manifest()['object_count'],1)
    def test_no_mutating_contract(self):
        self.f.register(self.a)
        with self.assertRaises(Rejection):self.f.register(self.a)
    def test_bridge(self):
        self.f.register(self.a);self.f.register(self.b)
        self.f.declare_bridge('roots','leaves',{'name':'label','meaning':'meaning'})
        src=self.f.ingest('roots',{'name':'root','meaning':'support'})
        dst=self.f.bridge(src,'leaves');self.assertNotEqual(src,dst);self.assertEqual(self.f.objects[dst]['record']['label'],'root')
    def test_bridge_requires_admission(self):
        self.f.register(self.a);self.f.register(self.b);src=self.f.ingest('roots',{'name':'x','meaning':'y'})
        with self.assertRaises(Rejection):self.f.bridge(src,'leaves')
    def test_partial_bridge_rejected(self):
        self.f.register(self.a);self.f.register(self.b)
        self.f.declare_bridge('roots','leaves',{'name':'label'})
        src=self.f.ingest('roots',{'name':'x','meaning':'y'})
        with self.assertRaises(Rejection):self.f.bridge(src,'leaves')

class CGITTests(unittest.TestCase):
    def test_child_first_commit(self):
        g=ObjectGraph();a=g.put('source',{'text':'A'});b=g.put('source',{'text':'B'})
        t=g.put('tree',{'name':'test'},(a,b));c=g.put('commit',{'parent':None},(t,));self.assertTrue(g.verify(c))
    def test_order_commits(self):
        g=ObjectGraph();a=g.put('source',{'x':1});b=g.put('source',{'x':2});self.assertNotEqual(g.put('tree',{},(a,b)),g.put('tree',{},(b,a)))
    def test_dedup_content(self):
        g=ObjectGraph();a=g.put('source',{'x':1});b=g.put('source',{'x':1});self.assertEqual(a,b);self.assertEqual(g.count(),1)
    def test_nonexistent_child(self):
        g=ObjectGraph()
        with self.assertRaises(Rejection):g.put('tree',{},('sha256:absent',))
    def test_tamper_detected(self):
        g=ObjectGraph();a=g.put('source',{'x':1});g._blobs[a]['payload']['x']=2;self.assertFalse(g.verify(a))
    def test_get_copy(self):
        g=ObjectGraph();a=g.put('source',{'x':1});obj=g.get(a);obj['payload']['x']=4;self.assertTrue(g.verify(a))

if __name__=='__main__':unittest.main()
