"""Real-process CLI checks: no mocked subprocesses or fake persistence."""
import json
import http.client
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.parse import urlsplit


PACKAGE_ROOT = Path(__file__).resolve().parent.parent


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.state_dir = self.root / "state"
        self.requirements = self.root / "requirements.json"
        self.requirements.write_text(json.dumps([
            {"id": "BOOT-001", "title": "Capture verification", "verifier": "artifact-integrity"},
            {"id": "BOOT-002", "title": "Scientific contracts", "verifier": "scientific-contracts"}]))

    def run_cli(self, *arguments, expected=0, env=None):
        environment = dict(os.environ)
        environment.pop("POLYIA_OPERATOR_TOKEN", None)
        environment.pop("POLYIA_READ_TOKEN", None)
        environment.update(env or {})
        result = subprocess.run([sys.executable, "-m", "polyia", *arguments,
                                 "--state-dir", str(self.state_dir), "--workspace", str(self.workspace)],
                                cwd=PACKAGE_ROOT, text=True, capture_output=True, timeout=20, env=environment)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def initialize(self):
        return json.loads(self.run_cli("init", "--requirements", str(self.requirements)).stdout)

    def test_init_status_verify_across_distinct_processes(self):
        initialized = self.initialize()
        self.assertEqual(initialized["state"]["revision"], 0)
        status = json.loads(self.run_cli("status").stdout)
        self.assertEqual(status["commission_status"], "NOT_COMMISSIONED")
        verified = json.loads(self.run_cli("verify").stdout)
        self.assertTrue(verified["ok"])
        self.assertEqual(verified["checked"]["events"], 0)

    def test_command_file_retry_reuses_durable_receipt_in_new_process(self):
        self.initialize()
        path = self.root / "command.json"
        path.write_text(json.dumps({"command_id": "cli-one", "expected_revision": 0,
                                   "kind": "checkpoint.create", "payload": {"note": "new process"}}))
        first = json.loads(self.run_cli("command", "--file", str(path)).stdout)
        second = json.loads(self.run_cli("command", "--file", str(path)).stdout)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(self.run_cli("status").stdout)["revision"], 1)

    def test_stale_cli_command_is_explicit_error_and_leaves_revision(self):
        self.initialize()
        path = self.root / "command.json"
        path.write_text(json.dumps({"command_id": "stale", "expected_revision": 4,
                                   "kind": "checkpoint.create", "payload": {"note": "stale"}}))
        failure = self.run_cli("command", "--file", str(path), expected=2)
        self.assertEqual(json.loads(failure.stderr)["error"]["code"], "REVISION_CONFLICT")
        self.assertEqual(json.loads(self.run_cli("status").stdout)["revision"], 0)

    def test_serve_requires_environment_operator_token(self):
        self.initialize()
        result = self.run_cli("serve", "--port", "0", expected=2)
        self.assertEqual(json.loads(result.stderr)["error"]["code"], "MISSING_OPERATOR_TOKEN")

    def test_read_commands_do_not_silently_initialize_a_missing_ledger(self):
        result = self.run_cli("status", expected=2)
        self.assertEqual(json.loads(result.stderr)["error"]["code"], "NOT_INITIALIZED")
        self.assertFalse((self.state_dir / "ledger.sqlite3").exists())

    def test_worker_zero_iterations_does_not_claim_unperformed_experiments(self):
        self.initialize()
        result = json.loads(self.run_cli("worker", "--iterations", "0").stdout)
        self.assertEqual(result["completed"], 0)
        self.assertEqual(result["runs"], [])
        self.assertEqual(json.loads(self.run_cli("status").stdout)["revision"], 0)

    def test_worker_respects_applied_research_pause(self):
        self.initialize()
        commands = [
            {"command_id": "pause", "expected_revision": 0, "kind": "guidance.submit",
             "payload": {"target": "research", "text": "pause", "action": {"kind": "pause_research"}}},
            {"command_id": "ack", "expected_revision": 1, "kind": "guidance.ack",
             "payload": {"guidance_id": "pause", "disposition": "ACKNOWLEDGED", "reason": "requested"}},
            {"command_id": "apply", "expected_revision": 2, "kind": "guidance.apply", "payload": {"guidance_id": "pause"}},
        ]
        for command in commands:
            path = self.root / "command.json"
            path.write_text(json.dumps(command))
            self.run_cli("command", "--file", str(path))
        result = json.loads(self.run_cli("worker", "--iterations", "3").stdout)
        self.assertEqual(result["status"], "PAUSED")
        self.assertEqual(result["completed"], 0)
        self.assertEqual(json.loads(self.run_cli("status").stdout)["revision"], 3)

    def test_commit_survives_process_exit_before_receipt_delivery(self):
        self.initialize()
        request = {"command_id": "lost-response", "expected_revision": 0,
                   "kind": "checkpoint.create", "payload": {"note": "commit before process exit"}}
        script = """import json, os, sys
from polyia.store import Ledger
ledger = Ledger(sys.argv[1], sys.argv[2])
ledger.command(json.loads(sys.argv[3]), actor='local-operator')
os._exit(23)
"""
        result = subprocess.run([sys.executable, "-c", script, str(self.state_dir / "ledger.sqlite3"),
                                 str(self.workspace), json.dumps(request)], cwd=PACKAGE_ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(result.stdout, "")
        path = self.root / "retry.json"
        path.write_text(json.dumps(request))
        receipt = json.loads(self.run_cli("command", "--file", str(path)).stdout)
        self.assertEqual(receipt["revision"], 1)
        verified = json.loads(self.run_cli("verify").stdout)
        self.assertEqual(verified["checked"]["events"], 1)
        self.assertTrue(verified["ok"])

    def test_demo_executes_artifact_science_guidance_and_checkpoint_flow(self):
        self.initialize()
        report = json.loads(self.run_cli("demo").stdout)
        self.assertTrue(report["ok"])
        self.assertTrue(report["verification"]["ok"])
        state = json.loads(self.run_cli("status").stdout)
        self.assertEqual(state["requirements"]["BOOT-001"]["status"], "ACCEPTED")
        self.assertEqual(state["requirements"]["BOOT-002"]["status"], "ACCEPTED")
        self.assertEqual(state["requirements"]["BOOT-001"]["priority"], 7)
        self.assertTrue(any(guidance["status"] == "APPLIED" for guidance in state["guidance"].values()))
        self.assertIsNotNone(state["latest_checkpoint"])
        self.assertEqual(state["runs"][0]["report"]["status"], "PASS")
        self.assertEqual(state["commission_status"], "NOT_COMMISSIONED")

    def test_worker_records_the_requested_finite_number_of_real_runs(self):
        self.initialize()
        report = json.loads(self.run_cli("worker", "--iterations", "2").stdout)
        self.assertEqual(report["completed"], 2)
        self.assertTrue(all(receipt["result"]["run"]["report"]["status"] == "PASS" for receipt in report["runs"]))
        self.assertEqual(len(json.loads(self.run_cli("status").stdout)["runs"]), 2)

    def test_serve_process_commits_authenticated_command_and_shuts_down_cleanly(self):
        self.initialize()
        output_path, error_path = self.root / "server-output.json", self.root / "server-error.txt"
        token = "cli-integration-test-operator-credential"
        environment = dict(os.environ, POLYIA_OPERATOR_TOKEN=token)
        environment.pop("POLYIA_READ_TOKEN", None)
        environment.pop("POLYIA_PUBLIC_ORIGIN", None)
        with output_path.open("w") as output, error_path.open("w") as errors:
            process = subprocess.Popen([sys.executable, "-m", "polyia", "serve", "--port", "0",
                                        "--state-dir", str(self.state_dir), "--workspace", str(self.workspace)],
                                       cwd=PACKAGE_ROOT, env=environment, stdout=output, stderr=errors)
            try:
                startup = None
                deadline = time.monotonic() + 8
                while time.monotonic() < deadline and process.poll() is None:
                    try:
                        startup = json.loads(output_path.read_text())
                        break
                    except json.JSONDecodeError:
                        time.sleep(0.01)
                self.assertIsNotNone(startup, error_path.read_text())
                self.assertEqual(startup["status"], "LISTENING")
                self.assertNotIn(token, output_path.read_text())
                endpoint = urlsplit(startup["url"])
                connection = http.client.HTTPConnection(endpoint.hostname, endpoint.port, timeout=5)
                request = {"command_id": "through-process", "expected_revision": 0,
                           "kind": "checkpoint.create", "payload": {"note": "HTTP process transition"}}
                try:
                    connection.request("POST", "/v1/commands", json.dumps(request),
                                       {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
                    response = connection.getresponse()
                    body = json.loads(response.read())
                    self.assertEqual(response.status, 200, body)
                    self.assertEqual(body["revision"], 1)
                finally:
                    connection.close()
                process.terminate()
                self.assertEqual(process.wait(timeout=5), 0, error_path.read_text())
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
        self.assertEqual(json.loads(self.run_cli("status").stdout)["revision"], 1)
        self.assertTrue(json.loads(self.run_cli("verify").stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
