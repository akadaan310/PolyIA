import tempfile,unittest,hashlib,json
from pathlib import Path
from polyia.lang import parse,canonical,compile_commission,CompileError
from polyia.compiler import compose,CompositionError
from polyia.registry import ATOMS,Atom
from polyia.automaton import make_artifact,to_dot,to_html
from polyia.harness import init,load,advance,verify,HarnessError,STAGES,EVIDENCE

SRC='''(commission (task "topology") (require "phonetic-prefix") (require "composed-automaton") (deny "invent-cognates") (evidence fixture) (budget 32))'''
class TestLang(unittest.TestCase):
 def test_roundtrip(self):self.assertEqual(canonical(parse(canonical(parse(SRC)))),canonical(parse(SRC)))
 def test_token(self):self.assertIn('topology',canonical(parse(SRC)))
 def test_extra(self):
  with self.assertRaises(CompileError):parse(SRC+'()')
 def test_bad_operator(self):
  with self.assertRaises(CompileError):compile_commission('(commission (task "x") (run "secret") (require "phonetic-prefix"))')
 def test_required(self):
  with self.assertRaises(CompileError):compile_commission('(commission (task "x"))')
 def test_budget(self):
  with self.assertRaises(CompileError):compile_commission('(commission (task "x") (require "phonetic-prefix") (budget 0))')
 def test_comment(self):self.assertEqual(compile_commission(';hi\n'+SRC).task,'topology')
 def test_unknown_escape(self):
  with self.assertRaises(CompileError):parse('(x "\\t")')
 def test_deep(self):
  with self.assertRaises(CompileError):parse('('*42+'x'+')'*42)
class TestCompose(unittest.TestCase):
 def setUp(self):self.c=compile_commission(SRC)
 def test_order(self):
  p=compose(self.c)
  self.assertEqual(p.steps[0].id,'text.surface@0.1')
  self.assertEqual(p.steps[-1].id,'automaton.package@0.1')
 def test_determinism(self):self.assertEqual(compose(self.c).digest,compose(self.c).digest)
 def test_no_extra(self):self.assertTrue(all(not a.effects for a in compose(self.c).steps))
 def test_unknown(self):
  with self.assertRaises(CompositionError):compose(compile_commission(SRC.replace('phonetic-prefix','unknown-capability')))
 def test_attested_refusal(self):
  with self.assertRaisesRegex(CompositionError,'attested'):
   compose(compile_commission(SRC.replace('(evidence fixture)','(evidence attested)')))
 def test_deny_guard(self):
  with self.assertRaisesRegex(CompositionError,'deny'):
   compose(compile_commission(SRC.replace('(deny "invent-cognates")','')))
 def test_budget_refusal(self):
  with self.assertRaisesRegex(CompositionError,'budget'):
   compose(compile_commission(SRC.replace('(budget 32)','(budget 2)')))
 def test_ambiguous_provider(self):
  plus=Atom('more.phonetic@0.1',('PhoneFeatures',),('PhoneticMatches',),('phonetic-prefix',))
  with self.assertRaisesRegex(CompositionError,'one provider'):compose(self.c,available=ATOMS+(plus,))
 def test_missing(self):
  with self.assertRaisesRegex(CompositionError,'one provider'):compose(self.c,available=tuple(a for a in ATOMS if a.id!='text.surface@0.1'))
 def test_cycle(self):
  replacement=Atom('loop.surface@0.1',('StateArtifact',),('Surface',),('surface',))
  arr=tuple(a for a in ATOMS if a.id!='text.surface@0.1')+(replacement,)
  with self.assertRaisesRegex(CompositionError,'cycle'):compose(self.c,available=arr)
 def test_artifact(self):
  a=make_artifact(self.c,compose(self.c))
  self.assertEqual(a['format'],'POLYIA-AUTOMATON/0.1')
  self.assertIsNone(a['observed_results'])
  self.assertEqual(a['transitions'][-1]['to'],'ACCEPT')
  self.assertIn('digraph',to_dot(a));self.assertIn('Fixture only',to_html(a))
 def test_json(self):json.dumps(make_artifact(self.c,compose(self.c)),ensure_ascii=False)
class TestHarness(unittest.TestCase):
 def test_initial(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);init(d);self.assertTrue(verify(d));self.assertEqual(load(d)['stage'],'PREFLIGHT')
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);init(d)
   with self.assertRaises(HarnessError):init(d)
 def test_gate_refuses(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);init(d)
   with self.assertRaises(HarnessError):advance(d,{'kind':'environment-audit','passed':False,'sha256':'a'*64})
 def test_valid_advance(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);init(d);new=advance(d,{'kind':'environment-audit','passed':True,'sha256':'a'*64})
   self.assertEqual(new['stage'],'INVENTORY');self.assertTrue(verify(d))
 def test_chain_tampering(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);init(d);advance(d,{'kind':'environment-audit','passed':True,'sha256':'a'*64})
   x=load(d);x['events'][0]['receipt']['kind']='falsified';(d/'harness_state.json').write_text(json.dumps(x))
   self.assertFalse(verify(d))
 def test_malformed_hash(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);init(d)
   with self.assertRaises(HarnessError):advance(d,{'kind':'environment-audit','passed':True,'sha256':'not-real'})
 def test_all_gates(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);init(d)
   for kind in EVIDENCE:advance(d,{'kind':kind,'passed':True,'sha256':'a'*64})
   self.assertEqual(load(d)['stage'],'RELEASE_CANDIDATE');self.assertTrue(verify(d))
   with self.assertRaises(HarnessError):advance(d,{'kind':'any','passed':True,'sha256':'a'*64})
if __name__=='__main__':unittest.main()
