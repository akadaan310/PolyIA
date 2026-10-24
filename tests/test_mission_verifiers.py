"""Mission acceptance checks use fresh execution, never submitted pass reports."""
import contextlib
import json
from pathlib import Path
import sqlite3
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from polyia.store import CommandError, Ledger


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('polyia/__init__.py', 'polyia/store.py', 'polyia/experiments.py',
           'polyia/mission_verifiers.py')


class MissionVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / 'workspace'
        self.workspace.mkdir()
        self.db = Path(self.temp.name) / 'state' / 'ledger.sqlite3'
        definitions = json.loads((ROOT / 'registry/constitution.json').read_text())['requirements']
        self.definitions = [r for r in definitions if r['id'] in ('PIA-042', 'PIA-040', 'PIA-041')]
        self.ledger = Ledger(self.db, self.workspace, self.definitions)
        self.addCleanup(lambda: self.ledger.close())
        self.counter = 0

    def command(self, kind, payload):
        self.counter += 1
        return self.ledger.command({'command_id': f'mission-{self.counter}',
            'expected_revision': self.ledger.state()['revision'], 'kind': kind, 'payload': payload})

    def candidate(self, requirement='PIA-042', omit=()):
        paths = []
        for name in SOURCES:
            if name in omit:
                continue
            target = self.workspace / name
            target.parent.mkdir(parents=True, exist_ok=True)
            original = ROOT / name
            target.write_bytes(original.read_bytes() if original.exists() else b'# adapter not implemented\n')
            paths.append(name)
        return self.command('requirement.produce', {'requirement_id': requirement, 'artifacts': paths})

    def verify(self, requirement='PIA-042'):
        return self.command('requirement.verify', {'requirement_id': requirement})['result']['verification']

    def test_real_capture_verifier_accepts_only_current_bound_production_and_reopens(self):
        produced = self.candidate()
        before = self.ledger.state()
        result = self.verify()
        self.assertEqual(result['outcome'], 'PASS', result)
        self.assertEqual(result['evidence_class'], 'SOFTWARE_CONFORMANCE')
        binding = result['mission_binding']
        self.assertEqual(binding['adapter'], 'PIA-042/capture-v1')
        self.assertEqual(binding['production_revision'], produced['revision'])
        self.assertEqual({m['identity']['module'] for m in binding['implementation']},
                         {'polyia', 'polyia.store', 'polyia.experiments', 'polyia.mission_verifiers'})
        self.assertGreaterEqual(len(result['report']['checks']), 10)
        self.assertTrue(all(c['pass'] is True for c in result['report']['checks']))
        after = self.ledger.state()
        self.assertEqual(before['guidance'], after['guidance'])
        self.assertEqual(before['runs'], after['runs'])
        self.assertEqual(before['requirements']['PIA-040'], after['requirements']['PIA-040'])
        self.command('requirement.accept', {'requirement_id': 'PIA-042'})
        accepted = self.ledger.state()
        self.assertEqual(accepted['requirements']['PIA-042']['status'], 'ACCEPTED')
        self.assertEqual(accepted['commission_status'], 'NOT_COMMISSIONED')
        self.ledger.close()
        with patch('polyia.mission_verifiers.prepare', side_effect=AssertionError('replay pinned live code')), \
             patch('polyia.mission_verifiers.run_capture_checks', side_effect=AssertionError('replay executed tests')):
            self.ledger = Ledger(self.db, self.workspace)
            self.assertEqual(self.ledger.state(), accepted)
            self.assertTrue(self.ledger.verify()['ok'])

    def test_unrelated_evidence_and_forged_report_are_refused(self):
        for name, content in [('note.txt', b'just notes'),
                              ('report.json', b'{"status":"PASS","checks":[{"pass":true}]}')]:
            with self.subTest(name=name):
                (self.workspace / name).write_bytes(content)
                self.command('requirement.produce', {'requirement_id':'PIA-042', 'artifacts':[name]})
                result = self.verify()
                self.assertEqual(result['outcome'], 'FAIL', result)
                self.assertEqual(result['report']['reason'], 'MISSION_INPUT_MISMATCH')

    def test_missing_dependency_and_extra_forged_descriptor_are_refused(self):
        self.candidate(omit=('polyia/experiments.py',))
        self.assertEqual(self.verify()['outcome'], 'FAIL')
        self.candidate()
        (self.workspace / 'descriptor.json').write_text('{"requirement_id":"PIA-042","pass":true}')
        self.command('requirement.produce', {'requirement_id':'PIA-042', 'artifacts':list(SOURCES)+['descriptor.json']})
        self.assertEqual(self.verify()['outcome'], 'FAIL')

    def test_changed_captured_source_is_not_the_running_implementation(self):
        self.candidate()
        (self.workspace / 'polyia/store.py').write_bytes(b'# unrelated source replacement\n')
        self.command('requirement.produce', {'requirement_id':'PIA-042', 'artifacts':list(SOURCES)})
        result = self.verify()
        self.assertEqual(result['outcome'], 'FAIL', result)
        self.assertEqual(result['report']['reason'], 'MISSION_INPUT_MISMATCH')

    def test_workspace_drift_keeps_historical_candidate_and_reproduction_invalidates(self):
        self.candidate()
        (self.workspace / 'polyia/store.py').write_bytes(b'changed workspace only')
        self.assertEqual(self.verify()['outcome'], 'PASS')
        self.command('requirement.accept', {'requirement_id':'PIA-042'})
        self.assertGreater(self.ledger.verify()['workspace_drift']['changed'], 0)
        self.command('requirement.produce', {'requirement_id':'PIA-042', 'artifacts':list(SOURCES)})
        with self.assertRaises(CommandError) as error:
            self.command('requirement.accept', {'requirement_id':'PIA-042'})
        self.assertEqual(error.exception.code, 'INVALID_TRANSITION')

    def test_other_mission_remains_unsupported(self):
        self.candidate('PIA-041')
        self.assertEqual(self.verify('PIA-041')['outcome'], 'UNSUPPORTED')

    def test_guidance_adapter_proves_actual_effects_and_retains_every_applicability_record(self):
        self.candidate('PIA-040')
        before = self.ledger.state()
        result = self.verify('PIA-040')
        self.assertEqual(result['outcome'], 'PASS', result)
        self.assertEqual(result['mission_binding']['adapter'], 'PIA-040/guidance-effects-v1')
        contract = json.loads(self.ledger.get_blob(result['mission_binding']['contract']['sha256']))
        applicability = contract['inherited_applicability']
        self.assertEqual(applicability['core'], [])
        self.assertEqual(len(applicability['supplemental']), 75)
        self.assertEqual({r['origin_id'] for r in applicability['supplemental']},
                         {r['origin_id'] for r in applicability['decisions']})
        self.assertTrue(all(r['rationale'] and r['classification'] for r in applicability['decisions']))
        after = self.ledger.state()
        self.assertEqual(before['guidance'], after['guidance'])
        self.assertEqual(before['research'], after['research'])
        self.assertEqual(before['runs'], after['runs'])
        self.command('requirement.accept', {'requirement_id':'PIA-040'})
        accepted = self.ledger.state()
        self.ledger.close()
        with patch('polyia.mission_verifiers.prepare', side_effect=AssertionError('Replay pinned live source')), \
             patch('polyia.mission_verifiers.run_guidance_checks', side_effect=AssertionError('Replay ran guidance fixtures')):
            self.ledger = Ledger(self.db, self.workspace)
            self.assertEqual(self.ledger.state(), accepted)
            self.assertTrue(self.ledger.verify()['ok'])
        self.assertEqual(accepted['commission_status'], 'NOT_COMMISSIONED')

    def test_verifier_payload_cannot_supply_descriptor_or_outcome(self):
        self.candidate()
        with self.assertRaises(CommandError) as error:
            self.command('requirement.verify', {'requirement_id':'PIA-042', 'outcome':'PASS'})
        self.assertEqual(error.exception.code, 'INVALID_PAYLOAD')

    def test_captured_binding_blob_corruption_blocks_acceptance_and_reopen(self):
        self.candidate()
        result = self.verify()
        self.assertEqual(result['outcome'], 'PASS', result)
        digest = result['mission_binding']['contract']['sha256']
        with contextlib.closing(sqlite3.connect(self.db)) as conn:
            with conn:
                conn.execute('UPDATE blobs SET data=? WHERE digest=?', (b'corrupt contract', digest))
        with self.assertRaises(CommandError) as error:
            self.command('requirement.accept', {'requirement_id':'PIA-042'})
        self.assertEqual(error.exception.code, 'INTEGRITY_ERROR')
        self.ledger.close()
        with self.assertRaises(CommandError):
            Ledger(self.db, self.workspace)

    def test_loaded_runner_or_store_policy_replacement_cannot_forge_success(self):
        from polyia import mission_verifiers, store
        self.candidate()
        with patch.object(mission_verifiers, 'run_capture_checks', return_value={
                'status':'PASS', 'checks':[{'name':'fabricated', 'pass':True}]}):
            result = self.verify()
            self.assertEqual(result['outcome'], 'ERROR', result)
            self.assertEqual(result['report']['reason'], 'IMPLEMENTATION_CHANGED')
        with patch.object(store, 'MAX_ARTIFACT_BYTES', store.MAX_ARTIFACT_BYTES + 1):
            result = self.verify()
            self.assertEqual(result['outcome'], 'ERROR', result)
            self.assertEqual(result['report']['reason'], 'IMPLEMENTATION_CHANGED')

    def test_undeclared_loaded_class_hook_is_not_part_of_the_bound_implementation(self):
        self.candidate()
        with patch.object(Ledger, '__getattribute__', object.__getattribute__):
            result = self.verify()
            self.assertEqual(result['outcome'], 'ERROR', result)
            self.assertEqual(result['report']['reason'], 'IMPLEMENTATION_CHANGED')

    def test_contextmanager_wrapper_must_match_the_actual_standard_wrapper(self):
        self.candidate()
        original = Ledger._transaction

        def make_forwarder(target):
            def forwarding(*args, **kwargs):
                return target(*args, **kwargs)
            return forwarding

        forwarding = make_forwarder(original)
        replaced = types.FunctionType(forwarding.__code__, vars(contextlib), closure=forwarding.__closure__)
        replaced.__module__ = original.__module__
        replaced.__wrapped__ = original.__wrapped__
        with patch.object(Ledger, '_transaction', replaced):
            result = self.verify()
            self.assertEqual(result['outcome'], 'ERROR', result)
            self.assertEqual(result['report']['reason'], 'IMPLEMENTATION_CHANGED')

    def isolated(self, action, source_change=None, requirement='PIA-042'):
        root = Path(self.temp.name) / ('installed-' + str(self.counter))
        root.mkdir()
        shutil.copytree(ROOT / 'polyia', root / 'polyia', ignore=shutil.ignore_patterns('__pycache__'))
        (root / 'registry').mkdir()
        for name in ('constitution.json', 'acceptance.json', 'inherited_obligations.json', 'inherited_supplemental.json'):
            shutil.copyfile(ROOT / 'registry' / name, root / 'registry' / name)
        if requirement == 'PIA-040':
            records = json.loads((ROOT / 'registry/inherited_supplemental.json').read_text())['records']
            for path in {r['source_path'] for r in records if 'PIA-040' in r['target_obligations']}:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
        if source_change:
            path = root / 'polyia/store.py'
            text = path.read_text()
            self.assertIn(source_change[0], text)
            path.write_text(text.replace(*source_change))
        script = '''
import json,sys
from pathlib import Path
sys.path.insert(0,ROOT)
from polyia import store, mission_verifiers
base=Path(ROOT)
workspace=base/'candidate'
workspace.mkdir()
definitions=[r for r in json.loads((base/'registry/constitution.json').read_text())['requirements'] if r['id']=='PIA-042']
ledger=store.Ledger(base/'data/ledger.sqlite3',workspace,definitions)
counter=0
def command(kind,payload):
 global counter
 counter+=1
 return ledger.command({'command_id':'isolate-'+str(counter),'expected_revision':ledger.state()['revision'],'kind':kind,'payload':payload})
paths=[]
for module,path in mission_verifiers.MODULES:
 target=workspace/path
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_bytes((base/path).read_bytes())
 paths.append(path)
command('requirement.produce',{'requirement_id':'PIA-042','artifacts':paths})
ACTION
ledger.close()
'''.replace('ROOT', repr(str(root))).replace('ACTION', action).replace("'PIA-042'", repr(requirement))
        process = subprocess.run([sys.executable, '-I', '-B', '-c', script], capture_output=True,
                                 text=True, timeout=30, env={'PATH': os.defpath}, cwd=root)
        self.assertEqual(process.returncode, 0, process.stderr)
        return json.loads(process.stdout)

    def test_changed_or_missing_installed_dependency_blocks_acceptance(self):
        for mutation in ["(base/'polyia/store.py').write_bytes((base/'polyia/store.py').read_bytes()+b'\\n# changed installed candidate\\n')",
                         "(base/'polyia/experiments.py').unlink()"]:
            self.counter += 1
            result = self.isolated('''
verification=command('requirement.verify',{'requirement_id':'PIA-042'})['result']['verification']
assert verification['outcome']=='PASS',verification
MUTATION
try:
 command('requirement.accept',{'requirement_id':'PIA-042'})
except store.CommandError as error:
 print(json.dumps({'refused':True,'reason':error.code}))
else:
 print(json.dumps({'refused':False}))
'''.replace('MUTATION', mutation))
            self.assertTrue(result['refused'], result)

    def test_changed_acceptance_or_applicability_contract_blocks_acceptance(self):
        for name in ('acceptance.json', 'inherited_obligations.json', 'inherited_supplemental.json'):
            self.counter += 1
            result = self.isolated('''
verification=command('requirement.verify',{'requirement_id':'PIA-042'})['result']['verification']
assert verification['outcome']=='PASS',verification
path=base/'registry'/NAME
path.write_bytes(path.read_bytes()+b'\\n')
try:
 command('requirement.accept',{'requirement_id':'PIA-042'})
except store.CommandError as error:
 print(json.dumps({'refused':True,'reason':error.code}))
else:
 print(json.dumps({'refused':False}))
'''.replace('NAME', repr(name)))
            self.assertEqual(result, {'refused':True,'reason':'MISSION_CONTRACT_CHANGED'})

    def test_coherent_but_broken_capture_implementation_fails_actual_fixture(self):
        result = self.isolated("print(json.dumps(command('requirement.verify',{'requirement_id':'PIA-042'})['result']['verification']))",
            ('status="UNCHANGED" if actual == artifact["sha256"] else "MODIFIED"', 'status="UNCHANGED"'))
        self.assertEqual(result['outcome'], 'FAIL', result)
        self.assertTrue(any(c['name']=='workspace_edit_is_drift_not_changed_evidence' and c['pass'] is False
                            for c in result['report']['checks']))

    def test_guidance_driver_detects_coherent_missing_acknowledgement_and_pause_guards(self):
        cases = [('if guidance["status"] != "ACKNOWLEDGED":', 'if False:', 'unacknowledged_cannot_apply'),
                 ('if state["research"]["paused"]:', 'if False:', 'pause_blocks_real_registered_work')]
        for original, broken, expected in cases:
            with self.subTest(expected=expected):
                self.counter += 1
                result = self.isolated("print(json.dumps(command('requirement.verify',{'requirement_id':'PIA-042'})['result']['verification']))",
                                       (original, broken), requirement='PIA-040')
                self.assertEqual(result['outcome'], 'FAIL', result)
                self.assertTrue(any(c['name'] == expected and c['pass'] is False for c in result['report']['checks']))

    def test_changed_inherited_source_blocks_guidance_verification(self):
        result = self.isolated('''
path=base/'sources/expanded/PHONEX_ULWS/ULWS_PHONEX_QIA_v0.1/CODEX_GOD_SEED.md'
path.write_bytes(path.read_bytes()+b'\\nchanged inherited source\\n')
print(json.dumps(command('requirement.verify',{'requirement_id':'PIA-042'})['result']['verification']))
''', requirement='PIA-040')
        self.assertEqual(result['outcome'], 'FAIL', result)
        self.assertEqual(result['report']['reason'], 'MISSION_CONTRACT_CHANGED')

    def test_guidance_reproduction_does_not_inherit_prior_acceptance(self):
        self.candidate('PIA-040')
        self.assertEqual(self.verify('PIA-040')['outcome'], 'PASS')
        self.command('requirement.accept', {'requirement_id':'PIA-040'})
        self.candidate('PIA-040')
        with self.assertRaises(CommandError) as error:
            self.command('requirement.accept', {'requirement_id':'PIA-040'})
        self.assertEqual(error.exception.code, 'INVALID_TRANSITION')


if __name__ == '__main__':
    unittest.main()
