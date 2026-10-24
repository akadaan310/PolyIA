import sys, pathlib, unittest, math
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from rasm_state import *

class TestRasmState(unittest.TestCase):
    def test_28(self): self.assertEqual(len(HIJAI),28)
    def test_medial_partition(self): self.assertEqual(set(''.join(CLASS_MEDIAL.values())),set(HIJAI))
    def test_final_partition(self): self.assertEqual(set(''.join(CLASS_FINAL.values())),set(HIJAI))
    def test_15(self): self.assertEqual(len(CLASS_MEDIAL),15)
    def test_subgroup_medial(self): self.assertEqual(partition_order(CLASS_MEDIAL),92160)
    def test_subgroup_universal(self):
        common={**CLASS_MEDIAL, 'ٮ':'بتث','ں':'ن','ى':'ي'}
        self.assertEqual(partition_order(common),4608)
    def test_positions(self): self.assertEqual(positions('كتب'),('initial','medial','final'))
    def test_skeleton(self): self.assertEqual(skeleton('كتب'),'كٮٮ')
    def test_count(self): self.assertEqual(degree('كتب'),15)
    def test_product(self): self.assertEqual(len(candidates('كتب')),15)
    def test_hartley(self): self.assertAlmostEqual(hartley('كتب'),math.log2(15))
    def test_lexical_vs_combinatorial(self): self.assertTrue(len(word_report('كتب')['lexical_seed_candidates'])<15)
    def test_katama_is_not_same_rasm(self): self.assertNotEqual(skeleton('كتب'),skeleton('كتم'))
    def test_katama_zone(self): self.assertTrue(phonetic_relation('ب','م')['same_zone'])
    def test_katama_point(self): self.assertTrue(phonetic_relation('ب','م')['same_point'])
    def test_fa_same_zone_but_not_point(self):
        self.assertTrue(phonetic_relation('ب','ف')['same_zone']);self.assertFalse(phonetic_relation('ب','ف')['same_point'])
    def test_qalqala_five(self): self.assertEqual(QALQALA,set('قطبجد'))
    def test_jahr_shiddah_six(self): self.assertEqual(JAHR&SHIDDAH,set('ءقطبجد'))
    def test_hamza_not_qalqala(self): self.assertNotIn('ء',QALQALA)
    def test_dotted_same(self): self.assertTrue(dotted_related('كتب','كبت'))
    def test_different_root(self): self.assertFalse(dotted_related('كتب','كتم'))
    def test_lattice_conflict(self): self.assertEqual(lattice_meet([{'ب'}],[{'ت'}]),[set()])
    def test_lattice_join(self): self.assertEqual(lattice_join([{'ب'}],[{'ت'}]),[{'ب','ت'}])
    def test_entropy_uniform(self): self.assertAlmostEqual(entropy([0.5,0.5]),1.0)
    def test_entropy_nonneutral(self): self.assertLess(entropy([.9,.1]),1.0)
    def test_quantum_string_content_address(self):
        q=QuantumString('كتب','كتم','same_articulation_point','ART','classical', 'proposed','')
        self.assertEqual(q.address(),q.address())
        self.assertFalse(q.executable())
    def test_verified_requires_reference(self):
        self.assertTrue(QuantumString('ب','م','same_point','ART','tajwid-point','verified','Arabic Timeless/Layer17').executable())
    def test_ta_marbuta_not_losslessly_folded(self):
        with self.assertRaises(ValueError):skeleton('كتبة')
    def test_hamza_not_silently_folded(self):
        with self.assertRaises(ValueError):skeleton('ء')
    def test_joint_features_do_not_mean_qalqala(self):self.assertEqual((JAHR&SHIDDAH)-QALQALA,{'ء'})

if __name__=='__main__':unittest.main(verbosity=2)
