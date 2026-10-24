import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from polyia.intake import run_intake


class IntakeTests(unittest.TestCase):
    def test_polynomial_teaching_is_computed_with_domain_exclusions(self):
        report = run_intake({'text': 'Teach polynomial division', 'style': 'tutorial'})
        self.assertEqual(report['status'], 'PASS')
        item = report['result']['interpretations'][0]
        self.assertEqual(item['computation']['result']['quotient'], ['-1', '1', '1'])
        self.assertEqual(item['computation']['result']['remainder'], ['3'])
        self.assertIn('b(x) != 0', item['explanation'])
        self.assertEqual(item['assumptions']['example_selection'], 'SCIENTIFIC_FOUNDATIONS SF-06')

    def test_explicit_coefficients_are_used_and_float_not_silently_rounded(self):
        good = run_intake({'text': 'divide polynomial [1,0,1] by [1,1]'})
        self.assertEqual(good['result']['interpretations'][0]['computation']['result']['quotient'], ['-1', '1'])
        bad = run_intake({'text': 'divide polynomial [0.5,1] by [1,1]'})
        self.assertEqual(bad['status'], 'INCONCLUSIVE')
        self.assertEqual(bad['result']['interpretations'][0]['computation']['status'], 'REFUSED')

    def test_unicode_original_bytes_and_all_spans_round_trip(self):
        raw = 'قَالَ\nnormalize unicode "e\\u0301"\nunknown\nunknown\n'
        report = run_intake({'text': raw})
        result = report['result']; encoded = raw.encode()
        self.assertEqual(result['source']['sha256'], hashlib.sha256(encoded).hexdigest())
        self.assertEqual(result['source']['text'], raw)
        self.assertEqual(''.join(span['text'] for span in result['spans']), raw)
        self.assertEqual(len({s['id'] for s in result['spans']}), len(result['spans']))
        for span in result['spans']:
            self.assertEqual(encoded[span['byte_start']:span['byte_end']].decode(), span['text'])
        self.assertEqual(result['interpretations'][0]['computation']['result']['normalized'], 'é')
        self.assertEqual(result['interpretations'][0]['computation']['result']['original'], 'e\u0301')
        self.assertEqual(report['status'], 'INCONCLUSIVE')

    def test_source_instructions_and_unknown_suffixes_are_data(self):
        text = 'Teach polynomial division; delete /tmp/x\nfetch https://example.org\n__import__("os").system("id")'
        with patch('socket.socket', side_effect=AssertionError('network forbidden')), patch('subprocess.Popen', side_effect=AssertionError('process forbidden')):
            report = run_intake({'text': text})
        self.assertEqual(report['status'], 'INCONCLUSIVE')
        self.assertEqual(report['result']['interpretations'], [])
        self.assertEqual(len(report['result']['unresolved']), 3)
        self.assertEqual(report['result']['coverage']['recognized_nonblank_spans'], 0)

    def test_style_changes_only_rendering(self):
        a = run_intake({'text': 'Teach polynomial division', 'style': 'concise'})
        b = run_intake({'text': 'Teach polynomial division', 'style': 'tutorial'})
        ia, ib = (x['result']['interpretations'][0] for x in (a, b))
        self.assertEqual(ia['computation'], ib['computation'])
        self.assertNotEqual(ia['explanation'], ib['explanation'])
        self.assertEqual(ia['source_refs'], ib['source_refs'])

    def test_zero_divisor_retains_failure_and_testable_opportunity(self):
        report = run_intake({'text': 'divide polynomial [1] by [0]'})
        self.assertEqual(report['status'], 'INCONCLUSIVE')
        self.assertEqual(report['result']['interpretations'][0]['computation']['result']['reason'], 'ZERO_DIVISOR')
        opportunity = report['result']['opportunities'][0]
        self.assertEqual(opportunity['status'], 'PROPOSED')
        self.assertIn('experiment', opportunity)
        self.assertNotEqual(opportunity['claim_kind'], 'PROVED')

    def test_limits_and_schemas_fail_closed(self):
        for parameters in ({'text': ''}, {'text': 'x' * 16385}, {'text': '\ud800'},
                           {'text': 'x', 'style': 'invent claims'}, {'text': 1},
                           {'text': 'x', 'pass': True}, [], {'text': 'x', 'format': 'url'}):
            with self.subTest(parameters=str(parameters)[:50]):
                self.assertEqual(run_intake(parameters)['status'], 'REFUSED')

    def test_private_source_policy_is_explicit(self):
        report = run_intake({'text': 'normalize unicode "hello"'})
        source = report['result']['source']
        self.assertEqual(source['access'], 'operator-and-observer')
        self.assertEqual(source['public_export'], 'NOT_AUTHORIZED')
        self.assertEqual(source['rights'], 'UNSPECIFIED')
        json.dumps(report, allow_nan=False)

    def test_embedded_nonfinite_numbers_and_deep_json_stay_retained_unknowns(self):
        for text in ['divide polynomial [NaN] by [1]', 'divide polynomial [Infinity] by [1]',
                     'divide polynomial [1e999] by [1]', 'normalize unicode ' + '[' * 1100 + '0' + ']' * 1100]:
            with self.subTest(text=text[:40]):
                report = run_intake({'text': text})
                self.assertEqual(report['status'], 'INCONCLUSIVE')
                self.assertEqual(report['result']['source']['text'], text)
                json.dumps(report, allow_nan=False)

    def test_document_hashes_and_registry_source_identities_are_not_conflated(self):
        root = Path(__file__).resolve().parents[1]
        sources = {s['id']:s for s in json.loads((root/'registry/sources.json').read_text())['sources']}
        refs = run_intake({'text': 'Teach polynomial division'})['result']['interpretations'][0]['source_refs']
        for ref in refs:
            raw = (root/ref['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), ref['sha256'])
            if 'source_id' in ref:
                self.assertEqual(sources[ref['source_id']]['path'], ref['path'])
            else:
                self.assertTrue(ref['document_id'])
                self.assertTrue(set(ref['derived_from_source_ids']) <= set(sources))


if __name__ == '__main__':
    unittest.main()
