"""Explicit Linux/Bubblewrap read boundary for the fixed native engine.

This optional operator tool never falls back to unsandboxed execution. It is
not the experiment seal/witness lifecycle or a general arbitrary-code runner.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time

BWRAP = '/usr/bin/bwrap'
RUNTIME = '/opt/polyia/runtime'
POLICY = 'polyia.native-bwrap/0.1'
DEFAULT_BUDGETS = {'wall_seconds': 5.0, 'cpu_seconds': 2,
                   'memory_bytes': 256 * 1024 * 1024, 'output_bytes': 256 * 1024}
SOURCE_FILES = ('polyia/native.py', 'polyia/__init__.py', 'polyia/isolated_worker.py')
NATIVE_IMPORTS = {'fractions', 'hashlib', 'json', 're', 'argparse', 'sys'}


def _error(status, reason):
    return {'status': status, 'reason': reason, 'policy': {'name': POLICY},
            'llm_inference': False, 'independent_scientific_witness': False}


def _budgets(requested):
    if requested is not None and (type(requested) is not dict or set(requested) - set(DEFAULT_BUDGETS)):
        raise ValueError('Budget schema')
    limits = dict(DEFAULT_BUDGETS, **(requested or {}))
    wall = limits['wall_seconds']
    if type(wall) not in (int, float) or not math.isfinite(wall) or not 0.1 <= wall <= 30:
        raise ValueError('Wall budget')
    for key, low, high in (('cpu_seconds', 1, 10), ('memory_bytes', 64 * 1024 * 1024, 512 * 1024 * 1024),
                           ('output_bytes', 1024, 4 * 1024 * 1024)):
        if type(limits[key]) is not int or not low <= limits[key] <= high:
            raise ValueError('Resource budget')
    return limits


def _libraries():
    architecture = platform.machine()
    if architecture == 'aarch64':
        return [('/lib/aarch64-linux-gnu', '/lib/aarch64-linux-gnu'),
                ('/lib/ld-linux-aarch64.so.1', '/lib/ld-linux-aarch64.so.1')]
    if architecture == 'x86_64':
        return [('/lib/x86_64-linux-gnu', '/lib/x86_64-linux-gnu'),
                ('/lib64/ld-linux-x86-64.so.2', '/lib64/ld-linux-x86-64.so.2')]
    return []


def _read_fixed_sources():
    root = Path(__file__).resolve().parent.parent
    sources = {}
    for path in SOURCE_FILES:
        with (root / path).open('rb') as stream:
            data = stream.read(1024 * 1024 + 1)
        if not data or len(data) > 1024 * 1024:
            raise ValueError('Fixed source budget')
        sources[path] = data
    tree = ast.parse(sources['polyia/native.py'])
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module] if node.level == 0 else [None]
        else:
            continue
        if not set(names) <= NATIVE_IMPORTS:
            raise ValueError('Undeclared native constructor dependency')
    package = ast.parse(sources['polyia/__init__.py'])
    if any(not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and type(node.value.value) is str)
           and not (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name) and node.targets[0].id == '__version__'
                    and isinstance(node.value, ast.Constant) and type(node.value.value) is str)
           for node in package.body):
        raise ValueError('Package initializer has undeclared execution')
    return sources


def _terminate(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=5)


def _descendants(pid):
    """Observe only this launched process tree; fixed workers never spawn jobs."""
    found, pending = set(), [pid]
    while pending and len(found) < 32:
        parent = pending.pop()
        try:
            children = Path(f'/proc/{parent}/task/{parent}/children').read_text().split()
        except OSError:
            continue
        for child in children[:32]:
            if child.isdigit() and int(child) not in found:
                found.add(int(child))
                pending.append(int(child))
    return found


def _supervise(command, limits):
    started = time.monotonic()
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env={}, close_fds=True, start_new_session=True, cwd='/')
    buffers = {process.stdout: bytearray(), process.stderr: bytearray()}
    selector = selectors.DefaultSelector()
    for stream in buffers:
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ)
    reason, count, descendants = None, 0, set()
    try:
        while selector.get_map():
            descendants.update(_descendants(process.pid))
            remaining = limits['wall_seconds'] - (time.monotonic() - started)
            if remaining <= 0:
                reason = 'WALL_LIMIT'
                break
            for key, _ in selector.select(min(remaining, 0.1)):
                data = os.read(key.fileobj.fileno(), 4096)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                count += len(data)
                if count > limits['output_bytes']:
                    reason = 'OUTPUT_LIMIT'
                    break
                buffers[key.fileobj].extend(data)
            if reason:
                break
        descendants.update(_descendants(process.pid))
        if reason:
            _terminate(process)
        else:
            remaining = limits['wall_seconds'] - (time.monotonic() - started)
            try:
                process.wait(timeout=max(0.001, remaining))
            except subprocess.TimeoutExpired:
                reason = 'WALL_LIMIT'
                _terminate(process)
        # --die-with-parent and the private PID namespace terminate the worker
        # when Bubblewrap dies. Observe cleanup as well as wait/reap our child.
        cleanup_deadline = time.monotonic() + 1
        while any(Path(f'/proc/{pid}').exists() for pid in descendants) and time.monotonic() < cleanup_deadline:
            time.sleep(0.01)
        descendants_gone = not any(Path(f'/proc/{pid}').exists() for pid in descendants)
        return (bytes(buffers[process.stdout]), bytes(buffers[process.stderr]), reason,
                {'pid': process.pid, 'exit_code': process.returncode, 'reaped': process.poll() is not None,
                 'observed_descendant_pids': sorted(descendants), 'observed_descendants_gone': descendants_gone,
                 'wall_seconds': time.monotonic() - started, 'observed_output_bytes': count})
    finally:
        selector.close()
        if process.poll() is None:
            _terminate(process)
        for stream in buffers:
            stream.close()


def _run(mode, payload, budgets):
    try:
        limits = _budgets(budgets)
    except (ValueError, TypeError):
        return _error('REFUSED', 'INVALID_BUDGET')
    libraries = _libraries()
    executable = Path(RUNTIME) / 'bin/python3'
    if sys.platform != 'linux' or not libraries or not Path(BWRAP).is_file() or not executable.is_file():
        return _error('UNAVAILABLE', 'LINUX_BWRAP_RUNTIME_REQUIRED')
    try:
        for path in [Path(BWRAP), Path(RUNTIME), executable] + [Path(source) for source, _ in libraries]:
            metadata = path.stat()
            if metadata.st_uid != 0 or metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                return _error('UNAVAILABLE', 'UNTRUSTED_PLATFORM_GRANT')
        sources = _read_fixed_sources()
        with Path(__file__).open('rb') as stream:
            controller_source = stream.read(1024 * 1024 + 1)
        if not controller_source or len(controller_source) > 1024 * 1024:
            raise ValueError('Controller source budget')
        binary_digest = hashlib.sha256(executable.read_bytes()).hexdigest()
        bwrap_digest = hashlib.sha256(Path(BWRAP).read_bytes()).hexdigest()
    except (OSError, ValueError, SyntaxError):
        return _error('UNAVAILABLE', 'FIXED_DEPENDENCY_UNAVAILABLE')
    request = dict(payload, mode=mode, budgets=limits)
    encoded = json.dumps(request, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
    if len(encoded) > 32768:
        return _error('REFUSED', 'INPUT_TOO_LARGE')
    with tempfile.TemporaryDirectory(prefix='polyia-native-isolation-') as temporary:
        stage = Path(temporary)
        (stage / 'app/polyia').mkdir(parents=True)
        (stage / 'input').mkdir()
        for path, data in sources.items():
            target = stage / 'app' / ('isolated_worker.py' if path.endswith('/isolated_worker.py') else path)
            target.write_bytes(data)
            target.chmod(0o400)
        (stage / 'input/request.json').write_bytes(encoded)
        (stage / 'input/request.json').chmod(0o400)
        command = [BWRAP, '--unshare-all', '--unshare-user', '--unshare-pid', '--unshare-net',
                   '--die-with-parent', '--new-session', '--cap-drop', 'ALL', '--clearenv',
                   '--setenv', 'LANG', 'C.UTF-8', '--hostname', 'polyia-isolated',
                   '--ro-bind', RUNTIME, '/runtime', '--dir', '/lib', '--dir', '/lib64']
        for source, destination in libraries:
            command.extend(['--ro-bind', source, destination])
        command.extend(['--ro-bind', str(stage / 'app'), '/app', '--ro-bind', str(stage / 'input'), '/input',
                        '--proc', '/proc', '--dev', '/dev', '--chdir', '/app', '--remount-ro', '/', '--',
                        '/runtime/bin/python3', '-I', '-S', '-B', '/app/isolated_worker.py'])
        try:
            stdout, stderr, limited, process = _supervise(command, limits)
        except OSError:
            return _error('UNAVAILABLE', 'SANDBOX_LAUNCH_FAILED')
    report = _error('ERROR', 'WORKER_PROTOCOL_ERROR')
    report.update(process=process, budgets=limits,
                  controller={'path': 'polyia/isolation.py', 'sha256': hashlib.sha256(controller_source).hexdigest(),
                              'size': len(controller_source), 'scope': 'source-file identity; loaded controller remains trusted'},
                  implementation=[{'path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
                                  for path, data in sources.items()],
                  input_sha256=hashlib.sha256(encoded).hexdigest(),
                  runtime={'path': RUNTIME, 'executable_sha256': binary_digest,
                           'bubblewrap_sha256': bwrap_digest, 'architecture': platform.machine()},
                  policy={'name': POLICY, 'readonly_grants': ['/runtime', '/app', '/input'] + [target for _, target in libraries],
                          'private_kernel_views': ['/proc', '/dev'], 'network': 'private namespace; no host interfaces',
                          'host_home_workspace_witness_dbus': 'not mounted', 'environment': 'cleared; LANG=C.UTF-8',
                          'capabilities': 'all dropped', 'inherited_descriptors': 'closed except stdio'},
                  dependency_roles={'native_compiler_vm': 'constructor', 'fractions.Fraction': 'constructor arithmetic',
                                    'native_ast_evaluator': 'shared-dependency internal consistency check'},
                  limitations=['Optional Linux read boundary for fixed trusted native code; not an arbitrary-code security service.',
                               'Kernel, Bubblewrap, interpreter, standard library and readonly platform libraries remain trusted.',
                               'No independent post-seal witness, experiment lifecycle, worker queue or mission acceptance is implemented.',
                               'CPU/address-space limits start in the fixed worker; parent wall/output limits also cover startup.'])
    if not process['observed_descendants_gone']:
        report.update(status='ERROR', reason='PROCESS_CLEANUP_INCOMPLETE')
        return report
    if limited:
        report.update(status='RESOURCE_LIMIT', reason=limited)
        return report
    try:
        child = json.loads(stdout)
        expected_sources = {('isolated_worker.py' if path.endswith('/isolated_worker.py') else path): hashlib.sha256(data).hexdigest()
                            for path, data in sources.items()}
        if (type(child) is not dict or child.get('status') not in ('PASS', 'REFUSED', 'READ_DENIED', 'RESOURCE_LIMIT', 'ERROR')
                or type(child.get('worker')) is not dict
                or child['worker'].get('input_sha256') != report['input_sha256']
                or child['worker'].get('sources') != expected_sources or process['exit_code'] != 0):
            return report
        report.pop('reason', None)
        report.update(child)
        return report
    except (ValueError, UnicodeError, TypeError):
        if stderr.startswith(b'bwrap:'):
            report.update(status='UNAVAILABLE', reason='NAMESPACE_SETUP_FAILED')
        elif process['exit_code'] in (-signal.SIGXCPU, -signal.SIGKILL, 128 + signal.SIGXCPU, 128 + signal.SIGKILL):
            report.update(status='RESOURCE_LIMIT', reason='CPU_HARD_LIMIT_OR_EXTERNAL_SIGNAL')
        return report


def run_native(source, *, budgets=None):
    if type(source) is not str:
        return _error('REFUSED', 'NATIVE_SOURCE_REQUIRED')
    try:
        if not source.strip() or len(source.encode('utf-8')) > 16384:
            return _error('REFUSED', 'SOURCE_BYTE_LIMIT')
    except UnicodeError:
        return _error('REFUSED', 'INVALID_UNICODE')
    return _run('native', {'source': source}, budgets)


def probe_read(path, *, budgets=None):
    if type(path) is not str or not path.startswith('/') or '\x00' in path or len(path) > 4096:
        return _error('REFUSED', 'ABSOLUTE_WITHHELD_PATH_REQUIRED')
    try:
        path.encode('utf-8')
        candidate = Path(path).resolve()
        granted = [Path(RUNTIME).resolve()] + [Path(source).resolve() for source, _ in _libraries()]
        aliases = [Path(name) for name in ('/runtime', '/app', '/input', '/lib', '/lib64', '/proc', '/dev')]
        if any(candidate == base or candidate.is_relative_to(base) for base in granted + aliases):
            return _error('REFUSED', 'PROBE_OVERLAPS_DECLARED_GRANT')
        if not candidate.is_file():
            return _error('REFUSED', 'WITHHELD_REGULAR_FILE_REQUIRED')
    except (OSError, RuntimeError, UnicodeError):
        return _error('REFUSED', 'WITHHELD_REGULAR_FILE_REQUIRED')
    return _run('probe_read', {'path': str(candidate)}, budgets)


def run_control(name, *, budgets=None):
    """Explicit fixed negative controls; no caller-supplied executable or script."""
    if name not in ('wall', 'cpu', 'memory', 'output'):
        return _error('REFUSED', 'UNREGISTERED_CONTROL')
    return _run('control_' + name, {}, budgets)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Explicit fixed native Bubblewrap runner; no unsandboxed fallback')
    parser.add_argument('mode', choices=('native', 'probe'))
    parser.add_argument('--path', help='Host witness path for the fixed read-denial control; never mounted')
    arguments = parser.parse_args()
    if arguments.mode == 'native':
        try:
            source = sys.stdin.buffer.read(16385).decode('utf-8')
            report = run_native(source)
        except UnicodeError:
            report = _error('REFUSED', 'INVALID_UNICODE')
    else:
        report = probe_read(arguments.path)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0 if report['status'] in ('PASS', 'READ_DENIED') else 2


if __name__ == '__main__':
    raise SystemExit(main())
