"""Durable HTTP client recovery against actual service/ledger transitions."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from polyia.remote import RemoteClient, RemoteError
from polyia.server import make_server
from polyia.store import Ledger


class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); (self.root / 'workspace').mkdir()
        self.ledger = Ledger(self.root / 'state/ledger.sqlite3', self.root / 'workspace',
            [{'id': 'R-1', 'title': 'Fixture', 'verifier': 'artifact-integrity'}])
        self.addCleanup(self.ledger.close)
        self.server = make_server(self.ledger, token='remote-operator-secret', read_token='remote-reader-secret')
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
        self.thread.start(); self.addCleanup(self.stop)
        self.origin = 'http://127.0.0.1:' + str(self.server.server_port)
        self.journal = self.root / 'client/outbox.sqlite3'
        self.client = self.open(); self.addCleanup(lambda: self.client.close())

    def stop(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(3)

    def open(self, token='remote-operator-secret', origin=None):
        return RemoteClient(origin or self.origin, token, self.journal, allow_loopback_http=True)

    def command(self, cid='remote-one', revision=0):
        return {'command_id': cid, 'expected_revision': revision, 'kind': 'guidance.submit',
                'payload': {'target': 'R-1', 'text': 'Preserve a machine client receipt',
                            'action': {'kind': 'set_priority', 'target': 'R-1', 'priority': 8}}}

    def test_actual_command_receipt_is_durable_and_exact_retry_is_observational(self):
        command = self.command(); receipt = self.client.submit(command)
        self.assertEqual(receipt['revision'], 1)
        self.assertIsNone(self.client.pending())
        self.client.close(); self.client = self.open()
        self.assertEqual(self.client.submit(command), receipt)
        self.assertEqual(self.ledger.state()['revision'], 1)
        self.assertEqual(self.client.state(), self.ledger.state())

    def test_lost_committed_response_survives_client_restart_and_new_work_is_held(self):
        original = self.client._request
        def lost(path, body=None):
            status, result = original(path, body)
            if body is not None:
                raise RemoteError('UNCERTAIN', 'simulated connection loss after actual commit')
            return status, result
        command = self.command()
        with patch.object(self.client, '_request', lost):
            with self.assertRaises(RemoteError): self.client.submit(command)
        self.assertEqual(self.ledger.state()['revision'], 1)
        self.assertEqual(self.client.pending(), command)
        with self.assertRaises(RemoteError) as refused: self.client.submit(self.command('different', 1))
        self.assertEqual(refused.exception.code, 'PENDING_COMMAND')
        self.client.close(); self.client = self.open()
        recovered = self.client.recover()
        self.assertEqual(recovered['command_id'], command['command_id'])
        self.assertEqual(self.ledger.state()['revision'], 1)
        self.assertIsNone(self.client.pending())

    def test_lost_pre_dispatch_recovers_same_request_after_receipt_not_found(self):
        command = self.command()
        with patch.object(self.client, '_request', side_effect=RemoteError('UNCERTAIN', 'before dispatch')):
            with self.assertRaises(RemoteError): self.client.submit(command)
        self.assertEqual(self.ledger.state()['revision'], 0)
        self.client.close(); self.client = self.open()
        self.assertEqual(self.client.recover()['revision'], 1)
        self.assertEqual(self.ledger.state()['revision'], 1)

    def test_recovery_does_not_adopt_another_request_with_same_id_and_revision(self):
        mine = self.command()
        with patch.object(self.client, '_request', side_effect=RemoteError('UNCERTAIN', 'before dispatch')):
            with self.assertRaises(RemoteError): self.client.submit(mine)
        different = self.command(); different['payload']['action']['priority'] = 3
        with RemoteClient(self.origin, 'remote-operator-secret', self.root / 'other-collision/outbox.sqlite3', allow_loopback_http=True) as other:
            other.submit(different)
        with self.assertRaises(RemoteError): self.client.recover()
        self.assertEqual(self.client.pending(), mine)
        self.assertEqual(self.ledger.state()['guidance'][mine['command_id']]['action']['priority'], 3)

    def test_decoded_credential_and_caller_credential_are_never_journaled(self):
        secret = 'remote-operator-secret'
        command = self.command(); command['payload']['text'] = secret
        with self.assertRaises(RemoteError) as error: self.client.submit(command)
        self.assertEqual(error.exception.code, 'CREDENTIAL_IN_COMMAND')
        self.assertIsNone(self.client.pending())
        import io
        class Response(io.BytesIO):
            code = 200
        encoded = b'{"result":"\\u0072emote-operator-secret"}'
        with patch.object(self.client._opener, 'open', return_value=Response(encoded)):
            with self.assertRaises(RemoteError): self.client._request('/v1/state')
        self.client.state()
        receipt = {'ok': True, 'command_id': 'remote-one', 'actor': 'operator', 'revision': 1,
                   'head': '0'*64, 'result': {'echo': secret}}
        with patch.object(self.client, '_request', return_value=(200, receipt)):
            with self.assertRaises(RemoteError): self.client.submit(self.command())
        for path in self.journal.parent.iterdir():
            self.assertNotIn(secret.encode(), path.read_bytes())

    def test_read_role_refusal_keeps_pending_for_exact_recovery_with_operator(self):
        self.client.close(); self.client = self.open('remote-reader-secret')
        command = self.command()
        with self.assertRaises(RemoteError) as error: self.client.submit(command)
        self.assertEqual(error.exception.code, 'UNCERTAIN')
        self.assertEqual(self.client.pending(), command)
        self.client.close(); self.client = self.open()
        self.assertEqual(self.client.recover()['revision'], 1)

    def test_well_formed_revision_conflict_is_retained_as_definite_refusal(self):
        self.client.submit(self.command())
        stale = self.command('stale', 0)
        with self.assertRaises(RemoteError) as error: self.client.submit(stale)
        self.assertEqual(error.exception.code, 'REVISION_CONFLICT')
        self.assertIsNone(self.client.pending())
        self.client.close(); self.client = self.open()
        with self.assertRaises(RemoteError) as error: self.client.submit(stale)
        self.assertEqual(error.exception.code, 'REVISION_CONFLICT')
        self.assertEqual(self.ledger.state()['revision'], 1)

    def test_id_reuse_cannot_change_request_and_origin_cannot_change(self):
        command = self.command(); self.client.submit(command)
        command['payload']['text'] = 'Different operation'
        with self.assertRaises(RemoteError) as error: self.client.submit(command)
        self.assertEqual(error.exception.code, 'ID_REUSE')
        with self.assertRaises(RemoteError) as error: self.open(origin='https://other.example')
        self.assertEqual(error.exception.code, 'ORIGIN_CHANGED')

    def test_ambiguous_http_envelopes_never_discard_pending_identity(self):
        for index, response in enumerate([(429, {}), (400, {}), (409, {'error': []}), (409, {'error': {'code': 'REVISION_CONFLICT'}}),
                                          (200, {'command_id': 'wrong', 'revision': 1}), (200, b'bad')]):
            with self.subTest(response=response):
                journal = self.root / ('other-' + str(index)) / 'outbox.sqlite3'
                with RemoteClient(self.origin, 'remote-operator-secret', journal, allow_loopback_http=True) as client:
                    client.state()  # Establish actual compatible protocol before corrupting replies.
                    with patch.object(client, '_request', return_value=response):
                        with self.assertRaises(RemoteError): client.submit(self.command())
                    self.assertEqual(client.pending(), self.command())
                    self.assertEqual(self.ledger.state()['revision'], 0)

    def test_incompatible_protocol_holds_request_without_dispatch(self):
        wrong = {'protocol': 'polyia.command-plane', 'protocol_version': '9.0.0', 'api_base': '/v1'}
        with patch.object(self.client, '_request', return_value=(200, wrong)) as transport:
            with self.assertRaises(RemoteError) as error: self.client.submit(self.command())
            self.assertEqual(error.exception.code, 'PROTOCOL_MISMATCH')
            self.assertEqual(transport.call_args.args, ('/.well-known/polyia.json',))
        self.assertEqual(self.client.pending(), self.command())
        self.assertEqual(self.ledger.state()['revision'], 0)

    def test_same_python_value_with_different_json_type_is_id_reuse(self):
        command = self.command(); self.client.submit(command)
        command['payload']['action']['priority'] = 8.0
        with self.assertRaises(RemoteError) as error: self.client.submit(command)
        self.assertEqual(error.exception.code, 'ID_REUSE')

    def test_redirects_are_not_followed_and_credentials_are_not_persisted(self):
        self.client.submit(self.command())
        for p in self.journal.parent.iterdir():
            self.assertNotIn(b'remote-operator-secret', p.read_bytes())
            self.assertNotIn(b'remote-reader-secret', p.read_bytes())
            self.assertEqual(p.stat().st_mode & 0o077, 0)
        self.assertEqual(self.journal.parent.stat().st_mode & 0o077, 0)
        from polyia.remote import _NoRedirect
        self.assertIsNone(_NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example'))

    def test_real_redirect_cannot_send_bearer_to_a_second_server(self):
        received = []
        class Destination(BaseHTTPRequestHandler):
            def do_GET(self):
                received.append(True); self.send_response(200); self.end_headers(); self.wfile.write(b'{}')
            def log_message(self, *args): pass
        target = HTTPServer(('127.0.0.1', 0), Destination)
        class Redirect(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header('Location', 'http://127.0.0.1:' + str(target.server_port) + '/v1/state')
                self.end_headers(); self.wfile.write(b'{}')
            def log_message(self, *args): pass
        redirect = HTTPServer(('127.0.0.1', 0), Redirect)
        threads = [threading.Thread(target=s.serve_forever, kwargs={'poll_interval': .01}, daemon=True) for s in (target, redirect)]
        for thread in threads: thread.start()
        try:
            with RemoteClient('http://127.0.0.1:' + str(redirect.server_port), 'remote-operator-secret',
                              self.root / 'redirect/outbox.sqlite3', allow_loopback_http=True) as client:
                with self.assertRaises(RemoteError): client.state()
            self.assertEqual(received, [])
        finally:
            for server in (target, redirect): server.shutdown(); server.server_close()
            for thread in threads: thread.join(3)

    def test_two_clients_cannot_dispatch_different_commands_through_one_journal(self):
        with self.open() as other:
            with self.client._locked(), self.assertRaises(RemoteError) as error:
                other.submit(self.command())
            self.assertEqual(error.exception.code, 'CLIENT_BUSY')
        self.assertEqual(self.ledger.state()['revision'], 0)

    def test_unsafe_origins_and_symlink_journal_are_refused(self):
        for origin in ['http://example.com', 'https://user:password@example.com', 'https://example.com/path',
                       'https://example.com?token=x', 'https://example.com#secret', 'http://localhost:80']:
            with self.subTest(origin=origin), self.assertRaises(RemoteError): self.open(origin=origin)
        self.client.close()
        self.journal.unlink(); self.journal.symlink_to(self.root / 'elsewhere')
        with self.assertRaises(RemoteError): self.open()

    def test_tampered_journal_and_invalid_commands_fail_before_network(self):
        self.client.submit(self.command())
        self.client._db.execute("UPDATE requests SET request_json='{}'")
        with self.assertRaises(RemoteError): self.client.submit(self.command())
        for command in [{}, {**self.command('bad'), 'expected_revision': True},
                        {**self.command('bad'), 'payload': {'nonfinite': float('nan')}}]:
            with self.assertRaises(RemoteError): self.client.submit(command)


if __name__ == '__main__': unittest.main()
