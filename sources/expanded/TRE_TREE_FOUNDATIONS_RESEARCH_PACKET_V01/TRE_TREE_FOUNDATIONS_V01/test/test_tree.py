import unittest
from tre.core import TreeMachine, Rejection, run_fixture, digest

class TREEChecks(unittest.TestCase):
    def test_two_trees_share_trunk(self):
        m=TreeMachine(); self.assertEqual(m.nodes['r0'].kind,'root');self.assertEqual(m.nodes['s0'].kind,'shoot');self.assertEqual(m.nodes['r0'].parent,'t0')
    def test_bifurcation_and_coupling(self):
        a=run_fixture(); ns=a['state']['nodes'];s=next(x for x in ns if x['id']=='s2');self.assertEqual(sum(1 for n in ns if n['parent']=='s2'),2);self.assertEqual(len(a['state']['couplings']),3)
    def test_identical_seed_replay(self):
        self.assertEqual(run_fixture(),run_fixture())
    def test_different_seed_changes_commit_not_topology(self):
        x,y=run_fixture('A'),run_fixture('B');self.assertNotEqual(x['topology']['content_id'],y['topology']['content_id']);self.assertEqual(x['topology']['children'],y['topology']['children'])
    def test_negative_unknown_kind(self):
        m=TreeMachine();before=m.content_id()
        with self.assertRaises(Rejection):m.grow('teleport','s0')
        self.assertEqual(m.content_id(),before)
    def test_parent_type(self):
        m=TreeMachine()
        with self.assertRaises(Rejection):m.grow('leaf','r0',provider='r0')
    def test_no_leaf_without_root_witness(self):
        m=TreeMachine()
        with self.assertRaises(Rejection):m.grow('leaf','s0')
    def test_no_fake_provider(self):
        m=TreeMachine()
        with self.assertRaises(Rejection):m.grow('leaf','s0',provider='s0')
    def test_stale_version(self):
        m=TreeMachine();m.grow('root','r0')
        with self.assertRaises(Rejection):m.grow('root','r0',expected_version=0)
    def test_budget(self):
        m=TreeMachine(carbon=0,water=0)
        with self.assertRaises(Rejection):m.grow('root','r0')
    def test_resource_conservation(self):
        x=run_fixture()['state']['resources'];self.assertEqual(x['carbon']+x['used_carbon'],x['total_carbon_in']);self.assertEqual(x['water']+x['used_water'],x['total_water_in'])
    def test_no_fruit_without_leaf(self):
        m=TreeMachine()
        with self.assertRaises(Rejection):m.grow('fruit','s0',provider='r0')
    def test_hash_domain_separation(self):
        self.assertNotEqual(digest('A',{'x':1}),digest('B',{'x':1}))
    def test_no_zero_absorption(self):
        m=TreeMachine();before=m.content_id()
        with self.assertRaises(Rejection):m.absorb('r0',0)
        self.assertEqual(m.content_id(),before)
    def test_invalid_resources(self):
        with self.assertRaises(Rejection):TreeMachine(carbon=-1)
    def test_original_immutable_node(self):
        m=TreeMachine()
        with self.assertRaises(Exception):m.nodes['r0'].id='altered'
    def test_leaf_above_ground(self):
        m=TreeMachine();l=m.grow('leaf','s0',provider='r0');self.assertGreater(l.xyz[2],0)
    def test_root_below_ground(self):
        m=TreeMachine();r=m.grow('root','r0');self.assertLess(r.xyz[2],0)
    def test_event_hash_chain(self):
        x=run_fixture()['events'];self.assertEqual([e['version'] for e in x],list(range(1,len(x)+1)))
        for a,b in zip(x,x[1:]):self.assertEqual(a['after'],b['before'])
    def test_event_hash_matches_final_state(self):
        x=run_fixture();self.assertEqual(x['events'][-1]['after'],x['topology']['content_id'])
    def test_revision_conflict_for_assimilation(self):
        m=TreeMachine();m.grow('root','r0')
        with self.assertRaises(Rejection):m.absorb('r0',1,expected_version=0)
    def test_unrecognized_type_admission(self):
        m=TreeMachine()
        with self.assertRaises(Rejection):m.grow('leaf','s0',provider='nonexistent')
    def test_canonical_encoding_independent_of_dict_insertion(self):
        self.assertEqual(digest('TREE',{'a':1,'b':2}),digest('TREE',{'b':2,'a':1}))

if __name__=='__main__': unittest.main()
