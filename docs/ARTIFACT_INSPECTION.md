# Authenticated captured-artifact inspection

The command plane can return the actual bytes previously captured by the ledger.
This makes the constructed Book of Forms and other produced evidence inspectable
through the same private service that records their identities. It does not
publish a library, serve workspace paths, or change scientific or mission
acceptance. The commissioning coordinator separately deploys this implementation.

## Byte interface

`GET /v1/blobs/{digest}?offset=0&limit=65536` requires an operator or read bearer
token in the `Authorization` header. `digest` is exactly 64 lowercase hexadecimal
characters identifying a captured SHA-256 object. Tokens never belong in URLs.

Successful responses are JSON with exactly these fields:

```json
{
  "digest": "<64 lowercase hexadecimal characters>",
  "total_size": 70144,
  "offset": 0,
  "encoding": "base64",
  "data": "<base64 encoding of the requested captured bytes>",
  "next_offset": 65536
}
```

The illustration abbreviates the digest and encoded bytes. The response's
`data` is ordinary padded base64, with no text conversion or MIME execution.
Decode each chunk and concatenate in offset order. Follow `next_offset` until
it is null; a client reconstructing the whole object can then independently
check SHA-256 against `digest`.

| Input | Contract |
| --- | --- |
| `offset` | Default 0; one ASCII decimal integer from 0 through 2^63−1; must not exceed the object's size. |
| `limit` | Default and maximum 65,536 decoded bytes; minimum 1. |
| EOF | Offset equal to total size returns empty base64 and null continuation. |
| Query validation | Unknown keys, duplicate keys, empty values, signed/fractional/nondecimal values and malformed queries refuse. Decimal fields have at most 19 digits. |
| HTTP Range | Refused; use the explicit JSON chunk interface. |
| `HEAD` | Same authorization, validation, full-object hash check, status and representation length as GET; no response body. |

Errors use the existing structured error envelope. Invalid digest/query is 400;
missing/invalid authorization is 401; absent stored digest is 404; corrupt size
or hash is 409 `INTEGRITY_ERROR`; an offset beyond EOF is 416 `INVALID_RANGE`.
Other methods return 405. Host/origin checks, connection admission budgets,
`Cache-Control: no-store`, CSP and other existing HTTP boundaries also apply.

The route delegates exclusively to `Ledger.get_blob`. That method validates the
stored length and SHA-256 before any captured content is returned. It never
consults the live artifact path. Editing or removing a workspace file therefore
does not alter the bytes read under an earlier captured digest. A successful
read says that these stored bytes match the identity; it does not establish
that their claims are true or that the whole ledger has passed verification.

GET and HEAD do not submit commands, advance semantic revision, append events,
or change requirement status. Operational access/refusal logs use the finite
category `blob`; they contain no digest, raw path, query, token or content.
Discovery advertises `captured_artifact_reads: true` and `blob_chunk_bytes:
65536`. [OpenAPI](../registry/openapi.json) describes both methods and the
`BlobChunk` response.

## UI and Book of Forms

Connect with read or operator access, select an obligation, and inspect its
**Captured artifacts** list. Each row shows the captured path, byte size and
SHA-256. Merely displaying that list fetches no blob content. **Inspect bytes**
explicitly loads the first chunk; byte offset, chunk size and **Next chunk**
permit further inspection. Content is held only for the current chunk.

The constructed Book of Forms was produced under **PIA-189**. Select that
obligation and the captured `books/book-of-forms/BOOK.md` entry. The service reads
that captured version, even if a newer working edition exists. The viewer does
not turn source links or Markdown into executable navigation, nor does it expose
uncaptured files or a public corpus listing.

The UTF-8 view uses fatal decoding with no replacement characters, retains a BOM
if present, and renders via `textContent`. HTML, Markdown and source code remain
inert text. Chunks containing control bytes or invalid UTF-8 instead show base64
with **Binary or incomplete UTF-8 sequence**. A valid file can acquire that label
when a byte boundary splits a multibyte character; it is not a claim that the
complete file is binary. Selecting **Exact bytes as base64** always exposes the
unaltered chunk. The panel explicitly labels complete versus partial content
and its half-open byte interval.

Changing the selected capture invalidates prior requests. Disconnect, session
change and pagehide clear captured content; late responses cannot restore it.
No token is added to a hyperlink or download URL, and no dynamic HTML is used.

## Memory and scope

The 64 KiB cap bounds each returned decoded chunk, not the complete database read.
`get_blob` currently loads and hashes the entire stored object for every GET or
HEAD. Ordinary artifact capture limits each file to **8 MiB** and the command
aggregate to **32 MiB**. Source-context capture separately limits each file to
2 MiB and its aggregate to 8 MiB. The reader inherits these capture boundaries;
it is not a streaming database API or an additional defense against manually
injected oversized database rows. Concurrent handlers can hold separate blob
copies, in addition to SQLite and encoding allocations. Existing handler/rate
admission limits remain in force.

The viewer retains one bounded chunk, not an accumulating whole-book buffer.
Authenticated roles share the existing service-wide read scope: any stored digest
they know can be inspected. This increment does not introduce per-artifact ACLs,
public publishing, bulk export, search or custody admission of new sources.

## Registered rasm example

The experiment selector and OpenAPI experiment enumeration now include `rasm`.
**Use rasm example · كتب** fills the following envelope without submitting it:

```json
{
  "version": "polyia.rasm/0.1",
  "chart": "timeless.rsa28/0.1",
  "operation": "project",
  "text": "كتب"
}
```

An operator can then run the registered experiment explicitly. The actual result
has contextual skeleton `كٮٮ` and 15 consonant fillings under the named authored
chart. It does not identify the intended historical reading or certify semantic
equivalence; see [Rasm implementation](RASM_IMPLEMENTATION.md).

## Verification evidence

The new HTTP tests were written before the route. After correcting fixture
setup to honor existing runtime-directory and nonempty-evidence capture guards,
the red run produced 25 failing assertions across eight tests because the route
did not exist. Implementation and schema then passed all eight tests. The
zero-length byte-reader boundary uses an explicitly inserted, correctly hashed
test object; production capture still rejects empty produced evidence.

Three initial UI tests failed for the missing viewer, then passed after it was
implemented. A fourth test failed before the rasm selector/example was added,
then executed the real registered projection successfully. The test DOM rejects
dynamic `innerHTML`; it exercises actual application handlers against a listening
HTTP service. This is DOM wiring evidence, not full-browser rendering or
accessibility certification.

Focused verification for this increment:

```bash
/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -p test_artifact_http.py -q
/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -p test_server.py -q
PYTHON=/opt/polyia/runtime/bin/python3 PYTHONDONTWRITEBYTECODE=1 node --test web/ui.test.mjs web/client.test.mjs
```

Results: **8 artifact HTTP tests**, **22 existing server tests**, and **22 Node
UI/client tests** (13 UI, 9 client). Coverage includes both roles, unauthenticated
denial, URL credential refusal, exact reassembly after workspace mutation,
EOF/one-byte/chunk limits, invalid queries, missing blobs, wrong-length and
same-length corruption, HEAD behavior, finite audit fields, unchanged semantic
state, hostile book markup, binary bytes, split UTF-8, continuation and stale
session responses. The coordinator performs the consolidated release suite and
deployment separately; no full-project acceptance is inferred from these counts.
