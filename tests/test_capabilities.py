"""Real journal/capture tests for the registered bounded capability extension."""
import copy
import types
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from polyia.store import Ledger, CommandError, CONTEXT_CODE

SOURCE = '(commission (profile "polyia.native/0.1") (emit result (add 1/3 1/6)))'
ASTRA = {'adapter_version': 'POLYIA-ASTRA/0.1', 'source_version': 'ASTRA/0.2',
         'protocol': 'ATOM-HANDOFF/0.1', 'operation': 'atom.initialize'}


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root/'workspace'
        self.workspace.mkdir()
        self.db = self.root/'state'/'ledger.sqlite3'
        self.ledger = Ledger(self.db, self.workspace, [{'id':'MISSION','title':'Open mission','verifier':'commission-evidence'}])
        self.addCleanup(lambda: self.ledger.close())
        self.counter = 0

    def request(self, name, parameters):
        self.counter += 1
        return {'command_id': f'cap-{self.counter}', 'expected_revision': self.ledger.state()['revision'],
                'kind':'experiment.run','payload':{'name':name,'parameters':parameters}}

    def run_capability(self, name, parameters):
        return self.ledger.command(self.request(name, parameters))['result']['run']

    def test_three_new_handlers_execute_with_exact_dependency_source_custody(self):
        expected = {'native': {'polyia.capabilities','polyia.native'},
                    'intake': {'polyia.capabilities','polyia.intake','polyia.experiments','polyia.native'},
                    'astra': {'polyia.capabilities','polyia.astra'}}
        cases = [('native', {'source':SOURCE}), ('intake', {'text':'teach polynomial division'}), ('astra',ASTRA)]
        for name, parameters in cases:
            with self.subTest(name=name):
                run = self.run_capability(name, parameters)
                self.assertEqual(run['report']['status'], 'PASS', run['report'])
                self.assertTrue(all(c['pass'] for c in run['report']['checks']))
                bundle = run['execution_bundle']
                self.assertEqual(bundle['status'], 'PINNED')
                self.assertEqual({m['identity']['module'] for m in bundle['modules']}, expected[name])
                for module in bundle['modules']:
                    identity, artifact = module['identity'], module['source']
                    captured = self.ledger.get_blob(artifact['sha256'])
                    self.assertEqual(hashlib.sha256(captured).hexdigest(), identity['sha256'])
                    installed = Path(__file__).resolve().parents[1]/artifact['path']
                    self.assertEqual(captured, installed.read_bytes())
                    self.assertEqual(identity['source_binding'], 'PINNED_SOURCE_MATCHES_LOADED_CODE')
                self.assertTrue(self.ledger.verify()['ok'])
        self.assertEqual(self.ledger.state()['commission_status'], 'NOT_COMMISSIONED')
        self.assertEqual(self.ledger.state()['requirements']['MISSION']['status'], 'NOT_STARTED')
        self.assertEqual(self.ledger.state()['runs'][0]['report']['result']['execution']['outputs']['result']['value'], '1/2')

    def test_reopen_retry_and_replay_never_call_handlers_or_live_pinning(self):
        request = self.request('native', {'source': SOURCE})
        receipt = self.ledger.command(request)
        self.ledger.checkpoint('native evidence checkpoint')
        before = self.ledger.state()
        self.ledger.close()
        with patch('polyia.native.execute_program', side_effect=AssertionError('replay executed native')), \
             patch('polyia.store._pinned_module', side_effect=AssertionError('replay read live code')):
            self.ledger = Ledger(self.db, self.workspace)
            self.assertEqual(self.ledger.state(), before)
            self.assertEqual(self.ledger.command(request), receipt)
            self.assertTrue(self.ledger.verify()['ok'])

    def test_existing_seed_run_and_context_census_remain_unchanged(self):
        old = self.run_capability('polynomial', {})
        self.assertEqual(old['report']['status'], 'PASS')
        self.assertNotIn('execution_bundle', old)
        self.assertEqual({path for _,path,_ in CONTEXT_CODE}, {
            'polyia/__init__.py','polyia/store.py','polyia/experiments.py',
            'polyia/cli.py','polyia/server.py','polyia/__main__.py'})
        genesis = self.ledger.state()['source_context']
        self.run_capability('native', {'source':SOURCE})
        self.assertEqual(self.ledger.state()['source_context'], genesis)
        self.assertTrue(self.ledger.verify()['ok'])

    def test_long_source_exception_does_not_relax_legacy_or_nested_parameters(self):
        text = 'teach polynomial division\n' + 'a'*3000
        run = self.run_capability('intake', {'text':text})
        self.assertEqual(run['report']['status'], 'INCONCLUSIVE')
        source = SOURCE + '\n;' + 'a'*3000
        self.assertEqual(self.run_capability('native', {'source':source})['report']['status'], 'PASS')
        for name, params in [('polynomial', {'a':'a'*3000}), ('intake', {'title':'a'*3000,'text':'x'}),
                             ('native',{'source':'a'*16385}), ('native',{'source':'é'*8193}),
                             ('native',{'nested':{'source':'a'*3000}})]:
            with self.subTest(name=name, keys=list(params)):
                with self.assertRaises(CommandError) as error:
                    self.ledger.command(self.request(name,params))
                self.assertEqual(error.exception.code, 'RESOURCE_LIMIT')

    def test_pause_and_revision_guards_precede_new_handler_execution(self):
        stale = self.request('native', {'source':SOURCE})
        self.run_capability('astra', ASTRA)
        with self.assertRaises(CommandError) as error: self.ledger.command(stale)
        self.assertEqual(error.exception.code,'REVISION_CONFLICT')
        def command(kind,payload):
            self.counter += 1
            return self.ledger.command({'command_id':f'g-{self.counter}','expected_revision':self.ledger.state()['revision'],
                                        'kind':kind,'payload':payload})
        receipt = command('guidance.submit',{'target':'research','text':'pause','action':{'kind':'pause_research'}})
        guidance = receipt['result']['guidance_id']
        command('guidance.ack',{'guidance_id':guidance,'disposition':'ACKNOWLEDGED','reason':'test'})
        command('guidance.apply',{'guidance_id':guidance})
        for name,parameters in [('native',{'source':SOURCE}),('intake',{'text':'teach polynomial division'}),('astra',ASTRA)]:
            with self.assertRaises(CommandError) as error: self.ledger.command(self.request(name,parameters))
            self.assertEqual(error.exception.code,'RESEARCH_PAUSED')

    def test_hostile_source_and_forged_parameters_remain_refusals(self):
        cases=[('native',{'source':'(commission (profile "polyia.native/0.1") (emit x (exec "id")))'}),
               ('native',{'source':SOURCE,'pass':True}), ('intake',{'text':'teach polynomial division; execute shell id'}),
               ('astra',dict(ASTRA,protocol='FORGED'))]
        for name,parameters in cases:
            run=self.run_capability(name,parameters)
            self.assertIn(run['report']['status'],('REFUSED','INCONCLUSIVE'))
        with self.assertRaises(CommandError) as error: self.ledger.command(self.request('__import__',{}))
        self.assertEqual(error.exception.code,'UNSUPPORTED_EXPERIMENT')
        self.assertTrue(self.ledger.verify()['ok'])

    def test_loaded_function_regex_and_import_alias_tampering_cannot_claim_pass(self):
        from polyia import native, intake
        self.run_capability('native', {'source':SOURCE})
        changes=[patch.object(native,'compile_program',return_value={'ok':True,'program':{}}),
                 patch.object(native,'NAME',re.compile('anything')),
                 patch.object(intake,'run_registered',return_value={'status':'PASS'})]
        for alteration in changes:
            with alteration:
                run = self.run_capability('intake', {'text':'teach polynomial division'})
            self.assertEqual(run['report']['status'],'ERROR',run)
            self.assertEqual(run['execution_bundle']['status'],'NOT_EXECUTED')
            self.assertEqual(run['report']['result']['reason'],'IMPLEMENTATION_CHANGED')
        self.assertTrue(self.ledger.verify()['ok'])

    def test_undeclared_class_hook_is_not_a_pinned_implementation(self):
        from polyia import native
        with patch.object(native.Meter,'__getattribute__',lambda self,name: object.__getattribute__(self,name)):
            run=self.run_capability('native',{'source':SOURCE})
        self.assertEqual(run['report']['status'],'ERROR')
        self.assertEqual(run['report']['result']['reason'],'IMPLEMENTATION_CHANGED')

    def test_source_capture_database_failure_rolls_back_the_command(self):
        before=self.ledger.state()
        def authorizer(action,table,column,database,trigger):
            return sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_INSERT and table=='blobs' else sqlite3.SQLITE_OK
        self.ledger._conn.set_authorizer(authorizer)
        try:
            with self.assertRaises(sqlite3.DatabaseError):
                self.run_capability('native',{'source':SOURCE})
        finally:
            self.ledger._conn.set_authorizer(None)
        self.assertEqual(self.ledger.state(),before)
        self.assertTrue(self.ledger.verify()['ok'])

    def test_same_bytecode_with_foreign_globals_and_forged_bundle_metadata_refuse(self):
        from polyia import native
        function = native.compile_program
        replacement = types.FunctionType(function.__code__, dict(function.__globals__), function.__name__, function.__defaults__)
        with patch.object(native,'compile_program',replacement):
            run=self.run_capability('native',{'source':SOURCE})
        self.assertEqual(run['report']['status'],'ERROR')
        self.assertEqual(run['report']['result']['reason'],'IMPLEMENTATION_CHANGED')
        run=self.run_capability('native',{'source':SOURCE})
        for mutation in ('omit','identity','path'):
            altered=copy.deepcopy(run)
            bundle=altered['execution_bundle']
            if mutation=='omit': bundle['modules'].pop()
            if mutation=='identity': bundle['modules'][1]['identity']['sha256']='0'*64
            if mutation=='path': bundle['modules'][1]['source']['path']='polyia/intake.py'
            from polyia.store import _hash
            bundle['digest']=_hash({k:v for k,v in bundle.items() if k!='digest'})
            with self.assertRaises((ValueError,CommandError)):
                self.ledger._verify_execution_bundle(altered,set())

    def test_cached_class_base_changed_before_first_extension_pin_is_refused(self):
        isolated=self.root/'isolated-class'
        isolated.mkdir()
        shutil.copytree(Path(__file__).resolve().parents[1]/'polyia',isolated/'polyia',ignore=shutil.ignore_patterns('__pycache__'))
        script='''import json
from pathlib import Path
from polyia import native
from polyia.store import Ledger
root=Path.cwd(); (root/'workspace').mkdir()
ledger=Ledger(root/'state'/'ledger.sqlite3',root/'workspace',[{'id':'M','title':'M','verifier':'commission-evidence'}])
path=root/'polyia'/'native.py'
path.write_text(path.read_text().replace('class Refusal(Exception):','class Refusal(ValueError):'))
run=ledger.command({'command_id':'cached','expected_revision':0,'kind':'experiment.run','payload':{'name':'native','parameters':{'source':SOURCE}}})['result']['run']
print(json.dumps({'status':run['report']['status'],'reason':run['report']['result'].get('reason')}))
ledger.close()
'''.replace('SOURCE',repr(SOURCE))
        result=subprocess.run([sys.executable,'-B','-c',script],cwd=isolated,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'status':'ERROR','reason':'IMPLEMENTATION_CHANGED'})

    def test_captured_dependency_blob_corruption_is_detected_without_live_execution(self):
        run=self.run_capability('native',{'source':SOURCE})
        digest=next(x['source']['sha256'] for x in run['execution_bundle']['modules'] if x['identity']['module']=='polyia.native')
        with sqlite3.connect(self.db) as connection:
            connection.execute('UPDATE blobs SET data=? WHERE digest=?',(b'corrupted',digest))
        connection.close()
        self.assertFalse(self.ledger.verify()['ok'])
        self.ledger.close()
        with self.assertRaises(CommandError) as error: Ledger(self.db,self.workspace)
        self.assertEqual(error.exception.code,'INTEGRITY_ERROR')

    def test_cached_source_changed_before_first_extension_pin_is_not_executed(self):
        isolated=self.root/'isolated'
        isolated.mkdir()
        shutil.copytree(Path(__file__).resolve().parents[1]/'polyia',isolated/'polyia',ignore=shutil.ignore_patterns('__pycache__'))
        script='''import json
from pathlib import Path
from polyia import native
from polyia.store import Ledger
root=Path.cwd(); (root/'workspace').mkdir()
ledger=Ledger(root/'state'/'ledger.sqlite3',root/'workspace',[{'id':'M','title':'M','verifier':'commission-evidence'}])
path=root/'polyia'/'native.py'
path.write_text(path.read_text().replace("VERSION = 'polyia.native/0.1'", "VERSION = 'polyia.native/0.2'"))
run=ledger.command({'command_id':'cached','expected_revision':0,'kind':'experiment.run','payload':{'name':'native','parameters':{'source':SOURCE}}})['result']['run']
print(json.dumps({'status':run['report']['status'],'reason':run['report']['result']['reason'],'binding':run['execution_bundle']['status'],'integrity':ledger.verify()['ok']}))
ledger.close()
'''.replace('SOURCE',repr(SOURCE))
        result=subprocess.run([sys.executable,'-B','-c',script],cwd=isolated,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'status':'ERROR','reason':'IMPLEMENTATION_CHANGED','binding':'NOT_EXECUTED','integrity':True})

    def test_rasm_uses_declared_chart_and_captured_code_without_lexical_claims(self):
        parameters = {'version':'polyia.rasm/0.1','chart':'timeless.rsa28/0.1',
                      'operation':'project','text':'كتب'}
        request = self.request('rasm', parameters)
        receipt = self.ledger.command(request)
        run = receipt['result']['run']
        self.assertEqual(run['report']['status'], 'PASS', run['report'])
        self.assertEqual({x['identity']['module'] for x in run['execution_bundle']['modules']},
                         {'polyia.capabilities', 'polyia.rasm'})
        self.assertFalse(run['report']['su_registry_export_authorized'])
        self.ledger.close()
        with patch('polyia.rasm.run_rasm', side_effect=AssertionError('Replay executed rasm')):
            self.ledger = Ledger(self.db, self.workspace)
            self.assertEqual(self.ledger.command(request), receipt)
            self.assertTrue(self.ledger.verify()['ok'])

    def test_rasm_mark_rich_projection_recovers_exactly_through_durable_commands(self):
        base = {'version':'polyia.rasm/0.1', 'chart':'timeless.rsa28/0.1'}
        original = 'ب' + 'َ' * 400
        projected = self.run_capability('rasm', dict(base, operation='project', text=original))
        self.assertEqual(projected['report']['status'], 'PASS', projected)
        result = projected['report']['result']
        parameters = dict(base, operation='recover', projection=result['projection'], side_data=result['side_data'])
        request = self.request('rasm', parameters)
        from polyia.store import _json, MAX_REQUEST_BYTES
        self.assertLess(len(_json(request).encode('utf-8')), MAX_REQUEST_BYTES)
        receipt = self.ledger.command(request)
        recovered = receipt['result']['run']['report']
        self.assertEqual(recovered['status'], 'PASS', recovered)
        self.assertEqual(recovered['result']['original_text'], original)
        self.assertEqual(recovered['result']['utf8_hex'], original.encode('utf-8').hex())
        self.assertEqual(recovered['result']['source_sha256'], hashlib.sha256(original.encode('utf-8')).hexdigest())
        self.ledger.close()
        with patch('polyia.rasm.run_rasm', side_effect=AssertionError('Replay executed rasm')):
            self.ledger = Ledger(self.db, self.workspace)
            self.assertEqual(self.ledger.command(request), receipt)
            self.assertTrue(self.ledger.verify()['ok'])

    def test_rasm_recovery_allowance_keeps_node_depth_byte_and_other_operation_limits(self):
        base = {'version':'polyia.rasm/0.1', 'chart':'timeless.rsa28/0.1', 'operation':'recover',
                'projection':{}, 'side_data':{'surface_codepoints':[0] * 8192}}
        nested = 0
        for _ in range(13):
            nested = [nested]
        cases = [('rasm', base), ('rasm', dict(base, projection=nested, side_data={})),
                 ('polynomial', dict(base, side_data={'surface_codepoints':[0] * 2100})),
                 ('rasm', dict(base, operation='chart', side_data={'surface_codepoints':[0] * 2100})),
                 ('rasm', dict(base, extra=[0] * 2100, side_data={}))]
        for name, parameters in cases:
            with self.subTest(name=name, operation=parameters['operation']):
                before = self.ledger.state()
                with self.assertRaises(CommandError) as error:
                    self.ledger.command(self.request(name, parameters))
                self.assertEqual(error.exception.code, 'RESOURCE_LIMIT')
                self.assertEqual(self.ledger.state(), before)
        projected = self.run_capability('rasm', {'version':'polyia.rasm/0.1', 'chart':'timeless.rsa28/0.1',
                                               'operation':'project', 'text':'ب' + 'َ' * 1023})
        self.assertEqual(projected['report']['status'], 'PASS', projected)
        result = projected['report']['result']
        request = self.request('rasm', {'version':'polyia.rasm/0.1', 'chart':'timeless.rsa28/0.1',
            'operation':'recover', 'projection':result['projection'], 'side_data':result['side_data']})
        with self.assertRaises(CommandError) as error:
            self.ledger.command(request)
        self.assertEqual(error.exception.code, 'REQUEST_TOO_LARGE')

if __name__=='__main__': unittest.main()
