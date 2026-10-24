"""Bounded, source-preserving prompt intake. No model or ambient tool calls.

S0/S1 follow SRC-CORPUS; computation claims follow SF-06 and PIA-122/124/180.
Recognized command lines are a declared language, not general prose comprehension.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata

from .experiments import run_registered

VERSION = 'polyia.intake/0.1'
MAX_BYTES = 16384
MAX_SPANS = 128
SOURCE_REFS = [
    {'source_id': 'SRC-CORPUS', 'path': 'sources/originals/corpus engine design (1).md',
     'anchor': 'Data Structure', 'version': '2026-10-23',
     'sha256': '954c18425dd507f617d607ceb18093478e044397088917db52ae5d4730fe8e1f'},
    {'document_id': 'DOC-GOD-SEED-1.0.0', 'derived_from_source_ids': ['SRC-OWNER-CURRENT'],
     'path': 'GOD_SEED.md', 'anchor': 'PIA-122', 'version': '1.0.0',
     'sha256': '4f179f83ff2279e1bf3e471ac8edc80456b9fdff29548332bf5b649a3c724f38'},
]
POLYNOMIAL = re.compile(r'divide polynomial\s+(\[[^\[\]\n]*\])\s+by\s+(\[[^\[\]\n]*\])', re.I)


def _nonfinite(value):
    raise ValueError('Nonfinite JSON numbers are not admitted.')


def _json_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('JSON number exceeds the finite float range.')
    return number


def _parse_json(text):
    return json.loads(text, parse_constant=_nonfinite, parse_float=_json_float)


def _refused(code, detail):
    return {'status': 'REFUSED', 'evidence_class': 'REFUSAL',
            'result': {'reason': code, 'detail': detail}, 'checks': [],
            'limitations': ['No interpretation or source capture was admitted.'],
            'kernel_version': VERSION, 'llm_inference': False}


def _explain(computation, style):
    if computation['status'] != 'PASS':
        return 'No result admitted: ' + computation['result'].get('reason', computation['status']) + '.'
    r = computation['result']
    if 'quotient' in r:
        text = ('Over Q[x], ascending-power quotient coefficients are ' + str(r['quotient'])
                + ' and remainder coefficients are ' + str(r['remainder'])
                + '. The exact coefficient checks establish a = b*q + r. '
                'Rational-function and derivative interpretations require b(x) != 0.')
        if style == 'tutorial':
            text += (' Coefficients are listed from the constant term upward. '
                     'Euclidean division constructs q and r; differentiating a=bq+r gives '
                     'a′=b′q+bq′+r′. The product and quotient derivative numerators agree '
                     'by coefficient comparison. This finite result does not solve arbitrary calculus problems.')
        return text
    return ('NFC normalization produced ' + json.dumps(r['normalized'], ensure_ascii=False)
            + '; the original text remains retained. Canonical Unicode equivalence does not establish meaning.')


def _recognize(line, style):
    assumptions = {}
    if line.lower() == 'teach polynomial division':
        parameters = {'a': [4, -2, 0, 1], 'b': [-1, 1]}
        assumptions = {'example_selection': 'SCIENTIFIC_FOUNDATIONS SF-06', 'coefficient_field': 'Q'}
        computation = run_registered('polynomial', parameters)
        kind = 'polynomial-teaching-example'
    elif match := POLYNOMIAL.fullmatch(line):
        try:
            parameters = {'a': _parse_json(match[1]), 'b': _parse_json(match[2])}
        except (ValueError, RecursionError):
            return None
        computation = run_registered('polynomial', parameters)
        kind = 'polynomial-division'
        assumptions = {'coefficient_field': 'Q', 'coefficient_order': 'ascending powers of x'}
    elif line.lower().startswith('normalize unicode '):
        try:
            original = _parse_json(line[len('normalize unicode '):])
            if not isinstance(original, str):
                return None
            original.encode('utf-8')
        except (ValueError, UnicodeError, RecursionError):
            return None
        normalized = unicodedata.normalize('NFC', original)
        parameters = {'text': original}
        computation = {'status': 'PASS', 'evidence_class': 'EXACT_REPRESENTATION_TRANSFORM',
            'result': {'original': original, 'normalized': normalized, 'normalization': 'NFC',
                       'unicode_version': unicodedata.unidata_version,
                       'loss': 'Normalized value alone cannot recover the original codepoint sequence.',
                       'semantic_equivalence_claim': False},
            'checks': [{'name': 'NFC idempotence', 'pass': unicodedata.normalize('NFC', normalized) == normalized}],
            'limitations': ['Unicode representation transform; no language understanding or historical linguistic claim.']}
        kind = 'unicode-normalization'
    else:
        return None
    refs = SOURCE_REFS + [{'document_id': 'DOC-SCIENTIFIC-FOUNDATIONS-1.0',
                           'derived_from_source_ids': ['SRC-OWNER-CURRENT', 'SRC-UCG156'],
                           'path': 'docs/SCIENTIFIC_FOUNDATIONS.md',
                           'anchor': 'SF-06' if kind.startswith('polynomial') else 'SF-11',
                           'version': '1.0.0',
                           'sha256': '78dff0f8c6637449d043e3816d2d4f6cfc5a42a2d4aad6dd662f2d6b5e9cd8f0'}]
    return {'kind': kind, 'parameters': parameters, 'assumptions': assumptions,
            'computation': computation, 'source_refs': refs,
            'explanation': _explain(computation, style), 'effects': []}


def run_intake(parameters):
    if not isinstance(parameters, dict) or set(parameters) - {'text', 'style', 'title', 'format'}:
        return _refused('PARAMETER_SCHEMA', 'Use text, optional style/title/format only.')
    text = parameters.get('text')
    style = parameters.get('style', 'concise')
    title = parameters.get('title', 'Submitted source')
    fmt = parameters.get('format', 'text')
    if not isinstance(text, str) or not text.strip():
        return _refused('TEXT_REQUIRED', 'Submit nonempty UTF-8 text.')
    if not isinstance(style, str) or style not in ('concise', 'tutorial'):
        return _refused('STYLE_UNSUPPORTED', 'Styles are concise and tutorial.')
    if not isinstance(title, str) or len(title) > 200 or fmt not in ('text', 'polyia'):
        return _refused('PARAMETER_SCHEMA', 'Bounded title and text/polyia format required.')
    try:
        raw = text.encode('utf-8'); title.encode('utf-8')
    except UnicodeError:
        return _refused('INVALID_UNICODE', 'Unpaired Unicode surrogates are not source text.')
    if len(raw) > MAX_BYTES:
        return _refused('RESOURCE_LIMIT', 'Source text exceeds 16384 UTF-8 bytes.')
    pieces = [text] if fmt == 'polyia' else text.splitlines(keepends=True)
    if len(pieces) > MAX_SPANS:
        return _refused('RESOURCE_LIMIT', 'Source exceeds 128 spans.')
    sha = hashlib.sha256(raw).hexdigest()
    source = {'id': 'source-' + sha, 'sha256': sha, 'text': text, 'bytes': len(raw),
              'title': title, 'format': fmt, 'encoding': 'UTF-8', 'rights': 'UNSPECIFIED',
              'access': 'operator-and-observer', 'public_export': 'NOT_AUTHORIZED'}
    spans, interpretations, unresolved, opportunities = [], [], [], []
    offset = 0
    for piece in pieces:
        length = len(piece.encode('utf-8'))
        span_id = 'span-' + hashlib.sha256((sha + ':' + str(offset) + ':' + str(length)).encode()).hexdigest()
        span = {'id': span_id, 'source_id': source['id'], 'byte_start': offset,
                'byte_end': offset + length, 'text': piece,
                'normalized': unicodedata.normalize('NFC', piece),
                'normalization': 'NFC', 'unicode_version': unicodedata.unidata_version}
        spans.append(span); offset += length
        if not piece.strip():
            continue
        if fmt == 'polyia':
            from .native import compile_program, execute_program
            compiled = compile_program(piece)
            executed = execute_program(compiled['program']) if compiled.get('ok') else compiled
            item = {'kind': 'native-program', 'effects': [], 'source_refs': SOURCE_REFS,
                    'computation': executed, 'compilation': compiled,
                    'explanation': 'See typed outputs and refusal diagnostics; native compilation does not interpret arbitrary prose.'}
            success = executed.get('ok') is True
        else:
            item = _recognize(piece.strip(), style)
            success = item is not None and item['computation']['status'] == 'PASS'
        if item is None:
            unresolved.append({'span_id': span_id, 'reason': 'UNSUPPORTED_INTENT',
                'detail': 'No complete registered command grammar matches this span; no implied instruction was executed.'})
            continue
        item['span_id'] = span_id
        interpretations.append(item)
        if not success:
            unresolved.append({'span_id': span_id, 'reason': 'COMPUTATION_REFUSED_OR_FAILED',
                               'detail': 'The recognized structure did not establish an admitted result.'})
            if item['kind'].startswith('polynomial'):
                opportunities.append({'status': 'PROPOSED', 'claim_kind': 'REGRESSION_EXPERIMENT',
                    'source_span': span_id, 'hypothesis': 'The polynomial kernel consistently refuses this inadmissible input.',
                    'experiment': {'name': 'polynomial', 'parameters': item['parameters']},
                    'falsification': 'An admitted output on the identical inadmissible input refutes this guard expectation.',
                    'budget': {'invocations': 1}, 'automatic_execution': False})
    nonblank = sum(bool(p.strip()) for p in pieces)
    recognized = len(interpretations)
    checks = [{'name': 'source spans partition retained bytes', 'pass': offset == len(raw) and ''.join(s['text'] for s in spans) == text},
              {'name': 'source digest matches retained UTF-8', 'pass': hashlib.sha256(source['text'].encode()).hexdigest() == sha}]
    return {'status': 'PASS' if not unresolved and recognized else 'INCONCLUSIVE',
            'evidence_class': 'SOURCE_CUSTODY_AND_SCOPED_COMPUTATION',
            'result': {'source': source, 'spans': spans, 'interpretations': interpretations,
                'unresolved': unresolved, 'opportunities': opportunities,
                'coverage': {'nonblank_spans': nonblank, 'recognized_nonblank_spans': recognized,
                             'unresolved_spans': len(unresolved)},
                'state_map': ['SOURCE_CAPTURED', 'SPANS_IDENTIFIED', 'GRAMMAR_MATCHED', 'BOUNDED_COMPUTATIONS_CHECKED', 'PROJECTION_RETURNED']},
            'checks': checks, 'kernel_version': VERSION, 'llm_inference': False,
            'limitations': ['Supported text is a complete-line grammar, not arbitrary natural-language understanding.',
                'Formats are supplied UTF-8 text and native Poly IA source; URL/PDF/EPUB fetching is unsupported.',
                'Unknown or contradictory prose remains unresolved; no unsupported semantic facts are inferred.',
                'Source bytes become durable when this result is committed through the state service.',
                'Research proposals remain unexecuted until an authorized registered experiment is requested.']}
