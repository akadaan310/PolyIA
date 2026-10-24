"""Executable book checks: wrong answers and forged source anchors must fail."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools/build_book_of_forms.py'
if TOOL.exists():
    spec = importlib.util.spec_from_file_location('book_builder', TOOL)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
else:
    builder = None


class BookOfFormsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(builder, 'Book builder is not implemented')

    def exercises(self):
        return json.loads((ROOT / 'books/book-of-forms/exercises.json').read_text())

    def test_real_exercises_include_exact_results_and_expected_refusals(self):
        receipts = builder.run_exercises(self.exercises(), ROOT)
        by_id = {item['id']: item for item in receipts}
        self.assertEqual(by_id['BF-02']['observed']['result.quotient'], ['-1', '1', '1'])
        self.assertEqual(by_id['BF-05']['observed']['result.values.ratio.value'], '5/2')
        self.assertEqual(by_id['BF-03']['observed']['result.reason'], 'ZERO_DIVISOR')
        self.assertEqual(by_id['BF-10']['observed']['restart_equal'], True)
        self.assertTrue(all(item['expectations_match'] for item in receipts))

    def test_wrong_expected_answer_cannot_publish_a_green_book(self):
        data = self.exercises()
        data['exercises'][1]['expected']['result.quotient'] = ['999']
        with self.assertRaises(builder.BookError):
            builder.run_exercises(data, ROOT)

    def test_no_vacuous_success_or_unknown_executor(self):
        data = self.exercises(); data['exercises'] = []
        with self.assertRaises(builder.BookError): builder.run_exercises(data, ROOT)
        data = self.exercises(); data['exercises'][0]['executor'] = 'shell'
        with self.assertRaises(builder.BookError): builder.run_exercises(data, ROOT)
        data = self.exercises(); data['exercises'][0]['expected'] = {}
        with self.assertRaises(builder.BookError): builder.run_exercises(data, ROOT)

    def test_atlas_resolves_every_original_topic_and_declares_no_topic_admission(self):
        registry = json.loads((ROOT / 'registry/university.json').read_text())
        atlas = builder.load_atlas(ROOT, registry)
        self.assertEqual(len(atlas), 62)
        self.assertEqual({item['id'] for item in atlas}, {item['id'] for item in registry['topics']})
        self.assertTrue(all(item['runtime_capability'] == 'NOT_ADMITTED_BY_THIS_PACKAGE' for item in atlas))
        self.assertTrue(all(item['source_sha256'] and item['source_line'] > 0 for item in atlas))

    def test_missing_duplicate_or_tampered_topic_source_refuses(self):
        registry = json.loads((ROOT / 'registry/university.json').read_text())
        for mutation in ['missing', 'duplicate', 'digest', 'anchor']:
            changed = copy.deepcopy(registry)
            if mutation == 'missing': changed['topics'].pop()
            elif mutation == 'duplicate': changed['topics'][-1] = changed['topics'][0]
            elif mutation == 'digest': changed['topics'][0]['source_sha256'] = '0'*64
            else: changed['topics'][0]['source_line'] = 1
            with self.subTest(mutation=mutation), self.assertRaises(builder.BookError):
                builder.load_atlas(ROOT, changed)

    def test_deterministic_render_and_scoped_evidence(self):
        first = builder.build(ROOT)
        second = builder.build(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(first['evidence']['mission_status'], 'NOT_COMMISSIONED')
        self.assertEqual(first['evidence']['book_id'], 'BOOK-OF-FORMS')
        self.assertEqual(first['evidence']['atlas_count'], 62)
        self.assertGreaterEqual(len(first['evidence']['exercises']), 10)
        builder.build(ROOT, check=True)

    def test_kernel_pass_without_actual_checks_cannot_publish(self):
        original = builder._execute
        for checks in ([], [{'name': 'forged truth value', 'pass': 'false'}]):
            def empty_checks(name, parameters):
                result = original(name, parameters)
                if result.get('status') == 'PASS':
                    result['checks'] = checks
                return result
            with self.subTest(checks=checks), patch.object(builder, '_execute', empty_checks):
                with self.assertRaises(builder.BookError):
                    builder.run_exercises(self.exercises(), ROOT)


if __name__ == '__main__': unittest.main()
