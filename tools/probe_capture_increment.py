#!/usr/bin/env python3
"""Exercise installed 1.3 via real authenticated HTTPS, retaining actual receipts.

Deployment operator only. Credentials come from POLYIA_* environment variables;
no credential enters a URL, report or command. Mutating retries reuse exact bytes.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
import uuid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    args = parser.parse_args()
    assert args.origin.startswith('https://') and args.origin.count('/') == 2
    prefix = 'capture-' + uuid.uuid4().hex
    report = {'ok': False, 'origin': args.origin, 'release': str(args.release),
              'checks': [], 'commands': [], 'scope': 'real public HTTPS requests from target VM'}
    output = args.artifacts / (prefix + '-receipt.json')

    def save():
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
        output.chmod(0o644)

    def request(path, body=None, *, expected=200):
        data = None if body is None else json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        token = os.environ['POLYIA_READ_TOKEN' if body is None else 'POLYIA_OPERATOR_TOKEN']
        for attempt in range(4):
            req = urllib.request.Request(args.origin + path, data=data,
                headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=25) as response:
                    status, raw = response.status, response.read()
            except urllib.error.HTTPError as error:
                status, raw = error.code, error.read()
            except (OSError, TimeoutError):
                if attempt == 3:
                    raise
                time.sleep(1)
                continue
            if status in (502, 503, 504) and attempt < 3:
                time.sleep(1)
                continue
            assert status == expected, (path, status, expected)
            return json.loads(raw)

    def state():
        return request('/v1/state')

    def command(kind, payload, *, expected=200):
        body = {'command_id': prefix + '-' + str(len(report['commands'])),
                'expected_revision': state()['revision'], 'kind': kind, 'payload': payload}
        item = {'request': body}; report['commands'].append(item); save()
        item['receipt'] = request('/v1/commands', body, expected=expected); save()
        return item['receipt']

    def check(name, value):
        assert value, name
        report['checks'].append({'name': name, 'pass': True}); save()

    def stage(path, raw):
        target = args.artifacts / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw); target.chmod(0o644)
        return path

    def captured(artifact):
        offset, chunks = 0, []
        while True:
            chunk = request('/v1/blobs/' + artifact['sha256'] + '?offset=' + str(offset) + '&limit=8192')
            assert chunk['digest'] == artifact['sha256'] and chunk['offset'] == offset
            assert chunk['total_size'] == artifact['size'] and chunk['encoding'] == 'base64'
            data = base64.b64decode(chunk['data'], validate=True)
            assert len(data) <= 8192
            chunks.append(data)
            if chunk['next_offset'] is None:
                break
            assert chunk['next_offset'] == offset + len(data) and len(data) > 0
            offset = chunk['next_offset']
        raw = b''.join(chunks)
        assert len(raw) == artifact['size'] and hashlib.sha256(raw).hexdigest() == artifact['sha256']
        return raw

    try:
        report['start_revision'] = state()['revision']; save()
        discovery = request('/.well-known/polyia.json')
        check('deployed service exposes captured bytes and rasm', discovery['capabilities']['captured_artifact_reads']
              and 'rasm' in discovery['capabilities']['experiments'])
        report['guidance_review'] = [{'id': key, 'status': item['status'], 'target': item['target']}
            for key, item in state()['guidance'].items() if item['status'] in ('SUBMITTED', 'DEFERRED')]
        save()
        command('checkpoint.create', {'note': 'Runtime1.3 source context before actual PIA-042 conformance acceptance; source-linked capture/rasm commissioning.'})
        paths = [stage(path, (args.release / path).read_bytes()) for path in
                 ['polyia/__init__.py', 'polyia/store.py', 'polyia/experiments.py', 'polyia/mission_verifiers.py']]
        command('requirement.produce', {'requirement_id': 'PIA-042', 'artifacts': paths,
            'note': 'Exact installed1.3 implementation under PIA-042/capture-v1; no supplied PASS report.'})
        verification = command('requirement.verify', {'requirement_id': 'PIA-042'})['result']['verification']
        check('actual PIA-042 fresh verifier passed', verification['outcome'] == 'PASS'
              and verification['evidence_class'] == 'SOFTWARE_CONFORMANCE'
              and len(verification['report']['checks']) == 16
              and all(c['pass'] is True for c in verification['report']['checks']))
        command('requirement.accept', {'requirement_id': 'PIA-042'})
        check('observer sees accepted bound PIA-042', state()['requirements']['PIA-042']['status'] == 'ACCEPTED')
        params = {'version': 'polyia.rasm/0.1', 'chart': 'timeless.rsa28/0.1', 'operation': 'project', 'text': 'كتب'}
        projection = command('experiment.run', {'name': 'rasm', 'parameters': params})['result']['run']
        check('actual rasm has fifteen chart fillings', projection['report']['status'] == 'PASS'
              and projection['report']['result']['inverse']['candidate_total'] == 15
              and projection['report']['su_registry_export_authorized'] is False)
        marked = command('experiment.run', {'name': 'rasm', 'parameters': {**params, 'text': 'ب' + 'َ' * 400}})['result']['run']
        value = marked['report']['result']
        recovery = command('experiment.run', {'name': 'rasm', 'parameters': {
            'version': params['version'], 'chart': params['chart'], 'operation': 'recover',
            'projection': value['projection'], 'side_data': value['side_data']}})['result']['run']
        check('large bounded recovery executes through actual command API', recovery['report']['status'] == 'PASS'
              and recovery['report']['result']['original_text'] == 'ب' + 'َ' * 400)
        rasm_paths = [stage('polyia/rasm.py', (args.release / 'polyia/rasm.py').read_bytes()),
            stage(prefix + '-rasm.json', (json.dumps(projection, ensure_ascii=False) + '\n').encode())]
        command('requirement.produce', {'requirement_id': 'PIA-128', 'artifacts': rasm_paths,
            'note': 'Source-pinned authored chart and actual live projection; full corpus/export acceptance remains open.'})
        books = ['books/book-of-forms/' + name for name in ['BOOK.md', 'exercises.json', 'evidence.json']]
        command('requirement.produce', {'requirement_id': 'PIA-189', 'artifacts':
            [stage(path, (args.release / path).read_bytes()) for path in books],
            'note': 'Owner-authorized Book of Forms construction and twelve executed exercises, rebuilt against1.3; wider curriculum acceptance remains open.'})
        for artifact in state()['requirements']['PIA-189']['artifacts']:
            check('observer reconstructs exact captured ' + artifact['path'], captured(artifact) == (args.release / artifact['path']).read_bytes())
        for rid, priority in [('PIA-040', 9), ('PIA-085', 8), ('PIA-097', 8)]:
            submitted = command('guidance.submit', {'target': rid, 'text': 'Continue source-based full commission after capture acceptance: guidance effects, quantitative compiler contracts and constructive generators. Preserve unmet inherited gates.',
                'action': {'kind': 'set_priority', 'target': rid, 'priority': priority}})
            gid = submitted['result']['guidance_id']
            command('guidance.ack', {'guidance_id': gid, 'disposition': 'ACKNOWLEDGED',
                'reason': 'Exact source contracts read, independent next work assigned and underway.'})
            command('guidance.apply', {'guidance_id': gid})
            check(rid + ' priority actually applied', state()['requirements'][rid]['priority'] == priority
                  and state()['guidance'][gid]['status'] == 'APPLIED')
        unsupported = command('requirement.verify', {'requirement_id': 'PIA-128'})['result']['verification']
        check('partial rasm cannot certify full inherited obligation', unsupported['outcome'] == 'UNSUPPORTED')
        before = state()['revision']
        command('requirement.accept', {'requirement_id': 'PIA-128'}, expected=409)
        check('unsupported acceptance leaves revision unchanged', state()['revision'] == before)
        checkpoint = command('checkpoint.create', {'note': 'Actual1.3 PIA-042 acceptance, rasm round trip, observer Book of Forms byte reconstruction and applied next-work guidance; full commission remains NOT_COMMISSIONED.'})
        before = state(); last = report['commands'][-1]
        old_pid = subprocess.check_output(['systemctl', 'show', 'polyia.service', '--property=MainPID', '--value'], text=True).strip()
        subprocess.run(['systemctl', 'restart', 'polyia.service'], check=True)
        after = state()
        pid = subprocess.check_output(['systemctl', 'show', 'polyia.service', '--property=MainPID', '--value'], text=True).strip()
        check('real process restart preserves full accepted state', before == after and pid != old_pid and pid != '0')
        check('exact retry after restart returns original receipt', request('/v1/commands', last['request']) == last['receipt'])
        integrity = request('/v1/verify')
        check('full retained ledger verifies', integrity['ok'])
        check('remaining full commission stays open', state()['commission_status'] == 'NOT_COMMISSIONED')
        report.update(ok=True, final_revision=state()['revision'], checkpoint=checkpoint,
            integrity=integrity, limitations=['Public HTTPS clients execute on the target VM, not an independent host.',
            'The sixteen capture checks establish finite software conformance only; other mission gates remain open.'])
        save(); print(json.dumps({'ok': True, 'checks': len(report['checks']), 'revision': report['final_revision'], 'receipt': str(output)}))
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error); save(); raise


if __name__ == '__main__':
    main()
