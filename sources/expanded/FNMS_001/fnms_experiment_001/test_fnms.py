import unittest
from fnms import build_graph, inspect_molecule, run
class FNMS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=build_graph()
        cls.o=run()
    def test_typed_nodes(self): self.assertEqual(len(self.g.nodes),25)
    def test_latins_are_not_chemicals(self):
        self.assertIsNone(self.g.walk('latin_phrase','iupac',frozenset({'translated_as','also_named','denotes_structure'})))
    def test_phrase_has_morphological_components(self):
        self.assertEqual(self.g.targets('brand','parses_to'),['head','pain','reliever'])
    def test_latin_phrase_expresses_intent(self):
        self.assertEqual(self.g.targets('latin_phrase','expresses'),['intention'])
    def test_semantic_inverse_not_unique(self): self.assertEqual(len(self.o['semantic_candidate_set']),3)
    def test_syntactic_brand_has_no_automatic_identity(self):
        self.assertIsNone(self.g.walk('brand','acetaminophen',frozenset({'translated_as','parses_to','expresses'})))
    def test_semantic_path_requires_evidence(self):
        e=self.o['semantic_witness']; self.assertEqual([r['op'] for r in e],['expresses','targets_effect','supported_by'])
    def test_identity_assignment_carries_stipulation(self):
        e=self.o['asserted_identity_witness']; self.assertEqual(e[0]['status'],'stipulated')
    def test_formula(self): self.assertEqual(self.o['chemical_validation']['formula'],'C8H9NO2')
    def test_functional_groups(self):
        c=self.o['chemical_validation']; self.assertEqual(c['phenol_matches'],1); self.assertEqual(c['amide_matches'],1)
    def test_benzene_ring(self): self.assertEqual(self.o['chemical_validation']['aromatic_six_rings'],1)
    def test_para(self): self.assertEqual(self.o['chemical_validation']['regiochemistry'][0]['relative_position'],'para')
    def test_group_decomposition(self): self.assertEqual(self.g.targets('structure','has_component'),['amide','benzene','para','phenol'])
    def test_antonym_polarity_requires_same_dimension(self):
        self.assertEqual(self.g.targets('intention','has_polarity'),['relief'])
        self.assertEqual(self.g.targets('negative_intention','has_polarity'),['aggravation'])
    def test_formula_collides_under_ring_position(self):
        para=inspect_molecule('CC(=O)Nc1ccc(O)cc1')
        meta=inspect_molecule('CC(=O)Nc1cccc(O)c1')
        ortho=inspect_molecule('CC(=O)Nc1ccccc1O')
        self.assertEqual(len({para['formula'],meta['formula'],ortho['formula']}),1)
        self.assertEqual({x['regiochemistry'][0]['relative_position'] for x in (para,meta,ortho)}, {'ortho','meta','para'})
    def test_functional_groups_do_not_specify_regiochemistry(self):
        meta=inspect_molecule('CC(=O)Nc1cccc(O)c1')
        self.assertEqual((meta['phenol_matches'],meta['amide_matches']),(1,1))
        self.assertNotEqual(meta['regiochemistry'][0]['relative_position'],'para')
    def test_unsupported_path_removed_by_evidence_ablation(self):
        g=build_graph()
        g.edges=[e for e in g.edges if e.op != 'supported_by']
        self.assertIsNone(g.walk('brand','acetaminophen',frozenset({'expresses','targets_effect','supported_by'})))
        self.assertEqual(len(g.walk('brand','acetaminophen',frozenset({'asserted_active'}))),1)
    def test_asserted_identity_removed_by_ablation(self):
        g=build_graph()
        g.edges=[e for e in g.edges if e.op != 'asserted_active']
        self.assertIsNone(g.walk('brand','acetaminophen',frozenset({'asserted_active'})))
        self.assertIsNotNone(g.walk('brand','acetaminophen',frozenset({'expresses','targets_effect','supported_by'})))
    def test_illegal_type_bridge_refused(self):
        with self.assertRaises(AssertionError): self.g.edge('latin_head','denotes_structure','structure','fake','no evidence')
if __name__=='__main__': unittest.main(verbosity=2)
