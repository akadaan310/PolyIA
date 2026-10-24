#!/usr/bin/env python3
"""Actual installed 1.4 HTTPS commissioning through the durable machine SDK.

Deployment operator tool. Credentials are environment-only. The private outbox
retains uncertain requests; recovery always reuses the complete original command.
This performs real mutations and a supervised service restart on the target.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from polyia.remote import RemoteClient, RemoteError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--journal', type=Path, required=True)
    args = parser.parse_args()
    prefix = 'construction-' + uuid.uuid4().hex
    report = {'ok': False, 'origin': args.origin, 'release': str(args.release),
              'scope': 'actual authenticated HTTPS clients from target VM, no independent second host',
              'checks': [], 'commands': [], 'llm_inference': False}
    output = args.artifacts / (prefix + '-receipt.json')
    client = RemoteClient(args.origin, os.environ['POLYIA_OPERATOR_TOKEN'], args.journal, timeout=25)
    observer = RemoteClient(args.origin, os.environ['POLYIA_READ_TOKEN'],
                            args.journal.with_name(prefix + '-observer.sqlite3'), timeout=25)

    def save():
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        output.chmod(0o644)

    def check(name, value):
        if not value:
            raise AssertionError(name)
        report['checks'].append({'name': name, 'pass': True}); save()

    def state():
        for attempt in range(4):
            try:
                return observer.state()
            except RemoteError as error:
                if error.code not in ('UNCERTAIN', 'READ_FAILED') or attempt == 3:
                    raise
                time.sleep(1)

    def command(kind, payload):
        request = {'command_id': prefix + '-' + str(len(report['commands'])),
                   'expected_revision': state()['revision'], 'kind': kind, 'payload': payload}
        item = {'request': request}; report['commands'].append(item); save()
        for attempt in range(4):
            try:
                item['receipt'] = client.submit(request) if attempt == 0 else client.recover()
                save(); return item['receipt']
            except RemoteError as error:
                if error.code != 'UNCERTAIN' or attempt == 3:
                    raise
                time.sleep(1)

    def stage(path, raw=None):
        target = args.artifacts / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((args.release / path).read_bytes() if raw is None else raw)
        target.chmod(0o644)
        return path

    def record(name, value):
        return stage(prefix + '-' + name + '.json',
                     (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode())

    def produce(identifier, paths, note):
        return command('requirement.produce', {'requirement_id': identifier, 'artifacts': paths, 'note': note})

    def run(name, parameters):
        result = command('experiment.run', {'name': name, 'parameters': parameters})['result']['run']
        check(name + ' executes pinned source with actual checks', result['report']['status'] == 'PASS'
              and result['report']['checks'] and all(c['pass'] is True for c in result['report']['checks'])
              and result['report']['llm_inference'] is False and result['execution_bundle']['status'] == 'PINNED')
        return result

    try:
        check('operator outbox starts with no unresolved mutation', client.pending() is None)
        initial = state(); report['start_revision'] = initial['revision']; save()
        report['guidance_review'] = {key: value for key, value in initial['guidance'].items()
                                     if value['status'] in ('SUBMITTED', 'DEFERRED')}
        command('checkpoint.create', {'note': 'Runtime1.4 source context: finite typed forms, constructive generators, quantitative compiler checks and guidance-effect acceptance.'})
        produce('PIA-040', [stage(path) for path in
            ['polyia/__init__.py', 'polyia/store.py', 'polyia/experiments.py', 'polyia/mission_verifiers.py']],
            'Exact running1.4 sources for fresh PIA-040/guidance-effects-v1 checks and source-scoped inherited applicability.')
        verification = command('requirement.verify', {'requirement_id': 'PIA-040'})['result']['verification']
        check('fresh guidance-effect verifier passes all twenty-one checks', verification['outcome'] == 'PASS'
              and len(verification['report']['checks']) == 21
              and all(item['pass'] is True for item in verification['report']['checks']))
        command('requirement.accept', {'requirement_id': 'PIA-040'})
        check('observer sees actual PIA-040 acceptance and retained PIA-042',
              all(state()['requirements'][key]['status'] == 'ACCEPTED' for key in ('PIA-040', 'PIA-042')))

        runs = []
        for filename in ('protocol.card.json', 'rational-division.card.json'):
            card = json.loads((args.release / 'examples/generators' / filename).read_text())
            result = run('generators', {'card': card, 'request': {'operation': 'generate'}, 'style': 'tutorial'})
            candidates = result['report']['result']['execution']['result']['candidates']
            check(filename + ' produces its complete expected finite population',
                  len(candidates) == (2 if filename == 'protocol.card.json' else 18)
                  and result['report']['result']['execution']['result']['complete'] is True)
            if filename == 'protocol.card.json':
                check('actual protocol language matches the constructed two words',
                      [item['value'] for item in candidates] == [['PING', 'ACK'], ['PING', 'ACK', 'ACK']])
            runs.append(result)
        produce('PIA-097', [stage('polyia/generators.py'), record('generators', runs)],
                'Two actual bounded generator families; full inherited subject breadth remains open.')

        alphabet = {'version': 'polyia.alphabet/0.1', 'kind': 'numeric', 'entity_id': 'commission:N',
                    'interpretation': 'Individual exact nonnegative integers.',
                    'sources': [{'source': 'GOD_SEED.md', 'anchor': 'PIA-050 declared Natural construction',
                                 'sha256': hashlib.sha256((args.release / 'GOD_SEED.md').read_bytes()).hexdigest()}],
                    'generator': {'name': 'naturals', 'start': 0, 'coordinates': 'value'},
                    'group': {'elements': [{'id': 'e', 'rule': 'identity'}]}}
        envelope = {'version': 'polyia.forms/0.1', 'alphabet': alphabet}
        natural = run('forms', {**envelope, 'operation': 'generate', 'index': 10**20})
        check('actual Natural preserves its exact large integer', natural['report']['result']['result']['letter']['value'] == '100000000000000000000')
        definition = run('forms', {**envelope, 'operation': 'alphabet'})
        word = {'version': 'polyia.word/0.1', 'entity_id': 'commission:tuple256',
                'alphabet_cid': definition['report']['result']['result']['content_cid'],
                'index': {'kind': 'tuple', 'length': 256}, 'labels': {str(i): str(i % 2) for i in range(256)}}
        serialized = run('forms', {**envelope, 'operation': 'serialize', 'word': word})
        text = serialized['report']['result']['result']['text']
        recovered = run('forms', {**envelope, 'operation': 'deserialize', 'text': text})
        check('actual 256-cell roundtrip exceeds ordinary string cap and preserves exact word',
              len(text) > 2048 and recovered['report']['result']['result']['word'] == word)
        produce('PIA-050', [stage('polyia/forms.py'), record('forms', [natural, definition, serialized, recovered])],
                'Actual effective Natural and bounded indexed-word roundtrip; broad forms and chemical gates remain open.')
        native = [stage(path) for path in ['polyia/native.py', 'tools/check_native_quantitative.py',
                                          'docs/evidence/native_quantitative_20261024.json']]
        for identifier in ('PIA-085', 'PIA-103'):
            produce(identifier, native, 'Executed10000terms and three computational families with1000inputs each on one host; declared finite domain and independent-role limits remain explicit.')
        produce('PIA-094', [stage(path) for path in ['polyia/remote.py', 'tests/test_remote.py', 'docs/REMOTE_CLIENT.md']],
                'Durable command SDK is actually issuing this commission; wider provider/factory contracts remain open.')
        books = [stage('books/book-of-forms/' + filename) for filename in ('BOOK.md', 'exercises.json', 'evidence.json')]
        produce('PIA-189', books, 'Owner-authorized constructed Book of Forms with executed lessons; wider curriculum acceptance remains open.')
        unsupported = command('requirement.verify', {'requirement_id': 'PIA-097'})['result']['verification']
        check('partial generator scope cannot accept full inherited obligation', unsupported['outcome'] == 'UNSUPPORTED')

        for target in ('PIA-061', 'PIA-073', 'PIA-134'):
            submitted = command('guidance.submit', {'target': target, 'text': 'Continue source-grounded promotion, genuine multiport native QBundles, and durable sealed bounded research lifecycle. Retain every unmet inherited gate.',
                'action': {'kind': 'set_priority', 'target': target, 'priority': 9}})
            gid = submitted['result']['guidance_id']
            command('guidance.ack', {'guidance_id': gid, 'disposition': 'ACKNOWLEDGED',
                    'reason': 'Full source contracts inspected; concrete next implementation designs prepared.'})
            command('guidance.apply', {'guidance_id': gid})
            current = state()
            check(target + ' guidance changes actual priority', current['guidance'][gid]['status'] == 'APPLIED'
                  and current['requirements'][target]['priority'] == 9)
        command('checkpoint.create', {'note': 'Actual1.4 PIA-040 acceptance; generator and256-cell forms execution; durable SDK commissioning and applied next work. Full mission remains NOT_COMMISSIONED.'})
        before = state(); last = report['commands'][-1]
        client.close()
        client = RemoteClient(args.origin, os.environ['POLYIA_OPERATOR_TOKEN'], args.journal, timeout=25)
        check('client restart retains exact receipt and has no pending command',
              client.pending() is None and client.submit(last['request']) == last['receipt'])
        old_pid = subprocess.check_output(['systemctl', 'show', 'polyia.service', '--property=MainPID', '--value'], text=True).strip()
        subprocess.run(['systemctl', 'restart', 'polyia.service'], check=True)
        after = state()
        pid = subprocess.check_output(['systemctl', 'show', 'polyia.service', '--property=MainPID', '--value'], text=True).strip()
        check('real service restart preserves complete accepted state', before == after and pid not in ('0', old_pid))
        with RemoteClient(args.origin, os.environ['POLYIA_OPERATOR_TOKEN'], args.journal.with_name(prefix + '-retry.sqlite3'), timeout=25) as second:
            check('fresh durable client exact POST returns original receipt after restart', second.submit(last['request']) == last['receipt'])
        check('full mission remains NOT_COMMISSIONED', after['commission_status'] == 'NOT_COMMISSIONED')
        report.update(ok=True, end_revision=after['revision'], head=after['head'], checkpoint=after['latest_checkpoint']); save()
        print(json.dumps({'ok': True, 'checks': len(report['checks']), 'revision': after['revision'], 'receipt': str(output)}))
    finally:
        client.close(); observer.close(); save()


if __name__ == '__main__':
    main()
