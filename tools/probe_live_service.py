#!/usr/bin/env python3
"""Exercise an installed service over HTTPS; never print authentication values.

Run as the deployment operator with POLYIA_* secrets in the environment.
The caller owns service restart and consistent backup operations. This probe
does not certify the full mission or production hosting.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request
import uuid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--service', default='polyia.service')
    args = parser.parse_args()
    assert args.origin.startswith('https://') and args.origin.count('/') == 2
    operator = os.environ['POLYIA_OPERATOR_TOKEN']
    reader = os.environ['POLYIA_READ_TOKEN']
    checks = []
    requests = []
    prefix = 'live-' + uuid.uuid4().hex

    def request(path, token=None, body=None, expected=200):
        headers = {'Authorization': 'Bearer ' + token} if token else {}
        if body is not None:
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(args.origin + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read()
        assert status == expected, (path, status, expected)
        return json.loads(raw)

    def state():
        return request('/v1/state', reader)

    def command(kind, payload):
        body = {'command_id': prefix + '-' + str(len(requests)),
                'expected_revision': state()['revision'],
                'kind': kind, 'payload': payload}
        result = request('/v1/commands', operator, body)
        requests.append({'request': body, 'receipt': result})
        return result

    def check(name, condition):
        assert condition, name
        checks.append({'name': name, 'pass': True})

    args.artifacts.mkdir(parents=True, exist_ok=True)
    discovery = request('/.well-known/polyia.json')
    check('actual HTTPS discovery', discovery['protocol_version'] == '1.0.0')
    check('declared no inference', discovery['capabilities']['llm_inference'] is False)
    request('/v1/state', expected=401)
    checks.append({'name': 'unauthenticated state refused', 'pass': True})
    start = state()
    request('/v1/commands', reader, {'command_id': prefix + '-denied',
        'expected_revision': start['revision'], 'kind': 'checkpoint.create',
        'payload': {}}, expected=403)
    check('observer mutation refused without semantic change', state()['revision'] == start['revision'])
    check('polling is observational', state()['revision'] == state()['revision'])

    submitted = command('guidance.submit', {'target': 'PIA-008',
        'text': 'Commissioning operator applies the owner directive: prioritize the actual live service and retain full mission NOT_COMMISSIONED.',
        'action': {'kind': 'set_priority', 'target': 'PIA-008', 'priority': 9}})
    gid = submitted['command_id']
    command('guidance.ack', {'guidance_id': gid, 'disposition': 'ACKNOWLEDGED',
        'reason': 'Read current owner directive and GOD_SEED PIA-008; actual target service is running.'})
    command('guidance.apply', {'guidance_id': gid})
    after = state()
    check('guidance actually applied', after['guidance'][gid]['status'] == 'APPLIED'
        and after['requirements']['PIA-008']['priority'] == 9)

    for target, text in [
        ('PIA-037', 'Inspect the actual supplied HTTPS address and preserve checkpoint continuity. A tunnel address may change; source gates do not invent a permanent-domain or minimum-uptime condition.'),
        ('PIA-015', 'DEC-004 resolves Book of Forms as a new construction under the owner clarification. Inspect the constructed book and its executed exercises; retained prior books remain distinct.')]:
        receipt = command('guidance.submit', {'target': target, 'text': text})
        command('guidance.ack', {'guidance_id': receipt['command_id'], 'disposition': 'ACKNOWLEDGED',
            'reason': 'Current owner clarification and source-based gate audit incorporated; text records do not claim an executable applied effect.'})

    code = (args.release / 'polyia/experiments.py').read_bytes()
    (args.artifacts / 'initial-kernel.py').write_bytes(code)
    run = command('experiment.run', {'name': 'acceptance', 'parameters': {}})
    check('registered exact seed run', run['result']['run']['report']['status'] == 'PASS')
    (args.artifacts / 'initial-science-run.json').write_text(json.dumps(run, indent=2) + '\n')
    for rid, paths in [('BOOT-001', ['initial-science-run.json']),
                       ('BOOT-002', ['initial-kernel.py', 'initial-science-run.json'])]:
        command('requirement.produce', {'requirement_id': rid, 'artifacts': paths,
            'note': 'Scoped live bootstrap check only; full mission gates remain open.'})
        verified = command('requirement.verify', {'requirement_id': rid})
        check(rid + ' actual verifier passed', verified['result']['verification']['outcome'] == 'PASS')
        command('requirement.accept', {'requirement_id': rid})
    cp = command('checkpoint.create', {'note': 'Actual Oracle service HTTPS commissioning checkpoint; source-linked bootstrap evidence only. GOD_SEED PIA-008/020/181.'})
    before = state()
    old_checkpoint = request('/v1/checkpoints/latest', reader)
    check('checkpoint sources captured', before['source_context']['status'] == 'SOURCED')
    pid_before = subprocess.check_output(['systemctl', 'show', args.service, '-p', 'MainPID', '--value'], text=True).strip()
    subprocess.run(['systemctl', 'restart', args.service], check=True)
    for attempt in range(30):
        try:
            after = state()
            break
        except (OSError, AssertionError):
            time.sleep(0.5)
    else:
        raise AssertionError('Service did not recover after restart')
    pid_after = subprocess.check_output(['systemctl', 'show', args.service, '-p', 'MainPID', '--value'], text=True).strip()
    check('actual supervised process restart', pid_before != pid_after and pid_after != '0')
    check('restart preserves revision and event head', (before['revision'], before['head']) == (after['revision'], after['head']))
    check('restart preserves checkpoint bytes', old_checkpoint == request('/v1/checkpoints/latest', reader))
    check('lost-response exact retry returns original receipt', request('/v1/commands', operator, requests[-1]['request']) == cp)
    check('retry did not apply twice', state()['revision'] == before['revision'])
    integrity = request('/v1/verify', reader)
    check('full ledger integrity', integrity['ok'] is True)
    check('bootstrap does not commission mission', after['commission_status'] == 'NOT_COMMISSIONED')
    report = {'schema_version': 1, 'run_id': prefix, 'result': 'PASS',
        'scope': 'Actual target HTTPS commissioning service probe; not production hosting or full commission acceptance',
        'origin': args.origin, 'protocol_version': discovery['protocol_version'],
        'host': platform.node(), 'python': platform.python_version(), 'sqlite': sqlite3.sqlite_version,
        'release': str(args.release), 'kernel_sha256': hashlib.sha256(code).hexdigest(),
        'process_restart': {'before_pid': pid_before, 'after_pid': pid_after},
        'revision': after['revision'], 'head': after['head'], 'checkpoint': old_checkpoint['id'],
        'checks': checks, 'commands': requests, 'integrity': integrity,
        'limitations': ['Temporary tunnel hostname changes if its process restarts.',
            'Two client roles use separate HTTPS requests on the target; off-host authenticated client remains unperformed.',
            'Permanent DNS, production load/rate controls, redacted pre-auth audit and off-host backups are not certified.',
            'All 192 mission obligations remain unaccepted.']}
    path = args.artifacts / 'initial-live-service.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('run_id', 'result', 'origin', 'revision', 'head', 'checkpoint', 'scope')}))


if __name__ == '__main__':
    main()
