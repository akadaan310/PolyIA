# HTTP admission and redacted logging

This change bounds the standard-library commissioning server's connection handlers and request admission. It adds safe operational records for failures rejected before ledger commands. It does not make the full mission commissioned or certify production traffic capacity.

## Design and implementation plan

The existing server closes each connection after one request. A semaphore therefore bounds active request handlers before thread creation, including connections still sending headers. A global token bucket controls admission before parsing or authentication. Global admission works behind a loopback reverse proxy without trusting client-supplied forwarding headers. Per-client limits would require a separately authenticated proxy identity contract; relying only on operating-system thread exhaustion would provide less controlled refusal.

Implementation is restricted to `polyia/server.py`, `tests/test_server_limits.py`, and this document. Existing host, origin, bearer, body, and ledger guards remain required.

- [x] Write actual-socket tests for concurrency refusal/recovery, rate exhaustion/recovery, and redaction of hostile HTTP input; observe failures on the existing server.
- [x] Add admission before thread creation, release slots on every termination path, and emit bounded generic rejection responses.
- [x] Add fixed-schema JSON logs for requests, pre-authentication refusals, parse failures, and admission refusals.
- [x] Run the new tests, the existing Python suite, and the JavaScript interface suites; record precise results and remaining limits.

## Configuration

`make_server` accepts keyword-only `max_active_requests=32`, `request_rate=20.0`, `request_burst=60`, and `socket_timeout=10.0`. Active handlers must be an integer from 1 through 1024; burst must be an integer from 1 through 1,000,000. Rate must be a finite number from 0.001 through 1,000,000 connections per second; timeout must be a finite number from 0.001 through 60 seconds. Boolean values are refused. These constructor ranges prevent arithmetic/socket overflow; operators must choose lower values compatible with the host's task and memory limits. Existing callers use these defaults without new dependencies. The current CLI uses these constructor defaults; it does not introduce command-line or environment overrides.

Admission charges one token per accepted TCP connection, including malformed, incomplete, and unauthenticated requests. Tokens refill using monotonic time, up to the burst allowance. A connection denied by rate admission gets a best-effort HTTP 429 response; one denied by the handler cap gets HTTP 503. Both include `Retry-After`, the existing security headers, `Cache-Control: no-store`, and `Connection: close`, without parsing or reflecting the request. Refusal writes have a 100 ms socket timeout. A peer still sending a request body can observe a transport failure instead of the refusal response; clients must preserve the exact unresolved command for any retry. No authority or authentication assertion is made by those generic refusals. Admitted requests still pass all existing guards.

## Log contract

The `polyia.server` logger emits one JSON record for each completed handler and each admission refusal. Fields are `event`, `request_id`, `method`, `route`, and `status`. Request IDs are generated locally. Methods and route categories come from finite allowlists. Unknown methods become `OTHER`; requests rejected before route parsing use `unparsed`. No raw path, query, identifier, address, header, body, token, or exception detail enters these records. A status of `0` means no response was selected, such as an incomplete connection that timed out. A logged HTTP status records the response selected by the server, not proof the peer received it.

By default, records go to standard error as JSON, suitable for a supervisor's journal. A preconfigured logger handler may select a different sink. These records are separate from the immutable ledger and need an operational retention/access policy. Host logging configuration must bound storage and handle a saturated sink.

## Limits and required operational checks

The budget is per process and shared by all clients. One noisy client can temporarily deny admission to others, including health checks; forwarding-header spoofing cannot obtain another allowance. Restart resets the burst allowance. The kernel listen backlog, external proxy, bandwidth, memory, CPU, and journal storage still need host-level controls. Socket timeout limits inactive reads, not a total request deadline or expensive admitted ledger work. This is not a benchmark, a distributed rate limiter, or a production denial-of-service guarantee.

Deploying the change requires a new release record and separate live checks: access/refusal status through the actual proxy, source-linked checkpoint and restart continuity, redacted journal output, and supervised resource settings. The temporary public tunnel's hostname lifecycle remains a separate deployment issue.

## Verification record

On 24 October 2026, the nine new socket tests failed against the original server and passed after implementation. The initial implementation passed all 167 then-current Python tests plus 7 client and 7 UI JavaScript tests using CPython 3.13.17 / SQLite 3.53.1 and Node 22.23.3. Subsequent checks added explicit numeric configuration bounds and refusal security headers, and corrected test synchronization so receiving response bytes is not mistaken for release of the handler slot. The final focused suite passed five consecutive runs. The integrating agent owns the final combined-suite and deployment run after concurrent changes settle; these records do not certify that later combined release.

Commands: `/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -p test_server_limits.py -v`; `/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -v`; `PYTHON=/opt/polyia/runtime/bin/python3 PYTHONDONTWRITEBYTECODE=1 node --test web/client.test.mjs`; the same Node command with `web/ui.test.mjs`.
