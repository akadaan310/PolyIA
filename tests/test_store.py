"""Durability and authority tests against actual SQLite files and workspace bytes."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib
import json
from pathlib import Path
import sqlite3
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch


class StoreTests(unittest.TestCase):
    def setUp(self):
        try:
            module = importlib.import_module("polyia.store")
        except ModuleNotFoundError:
            module = None
        self.assertIsNotNone(module, "The durable bootstrap runtime is not implemented yet")
        self.Ledger, self.CommandError = module.Ledger, module.CommandError
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.database = self.root / "state" / "ledger.sqlite3"
        self.requirements = [
            {"id": "R-1", "title": "Captured evidence", "verifier": "artifact-integrity"},
            {"id": "R-2", "title": "Scientific contracts", "verifier": "scientific-contracts"},
            {"id": "R-3", "title": "Future integration", "verifier": "not-installed"},
        ]
        self.store = self.Ledger(self.database, self.workspace, self.requirements)
        self.addCleanup(self.store.close)
        self.counter = 0

    def request(self, kind, payload, *, revision=None, command_id=None):
        self.counter += 1
        return {"command_id": command_id or f"test-{self.counter}",
                "expected_revision": self.store.state()["revision"] if revision is None else revision,
                "kind": kind, "payload": payload}

    def command(self, kind, payload, **kwargs):
        return self.store.command(self.request(kind, payload, **kwargs))

    def artifact(self, name="evidence.txt", data=b"actual evidence\n"):
        (self.workspace / name).write_bytes(data)
        return name

    def produce(self, requirement_id="R-1"):
        artifact = self.artifact()
        if requirement_id == "R-2":
            kernel = Path(__file__).resolve().parent.parent / "polyia" / "experiments.py"
            artifact = self.artifact("kernel-copy.py", kernel.read_bytes())
        return self.command("requirement.produce", {
            "requirement_id": requirement_id, "artifacts": [artifact], "note": "captured"})

    def assertRefused(self, request, code=None, **kwargs):
        before = self.store.state()["revision"]
        with self.assertRaises(self.CommandError) as raised:
            self.store.command(request, **kwargs)
        if code:
            self.assertEqual(raised.exception.code, code)
        self.assertEqual(self.store.state()["revision"], before)
        return raised.exception

    def test_genesis_has_no_blanket_commission_acceptance(self):
        state = self.store.state()
        self.assertEqual(state["revision"], 0)
        self.assertEqual(state["commission_status"], "NOT_COMMISSIONED")
        self.assertEqual(state["requirements"]["R-1"]["status"], "NOT_STARTED")
        self.assertEqual(len(state["head"]), 64)
        self.assertTrue(self.store.verify()["ok"])

    def test_submitted_guidance_survives_new_instance_with_exact_receipt(self):
        request = self.request("guidance.submit", {"target": "R-1", "text": "retain <script> as text"})
        receipt = self.store.command(request, actor="alice")
        before = self.store.state()
        self.store.close()
        with self.Ledger(self.database, self.workspace) as reopened:
            self.assertEqual(reopened.state(), before)
            self.assertEqual(reopened.command(request, actor="alice"), receipt)
            self.assertEqual(reopened.state()["guidance"][request["command_id"]]["status"], "SUBMITTED")
            self.assertEqual(reopened.events()[0]["actor"], "alice")
            self.assertTrue(reopened.verify()["ok"])

    def test_exact_retry_is_idempotent_but_changed_request_conflicts(self):
        request = self.request("guidance.submit", {"target": "research", "text": "consider"})
        receipt = self.store.command(request)
        self.assertEqual(self.store.command(request), receipt)
        self.assertEqual(len(self.store.events()), 1)
        changed = dict(request, payload={"target": "research", "text": "changed"})
        self.assertRefused(changed, "IDEMPOTENCY_CONFLICT")

    def test_command_ids_are_scoped_by_actor(self):
        request = self.request("checkpoint.create", {"note": "first"}, command_id="shared")
        first = self.store.command(request, actor="alice")
        second = self.store.command(dict(request, expected_revision=1), actor="bob")
        self.assertEqual((first["revision"], second["revision"]), (1, 2))
        self.assertEqual(self.store.get_command("shared", actor="alice"), first)
        self.assertEqual(self.store.get_command("shared", actor="bob"), second)

    def test_two_connections_cannot_apply_the_same_revision(self):
        second = self.Ledger(self.database, self.workspace)
        self.addCleanup(second.close)
        gate = threading.Barrier(2)

        def apply(store, command_id):
            gate.wait()
            try:
                return store.command({"command_id": command_id, "expected_revision": 0,
                                      "kind": "checkpoint.create", "payload": {"note": command_id}})
            except self.CommandError as error:
                return error.code

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda pair: apply(*pair), [(self.store, "one"), (second, "two")]))
        self.assertEqual(sum(isinstance(item, dict) for item in results), 1)
        self.assertIn("REVISION_CONFLICT", results)
        self.assertEqual(self.store.state()["revision"], 1)
        self.assertTrue(self.store.verify()["ok"])

    def test_missing_command_scope_cannot_mutate(self):
        request = self.request("checkpoint.create", {"note": "forbidden"})
        self.assertRefused(request, "FORBIDDEN", scopes=("read",))
        self.assertEqual(self.store.refusals()[-1]["code"], "FORBIDDEN")

    def test_strict_request_schema_refuses_forged_verifier_result(self):
        self.produce()
        request = self.request("requirement.verify", {"requirement_id": "R-1", "outcome": "PASS"})
        self.assertRefused(request, "INVALID_PAYLOAD")
        self.assertEqual(self.store.state()["requirements"]["R-1"]["status"], "PRODUCED")
        self.assertTrue(self.store.verify()["ok"])

    def test_invalid_revision_and_nonobject_payload_are_retained_as_refusals(self):
        request = self.request("checkpoint.create", {"note": "bad"})
        self.assertRefused(dict(request, expected_revision=True), "INVALID_REQUEST")
        self.assertRefused(dict(request, payload=[]), "INVALID_REQUEST")
        self.assertEqual(len(self.store.refusals()), 2)

    def test_guidance_acknowledgment_then_apply_changes_actual_priority(self):
        submission = self.command("guidance.submit", {"target": "R-1", "text": "prioritize",
            "action": {"kind": "set_priority", "target": "R-1", "priority": 9}})
        guidance_id = submission["result"]["guidance_id"]
        self.command("guidance.ack", {"guidance_id": guidance_id, "disposition": "ACKNOWLEDGED", "reason": "accepted"})
        receipt = self.command("guidance.apply", {"guidance_id": guidance_id})
        state = self.store.state()
        self.assertEqual(state["requirements"]["R-1"]["priority"], 9)
        self.assertEqual(state["guidance"][guidance_id]["status"], "APPLIED")
        self.assertEqual(state["guidance"][guidance_id]["applied_revision"], receipt["revision"])
        self.assertTrue(state["guidance"][guidance_id]["effects"])

    def test_free_text_guidance_cannot_be_marked_applied(self):
        guidance_id = self.command("guidance.submit", {"target": "research", "text": "please improve"})["result"]["guidance_id"]
        self.command("guidance.ack", {"guidance_id": guidance_id, "disposition": "ACKNOWLEDGED", "reason": "read"})
        self.assertRefused(self.request("guidance.apply", {"guidance_id": guidance_id}), "NO_APPLICABLE_ACTION")
        self.assertEqual(self.store.state()["guidance"][guidance_id]["status"], "ACKNOWLEDGED")

    def test_unacknowledged_and_rejected_guidance_cannot_apply(self):
        guidance_id = self.command("guidance.submit", {"target": "research", "text": "pause",
            "action": {"kind": "pause_research"}})["result"]["guidance_id"]
        self.assertRefused(self.request("guidance.apply", {"guidance_id": guidance_id}), "INVALID_TRANSITION")
        self.command("guidance.ack", {"guidance_id": guidance_id, "disposition": "REJECTED", "reason": "continue"})
        self.assertRefused(self.request("guidance.apply", {"guidance_id": guidance_id}), "INVALID_TRANSITION")
        self.assertFalse(self.store.state()["research"]["paused"])

    def test_produce_verify_accept_uses_immutable_captured_bytes(self):
        self.produce()
        (self.workspace / "evidence.txt").write_bytes(b"changed after capture")
        self.command("requirement.verify", {"requirement_id": "R-1"})
        verified = self.store.state()["requirements"]["R-1"]
        self.assertEqual(verified["status"], "VERIFIED")
        self.assertEqual(verified["verification"]["outcome"], "PASS")
        self.assertEqual(verified["verification"]["evidence_class"], "ARTIFACT_INTEGRITY")
        self.command("requirement.accept", {"requirement_id": "R-1"})
        self.assertEqual(self.store.state()["requirements"]["R-1"]["status"], "ACCEPTED")
        self.assertEqual(self.store.state()["commission_status"], "NOT_COMMISSIONED")
        self.assertTrue(self.store.verify()["ok"])

    def test_accept_requires_current_verification_and_reproduction_invalidates_it(self):
        self.produce()
        self.assertRefused(self.request("requirement.accept", {"requirement_id": "R-1"}), "INVALID_TRANSITION")
        self.command("requirement.verify", {"requirement_id": "R-1"})
        self.produce()
        self.assertRefused(self.request("requirement.accept", {"requirement_id": "R-1"}), "INVALID_TRANSITION")

    def test_unsupported_verifier_retains_failure_without_acceptance(self):
        self.produce("R-3")
        receipt = self.command("requirement.verify", {"requirement_id": "R-3"})
        state = self.store.state()["requirements"]["R-3"]
        self.assertEqual(state["status"], "PRODUCED")
        self.assertEqual(receipt["result"]["verification"]["outcome"], "UNSUPPORTED")
        self.assertEqual(len(state["verification_attempts"]), 1)
        self.assertRefused(self.request("requirement.accept", {"requirement_id": "R-3"}), "INVALID_TRANSITION")

    def test_empty_artifacts_and_empty_files_are_rejected(self):
        self.assertRefused(self.request("requirement.produce", {"requirement_id": "R-1", "artifacts": [], "note": "empty"}), "INVALID_PAYLOAD")
        self.artifact("empty.txt", b"")
        self.assertRefused(self.request("requirement.produce", {"requirement_id": "R-1", "artifacts": ["empty.txt"], "note": "empty"}), "EMPTY_ARTIFACT")

    def test_unsafe_secret_runtime_and_escaping_symlink_artifacts_are_rejected(self):
        outside = self.root / "outside.txt"
        outside.write_text("outside")
        (self.workspace / "escape.txt").symlink_to(outside)
        (self.workspace / ".env").write_text("SECRET=example")
        (self.workspace / ".polyia-state").mkdir()
        (self.workspace / ".polyia-state" / "data.txt").write_text("private")
        for path in ["../outside.txt", str(outside), "escape.txt", ".env", ".polyia-state/data.txt"]:
            with self.subTest(path=path):
                self.assertRefused(self.request("requirement.produce", {"requirement_id": "R-1", "artifacts": [path], "note": "unsafe"}), "UNSAFE_ARTIFACT")

    def test_blob_corruption_is_detected_before_acceptance_and_on_reopen(self):
        self.produce()
        self.command("requirement.verify", {"requirement_id": "R-1"})
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE blobs SET data = ?", (b"altered evidence",))
        self.assertFalse(self.store.verify()["ok"])
        self.assertRefused(self.request("requirement.accept", {"requirement_id": "R-1"}), "INTEGRITY_ERROR")
        with self.assertRaises(self.CommandError) as raised:
            self.Ledger(self.database, self.workspace)
        self.assertEqual(raised.exception.code, "INTEGRITY_ERROR")

    def test_event_corruption_is_detected_without_repair(self):
        self.command("checkpoint.create", {"note": "original"})
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE events SET actor = 'forged' WHERE sequence = 1")
        report = self.store.verify()
        self.assertFalse(report["ok"])
        self.assertTrue(report["diagnostics"])
        with self.assertRaises(self.CommandError):
            self.Ledger(self.database, self.workspace)

    def test_current_state_corruption_is_detected(self):
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE materialized SET state_json = '{}' WHERE singleton = 1")
        self.assertFalse(self.store.verify()["ok"])

    def test_checkpoint_is_source_linked_and_tampering_is_detected(self):
        self.produce()
        receipt = self.command("checkpoint.create", {"note": "recoverable snapshot"})
        checkpoint_id = receipt["result"]["checkpoint_id"]
        checkpoint = self.store.get_checkpoint(checkpoint_id)
        self.assertEqual(checkpoint["revision"], 2)
        self.assertEqual(checkpoint["head"], receipt["head"])
        self.assertEqual(checkpoint["state"]["requirements"]["R-1"]["artifacts"][0]["sha256"], hashlib.sha256(b"actual evidence\n").hexdigest())
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE checkpoints SET state_json = '{}' WHERE checkpoint_id = ?", (checkpoint_id,))
        self.assertFalse(self.store.verify()["ok"])

    def test_event_pagination_and_refusal_receipts_are_distinct(self):
        for i in range(3):
            self.command("checkpoint.create", {"note": str(i)})
        self.assertRefused(self.request("checkpoint.create", {"note": "stale"}, revision=0), "REVISION_CONFLICT")
        self.assertEqual([event["sequence"] for event in self.store.events(after=1, limit=1)], [2])
        self.assertEqual(self.store.state()["revision"], 3)
        self.assertEqual(self.store.refusals()[-1]["code"], "REVISION_CONFLICT")

    def test_workspace_drift_is_reported_without_rewriting_captured_history(self):
        self.produce()
        (self.workspace / "evidence.txt").write_bytes(b"live workspace changed")
        report = self.store.verify()
        self.assertTrue(report["ok"])
        self.assertIn("workspace_drift", report)
        self.assertEqual(report["workspace_drift"]["changed"], 1)
        self.assertEqual(report["workspace_drift"]["artifacts"][0]["status"], "MODIFIED")
        (self.workspace / "evidence.txt").unlink()
        self.assertEqual(self.store.verify()["workspace_drift"]["artifacts"][0]["status"], "MISSING")

    def test_nonstring_disposition_is_refused_and_audited(self):
        guidance_id = self.command("guidance.submit", {"target": "research", "text": "consider"})["result"]["guidance_id"]
        self.assertRefused(self.request("guidance.ack", {"guidance_id": guidance_id, "disposition": [], "reason": "malformed"}), "INVALID_PAYLOAD")
        self.assertEqual(self.store.refusals()[-1]["code"], "INVALID_PAYLOAD")

    def test_nonstring_action_kind_is_refused_and_audited(self):
        self.assertRefused(self.request("guidance.submit", {"target": "research", "text": "malformed", "action": {"kind": []}}), "UNSUPPORTED_ACTION")
        self.assertEqual(self.store.refusals()[-1]["code"], "UNSUPPORTED_ACTION")

    def test_partial_capture_failure_rolls_back_blobs_and_state(self):
        initial_blobs = self.store.verify()["checked"]["blobs"]
        self.artifact()
        self.assertRefused(self.request("requirement.produce", {"requirement_id": "R-1", "artifacts": ["evidence.txt", "missing.txt"]}), "MISSING_ARTIFACT")
        self.assertEqual(self.store.state()["requirements"]["R-1"]["status"], "NOT_STARTED")
        report = self.store.verify()
        self.assertTrue(report["ok"])
        self.assertEqual(report["checked"]["blobs"], initial_blobs)

    def test_receipt_corruption_cannot_forge_an_idempotent_success(self):
        request = self.request("checkpoint.create", {"note": "original"})
        self.store.command(request)
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE receipts SET receipt_json = '{}' WHERE command_id=?", (request["command_id"],))
        self.assertFalse(self.store.verify()["ok"])
        self.assertRefused(request, "INTEGRITY_ERROR")

    def test_genesis_corruption_is_detected(self):
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE genesis SET digest = ?", ("0" * 64,))
        self.assertFalse(self.store.verify()["ok"])

    def test_historical_blobs_remain_checked_after_reproduction(self):
        initial_blobs = self.store.verify()["checked"]["blobs"]
        self.produce()
        original_digest = hashlib.sha256(b"actual evidence\n").hexdigest()
        self.artifact(data=b"new evidence")
        self.command("requirement.produce", {"requirement_id": "R-1", "artifacts": ["evidence.txt"]})
        self.assertEqual(self.store.verify()["checked"]["blobs"], initial_blobs + 2)
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE blobs SET data=? WHERE digest=?", (b"tampered old snapshot", original_digest))
        self.assertFalse(self.store.verify()["ok"])

    def test_scientific_contracts_run_real_registered_acceptance(self):
        self.produce("R-2")
        result = self.command("requirement.verify", {"requirement_id": "R-2"})
        verification = result["result"]["verification"]
        self.assertEqual(verification["outcome"], "PASS")
        self.assertGreaterEqual(len(verification["report"]["checks"]), 10)
        self.assertTrue(all(check["pass"] for check in verification["report"]["checks"]))
        self.assertNotEqual(verification["evidence_class"], "ARTIFACT_INTEGRITY")
        self.assertEqual(verification["code_identity"]["module"], "polyia.experiments")
        self.command("requirement.accept", {"requirement_id": "R-2"})
        self.assertEqual(self.store.state()["requirements"]["R-2"]["status"], "ACCEPTED")

    def test_experiment_replay_consumes_recorded_result_without_reexecution(self):
        self.command("experiment.run", {"name": "acceptance", "parameters": {}})
        before = self.store.state()
        self.store.close()
        # A fault sentinel at the registered execution boundary proves replay
        # never invokes that boundary; actual creation above used the real core.
        with patch("polyia.experiments.run_registered", side_effect=AssertionError("Replay executed an experiment")):
            with self.Ledger(self.database, self.workspace) as reopened:
                self.assertEqual(reopened.state(), before)
                self.assertTrue(reopened.verify()["ok"])

    def test_refused_scientific_inputs_are_retained_with_no_pass_claim(self):
        receipt = self.command("experiment.run", {"name": "polynomial", "parameters": {"b": [0]}})
        self.assertEqual(receipt["result"]["run"]["report"]["status"], "REFUSED")
        self.assertEqual(self.store.state()["runs"][0]["parameters"], {"b": [0]})
        self.assertEqual(self.store.state()["runs"][0]["report"]["status"], "REFUSED")
        self.assertTrue(self.store.verify()["ok"])

    def test_verifier_runtime_failure_is_retained_and_cannot_accept(self):
        self.produce("R-2")
        # Explicit fault injection, not a replacement success oracle: this
        # checks persistence of a runtime failure that the pure core seldom emits.
        with patch("polyia.experiments.Fraction", side_effect=RuntimeError("controlled failure")):
            receipt = self.command("requirement.verify", {"requirement_id": "R-2"})
        self.assertEqual(receipt["result"]["verification"]["outcome"], "ERROR")
        self.assertEqual(receipt["result"]["verification"]["report"]["reason"], "RuntimeError")
        requirement = self.store.state()["requirements"]["R-2"]
        self.assertEqual(requirement["status"], "PRODUCED")
        self.assertEqual(len(requirement["verification_attempts"]), 1)
        self.assertRefused(self.request("requirement.accept", {"requirement_id": "R-2"}), "INVALID_TRANSITION")

    def test_experiment_runtime_failure_is_retained_without_success_result(self):
        with patch("polyia.experiments.Fraction", side_effect=RuntimeError("controlled failure")):
            receipt = self.command("experiment.run", {"name": "acceptance", "parameters": {}})
        self.assertEqual(receipt["result"]["run"]["report"]["status"], "ERROR")
        self.assertEqual(receipt["result"]["run"]["report"]["result"]["error_type"], "RuntimeError")
        self.assertEqual(self.store.state()["runs"][0]["report"]["status"], "ERROR")
        self.assertTrue(self.store.verify()["ok"])

    def test_token_named_artifact_is_rejected(self):
        self.artifact("access_token.json", b'{"token":"example"}')
        self.assertRefused(self.request("requirement.produce", {"requirement_id": "R-1", "artifacts": ["access_token.json"]}), "UNSAFE_ARTIFACT")

    def test_open_does_not_silently_recreate_a_deleted_table(self):
        self.store.close()
        with sqlite3.connect(self.database) as raw:
            raw.execute("DROP TABLE checkpoints")
        with self.assertRaises(self.CommandError) as raised:
            self.Ledger(self.database, self.workspace)
        self.assertEqual(raised.exception.code, "INTEGRITY_ERROR")
        with sqlite3.connect(self.database) as raw:
            self.assertIsNone(raw.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'").fetchone())

    def test_open_reports_malformed_genesis_as_integrity_error(self):
        self.store.close()
        with sqlite3.connect(self.database) as raw:
            raw.execute("UPDATE genesis SET document_json = 'not json'")
        with self.assertRaises(self.CommandError) as raised:
            self.Ledger(self.database, self.workspace, self.requirements)
        self.assertEqual(raised.exception.code, "INTEGRITY_ERROR")

    def test_invalid_initial_requirements_leave_no_partial_ledger(self):
        database = self.root / "retry-init" / "ledger.sqlite3"
        with self.assertRaises(self.CommandError):
            self.Ledger(database, self.workspace, [{"id": "duplicate", "title": "bad", "verifier": "artifact-integrity"}] * 2)
        with self.Ledger(database, self.workspace, self.requirements) as initialized:
            self.assertEqual(initialized.state()["revision"], 0)
            self.assertTrue(initialized.verify()["ok"])

    def test_missing_safe_open_primitive_refuses_capture(self):
        self.artifact()
        with patch("polyia.store.os.O_NOFOLLOW", 0):
            self.assertRefused(self.request("requirement.produce", {"requirement_id": "R-1", "artifacts": ["evidence.txt"]}), "UNSUPPORTED_PLATFORM")

    def assert_corruption_blocks_commands_and_reopen(self, ledger, database):
        before = ledger.state()["revision"]
        self.assertFalse(ledger.verify()["ok"])
        with self.assertRaises(self.CommandError) as raised:
            ledger.command({"command_id": "after-corruption", "expected_revision": before,
                            "kind": "checkpoint.create", "payload": {"note": "must refuse"}})
        self.assertEqual(raised.exception.code, "INTEGRITY_ERROR")
        self.assertEqual(ledger.state()["revision"], before)
        with self.assertRaises(self.CommandError) as raised:
            self.Ledger(database, self.workspace)
        self.assertEqual(raised.exception.code, "INTEGRITY_ERROR")

    def test_materialization_scalar_type_corruption_is_never_equal(self):
        cases = [("integer-to-float", ("requirements", "R-1", "priority"), 5.0),
                 ("boolean-to-integer", ("research", "paused"), 0)]
        for name, path, value in cases:
            with self.subTest(case=name):
                database = self.root / name / "ledger.sqlite3"
                with self.Ledger(database, self.workspace, self.requirements) as ledger:
                    with sqlite3.connect(database) as raw:
                        state = json.loads(raw.execute("SELECT state_json FROM materialized").fetchone()[0])
                        target = state
                        for key in path[:-1]:
                            target = target[key]
                        target[path[-1]] = value
                        raw.execute("UPDATE materialized SET state_json=?", (json.dumps(state),))
                    self.assert_corruption_blocks_commands_and_reopen(ledger, database)

    def test_receipt_and_recorded_request_scalar_types_are_strict(self):
        cases = [("receipt_json", "ok", 1), ("receipt_json", "revision", 1.0),
                 ("request_json", "expected_revision", 0.0), ("request_json", "expected_revision", False)]
        for index, (column, field, value) in enumerate(cases):
            with self.subTest(column=column, field=field, value=value):
                database = self.root / f"receipt-types-{index}" / "ledger.sqlite3"
                with self.Ledger(database, self.workspace, self.requirements) as ledger:
                    ledger.command({"command_id": "original", "expected_revision": 0,
                                    "kind": "checkpoint.create", "payload": {"note": "original"}})
                    with sqlite3.connect(database) as raw:
                        record = json.loads(raw.execute(f"SELECT {column} FROM receipts").fetchone()[0])
                        record[field] = value
                        raw.execute(f"UPDATE receipts SET {column}=?", (json.dumps(record),))
                    self.assert_corruption_blocks_commands_and_reopen(ledger, database)

    def test_checkpoint_scalar_type_corruption_is_never_equal(self):
        for index, value in enumerate((5.0, True)):
            with self.subTest(value=value):
                database = self.root / f"checkpoint-types-{index}" / "ledger.sqlite3"
                with self.Ledger(database, self.workspace, self.requirements) as ledger:
                    if value is True:
                        submission = ledger.command({"command_id": "priority", "expected_revision": 0, "kind": "guidance.submit",
                            "payload": {"target": "R-1", "text": "set one", "action": {"kind": "set_priority", "target": "R-1", "priority": 1}}})
                        ledger.command({"command_id": "ack", "expected_revision": 1, "kind": "guidance.ack",
                            "payload": {"guidance_id": submission["result"]["guidance_id"], "disposition": "ACKNOWLEDGED", "reason": "set"}})
                        ledger.command({"command_id": "apply", "expected_revision": 2, "kind": "guidance.apply", "payload": {"guidance_id": "priority"}})
                    ledger.command({"command_id": "checkpoint", "expected_revision": ledger.state()["revision"],
                                    "kind": "checkpoint.create", "payload": {"note": "snapshot"}})
                    with sqlite3.connect(database) as raw:
                        state = json.loads(raw.execute("SELECT state_json FROM checkpoints").fetchone()[0])
                        state["requirements"]["R-1"]["priority"] = value
                        raw.execute("UPDATE checkpoints SET state_json=?", (json.dumps(state),))
                    self.assert_corruption_blocks_commands_and_reopen(ledger, database)

    def test_genesis_scalar_type_corruption_is_rejected(self):
        for index, value in enumerate((5.0, True)):
            with self.subTest(value=value):
                database = self.root / f"genesis-types-{index}" / "ledger.sqlite3"
                with self.Ledger(database, self.workspace, self.requirements) as ledger:
                    with sqlite3.connect(database) as raw:
                        genesis = json.loads(raw.execute("SELECT document_json FROM genesis").fetchone()[0])
                        genesis["state"]["requirements"]["R-1"]["priority"] = value
                        raw.execute("UPDATE genesis SET document_json=?", (json.dumps(genesis),))
                    self.assert_corruption_blocks_commands_and_reopen(ledger, database)

    def source_context_files(self, version="one"):
        directory = self.workspace / "registry"
        directory.mkdir(exist_ok=True)
        requirements = json.loads(json.dumps(self.requirements))
        requirements[0]["mandate"] = "Keep the complete obligation"
        requirements[0]["acceptance"] = "Preserve actual captured bytes"
        requirements[0]["scope"] = "bootstrap-only"
        requirements[0]["authority"] = {"owner": "test-owner", "version": version}
        requirements[0]["source_refs"] = ["SRC-TEST"]
        requirements[0]["continuity"] = ["K-SRC", "K-STATE"]
        records = {
            "constitution.json": {"schema_version": 1, "edition": version, "requirements": requirements},
            "sources.json": {"schema_version": 1, "version": version, "files": [{"path": "external-corpus.txt", "sha256": "a" * 64}]},
            "authority.json": {"schema_version": 1, "policy_revision": version, "owner": "test-owner"},
        }
        for name, record in records.items():
            (directory / name).write_text(json.dumps(record))
        return requirements, {"registry/" + name: (directory / name).read_bytes() for name in records}

    def test_requirement_scope_authority_and_acceptance_metadata_survive_restart(self):
        requirements, _ = self.source_context_files()
        database = self.root / "metadata" / "ledger.sqlite3"
        with self.Ledger(database, self.workspace, requirements) as ledger:
            requirement = ledger.state()["requirements"]["R-1"]
            for field in ("mandate", "acceptance", "scope", "authority", "source_refs", "continuity"):
                self.assertEqual(requirement.get(field), requirements[0][field])
        with self.Ledger(database, self.workspace) as reopened:
            self.assertEqual(reopened.state()["requirements"]["R-1"]["authority"], {"owner": "test-owner", "version": "one"})

    def test_default_genesis_captures_actual_package_control_manifests(self):
        database = self.root / "default-context" / "ledger.sqlite3"
        with self.Ledger(database, self.workspace) as ledger:
            state = ledger.state()
            self.assertIn("source_context", state)
            context = state["source_context"]
            self.assertEqual(context["status"], "SOURCED")
            self.assertEqual(context["registry_origin"], "package")
            self.assertEqual(context["version"], 1)
            self.assertEqual(context["captured_revision"], 0)
            descriptors = {item["role"]: item for item in context["objects"]}
            package_root = Path(__file__).resolve().parent.parent
            for role, path in (("constitution", "registry/constitution.json"), ("source-manifest", "registry/sources.json"), ("authority", "registry/authority.json")):
                self.assertIn(role, descriptors)
                self.assertEqual(ledger.get_blob(descriptors[role]["sha256"]), (package_root / path).read_bytes())
            self.assertTrue(any(item["path"] == "polyia/store.py" for item in context["objects"]))
            self.assertEqual(state["commission_status"], "NOT_COMMISSIONED")

    def test_custom_genesis_without_registries_is_explicitly_unsourced(self):
        state = self.store.state()
        self.assertIn("source_context", state)
        context = state["source_context"]
        self.assertEqual(context["status"], "UNSOURCED")
        self.assertEqual(context["registry_origin"], "workspace")
        missing = {item["role"]: item for item in context["missing"]}
        for role in ("constitution", "source-manifest", "authority"):
            self.assertEqual(missing[role]["status"], "UNAVAILABLE")
        self.assertTrue(self.store.verify()["ok"])

    def test_checkpoint_refreshes_context_and_retains_historical_source_bytes(self):
        requirements, first_bytes = self.source_context_files()
        database = self.root / "source-history" / "ledger.sqlite3"
        with self.Ledger(database, self.workspace, requirements) as ledger:
            first_receipt = ledger.command({"command_id": "first", "expected_revision": 0,
                                            "kind": "checkpoint.create", "payload": {"note": "first sources"}})
            first = ledger.get_checkpoint(first_receipt["result"]["checkpoint_id"])
            self.assertIn("source_context", first["state"])
            initial = first["state"]["source_context"]
            self.assertEqual(initial["version"], 2)
            _, second_bytes = self.source_context_files("two")
            second_receipt = ledger.command({"command_id": "second", "expected_revision": 1,
                                             "kind": "checkpoint.create", "payload": {"note": "new source version"}})
            second = ledger.get_checkpoint(second_receipt["result"]["checkpoint_id"])
            updated = second["state"]["source_context"]
            self.assertEqual(updated["version"], 3)
            self.assertNotEqual(initial["digest"], updated["digest"])
            for context, expected in ((initial, first_bytes), (updated, second_bytes)):
                for item in context["objects"]:
                    if item["path"] in expected:
                        self.assertEqual(ledger.get_blob(item["sha256"]), expected[item["path"]])
            self.assertEqual(second["state"]["requirements"]["R-1"]["authority"]["version"], "one")
            self.assertEqual(updated["definition_binding"]["status"], "DIFFERENT")
            expected_state = ledger.state()
        with patch.object(self.Ledger, "_capture_source_context", side_effect=AssertionError("Replay read live source files")):
            with self.Ledger(database, self.workspace) as reopened:
                self.assertEqual(reopened.state(), expected_state)
                self.assertTrue(reopened.verify()["ok"])
                self.assertEqual(reopened.get_checkpoint(first["id"]), first)

    def test_old_context_blob_corruption_and_removal_are_detected(self):
        for index, remove in enumerate((False, True)):
            with self.subTest(remove=remove):
                requirements, _ = self.source_context_files("one")
                database = self.root / f"context-corruption-{index}" / "ledger.sqlite3"
                with self.Ledger(database, self.workspace, requirements) as ledger:
                    self.assertIn("source_context", ledger.state())
                    old = next(item for item in ledger.state()["source_context"]["objects"] if item["role"] == "source-manifest")
                    self.source_context_files("two")
                    ledger.command({"command_id": "new-context", "expected_revision": 0,
                                    "kind": "checkpoint.create", "payload": {"note": "new context"}})
                    with sqlite3.connect(database) as raw:
                        if remove:
                            raw.execute("DELETE FROM blobs WHERE digest=?", (old["sha256"],))
                        else:
                            raw.execute("UPDATE blobs SET data=? WHERE digest=?", (b"changed historical source manifest", old["sha256"]))
                    self.assert_corruption_blocks_commands_and_reopen(ledger, database)

    def test_definition_metadata_scalar_types_cannot_silently_change(self):
        requirements = json.loads(json.dumps(self.requirements))
        requirements[0]["evidence_required"] = True
        database = self.root / "definition-types" / "ledger.sqlite3"
        with self.Ledger(database, self.workspace, requirements):
            pass
        requirements[0]["evidence_required"] = 1
        with self.assertRaises(self.CommandError) as raised:
            self.Ledger(database, self.workspace, requirements)
        self.assertEqual(raised.exception.code, "CONFIGURATION_CONFLICT")

    def test_unrelated_text_cannot_satisfy_scientific_production(self):
        self.command("requirement.produce", {"requirement_id": "R-2", "artifacts": [self.artifact("irrelevant.txt", b"An unrelated note is not the executed kernel.")]})
        receipt = self.command("requirement.verify", {"requirement_id": "R-2"})
        self.assertEqual(receipt["result"]["verification"]["outcome"], "FAIL")
        self.assertEqual(receipt["result"]["verification"]["report"]["reason"], "PRODUCED_KERNEL_MISMATCH")
        self.assertRefused(self.request("requirement.accept", {"requirement_id": "R-2"}), "INVALID_TRANSITION")

    def test_altered_kernel_copy_cannot_satisfy_scientific_production(self):
        kernel = Path(__file__).resolve().parent.parent / "polyia" / "experiments.py"
        self.artifact("altered-kernel.py", kernel.read_bytes() + b"\n# This is a different captured source identity.\n")
        self.command("requirement.produce", {"requirement_id": "R-2", "artifacts": ["altered-kernel.py"]})
        receipt = self.command("requirement.verify", {"requirement_id": "R-2"})
        self.assertEqual(receipt["result"]["verification"]["outcome"], "FAIL")
        self.assertEqual(self.store.state()["requirements"]["R-2"]["status"], "PRODUCED")

    def test_scientific_inputs_have_exact_kernel_and_linked_run_roles(self):
        run = self.command("experiment.run", {"name": "acceptance", "parameters": {}})["result"]["run"]
        kernel = Path(__file__).resolve().parent.parent / "polyia" / "experiments.py"
        self.artifact("kernel-copy.py", kernel.read_bytes())
        self.artifact("run-receipt.json", json.dumps(run).encode())
        self.artifact("notes.txt", b"Ancillary commentary; never the scientific input.")
        self.command("requirement.produce", {"requirement_id": "R-2", "artifacts": ["kernel-copy.py", "run-receipt.json", "notes.txt"]})
        receipt = self.command("requirement.verify", {"requirement_id": "R-2"})
        verification = receipt["result"]["verification"]
        self.assertEqual(verification["outcome"], "PASS")
        self.assertEqual({item.get("role") for item in verification["inputs"]}, {"executing-kernel", "recorded-run"})
        self.assertEqual(verification["ancillary_attachments"][0]["path"], "notes.txt")
        self.assertEqual(verification["code_identity"]["sha256"], hashlib.sha256(kernel.read_bytes()).hexdigest())
        self.assertEqual(len(verification["code_identity"]["loaded_code_sha256"]), 64)
        self.command("requirement.accept", {"requirement_id": "R-2"})
        self.assertTrue(self.store.verify()["ok"])

    def test_mismatched_or_type_altered_run_receipt_is_not_scientific_evidence(self):
        original = self.command("experiment.run", {"name": "acceptance", "parameters": {}})["result"]["run"]
        kernel = Path(__file__).resolve().parent.parent / "polyia" / "experiments.py"
        self.artifact("kernel-copy.py", kernel.read_bytes())
        for change in ("result", "scalar-type"):
            with self.subTest(change=change):
                run = json.loads(json.dumps(original))
                if change == "result":
                    run["report"]["result"] = {"forged": "PASS"}
                else:
                    run["revision"] = float(run["revision"])
                self.artifact("mismatched-run.json", json.dumps(run).encode())
                self.command("requirement.produce", {"requirement_id": "R-2", "artifacts": ["kernel-copy.py", "mismatched-run.json"]})
                result = self.command("requirement.verify", {"requirement_id": "R-2"})
                self.assertEqual(result["result"]["verification"]["outcome"], "FAIL")
                self.assertEqual(result["result"]["verification"]["report"]["reason"], "UNLINKED_RUN_RECEIPT")
                self.assertRefused(self.request("requirement.accept", {"requirement_id": "R-2"}), "INVALID_TRANSITION")

    def test_changed_scientific_source_requires_restart_before_verification(self):
        isolated = self.root / "isolated-package"
        isolated.mkdir()
        shutil.copytree(Path(__file__).resolve().parent.parent / "polyia", isolated / "polyia", ignore=shutil.ignore_patterns("__pycache__"))
        script = '''import json
from pathlib import Path
from polyia.store import Ledger
root=Path.cwd()
workspace=root/'workspace'
workspace.mkdir()
kernel=root/'polyia'/'experiments.py'
original=kernel.read_bytes()
(workspace/'kernel.py').write_bytes(original)
ledger=Ledger(root/'state'/'ledger.sqlite3',workspace,[{'id':'SCI','title':'science','verifier':'scientific-contracts'}])
ledger.command({'command_id':'produce','expected_revision':0,'kind':'requirement.produce','payload':{'requirement_id':'SCI','artifacts':['kernel.py']}})
ledger.command({'command_id':'pin','expected_revision':1,'kind':'experiment.run','payload':{'name':'acceptance','parameters':{}}})
kernel.write_bytes(original+b'\\n# Source changed while this process was running.\\n')
receipt=ledger.command({'command_id':'verify','expected_revision':2,'kind':'requirement.verify','payload':{'requirement_id':'SCI'}})
print(json.dumps(receipt['result']['verification']))
ledger.close()
'''
        result = subprocess.run([sys.executable, "-c", script], cwd=isolated, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        verification = json.loads(result.stdout)
        self.assertEqual(verification["outcome"], "ERROR")
        self.assertEqual(verification["report"]["reason"], "IMPLEMENTATION_CHANGED")

    def test_cached_kernel_with_different_source_constants_is_refused_before_first_pin(self):
        isolated = self.root / "isolated-cached-package"
        isolated.mkdir()
        shutil.copytree(Path(__file__).resolve().parent.parent / "polyia", isolated / "polyia", ignore=shutil.ignore_patterns("__pycache__"))
        script = '''import json
from pathlib import Path
from polyia import experiments
from polyia.store import Ledger,CommandError
root=Path.cwd()
workspace=root/'workspace'
workspace.mkdir()
kernel=root/'polyia'/'experiments.py'
kernel.write_text(kernel.read_text().replace('MAX_DEGREE = 32','MAX_DEGREE = 31'))
try:
    ledger=Ledger(root/'state'/'ledger.sqlite3',workspace,[{'id':'SCI','title':'science','verifier':'scientific-contracts'}])
except CommandError as error:
    print(json.dumps({'code':error.code}))
else:
    print(json.dumps({'code':'INCORRECTLY_ADMITTED'}))
    ledger.close()
'''
        result = subprocess.run([sys.executable, "-c", script], cwd=isolated, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["code"], "IMPLEMENTATION_CHANGED")

    def test_cached_kernel_with_different_source_defaults_is_refused_before_first_pin(self):
        isolated = self.root / "isolated-default-package"
        isolated.mkdir()
        shutil.copytree(Path(__file__).resolve().parent.parent / "polyia", isolated / "polyia", ignore=shutil.ignore_patterns("__pycache__"))
        script = '''import json
from pathlib import Path
from polyia import experiments
from polyia.store import Ledger,CommandError
root=Path.cwd()
workspace=root/'workspace'
workspace.mkdir()
kernel=root/'polyia'/'experiments.py'
source=kernel.read_text()
changed=source.replace("evidence_class='EXACTLY_CHECKED'", "evidence_class='CHANGED_DEFAULT'")
assert changed != source
kernel.write_text(changed)
try:
    ledger=Ledger(root/'state'/'ledger.sqlite3',workspace,[{'id':'SCI','title':'science','verifier':'scientific-contracts'}])
except CommandError as error:
    print(json.dumps({'code':error.code}))
else:
    print(json.dumps({'code':'INCORRECTLY_ADMITTED'}))
    ledger.close()
'''
        result = subprocess.run([sys.executable, "-c", script], cwd=isolated, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["code"], "IMPLEMENTATION_CHANGED")


if __name__ == "__main__":
    unittest.main()
