# Poly IA integrated commissioning package — approved design

Date: 2026-10-24. Owner: Abed Kadan. Design collaborator: 7u.

## Authority and requested delivery

The owner approved Option A in the current conversation and explicitly included Option B's formal vocabulary, division charters and scientific obligations, and Option C's working state/verification/guidance interface. This task creates the complete source-bearing commissioning package and a verified runnable bootstrap; it does not claim the later complete Poly IA system is already commissioned. The owner supplied https://github.com/akadaan310/PolyIA as the destination repository; it was empty at inspection on 2026-10-24. This package is prepared for that repository. Existing upstream repositories remain read-only source inputs.

## Immutable intent

- Preserve every supplied source and all inherited obligations. Complete coverage is independently measured against pinned source inventories. Original bytes are never silently corrected.
- Current owner decision: Division Infinity is IX; VII and VIII are open research charters. Their provisional themes are constructive synthesis and evidence-governed evolution. Shared infrastructure remains university-wide.
- Public name: Poly IA, Polymorphic Intelligence Agency / Poly Intelligence Agency. PURL means Programmable URL.
- Existing University subjects/books are canonical inputs, never omitted because of historical preview/sample labels. Source authority, claim kind, measured support, and runtime capability are separate fields.
- The native runtime acceptance workflows invoke no LLM. Optional model clients and specialized neural components are separate declarations and cannot certify truth or acquire execution authority.
- Grammars may become higher-level letters only with source identities, expansion maps, domains, preserved contracts, and loss declarations.
- Q-paths preserve typed context and witnesses; multi-input operations retain joint premises. Reachability and a relation's truth are distinct.
- Live service is Codex's first operational deliverable. Bootstrap uses Python standard library and SQLite transactions for portable, offline, demonstrably durable behavior; the full commission evaluates PostgreSQL migration explicitly. This is a documented implementation choice, not a claim that PostgreSQL was deployed here.
- Astra is ASTRA Universal Traversals/Celestial Shells with its ATOM contract, not Astro framework. Preserve machine/view separation.
- Commission completion is finite and evidence-defined; the research program and Automaton Science University continue afterward under standing authority and resource policies.

## Package structure and ownership

- GOD_SEED.md: extensive executable constitutional commission, 192 stable obligations in 16 titles, plus sections for bootstrap, laws, authority, references, and delivery.
- CODEX_START.md: copyable entry directive.
- registry/: machine-readable constitution, continuity keys, inherited obligation crosswalk, source inventory, acceptance matrix, vocabulary.
- docs/: formal scientific foundations, vocabulary, division charters, Astra integration, source reconciliation, protocol, runbooks, post-commission mandate.
- polyia/: zero-third-party-dependency bootstrap runtime, HTTP service, CLI, exact scientific demonstrations.
- web/: accessible command plane served by the bootstrap; real state and guarded commands.
- tests/: meaningful functional/adversarial tests, including durable replay and process restart.
- sources/originals/: every current attachment unchanged.
- sources/recovered/: actual prior Poly IA, Q-Strings, Division Knot, Astra and related canonical materials.
- sources/repos/: pinned complete source snapshots and publication files from the canonical university repositories.
- evidence/: scoped fresh results, source/obligation coverage, protocol demonstration, limitations.
- deploy/: loopback service plus reverse-proxy/systemd examples; no real credentials.

## Shared runtime interface — fixed for parallel implementation

Python 3.11+. Package import is `polyia`. Implementation modules are `polyia/store.py`, `polyia/server.py`, `polyia/cli.py`, `polyia/experiments.py`. Source paths are relative to package root. Runtime data defaults to a separate `.polyia-state` directory ignored by Git.

`Ledger(db_path, workspace, requirements=None)` is a context-manageable or explicitly closeable durable store. `requirements` is a list of dictionaries with `id`, `title`, and `verifier`.

Public methods:

- `state() -> dict`: schema_version, revision, head, commission_status, requirements dictionary, guidance dictionary, research state, runs, latest checkpoint. Revision/head are an envelope outside reducer state hashes.
- `events(after=0, limit=100) -> list[dict]`: ordered committed events; each has sequence, event ID/hash, previous hash, kind, full payload, actor, timestamp, and before/after state hashes.
- `command(request, actor='operator', scopes=('command',)) -> dict`: request contains command_id (stable nonempty string), expected_revision (integer), kind, and payload (object). Response names applied revision, head and result. Replaying the same ID and same actor/payload returns the original receipt; reuse with different content fails. Revision guards apply to new commands.
- `verify() -> dict`: verifies genesis, event chain, deterministic reduction, current materialization, captured artifact bytes and stored checkpoints. Returns ok plus checked counts and diagnostics. Verification does not silently repair corruption.
- `checkpoint()`: preferably only through `command` kind `checkpoint.create` for authenticated API mutations.
- `close()`.

`CommandError` has `.code`, `.message`, `.http_status` (default 400), and optional `.details`.

Known commands:

1. `guidance.submit`: payload `{target,text,action?}`. Target is a known requirement ID or `research`. Stores SUBMITTED guidance with ID equal to command_id.
2. `guidance.ack`: `{guidance_id,disposition,reason}`; disposition ACKNOWLEDGED, DEFERRED or REJECTED. Actor recorded.
3. `guidance.apply`: `{guidance_id}`; only acknowledged guidance. Applies its registered action, not text interpretation. Supported actions `{kind:'set_priority',target:<requirement>,priority:0..9}`, `{kind:'pause_research'}`, `{kind:'resume_research'}`. Stores exact applied revision/effects. Guidance without a supported action cannot be labelled APPLIED.
4. `requirement.produce`: `{requirement_id,artifacts:[relative file paths],note}`. Captures actual permitted workspace bytes into immutable content-addressed storage; rejects empty artifacts, unsafe paths, symlink escape, runtime data and secret filenames. Sets PRODUCED.
5. `requirement.verify`: `{requirement_id}`. Executes that requirement's registered verifier, never caller-supplied code or an arbitrary status. Requires produced artifacts and checks current hashes. A verifier receipt names code/source identity, inputs, outcome and evidence class. PASS sets VERIFIED; failure stays nonaccepted with retained evidence.
6. `requirement.accept`: `{requirement_id}`. Requires current VERIFIED evidence and artifact integrity, then ACCEPTED. Verification of bytes alone can satisfy only a requirement whose declared verifier is artifact integrity, never a scientific claim.
7. `checkpoint.create`: `{note}`. Records a source-linked immutable snapshot in the same transaction as the event; captured blobs remain resolvable.
8. `experiment.run`: `{name,parameters}`. Calls only `polyia.experiments.run_registered(name, parameters)`. This returns JSON with `status`, `evidence_class`, `result`, `checks`, `limitations`. Records full inputs, deterministic result, code identity and versions. Respects research pause and input budgets. No network, subprocess, eval, generated code loading, or LLM calls.

Default verifiers: `artifact-integrity` checks actual immutable artifacts; `scientific-contracts` calls experiments.run_registered('acceptance',{}). Unknown verifiers return an explicit unsupported outcome. Full constitutional obligations start NOT_STARTED; a working bootstrap is not blanket commission acceptance.

Mutations serialize in a SQLite transaction; command receipt/event/materialized state agree after restart. Refused requests retain diagnostics without masquerading as applied state transitions. Document whether refusal audit uses a separate journal. Replay consumes recorded results and never re-executes external effects. Check hash-chain integrity on opening an existing database.

## HTTP and interface contract

`make_server(ledger, host='127.0.0.1', port=0, token=..., read_token=None)` returns a ThreadingHTTPServer-compatible object. Enforce loopback binding in bootstrap; reverse proxy supplies remote TLS during actual deployment. `serve` CLI handles shutdown and does not embed secrets in URLs.

- GET `/`: static UI; contains no server token.
- GET `/healthz`: minimal non-sensitive liveness.
- GET `/.well-known/polyia.json`: protocol and capability discovery, no private state.
- GET `/v1/state`, `/v1/events?after=N&limit=N`, `/v1/commands/<id>`, `/v1/verify`, `/v1/checkpoints/...`: authenticated reads. Operator token can read; read_token cannot mutate. If a method is not implemented, do not advertise it.
- POST `/v1/commands`: operator bearer token, exact JSON schema, bounded body, strict content type, no arbitrary Origin/CORS wildcard. Use the Ledger command API.
- Event feed: implement resumable event JSON first, SSE only if tested and truthfully advertised. No fake websocket capability.
- UI: token entered explicitly and kept only in JS memory; real polling, current revision, heartbeat/connection state, obligations, guidance submit/ack/apply, checkpoint and experiment controls. Escape untrusted text using textContent. Errors and revision conflicts visible.
- Unknown/malformed paths, non-object payloads, stale revisions, unauthorized commands, oversized bodies and malicious text receive explicit safe errors.

CLI is owned with store module: `python -m polyia init --state-dir PATH`, `serve --state-dir PATH --host 127.0.0.1 --port 8765`, `status`, `verify`, `command --file PATH`, `demo`, `worker --iterations N`. Token passed via POLYIA_OPERATOR_TOKEN; optional POLYIA_READ_TOKEN. Server must require token for data routes. CLI is local trusted operator, uses same command semantics.

## Scientific demonstrations owned by coordinator

`run_registered(name, parameters)` names: `polynomial`, `grammar-promotion`, `qpath`, `acceptance`. Pure Python exact rational math; no LLM or external dependencies. `polynomial` constructs p=bq+r and verifies coefficient equality, rational derivative equivalence with domain exclusion, and product/quotient connection. `grammar-promotion` provides exact syntax expansion plus distinct semantics evidence. `qpath` demonstrates typed n-ary prerequisites/context, supported and refused paths. These are acceptance families, not replacements for canonical corpus or universal solvers.

## Reference system

Stable requirements PIA-001..PIA-192; human aliases I.01..XVI.12. Continuity keys K-SRC, K-AUTH, K-SEM, K-STATE, K-GUIDE, K-EVD, K-REPLAY, K-GEN, K-PATH, K-COST, K-EVOLVE, K-VIEW, K-COVER, K-LANG, K-SHIP, K-FRONTIER. Keys keep their meaning regardless of document section. References carry source_id, exact file/section, version/digest; Unicode is display only, ASCII IDs are canonical. DODGE is a new package label: Deliverable, Obligations, Dependencies, Guards, Evidence. It is not claimed as prior art.

## Completion evidence for this package

Full unit/integration suite; real HTTP commands; process restart/replay; stale/idempotent/conflicting guidance tests; rejected forged evidence/tampered data; scientific exact checks; full supplied-file digest check; all inherited clauses mapped; every constitution obligation has acceptance and continuity refs; no missing local artifact references; package manifest; fresh verification report and honest full-mission NOT_COMMISSIONED marker.
