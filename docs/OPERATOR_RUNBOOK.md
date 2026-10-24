# Poly IA bootstrap and target-service runbook

## What can run now

The package provides a Python standard-library state service, SQLite event history and captured blobs, guarded commands, real human/machine web interface, command-line operator tools, a finite experiment worker and exact scientific kernels. It needs no pip installation, model weights or LLM inference. The full mission remains `NOT_COMMISSIONED` while Codex extends and verifies the commissioned capabilities.

Use Linux or another supported POSIX environment for artifact capture: the runtime relies on directory descriptors and `O_NOFOLLOW` to reject symlink escapes and races. Unsupported capture platforms produce an explicit refusal. Python 3.11 or later is the language baseline. **Check the linked SQLite version**, not only the Python version. For multi-connection WAL operation use SQLite **3.51.3 or later**, or an explicitly patched backport such as 3.44.6 or 3.50.7. SQLite documents a WAL-reset race in earlier versions. The release environment's exact version is in the evidence report; this is a target preflight requirement, not an instruction to assume an Oracle image is current. [SQLite WAL documentation](https://www.sqlite.org/wal.html#walreset)

```bash
python3 -c 'import sys,sqlite3; print(sys.version); print(sqlite3.sqlite_version)'
python3 tools/verify_package.py
python3 tools/audit_no_llm.py
python3 -m unittest discover -s tests -v
```

HTTP tests create loopback sockets. A sandbox that forbids all sockets cannot run those tests until that local capability is available. Do not report skipped socket tests as passing. JavaScript test commands, when Node 20 or later is available, are:

```bash
node --test web/client.test.mjs
node --test web/ui.test.mjs
```

The UI-handler tests use a test-only DOM and the actual server. They verify behavior, not browser layout, assistive-technology certification or physical-device rendering. Browser testing remains a separate production gate.

## 1. Disposable local demonstration

Run from the package root. Choose a fresh directory outside the sources and never reuse a database from an incompatible schema.

```bash
python3 -m polyia init --state-dir /tmp/polyia-demo-state
python3 -m polyia demo --state-dir /tmp/polyia-demo-state
python3 -m polyia status --state-dir /tmp/polyia-demo-state
python3 -m polyia verify --state-dir /tmp/polyia-demo-state
```

`demo` creates real demonstration evidence files in the permitted workspace, captures them, executes scientific verification, records actual priority guidance and creates a checkpoint. It does not claim completion of the 192 mission obligations. The two BOOT requirements are explicitly narrower. The full default registry contains 194 entries: 192 mission obligations plus two bootstrap checks.

Captured production bytes are immutable. A later live edit is reported as workspace drift, and new production must be explicit. The scientific verifier must bind captured kernel bytes to the actual installed implementation it executes; unrelated attachments cannot satisfy that relationship. Source/constitution/authority context is captured at initialization/checkpoints, with explicit incomplete context for custom test workspaces that lack those files.

## 2. Start the actual local interface

Create an operator token using a password manager or a cryptographically secure generator. Paste it without echoing it into terminal logs; use a separate token for read-only observers.

```bash
read -rsp 'Paste operator token: ' POLYIA_OPERATOR_TOKEN
export POLYIA_OPERATOR_TOKEN
read -rsp 'Paste optional read-only token: ' POLYIA_READ_TOKEN
export POLYIA_READ_TOKEN
python3 -m polyia serve --state-dir /tmp/polyia-demo-state --host 127.0.0.1 --port 8765
```

Open **http://127.0.0.1:8765/** locally. Enter the same operator token in the interface; it remains in browser JavaScript memory. The token is not embedded in HTML or a URL. Read-token users can inspect but cannot command. Opening the page or polling state does not advance semantic revision.

Public discovery is at `/.well-known/polyia.json`; minimal liveness is `/healthz`. Sensitive endpoints require bearer authentication. The full contract and error behavior are in `docs/HTTP_PROTOCOL.md` and `registry/openapi.json`. Use `web/client.mjs` for a tested conflict-aware client.

The built-in server is a loopback commissioning server. Production TLS, request-rate controls and supervised lifecycle are provided by the target deployment boundary. There is no claim that this package has already installed a public server.

## 3. A command is a guarded transition

Read `/v1/state`, retain its current revision and create a unique command ID. For example:

```json
{
  "command_id": "owner-guidance-001",
  "expected_revision": 0,
  "kind": "guidance.submit",
  "payload": {
    "target": "PIA-061",
    "text": "Prioritize grammar-as-letter expansion and semantic evidence.",
    "action": {"kind": "set_priority", "target": "PIA-061", "priority": 9}
  }
}
```

The `0` is an example; substitute the actual current revision. Use the UI or save a real request as a JSON file and invoke:

```bash
python3 -m polyia command --state-dir /tmp/polyia-demo-state --file command.json --actor owner
```

Acknowledge the guidance with `guidance.ack`, reason and disposition. Then `guidance.apply` can apply its registered action. Text-only guidance can be recorded and acknowledged, but cannot be labeled applied through an unsupported action. An applied pause prevents later experiments; it does not interrupt the middle of an already executing bounded transaction.

An exact retry uses the same actor, command ID and original request, including its original expected revision. The original receipt is returned. A changed request with the same ID is refused. If a new request receives a revision conflict, read current state and decide a new command deliberately; the client never silently rebases a consequential command.

## 4. Inspect and guide during commissioning

Use the workbench to select obligations, capture permitted artifact paths, run registered verifiers, accept verified versions, inspect guidance, execute exact kernels, read event pages and create checkpoints. The default mission verifier is intentionally `commission-evidence`, which remains unsupported until Codex implements the actual acceptance adapters. This prevents a bootstrap artifact hash from satisfying an entire scientific obligation.

The controlling reference files are `registry/constitution.json`, `registry/acceptance.json`, `registry/work_contracts.json`, `registry/authority.json`, `registry/sources.json` and the inherited crosswalks. Codex extends these through versioned changes and real evidence. Source context captured at a checkpoint preserves the prior version even when the live files later change; historical requirements are not silently redefined.

Keep a clear distinction between a database event commit and a Git code commit. The production handoff should bind both identities where Git is available. The bootstrap records exact code/source digests and durable event/checkpoint identity; it does not manufacture a Git revision for an uncommitted directory.

## 5. Oracle installation as the first operational deliverable

Codex first inspects the real VM: operating system, Python/SQLite, available service manager, existing checkout, persistent disk, account, firewall/proxy, intended hostname, existing Ollama/model setup and available credentials. Inspection does not make those models a runtime dependency. Preserve existing services and concurrent work. Use the owner-supplied repository and actual target paths; the examples below are templates.

Stage code under a stable release directory such as `/opt/polyia`, and runtime data under a persistent dedicated directory such as `/var/lib/polyia`. Keep state outside the source tree. Create/use a least-privileged service account with read access to package files and write access to its state directory. Provision secrets through a root-readable service environment file or the target's existing secret store. Never put them in the source package, Git history or evidence bundle.

`deploy/polyia.service` is a reviewable supervisor template. Replace paths/account/interpreter if the actual VM differs. Initialize once under the intended account before enabling the service. Run `systemd-analyze verify` where systemd is present. `deploy/Caddyfile.example` demonstrates the HTTPS-to-loopback boundary; substitute the verified actual hostname and validate with the installed proxy's own command before activation. Set `POLYIA_PUBLIC_ORIGIN` to that same exact HTTPS origin. Preserve incoming Host and Origin, as required by the HTTP contract.

After installation, demonstrate from an independent client:

1. Discovery and authenticated state reads succeed at the actual HTTPS URL; unauthenticated private reads fail.
2. Guidance submission, explicit acknowledgement and actual application produce distinct events.
3. Production, registered verification and acceptance produce actual evidence; unknown verifiers remain unsupported.
4. A source-linked checkpoint resolves its constitution, source/policy identities and captured artifacts.
5. Service restart preserves revision, event head, receipts and checkpoint; an exact retry is not applied twice.
6. An observer can inspect the result without access to the commissioning chat.

Record the actual host, code digest/Git revision, public origin, service status, restart results and checkpoint. These are the first operational-delivery receipt. If hostname or target access is unavailable, state that specific blocker and continue other authorized work; do not claim a placeholder URL is live.

## 6. Bounded worker and continuous experiments

The supplied worker executes only registered finite experiments. It is useful for verifying supervision, pause/resume and durable run capture:

```bash
python3 -m polyia worker --state-dir /tmp/polyia-demo-state --iterations 3 --experiment acceptance
```

`deploy/polyia-research.service` and `deploy/polyia-research.timer` are optional supervisor templates that repeat a bounded seed run. They are not enabled by this package and do not claim autonomous novel discovery. The full commission must replace this narrow demonstration with the queue/lease/read-isolation/budget/admission system defined by PIA-133–156. Routine retries and repeated baseline checks remain labeled as such; a running timer is not a scientific finding.

## 7. Back up, restore and verify

Use SQLite's backup API through `tools/backup_state.py`. Do not copy only the main file while writers are active; WAL may hold committed data not yet in the main file. Keep backups separate from the live host and store the source release and external checkpoint anchors according to the target policy. The backup tool refuses to overwrite an existing destination.

```bash
python3 tools/backup_state.py /var/lib/polyia/ledger.sqlite3 /path/to/backups/polyia-snapshot.sqlite3
```

Restore into a fresh state directory, never over an active writer. With the matching runtime release and appropriate workspace, run `python3 -m polyia verify --state-dir RESTORED_DIRECTORY`. Compare the expected event head and checkpoint to an independently retained prior receipt. An internally consistent rewritten database is not proof against a malicious administrator; independent signed/anchored roots are a separate production requirement.

If integrity fails, stop mutations, preserve the database plus WAL/SHM and logs, diagnose a copy, and restore a known-good backup or create an explicitly authorized recovery lineage. Never delete events or recompute hashes just to make the display green. Schema upgrades require a tested migration; the bootstrap refuses incompatible existing schemas rather than silently changing historical meaning.

## 8. Limits and next implementation work

The portable store favors inspectable commissioning workloads: it verifies the full chain before mutations and retains complete run evidence in state. It is not a production throughput benchmark. PostgreSQL/object-storage migration, efficient event retention/indexing, multiple authenticated identities, signing/independent anchoring, redacted pre-auth access logs, external-effect outbox and general research isolation remain explicit commission work.

All acquired sources and books remain in `sources/`. Native compiler, broad article interpretation, full linguistic/math/chemistry families, Astra adapter, versioned improvements and university laboratories are specified in depth but are not falsely declared implemented by the seed. The accepted finite release and its open frontier must both be visible at the eventual live URL.
