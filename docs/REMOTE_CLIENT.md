# Durable machine client

`polyia.remote.RemoteClient` provides a standard-library client for the actual
HTTP command plane. Before sending a mutation, it commits the complete guarded
request to a private local SQLite journal. If the response disappears, that
request survives a client process restart. Recovery resends the exact original
request so the service validates its full actor-bound identity before returning
an earlier receipt or executing it. It never generates a fresh ID
to conceal an uncertain outcome.

The network client is separate from the pure scientific kernels. An article,
native program or source document cannot invoke it. Its operator configures the
service origin and bearer credential explicitly; there is no arbitrary source
URL fetch or external-effect adapter here. This implements part of the machine
SDK and retry contracts, not the complete broker/agency factory acceptance.

## Invocation

On a host with the package and the configured credential in its environment:

```bash
python -m polyia.remote --origin https://YOUR-ACTUAL-SERVICE \
  --journal /private/client/outbox.sqlite3 state
python -m polyia.remote --origin https://YOUR-ACTUAL-SERVICE \
  --journal /private/client/outbox.sqlite3 submit --file command.json
python -m polyia.remote --origin https://YOUR-ACTUAL-SERVICE \
  --journal /private/client/outbox.sqlite3 pending
python -m polyia.remote --origin https://YOUR-ACTUAL-SERVICE \
  --journal /private/client/outbox.sqlite3 recover
```

`YOUR-ACTUAL-SERVICE` is a placeholder, not a deployment claim. The origin can
instead come from `POLYIA_PUBLIC_ORIGIN`. The default credential is
`POLYIA_OPERATOR_TOKEN`; `--token-env POLYIA_READ_TOKEN` selects observer access.
The CLI has no argument for putting the secret itself in the process command
line. A command file uses the existing protocol's `command_id`, `kind`,
`payload`, and `expected_revision`; state reads supply the observed revision.
Read-then-write is not atomic: a concurrent mutation produces a revision conflict.

The Python API has the same boundary:

```python
with RemoteClient(origin, token, journal_path) as client:
    current = client.state()
    receipt = client.submit(complete_guarded_command)
```

No mutation is issued by construction, `state`, or `pending`. Reusing a completed
ID with identical canonical JSON returns the stored receipt. Changed JSON types
or values under that ID are refused, even when Python would compare the values
equal. One unresolved request prevents new requests through that journal.

The first network operation checks discovery for `polyia.command-plane` version
`1.0.0` and `/v1`. An incompatible version refuses dispatch while retaining any
pending request. Compatibility is checked again when a client process reopens;
a historical completed receipt can still be inspected locally without a network
call. This does not negotiate a new protocol or silently reinterpret old data.

## Recovery semantics

A valid matching committed receipt closes the pending operation. A complete
matching `REVISION_CONFLICT` refusal also closes it: the service checks a
committed exact request before its revision, so this refusal resolves the
original operation. Both outcomes remain in the local journal.

Authentication, admission-rate, proxy, parsing, malformed-receipt and transport
errors remain uncertain. A token rotation can be supplied when reopening the
same journal, then `recover` resends the same request. A GET receipt alone is
insufficient: it does not bind the full request and could belong to a colliding
ID from another client. There is deliberately no
automatic discard-and-resubmit behavior. A persistent non-revision refusal
requires operator reconciliation through the service's command and refusal
history; this client does not claim that an arbitrary error proves an earlier
lost request never committed. Other authorized clients can continue independent
work, while the original request identity remains retained.

The journal binds one exact origin. A tunnel hostname change requires explicit
service/ledger identity reconciliation and a separate client journal; an old
journal cannot silently send pending commands to a different address. Cryptographic
server identity beyond verified HTTPS and the configured origin is not supplied
by this client. Recovery is not proof of universal exactly-once external effects.

## Boundaries and evidence

The client accepts only HTTPS, with normal certificate validation and no redirect
following. The Python API has an explicit test-only allowance for literal
127.0.0.1/::1 HTTP, absent from the CLI. The bearer remains in process memory;
the journal stores requests and receipts, never the configured credential.
It refuses submitted command data and decoded responses containing that literal
credential, including JSON-escaped spellings. This is protection for the configured
credential, not a general detector of all secrets or arbitrary encodings. Private command/receipt
content remains private data: journal directories require owner-only access and
regular files require mode 0600. A POSIX file lock prevents concurrent dispatch
through one journal. The local account, its filesystem and interpreter are trusted.

Requests are limited to 64 KiB and responses to 16 MiB. The socket timeout is at
most 60 seconds; it is an inactivity timeout, not a hard total wall-clock limit
against a slowly streaming peer. The client does not provide background polling,
unlimited retries, journal pruning, distributed leases, signatures or backups.
It retains completed receipts as actual data rather than a scientific truth claim.

`tests/test_remote.py` uses listening HTTP servers and actual SQLite ledgers. It
checks lost responses before and after a real commit, client close/reopen,
idempotent recovery, stale revisions, observer refusal, JSON type-sensitive ID
reuse, malformed responses, local journal damage, private permissions, an actual
cross-origin redirect and concurrent journal ownership. The source contract is
the existing [HTTP protocol](HTTP_PROTOCOL.md), its read/command parity, and
[tool retry/uncertainty requirements](TOOL_AND_MODEL_CONTRACTS.md). No fresh test
count or live deployment is inferred from this specification; release evidence
records those separately.
