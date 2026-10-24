"""Behavioral checks for the quantitative corpus and evidence runner."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


class NativeQuantitativeTests(unittest.TestCase):
    def module(self):
        path = Path(__file__).resolve().parents[1] / 'tools' / 'check_native_quantitative.py'
        self.assertTrue(path.exists(), 'Quantitative native evidence runner must exist')
        spec = importlib.util.spec_from_file_location('native_quantitative', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_small_run_checks_distinct_machines_without_claiming_full_thresholds(self):
        report = self.module().run_checks(term_count=24, inputs_per_machine=8, seed=123)
        self.assertEqual(report['status'], 'PASS')
        self.assertFalse(report['thresholds_met'])
        self.assertFalse(report['mission_acceptance'])
        self.assertFalse(report['llm_inference'])
        self.assertEqual(report['environment']['hardware_hosts_tested'], 1)
        self.assertEqual(report['terms']['checked'], 24)
        self.assertEqual(report['terms']['roundtrip_failures'], 0)
        self.assertEqual(report['terms']['idempotence_failures'], 0)
        self.assertEqual(report['terms']['semantic_failures'], 0)
        self.assertEqual(len(report['machines']), 3)
        self.assertEqual({m['id'] for m in report['machines']},
                         {'polynomial-division', 'derivative-evaluation', 'literal-substitution'})
        for machine in report['machines']:
            self.assertEqual(machine['checked'], 8)
            self.assertEqual(machine['failures'], 0)
            self.assertEqual(machine['independent_witness_checks'], 8)
            self.assertGreater(machine['timings_ns']['compile']['total'], 0)
            self.assertGreater(machine['timings_ns']['vm']['total'], 0)
            self.assertGreater(machine['timings_ns']['reference']['total'], 0)

    def test_seeded_corpora_reproduce_with_timing_separate_from_observable_digests(self):
        module = self.module()
        first = module.run_checks(term_count=12, inputs_per_machine=3, seed=456)
        again = module.run_checks(term_count=12, inputs_per_machine=3, seed=456)
        self.assertEqual(first['terms']['corpus_sha256'], again['terms']['corpus_sha256'])
        self.assertEqual(first['terms']['result_sha256'], again['terms']['result_sha256'])
        for left, right in zip(first['machines'], again['machines']):
            self.assertEqual(left['corpus_sha256'], right['corpus_sha256'])
            self.assertEqual(left['result_sha256'], right['result_sha256'])

    def test_runner_rejects_unbounded_or_empty_work_requests(self):
        module = self.module()
        for kwargs in [{'term_count': 0}, {'term_count': 10001}, {'term_count': True},
                       {'inputs_per_machine': 0}, {'inputs_per_machine': 1001}, {'seed': -1}]:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    module.run_checks(**kwargs)

    def test_corrupted_reference_results_make_the_report_fail(self):
        module = self.module()
        # Deliberate evaluator mutation: the harness must detect disagreement,
        # even when a source compiled and the stack VM returned real outputs.
        with patch.object(module.native, '_reference', return_value={}):
            report = module.run_checks(term_count=4, inputs_per_machine=1, seed=17)
        self.assertEqual(report['status'], 'FAIL')
        self.assertFalse(report['thresholds_met'])
        self.assertEqual([machine['failures'] for machine in report['machines']], [1, 1, 1])
        self.assertTrue(report['failures'])


if __name__ == '__main__':
    unittest.main()
