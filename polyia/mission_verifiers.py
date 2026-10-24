"""Versioned, deliberately narrow mission acceptance; never executes input code."""
from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import platform
import re
import sqlite3
import sys
import tempfile
import threading
import types

from . import store


ADAPTER = 'PIA-042/capture-v1'
DEFINITION_SHA256 = '8988319b1135f79a4b567fe3e6604cca5e1db46e1b3f7fc463dcfd2bc8601442'
ACCEPTANCE_SHA256 = 'fc18a113742adfc8ade15524309fc988f2dc4d1b051bc4a856590b0d9758b1e8'
GUIDANCE_ADAPTER = 'PIA-040/guidance-effects-v1'
GUIDANCE_DEFINITION_SHA256 = '78bbba161e8161341fc0c2f27c61ed94411551ddf58095d507f798a8947dcdcf'
GUIDANCE_ACCEPTANCE_SHA256 = '7f9a4d6bf64916f6fa43b4f969267248accd49612d0ac19f66ad760557dae9f1'
# Explicit decisions for every non-upstream mapped record. These decisions do
# not mark the source's larger scientific, corpus or compiler duties complete.
GUIDANCE_INTEGRATED = {
    'SUP-9e3a285a12be4eb4-00000a12': ('APPLICABLE', 'Versioned application boundary: test stale revisions, actor scope and exact retries; no external access or new privilege is requested by these actions.'),
    'SUP-9e3a285a12be4eb4-00000c6b': ('CONDITIONAL_CAPABILITY', 'Cultural authority, licensing and export metadata govern PHONEX data operations. Priority and research pause/resume neither transform nor export a corpus; export actions remain unregistered.'),
    'SUP-82bda78d807ee7b8-00000a85': ('CONDITIONAL_CAPABILITY', 'LanguageVariety, Lexeme, Form, Pronunciation, Sense, Morpheme, Source and QRelation fields govern those objects. This action set constructs none of them and makes no linguistic equivalence claim.'),
    'SUP-b53938efb641f061-00000800': ('CONDITIONAL_CAPABILITY', 'Snapshot-pinned linguistic pack joins and independent pronunciation/meaning/cognacy records remain obligations of the concierge compiler; this verifier neither composes language packs nor certifies that compiler.'),
    'SUP-48c38a2a24128513-00000a8a': ('APPLICABLE', 'The stateful guidance kernel publishes explicit effects and uses revision-guarded concurrency plus replay. Test exact effects, a two-connection race, restart and nonexecuting replay; no ABI/WIT cross-package composition is claimed.'),
    'SUP-76646e2b7f57d09a-00001251': ('PRESERVED_SCIENTIFIC_CONTEXT', 'These Arabic morphological/etymological examples are retained authored claims. Applying priority or pause/resume does not evaluate, promote or certify them.'),
    'SUP-7a6e1604b84f211a-00009009': ('CONDITIONAL_CAPABILITY', 'Topology, category/operad, sheaf, semiring and Hilbert-space claims require their stated constructions. The guidance state machine asserts none of those mathematical structures.'),
    'SUP-7a6e1604b84f211a-000095b1': ('HISTORICAL_EVIDENCE', 'Preserve the QIA prototype 35-test account and its explicit limitations; none of those historical results enters this fresh guidance pass count.'),
    'SUP-e27e58b59c06ad28-00000000': ('HISTORICAL_EVIDENCE', 'The QIA TEST_REPORT is a prior run, not execution by this adapter; preserve its bytes without counting its 35 tests as new evidence.'),
    'SUP-ccc660d78c0b106a-0000113b': ('UPSTREAM_CONDITIONAL', 'The refined record scopes source reconnaissance, book text and campus-preservation duties to Grammar in Ciphers and its corpus adapter. These actions do not mutate a book, campus or upstream repository.'),
    'SUP-0d2001d0cb91b05c-00000f06': ('CONDITIONAL_CAPABILITY', 'Validity/supersession metadata and n-ary ontology constraints remain conditions of the DK0 ontology objects; guidance revisions are tested without claiming implementation of that ontology.'),
}
GUIDANCE_UPSTREAM = {
    'ASTRA': 'ASTRA product release, rendering, audio and device gates',
    'HOMELESS_DARK': 'DARK world subjects, physical actions, visualization, causality and University contribution export',
    'CIA_BROWSER': 'CIA browser tabs, frames, navigation epochs, consent, broker HOLD and desktop/mobile products',
    'PILLAR9': 'PILLAR9 source ingestion, native language and compiler forms',
    'GRAMMAR_IN_CIPHERS': 'Grammar in Ciphers edition-aware book, text and publication contracts',
    'TRE_TREE': 'TRE/CGIT source positions, tree compiler, dependency and execution contracts',
    'PUBLIC_UNIVERSITY': 'the independently governed public University repository and publication decisions',
    'GIN': 'Grammar in Numbers hypotheses and research decision history',
    'PURL': 'PURL resource endpoints, operation authorities, expected_version and HTTP/header/error compatibility',
    'SNAD': 'SNAD ACSP envelopes, corpus/compiler resources and PURL-native publication lifecycle',
    'SUBSTRATEIO': 'SubstrateIO hypothesis revisions and protocol validation',
}
REGISTRY_PINS = (
    ('registry/acceptance.json', 'c1d9683919367490a398dbf8adfa98c67b825cbb60d10db107ddc3d5cbdc950b'),
    ('registry/inherited_obligations.json', '3809c52c0678a3e3a0ad3dcbd4c729beb9f49ae915a23f088a2f8196ddabc998'),
    ('registry/inherited_supplemental.json', '22dd4966f8115ef6cd1681a64f86ffb460d6f32359897837468c310da7f68bd9'),
)
MODULES = (
    ('polyia', 'polyia/__init__.py'),
    ('polyia.store', 'polyia/store.py'),
    ('polyia.experiments', 'polyia/experiments.py'),
    ('polyia.mission_verifiers', 'polyia/mission_verifiers.py'),
)


def _refuse(code, message):
    raise store.CommandError(code, message, 409)


def _encoded(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def _digest(value):
    return hashlib.sha256(_encoded(value)).hexdigest()


def _policy_value(value):
    if isinstance(value, re.Pattern):
        return {'regex': value.pattern, 'flags': value.flags}
    if isinstance(value, (set, frozenset)):
        return {'type': type(value).__name__, 'values': sorted((_policy_value(v) for v in value), key=_encoded)}
    if isinstance(value, Path):
        return {'path': str(value)}
    if isinstance(value, (tuple, list)):
        return {'type': type(value).__name__, 'values': [_policy_value(v) for v in value]}
    if isinstance(value, dict):
        return {key: _policy_value(item) for key, item in value.items()}
    if type(value) in (str, int, bool, float, type(None)):
        return {'type': type(value).__name__, 'value': value}
    _refuse('IMPLEMENTATION_CHANGED', 'Mission code contains an unbound policy value')


def _source_value(node, values):
    """Only literal policy construction, never eval/exec of installed or input code."""
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        pass
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        left, right = _source_value(node.left, values), _source_value(node.right, values)
        if type(left) is int and type(right) is int:
            return left * right
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == 'frozenset' and len(node.args) == 1 and not node.keywords):
        return frozenset(_source_value(node.args[0], values))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == 're'
            and node.func.attr == 'compile' and len(node.args) == 1 and not node.keywords):
        return re.compile(_source_value(node.args[0], values))
    _refuse('IMPLEMENTATION_CHANGED', 'Mission policy construction is not supported by this binding version')


def _loaded_identity(module_name, source):
    """Compare installed source with actual functions, defaults, policies and imports.

    The interpreter/stdlib, this binding implementation and privileged installation
    remain trusted. This is drift detection, not a malicious-administrator proof.
    """
    module = importlib.import_module(module_name)
    expected_path = store.PACKAGE_ROOT / dict(MODULES)[module_name]
    if Path(module.__file__).resolve() != expected_path:
        _refuse('IMPLEMENTATION_CHANGED', 'Mission implementation is outside its installed package')
    if module_name == 'polyia.experiments':
        _, identity, pinned = store._pinned_science()
        if pinned != source:
            _refuse('IMPLEMENTATION_CHANGED', 'Scientific dependency source differs from loaded code')
        return identity
    tree = ast.parse(source, filename=str(expected_path))
    compiled = compile(source, str(expected_path), 'exec', dont_inherit=True, optimize=sys.flags.optimize)
    stack, code = [compiled], {}
    while stack:
        item = stack.pop()
        code[item.co_qualname] = store._hash(store._code_structure(item))
        stack.extend(v for v in item.co_consts if isinstance(v, types.CodeType))
    values, functions, imports, policies = {}, {}, {}, {}
    mutable = {'_SCIENCE_PIN', '_SCIENCE_PIN_LOCK', '_EXTENSION_PINS'}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name) or not (target.id.isupper() or target.id == '__version__'):
                    continue
                name = target.id
                if module_name == 'polyia.store' and name in mutable:
                    continue
                if module_name == 'polyia.store' and name == 'PACKAGE_ROOT':
                    value = Path(module.__file__).resolve().parent.parent
                elif module_name == 'polyia.store' and name == 'CONTEXT_CODE':
                    expected = "tuple(('runtime-source', f'polyia/{name}.py', True) for name in ('__init__', 'store', 'experiments', 'cli', 'server', '__main__'))"
                    if ast.dump(node.value) != ast.dump(ast.parse(expected, mode='eval').body):
                        _refuse('IMPLEMENTATION_CHANGED', 'Historical source-context contract changed')
                    value = tuple(('runtime-source', 'polyia/' + n + '.py', True)
                                  for n in ('__init__', 'store', 'experiments', 'cli', 'server', '__main__'))
                else:
                    value = _source_value(node.value, values)
                values[name] = value
                policies[name] = _policy_value(value)
                if _encoded(_policy_value(getattr(module, name, None))) != _encoded(policies[name]):
                    _refuse('IMPLEMENTATION_CHANGED', 'Loaded mission policy differs from installed source')
        nodes = []
        if isinstance(node, ast.FunctionDef):
            nodes = [(node.name, node, getattr(module, node.name, None))]
        elif isinstance(node, ast.ClassDef):
            cls = getattr(module, node.name, None)
            bases = (Exception,) if node.name == 'CommandError' else (object,)
            if not isinstance(cls, type) or cls.__module__ != module_name or cls.__bases__ != bases:
                _refuse('IMPLEMENTATION_CHANGED', 'Loaded mission class identity differs from source')
            nodes = [(node.name + '.' + n.name, n, vars(cls).get(n.name))
                     for n in node.body if isinstance(n, ast.FunctionDef)]
        for name, function_node, candidate in nodes:
            if isinstance(candidate, (staticmethod, classmethod)):
                candidate = candidate.__func__
            if not isinstance(candidate, types.FunctionType):
                _refuse('IMPLEMENTATION_CHANGED', 'Mission entrypoint is not its installed function')
            wrapped = inspect.unwrap(candidate)
            decorators = [ast.unparse(d) for d in function_node.decorator_list]
            if hasattr(candidate, '__wrapped__'):
                expected_wrapper = contextlib.contextmanager(wrapped)
                if (decorators != ['contextmanager'] or candidate.__globals__ is not vars(contextlib)
                        or candidate.__code__ is not expected_wrapper.__code__
                        or candidate.__defaults__ != expected_wrapper.__defaults__
                        or candidate.__kwdefaults__ != expected_wrapper.__kwdefaults__
                        or candidate.__closure__ is None or len(candidate.__closure__) != 1
                        or candidate.__closure__[0].cell_contents is not wrapped):
                    _refuse('IMPLEMENTATION_CHANGED', 'Mission function has an undeclared wrapper')
            elif any(d not in ('staticmethod', 'classmethod') for d in decorators):
                _refuse('IMPLEMENTATION_CHANGED', 'Mission function decorator is not source bound')
            defaults = tuple(_source_value(v, values) for v in function_node.args.defaults) or None
            kwdefaults = {arg.arg: _source_value(v, values)
                          for arg, v in zip(function_node.args.kwonlyargs, function_node.args.kw_defaults)
                          if v is not None} or None
            if (wrapped.__globals__ is not vars(module)
                    or store._hash(store._code_structure(wrapped.__code__)) != code.get(name)
                    or _encoded(_policy_value(wrapped.__defaults__)) != _encoded(_policy_value(defaults))
                    or _encoded(_policy_value(wrapped.__kwdefaults__)) != _encoded(_policy_value(kwdefaults))):
                _refuse('IMPLEMENTATION_CHANGED', 'Loaded mission function differs from installed source')
            functions[name] = {'code': code[name], 'defaults': _policy_value(defaults),
                               'kwdefaults': _policy_value(kwdefaults)}
        if isinstance(node, ast.Import):
            for item in node.names:
                if item.name not in sys.stdlib_module_names:
                    _refuse('IMPLEMENTATION_CHANGED', 'Mission import is outside the declared standard library')
                alias = item.asname or item.name
                if getattr(module, alias, None) is not importlib.import_module(item.name):
                    _refuse('IMPLEMENTATION_CHANGED', 'Loaded mission import alias was replaced')
                imports[alias] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module != '__future__':
            target = 'polyia' if node.level == 1 and node.module is None else node.module
            if node.level not in (0, 1) or target not in sys.stdlib_module_names | {'polyia'}:
                _refuse('IMPLEMENTATION_CHANGED', 'Mission dependency is not declared')
            imported = importlib.import_module(target)
            for item in node.names:
                alias = item.asname or item.name
                if getattr(module, alias, None) is not getattr(imported, item.name):
                    _refuse('IMPLEMENTATION_CHANGED', 'Loaded mission dependency alias was replaced')
                imports[alias] = target + '.' + item.name
    classes = store._extension_classes([n for n in tree.body if isinstance(n, ast.ClassDef)], module)
    if set(store._science_loaded_functions(module)) != set(functions):
        _refuse('IMPLEMENTATION_CHANGED', 'Mission implementation has undeclared functions')
    return {'module': module_name, 'sha256': hashlib.sha256(source).hexdigest(),
            'loaded_code_sha256': _digest({'functions': functions, 'policies': policies, 'imports': imports, 'classes': classes}),
            'package_version': store.__version__, 'python_version': platform.python_version(),
            'source_binding': 'PINNED_SOURCE_MATCHES_LOADED_CODE'}


def _guidance_applicability(ledger, records):
    decisions, verified_sources, integrated = [], {}, set()
    if len(records) != 75:
        _refuse('MISSION_CONTRACT_CHANGED', 'Guidance applicability census changed')
    for record in records:
        identifier = record['origin_id']
        path = record['source_path']
        if path not in verified_sources:
            data = ledger._capture_one(path, root=store.PACKAGE_ROOT)
            verified_sources[path] = data
        data = verified_sources[path]
        locator = record['locator']
        text = data[locator['byte_start']:locator['byte_end_exclusive']]
        if (hashlib.sha256(data).hexdigest() != record['source_sha256']
                or text != record['text_verbatim'].encode('utf-8')
                or hashlib.sha256(text).hexdigest() != record['text_sha256']):
            _refuse('MISSION_CONTRACT_CHANGED', 'Guidance source text no longer matches its retained inherited record')
        if identifier in GUIDANCE_INTEGRATED:
            integrated.add(identifier)
            classification, rationale = GUIDANCE_INTEGRATED[identifier]
        elif record['disposition'] == 'scoped_to_upstream' and record['source_family'] in GUIDANCE_UPSTREAM:
            classification = 'UPSTREAM_CONDITIONAL'
            rationale = ('This exact source clause remains a condition of ' + GUIDANCE_UPSTREAM[record['source_family']]
                         + '. The present verifier executes only Poly IA priority and research pause/resume; '
                         + 'it does not invoke or certify that upstream operation/product. Source scope: '
                         + record['enforcement_scope'])
        else:
            _refuse('MISSION_CONTRACT_CHANGED', 'Guidance inherited record lacks an explicit supported scope decision')
        decisions.append({'origin_id': identifier, 'source_text_sha256': record['text_sha256'],
                          'source_label': locator['label'], 'classification': classification, 'rationale': rationale})
    if integrated != set(GUIDANCE_INTEGRATED):
        _refuse('MISSION_CONTRACT_CHANGED', 'Guidance integrated applicability decisions are incomplete')
    return decisions


def prepare(ledger, requirement, state):
    """Read and bind candidate/contract inputs; no fixture execution or ledger writes."""
    identifier = requirement['id']
    if identifier not in ('PIA-042', 'PIA-040') or requirement['verifier'] != 'commission-evidence':
        _refuse('UNSUPPORTED_VERIFIER', 'No versioned mission adapter supports this requirement')
    guidance = identifier == 'PIA-040'
    adapter = GUIDANCE_ADAPTER if guidance else ADAPTER
    definition_hash = GUIDANCE_DEFINITION_SHA256 if guidance else DEFINITION_SHA256
    acceptance_hash = GUIDANCE_ACCEPTANCE_SHA256 if guidance else ACCEPTANCE_SHA256
    genesis = json.loads(ledger._conn.execute('SELECT document_json FROM genesis WHERE singleton=1').fetchone()[0])
    definition = genesis['definitions'][identifier]
    if _digest(definition) != definition_hash:
        _refuse('MISSION_CONTRACT_CHANGED', 'Mission definition is not the version supported by this adapter')
    artifacts = requirement['artifacts']
    by_path = {item['path']: item for item in artifacts}
    if set(by_path) != {path for _, path in MODULES} or len(artifacts) != len(MODULES):
        _refuse('MISSION_INPUT_MISMATCH', 'This mission adapter requires exactly its four declared implementation source files')
    implementation = []
    for module, path in MODULES:
        installed = ledger._capture_one(path, root=store.PACKAGE_ROOT)
        artifact = by_path[path]
        if ledger.get_blob(artifact['sha256']) != installed:
            _refuse('MISSION_INPUT_MISMATCH', 'Captured mission source does not match the running package')
        implementation.append({'identity': _loaded_identity(module, installed), 'source': artifact})
    registries, documents = [], []
    for path, expected_digest in REGISTRY_PINS:
        data = ledger._capture_one(path, root=store.PACKAGE_ROOT, maximum=16 * 1024 * 1024)
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected_digest:
            _refuse('MISSION_CONTRACT_CHANGED', 'The mission acceptance or inherited-applicability registry changed')
        registries.append({'path': path, 'sha256': digest, 'size': len(data)})
        documents.append(json.loads(data))
    rows = [r for r in documents[0]['requirements'] if r['requirement_id'] == identifier]
    core = [r for r in documents[1]['obligations'] if identifier in r['target_requirements']]
    supplemental = [r for r in documents[2]['records'] if identifier in r['target_obligations']]
    if len(rows) != 1 or _digest(rows[0]) != acceptance_hash or core or (supplemental and not guidance):
        _refuse('MISSION_CONTRACT_CHANGED', 'Mission acceptance or inherited conditions need a new adapter version')
    contract = {'schema_version': 1, 'adapter': adapter, 'definition': definition,
                'acceptance': rows[0], 'registries': registries,
                'inherited_applicability': {'method': 'all-target-records-v1', 'core': core,
                    'supplemental': supplemental, 'core_records_examined': len(documents[1]['obligations']),
                    'supplemental_records_examined': len(documents[2]['records'])}}
    if guidance:
        contract['inherited_applicability']['decisions'] = _guidance_applicability(ledger, supplemental)
    data = _encoded(contract)
    contract_blob = {'path': 'mission-contracts/' + ('PIA-040-guidance-effects-v1.json' if guidance else 'PIA-042-capture-v1.json'),
                     'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
    binding = {'schema_version': 1, 'adapter': adapter, 'requirement_id': identifier,
               'definition_sha256': _digest(definition), 'production_revision': requirement['produced_revision'],
               'production_actor': requirement['produced_by'], 'captured_artifacts': artifacts,
               'source_context_digest': state['source_context']['digest'],
               'implementation': implementation, 'contract': contract_blob}
    binding['digest'] = _digest(binding)
    return binding, data


def run_capture_checks():
    """Fixed finite experiment on private disposable stores, never the caller's DB."""
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'pass': bool(condition)})
        if not condition:
            raise AssertionError(name)

    with tempfile.TemporaryDirectory(prefix='polyia-pia042-') as temporary:
        root = Path(temporary)
        workspace = root / 'workspace'
        workspace.mkdir()
        database = root / 'state' / 'ledger.sqlite3'
        definitions = [{'id': 'CAPTURE', 'title': 'Disposable capture conformance fixture',
                        'verifier': 'artifact-integrity', 'scope': 'PIA-042 fixture only', 'version': 'fixture-v1'}]
        ledger = store.Ledger(database, workspace, definitions)
        counter = 0

        def command(kind, payload):
            nonlocal counter
            counter += 1
            return ledger.command({'command_id': 'fixture-' + str(counter),
                'expected_revision': ledger.state()['revision'], 'kind': kind, 'payload': payload}, actor='fixture-operator')

        def refused(kind, payload, expected):
            before = ledger.state()
            try:
                command(kind, payload)
            except store.CommandError as error:
                return error.code == expected and ledger.state() == before
            return False

        try:
            original = b'Original capture: \xce\xb1\x00\n'
            (workspace / 'capture.bin').write_bytes(original)
            receipt = command('requirement.produce', {'requirement_id': 'CAPTURE', 'artifacts': ['capture.bin']})
            artifact = receipt['result']['artifacts'][0]
            requirement = ledger.state()['requirements']['CAPTURE']
            check('actual_bytes_path_size_and_digest', ledger.get_blob(artifact['sha256']) == original
                  and artifact == {'path': 'capture.bin', 'sha256': hashlib.sha256(original).hexdigest(), 'size': len(original)})
            check('production_version_actor_and_semantic_scope', requirement['produced_revision'] == receipt['revision']
                  and requirement['produced_by'] == 'fixture-operator' and requirement['scope'] == definitions[0]['scope']
                  and requirement['version'] == 'fixture-v1')
            command('requirement.verify', {'requirement_id': 'CAPTURE'})
            command('requirement.accept', {'requirement_id': 'CAPTURE'})
            checkpoint = ledger.checkpoint('Retain accepted fixture snapshot')
            (workspace / 'capture.bin').write_bytes(b'new workspace bytes')
            report = ledger.verify()
            check('workspace_edit_is_drift_not_changed_evidence', report['ok'] and report['workspace_drift']['changed'] == 1
                  and report['workspace_drift']['artifacts'][0]['status'] == 'MODIFIED'
                  and ledger.get_blob(artifact['sha256']) == original)
            ledger.close()
            ledger = store.Ledger(database, workspace)
            check('reopen_resolves_original_snapshot', ledger.get_blob(artifact['sha256']) == original
                  and ledger.state()['requirements']['CAPTURE']['artifacts'] == [artifact])
            (workspace / 'capture.bin').unlink()
            check('missing_workspace_preserves_captured_snapshot', ledger.verify()['workspace_drift']['artifacts'][0]['status'] == 'MISSING'
                  and ledger.get_blob(artifact['sha256']) == original)
            (workspace / 'capture.bin').write_bytes(b'explicit new candidate')
            command('requirement.produce', {'requirement_id': 'CAPTURE', 'artifacts': ['capture.bin']})
            changed = ledger.state()['requirements']['CAPTURE']
            check('explicit_reproduction_creates_new_candidate', changed['status'] == 'PRODUCED'
                  and changed['verification'] is None and 'accepted_revision' not in changed
                  and changed['artifacts'][0]['sha256'] != artifact['sha256'])
            check('historical_accepted_snapshot_stays_resolvable', ledger.get_blob(artifact['sha256']) == original
                  and ledger.get_checkpoint(checkpoint['result']['checkpoint_id'])['state']['requirements']['CAPTURE']['status'] == 'ACCEPTED')
            check('stale_acceptance_refused', refused('requirement.accept', {'requirement_id': 'CAPTURE'}, 'INVALID_TRANSITION'))
            check('caller_pass_flag_refused', refused('requirement.verify', {'requirement_id': 'CAPTURE', 'outcome': 'PASS'}, 'INVALID_PAYLOAD'))
            (workspace / 'empty.txt').write_bytes(b'')
            check('empty_capture_refused', refused('requirement.produce', {'requirement_id': 'CAPTURE', 'artifacts': ['empty.txt']}, 'EMPTY_ARTIFACT'))
            check('missing_capture_rolls_back_partial_batch', refused('requirement.produce', {'requirement_id': 'CAPTURE',
                  'artifacts': ['capture.bin', 'missing.txt']}, 'MISSING_ARTIFACT') and ledger.verify()['ok'])
            (root / 'outside.txt').write_bytes(b'outside')
            (workspace / 'escape.txt').symlink_to(root / 'outside.txt')
            check('symlink_capture_refused', refused('requirement.produce', {'requirement_id': 'CAPTURE', 'artifacts': ['escape.txt']}, 'UNSAFE_ARTIFACT'))
            check('path_traversal_refused', refused('requirement.produce', {'requirement_id': 'CAPTURE', 'artifacts': ['../outside.txt']}, 'UNSAFE_ARTIFACT'))
            with (workspace / 'oversized.bin').open('wb') as stream:
                stream.truncate(store.MAX_ARTIFACT_BYTES + 1)
            check('oversized_capture_refused_before_read', refused('requirement.produce', {'requirement_id': 'CAPTURE', 'artifacts': ['oversized.bin']}, 'RESOURCE_LIMIT'))
            with contextlib.closing(sqlite3.connect(database)) as connection:
                with connection:
                    connection.execute('UPDATE blobs SET data=? WHERE digest=?', (b'corrupted fixture', artifact['sha256']))
            check('captured_blob_corruption_detected', ledger.verify()['ok'] is False)
            ledger.close()
            try:
                invalid = store.Ledger(database, workspace)
            except store.CommandError as error:
                check('corrupt_snapshot_cannot_reopen', error.code == 'INTEGRITY_ERROR')
            else:
                invalid.close()
                check('corrupt_snapshot_cannot_reopen', False)
        except AssertionError as error:
            checks.append({'name': 'fixture_assertion', 'pass': False, 'reason': str(error)})
        finally:
            ledger.close()
    return {'status': 'PASS' if checks and all(c['pass'] for c in checks) else 'FAIL',
            'evidence_class': 'SOFTWARE_CONFORMANCE', 'checks': checks,
            'result': {'adapter': ADAPTER, 'fixture_scope': 'fresh disposable SQLite ledgers',
                       'command': 'polyia.mission_verifiers.run_capture_checks',
                       'python': platform.python_version(), 'sqlite': sqlite3.sqlite_version},
            'limitations': ['Finite software conformance checks, not proof over every filesystem or crash schedule.',
                            'Interpreter, standard library, installed verifier and privileged host remain trusted.',
                            'No live deployment, unrelated mission or scientific content is certified.']}


def run_guidance_checks():
    """Independent finite driver: literal expected effects, real isolated commands."""
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'pass': bool(condition)})
        if not condition:
            raise AssertionError(name)

    with tempfile.TemporaryDirectory(prefix='polyia-pia040-') as temporary:
        root = Path(temporary)
        workspace = root / 'workspace'
        workspace.mkdir()
        database = root / 'state' / 'ledger.sqlite3'
        ledger = store.Ledger(database, workspace, [
            {'id': 'TARGET', 'title': 'Guidance fixture target', 'verifier': 'artifact-integrity'}])
        peer = store.Ledger(database, workspace)
        counter = 0

        def request(kind, payload):
            nonlocal counter
            counter += 1
            return {'command_id': 'guidance-fixture-' + str(counter),
                    'expected_revision': ledger.state()['revision'], 'kind': kind, 'payload': payload}

        def command(kind, payload):
            return ledger.command(request(kind, payload), actor='fixture-operator')

        def refused(kind, payload, expected, scopes=('command',)):
            before = ledger.state()
            try:
                ledger.command(request(kind, payload), actor='fixture-operator', scopes=scopes)
            except store.CommandError as error:
                return error.code == expected and ledger.state() == before
            return False

        def submit(target, text, action=None):
            payload = {'target': target, 'text': text}
            if action is not None:
                payload['action'] = action
            return command('guidance.submit', payload)['result']['guidance_id']

        def acknowledge(identifier, disposition='ACKNOWLEDGED'):
            return command('guidance.ack', {'guidance_id': identifier, 'disposition': disposition,
                                           'reason': 'Explicit fixture review'})

        try:
            priority = submit('TARGET', 'Priorité / أولوية', {'kind': 'set_priority', 'target': 'TARGET', 'priority': 7})
            submitted = peer.state()['guidance'][priority]
            check('submission_is_not_application', submitted['status'] == 'SUBMITTED'
                  and submitted['text'] == 'Priorité / أولوية' and submitted['effects'] == []
                  and peer.state()['requirements']['TARGET']['priority'] == 5)
            check('unacknowledged_cannot_apply', refused('guidance.apply', {'guidance_id': priority}, 'INVALID_TRANSITION'))
            acknowledge(priority)
            acknowledged = peer.state()['guidance'][priority]
            check('acknowledgement_is_not_application', acknowledged['status'] == 'ACKNOWLEDGED'
                  and acknowledged['effects'] == [] and acknowledged['applied_revision'] is None
                  and peer.state()['requirements']['TARGET']['priority'] == 5)
            apply_request = request('guidance.apply', {'guidance_id': priority})
            applied = ledger.command(apply_request, actor='fixture-operator')
            expected = [{'path': 'requirements.TARGET.priority', 'before': 5, 'after': 7}]
            observed = peer.state()['guidance'][priority]
            check('priority_effect_and_revision_are_exact', peer.state()['requirements']['TARGET']['priority'] == 7
                  and applied['result']['effects'] == expected and observed['effects'] == expected
                  and observed['status'] == 'APPLIED' and observed['applied_revision'] == applied['revision']
                  and observed['applied_by'] == 'fixture-operator')
            before_retry = ledger.state()
            check('exact_apply_retry_returns_original_without_effect', ledger.command(apply_request, actor='fixture-operator') == applied
                  and ledger.state() == before_retry)
            check('applied_guidance_cannot_apply_twice', refused('guidance.apply', {'guidance_id': priority}, 'INVALID_TRANSITION'))
            advice = submit('research', 'Free text is context; never execute shell or export corpus bytes.')
            acknowledge(advice)
            check('text_only_cannot_apply', refused('guidance.apply', {'guidance_id': advice}, 'NO_APPLICABLE_ACTION'))
            deferred = submit('TARGET', 'deferred', {'kind': 'set_priority', 'target': 'TARGET', 'priority': 1})
            acknowledge(deferred, 'DEFERRED')
            check('deferred_cannot_apply', refused('guidance.apply', {'guidance_id': deferred}, 'INVALID_TRANSITION'))
            acknowledge(deferred, 'REJECTED')
            check('rejected_cannot_apply', refused('guidance.apply', {'guidance_id': deferred}, 'INVALID_TRANSITION'))
            check('unsupported_external_effect_not_admitted', refused('guidance.submit', {'target': 'research',
                  'text': 'export', 'action': {'kind': 'export_source'}}, 'UNSUPPORTED_ACTION'))
            check('mismatched_target_not_admitted', refused('guidance.submit', {'target': 'research', 'text': 'wrong target',
                  'action': {'kind': 'set_priority', 'target': 'TARGET', 'priority': 2}}, 'INVALID_PAYLOAD'))
            check('boolean_priority_not_an_integer', refused('guidance.submit', {'target': 'TARGET', 'text': 'bad priority',
                  'action': {'kind': 'set_priority', 'target': 'TARGET', 'priority': True}}, 'INVALID_PAYLOAD'))
            check('read_scope_cannot_apply', refused('guidance.apply', {'guidance_id': advice}, 'FORBIDDEN', ('read',)))
            pause = submit('research', 'pause', {'kind': 'pause_research'})
            acknowledge(pause)
            paused = command('guidance.apply', {'guidance_id': pause})
            check('pause_changes_actual_state', peer.state()['research']['paused'] is True
                  and paused['result']['effects'] == [{'path': 'research.paused', 'before': False, 'after': True}]
                  and peer.state()['guidance'][pause]['applied_revision'] == paused['revision'])
            check('pause_blocks_real_registered_work', refused('experiment.run', {'name': 'polynomial', 'parameters': {}}, 'RESEARCH_PAUSED'))
            checkpoint = ledger.checkpoint('Paused guidance fixture')
            paused_state = ledger.state()
            peer.close()
            ledger.close()
            ledger = store.Ledger(database, workspace)
            peer = store.Ledger(database, workspace)
            check('restart_preserves_pause_effects_and_history', ledger.state() == paused_state
                  and peer.get_checkpoint(checkpoint['result']['checkpoint_id'])['state']['research']['paused'] is True
                  and ledger.verify()['ok'])
            resume = submit('research', 'resume', {'kind': 'resume_research'})
            acknowledge(resume)
            resumed = command('guidance.apply', {'guidance_id': resume})
            check('resume_changes_actual_state', peer.state()['research']['paused'] is False
                  and resumed['result']['effects'] == [{'path': 'research.paused', 'before': True, 'after': False}]
                  and peer.state()['guidance'][resume]['applied_revision'] == resumed['revision'])
            run = command('experiment.run', {'name': 'polynomial', 'parameters': {}})['result']['run']
            check('resumed_registered_work_really_executes', run['report']['status'] == 'PASS'
                  and bool(run['report']['checks']) and all(c['pass'] for c in run['report']['checks']))
            left = submit('TARGET', 'race left', {'kind': 'set_priority', 'target': 'TARGET', 'priority': 3})
            right = submit('TARGET', 'race right', {'kind': 'set_priority', 'target': 'TARGET', 'priority': 9})
            acknowledge(left)
            acknowledge(right)
            revision = ledger.state()['revision']
            barrier = threading.Barrier(2, timeout=5)
            outcomes = []

            def race(connection, identifier, value):
                try:
                    barrier.wait()
                    receipt = connection.command({'command_id': 'race-' + identifier, 'expected_revision': revision,
                        'kind': 'guidance.apply', 'payload': {'guidance_id': identifier}}, actor='fixture-' + identifier)
                    outcomes.append(('PASS', value, receipt))
                except store.CommandError as error:
                    outcomes.append((error.code, value, None))
                except Exception as error:
                    outcomes.append((type(error).__name__, value, None))

            threads = [threading.Thread(target=race, args=(ledger, left, 3)),
                       threading.Thread(target=race, args=(peer, right, 9))]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(20)
            check('two_connection_race_has_one_admitted_effect', not any(t.is_alive() for t in threads)
                  and sorted(item[0] for item in outcomes) == ['PASS', 'REVISION_CONFLICT']
                  and ledger.state()['revision'] == revision + 1)
            winner = next(item for item in outcomes if item[0] == 'PASS')
            check('race_receipt_matches_observed_priority', peer.state()['requirements']['TARGET']['priority'] == winner[1]
                  and winner[2]['result']['effects'] == [{'path': 'requirements.TARGET.priority', 'before': 7, 'after': winner[1]}])
            check('guidance_history_replays_consistently', ledger.verify()['ok'] and peer.verify()['ok'])
        except AssertionError as error:
            checks.append({'name': 'fixture_assertion', 'pass': False, 'reason': str(error)})
        finally:
            peer.close()
            ledger.close()
    return {'status': 'PASS' if checks and all(c['pass'] for c in checks) else 'FAIL',
            'evidence_class': 'SOFTWARE_CONFORMANCE', 'checks': checks,
            'result': {'adapter': GUIDANCE_ADAPTER, 'fixture_scope': 'two connections to disposable SQLite ledgers',
                       'command': 'polyia.mission_verifiers.run_guidance_checks',
                       'python': platform.python_version(), 'sqlite': sqlite3.sqlite_version},
            'limitations': ['Finite guidance effect checks with explicit literal expectations; not a proof over all schedules.',
                            'No HTTP, browser, Codex polling loop or upstream product compatibility is certified.',
                            'Mapped source conditions remain scoped; historical scientific tests are not counted as fresh passes.',
                            'Interpreter, standard library, installed verifier and privileged host remain trusted.']}
