"""Fixed Bubblewrap entrypoint. Never imports or evaluates caller Python code."""
import errno
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time


class BudgetLimit(Exception):
    pass


def _cpu_limit(signum, frame):
    raise BudgetLimit('CPU_LIMIT')


def main():
    request_bytes = Path('/input/request.json').read_bytes()
    if len(request_bytes) > 32768:
        raise ValueError('Fixed worker input exceeds its byte limit')
    request = json.loads(request_bytes)
    limits = request['budgets']
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    resource.setrlimit(resource.RLIMIT_FSIZE, (4096, 4096))
    resource.setrlimit(resource.RLIMIT_AS, (limits['memory_bytes'], limits['memory_bytes']))
    resource.setrlimit(resource.RLIMIT_CPU, (limits['cpu_seconds'], limits['cpu_seconds'] + 1))
    signal.signal(signal.SIGXCPU, _cpu_limit)
    observed = {'pid': os.getpid(), 'environment_names': sorted(os.environ),
                'visible_fds': sorted(int(p) for p in os.listdir('/proc/self/fd')),
                'namespaces': {name: os.readlink('/proc/self/ns/' + name) for name in ('mnt', 'net', 'pid', 'user')},
                'network_interfaces': sorted(line.split(':')[0].strip() for line in Path('/proc/net/dev').read_text().splitlines()[2:]),
                'effective_capabilities': next(line.split()[1] for line in Path('/proc/self/status').read_text().splitlines()
                                               if line.startswith('CapEff:')),
                'python': sys.version.split()[0], 'input_sha256': hashlib.sha256(request_bytes).hexdigest(),
                'sources': {name: hashlib.sha256(Path('/app/' + name).read_bytes()).hexdigest()
                            for name in ('polyia/native.py', 'polyia/__init__.py', 'isolated_worker.py')}}
    result = {'status': 'ERROR', 'worker': observed}
    try:
        mode = request['mode']
        if mode == 'native':
            sys.path.insert(0, '/app')
            from polyia.native import compile_program, execute_program
            compiled = compile_program(request['source'])
            if not compiled['ok']:
                result.update(status='REFUSED', result=compiled)
            else:
                execution = execute_program(compiled['program'])
                result.update(status='PASS' if execution['ok'] else 'REFUSED', result=execution)
        elif mode == 'probe_read':
            try:
                descriptor = os.open(request['path'], os.O_RDONLY | os.O_NONBLOCK)
            except OSError as error:
                if error.errno in (errno.ENOENT, errno.EACCES, errno.EPERM):
                    result.update(status='READ_DENIED', denied_resource=request['path'],
                                  denial_errno=errno.errorcode[error.errno])
                else:
                    result.update(status='ERROR', reason='READ_PROBE_FAILED')
            else:
                os.close(descriptor)
                result.update(status='ERROR', reason='WITNESS_READ_ALLOWED', denied_resource=request['path'])
        elif mode == 'control_wall':
            time.sleep(60)
        elif mode == 'control_cpu':
            while True:
                pass
        elif mode == 'control_memory':
            bytearray(limits['memory_bytes'] * 2)
        elif mode == 'control_output':
            while True:
                os.write(1, b'x' * 4096)
        else:
            result.update(status='REFUSED', reason='UNREGISTERED_WORKER_MODE')
    except BudgetLimit as error:
        result.update(status='RESOURCE_LIMIT', reason=str(error))
    except MemoryError:
        result.update(status='RESOURCE_LIMIT', reason='MEMORY_LIMIT')
    except Exception as error:
        # Exception text can contain input data; never echo it into diagnostics.
        result.update(status='ERROR', reason='WORKER_EXCEPTION', exception_type=type(error).__name__)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
