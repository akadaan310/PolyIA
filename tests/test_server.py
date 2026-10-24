"""HTTP protocol tests using a listening socket and the real SQLite ledger."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import importlib
import json
from pathlib import Path
import socket
import tempfile
import threading
import unittest


OPERATOR_TOKEN = "test-operator-token-that-is-never-in-assets"
READ_TOKEN = "test-read-token-that-is-never-in-assets"


class HTTPTests(unittest.TestCase):
    def setUp(self):
        try:
            module = importlib.import_module("polyia.server")
        except ModuleNotFoundError:
            module = None
        self.assertIsNotNone(module, "The real HTTP command plane is not implemented yet")
        self.make_server = module.make_server
        from polyia.store import Ledger
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        (self.workspace / "proof.txt").write_text("Captured evidence from the test workspace.\n")
        self.ledger = Ledger(self.root / "state" / "ledger.sqlite3", self.workspace, [
            {"id": "R-1", "title": "Recorded artifact", "verifier": "artifact-integrity"},
        ])
        self.addCleanup(self.ledger.close)
        self.server = self.make_server(self.ledger, token=OPERATOR_TOKEN, read_token=READ_TOKEN)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.counter = 0

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, method, path, *, token=OPERATOR_TOKEN, data=None, raw=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        request_headers = {}
        if token is not None:
            request_headers["Authorization"] = "Bearer " + token
        if data is not None:
            raw = json.dumps(data).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        request_headers.update(headers or {})
        try:
            connection.request(method, path, body=raw, headers=request_headers)
            response = connection.getresponse()
            body = response.read()
            content_type = response.getheader("Content-Type", "")
            result = json.loads(body) if "application/json" in content_type and body else body
            return response.status, dict(response.getheaders()), result
        finally:
            connection.close()

    def raw_request(self, request):
        with socket.create_connection(("127.0.0.1", self.server.server_port), timeout=5) as connection:
            connection.sendall(request)
            connection.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
        header, body = b"".join(chunks).split(b"\r\n\r\n", 1)
        return int(header.split(b" ")[1]), json.loads(body)

    def command_body(self, kind, payload, *, revision=None, command_id=None):
        self.counter += 1
        return {"command_id": command_id or f"http-{self.counter}",
                "expected_revision": self.ledger.state()["revision"] if revision is None else revision,
                "kind": kind, "payload": payload}

    def command(self, kind, payload, **kwargs):
        return self.request("POST", "/v1/commands", data=self.command_body(kind, payload, **kwargs))

    def assert_error(self, response, status, code):
        self.assertEqual(response[0], status, response)
        self.assertFalse(response[2]["ok"])
        self.assertEqual(response[2]["error"]["code"], code)
        self.assertTrue(response[2]["request_id"])

    def test_public_surface_is_live_but_contains_no_token_or_private_state(self):
        status, headers, health = self.request("GET", "/healthz", token=None)
        self.assertEqual(status, 200)
        self.assertTrue(health["ok"])
        self.assertNotIn("revision", health)
        status, headers, discovery = self.request("GET", "/.well-known/polyia.json", token=None)
        self.assertEqual(status, 200)
        self.assertTrue(discovery["capabilities"]["event_polling"])
        for unavailable in ("sse", "websocket", "llm_inference", "remote_binding"):
            self.assertFalse(discovery["capabilities"][unavailable])
        for path, content_type in (("/", "text/html"), ("/app.js", "javascript"),
                                   ("/client.mjs", "javascript"), ("/styles.css", "text/css")):
            status, headers, body = self.request("GET", path, token=None)
            self.assertEqual(status, 200)
            self.assertIn(content_type, headers["Content-Type"])
            self.assertNotIn(OPERATOR_TOKEN.encode(), body)
            self.assertNotIn(READ_TOKEN.encode(), body)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_all_private_reads_require_bearer_authorization(self):
        for path in ("/v1/state", "/v1/events", "/v1/verify", "/v1/commands/missing",
                     "/v1/checkpoints/latest", "/v1/refusals"):
            with self.subTest(path=path):
                response = self.request("GET", path, token=None)
                self.assert_error(response, 401, "UNAUTHORIZED")
                self.assertEqual(response[1]["WWW-Authenticate"], 'Bearer realm="polyia"')
        self.assert_error(self.request("GET", "/v1/state", token="wrong"), 401, "UNAUTHORIZED")

    def test_operator_and_read_token_can_read_but_read_token_cannot_mutate(self):
        for token, scope in ((OPERATOR_TOKEN, "operator"), (READ_TOKEN, "read")):
            response = self.request("GET", "/v1/state", token=token)
            self.assertEqual(response[0], 200)
            self.assertEqual(response[1]["X-PolyIA-Scope"], scope)
            self.assertEqual(response[2]["revision"], 0)
            self.assertEqual(response[2]["commission_status"], "NOT_COMMISSIONED")
        body = self.command_body("checkpoint.create", {"note": "reader cannot apply"})
        self.assert_error(self.request("POST", "/v1/commands", token=READ_TOKEN, data=body), 403, "FORBIDDEN")
        self.assertEqual(self.ledger.state()["revision"], 0)

    def test_real_command_retry_conflict_receipt_and_resumable_events(self):
        body = self.command_body("guidance.submit", {"target": "R-1", "text": "Preserve <script>alert(1)</script> as text."})
        first = self.request("POST", "/v1/commands", data=body)
        retry = self.request("POST", "/v1/commands", data=body)
        self.assertEqual(first[0], 200)
        self.assertEqual(retry[2], first[2])
        self.assertEqual(first[2]["revision"], 1)
        lookup = self.request("GET", "/v1/commands/" + body["command_id"])
        self.assertEqual(lookup[2], first[2])
        self.assert_error(self.command("checkpoint.create", {"note": "stale"}, revision=0), 409, "REVISION_CONFLICT")
        changed = dict(body, payload={"target": "R-1", "text": "Different command"})
        self.assert_error(self.request("POST", "/v1/commands", data=changed), 409, "IDEMPOTENCY_CONFLICT")
        self.assertEqual(self.command("checkpoint.create", {"note": "next"})[0], 200)
        events = self.request("GET", "/v1/events?after=0&limit=1")[2]
        self.assertEqual([item["sequence"] for item in events["events"]], [1])
        self.assertEqual(events["events"][0]["payload"]["request"], body)
        self.assertEqual(events["next_after"], 1)
        later = self.request("GET", "/v1/events?after=1&limit=100")[2]
        self.assertEqual([item["sequence"] for item in later["events"]], [2])
        self.assertEqual(later["next_after"], 2)
        self.assertEqual(self.ledger.state()["revision"], 2)
        refusals = self.request("GET", "/v1/refusals?limit=10", token=READ_TOKEN)[2]["refusals"]
        self.assertEqual({item["code"] for item in refusals}, {"REVISION_CONFLICT", "IDEMPOTENCY_CONFLICT"})

    def test_guidance_submit_acknowledge_apply_changes_real_state(self):
        receipt = self.command("guidance.submit", {"target": "R-1", "text": "Move this first",
            "action": {"kind": "set_priority", "target": "R-1", "priority": 9}})
        self.assertEqual(receipt[0], 200)
        guidance_id = receipt[2]["result"]["guidance_id"]
        self.assertEqual(self.command("guidance.ack", {"guidance_id": guidance_id,
            "disposition": "ACKNOWLEDGED", "reason": "Reviewed"})[0], 200)
        self.assertEqual(self.command("guidance.apply", {"guidance_id": guidance_id})[0], 200)
        state = self.request("GET", "/v1/state")[2]
        self.assertEqual(state["requirements"]["R-1"]["priority"], 9)
        self.assertEqual(state["guidance"][guidance_id]["status"], "APPLIED")
        self.assertEqual(state["guidance"][guidance_id]["applied_revision"], 3)

    def test_produce_verify_accept_checkpoint_and_integrity_are_real(self):
        self.assertEqual(self.command("requirement.produce", {"requirement_id": "R-1",
            "artifacts": ["proof.txt"], "note": "Capture local bytes"})[0], 200)
        self.assert_error(self.command("requirement.accept", {"requirement_id": "R-1"}), 409, "INVALID_TRANSITION")
        verified = self.command("requirement.verify", {"requirement_id": "R-1"})
        self.assertEqual(verified[2]["result"]["verification"]["evidence_class"], "ARTIFACT_INTEGRITY")
        self.assertEqual(self.command("requirement.accept", {"requirement_id": "R-1"})[0], 200)
        receipt = self.command("checkpoint.create", {"note": "Accepted captured bytes"})[2]
        checkpoint_id = receipt["result"]["checkpoint_id"]
        checkpoint = self.request("GET", "/v1/checkpoints/" + checkpoint_id)[2]
        latest = self.request("GET", "/v1/checkpoints/latest")[2]
        self.assertEqual(checkpoint, latest)
        self.assertEqual(checkpoint["head"], receipt["head"])
        self.assertEqual(checkpoint["state"]["requirements"]["R-1"]["status"], "ACCEPTED")
        self.assertTrue(self.request("GET", "/v1/verify", token=READ_TOKEN)[2]["ok"])
        self.assertEqual(self.request("GET", "/v1/state")[2]["commission_status"], "NOT_COMMISSIONED")

    def test_unavailable_command_and_missing_read_have_explicit_safe_errors(self):
        self.assert_error(self.request("GET", "/v1/commands/missing"), 404, "NOT_FOUND")
        self.assert_error(self.request("GET", "/v1/checkpoints/latest"), 404, "NOT_FOUND")
        self.assert_error(self.request("GET", "/v1/checkpoints/missing"), 404, "NOT_FOUND")
        response = self.command("arbitrary.execute", {"program": "not executable"})
        self.assertEqual(response[0], 400)
        self.assertFalse(response[2]["ok"])
        self.assertEqual(self.ledger.state()["revision"], 0)

    def test_two_real_http_writers_cannot_apply_one_revision(self):
        first = self.command_body("checkpoint.create", {"note": "one"}, revision=0)
        second = self.command_body("checkpoint.create", {"note": "two"}, revision=0)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda body: self.request("POST", "/v1/commands", data=body), [first, second]))
        self.assertEqual(sorted(result[0] for result in results), [200, 409])
        self.assertEqual(self.ledger.state()["revision"], 1)
        self.assertTrue(self.ledger.verify()["ok"])

    def test_json_media_type_and_body_budget_are_enforced(self):
        self.assert_error(self.request("POST", "/v1/commands", raw=b"{}",
            headers={"Content-Type": "text/plain"}), 415, "UNSUPPORTED_MEDIA_TYPE")
        self.assert_error(self.request("POST", "/v1/commands", raw=b"{}",
            headers={"Content-Type": "application/json; charset=latin-1"}), 415, "UNSUPPORTED_MEDIA_TYPE")
        self.assert_error(self.request("POST", "/v1/commands", raw=b"x" * 65537,
            headers={"Content-Type": "application/json"}), 413, "BODY_TOO_LARGE")
        self.assertEqual(self.ledger.state()["revision"], 0)

    def test_malformed_nonfinite_duplicate_and_deep_json_are_refused(self):
        for raw in (b"{", b"\xff", b"[]", b"null", b'{"a":1,"a":2}', b'{"value":NaN}',
                    b'{"value":Infinity}', b"[" * 80 + b"0" + b"]" * 80):
            with self.subTest(raw=raw[:40]):
                result = self.request("POST", "/v1/commands", raw=raw, headers={"Content-Type": "application/json"})
                self.assertEqual(result[0], 400)
                self.assertFalse(result[2]["ok"])
        self.assertEqual(self.ledger.state()["revision"], 0)

    def test_exact_top_level_schema_cannot_smuggle_status_or_boolean_revision(self):
        good = self.command_body("checkpoint.create", {"note": "candidate"})
        for changed in (dict(good, status="ACCEPTED"), dict(good, expected_revision=True),
                        dict(good, payload=[]), dict(good, command_id=""),
                        {key: value for key, value in good.items() if key != "expected_revision"}):
            with self.subTest(request=changed):
                self.assert_error(self.request("POST", "/v1/commands", data=changed), 400, "INVALID_REQUEST")
        self.assertEqual(self.ledger.state()["revision"], 0)

    def test_invalid_event_parameters_and_unknown_paths_are_safe(self):
        for query in ("after=-1", "after=1.2", "after=true", "limit=0", "limit=1001",
                      "limit=1&limit=2", "after=", "token=secret", "after=999999999999999999999999999999"):
            with self.subTest(query=query):
                self.assert_error(self.request("GET", "/v1/events?" + query), 400, "INVALID_QUERY")
        for path in ("/missing", "/../polyia/store.py", "/%2e%2e/polyia/store.py", "/app.js/extra", "/v1/commands/a%2fb"):
            response = self.request("GET", path)
            self.assertIn(response[0], (400, 404))
            self.assertFalse(response[2]["ok"])
        self.assert_error(self.request("GET", "/v1/state?token=secret"), 400, "INVALID_QUERY")

    def test_cross_origin_and_host_rebinding_are_refused(self):
        body = self.command_body("checkpoint.create", {"note": "origin"})
        for origin in ("https://evil.example", "null", "http://localhost:1"):
            self.assert_error(self.request("POST", "/v1/commands", data=body,
                headers={"Origin": origin}), 403, "ORIGIN_FORBIDDEN")
        self.assert_error(self.request("GET", "/v1/state", headers={"Host": "evil.example"}), 421, "HOST_FORBIDDEN")
        self.assert_error(self.request("POST", "/v1/commands", data=body,
            headers={"Sec-Fetch-Site": "cross-site"}), 403, "ORIGIN_FORBIDDEN")
        origin = f"http://127.0.0.1:{self.server.server_port}"
        self.assertEqual(self.request("POST", "/v1/commands", data=body, headers={"Origin": origin})[0], 200)
        self.assertEqual(self.ledger.state()["revision"], 1)

    def test_ambiguous_framing_headers_are_rejected_before_mutation(self):
        port = self.server.server_port
        base = f"POST /v1/commands HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nAuthorization: Bearer {OPERATOR_TOKEN}\r\nContent-Type: application/json\r\n"
        cases = (
            (base + "Content-Length: 2\r\nContent-Length: 2\r\n\r\n{}", 400),
            (base + "Transfer-Encoding: chunked\r\n\r\n0\r\n\r\n", 400),
            (base + "\r\n{}", 411),
            (base + "Content-Length: -1\r\n\r\n", 400),
        )
        for wire, expected in cases:
            with self.subTest(wire=wire[-90:]):
                status, result = self.raw_request(wire.encode("ascii"))
                self.assertEqual(status, expected)
                self.assertFalse(result["ok"])
        self.assertEqual(self.ledger.state()["revision"], 0)

    def test_duplicate_authorization_host_and_origin_are_not_ambiguous(self):
        port = self.server.server_port
        base = f"GET /v1/state HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nAuthorization: Bearer {OPERATOR_TOKEN}\r\n"
        for extra in ("Authorization: Bearer wrong", "Host: evil.example",
                      f"Origin: http://127.0.0.1:{port}\r\nOrigin: https://evil.example"):
            status, result = self.raw_request((base + extra + "\r\n\r\n").encode("ascii"))
            self.assertIn(status, (400, 401, 403, 421))
            self.assertFalse(result["ok"])

    def test_known_route_wrong_method_is_safe_and_has_no_cors_wildcard(self):
        response = self.request("OPTIONS", "/v1/commands", headers={"Origin": "https://evil.example"})
        self.assertIn(response[0], (403, 405))
        self.assertNotIn("Access-Control-Allow-Origin", response[1])
        self.assert_error(self.request("GET", "/v1/commands"), 405, "METHOD_NOT_ALLOWED")
        self.assert_error(self.request("DELETE", "/v1/state"), 405, "METHOD_NOT_ALLOWED")

    def test_loopback_binding_and_separate_nonempty_tokens_are_required(self):
        for host in ("0.0.0.0", "192.0.2.1", "example.com", "::"):
            with self.subTest(host=host), self.assertRaises(ValueError):
                self.make_server(self.ledger, host=host, token=OPERATOR_TOKEN)
        for kwargs in ({}, {"token": ""}, {"token": "contains whitespace"},
                       {"token": OPERATOR_TOKEN, "read_token": OPERATOR_TOKEN}):
            with self.subTest(kwargs=kwargs), self.assertRaises((ValueError, TypeError)):
                self.make_server(self.ledger, **kwargs)

    def test_public_https_origin_is_explicit_and_matches_host(self):
        with self.make_server(self.ledger, token=OPERATOR_TOKEN,
                              public_origin="https://commission.example.test") as server:
            thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
            thread.start()
            original = self.server
            self.server = server
            try:
                allowed = self.request("GET", "/v1/state", headers={"Host": "commission.example.test",
                    "Origin": "https://commission.example.test"})
                self.assertEqual(allowed[0], 200)
                self.assert_error(self.request("GET", "/v1/state", headers={"Host": "commission.example.test",
                    "Origin": "https://different.example.test"}), 403, "ORIGIN_FORBIDDEN")
                self.assert_error(self.request("GET", "/v1/state", headers={"Origin": "https://commission.example.test"}),
                    403, "ORIGIN_FORBIDDEN")
                self.assertEqual(self.request("GET", "/v1/state")[0], 200)
            finally:
                self.server = original
                server.shutdown()
                thread.join(timeout=3)
        for origin in ("http://example.test", "https://example.test/path", "https://user@example.test",
                       "https://*.example.test", "https://example.test?x=1", "null"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                self.make_server(self.ledger, token=OPERATOR_TOKEN, public_origin=origin)

    def test_openapi_discovery_resolves_to_the_exact_command_contract(self):
        discovery = self.request("GET", "/.well-known/polyia.json", token=None)[2]
        response = self.request("GET", discovery["openapi"], token=None)
        self.assertEqual(response[0], 200)
        schema = response[2]
        self.assertEqual(schema["openapi"], "3.1.0")
        command = schema["paths"]["/v1/commands"]["post"]
        self.assertEqual(command["security"], [{"operatorBearer": []}])
        self.assertEqual(command["requestBody"]["content"]["application/json"]["schema"],
                         {"$ref": "#/components/schemas/Command"})
        self.assertEqual(len(schema["components"]["schemas"]["Command"]["oneOf"]), 8)

    def test_science_runs_record_actual_result_and_respect_guidance_pause(self):
        for name in ("polynomial", "grammar-promotion", "qpath", "acceptance"):
            receipt = self.command("experiment.run", {"name": name, "parameters": {}})
            self.assertEqual(receipt[0], 200)
            run = receipt[2]["result"]["run"]
            self.assertEqual(run["name"], name)
            self.assertEqual(run["report"]["status"], "PASS")
            self.assertTrue(run["report"]["checks"])
            self.assertTrue(run["report"]["limitations"])
            self.assertEqual(len(run["code_identity"]["sha256"]), 64)
        submission = self.command("guidance.submit", {"target": "research", "text": "Pause exact runs",
            "action": {"kind": "pause_research"}})[2]
        guidance_id = submission["result"]["guidance_id"]
        self.command("guidance.ack", {"guidance_id": guidance_id, "disposition": "ACKNOWLEDGED", "reason": "Approved pause"})
        self.command("guidance.apply", {"guidance_id": guidance_id})
        self.assert_error(self.command("experiment.run", {"name": "acceptance", "parameters": {}}), 409, "RESEARCH_PAUSED")
        self.assertEqual(len(self.request("GET", "/v1/state")[2]["runs"]), 4)

    def test_unexpected_runtime_exception_is_not_exposed_to_clients(self):
        original = self.ledger.state
        def broken_read():
            raise RuntimeError("private-path and token-like-secret must not be exposed")
        self.ledger.state = broken_read
        try:
            with self.assertLogs("polyia.server", level="ERROR") as captured:
                response = self.request("GET", "/v1/state")
            self.assert_error(response, 500, "INTERNAL_ERROR")
            self.assertNotIn("token-like-secret", json.dumps(response[2]))
            self.assertNotIn("token-like-secret", " ".join(captured.output))
        finally:
            self.ledger.state = original

    def test_head_responses_have_no_body_and_private_head_still_requires_auth(self):
        status, headers, body = self.request("HEAD", "/", token=None)
        self.assertEqual(status, 200)
        self.assertEqual(body, b"")
        self.assertGreater(int(headers["Content-Length"]), 0)
        self.assertEqual(self.request("HEAD", "/v1/state", token=None)[0], 401)


if __name__ == "__main__":
    unittest.main()
