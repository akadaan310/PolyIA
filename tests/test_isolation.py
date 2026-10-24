"""Real Linux namespace/resource checks; host witness permissions allow reading."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

if importlib.util.find_spec('polyia.isolation'):
    from polyia import isolation
else:
    isolation = None

SOURCE = '(commission (profile "polyia.native/0.1") (emit result (add 1/3 1/6)))'


class IsolationTests(unittest.TestCase):
    def run_native(self, source=SOURCE, **kwargs):
        if isolation is None:
            return {'status':'UNAVAILABLE', 'reason':'NOT_IMPLEMENTED'}
        return isolation.run_native(source, **kwargs)

    def test_actual_sandbox_runs_only_fixed_native_engine_with_source_identity(self):
        report = self.run_native()
        self.assertEqual(report['status'], 'PASS', report)
        self.assertEqual(report['result']['outputs']['result']['value'], '1/2')
        self.assertTrue(report['process']['reaped'])
        self.assertEqual(report['process']['exit_code'], 0)
        self.assertEqual(report['policy']['name'], 'polyia.native-bwrap/0.1')
        self.assertEqual({x['path'] for x in report['implementation']},
                         {'polyia/native.py', 'polyia/__init__.py', 'polyia/isolated_worker.py'})
        self.assertFalse(report['independent_scientific_witness'])
        self.assertFalse(report['llm_inference'])
        self.assertFalse(Path('/proc') .joinpath(str(report['process']['pid'])).exists())

    def test_report_identifies_parent_policy_source_without_claiming_attestation(self):
        report = self.run_native()
        expected = hashlib.sha256(Path(isolation.__file__).read_bytes()).hexdigest()
        self.assertEqual(report.get('controller', {}).get('sha256'), expected)
        self.assertEqual(report['controller']['scope'], 'source-file identity; loaded controller remains trusted')

    def test_same_uid_readable_host_witness_is_denied_without_content_disclosure(self):
        self.assertIsNotNone(isolation, 'isolation boundary not implemented')
        with tempfile.TemporaryDirectory() as directory:
            witness = Path(directory) / 'withheld-answer.txt'
            marker = 'WITHHELD_' + os.urandom(16).hex()
            witness.write_text(marker)
            witness.chmod(0o600)
            self.assertEqual(witness.read_text(), marker)
            report = isolation.probe_read(str(witness))
            self.assertEqual(report['status'], 'READ_DENIED', report)
            self.assertEqual(report['denied_resource'], str(witness))
            self.assertEqual(report.get('denial_errno'), 'ENOENT')
            self.assertNotIn(marker, json.dumps(report))
            self.assertEqual(witness.read_text(), marker)
            self.assertTrue(report['process']['reaped'])

    def test_environment_descriptors_and_namespaces_do_not_share_host_context(self):
        self.assertIsNotNone(isolation, 'isolation boundary not implemented')
        with tempfile.NamedTemporaryFile() as opened:
            os.set_inheritable(opened.fileno(), True)
            with patch.dict(os.environ, {'POLYIA_PRIVATE_WITNESS':'never disclose this value'}):
                report = self.run_native()
            self.assertEqual(report['status'], 'PASS', report)
            observed = report['worker']
            self.assertNotIn('POLYIA_PRIVATE_WITNESS', observed['environment_names'])
            for name in ('mnt', 'net', 'pid', 'user'):
                self.assertNotEqual(observed['namespaces'][name], os.readlink('/proc/self/ns/' + name))
            self.assertTrue(all(value in (0, 1, 2, 3) for value in observed['visible_fds']))
            self.assertEqual(observed['effective_capabilities'], '0000000000000000')
            self.assertEqual(observed.get('network_interfaces'), ['lo'])

    def test_native_effect_request_is_refused_inside_sandbox(self):
        report = self.run_native('(commission (profile "polyia.native/0.1") (emit result (exec "id")))')
        self.assertEqual(report['status'], 'REFUSED', report)
        self.assertTrue(report['process']['reaped'])

    def test_unavailable_bubblewrap_fails_closed_without_fallback(self):
        self.assertIsNotNone(isolation, 'isolation boundary not implemented')
        with patch.object(isolation, 'BWRAP', '/nonexistent/polyia-bwrap'):
            report = self.run_native()
        self.assertEqual(report['status'], 'UNAVAILABLE', report)
        self.assertNotIn('process', report)

    def test_actual_mount_setup_failure_is_redacted_and_has_no_native_fallback(self):
        supervise = isolation._supervise
        private_marker = 'PRIVATE_MISSING_MOUNT_' + os.urandom(8).hex()
        def fail_setup(command, limits):
            command = list(command)
            insertion = command.index('--')
            command[insertion:insertion] = ['--ro-bind', '/nonexistent/' + private_marker, '/denied']
            return supervise(command, limits)
        with patch.object(isolation, '_supervise', fail_setup):
            report = self.run_native()
        self.assertEqual(report['status'], 'UNAVAILABLE', report)
        self.assertEqual(report['reason'], 'NAMESPACE_SETUP_FAILED')
        self.assertNotIn('result', report)
        self.assertNotIn(private_marker, json.dumps(report))
        self.assertTrue(report['process']['reaped'])

    def test_group_writable_root_owned_platform_grant_fails_closed(self):
        stat_path = Path.stat
        def group_writable(path, *args, **kwargs):
            metadata = stat_path(path, *args, **kwargs)
            if str(path) == isolation.BWRAP:
                return SimpleNamespace(st_mode=metadata.st_mode | 0o020, st_uid=0)
            return metadata
        with patch.object(Path, 'stat', group_writable):
            report = self.run_native()
        self.assertEqual(report['status'], 'UNAVAILABLE', report)
        self.assertEqual(report['reason'], 'UNTRUSTED_PLATFORM_GRANT')
        self.assertNotIn('process', report)

    def test_malformed_worker_identity_is_a_structured_protocol_error(self):
        supervise = isolation._supervise
        for malformed in (None, [], 'invalid'):
            def corrupt_identity(command, limits):
                stdout, stderr, limited, process = supervise(command, limits)
                response = json.loads(stdout)
                response['worker'] = malformed
                return json.dumps(response).encode(), stderr, limited, process
            with self.subTest(worker=malformed), patch.object(isolation, '_supervise', corrupt_identity):
                try:
                    report = self.run_native()
                except Exception as error:
                    report = {'status': 'UNCAUGHT', 'reason': type(error).__name__}
                self.assertEqual(report['status'], 'ERROR', report)
                self.assertEqual(report['reason'], 'WORKER_PROTOCOL_ERROR')

    def test_invalid_budgets_and_oversized_native_input_refuse_before_launch(self):
        for budgets in ({'wall_seconds':float('nan')}, {'cpu_seconds':True},
                        {'memory_bytes':1}, {'output_bytes':0}, {'unknown':10}):
            with self.subTest(budgets=budgets):
                report = self.run_native(budgets=budgets)
                self.assertEqual(report['status'], 'REFUSED', report)
                self.assertNotIn('process', report)
        self.assertEqual(self.run_native('a'*16385)['status'], 'REFUSED')

    def test_wall_cpu_memory_and_output_limits_stop_and_reap_actual_workers(self):
        self.assertIsNotNone(isolation, 'isolation boundary not implemented')
        cases = [('wall', {'wall_seconds':0.25}, 'WALL_LIMIT'),
                 ('cpu', {'cpu_seconds':1, 'wall_seconds':5}, 'CPU_LIMIT'),
                 ('memory', {'memory_bytes':64*1024*1024}, 'MEMORY_LIMIT'),
                 ('output', {'output_bytes':1024}, 'OUTPUT_LIMIT')]
        for name, budgets, reason in cases:
            with self.subTest(control=name):
                report = isolation.run_control(name, budgets=budgets)
                self.assertEqual(report['status'], 'RESOURCE_LIMIT', report)
                self.assertEqual(report['reason'], reason, report)
                self.assertTrue(report['process']['reaped'])
                self.assertFalse(Path('/proc').joinpath(str(report['process']['pid'])).exists())
                if name in ('wall', 'output'):
                    children = report['process'].get('observed_descendant_pids', [])
                    self.assertTrue(children, 'Actual worker cleanup requires observing its host process')
                    for pid in children:
                        self.assertFalse(Path('/proc').joinpath(str(pid)).exists())

    def test_invalid_or_looping_host_paths_refuse_without_starting_a_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            loop = Path(directory) / 'loop'
            loop.symlink_to(loop)
            for path in (str(loop), '/tmp/invalid-\ud800'):
                with self.subTest(path=repr(path)):
                    try:
                        report = isolation.probe_read(path)
                    except Exception as error:
                        report = {'status': 'UNCAUGHT', 'reason': type(error).__name__}
                    self.assertEqual(report['status'], 'REFUSED', report)
                    self.assertNotIn('process', report)

    def test_probe_cannot_label_granted_runtime_or_guest_paths_as_withheld(self):
        self.assertIsNotNone(isolation, 'isolation boundary not implemented')
        for path in ('/opt/polyia/runtime/bin/python3', '/runtime/bin/python3', '/proc/self/environ', '/input/request.json'):
            with self.subTest(path=path):
                report = isolation.probe_read(path)
                self.assertEqual(report['status'], 'REFUSED', report)
                self.assertNotIn('process', report)

    def test_operator_cli_consumes_native_data_without_shell(self):
        process = subprocess.run([sys.executable, '-B', '-m', 'polyia.isolation', 'native'],
                                 input=SOURCE, capture_output=True, text=True, timeout=15)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
