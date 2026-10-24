import unittest,sys,math,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from qia import *

class QIATest(unittest.TestCase):
    def test_registered_q_theories(self):
        import json
        d=json.loads((Path(__file__).resolve().parents[1]/'schemas'/'Q_THEORIES_62.json').read_text())
        self.assertEqual(len(d['theories']),62)
        self.assertEqual(len({x['source_topic_id'] for x in d['theories']}),62)
        self.assertEqual([sum(x['source_division']==c for x in d['theories']) for c in 'I II III IV V VI'.split()],[10,10,10,12,10,10])
    def test_exact_ascii(self):
        r=exact_encoding('A  B\nC');self.assertTrue(verify_encoding(r));self.assertEqual(r['raw_byte_count'],6)
    def test_arabic_utf8(self):
        self.assertTrue(verify_encoding(exact_encoding('الْبَيَان')))
    def test_unequal_nfc(self):
        self.assertTrue(exact_encoding('e\u0301')['nfc_changed'])
        self.assertNotEqual(exact_encoding('e\u0301')['sha256'],exact_encoding('é')['sha256'])
    def test_segment(self):
        q=lexicon_demo();self.assertIn('triple',q.derive(['phrase']))
    def test_three_port_requires_all(self):
        q=lexicon_demo();self.assertNotIn('intention',q.derive(['head','pain']))
        self.assertIn('intention',q.derive(['head','pain','reliever']))
    def test_no_infer_active(self):
        q=lexicon_demo();self.assertNotIn('acetaminophen',q.derive(['phrase','head','pain','reliever']))
    def test_identity_requires_stipulation(self):
        q=lexicon_demo();self.assertNotIn('acetaminophen',q.derive(['named-product']))
        self.assertIn('acetaminophen',q.derive(['named-product'],allowed={'user_stipulation'}))
    def test_finite_ambiguity(self):
        q=lexicon_demo();self.assertEqual(len(q.inverse_fiber('SUPPORTS_INDICATION','headache')),3)
    def test_medical_to_intent_not_inverse(self):
        q=lexicon_demo();self.assertNotIn('acetaminophen',q.derive(['headache']))
    def test_latin_vs_greek(self):
        c=lexical_candidates();self.assertEqual(c['head'][1]['language'],'Greek')
    def test_wrong_sort(self):
        q=lexicon_demo()
        with self.assertRaises(QIARefusal):
            q.add_claim(Claim('invalid','PRODUCT_IDENTITY',('head',),'acetaminophen','user_stipulation','x','c'))
    def test_missing_evidence(self):
        q=lexicon_demo()
        with self.assertRaises(QIARefusal):
            q.add_claim(Claim('invalid','PRODUCT_IDENTITY',('named-product',),'acetaminophen','user_stipulation','','c'))
    def test_unknown_status(self):
        q=lexicon_demo()
        with self.assertRaises(QIARefusal):
            q.add_claim(Claim('invalid','PRODUCT_IDENTITY',('named-product',),'acetaminophen','magic','x','c'))
    def test_negative_weight_rejected(self):
        q=lexicon_demo()
        with self.assertRaises(QIARefusal):
            q.add_claim(Claim('invalid','PRODUCT_IDENTITY',('named-product',),'acetaminophen','user_stipulation','x','c',-1))
    def test_hypothesis_not_admitted(self):
        q=lexicon_demo();q.register(RelationSignature('GUESS',('Intent',),'Substance'))
        q.add_claim(Claim('guess','GUESS',('intention',),'ibuprofen','hypothesis','unverified','model'))
        self.assertNotIn('ibuprofen',q.derive(['intention']))
    def test_min_derivation_tree(self):
        q=lexicon_demo();q.register(RelationSignature('ALTERNATE',('Intent',),'Effect'))
        q.add_claim(Claim('cheap','ALTERNATE',('intention',),'headache','formal_derivation','shortcut','model',0.1))
        self.assertIn('cheap',q.derive(['intention'])['headache'].claim_ids)
    def test_no_random_semantic_from_hash(self):
        q=lexicon_demo();self.assertNotIn('acetaminophen',q.derive(['phrase']))
    def test_hadamard_norm(self):
        w=two_basis_interference()
        self.assertTrue(all(abs(n-1)<1e-12 for n in w['norms']))
        self.assertAlmostEqual(w['after_one_H'][0],0.5)
    def test_hadamard_interference(self):
        w=two_basis_interference();self.assertAlmostEqual(w['after_two_H'][0],1)
        self.assertAlmostEqual(w['after_two_H'][1],0)
    def test_spring_one_step(self):
        s=SpringMassIR(1,100,0,0.1,0,0.005)
        self.assertLess(s.step().position_m,s.position_m)
    def test_spring_deterministic(self):
        s=SpringMassIR(1,100,.1,.1,0,.005)
        self.assertEqual(s.step(),s.step())
    def test_spring_small_step_bounded_energy(self):
        s=SpringMassIR(1,100,0,0.1,0,0.0001)
        start=s.energy_joules()
        for i in range(10000):s=s.step()
        self.assertLess(abs(s.energy_joules()-start)/start,0.003)
    def test_spring_invalid_mass(self):
        with self.assertRaises(QIARefusal):SpringMassIR(0,100,0,1,0,.01)
    def test_spring_undamped_stability_guard(self):
        self.assertLess(SpringMassIR(1,100,0,0,0,.01).stability_ratio_undamped(),2)
    def test_sound_delay(self):
        self.assertAlmostEqual(geometric_optics_sound_demo(343)['sound_delay_s'],1)
    def test_sound_square_law(self):
        self.assertAlmostEqual(geometric_optics_sound_demo(10)['ideal_isotropic_intensity_ratio_to_1m'],0.01)
    def test_sound_nonpositive_distance(self):
        with self.assertRaises(QIARefusal): geometric_optics_sound_demo(0)
    def test_derive_ablation(self):
        q=lexicon_demo();del q.claims['effect']
        self.assertNotIn('headache',q.derive(['head','pain','reliever']))
    def test_ordered_ports_refuse(self):
        q=lexicon_demo()
        with self.assertRaises(QIARefusal):
            q.add_claim(Claim('bad','INTERPRET_3',('head','pain','caput'),'intention','formal_derivation','x','model'))
    def test_certificate_stipulated(self):
        q=lexicon_demo()
        c=q.certificate('acetaminophen',['named-product'],allowed={'user_stipulation'})
        self.assertEqual(c['verdict'],'derivable-under-registered-claims')
        self.assertEqual(c['claim_witness'][0]['status'],'user_stipulation')

if __name__=='__main__':unittest.main()

class ExtensionsTest(unittest.TestCase):
    def test_dimensional_force(self):
        from qia import DimQuantity
        m=DimQuantity(2,(0,1,0)); a=DimQuantity(3,(1,0,-2))
        f=m*a
        self.assertEqual(f.dims,(1,1,-2));self.assertEqual(f.value,6)
    def test_dimensional_refusal(self):
        from qia import DimQuantity
        with self.assertRaises(QIARefusal): _=DimQuantity(1,(1,0,0))+DimQuantity(1,(0,0,1))
    def test_fca_closure(self):
        from qia import formal_context_closure
        context={'a':{'grammar','simulation'},'b':{'grammar','typing'},'c':{'typing'}}
        self.assertEqual(formal_context_closure(context,{'grammar'})['closed_intent'],['grammar'])
        self.assertEqual(formal_context_closure(context,{'grammar','simulation'})['extent'],['a'])
    def test_fca_closure_idempotent(self):
        from qia import formal_context_closure
        context={'x':{'a','b'},'y':{'a','c'}}
        c=set(formal_context_closure(context,{'b'})['closed_intent'])
        self.assertEqual(set(formal_context_closure(context,c)['closed_intent']),c)
