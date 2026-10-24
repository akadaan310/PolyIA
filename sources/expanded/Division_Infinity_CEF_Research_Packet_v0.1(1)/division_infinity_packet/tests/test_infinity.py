import sys, unittest, copy
import json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from infinity import *

class TestInfinity(unittest.TestCase):
    def setUp(self): self.g=abstract_demonstrator()
    def test_ascii_space_binary(self):
        self.assertEqual(utf8_bits('A B'),'010000010010000001000010')
    def test_duplicate_whitespace_is_preserved(self):
        self.assertEqual(bits_utf8(utf8_bits('two  words \n')),'two  words \n')
    def test_arabic_round_trip(self):
        self.assertEqual(bits_utf8(utf8_bits('عِلْمٌ')),'عِلْمٌ')
    def test_combining_mark_round_trip(self):
        self.assertEqual(bits_utf8(utf8_bits('e\u0301')), 'e\u0301')
    def test_binary_segments_exact(self):
        b=binary_record(' A\tβ  ')
        self.assertEqual(''.join(v['bits'] for v in b['segments']),b['utf8_bits'])
        self.assertEqual([v['kind'] for v in b['segments']],['whitespace','nonwhitespace','whitespace','nonwhitespace','whitespace'])
    def test_unicode_normalization_is_explicit(self):
        b=binary_record('e\u0301')
        self.assertTrue(b['NFC_changes_original'])
        self.assertNotEqual(b['utf8_bits'],utf8_bits(b['NFC']))
    def test_binary_record_per_codepoint(self):
        b=binary_record('α B')
        self.assertEqual([v['unicode'] for v in b['codepoints']],['U+03B1','U+0020','U+0042'])
    def test_binary_of_serializable_form(self):
        r=canonical_record_bits({'z':2,'a':'α'})
        self.assertEqual(bits_utf8(r['utf8_bits']),r['canonical_json'])
    def test_entanglement_requires_all_three_inputs(self):
        self.assertNotIn('w',self.g.reachable(['a','d'])[0])
        self.assertIn('w',self.g.reachable(['a','d','p'])[0])
    def test_stipulation_not_automatically_fact(self):
        self.assertNotIn('c',self.g.reachable(['n'])[0])
        self.assertIn('c',self.g.reachable(['n'],{'stipulated','established'})[0])
    def test_hypothesis_not_certified_as_fact(self):
        self.assertNotIn('h',self.g.reachable(['c'])[0])
    def test_multiple_entanglement_strands(self):
        c=self.g.certificate('ent-reinterpret')
        self.assertEqual(len(c['strands']),2)
        self.assertEqual({s['status'] for s in c['strands']},{'hypothesis','established'})
    def test_wrong_types_rejected(self):
        with self.assertRaises(RejectedBridge):
            self.g.add_entanglement(Entanglement('wrong',('n',),('a',),
                              (Strand('ENCODE_UTF8','established','fake'),)))
    def test_untyped_operator_rejected(self):
        with self.assertRaises(RejectedBridge):
            self.g.add_entanglement(Entanglement('unknown',('n',),('b',),
                              (Strand('DOES_NOT_EXIST','established','fake'),)))
    def test_hyperedge_port_order_matters(self):
        with self.assertRaises(RejectedBridge):
            self.g.add_entanglement(Entanglement('wrong-order',('p','d','a'),('w',),
                              (Strand('SHARES_PROPERTY','derived','fake'),)))
    def test_fiber_returns_tuple(self):
        self.assertEqual(self.g.fiber('ENCODE_UTF8','b'),[('n',)])
    def test_no_empty_entanglement(self):
        with self.assertRaises(RejectedBridge):
            self.g.add_entanglement(Entanglement('empty',(),(),(Strand('ENCODE_UTF8','established','fake'),)))
    def test_utf8_ill_formed(self):
        with self.assertRaises(ValueError): bits_utf8('00001')
        with self.assertRaises(UnicodeDecodeError): bits_utf8('11111111')
    def test_unknown_seed(self):
        with self.assertRaises(KeyError): self.g.reachable(['no-such-form'])
    def test_snapshot_is_json_serializable(self):
        self.assertIn('CEFC/0.1',json.dumps(self.g.snapshot()))
    def test_every_form_has_binary_record(self):
        for f in self.g.snapshot()['forms']:
            self.assertEqual(bits_utf8(f['value_utf8_bits']),f['value'])
            self.assertEqual(bits_utf8(f['record_binary']['utf8_bits']),f['record_binary']['canonical_json'])
    def test_reified_edge_is_form_and_has_binary(self):
        f=self.g.reify_entanglement('ent-three')
        self.assertEqual(f.sort,'Entanglement')
        self.assertIn('ent-three',f.value)
        self.assertTrue(any(v['id']==f.id and v['value_utf8_bits'] for v in self.g.snapshot()['forms']))
    def test_projection_fibers_expose_collisions(self):
        self.assertEqual(self.g.finite_projection_fibers({'a':'shape-q','d':'shape-q','p':'shape-r'}),
                         {'shape-q':['a','d'],'shape-r':['p']})

if __name__=='__main__': unittest.main(verbosity=2)
