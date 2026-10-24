"""Local operator commands for the portable Poly IA bootstrap."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import sys
import threading
import uuid

from .store import CommandError, Ledger, MAX_REQUEST_BYTES, REGISTERED_EXPERIMENTS


def _output(value, stream=None):
    print(json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False), file=stream or sys.stdout, flush=True)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def _read_json(path, *, maximum=MAX_REQUEST_BYTES):
    with Path(path).open("rb") as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise CommandError("REQUEST_TOO_LARGE", "JSON input exceeds its byte budget", 413)
    return json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Non-finite JSON number: {value}")))


def _parser():
    parser = argparse.ArgumentParser(prog="python -m polyia", description="Poly IA durable commissioning bootstrap")
    commands = parser.add_subparsers(dest="operation", required=True)
    for name in ("init", "status", "verify", "command", "serve", "demo", "worker"):
        command = commands.add_parser(name)
        command.add_argument("--state-dir", type=Path, default=Path(".polyia-state"), help="Durable SQLite directory")
        command.add_argument("--workspace", type=Path, default=Path.cwd(), help="Permitted artifact workspace")
        if name == "init":
            command.add_argument("--requirements", type=Path, help="Explicit requirement definitions JSON; defaults to packaged constitution")
        elif name == "command":
            command.add_argument("--file", type=Path, required=True, help="A complete guarded command JSON object")
            command.add_argument("--actor", default="local-operator", help="Stable local actor name for idempotency")
        elif name == "serve":
            command.add_argument("--host", default="127.0.0.1")
            command.add_argument("--port", type=int, default=8765)
            command.add_argument("--public-origin", default=os.environ.get("POLYIA_PUBLIC_ORIGIN"),
                                 help="One exact HTTPS origin for a configured reverse proxy")
        elif name == "worker":
            command.add_argument("--iterations", type=int, required=True, help="Bounded number of registered experiment invocations (0..100)")
            command.add_argument("--experiment", choices=sorted(REGISTERED_EXPERIMENTS), default="acceptance")
    return parser


def _local_command(ledger, kind, payload, *, actor="local-worker", command_id=None):
    return ledger.command({"command_id": command_id or str(uuid.uuid4()),
                           "expected_revision": ledger.state()["revision"], "kind": kind, "payload": payload}, actor=actor)


def _worker(ledger, iterations, experiment):
    if not 0 <= iterations <= 100:
        raise CommandError("RESOURCE_LIMIT", "Worker iterations must be between 0 and 100")
    runs = []
    for _ in range(iterations):
        if ledger.state()["research"]["paused"]:
            return {"status": "PAUSED", "requested": iterations, "completed": len(runs), "runs": runs}
        receipt = _local_command(ledger, "experiment.run", {"name": experiment, "parameters": {}})
        runs.append(receipt)
    return {"status": "COMPLETE", "requested": iterations, "completed": len(runs), "runs": runs,
            "scope": "Bounded registered bootstrap experiments; not unrestricted autonomous research"}


def _demo(ledger):
    state = ledger.state()
    required = {"BOOT-001": "artifact-integrity", "BOOT-002": "scientific-contracts"}
    if any(state["requirements"].get(identifier, {}).get("verifier") != verifier for identifier, verifier in required.items()):
        raise CommandError("DEMO_REQUIREMENTS_MISSING", "The demonstration needs BOOT-001 artifact-integrity and BOOT-002 scientific-contracts", 409)
    if state["research"]["paused"]:
        raise CommandError("RESEARCH_PAUSED", "Resume research through acknowledged guidance before running the demonstration", 409)
    directory = ledger.workspace / f"bootstrap-demo-{uuid.uuid4().hex}"
    directory.mkdir(mode=0o700)
    receipt_path = directory / "captured-evidence.txt"
    receipt_path.write_text("Poly IA bootstrap captured-byte demonstration. This is not full commission acceptance.\n", encoding="utf-8")
    receipts = []

    def apply(kind, payload):
        receipt = _local_command(ledger, kind, payload, actor="local-demo")
        receipts.append(receipt)
        return receipt

    apply("requirement.produce", {"requirement_id": "BOOT-001", "artifacts": [receipt_path.relative_to(ledger.workspace).as_posix()],
                                  "note": "Capture actual bytes for the bootstrap integrity workflow"})
    apply("requirement.verify", {"requirement_id": "BOOT-001"})
    apply("requirement.accept", {"requirement_id": "BOOT-001"})
    guidance = apply("guidance.submit", {"target": "BOOT-001", "text": "Demonstrate an acknowledged priority change",
                                         "action": {"kind": "set_priority", "target": "BOOT-001", "priority": 7}})
    guidance_id = guidance["result"]["guidance_id"]
    apply("guidance.ack", {"guidance_id": guidance_id, "disposition": "ACKNOWLEDGED", "reason": "Execute this registered bootstrap demonstration action"})
    apply("guidance.apply", {"guidance_id": guidance_id})
    scientific = apply("experiment.run", {"name": "acceptance", "parameters": {}})
    if scientific["result"]["run"]["report"]["status"] != "PASS":
        raise CommandError("DEMO_FAILED", "Scientific acceptance did not pass; the run and earlier commands remain recorded", 409,
                           {"run_id": scientific["command_id"], "report": scientific["result"]["run"]["report"]})
    science_path = directory / "scientific-contracts.json"
    science_path.write_text(json.dumps(scientific["result"]["run"], sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    kernel_path = directory / "experiments.py"
    kernel_path.write_bytes(Path(__file__).resolve().with_name("experiments.py").read_bytes())
    apply("requirement.produce", {"requirement_id": "BOOT-002",
                                  "artifacts": [kernel_path.relative_to(ledger.workspace).as_posix(), science_path.relative_to(ledger.workspace).as_posix()],
                                  "note": "Captured exact running kernel bytes and a linked committed acceptance run; verification executes independently"})
    apply("requirement.verify", {"requirement_id": "BOOT-002"})
    apply("requirement.accept", {"requirement_id": "BOOT-002"})
    apply("checkpoint.create", {"note": "Integrated bootstrap produce/verify/accept and guidance demonstration"})
    verification = ledger.verify()
    return {"ok": verification["ok"], "scope": "Bootstrap contracts only; full Poly IA commission remains NOT_COMMISSIONED",
            "receipts": receipts, "state": ledger.state(), "verification": verification,
            "artifact_directory": directory.relative_to(ledger.workspace).as_posix()}


def _serve(ledger, args):
    token = os.environ.get("POLYIA_OPERATOR_TOKEN")
    if not token:
        raise CommandError("MISSING_OPERATOR_TOKEN", "Set POLYIA_OPERATOR_TOKEN in the environment before serving")
    from .server import make_server
    server = make_server(ledger, host=args.host, port=args.port, token=token,
                         read_token=os.environ.get("POLYIA_READ_TOKEN"), public_origin=args.public_origin)
    previous = {}

    def stop(_signum, _frame):
        # BaseServer.shutdown must be invoked from a different thread than
        # serve_forever; otherwise shutdown deadlocks in the signal handler.
        threading.Thread(target=server.shutdown, daemon=True).start()

    for name in ("SIGINT", "SIGTERM"):
        number = getattr(signal, name, None)
        if number is not None:
            previous[number] = signal.signal(number, stop)
    host, port = server.server_address[:2]
    _output({"status": "LISTENING", "url": f"http://{host}:{port}", "authentication": "bearer token required for data routes"})
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()
        for number, handler in previous.items():
            signal.signal(number, handler)


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        database = args.state_dir.expanduser().resolve() / "ledger.sqlite3"
        if args.operation not in {"init", "demo"} and not database.is_file():
            raise CommandError("NOT_INITIALIZED", "Run python -m polyia init with this state directory first", 409)
        definitions = None
        if args.operation == "init" and args.requirements:
            definitions = _read_json(args.requirements, maximum=2 * 1024 * 1024)
            if isinstance(definitions, dict):
                definitions = definitions.get("requirements", definitions.get("obligations"))
        with Ledger(database, args.workspace, definitions) as ledger:
            if args.operation == "init":
                _output({"ok": True, "state": ledger.state(), "verification": ledger.verify()})
            elif args.operation == "status":
                _output(ledger.state())
            elif args.operation == "verify":
                result = ledger.verify()
                _output(result)
                return 0 if result["ok"] else 1
            elif args.operation == "command":
                _output(ledger.command(_read_json(args.file), actor=args.actor))
            elif args.operation == "worker":
                _output(_worker(ledger, args.iterations, args.experiment))
            elif args.operation == "serve":
                _serve(ledger, args)
            elif args.operation == "demo":
                _output(_demo(ledger))
        return 0
    except CommandError as error:
        _output({"ok": False, "error": error.as_dict()}, sys.stderr)
        return 2
    except (OSError, ValueError, UnicodeError) as error:
        _output({"ok": False, "error": {"code": "INVALID_INPUT", "message": str(error)}}, sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

