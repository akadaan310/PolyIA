"""Bounded contextual Timeless bridge. Pure computation; no source-file imports.

The charts are retained authored inventories, not universal paleographic laws.
Original surfaces and explicit inverse witnesses remain distinct from rasm.
"""
from __future__ import annotations

import copy
import hashlib
from itertools import islice, product
import json
from math import factorial, log2, prod
import unicodedata

VERSION = 'polyia.rasm/0.1'
CHART = 'timeless.rsa28/0.1'
HIJAI = 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
MEDIAL = {'ٮ': 'بتثني', 'ح': 'جحخ', 'د': 'دذ', 'ر': 'رز', 'س': 'سش',
          'ص': 'صض', 'ط': 'طظ', 'ع': 'عغ', 'ٯ': 'فق',
          'ا': 'ا', 'ك': 'ك', 'ل': 'ل', 'م': 'م', 'ه': 'ه', 'و': 'و'}
FINAL = {'ٮ': 'بتث', 'ح': 'جحخ', 'د': 'دذ', 'ر': 'رز', 'س': 'سش',
         'ص': 'صض', 'ط': 'طظ', 'ع': 'عغ', 'ٯ': 'فق', 'ا': 'ا',
         'ك': 'ك', 'ل': 'ل', 'م': 'م', 'ه': 'ه', 'و': 'و', 'ں': 'ن', 'ى': 'ي'}
CLOSED = 'ادذرزو'
POSITIONS = ('initial', 'medial', 'final', 'isolated')
DOT_VALUES = {
    'ا': (0, 'none'), 'ب': (1, 'below'), 'ت': (2, 'above'), 'ث': (3, 'above'),
    'ج': (1, 'below'), 'ح': (0, 'none'), 'خ': (1, 'above'), 'د': (0, 'none'),
    'ذ': (1, 'above'), 'ر': (0, 'none'), 'ز': (1, 'above'), 'س': (0, 'none'),
    'ش': (3, 'above'), 'ص': (0, 'none'), 'ض': (1, 'above'), 'ط': (0, 'none'),
    'ظ': (1, 'above'), 'ع': (0, 'none'), 'غ': (1, 'above'), 'ف': (1, 'above'),
    'ق': (2, 'above'), 'ك': (0, 'none'), 'ل': (0, 'none'), 'م': (0, 'none'),
    'ن': (1, 'above'), 'ه': (0, 'none'), 'و': (0, 'none'), 'ي': (2, 'below')}
BASE_MARKS = 'ًٌٍَُِّْ'
SOURCE_MARKS = BASE_MARKS + 'ٰٕٖٓٔٗ٘'
FOLDS = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ؤ': 'و', 'ئ': 'ي',
         'ء': 'ا', 'ة': 'ه', 'ى': 'ي'}
POINTS = ('jawf', 'halq', 'halq', 'halq', 'lisan', 'lisan', 'lisan', 'lisan',
          'lisan', 'lisan', 'lisan', 'lisan', 'lisan', 'lisan', 'shafatan', 'shafatan', 'khayshum')
POINT = {'ا': 0, 'ه': 1, 'ع': 2, 'ح': 2, 'غ': 3, 'خ': 3, 'ق': 4, 'ك': 5,
         'ج': 6, 'ش': 6, 'ي': 6, 'ض': 7, 'ل': 8, 'ن': 9, 'ر': 10,
         'ط': 11, 'د': 11, 'ت': 11, 'ص': 12, 'ز': 12, 'س': 12,
         'ظ': 13, 'ذ': 13, 'ث': 13, 'ف': 14, 'ب': 15, 'م': 15, 'و': 15}
PACKET = ('sources/expanded/Timeless_WAZNOMIA_QIA_Handoff_v0.1 (1)/'
          'Timeless_WAZNOMIA_QIA_Handoff_v0.1/')
PINS = (
    ('sources/originals/Timeless_WAZNOMIA_QIA_Handoff_v0.1 (1).zip',
     'd78020c3e0d04ca4e178ee6eda7a6a02b772a72090d5add4ab23ab2d7ac9a4f2', 'archive root'),
    (PACKET+'FOUNDATIONAL_STUDY.md', '1bcd88c5ecfe3c9bf549ff114896551cc1f7adb44a9a64c2b2bb23c9e45f2e6c', 'II, III, V, VII, VIII, XII'),
    (PACKET+'src/rasm_state.py', '8630918a3a9c33d3b7a0a899260ed274afd13cd4c2961de5e51547f382c66fbf', 'HIJAI, CLASS_MEDIAL, CLASS_FINAL, CLOSED, positions, domains, POINT'),
    (PACKET+'results/demo.json', '2846991f7cd82bfd34b9e28d1a90bd59dd44656c450f09568f4c0d43cf361d9d', 'كتب, كتم, كتب_to_كتم'),
    ('sources/additional/ARABIC_TIMELESS/dddd9d8e15fce60ab08ce79a867a8744d02be9a5/alphabet.ts', '5a1060396116b9bdb3fa620d83b850039fd9605fc6f91c86f804030653bb7906', 'CLASSES_MEDIAL, CLASSES_FINAL, MOTION, TASHKIL, ARTICULATION'),
    ('sources/additional/ARABIC_TIMELESS/89646ac622167a6a6535d8a109388eae00fdd552/text.ts', 'bc2f575277d7679e83093458f4b18450c8884ca09bdbb26eac3b3d458d03434e', 'fold, positionsOf, parseWord, expand'),
    ('sources/additional/ARABIC_TIMELESS/6bce80be21a2b53ea294c6d0f9ffa89eeb38beb0/variants.ts', '240501c4a8a8949021b2be8266c74fa90316734ef87ab423cb076f479588ba34', 'HAMZA_FOLD, TA_MARBUTA, ALIF_MAQSURA'),
)
LIMITS = (
    'Modern authored RSA28 chart; equivalence is not a universal historical manuscript assertion.',
    'Candidate fillings are not dictionary words, intended readings, semantic relations or quantum states.',
    'Dot constraints describe supplied chart features, not measured manuscript strokes.',
    'Only one word, at most 64 base letters and 1024 raw codepoints, is admitted per projection.',
    'Recovery requires retained side data; a skeleton or hash alone is not a reversible encoding.',
    'Source-fold is an explicit lossy lookup projection, never phonemic or lexical equivalence.',
    'Articulation comparison is confined to the named source 17-point chart, not acoustic measurement.',
    'Source pins are references; runtime performs no file verification or publication.',
    'No dictionary, morphology, syntax, historical attestation, SU export or full mission acceptance is supplied.',
)


class Refusal(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(detail)


def require(condition, code, detail):
    if not condition:
        raise Refusal(code, detail)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _json_guard(value):
    nodes, bytes_seen = 0, 0

    def visit(item, depth):
        nonlocal nodes, bytes_seen
        nodes += 1
        require(depth <= 16 and nodes <= 20000, 'RESOURCE_LIMIT', 'JSON depth/node budget exceeded')
        if type(item) is str:
            require(len(item) <= 8192, 'RESOURCE_LIMIT', 'String budget exceeded')
            try:
                bytes_seen += len(item.encode('utf-8'))
            except UnicodeEncodeError:
                raise Refusal('INVALID_UNICODE', 'Input must contain Unicode scalar values') from None
            require(bytes_seen <= 131072, 'RESOURCE_LIMIT', 'JSON string byte budget exceeded')
        elif type(item) is int:
            require(item.bit_length() <= 256, 'RESOURCE_LIMIT', 'Integer magnitude exceeds budget')
        elif type(item) in (dict, list):
            require(len(item) <= 4096, 'RESOURCE_LIMIT', 'JSON collection budget exceeded')
            if type(item) is dict:
                for key, child in item.items():
                    require(type(key) is str, 'SCHEMA', 'Object keys must be strings')
                    visit(key, depth+1)
                    visit(child, depth+1)
            else:
                for child in item:
                    visit(child, depth+1)
        elif type(item) is float:
            require(False, 'RESOURCE_LIMIT', 'This discrete interface accepts no floating-point input')
        else:
            require(item is None or type(item) is bool, 'SCHEMA', 'Only JSON values are accepted')
    visit(value, 0)


def _object(value, required, optional=()):
    require(type(value) is dict and set(required) <= value.keys()
            and value.keys() <= set(required) | set(optional), 'SCHEMA', 'Missing or unsupported fields')
    return value


def _raw(text):
    require(type(text) is str, 'SCHEMA', 'Text must be a string')
    require(bool(text), 'EMPTY_TEXT', 'A nonempty orthographic word is required')
    require(len(text) <= 1024 and len(text.encode('utf-8')) <= 4096, 'RESOURCE_LIMIT', 'Raw surface budget exceeded')
    data = text.encode('utf-8')
    return {'text': text, 'utf8_hex': data.hex(), 'codepoints': [ord(c) for c in text],
            'source_sha256': hashlib.sha256(data).hexdigest(),
            'unicode_nfc': unicodedata.normalize('NFC', text),
            'unicode_version': unicodedata.unidata_version}


def _table(position):
    return FINAL if position in ('final', 'isolated') else MEDIAL


def _positions(letters):
    positions = []
    for i, letter in enumerate(letters):
        back = i > 0 and letters[i-1] not in CLOSED
        front = i < len(letters)-1 and letter not in CLOSED
        positions.append('medial' if back and front else 'final' if back else 'initial' if front else 'isolated')
    return positions


def _dots(letter):
    count, position = DOT_VALUES[letter]
    return {'count': count, 'position': position}


def _project(raw, orthography):
    require(orthography in ('base28', 'source-fold/0.1'), 'VERSION', 'Unknown orthographic projection profile')
    letters, losses = [], []
    marks = BASE_MARKS if orthography == 'base28' else SOURCE_MARKS
    for index, char in enumerate(raw['text']):
        if char in HIJAI:
            letters.append(char)
        elif char in marks or char == 'ـ':
            require(bool(letters), 'UNSUPPORTED_SURFACE', 'Leading marks or tatweel lack an admitted base letter')
            losses.append({'codepoint_index': index, 'surface': char,
                           'kind': 'tatweel-omitted' if char == 'ـ' else 'mark-omitted',
                           'after_slot': len(letters)-1})
        elif char in FOLDS and orthography == 'source-fold/0.1':
            letters.append(FOLDS[char])
            losses.append({'codepoint_index': index, 'surface': char, 'kind': 'variant-fold',
                           'slot': len(letters)-1, 'base': FOLDS[char]})
        else:
            raise Refusal('UNSUPPORTED_SURFACE', 'Unmodeled letter/mark/separator at codepoint ' + str(index))
    require(0 < len(letters) <= 64, 'RESOURCE_LIMIT', 'Projection requires 1..64 base letters')
    positions = _positions(letters)
    glyphs, domains = [], []
    for letter, position in zip(letters, positions):
        glyph = next(glyph for glyph, domain in _table(position).items() if letter in domain)
        glyphs.append(glyph)
        domains.append(_table(position)[glyph])
    projection = {'schema': 'RASM-PROJECTION/0.1', 'chart': CHART, 'orthography': orthography,
                  'source_sha256': raw['source_sha256'], 'base_letters': ''.join(letters),
                  'skeleton': ''.join(glyphs), 'positions': positions, 'domains': domains,
                  'observed_chart_dots': [_dots(letter) for letter in letters], 'losses': losses,
                  'semantic_equivalence_claim': False}
    side = {'schema': 'RASM-SIDE-DATA/0.1', 'chart': CHART, 'orthography': orthography,
            'source_sha256': raw['source_sha256'], 'surface_codepoints': list(raw['codepoints'])}
    return projection, side


def _limit(value):
    require(type(value) is int and 1 <= value <= 4096, 'RESOURCE_LIMIT', 'candidate_limit must be an integer from 1 through 4096')
    return value


def _inverse(skeleton, positions, constraints, limit):
    require(type(skeleton) is str and 1 <= len(skeleton) <= 64, 'SCHEMA', 'Skeleton must contain 1..64 glyphs')
    require(type(positions) is list and len(positions) == len(skeleton)
            and all(type(p) is str and p in POSITIONS for p in positions), 'POSITION_CONTEXT', 'Every slot requires a known contextual position')
    domains = []
    for glyph, position in zip(skeleton, positions):
        require(glyph in _table(position), 'UNKNOWN_GLYPH', 'Glyph is absent from this position table')
        domains.append(_table(position)[glyph])
    # Each retained fiber has uniform joining behavior; one representative suffices.
    require(_positions([domain[0] for domain in domains]) == positions,
            'POSITION_CONTEXT', 'Positions contradict whole-word joining and boundary conditions')
    unbound_total = prod(len(domain) for domain in domains)
    if constraints is None:
        constraints = [None] * len(domains)
    require(type(constraints) is list and len(constraints) == len(domains), 'CONSTRAINT_SCHEMA', 'Constraints must align with all slots')
    narrowed = []
    for domain, constraint in zip(domains, constraints):
        if constraint is not None:
            require(type(constraint) is dict and bool(constraint) and set(constraint) <= {'letters', 'dots'}, 'CONSTRAINT_SCHEMA', 'Use letters and/or dots for a slot constraint')
            if 'letters' in constraint:
                letters = constraint['letters']
                require(type(letters) is list and len(letters) <= 28
                        and all(type(c) is str and len(c) == 1 and c in HIJAI for c in letters),
                        'CONSTRAINT_SCHEMA', 'Letter constraints are subsets of RSA28')
                domain = ''.join(letter for letter in domain if letter in letters)
            if 'dots' in constraint:
                dots = constraint['dots']
                require(type(dots) is dict and set(dots) == {'count', 'position'}, 'CONSTRAINT_SCHEMA', 'Dots require count and position')
                require(type(dots['count']) is int and 0 <= dots['count'] <= 3
                        and type(dots['position']) is str and dots['position'] in ('none', 'above', 'below')
                        and ((dots['count'] == 0) == (dots['position'] == 'none')),
                        'CONSTRAINT_SCHEMA', 'Invalid discrete dot count/position')
                domain = ''.join(letter for letter in domain if _dots(letter) == dots)
        narrowed.append(domain)
    count = prod(len(domain) for domain in narrowed)
    candidates = [''.join(candidate) for candidate in islice(product(*narrowed), limit)]
    result = {'skeleton': skeleton, 'positions': list(positions), 'domains': narrowed,
              'constraints': copy.deepcopy(constraints), 'unbound_candidate_total': unbound_total,
              'candidate_total': count, 'candidates': candidates, 'enumerated_count': len(candidates),
              'complete': count <= limit, 'candidate_limit': limit,
              'hartley_bits': log2(count) if count else None, 'hartley_evidence_class': 'BINARY64_LOG_OF_EXACT_COUNT',
              'shannon_entropy': None, 'count_scope': 'orthographic-fillings-not-attested-words',
              'manuscript_damage_claim': False,
              'interpretation': 'inconsistent-with-declared-constraints' if count == 0 else 'classical-candidate-set'}
    status = 'INCONCLUSIVE' if count == 0 else 'RESOURCE_LIMIT' if count > limit else 'PASS'
    return status, result


def _recover(projection, side):
    _object(side, {'schema', 'chart', 'orthography', 'source_sha256', 'surface_codepoints'})
    require(side['schema'] == 'RASM-SIDE-DATA/0.1' and side['chart'] == CHART,
            'VERSION', 'Unknown side-data schema or chart')
    points = side['surface_codepoints']
    require(type(points) is list and 1 <= len(points) <= 1024
            and all(type(p) is int and 0 <= p <= 0x10ffff and not 0xd800 <= p <= 0xdfff for p in points),
            'RECOVERY_MISMATCH', 'Invalid surface codepoints')
    raw = _raw(''.join(chr(point) for point in points))
    try:
        rebuilt, expected_side = _project(raw, side['orthography'])
    except Refusal:
        raise Refusal('RECOVERY_MISMATCH', 'Side data cannot reconstruct an admitted projection') from None
    require(canonical(rebuilt) == canonical(projection) and canonical(side) == canonical(expected_side),
            'RECOVERY_MISMATCH', 'Source digest, side data or projection disagree')
    return {'original_text': raw['text'], 'utf8_hex': raw['utf8_hex'], 'source_sha256': raw['source_sha256'],
            'codepoints': raw['codepoints'], 'recovery_scope': 'retained-side-data-and-projection-consistency',
            'authenticated_origin': False}


def _chart():
    return {'alphabet': HIJAI, 'position_tables': {p: dict(_table(p)) for p in POSITIONS},
            'class_counts': {p: len(_table(p)) for p in POSITIONS}, 'closed_letters': ''.join(c for c in HIJAI if c in CLOSED),
            'dots': {letter: _dots(letter) for letter in HIJAI},
            'permutation_orders': {'medial': prod(factorial(len(d)) for d in MEDIAL.values()),
                                   'all_positions': prod(factorial(len(d)) for d in FINAL.values())},
            'articulation_chart': 'source-classical-17-point-indexed-0-to-16',
            'articulation_points': dict(POINT), 'articulation_zones': list(POINTS)}


def _relate(source, target, orthography, requested):
    require(requested == 'chart-comparison', 'UNSUPPORTED_RELATION', 'Only chart comparison is implemented; semantic/historical promotion needs independent evidence')
    left_raw, right_raw = _raw(source), _raw(target)
    left, left_side = _project(left_raw, orthography)
    right, right_side = _project(right_raw, orthography)
    same_length = len(left['base_letters']) == len(right['base_letters'])
    substitutions = []
    if same_length:
        for index, (a, b) in enumerate(zip(left['base_letters'], right['base_letters'])):
            if a != b:
                substitutions.append({'slot': index, 'source': a, 'target': b,
                    'source_point': POINT[a], 'target_point': POINT[b],
                    'same_articulation_point': POINT[a] == POINT[b],
                    'same_articulation_zone': POINTS[POINT[a]] == POINTS[POINT[b]],
                    'source_position': left['positions'][index], 'target_position': right['positions'][index]})
    return {'source': left_raw, 'target': right_raw, 'source_projection': left, 'target_projection': right,
            'source_side_data': left_side, 'target_side_data': right_side,
            'same_rasm': left['skeleton'] == right['skeleton'] and left['positions'] == right['positions'],
            'slot_alignment': 'identity-by-index' if same_length else 'UNSUPPORTED_DIFFERENT_LENGTHS',
            'substitutions': substitutions, 'relation_type': 'chart-comparison',
            'articulation_chart': 'source-classical-17-point-indexed-0-to-16',
            'semantic_relationship': 'UNPROVED', 'historical_relationship': 'UNVERIFIED', 'executable': False}


def run_rasm(parameters: dict) -> dict:
    """Run only project/invert/recover/chart/relate under explicit version and chart."""
    report = {'status': 'PASS', 'evidence_class': 'EXACTLY_CHECKED', 'result': {}, 'checks': [],
              'limitations': list(LIMITS), 'llm_inference': False, 'kernel_version': VERSION,
              'chart': CHART, 'effect_class': 'pure', 'publication_scope': 'polyia.bridge.timeless',
              'su_registry_export_authorized': False,
              'sources': [{'path': p, 'sha256': h, 'anchor': a} for p, h, a in PINS]}
    raw = None
    try:
        _json_guard(parameters)
        base = {'version', 'chart', 'operation'}
        _object(parameters, base, {'text', 'source', 'target', 'skeleton', 'positions', 'constraints',
                'candidate_limit', 'projection', 'side_data', 'orthography', 'requested_relation'})
        require(parameters['version'] == VERSION and parameters['chart'] == CHART, 'VERSION', 'Explicit supported kernel/chart versions are required')
        operation = parameters['operation']
        schema = {'project': ({'text'}, {'orthography', 'candidate_limit'}),
                  'invert': ({'skeleton', 'positions'}, {'constraints', 'candidate_limit'}),
                  'recover': ({'projection', 'side_data'}, set()), 'chart': (set(), set()),
                  'relate': ({'source', 'target'}, {'orthography', 'requested_relation'})}
        require(type(operation) is str and operation in schema, 'UNKNOWN_OPERATION', 'Operation is not registered')
        required, optional = schema[operation]
        _object(parameters, base | required, optional)
        if operation == 'project':
            raw = _raw(parameters['text'])
            limit = _limit(parameters.get('candidate_limit', 256))
            projection, side = _project(raw, parameters.get('orthography', 'base28'))
            report['status'], inverse = _inverse(projection['skeleton'], projection['positions'], None, limit)
            report['result'] = {'raw': raw, 'projection': projection, 'side_data': side, 'inverse': inverse}
        elif operation == 'invert':
            report['status'], report['result'] = _inverse(parameters['skeleton'], parameters['positions'],
                parameters.get('constraints'), _limit(parameters.get('candidate_limit', 256)))
        elif operation == 'recover':
            report['result'] = _recover(parameters['projection'], parameters['side_data'])
        elif operation == 'chart':
            report['result'] = _chart()
        else:
            report['result'] = _relate(parameters['source'], parameters['target'],
                parameters.get('orthography', 'base28'), parameters.get('requested_relation', 'chart-comparison'))
        report['checks'] = [{'name': 'typed bounded chart operation', 'pass': True,
                             'scope': 'declared finite chart and retained surface; no external semantic truth'}]
        if report['status'] != 'PASS':
            report['evidence_class'] = report['status']
        return report
    except Refusal as error:
        report.update({'status': 'REFUSED', 'evidence_class': 'REFUSAL',
                       'result': {'reason': error.code, 'detail': str(error)}})
        if raw is not None:
            report['result']['raw'] = raw
        return report
