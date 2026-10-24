# HTTP and live interface implementation report

Date: 2026-10-24. Scope: the approved Poly IA commissioning bootstrap HTTP service, browser command plane, protocol registry, and their development evidence. Full-mission status: **NOT_COMMISSIONED**.

## Delivered result

The bootstrap has a real loopback HTTP service backed by the actual SQLite `Ledger`. Its interface reads actual state and submits the same guarded commands used by the local runtime. All eight registered command types are exposed through visible controls: guidance submission, disposition and application; artifact production, verification and acceptance; checkpoints; and registered scientific runs. Authenticated controls also inspect immutable command receipts, resumable events, checkpoint contents, integrity reports, and the separate ledger refusal journal.

The final captured run passed **90 Python tests**, including **22 real HTTP socket tests**, plus **7 browser protocol-client tests** and **7 UI-handler tests**. The JavaScript suites use the actual Python server and real SQLite state. The UI suite runs the actual application handlers against a small test-only DOM. It does not constitute a real-browser rendering or accessibility audit.

Full command output, timestamps, and scope limitations are in [`../evidence/interface-development.json`](../evidence/interface-development.json). Source hashes in that evidence identify this implementation snapshot. The broader project suite may gain additional tests after this report; these counts refer to the captured run.

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| [`../polyia/server.py`](../polyia/server.py) | `make_server` factory, fixed static routes, authentication and scope separation, Host/Origin policy, bounded JSON parsing, API dispatch, safe responses, and truthful capability discovery. |
| [`../web/index.html`](../web/index.html) | Complete command workspace, labeled native controls, initial disconnected state, explicit mission status, live error/notice regions, and all required workflows. |
| [`../web/styles.css`](../web/styles.css) | Responsive visual hierarchy, desktop navigation, smaller-screen layout, keyboard focus treatment, reduced-motion support, and legible secondary-text palette. |
| [`../web/app.js`](../web/app.js) | Actual state projection, polling, selection/filtering, command handlers, exact result display, safe text rendering, and session lifecycle management. |
| [`../web/client.mjs`](../web/client.mjs) | Memory-only bearer token, authenticated fetches, read/operator scopes, revision guards, receipt validation, unresolved-command preservation, and exact idempotent retry. |
| [`../tests/test_server.py`](../tests/test_server.py) | Python `unittest` tests using actual listening HTTP sockets, real SQLite files, captured workspace artifacts, and registered science. |
| [`../web/client.test.mjs`](../web/client.test.mjs) | Optional Node built-in tests for the browser protocol client against a real Python server, including response loss after commit and malformed receipts. |
| [`../web/ui.test.mjs`](../web/ui.test.mjs) | Optional Node built-in tests executing actual UI event handlers against a test-only DOM and the real HTTP server. |
| [`../registry/openapi.json`](../registry/openapi.json) | OpenAPI 3.1 route definitions, explicit read/operator schemes, all eight exact command payload alternatives, response schemas, and transport limits. |
| [`HTTP_PROTOCOL.md`](HTTP_PROTOCOL.md) | Human-readable protocol, authority model, cursor/retry semantics, proxy configuration contract, operational boundaries, and audit limitations. |
| [`../evidence/interface-development.json`](../evidence/interface-development.json) | Captured execution evidence, earlier red/green observations, implementation hashes, environment notes, and explicit unperformed checks. |

The runtime store, CLI, scientific implementation, constitution, deployment examples, source originals, and final package assembly are owned by the parallel coordinator/runtime work. This interface task did not commit, deploy, modify upstream sources, or install packages.

## Service behavior and decisions

### Authority and transport

`make_server(ledger, host='127.0.0.1', port=0, token=..., read_token=None, public_origin=None)` returns a `ThreadingHTTPServer` compatible instance. It enforces loopback binding. The explicit optional `public_origin` extension was coordinated with the CLI and permits one validated HTTPS reverse-proxy authority while preserving local access. Incoming Host and Origin are checked together. No forwarded header can expand authority, and no wildcard CORS grant is emitted.

The operator token can read and mutate. A distinct optional reader token can only read, including integrity verification. HTTP commands use the fixed actor `operator`. Token secrets are configuration, absent from served assets and URLs. Tokens in the browser are private JavaScript fields, never browser persistent storage, and the input is cleared on submission. Page exit and explicit disconnect clear the session projection.

The portable server provides strict request framing, a 64 KiB body budget, a 16 KiB parsed-header budget, bounded nesting and JSON value count, finite-number/unique-key checks, exact top-level command fields, and explicit safe errors. All paths come from a fixed route table or a validated identifier segment. Responses have no-store caching, restrictive CSP, nosniff, frame denial, and a request reference. Unexpected exception details are not returned or logged; only their class and request reference are logged.

### Durable commands and honest projection

State mutations delegate directly to `Ledger.command`. The server does not manufacture state transitions, verifier outcomes, scientific results, or receipts. Events are resumable JSON pages, not an advertised streaming transport. The browser shows current revision and its separately loaded event cursor. It treats a successful HTTP command receipt as a recorded operation and displays the inner verifier/scientific outcome separately.

If a response is lost after commit, the browser retains the exact original request. Retry uses the same command ID, payload, actor, and expected revision; it recovers the original receipt without advancing twice. A new command cannot replace an unresolved one. A revision conflict is shown to the operator, state is refreshed, and no automatic rebase silently changes intent. An incomplete or mismatched HTTP 200 receipt is rejected and remains recoverable.

`NOT_COMMISSIONED` remains visible. Accepting an artifact-integrity requirement does not accept a scientific claim or the whole commission. Scientific runs expose full report status, inputs, checks, limitations, versions, and code identity. Applied research pause disables the run control and is independently enforced by the runtime.

### Interface design

The workspace uses a persistent navigation rail, a clear connection panel, four factual summary metrics, searchable obligations, explicit workflow panels, and inspectable evidence records. Initial metrics are unknown until authenticated state is received. Four-second polling runs while the tab is visible; failed refreshes make the stale connection visible and disable mutations until a fresh read succeeds. Read tokens retain inspection controls while mutation controls are disabled.

Guidance text and every other dynamic string are inserted through text nodes or `textContent`. No dynamic HTML insertion is used. All data-bearing result panels show the actual JSON for inspection. Native controls have labels, keyboard focus styling, and explicit button states. A structural check found 100 unique IDs, 15 valid explicit label targets, and only packaged same-origin script/style references. Secondary text colors were adjusted for contrast on the pale workspace. A real browser and screen reader were not available, so these implementation properties are not a claim of complete accessibility conformance.

## Verification and results

The final recorded checks were run with Python 3.12.14 and Node v24.19.0. The product runtime requires Python 3.11+ and no third-party Python or browser packages. Optional development checks require a recent Node with the built-in test runner, fetch, Web Crypto, and structured cloning. Node is not needed to serve or use the interface.

| Command | Observed result | What it establishes |
| --- | --- | --- |
| `python -m unittest discover -s tests -v` | 90 tests passed; exit 0 | Current full Python suite, including store durability/replay, CLI subprocess behavior, science, and HTTP. |
| `node --test --test-isolation=none --test-reporter=spec web/client.test.mjs` | 7 tests passed; exit 0 | Actual browser protocol client against the real HTTP and SQLite runtime. |
| `node --test --test-isolation=none --test-reporter=spec web/ui.test.mjs` | 7 tests passed; exit 0 | Actual application event handlers, safe text rendering, all main command/read controls, external-state polling, and session lifecycle in a test-only DOM. |
| `node --check web/app.js` and `node --check web/client.mjs` | Exit 0 | JavaScript parse validity. |
| Python HTML structure check | 100 unique IDs; 15 explicit label references resolved | No duplicated IDs or broken explicit label targets in the source HTML. |

The two `--test-isolation=none` JavaScript commands above are separate invocations. Their test fixtures have separate Python servers and document globals. Do not combine them into one process with isolation disabled.

The default execution sandbox denied socket creation before HTTP assertions were reached. Narrow local-only escalation was approved for the tests; the successful runs use ephemeral loopback sockets and no external service. Earlier sandbox failures are recorded as environmental failures rather than product failures or passing assertions.

### HTTP scenarios exercised

The 22 HTTP tests cover public liveness/discovery and token-free assets; required authorization on private routes; reader/operator separation; exact receipt lookup and retries; stale and conflicting requests; concurrent revision guards; resumable event pages; guidance submission/acknowledgment/application; real artifact capture/verification/acceptance; checkpoint reads; ledger integrity reads; actual results from all four scientific experiments and research-pause refusal; unknown commands and records; exact schemas; malformed, duplicate, deep, and non-finite JSON; media type/body limits; invalid queries and paths; duplicate/ambiguous headers; content-length framing; disallowed Host and Origin; configured HTTPS authority; wrong methods and no CORS wildcard; loopback/token configuration validation; generic internal errors; HEAD behavior; and OpenAPI discovery resolution.

### Regressions found and corrected

The initial HTTP tests failed explicitly because the server did not exist. Once the server existed, the remaining static-asset test failed until the actual UI assets were present. OpenAPI discovery likewise had an observed 503 failure before the machine-readable contract was written.

Protocol-client tests were written before the client module and initially failed. Their transport-loss scenario intentionally commits a real command, discards its response, and then verifies that exact retry returns the original revision and receipt. A later regression test showed that a malformed HTTP 200 response could otherwise be interpreted as success; strict receipt identity, revision, head, and result validation corrected that behavior.

UI-handler tests reproduced two concrete lifecycle defects before their fixes: reconnecting during a delayed command response left the new session’s controls locked, and page exit cleared the token without clearing the visible connected state. Both have passing regression checks. The same UI suite exercises malicious guidance markup as preserved literal text, a full artifact acceptance workflow, science execution, checkpoint/integrity/receipt/refusal reads, an external writer followed by polling, and visible refusal of malformed scientific parameters without a state mutation.

## Material limits and outstanding commissioning work

No real-browser render or screenshot was produced. The installed Playwright library pointed to a Chromium executable that did not exist, and this task did not install a browser. Browser layout, complete keyboard/screen-reader behavior, and cross-browser conformance remain commissioning checks. The test-only DOM is described accurately and is not substituted for browser evidence.

No remote deployment, TLS termination, reverse-proxy runtime, production load test, global connection limiter, rate-limiting service, or multi-user identity system was established here. The optional configured HTTPS authority is covered by local HTTP header tests. Socket tests used IPv4 loopback; IPv6 loopback code has not been separately exercised.

The ledger refusal journal covers commands that reach the store. HTTP authentication, parsing, routing, Origin, and top-level schema refusals return diagnostics but are not durably audited. Production commissioning must add appropriate redacted access/security logs and resource controls. No full request URL/body/token is logged by the built-in handler.

Internal hash-chain and replay verification is scoped evidence, not a digital signature or an external truth guarantee. These results demonstrate a functioning commissioning bootstrap and its guarded interface. They do not confer blanket acceptance on the 192 constitutional obligations or end the standing research program.
