"""Contextual rasm checks: literal packet examples, recovery and negative controls."""
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / 'polyia/rasm.py').exists():
    from polyia.rasm import run_rasm
else:
    def run_rasm(parameters):
        return {'status': 'REFUSED', 'result': {'reason': 'NOT_IMPLEMENTED'}}


def call(operation, **values):
    return {'version': 'polyia.rasm/0.1', 'chart': 'timeless.rsa28/0.1',
            'operation': operation, **values}


class RasmTests(unittest.TestCase):
    def passed(self, parameters):
        result = run_rasm(parameters)
        self.assertEqual(result['status'], 'PASS', result)
        self.assertFalse(result['llm_inference'])
        return result['result']

    def refused(self, parameters, code):
        result = run_rasm(parameters)
        self.assertEqual(result['status'], 'REFUSED', result)
        self.assertEqual(result['result']['reason'], code, result)
        return result

    def test_packet_example_has_exact_fifteen_candidates_and_hartley_scope(self):
        result = self.passed(call('project', text='كتب'))
        self.assertEqual(result['projection']['skeleton'], 'كٮٮ')
        self.assertEqual(result['projection']['positions'], ['initial', 'medial', 'final'])
        self.assertEqual(result['projection']['domains'], ['ك', 'بتثني', 'بتث'])
        inverse = result['inverse']
        self.assertEqual(inverse['candidate_total'], 15)
        self.assertEqual(inverse['candidates'], ['كبب', 'كبت', 'كبث', 'كتب', 'كتت', 'كتث',
            'كثب', 'كثت', 'كثث', 'كنب', 'كنت', 'كنث', 'كيب', 'كيت', 'كيث'])
        self.assertAlmostEqual(inverse['hartley_bits'], 3.9068905956085187)
        self.assertEqual(inverse['count_scope'], 'orthographic-fillings-not-attested-words')
        self.assertIsNone(inverse['shannon_entropy'])

    def test_medial_final_partitions_and_source_subgroup_counts(self):
        result = self.passed(call('chart'))
        self.assertEqual(result['alphabet'], 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        self.assertEqual(result['class_counts'], {'initial': 15, 'medial': 15, 'final': 17, 'isolated': 17})
        self.assertEqual(result['permutation_orders'], {'medial': 92160, 'all_positions': 4608})
        for table in result['position_tables'].values():
            letters = ''.join(table.values())
            self.assertEqual(len(letters), 28)
            self.assertEqual(set(letters), set(result['alphabet']))

    def test_noon_ya_and_closed_neighbors_change_context(self):
        expected = {'نب': ('ٮٮ', ['initial', 'final']), 'بن': ('ٮں', ['initial', 'final']),
                    'ن': ('ں', ['isolated']), 'بي': ('ٮى', ['initial', 'final']),
                    'ي': ('ى', ['isolated']), 'بدب': ('ٮدٮ', ['initial', 'final', 'isolated'])}
        for text, (skeleton, positions) in expected.items():
            with self.subTest(text=text):
                p = self.passed(call('project', text=text))['projection']
                self.assertEqual(p['skeleton'], skeleton)
                self.assertEqual(p['positions'], positions)

    def test_dot_binding_is_typed_and_can_select_the_original(self):
        inverse = self.passed(call('invert', skeleton='كٮٮ', positions=['initial', 'medial', 'final'],
            constraints=[None, {'dots': {'count': 2, 'position': 'above'}}, None]))
        self.assertEqual(inverse['candidate_total'], 3)
        self.assertEqual(inverse['candidates'], ['كتب', 'كتت', 'كتث'])
        exact = self.passed(call('invert', skeleton='كٮٮ', positions=['initial', 'medial', 'final'],
            constraints=[None, {'letters': ['ت']}, {'dots': {'count': 1, 'position': 'below'}}]))
        self.assertEqual(exact['candidates'], ['كتب'])
        self.refused(call('invert', skeleton='ٮ', positions=['isolated'],
            constraints=[{'dots': {'count': True, 'position': 'below'}}]), 'CONSTRAINT_SCHEMA')

    def test_conflicting_constraints_are_model_bottom_not_manuscript_damage(self):
        result = run_rasm(call('invert', skeleton='ٮ', positions=['isolated'],
            constraints=[{'letters': ['ب'], 'dots': {'count': 2, 'position': 'above'}}]))
        self.assertEqual(result['status'], 'INCONCLUSIVE')
        self.assertEqual(result['result']['candidate_total'], 0)
        self.assertEqual(result['result']['candidates'], [])
        self.assertEqual(result['result']['interpretation'], 'inconsistent-with-declared-constraints')
        self.assertIsNone(result['result']['hartley_bits'])
        self.assertFalse(result['result']['manuscript_damage_claim'])

    def test_inversion_needs_context_and_rejects_impossible_positions(self):
        self.refused(call('invert', skeleton='ٮ'), 'SCHEMA')
        self.refused(call('invert', skeleton='ٮ', positions=['medial']), 'POSITION_CONTEXT')
        self.refused(call('invert', skeleton='ں', positions=['initial']), 'UNKNOWN_GLYPH')
        self.refused(call('invert', skeleton='ٮ', positions=['other']), 'POSITION_CONTEXT')

    def test_candidate_cap_preserves_total_and_symbolic_product(self):
        result = run_rasm(call('project', text='ب'*10, candidate_limit=5))
        self.assertEqual(result['status'], 'RESOURCE_LIMIT')
        inverse = result['result']['inverse']
        self.assertEqual(inverse['candidate_total'], 5859375)
        self.assertEqual(len(inverse['candidates']), 5)
        self.assertFalse(inverse['complete'])
        self.assertEqual(len(inverse['domains']), 10)
        self.assertEqual(result['result']['raw']['text'], 'ب'*10)

    def test_marks_tatweel_and_codepoint_order_recover_exactly(self):
        text = 'كَـتَبَّ'
        result = self.passed(call('project', text=text))
        self.assertEqual(result['projection']['base_letters'], 'كتب')
        self.assertEqual(result['raw']['text'], text)
        self.assertEqual(result['raw']['utf8_hex'], text.encode().hex())
        self.assertEqual(result['raw']['codepoints'], [ord(c) for c in text])
        recovered = self.passed(call('recover', projection=result['projection'], side_data=result['side_data']))
        self.assertEqual(recovered['original_text'], text)
        self.assertEqual(recovered['utf8_hex'], text.encode().hex())
        self.assertEqual(recovered['source_sha256'], hashlib.sha256(text.encode()).hexdigest())

    def test_variants_refuse_by_default_and_explicit_fold_records_losses(self):
        for text in ['ء', 'كتبة', 'أ', 'ى', 'أ']:
            with self.subTest(text=text):
                refused = self.refused(call('project', text=text), 'UNSUPPORTED_SURFACE')
                self.assertEqual(refused['result']['raw']['text'], text)
        text = 'أَإآٱؤئءةىأ'
        report = run_rasm(call('project', text=text, orthography='source-fold/0.1', candidate_limit=1))
        self.assertIn(report['status'], ['PASS', 'RESOURCE_LIMIT'], report)
        result = report['result']
        self.assertEqual(result['projection']['base_letters'], 'ااااوياهيا')
        self.assertTrue(result['projection']['losses'])
        recovered = self.passed(call('recover', projection=result['projection'], side_data=result['side_data']))
        self.assertEqual(recovered['original_text'], text)

    def test_unknown_marks_letters_and_leading_marks_are_not_silently_dropped(self):
        for text in ['كتبX', 'َكتب', 'ك\u0610تب', 'كتب كتب', 'ٮ']:
            with self.subTest(text=text):
                result = self.refused(call('project', text=text), 'UNSUPPORTED_SURFACE')
                self.assertEqual(result['result']['raw']['text'], text)

    def test_recovery_detects_changed_side_data_and_projection(self):
        original = self.passed(call('project', text='كَتَبَ'))
        changed = copy.deepcopy(original['side_data']); changed['surface_codepoints'][0] = ord('ل')
        self.refused(call('recover', projection=original['projection'], side_data=changed), 'RECOVERY_MISMATCH')
        changed = copy.deepcopy(original['projection']); changed['positions'][1] = 'final'
        self.refused(call('recover', projection=changed, side_data=original['side_data']), 'RECOVERY_MISMATCH')
        self.refused(call('recover', projection=original['projection']), 'SCHEMA')

    def test_relation_keeps_articulation_rasm_and_semantics_separate(self):
        result = self.passed(call('relate', source='كتب', target='كتم'))
        self.assertFalse(result['same_rasm'])
        self.assertTrue(result['substitutions'][0]['same_articulation_point'])
        self.assertEqual(result['substitutions'][0]['source_point'], 15)
        self.assertEqual(result['semantic_relationship'], 'UNPROVED')
        self.assertEqual(result['historical_relationship'], 'UNVERIFIED')
        self.assertFalse(result['executable'])
        self.assertTrue(self.passed(call('relate', source='كتب', target='كبت'))['same_rasm'])
        self.refused(call('relate', source='كتب', target='كتم', requested_relation='cognate'), 'UNSUPPORTED_RELATION')
        self.assertEqual(self.passed(call('project', text='كتم'))['inverse']['candidate_total'], 5)
        comparison = self.passed(call('relate', source='ب', target='ف'))['substitutions'][0]
        self.assertTrue(comparison['same_articulation_zone'])
        self.assertFalse(comparison['same_articulation_point'])

    def test_versions_schemas_numeric_bounds_and_invalid_unicode(self):
        self.refused(call('project', text='كتب', chart='universal-historical'), 'VERSION')
        self.refused(call('project', text='كتب', command='id'), 'SCHEMA')
        self.refused(call('shell', text='id'), 'UNKNOWN_OPERATION')
        for value in [0, -1, True, 1.5, 4097, 10**10000]:
            self.refused(call('project', text='كتب', candidate_limit=value), 'RESOURCE_LIMIT')
        self.refused(call('project', text='ب'*65), 'RESOURCE_LIMIT')
        self.refused(call('project', text=''), 'EMPTY_TEXT')
        self.refused(call('project', text='\ud800'), 'INVALID_UNICODE')

    def test_reports_are_pure_and_bridge_only(self):
        request = call('project', text='كتب')
        before = copy.deepcopy(request)
        a, b = run_rasm(request), run_rasm(request)
        self.assertEqual(a['status'], 'PASS', a)
        self.assertEqual(a, b)
        self.assertEqual(request, before)
        self.assertEqual(a['publication_scope'], 'polyia.bridge.timeless')
        self.assertFalse(a['su_registry_export_authorized'])
        json.dumps(a, allow_nan=False)

    def test_source_dot_table_is_the_actual_pinned_upstream_table(self):
        report = run_rasm(call('chart'))
        self.assertEqual(report['status'], 'PASS', report)
        source = (ROOT / 'examples/rasm/upstream/alphabet.ts').read_text()
        rows = re.findall(r'"([ابتثجحخدذرزسشصضطظعغفقكلمنهوي])":\s*\{[^\n]*dots:\s*(\d),\s*dotPosition:\s*"(above|below|none)"', source)
        self.assertEqual(len(rows), 28)
        self.assertEqual(report['result']['dots'], {letter: {'count': int(count), 'position': pos} for letter, count, pos in rows})
        for pin in report['sources']:
            data = (ROOT / pin['path']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), pin['sha256'])

    def test_upstream_snapshot_has_verified_blob_identity_and_exact_registry_admission(self):
        provenance = json.loads((ROOT / 'examples/rasm/upstream/provenance.json').read_text())
        self.assertEqual(provenance['status'], 'ADMITTED_SELECTED_FILE_SNAPSHOTS')
        registry = json.loads((ROOT/'registry/sources.json').read_text())
        sources = {item['id']: item for item in registry['sources']}
        for entry in provenance['files']:
            source = sources[entry['source_id']]
            self.assertEqual(source['path'], entry['canonical_path'])
            self.assertEqual(source['sha256'], entry['sha256'])
            self.assertEqual(source['git_blob_sha1'], entry['git_blob_sha1'])
            self.assertEqual((ROOT/source['path']).read_bytes(), (ROOT/entry['path']).read_bytes())
        for source in provenance['files']:
            data = (ROOT / source['path']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), source['sha256'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(), source['git_blob_sha1'])

    def test_base_and_fold_profiles_keep_canonically_equivalent_surfaces_distinct(self):
        left = run_rasm(call('project', text='أ', orthography='source-fold/0.1'))['result']
        right = run_rasm(call('project', text='أ', orthography='source-fold/0.1'))['result']
        self.assertEqual(left['raw']['unicode_nfc'], right['raw']['unicode_nfc'])
        self.assertNotEqual(left['raw']['source_sha256'], right['raw']['source_sha256'])
        self.assertNotEqual(left['side_data'], right['side_data'])
        self.assertEqual(left['projection']['skeleton'], right['projection']['skeleton'])
        for result, expected in [(left, 'أ'), (right, 'أ')]:
            recovered = self.passed(call('recover', projection=result['projection'], side_data=result['side_data']))
            self.assertEqual(recovered['original_text'], expected)

    def test_projection_matches_retained_source_for_every_letter_and_context(self):
        path = ROOT / ('sources/expanded/Timeless_WAZNOMIA_QIA_Handoff_v0.1 (1)/'
                       'Timeless_WAZNOMIA_QIA_Handoff_v0.1/src/rasm_state.py')
        spec = importlib.util.spec_from_file_location('_rasm_reference_for_tests', path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
            for letter in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي':
                for text in [letter, letter+'ب', 'ب'+letter, 'ب'+letter+'ب', 'د'+letter]:
                    result = self.passed(call('project', text=text))['projection']
                    self.assertEqual(result['skeleton'], module.skeleton(text))
                    self.assertEqual(result['positions'], list(module.positions(text)))
                    self.assertEqual(result['domains'], list(module.domains(text)))
        finally:
            sys.modules.pop(spec.name, None)


if __name__ == '__main__': unittest.main()
