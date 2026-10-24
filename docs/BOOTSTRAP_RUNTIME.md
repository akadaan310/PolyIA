# Durable commissioning runtime

This package implements a bounded, runnable commissioning service. Its successful demonstrations establish the declared bootstrap contracts. They do not complete the 192 constitutional obligations or the full Poly IA research system. `commission_status` remains `NOT_COMMISSIONED` in this runtime, including after both bootstrap requirements are accepted.

The executable implementation is in `polyia/store.py`, `polyia/cli.py`, and `polyia/server.py`; exact demonstrations are registered in `polyia/experiments.py`. Runtime version **1.1.0** uses ledger schema **2**. The commission document's edition is separate. Pre-remediation schema-1 databases are refused rather than silently migrated; preserve them for diagnosis and initialize a fresh schema-2 ledger for the release. Tests use actual SQLite databases, files, separate processes, and authenticated HTTP requests. `evidence/runtime-development.json` retains historical development results and the post-review verification checkpoint. The approved contract is `docs/APPROVED_DESIGN.md`; the independent pre-remediation findings remain in `docs/INDEPENDENT_RUNTIME_REVIEW.md`.

## 1. Start and inspect

Run from the extracted package root with Python 3.11 or newer. No third-party package installation is required. The tested environment is Linux; secure artifact capture requires POSIX directory-descriptor operations and `O_NOFOLLOW`. Capture explicitly refuses unsupported platforms instead of silently using an unsafe path-opening fallback. PostgreSQL, multi-host replication, and Windows parity have not been implemented by this bootstrap.

```bash
python -m polyia init --state-dir .polyia-state
python -m polyia status --state-dir .polyia-state
python -m polyia verify --state-dir .polyia-state
python -m polyia demo --state-dir .polyia-state
python -m polyia worker --state-dir .polyia-state --iterations 3
```

Every subcommand accepts `--workspace PATH`; it defaults to the current directory. Artifact paths are relative to that workspace. Keep runtime state in a separate directory. The default is `.polyia-state/ledger.sqlite3`, ignored by Git. `init` loads `registry/constitution.json`, or an explicitly supplied `--requirements FILE` containing a list or an object with a `requirements` list. Requirement definitions are captured in genesis. Reopening with conflicting definitions is refused. A later edit of the registry does not silently rewrite an existing ledger's constitution.

Read commands do not silently initialize an absent database. `init` is required before `status`, `verify`, `command`, `worker`, or `serve`. `demo` may initialize a new ledger using the packaged constitution. The demo requires `BOOT-001` with `artifact-integrity` and `BOOT-002` with `scientific-contracts`. It creates a uniquely named `bootstrap-demo-*` directory containing actual demonstration artifacts in the permitted workspace.

`demo` executes eleven guarded commands: produce, verify and accept the byte-integrity artifact; submit, acknowledge and apply a priority action; run exact acceptance; produce the exact kernel source together with its committed run record, verify and accept that linked evidence; and create a checkpoint. It copies the kernel into the demonstration directory, so a workspace separate from the installed code can still supply the exact bytes. Each command is individually atomic. If a later step fails, prior committed steps and the generated files remain available for diagnosis; the whole demo is not represented as one atomic command.

`worker --iterations N` executes a finite number of registered experiments, with a maximum of 100. Its default experiment is `acceptance`; `--experiment polynomial`, `grammar-promotion`, and `qpath` are also registered. `completed` counts recorded invocations, while each run's `report.status` gives its scientific outcome. Zero iterations produces zero runs. Applied pause guidance stops the worker before the next invocation. This is a bounded demonstration runner; it does not discover or execute arbitrary research code.

## 2. Serve the command plane

Supply a fresh operator bearer token through the environment, using the deployment environment or an interactive shell variable. It is never embedded in the URL or static UI.

```bash
python -m polyia serve --state-dir .polyia-state --host 127.0.0.1 --port 8765
```

The process requires `POLYIA_OPERATOR_TOKEN`. Optional `POLYIA_READ_TOKEN` supplies a distinct read-only credential. The UI asks the operator to enter the token and keeps it in JavaScript memory. For an explicitly configured reverse proxy, use `--public-origin https://polyia.example` or `POLYIA_PUBLIC_ORIGIN`; the server validates one exact HTTPS origin and still binds only to loopback. Preserve the original Host and Origin through the proxy. The deployment documentation covers the actual TLS boundary; running this command does not deploy TLS or expose a remote service.

The server uses the same `Ledger.command` interface as the CLI. SIGINT and SIGTERM perform orderly server shutdown. SQLite durability does not depend on graceful shutdown after a command has committed; an automated subprocess test exits immediately after commit and recovers the exact receipt in another process.

## 3. Commands and receipts

A command has exactly four fields:

```json
{
  "command_id": "priority-2026-10-24-001",
  "expected_revision": 0,
  "kind": "guidance.submit",
  "payload": {
    "target": "BOOT-001",
    "text": "Prioritize the captured-byte bootstrap check.",
    "action": {"kind": "set_priority", "target": "BOOT-001", "priority": 7}
  }
}
```

Save a complete request to a JSON file and run `python -m polyia command --state-dir .polyia-state --file request.json`. The local CLI actor defaults to `local-operator` and can be set with `--actor`. HTTP operator commands use the server's fixed operator identity. Changing actor changes the idempotency namespace; clients must retain their stable identity when retrying.

`expected_revision` must equal the current revision for a new command. Booleans are not accepted as integers. Commands commit under SQLite `BEGIN IMMEDIATE`, so two writers that submit the same expected revision cannot both advance it. A stale request receives `REVISION_CONFLICT` with the current revision and makes no accepted-state change.

`command_id` is a stable ASCII identifier of at most 128 characters. Within one actor, an exact retry of the entire request returns the original receipt, even after the revision has advanced or the process has restarted. Reusing the ID with any changed content, including a changed expected revision, returns `IDEMPOTENCY_CONFLICT`. This deduplication covers committed ledger transitions; it is not a promise of exactly-once delivery to arbitrary external systems.

An applied receipt contains `ok`, `command_id`, `actor`, `revision`, `head`, and `result`. `ok: true` means the command and its recorded result were committed. Scientific success is stated separately in `result.verification.outcome` or `result.run.report.status`. A committed run with `REFUSED`, `FAIL`, or `ERROR` is retained evidence of that outcome and is never converted into a passing result.

Refused commands raise `CommandError`, whose `code`, `message`, `http_status`, and optional `details` are exposed as safe structured errors. The CLI writes error JSON to stderr and exits with code 2. Successful commands write JSON to stdout. A valid `verify` report returns exit 0; integrity failures detected during opening fail before an ordinary state report is emitted.

## 4. Guidance has an executable meaning

| Command | Required behavior |
| --- | --- |
| `guidance.submit` | Retain the text, target, optional registered action, submitter, time and revision as `SUBMITTED`. |
| `guidance.ack` | Record a reason, actor and revision with `ACKNOWLEDGED`, `DEFERRED` or `REJECTED`. Applied and rejected guidance is closed. |
| `guidance.apply` | Require acknowledged guidance, execute its registered action, and record the exact applied revision and before/after effects. |

The public guidance ID equals the submission's command ID. Because this object ID is global within a ledger while command receipts are actor scoped, a second actor trying to create guidance with an already used guidance ID receives an explicit `GUIDANCE_ID_CONFLICT`; the earlier guidance is never overwritten.

The three registered actions are `set_priority` with a known requirement and integer priority 0–9, `pause_research`, and `resume_research`. A priority action must affect its guidance target; pause/resume require target `research`. Free text is retained without interpretation. Text-only guidance cannot be labelled `APPLIED`. Unsupported actions, malformed dispositions, unacknowledged application and stale acknowledgments all fail explicitly. Reads never apply pending guidance.

## 5. Produced artifacts are captured snapshots

`requirement.produce` receives a requirement ID and 1–32 relative file paths, with an optional note. It reads actual regular files, computes SHA-256, and stores their complete bytes in SQLite's content-addressed `blobs` table. A descriptor contains relative `path`, `sha256`, and byte `size`. Duplicate byte content is stored once. Empty lists, empty files, duplicate paths, directories, unsafe paths and unavailable files are refused.

Capture rejects absolute and parent-traversal paths, hidden files/directories, secret-like names, database names and the configured runtime directory. Secret-like patterns include credential, password, token, secret, API-key and private-key names and key-container suffixes. This filename policy does not inspect arbitrary document content for every possible secret: the local operator remains responsible for selecting appropriate evidence.

Capture walks directory descriptors without following symlinks and checks the opened file's identity, size and modification metadata before and after reading. This prevents a symlink replacement from redirecting an authorized path outside the workspace. Each file is limited to 8 MiB, with a 32 MiB total capture budget. If any file fails, the transaction rolls back all blobs and state changes from that command. No orphan successful-looking capture is left behind.

Verification and acceptance refer to the captured bytes. Editing or deleting the live source afterward does not alter the historical snapshot. `verify()` separately reports `workspace_drift`, including `UNCHANGED`, `MODIFIED`, `MISSING`, or `UNAVAILABLE` for currently referenced artifacts. A valid snapshot can therefore have `ok: true` while its live workspace has drifted. The report states this distinction explicitly.

Re-produce a requirement to capture new bytes. Reproduction resets its current verification and acceptance, while older events, attempts and captured blobs remain auditable. The verifier checks historical blobs as well as currently referenced ones, so corrupting an obsolete snapshot is still detected.

## 6. Verification and acceptance remain distinct

`requirement.verify` accepts only a requirement ID. Callers cannot submit an outcome, a verifier program, a code path or arbitrary success evidence. The requirement's genesis definition selects its registered verifier.

| Verifier | Passing evidence establishes | It does not establish |
| --- | --- | --- |
| `artifact-integrity` | The captured, nonempty artifacts exist and match their digests. Evidence class: `ARTIFACT_INTEGRITY`. | Scientific truth, artifact sufficiency for another requirement, or full commission completion. |
| `scientific-contracts` | The produced evidence includes the exact pinned kernel bytes. The corresponding loaded `acceptance` runner returns `PASS` with nonempty, explicitly passing checks for the seed families. Optional attached run evidence exactly matches a committed run and its fresh reproduction. | Verification of an unrelated text file, authority from an uploaded PASS field, arbitrary theorem validation, universal solving, or completion of other scientific obligations. |
| Any unsupported name, including pending `commission-evidence` | An explicit `UNSUPPORTED` outcome is retained. | A passing result or authority to accept that requirement. |

A verification receipt binds the verifier name, module source digest, package/Python version, captured artifact descriptors, actual checked inputs, revision, evidence class, outcome and report. For scientific verification, `captured_artifacts` retains the complete snapshot, `inputs` names `executing-kernel` and optional `recorded-run` roles, and `ancillary_attachments` explicitly identifies material that did not establish scientific correctness. Failed verification stays `PRODUCED`; all attempts remain in `verification_attempts`. Runtime exceptions at the registered verifier boundary become retained `ERROR` evidence. Base exceptions such as process termination do not manufacture a result; SQLite either commits the completed transaction or rolls it back.

The scientific production contract requires an artifact whose digest equals the pinned `polyia/experiments.py` implementation. An exact copy at any safe workspace path is sufficient; an altered copy or unrelated note is not. The verifier never executes an uploaded Python file. If a JSON attachment purports to be a run or scientific report, it must exactly match a passing committed `acceptance` run, or the full committed command receipt containing that run, with the same implementation and parameters. Comparison is type preserving. A forged result, changed scalar type, unmatched run ID or report from another implementation yields `UNLINKED_RUN_RECEIPT`. A linked report must also agree with the fresh exact acceptance result.

The runtime pins source bytes to the code actually loaded in the process. On first pin, it compiles the fixed installed module solely to compare its function-code structures, positional/keyword defaults, and literal constants with the already-loaded registered implementation. Function defaults must have an explicitly supported literal representation. The compiled comparison object is never executed or installed. The receipt includes both the source SHA-256 and a loaded-code SHA-256. Before and after execution, source bytes and loaded functions/defaults/constants must still match that pin. Editing the installed source during a running process yields `IMPLEMENTATION_CHANGED`; restart with a coherent package before producing new scientific evidence. This also detects a module imported before its source constants or defaults changed, rather than assuming that hashing a current file identifies cached Python code.

`requirement.accept` requires the current status `VERIFIED`, a passing receipt whose `captured_artifacts` equal the current snapshot, and intact captured bytes. Scientific acceptance additionally requires the current pinned implementation identity to equal the verification identity. A prior failed verification, unsupported verifier, caller-forged result, changed implementation, or reproduction without another passing verification cannot satisfy acceptance. Accepting a bootstrap requirement never changes the ledger's full commission status.

## 7. Durable events, checkpoints and recovery

Initialization creates the schema, genesis, source-context byte objects and initial state in one transaction. Genesis preserves complete requirement metadata, including mandate, acceptance, scope, authority, source references and continuity keys, as well as the initial reducer state and source context. Its digest is the initial `head`; revision starts at 0. Committed commands become events numbered 1, 2, 3, and so forth. The state envelope's revision and head sit outside the reducer-state hash.

Every event stores its sequence, unique event ID, previous hash, event hash, kind, actor, UTC timestamp, full request and recorded result, and before/after reducer-state digests. Canonical JSON uses sorted keys and refuses nonfinite numbers. The pure reducer does no file IO, model inference, networking, subprocess execution or experiment execution. It reconstructs state from committed records. Reproducing an experiment by executing its kernel is a separate new run, not replay.

SQLite WAL mode with `synchronous=FULL` provides the portable transaction boundary used here. A command commits the event, captured blobs, materialized state, receipt and optional checkpoint together. An abrupt process exit after that commit but before response delivery is resolved by retrying the same actor and exact command ID/request. Disk, filesystem and hardware durability still depend on the host honoring SQLite's documented synchronization assumptions.

Deployment must satisfy the release runbook's patched-SQLite WAL preflight. Merely recording a SQLite version in an execution receipt is not a deployment compatibility approval.

`checkpoint.create` stores the complete resulting reducer state, source event revision and head, state digest and previous checkpoint ID, and refreshes `state.source_context`. The context has its own version, digest, capture revision and timestamp. It captures the actual bytes of `registry/constitution.json`, `registry/sources.json`, and `registry/authority.json`, optional repository pins and inherited-obligation mapping, and the bootstrap runtime sources. Each context file is limited to 2 MiB and the combined context to 8 MiB. Byte objects are deduplicated by digest. The scientific source descriptor is linked to the recorded executing-code identity.

Default initialization takes controlling registries from the installed package. Explicitly supplied custom requirement definitions take optional registry context from the selected workspace. That choice is stored in genesis and does not switch on reopening. The context names every expected object and every unavailable object with a role, origin, path, required flag and reason. `SOURCED` means all required context objects were captured; `INCOMPLETE` means some required objects are unavailable; `UNSOURCED` means none of the three controlling registries is present. Missing optional files remain explicitly named even when required context is complete. A valid but unsourced test ledger does not claim a fully source-linked commission snapshot.

The captured source manifest identifies the immutable external package files. Their corpus bodies are not copied into the database; the context explicitly records `corpus_bytes_copied: 0` and the manifest-only verification scope. Full package-file custody checks remain a separate release gate. A new checkpoint captures a changed live manifest, policy or constitution as a new context version. Earlier contexts and source bytes remain retrievable through `get_checkpoint(id)` and the local `get_blob(sha256)` API. `definition_binding` states `MATCH`, `DIFFERENT`, or `UNAVAILABLE` between the observed constitution and the genesis definitions. Capturing a new constitution file does not silently install different obligations into an existing ledger.

Checkpoints are append-only through the application; historical context blobs are retained. The latest pointer is available in `state().latest_checkpoint`. Context replay uses only stored descriptors and byte objects; it does not consult live registry files or re-execute science. Checkpoints do not bypass verification or automatically authorize rollback.

`verify()` checks required table presence, SQLite consistency, genesis, the entire event chain, contiguous sequences, request/event agreement, deterministic state reduction, command receipts, current materialization, every source-context version, every referenced historical blob and every stored checkpoint. JSON identity comparisons use canonical serialization and distinguish booleans, integers and floats. The verifier recomputes the hashes of the actual decoded materialized and checkpoint state, as well as comparing them with replay; a stored `5.0` cannot pass as the expected integer `5`, and a receipt's integer `1` cannot pass as boolean `true`. Opening an existing ledger performs those checks before allowing work, and each new command rechecks the ledger inside its serialized transaction. A missing table, corrupt event, malformed genesis, altered receipt, changed artifact/context blob or inconsistent checkpoint is reported as an integrity error. The program does not silently recreate missing tables or repair corrupted state.

On corruption, preserve the database and its WAL/SHM files and diagnose a copy. Restore a separately verified backup if necessary. There is deliberately no automatic repair, history rewriting, branch/merge or distributed failover in this bootstrap. For a consistent live backup use SQLite's backup API; alternatively stop all writers cleanly before copying the database. Copying a live main database file alone may omit committed WAL content.

## 8. Refusals, authority and limits

Command refusals are appended to a separate `refusals` table after the rejected transition has rolled back. Entries include time, actor, command ID/kind when available, request digest, error code, message and structured details. They do not increment revision, create a successful command receipt, or masquerade as applied transitions. Raw command text is not copied into this diagnostic journal. The refusal journal is not part of the accepted-state hash chain and is not itself tamper-evident. If the storage device cannot persist an audit entry, it cannot offer a durable refusal audit.

The ledger's hashes establish internal consistency with retained bytes. They are not signatures, independently witnessed timestamps or external truth certificates. A privileged administrator able to replace the database and recompute every digest can construct a different self-consistent history. External anchoring, signatures, separate trust domains, production key management and authorization beyond the declared operator/read boundary belong to later commission work.

The bootstrap restricts request JSON to 64 KiB, artifacts to the stated byte budgets, parameter depth to 12 and parameter item count to 2048. Registered scientific kernels apply their own exact-domain and computation budgets. Experiment reports are limited to 4 MiB. The complete event chain is verified before each new command, and all run evidence remains in state; this favors small, inspectable commissioning workloads over high-throughput production operation. Retention, compaction, independent verification workers and PostgreSQL migration require separate measured designs.

No runtime command permits networking, arbitrary subprocesses, `eval`, code supplied by a caller, dynamic research plugin loading or LLM execution. The local CLI and deployment environment remain trusted operator surfaces. Installing changed Python source is outside the command API and must follow the later code-governance contract.

## 9. Evidence and tests

Run the full suite from the package root:

```bash
python -m unittest discover -s tests -v
```

The store and CLI tests cover durable new-instance recovery; actor-scoped retry/conflicting reuse; concurrent revision races; command scope refusal; malformed/forged inputs; actual guidance effects; text-only non-application; immutable capture; rollback of partial capture; empty, unsafe and secret-like files; unsupported and faulted verifiers; retained refused scientific runs; replay without experiment execution; altered genesis, events, receipts, materialization, blobs and checkpoints; strict boolean/integer/float distinctions; complete requirement metadata; changed and missing source context; historical source-byte retrieval and corruption; exact kernel/run binding; cached implementation drift; deleted tables without silent repair; live-source drift; initialization rollback; finite workers; and an actual process exit after commit with no receipt delivery. HTTP tests require permission to bind a loopback socket. An environment that prohibits all sockets cannot exercise those tests until that local capability is permitted; tests are not replaced by mocked network success.

These tests are scoped evidence for this implementation. They are not evidence of remote deployment, production load, machine compromise resistance, a running PostgreSQL cluster, or full scientific commission completion.

## 10. Response to the independent review

The pre-remediation observations in `docs/INDEPENDENT_RUNTIME_REVIEW.md` are retained. The following describes implementation changes; the coordinator's scoped re-review and final release evidence remain separate gates.

| Finding | Implementation response | Focused regression evidence |
| --- | --- | --- |
| IRR-01 | Canonical type-preserving comparisons and hashes of the actual stored JSON replace loose decoded-dictionary equality. | Float/integer and boolean/integer mutations of materialization, receipts, requests, genesis and checkpoints; refused next command and rejected reopen. |
| IRR-02 | Coordinator-owned exact-number admission now checks the small integer/ratio grammar and integer bit budget before numeric construction. | The integrated science suite includes constructor-sentinel and large-integer preflight tests. |
| IRR-03 | Full obligation metadata and versioned source context are captured in genesis and checkpoints; retained byte objects resolve independently of live source files. | Default package context, explicit unsourced custom contexts, changed manifest/constitution/policy, historical retrieval, and removed/corrupt old context objects. |
| IRR-04 | Scientific verification requires exact pinned kernel bytes; optional run evidence is linked strictly to committed execution and fresh checks. Cached-code/source mismatch is refused. | Unrelated text, altered kernel copies, forged/type-altered reports, valid evidence roles, source edits during a process, and pre-pin cached constant/default mismatch. |
