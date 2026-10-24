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
import types

from . import store


ADAPTER = 'PIA-042/capture-v1'
DEFINITION_SHA256 = '8988319b1135f79a4b567fe3e6604cca5e1db46e1b3f7fc463dcfd2bc8601442'
ACCEPTANCE_SHA256 = 'fc18a113742adfc8ade15524309fc988f2dc4d1b051bc4a856590b0d9758b1e8'
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


def prepare(ledger, requirement, state):
    """Read and bind candidate/contract inputs; no fixture execution or ledger writes."""
    if requirement['id'] != 'PIA-042' or requirement['verifier'] != 'commission-evidence':
        _refuse('UNSUPPORTED_VERIFIER', 'This mission adapter only supports PIA-042')
    genesis = json.loads(ledger._conn.execute('SELECT document_json FROM genesis WHERE singleton=1').fetchone()[0])
    definition = genesis['definitions']['PIA-042']
    if _digest(definition) != DEFINITION_SHA256:
        _refuse('MISSION_CONTRACT_CHANGED', 'PIA-042 definition is not the version supported by this adapter')
    artifacts = requirement['artifacts']
    by_path = {item['path']: item for item in artifacts}
    if set(by_path) != {path for _, path in MODULES} or len(artifacts) != len(MODULES):
        _refuse('MISSION_INPUT_MISMATCH', 'PIA-042 requires exactly its four declared implementation source files')
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
    rows = [r for r in documents[0]['requirements'] if r['requirement_id'] == 'PIA-042']
    core = [r for r in documents[1]['obligations'] if 'PIA-042' in r['target_requirements']]
    supplemental = [r for r in documents[2]['records'] if 'PIA-042' in r['target_obligations']]
    if len(rows) != 1 or _digest(rows[0]) != ACCEPTANCE_SHA256 or core or supplemental:
        _refuse('MISSION_CONTRACT_CHANGED', 'PIA-042 acceptance or inherited conditions need a new adapter version')
    contract = {'schema_version': 1, 'adapter': ADAPTER, 'definition': definition,
                'acceptance': rows[0], 'registries': registries,
                'inherited_applicability': {'method': 'all-target-records-v1', 'core': core,
                    'supplemental': supplemental, 'core_records_examined': len(documents[1]['obligations']),
                    'supplemental_records_examined': len(documents[2]['records'])}}
    data = _encoded(contract)
    contract_blob = {'path': 'mission-contracts/PIA-042-capture-v1.json',
                     'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
    binding = {'schema_version': 1, 'adapter': ADAPTER, 'requirement_id': 'PIA-042',
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
