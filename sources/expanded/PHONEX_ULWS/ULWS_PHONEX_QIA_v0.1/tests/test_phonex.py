import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from phonex import *

class TestPhonex(unittest.TestCase):
    def setUp(self): self.a=Atlas(sample())
    def test_count(self): self.assertEqual(len(self.a.forms),7)
    def test_same_phone(self): self.assertEqual(segment_distance('t','t'),0)
    def test_emphatic(self): self.assertGreater(segment_distance('t','tˤ'),0)
    def test_emphatic_near(self): self.assertLess(segment_distance('t','tˤ'),segment_distance('t','m'))
    def test_p_b_close(self): self.assertLess(segment_distance('p','b'),segment_distance('p','l'))
    def test_vowels(self): self.assertGreater(segment_distance('u','ɒ'),0)
    def test_prefix_topology(self):
        out=self.a.match(('t','ə','p','ɒ','l'),budget=.5)
        self.assertIn('eng-topology',{x['id'] for x in out['matches']})
    def test_carried_emphatic(self):
        out=self.a.match(('t','u','b','u','l'),budget=.20)
        self.assertIn('arb-topologia-ta',{x['id'] for x in out['matches']})
    def test_do_not_anywhere_substring(self):
        out=self.a.match(('ɡ','ɹ','ə','f'),budget=.10)
        self.assertNotIn('eng-topography',{x['id'] for x in out['matches']})
    def test_no_etymology(self):self.assertFalse(self.a.match(('t',))['historical_inference'])
    def test_no_semantic_proof(self):self.assertFalse(self.a.match(('t',))['semantic_inference'])
    def test_status(self):self.assertTrue(all(x['status']=='PHONETIC_CANDIDATE_ONLY' for x in self.a.match(('t',))['matches']))
    def test_approx_not_exhaustive(self):self.assertIn('INCOMPLETE',self.a.match(('t',))['completeness'])
    def test_source_attestation(self):self.assertTrue(all(x['evidence']=='illustrative_only' for x in self.a.match(('t',))['matches']))
    def test_two_meanings_not_collapsed(self):
        out=self.a.match(('t','ə','p','ɒ'),budget=0)
        self.assertIn('toy-homophone',{x['id'] for x in out['matches']})
        self.assertNotEqual(self.a.forms['toy-homophone'].gloss,self.a.forms['eng-topology'].gloss)
    def test_query_refused(self):
        with self.assertRaises(ValueError):self.a.match(())
    def test_duplicate_id_refused(self):
        with self.assertRaises(ValueError):Atlas(sample()+[sample()[0]])
    def test_unknown_features(self):self.assertEqual(segment_distance('UNKNOWN','t'),1)
    def test_bounded_cost(self):self.assertTrue(0<=phonetic_prefix_distance(('t',),('t','a'))[0]<=1)
    def test_qstring_deterministic(self):self.assertEqual(qstring_id({'a':1,'b':2}),qstring_id({'b':2,'a':1}))
    def test_qstring_changes(self):self.assertNotEqual(qstring_id({'a':1}),qstring_id({'a':2}))
    def test_dot_not_stripped(self):self.assertEqual(self.a.forms['arb-topologia-ta'].surface,'طوبولوجيا')
    def test_full_candidate_metadata(self):
        v=self.a.match(('t',))
        self.assertIn('source',v['matches'][0])
    def test_no_fake_literal_ipa_seg(self):
        self.assertEqual(segment_distance('d͡ʒ','d͡ʒ'),0)
    def test_exact_prefix_index(self):self.assertIn('eng-topology',self.a.prefix[('t','ə')])

if __name__=='__main__':unittest.main()
