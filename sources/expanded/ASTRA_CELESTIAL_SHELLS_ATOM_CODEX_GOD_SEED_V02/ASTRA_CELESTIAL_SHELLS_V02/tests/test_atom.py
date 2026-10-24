import copy,json,tempfile,unittest
from pathlib import Path
from atom.core import Universe,AtomError,digest,PHASES
class AtomTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.u=Universe(Path(self.tmp.name))
    def _run(self,name,kind,p=None):
        self.u.register(name,kind);r=[]
        for i in range(6):r.append(self.u.advance(name if i==0 else None,p if i==0 else None))
        return r
    def test_sequence(self):
        r=self._run('flight','journey',{'destination':'Mars'})
        self.assertEqual([x['phase'] for x in r],list(PHASES[1:]));self.assertEqual(self.u.verify()['checkpoints'],1)
    def test_lock_is_immutable(self):
        self._run('flight','journey');before=self.u.state()['last_checkpoint'];path=self.u.checkpoints/(before+'.json');data=path.read_bytes();
        self.u.advance();self.u.register('visual','render');[self.u.advance('visual' if i==0 else None) for i in range(6)]
        self.assertEqual(data,path.read_bytes());self.assertEqual(self.u.verify()['checkpoints'],2)
    def test_old_cp_tamper(self):
        self._run('flight','journey');p=self.u.checkpoints/(self.u.state()['last_checkpoint']+'.json');p.write_text('{}');
        with self.assertRaises(AtomError):self.u.verify()
    def test_bad_receipt(self):
        self._run('flight','journey');p=self.u.events;p.write_text(p.read_text().replace('REGISTER','CORRUPTED',1))
        with self.assertRaises(AtomError):self.u.verify()
    def test_unsupported_journey(self):
        self.u.register('journey','journey');self.u.advance('journey',{'destination':'Andromeda'});self.u.advance();
        with self.assertRaises(AtomError):self.u.advance()
        self.assertEqual(self.u.state()['phase'],'ADMIT')
    def test_plates(self):
        self._run('visual','render',{'plates':['plasma','hud'],'depth':[.2,.9]});self.assertEqual(self.u.state()['results'][-1]['output']['plates'][0]['name'],'plasma')
    def test_bad_plate(self):
        self.u.register('visual','render');self.u.advance('visual',{'plates':['plasma','plasma'],'depth':[.2,.9]});self.u.advance()
        with self.assertRaises(AtomError):self.u.advance()
    def test_no_real_gaze(self):
        self.u.register('gaze','focus');self.u.advance('gaze',{'mode':'eye-tracking'});self.u.advance()
        with self.assertRaises(AtomError):self.u.advance()
    def test_focus_sim(self):
        self._run('gaze','focus',{'x':.25,'y':.4});self.assertFalse(self.u.state()['results'][-1]['output']['is_eye_tracking'])
    def test_economy(self):
        self._run('credits','economy',{'grant':8});self.assertEqual(self.u.state()['credits'],8)
    def test_bad_economy(self):
        self.u.register('credits','economy');self.u.advance('credits',{'grant':100000});self.u.advance()
        with self.assertRaises(AtomError):self.u.advance()
    def test_science(self):
        self._run('spectra','science');self.assertFalse(self.u.state()['results'][-1]['output']['measured'])
    def test_evidence(self):
        self._run('artifact','evidence',{'content':'hello'});self.assertEqual(len(self.u.state()['results'][-1]['output']['sha256']),64)
    def test_policy(self):self.assertEqual(self.u.choose()['action'],'VERIFY')
    def test_cannot_skip_checkpoint(self):
        self.u.register('a','render');self.u.advance('a');self.assertEqual(self.u.verify()['checkpoints'],0)
    def test_prohibit_duplicate(self):
        self.u.register('a','render');
        with self.assertRaises(AtomError):self.u.register('a','render')
    def test_model_no_executables(self):self.assertFalse(self.u.protocol()['llm_required'])
    def test_resume_requires_hold(self):
        self._run('a','render');
        with self.assertRaises(AtomError):self.u.register('b','focus')
    def test_report_verifies(self):self.assertTrue(self.u.report()['verification']['verified'])
    def test_source_archive_locked_against_later_change(self):
        from pathlib import Path
        project=Path(self.tmp.name)
        self.u=Universe(project/'.atom-state')
        (project/'web').mkdir();(project/'web'/'app.js').write_text('version one')
        self._run('a','render')
        cp=self.u.state()['last_checkpoint'];snap=json.loads((self.u.checkpoints/(cp+'.json')).read_text())
        key=snap['source_archive']['web/app.js']['sha256'];self.assertEqual((self.u.objects/key).read_text(),'version one')
        (project/'web'/'app.js').write_text('version two')
        self.assertTrue(self.u.verify()['verified'])
        (self.u.objects/key).write_text('malicious modification')
        with self.assertRaises(AtomError):self.u.verify()

    def test_parent_checkpoint(self):
        self._run('a','render');a=self.u.state()['last_checkpoint'];self.u.advance();self._run('b','journey');b=self.u.state()['last_checkpoint'];self.assertEqual(json.loads((self.u.checkpoints/(b+'.json')).read_text())['parent'],a)

if __name__=='__main__':unittest.main()

class DriverTests(unittest.TestCase):
    def test_headless_safe_plan(self):
        from atom.driver import execute
        with tempfile.TemporaryDirectory() as d:
            universe=Universe(Path(d)/'.state')
            plan={'protocol':'ATOM-PLAN/0.1','steps':[{'atom':'a','kind':'render','params':{}},{'atom':'b','kind':'economy','params':{'grant':3}}]}
            dry=execute(universe,plan,True)
            self.assertEqual(universe.state()['tick'],0)
            self.assertTrue(dry['dry_run'])
            result=execute(universe,plan,False)
            self.assertEqual(result['executed'],2)
            self.assertEqual(universe.state()['credits'],3)
            self.assertEqual(universe.verify()['checkpoints'],2)
    def test_reject_unknown_step(self):
        from atom.driver import validate_plan
        with self.assertRaises(AtomError):validate_plan({'protocol':'ATOM-PLAN/0.1','steps':[{'atom':'a','kind':'shell','params':{}}]})
