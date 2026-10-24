"""Captured byte inspection through real HTTP, SQLite, roles and audit logs."""
import base64
import hashlib
import http.client
import json
import logging
from pathlib import Path
import tempfile
import threading
import unittest

from polyia.server import make_server
from polyia.store import Ledger


class ArtifactHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        self.original = bytes(range(256)) * 274
        (self.workspace / 'captured.bin').write_bytes(self.original)
        self.ledger = Ledger(self.root / 'state' / 'ledger.sqlite3', self.workspace, [
            {'id': 'R-1', 'title': 'Captured bytes', 'verifier': 'artifact-integrity'}])
        self.addCleanup(self.ledger.close)
        receipt = self.ledger.command({'command_id': 'capture', 'expected_revision': 0,
            'kind': 'requirement.produce', 'payload': {'requirement_id': 'R-1',
            'artifacts': ['captured.bin']}})
        self.digest = receipt['result']['artifacts'][0]['sha256']
        # Production capture rejects empty evidence; exercise the byte reader's
        # zero-length boundary with a correctly hashed stored fixture only.
        self.empty_digest = hashlib.sha256(b'').hexdigest()
        self.ledger._conn.execute('INSERT INTO blobs(digest,data,size) VALUES(?,?,?)',
                                  (self.empty_digest, b'', 0))
        self.path = '/v1/blobs/' + self.digest
        self.server = make_server(self.ledger, token='operator-test', read_token='reader-test', request_burst=1000)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(3)

    def request(self, path=None, *, token='reader-test', method='GET', headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        values = {} if token is None else {'Authorization': 'Bearer ' + token}
        values.update(headers or {})
        try:
            connection.request(method, path or self.path, headers=values)
            response = connection.getresponse()
            data = response.read()
            return response.status, dict(response.getheaders()), json.loads(data) if data else data
        finally:
            connection.close()

    def test_operator_and_reader_reassemble_exact_capture_after_workspace_mutation(self):
        before = self.ledger.state()
        (self.workspace / 'captured.bin').write_bytes(b'workspace has changed')
        for token, scope in [('reader-test', 'read'), ('operator-test', 'operator')]:
            with self.subTest(role=scope):
                status, headers, first = self.request(token=token)
                self.assertEqual(status, 200)
                self.assertEqual(headers['X-PolyIA-Scope'], scope)
                self.assertEqual(headers['Cache-Control'], 'no-store')
                self.assertEqual(first['digest'], self.digest)
                self.assertEqual(first['total_size'], 70144)
                self.assertEqual(first['offset'], 0)
                self.assertEqual(first['encoding'], 'base64')
                self.assertEqual(first['next_offset'], 65536)
                start = base64.b64decode(first['data'], validate=True)
                self.assertEqual(start, self.original[:65536])
                status, _, last = self.request(self.path + '?offset=65536&limit=65536', token=token)
                self.assertEqual(status, 200)
                self.assertIsNone(last['next_offset'])
                captured = start + base64.b64decode(last['data'], validate=True)
                self.assertEqual(captured, self.original)
                self.assertEqual(hashlib.sha256(captured).hexdigest(), self.digest)
        self.assertEqual(self.ledger.state(), before, 'Reading bytes must not advance or alter semantic state')

    def test_private_route_never_accepts_url_credentials(self):
        for path, token in [(self.path, None), (self.path, 'wrong'),
                            (self.path + '?token=reader-test', None)]:
            with self.subTest(path=path):
                status, headers, body = self.request(path, token=token)
                self.assertEqual(status, 401)
                self.assertEqual(body['error']['code'], 'UNAUTHORIZED')
                self.assertIn('Bearer', headers['WWW-Authenticate'])
        self.assertEqual(self.request(self.path + '?token=reader-test')[0], 400)

    def test_head_checks_the_same_capture_and_has_no_body(self):
        status, get_headers, _ = self.request(self.path + '?offset=3&limit=7')
        self.assertEqual(status, 200)
        status, head_headers, body = self.request(self.path + '?offset=3&limit=7', method='HEAD')
        self.assertEqual(status, 200)
        self.assertEqual(body, b'')
        self.assertEqual(head_headers['Content-Length'], get_headers['Content-Length'])
        self.assertEqual(head_headers['Content-Type'], get_headers['Content-Type'])
        self.assertEqual(self.request(method='POST')[0], 405)

    def test_empty_end_and_single_byte_boundaries(self):
        for path in ['/v1/blobs/' + self.empty_digest, self.path + '?offset=70144']:
            status, _, result = self.request(path)
            self.assertEqual(status, 200)
            self.assertEqual(result['data'], '')
            self.assertIsNone(result['next_offset'])
        status, _, result = self.request(self.path + '?offset=70143&limit=1')
        self.assertEqual(status, 200)
        self.assertEqual(result['data'], '/w==')
        self.assertIsNone(result['next_offset'])
        status, _, result = self.request(self.path + '?offset=70145')
        self.assertEqual(status, 416)
        self.assertEqual(result['error']['code'], 'INVALID_RANGE')

    def test_invalid_queries_and_digests_are_refused(self):
        for query in ['limit=0', 'limit=65537', 'limit=-1', 'limit=1.0', 'limit=',
                      'offset=-1', 'offset=1&offset=2', 'limit=1&limit=2',
                      'offset=9223372036854775808', 'offset=abc', 'offset=%FF',
                      'limit=1&unknown=2', 'offset', 'offset=+1']:
            with self.subTest(query=query):
                status, _, body = self.request(self.path + '?' + query)
                self.assertEqual(status, 400)
                self.assertEqual(body['error']['code'], 'INVALID_QUERY')
        for digest in [self.digest.upper(), 'a' * 63, 'a' * 65, 'z' * 64, '../server.py']:
            with self.subTest(digest=digest):
                self.assertIn(self.request('/v1/blobs/' + digest)[0], (400, 404))
        self.assertEqual(self.request(headers={'Range': 'bytes=0-10'})[0], 400)

    def test_missing_and_corrupt_capture_never_return_bytes(self):
        status, _, missing = self.request('/v1/blobs/' + '0' * 64)
        self.assertEqual(status, 404)
        self.assertEqual(missing['error']['code'], 'NOT_FOUND')
        for corrupted in [b'corrupt', b'A' * len(self.original)]:
            with self.subTest(corruption='length' if len(corrupted) != len(self.original) else 'hash'):
                with self.ledger._lock:
                    self.ledger._conn.execute('UPDATE blobs SET data=? WHERE digest=?', (corrupted, self.digest))
                status, _, corrupt = self.request()
                self.assertEqual(status, 409)
                self.assertEqual(corrupt['error']['code'], 'INTEGRITY_ERROR')
                self.assertNotIn('data', corrupt)
                self.assertEqual(self.request(method='HEAD')[0], 409)

    def test_discovery_and_schema_describe_authenticated_bounded_inspection(self):
        status, _, discovery = self.request('/.well-known/polyia.json', token=None)
        self.assertEqual(status, 200)
        self.assertTrue(discovery['capabilities'].get('captured_artifact_reads'))
        self.assertEqual(discovery['limits'].get('blob_chunk_bytes'), 65536)
        _, _, schema = self.request('/openapi.json', token=None)
        self.assertIn('/v1/blobs/{digest}', schema['paths'])
        route = schema['paths']['/v1/blobs/{digest}']
        self.assertIn('get', route)
        self.assertIn('head', route)
        self.assertNotEqual(route['get'].get('security', schema['security']), [])

    def test_audit_uses_finite_category_without_digest_path_or_query(self):
        completed = threading.Event()
        class CompletionHandler(logging.Handler):
            def emit(self, record):
                completed.set()
        with self.assertLogs('polyia.server', level='INFO') as captured:
            observer = CompletionHandler()
            logger = logging.getLogger('polyia.server')
            logger.addHandler(observer)
            try:
                self.assertEqual(self.request(self.path + '?limit=1')[0], 200)
                self.assertTrue(completed.wait(2), 'Request completion audit was not emitted')
            finally:
                logger.removeHandler(observer)
        records = [json.loads(record.getMessage()) for record in captured.records]
        self.assertTrue(any(record['route'] == 'blob' for record in records))
        encoded = json.dumps(records)
        for secret in [self.digest, '/v1/blobs/', 'limit=1', 'reader-test']:
            self.assertNotIn(secret, encoded)


if __name__ == '__main__':
    unittest.main()
