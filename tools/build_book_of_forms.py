#!/usr/bin/env python3
"""Build/check the constructed Book of Forms and execute its bounded exercises.

Only --write changes files, confined to the book and its local evidence JSON.
The durable-ledger exercise creates and removes its own temporary SQLite store.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from polyia.astra import run_adapter
from polyia.experiments import run_registered
from polyia.intake import run_intake
from polyia.native import compile_program, execute_program
from polyia.store import Ledger

BOOK = 'books/book-of-forms/BOOK.md'
EXERCISES = 'books/book-of-forms/exercises.json'
EVIDENCE = 'books/book-of-forms/evidence.json'
SOURCE_PATHS = (
    'docs/FORMAL_VOCABULARY.md', 'docs/SCIENTIFIC_FOUNDATIONS.md',
    'docs/NATIVE_LANGUAGE.md', 'docs/ASTRA_INTEGRATION.md',
    'docs/BOOTSTRAP_RUNTIME.md', 'docs/AUTOMATON_SCIENCE_UNIVERSITY.md',
    'docs/DIVISION_CHARTERS.md', 'registry/university.json',
    'polyia/experiments.py', 'polyia/native.py', 'polyia/intake.py',
    'polyia/astra.py', 'polyia/store.py', 'tools/build_book_of_forms.py', EXERCISES,
)
TOPIC_EXERCISES = {
    'transition-systems': 'BF-10: one durable command and retry',
    'admissibility': 'BF-03, BF-06, BF-11: explicit guard examples',
    'alphabets-words': 'BF-04: finite words with token identities',
    'generative-grammars': 'BF-04: finite-language promotion only',
    'alphabet-towers': 'BF-04: one promotion level only',
    'compositional-forms': 'BF-05: two rational hypersteps',
    'typed-machines': 'BF-07: closed pure native program',
    'types-as-admissibility': 'BF-11: one negative type case',
    'symbolic-composition': 'BF-05: rational composition only',
    'grammars-as-programs': 'BF-07: bounded native profile',
    'compilation': 'BF-07: serialization and VM execution',
    'projective-camera': 'BF-12: one camera projection',
    'celestial-geometry': 'BF-12: one authored sky direction',
}


class BookError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise BookError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_bytes(root, relative):
    require(isinstance(relative, str) and not Path(relative).is_absolute(), 'Source path must be relative')
    target = (root / relative).resolve()
    require(target.is_relative_to(root.resolve()), 'Source path escapes the repository')
    require(target.is_file() and target.stat().st_size <= 8 * 1024 * 1024, 'Missing or oversized source: ' + relative)
    return target.read_bytes()


def _ledger_exercise(parameters):
    require(parameters == {}, 'The ledger exercise has no caller-selected operations')
    with tempfile.TemporaryDirectory(prefix='book-of-forms-') as directory:
        root = Path(directory)
        workspace = root / 'workspace'
        workspace.mkdir()
        database = root / 'ledger.sqlite3'
        requirements = [{'id': 'BOOK-LESSON', 'title': 'Temporary teaching ledger', 'verifier': 'artifact-integrity'}]
        request = {'command_id': 'book-guidance-1', 'expected_revision': 0,
                   'kind': 'guidance.submit', 'payload': {'target': 'BOOK-LESSON', 'text': 'Retain the worked example.'}}
        with Ledger(database, workspace, requirements) as ledger:
            receipt = ledger.command(request, actor='book-exercise')
            before = ledger.state()
        with Ledger(database, workspace) as reopened:
            after = reopened.state()
            same = reopened.command(request, actor='book-exercise') == receipt
            return {'revision': after['revision'], 'event_count': len(reopened.events()),
                    'restart_equal': canonical(after) == canonical(before),
                    'retry_same_receipt': same, 'verified': reopened.verify()['ok'],
                    'commission_status': after['commission_status']}


def _execute(name, parameters):
    require(type(parameters) is dict, 'Exercise input must be an object')
    if name in ('polynomial', 'grammar-promotion', 'qpath'):
        return run_registered(name, parameters)
    if name == 'native':
        require(set(parameters) == {'source'}, 'Native exercise accepts source only')
        compiled = compile_program(parameters['source'])
        if not compiled['ok']:
            return compiled
        package = json.loads(json.dumps(compiled['program'], ensure_ascii=False, allow_nan=False))
        return execute_program(package)
    if name == 'intake':
        return run_intake(parameters)
    if name == 'astra':
        return run_adapter(parameters)
    if name == 'durable-ledger':
        return _ledger_exercise(parameters)
    raise BookError('Unregistered exercise executor: ' + str(name))


def _select(value, path):
    require(type(path) is str and 0 < len(path) <= 200, 'Invalid expected-result path')
    try:
        for part in path.split('.'):
            value = value[int(part)] if type(value) is list else value[part]
    except (TypeError, KeyError, IndexError, ValueError):
        raise BookError('Expected result field is absent: ' + path) from None
    return value


def run_exercises(specification, root=ROOT):
    require(type(specification) is dict and set(specification) == {'schema', 'edition', 'exercises'}, 'Invalid exercise document')
    require(specification['schema'] == 'BOOK-OF-FORMS-EXERCISES/0.1' and specification['edition'] == '0.1.0', 'Unsupported book exercise version')
    exercises = specification['exercises']
    require(type(exercises) is list and 10 <= len(exercises) <= 64, 'The edition requires 10..64 actual exercises')
    require(len(canonical(specification)) <= 262144, 'Exercise input budget exceeded')
    receipts, seen = [], set()
    for exercise in exercises:
        require(type(exercise) is dict and set(exercise) == {'id', 'chapter', 'title', 'executor', 'input', 'expected', 'evidence_scope', 'sources'}, 'Invalid exercise schema')
        name = exercise['id']
        require(type(name) is str and re.fullmatch(r'BF-[0-9]{2}', name) and name not in seen, 'Exercise IDs must be unique')
        seen.add(name)
        require(type(exercise['chapter']) is int and 1 <= exercise['chapter'] <= 8, 'Invalid chapter')
        require(type(exercise['expected']) is dict and exercise['expected'], 'Expected fields cannot be empty')
        require(type(exercise['sources']) is list and exercise['sources'], 'Every exercise needs a source')
        sources = []
        for source in exercise['sources']:
            require(type(source) is dict and set(source) == {'path', 'anchor'}, 'Invalid source reference')
            data = source_bytes(root, source['path'])
            require(type(source['anchor']) is str and source['anchor'] and source['anchor'] in data.decode('utf-8'), 'Unresolved source anchor')
            sources.append({**source, 'sha256': sha(data)})
        result = _execute(exercise['executor'], exercise['input'])
        observed = {path: _select(result, path) for path in exercise['expected']}
        require(canonical(observed) == canonical(exercise['expected']), name + ': actual result differs from the independently declared answer')
        # Expected refusals are successful lessons, never successful computations.
        if result.get('status') == 'PASS':
            checks = result.get('checks')
            require(type(checks) is list and bool(checks) and all(
                type(c) is dict and (c['pass'] is True if 'pass' in c else c.get('verdict') == 'PASS')
                for c in checks), name + ': computation needs nonempty, explicitly passing checks')
        if result.get('ok') is True and exercise['executor'] == 'native':
            require(result['verification']['agreement'] is True, name + ': VM/reference disagreement')
        receipts.append({'id': name, 'chapter': exercise['chapter'], 'title': exercise['title'],
                         'executor': exercise['executor'], 'input': exercise['input'],
                         'expected': exercise['expected'], 'observed': observed,
                         'expectations_match': True, 'result_sha256': sha(canonical(result)),
                         'computation_status': result.get('status', 'PASS' if result.get('ok', result.get('verified')) else 'REFUSED'),
                         'evidence_scope': exercise['evidence_scope'], 'sources': sources})
    require({e['chapter'] for e in exercises} == set(range(1, 9)), 'Each chapter needs an executed exercise')
    return receipts


def load_atlas(root, registry):
    require(sha(source_bytes(root, registry['source_registry'])) == registry['source_sha256'], 'Canonical University registry digest mismatch')
    topics = registry['topics']
    require(len(topics) == 62 and len({t['id'] for t in topics}) == 62, 'All 62 distinct canonical topics must be retained')
    divisions = {d['id']: d for d in registry['divisions']}
    expected_ids = {topic for d in divisions.values() for topic in d.get('topic_ids', [])}
    require(expected_ids == {t['id'] for t in topics}, 'Division and topic census disagree')
    require(divisions['infinity']['numeral'] == 'IX' and all(divisions[d]['status'] == 'open-research-charter' for d in ('open-vii', 'open-viii')), 'Current division decision is not preserved')
    atlas = []
    for topic in topics:
        data = source_bytes(root, topic['source'])
        require(sha(data) == topic['source_sha256'], 'Topic source digest mismatch: ' + topic['id'])
        lines = data.decode('utf-8').splitlines()
        line = topic['source_line']
        require(type(line) is int and 1 <= line <= len(lines), 'Topic source line is invalid')
        require(re.search(r"id:\s*'" + re.escape(topic['id']) + "'", lines[line-1]) is not None, 'Topic source anchor mismatch: ' + topic['id'])
        subject = re.search(r"subject:\s*'([^']*)'", '\n'.join(lines[line:line+5]))
        require(subject is not None, 'Topic subject cannot be resolved')
        require(topic['division'] in divisions and topic['id'] in divisions[topic['division']]['topic_ids'], 'Topic division changed')
        atlas.append({**topic, 'subject': subject[1], 'division_numeral': divisions[topic['division']]['numeral'],
                      'book_exercise_scope': TOPIC_EXERCISES.get(topic['id'], 'Source-linked reading; no executed topic lesson in this edition')})
    return sorted(atlas, key=lambda item: (item['division_numeral'], item['source_line']))


def _replace_block(book, name, content):
    start, end = '<!-- BEGIN ' + name + ' -->', '<!-- END ' + name + ' -->'
    require(book.count(start) == book.count(end) == 1, 'Book must contain one ' + name + ' block')
    before, rest = book.split(start)
    _, after = rest.split(end)
    return before + start + '\n\n' + content.rstrip() + '\n\n' + end + after


def build(root=ROOT, *, write=False, check=False):
    root = Path(root).resolve()
    specification = json.loads(source_bytes(root, EXERCISES))
    receipts = run_exercises(specification, root)
    atlas = load_atlas(root, json.loads(source_bytes(root, 'registry/university.json')))
    book = source_bytes(root, BOOK).decode('utf-8')
    rows = ['| Division | Canonical topic and source | Retained capability status | Lesson scope in this edition |',
            '|---|---|---|---|']
    for topic in atlas:
        link = '../../' + topic['source'] + '#L' + str(topic['source_line'])
        rows.append(f"| {topic['division_numeral']} | [`{topic['id']}` — {topic['subject']}]({link}) | `{topic['runtime_capability']}` | {topic['book_exercise_scope']} |")
    book = _replace_block(book, 'GENERATED ATLAS', '\n'.join(rows))
    rows = []
    for receipt in receipts:
        rows.extend([f"### {receipt['id']} — {receipt['title']}", '',
                     'Executed result: `' + receipt['computation_status'] + '`. The declared answer matches.', '',
                     '```json', json.dumps(receipt['observed'], ensure_ascii=False, indent=2, sort_keys=True), '```', '',
                     receipt['evidence_scope'], ''])
    book = _replace_block(book, 'VERIFIED EXERCISES', '\n'.join(rows))
    paths = sorted(set(SOURCE_PATHS) | {t['source'] for t in atlas} |
                   {json.loads(source_bytes(root, 'registry/university.json'))['source_registry']})
    evidence = {'schema': 'BOOK-OF-FORMS-EVIDENCE/0.1', 'book_id': 'BOOK-OF-FORMS', 'edition': '0.1.0',
                'claim_kind': 'CONSTRUCTED_RESEARCH_AND_TEACHING_ARTIFACT', 'mission_status': 'NOT_COMMISSIONED',
                'book_sha256': sha(book.encode('utf-8')), 'atlas_count': len(atlas), 'atlas': atlas,
                'exercises': receipts,
                'sources': [{'path': path, 'sha256': sha(source_bytes(root, path))} for path in paths],
                'limitations': ['No university or mission acceptance is asserted.',
                    'Finite expected outputs and guard refusals do not prove every source theorem or admit every topic.',
                    'Native differential witnesses share their frontend and rational library.',
                    'Temporary ledger observation excludes volatile identifiers/timestamps and is not live-service crash recovery.',
                    'Catalog and source custody do not establish scholarly truth or educational effectiveness.',
                    'No timestamp or signature is asserted by this reproducible local evidence file.']}
    encoded = json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n'
    if check:
        require(source_bytes(root, BOOK).decode('utf-8') == book, 'Generated book sections are stale; run --write')
        require(source_bytes(root, EVIDENCE).decode('utf-8') == encoded, 'Exercise/source evidence is stale; run --write')
    if write:
        (root / BOOK).write_text(book, encoding='utf-8')
        (root / EVIDENCE).write_text(encoded, encoding='utf-8')
    return {'book': book, 'evidence': evidence}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true', help='execute lessons and update generated sections/evidence')
    mode.add_argument('--check', action='store_true', help='execute lessons and verify reproducible checked-in outputs')
    args = parser.parse_args()
    try:
        result = build(write=args.write, check=args.check)
    except (BookError, ValueError, OSError, KeyError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 2
    print(json.dumps({'ok': True, 'book_id': 'BOOK-OF-FORMS', 'edition': '0.1.0',
                      'book_sha256': result['evidence']['book_sha256'], 'atlas_topics': 62,
                      'exercises': len(result['evidence']['exercises']), 'mission_status': 'NOT_COMMISSIONED'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
