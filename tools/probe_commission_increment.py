#!/usr/bin/env python3
"""Record actual HTTPS capability checks and source-linked productions.

Explicit deployment-operator tool: tokens come from the environment, and the
operator supplies an installed release and artifact workspace. No model calls.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
import uuid


class UnexpectedStatus(Exception):
    def __init__(self, path, status, expected):
        self.status = status
        super().__init__(path, status, expected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    args = parser.parse_args()
    assert args.origin.startswith('https://') and args.origin.count('/') == 2
    prefix = 'increment-' + uuid.uuid4().hex
    receipts, requests, checks = [], [], []

    def read(path, body=None, *, observer=False, expected=200):
        token = os.environ['POLYIA_READ_TOKEN' if observer else 'POLYIA_OPERATOR_TOKEN']
        req = urllib.request.Request(args.origin + path,
            data=None if body is None else json.dumps(body, allow_nan=False).encode(),
            headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read()
        if status != expected:
            raise UnexpectedStatus(path, status, expected)
        return json.loads(raw)

    def state():
        return read('/v1/state', observer=True)

    def command(kind, payload, expected=200):
        body = {'command_id': prefix + '-' + str(len(requests)),
                'expected_revision': state()['revision'], 'kind': kind, 'payload': payload}
        result = read('/v1/commands', body, expected=expected)
        requests.append(body); receipts.append(result)
        return result

    def check(name, value):
        assert value, name
        checks.append({'name': name, 'pass': True})

    def save(name, value):
        target = args.artifacts / (prefix + '-' + name)
        target.write_bytes(value if isinstance(value, bytes) else (json.dumps(value, indent=2, allow_nan=False) + '\n').encode())
        target.chmod(0o644)
        return target.name

    start = state()
    discovery = read('/.well-known/polyia.json')
    check('deployed discovery exposes real new handlers', {'native', 'intake', 'astra'} <= set(discovery['capabilities']['experiments']))
    check('deployed boundary bounds admission', discovery['limits']['active_handlers'] == 32)
    runs = {}
    native_source = (args.release / 'examples/native/polynomial.polyia').read_text()
    cases = [('native', {'source': native_source}),
             ('intake', {'text': 'Teach polynomial division\nUnsupported Arabic request: قَالَ', 'style': 'tutorial'}),
             ('astra', {'adapter_version': 'POLYIA-ASTRA/0.1', 'source_version': 'ASTRA/0.2',
                        'protocol': 'ATOM-HANDOFF/0.1', 'operation': 'geometry.project',
                        'input': {'observer': 'ICRS-direction-only', 'points': [{'id': 'authored-direction',
                            'ra_deg': 90, 'dec_deg': 0, 'provenance': {'kind': 'synthetic', 'source_id': 'authored:commissioning'}}],
                            'view': {'width': 800, 'height': 500, 'distance': 4, 'yaw_rad': 0, 'pitch_rad': 0}}})]
    for name, parameters in cases:
        receipt = command('experiment.run', {'name': name, 'parameters': parameters})
        run = receipt['result']['run']; runs[name] = run
        check(name + ' captured loaded source bundle', run['execution_bundle']['status'] == 'PINNED')
        check(name + ' actual observer sees committed run', state()['runs'][-1] == run)
    output = runs['native']['report']['result']['execution']['outputs']
    check('native exact polynomial outputs', output['quotient']['value'] == ['1', '1'] and output['remainder']['value'] == ['0'] and output['derivative_at_three_halves']['value'] == '3')
    intake = runs['intake']['report']
    check('mixed source retains unknowns and exact computation', intake['status'] == 'INCONCLUSIVE' and len(intake['result']['unresolved']) == 1 and intake['result']['interpretations'][0]['computation']['result']['remainder'] == ['3'])
    point = runs['astra']['report']['result']['projection']['points'][0]
    check('actual Astra projection matches declared fixture', abs(point['screen']['x'] - 578.75) < 1e-9 and point['screen']['y'] == 255)
    refused = command('experiment.run', {'name': 'native', 'parameters': {'source': '(commission (profile "polyia.native/0.1") (emit bad (add "x" 1)))'}})
    check('native type refusal retained', refused['result']['run']['report']['status'] == 'REFUSED')
    nonfinite = command('experiment.run', {'name': 'intake', 'parameters': {'text': 'divide polynomial [NaN] by [1]'}})
    check('nonfinite embedded input remains serializable unknown', nonfinite['result']['run']['report']['status'] == 'INCONCLUSIVE')

    production_paths = {}
    for name, rid in [('native', 'PIA-085'), ('intake', 'PIA-122'), ('astra', 'PIA-160')]:
        paths = [save(name + '.json', runs[name]), save(name + '.py', (args.release / ('polyia/' + name + '.py')).read_bytes())]
        production_paths[rid] = paths
    production_paths['PIA-189'] = [save('book-' + Path(path).name, (args.release / path).read_bytes())
        for path in ['books/book-of-forms/BOOK.md', 'books/book-of-forms/exercises.json', 'books/book-of-forms/evidence.json']]
    for rid, paths in production_paths.items():
        command('requirement.produce', {'requirement_id': rid, 'artifacts': paths,
            'note': 'Actual source-linked runtime1.2 production and retained run/teaching evidence; full inherited acceptance remains open.'})
    for rid, priority in [('PIA-042', 9), ('PIA-128', 8)]:
        submitted = command('guidance.submit', {'target': rid,
            'text': 'Continue full commission with actual artifact-capture acceptance and source-exact rasm construction. All other gates remain explicit.',
            'action': {'kind': 'set_priority', 'target': rid, 'priority': priority}})
        gid = submitted['result']['guidance_id']
        command('guidance.ack', {'guidance_id': gid, 'disposition': 'ACKNOWLEDGED',
            'reason': 'Source requirements and inherited acceptance reviewed; next bounded work assigned.'})
        command('guidance.apply', {'guidance_id': gid})
        check(rid + ' priority actually applied', state()['requirements'][rid]['priority'] == priority and state()['guidance'][gid]['status'] == 'APPLIED')
    verified = command('requirement.verify', {'requirement_id': 'PIA-085'})
    check('partial native implementation cannot pass full obligation', verified['result']['verification']['outcome'] == 'UNSUPPORTED')
    before_refusal = state()['revision']
    command('requirement.accept', {'requirement_id': 'PIA-085'}, expected=409)
    check('unverified mission acceptance does not mutate state', state()['revision'] == before_refusal)
    cp = command('checkpoint.create', {'note': 'Runtime1.2 real HTTPS native/intake/Astra runs, Book of Forms production, source bundles and applied next-work guidance. Full mission NOT_COMMISSIONED.'})
    checkpoint_request = requests[-1]
    before_restart = state(); checkpoint = read('/v1/checkpoints/latest', observer=True)
    save('before-restart.json', {'status': 'CHECKPOINT_RECORDED_RESTART_PENDING',
        'checks': checks, 'commands': receipts, 'requests': requests,
        'revision': before_restart['revision'], 'head': before_restart['head'], 'checkpoint': checkpoint['id']})
    subprocess.run(['systemctl', 'restart', 'polyia.service'], check=True)
    for _ in range(30):
        try:
            after = state(); break
        except OSError:
            time.sleep(.5)
        except UnexpectedStatus as error:
            if error.status not in (502, 503, 504):
                raise
            time.sleep(.5)
    else:
        raise AssertionError('Service did not recover')
    check('extended run history survives process restart', before_restart == after)
    check('checkpoint survives restart exactly', checkpoint == read('/v1/checkpoints/latest', observer=True))
    check('checkpoint exact retry returns original receipt', cp == read('/v1/commands', checkpoint_request))
    integrity = read('/v1/verify', observer=True)
    check('captured extension bundles and history verify', integrity['ok'])
    check('full mission remains uncommissioned', state()['commission_status'] == 'NOT_COMMISSIONED')
    report = {'scope': 'Actual target HTTPS runtime1.2 capability and continuation probe; not full-mission acceptance',
              'run_id': prefix, 'origin': args.origin, 'release': str(args.release),
              'revision': after['revision'], 'head': after['head'], 'checkpoint': checkpoint['id'],
              'checks': checks, 'commands': receipts, 'requests': requests,
              'initial_revision': start['revision'], 'integrity': integrity,
              'limits': ['HTTPS clients run on the target via the public endpoint; independent-host authenticated probe remains separate.',
                         'Temporary tunnel address changes after tunnel restart.', 'Native, intake, Astra and book outputs cover their declared bounded profiles.']}
    filename = save('receipt.json', report)
    print(json.dumps({'result': 'PASS', 'checks': len(checks), 'revision': report['revision'],
                      'checkpoint': report['checkpoint'], 'artifact': filename}))


if __name__ == '__main__':
    main()
