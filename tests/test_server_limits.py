"""Admission and redaction checks against actual listening HTTP sockets."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import inspect
import json
import queue
import socket
import tempfile
import threading
import time
from pathlib import Path
import unittest
from unittest.mock import patch

from polyia.server import make_server
from polyia.store import Ledger


TOKEN = 'operator-secret-not-for-logs'


class BoundaryLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.ledger = Ledger(root / 'state' / 'ledger.sqlite3', root, [
            {'id': 'R-1', 'title': 'Test record', 'verifier': 'artifact-integrity'},
        ])
        self.addCleanup(self.ledger.close)
        self.handler_states = {}

    def start_server(self, **limits):
        for name in limits:
            self.assertIn(name, inspect.signature(make_server).parameters,
                          'HTTP admission must expose its bounded configuration')
        server = make_server(self.ledger, token=TOKEN, **limits)
        ready = queue.Queue()
        base = server.RequestHandlerClass
        completed = set()
        active = set()
        condition = threading.Condition()
        original_thread = server.process_request_thread

        def observed_thread(request, address):
            with condition:
                active.add(address)
            try:
                original_thread(request, address)
            finally:
                with condition:
                    active.remove(address)
                    completed.add(address)
                    condition.notify_all()

        server.process_request_thread = observed_thread
        self.handler_states[server] = condition, completed

        class ObservedHandler(base):
            def setup(self):
                super().setup()
                ready.put(None)

        server.RequestHandlerClass = ObservedHandler
        worker = threading.Thread(target=server.serve_forever,
                                  kwargs={'poll_interval': 0.01}, daemon=True)
        worker.start()

        def stop():
            server.shutdown()
            server.server_close()
            worker.join(timeout=3)
            with condition:
                self.assertTrue(condition.wait_for(lambda: not active, timeout=3),
                                'Test connections must finish before closing their ledger')

        self.addCleanup(stop)
        return server, ready

    def request(self, server, method='GET', path='/healthz', headers=None, body=None):
        connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
        try:
            connection.connect()
            peer = connection.sock.getsockname()
            connection.request(method, path, headers=headers or {}, body=body)
            response = connection.getresponse()
            data = response.read()
            result = json.loads(data) if data else None
            if not result or result.get('error', {}).get('code') not in ('RATE_LIMITED', 'SERVER_BUSY'):
                condition, completed = self.handler_states[server]
                with condition:
                    self.assertTrue(condition.wait_for(lambda: peer in completed, timeout=3),
                                    'Response bytes can arrive before the handler releases its slot')
                    completed.remove(peer)
            return response.status, dict(response.getheaders()), result
        finally:
            connection.close()

    def eventually_available(self, server):
        deadline = time.monotonic() + 2
        while True:
            response = self.request(server)
            if response[0] != 503 or time.monotonic() >= deadline:
                return response
            time.sleep(0.01)

    def hold_headers(self, server, ready):
        connection = socket.create_connection(('127.0.0.1', server.server_port), timeout=3)
        self.addCleanup(connection.close)
        connection.sendall(f'GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{server.server_port}\r\n'.encode())
        ready.get(timeout=2)
        return connection

    def test_slow_headers_cannot_create_a_second_handler_and_disconnect_releases_slot(self):
        server, ready = self.start_server(max_active_requests=1)
        first = self.hold_headers(server, ready)
        response = self.request(server)
        self.assertEqual(response[0], 503)
        self.assertEqual(response[2]['error']['code'], 'SERVER_BUSY')
        self.assertEqual(response[1]['Connection'], 'close')
        self.assertEqual(response[1]['Cache-Control'], 'no-store')
        self.assertEqual(response[1].get('X-Frame-Options'), 'DENY')
        self.assertEqual(response[1].get('Referrer-Policy'), 'no-referrer')
        self.assertIn("default-src 'none'", response[1].get('Content-Security-Policy', ''))
        self.assertGreaterEqual(int(response[1]['Retry-After']), 1)
        self.assertTrue(ready.empty(), 'Rejected connections must not start handler threads')
        first.close()
        self.assertEqual(self.eventually_available(server)[0], 200)

    def test_header_timeout_releases_the_only_handler_slot(self):
        server, ready = self.start_server(max_active_requests=1, socket_timeout=0.1)
        first = self.hold_headers(server, ready)
        self.assertEqual(first.recv(4096), b'')
        self.assertEqual(self.eventually_available(server)[0], 200)

    def test_auth_and_json_refusals_release_slots_without_mutation(self):
        server, _ = self.start_server(max_active_requests=1)
        self.assertEqual(self.request(server, path='/v1/state')[0], 401)
        self.assertEqual(self.eventually_available(server)[0], 200)
        response = self.request(server, method='POST', path='/v1/commands',
                                headers={'Authorization': 'Bearer ' + TOKEN,
                                         'Content-Type': 'application/json'}, body=b'{')
        self.assertEqual(response[0], 400)
        self.assertEqual(self.eventually_available(server)[0], 200)
        self.assertEqual(self.ledger.state()['revision'], 0)

    def test_global_rate_budget_counts_unauthenticated_requests_and_ignores_forwarded_identity(self):
        server, _ = self.start_server(request_rate=1.0, request_burst=2)
        for address in ('192.0.2.1', '198.51.100.1'):
            response = self.request(server, path='/v1/state', headers={'X-Forwarded-For': address})
            self.assertEqual(response[0], 401)
        response = self.request(server, headers={'X-Forwarded-For': '203.0.113.1',
                                                 'CF-Connecting-IP': '203.0.113.2'})
        self.assertEqual(response[0], 429)
        self.assertEqual(response[2]['error']['code'], 'RATE_LIMITED')
        self.assertEqual(response[1]['Retry-After'], '1')
        time.sleep(1.05)
        self.assertEqual(self.request(server)[0], 200)
        self.assertEqual(self.ledger.state()['revision'], 0)

    def test_simultaneous_requests_share_one_atomic_rate_budget(self):
        server, _ = self.start_server(request_rate=0.001, request_burst=3)
        start = threading.Barrier(8)

        def fetch(_):
            start.wait(timeout=3)
            return self.request(server)[0]

        with ThreadPoolExecutor(max_workers=8) as pool:
            statuses = list(pool.map(fetch, range(8)))
        self.assertEqual(sorted(statuses), [200, 200, 200, 429, 429, 429, 429, 429])

    def test_logging_covers_pre_auth_and_parse_failures_without_input_values(self):
        server, _ = self.start_server()
        responses = []
        with self.assertLogs('polyia.server', level='INFO') as captured:
            responses.append(self.request(server, path='/v1/state',
                                          headers={'Authorization': 'Bearer HEADER-CANARY'}))
            responses.append(self.request(server, method='POST', path='/v1/commands',
                headers={'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'},
                body=b'{"private": "BODY-CANARY",}'))
            responses.append(self.request(server, path='/healthz?token=QUERY-CANARY'))
            responses.append(self.request(server, path='/PATH-CANARY'))
            responses.append(self.request(server, method='METHOD-CANARY'))
            responses.append(self.request(server, headers={'Host': 'HOST-CANARY'}))
            responses.append(self.request(server))
            deadline = time.monotonic() + 2
            while len(captured.records) < 7 and time.monotonic() < deadline:
                time.sleep(0.01)
        self.assertEqual([response[0] for response in responses], [401, 400, 400, 404, 501, 421, 200])
        self.assertEqual(len(captured.records), 7)
        records = [json.loads(record.getMessage()) for record in captured.records]
        self.assertEqual([record['status'] for record in records], [401, 400, 400, 404, 501, 421, 200])
        for record in records:
            self.assertEqual(set(record), {'event', 'request_id', 'method', 'route', 'status'})
            self.assertEqual(record['event'], 'http_access')
            self.assertRegex(record['request_id'], r'^[0-9a-f]{32}$')
        self.assertEqual(records[0]['route'], 'state')
        self.assertEqual(records[1]['route'], 'commands')
        self.assertEqual(records[3]['route'], 'unknown')
        self.assertEqual(records[4]['method'], 'OTHER')
        serialized = json.dumps(records)
        for secret in (TOKEN, 'HEADER-CANARY', 'BODY-CANARY', 'QUERY-CANARY',
                       'PATH-CANARY', 'METHOD-CANARY', 'HOST-CANARY'):
            self.assertNotIn(secret, serialized)
        self.assertEqual(self.ledger.state()['revision'], 0)

    def test_admission_refusals_have_redacted_correlated_records(self):
        server, ready = self.start_server(max_active_requests=1, request_rate=0.001, request_burst=2)
        first = self.hold_headers(server, ready)
        with self.assertLogs('polyia.server', level='INFO') as captured:
            busy = self.request(server, path='/PRIVATE-PATH', headers={'Authorization': 'Bearer SECRET'})
            rate = self.request(server, method='PRIVATE-METHOD', path='/PRIVATE-PATH')
            deadline = time.monotonic() + 2
            while len(captured.records) < 2 and time.monotonic() < deadline:
                time.sleep(0.01)
        self.assertEqual([busy[0], rate[0]], [503, 429])
        records = [json.loads(record.getMessage()) for record in captured.records]
        self.assertEqual([record['status'] for record in records], [503, 429])
        self.assertEqual([record['request_id'] for record in records],
                         [busy[2]['request_id'], rate[2]['request_id']])
        self.assertTrue(all(record['method'] == 'OTHER' and record['route'] == 'unparsed' for record in records))
        self.assertNotIn('SECRET', json.dumps(records))
        first.close()

    def test_thread_start_failure_releases_admission_without_logging_exception_details(self):
        server, _ = self.start_server(max_active_requests=1)
        with self.assertLogs('polyia.server', level='ERROR') as captured:
            with patch('threading.Thread.start', side_effect=RuntimeError('PRIVATE-FAILURE')):
                with socket.create_connection(('127.0.0.1', server.server_port), timeout=3) as connection:
                    self.assertEqual(connection.recv(1024), b'')
        self.assertNotIn('PRIVATE-FAILURE', ' '.join(captured.output))
        self.assertEqual(self.eventually_available(server)[0], 200)

    def test_unsafe_numeric_and_boolean_configuration_is_rejected(self):
        for kwargs in ({'max_active_requests': 0}, {'max_active_requests': True},
                       {'request_rate': float('inf')}, {'request_rate': float('nan')},
                       {'request_rate': 0}, {'request_burst': False}, {'request_burst': 0},
                       {'socket_timeout': 0}, {'socket_timeout': float('nan')},
                       {'request_rate': 10**1000}, {'request_rate': 1e-320},
                       {'socket_timeout': 1e300}, {'max_active_requests': 1025},
                       {'request_burst': 1000001}):
            for name in kwargs:
                self.assertIn(name, inspect.signature(make_server).parameters)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                make_server(self.ledger, token=TOKEN, **kwargs)


if __name__ == '__main__':
    unittest.main()
