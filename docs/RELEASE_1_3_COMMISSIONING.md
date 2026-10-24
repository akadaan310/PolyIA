# Runtime 1.3.0 commissioning increment

This increment makes captured evidence inspectable, adds the source-grounded
Timeless rasm bridge, and implements the first full-mission acceptance adapter,
PIA-042. The full Option A commission, including B/C, remains **NOT_COMMISSIONED**.

## Behavior and boundaries

- Authenticated observers and operators can inspect immutable captured bytes
  through GET/HEAD `/v1/blobs/{sha256}` and the browser. Responses contain at most
  64 KiB of decoded bytes. Workspace edits cannot alter a captured object. The
  current reader hashes the entire stored object in memory; see
  [artifact inspection](ARTIFACT_INSPECTION.md).
- The registered rasm bridge projects contextual Arabic skeletons, enumerates
  bounded inverse fibers, preserves original surface information for exact
  recovery, and keeps scientific and publication limits explicit. The authored
  chart gives كتب fifteen possible consonant fillings. Three additional upstream
  TypeScript files are admitted as selected file snapshots with exact Git/SHA
  identities; none replaces an original source. See [rasm](RASM_IMPLEMENTATION.md).
- PIA-042 verification runs sixteen fresh artifact-capture conformance checks.
  Exact candidate source, loaded implementation, obligation/acceptance versions,
  source context and inherited applicability are bound. Replay does not rerun
  the verifier. All other mission adapters remain unsupported in this release;
  see [mission verification](MISSION_VERIFIERS.md).
- Historical schema-2 contexts and existing native/intake/Astra execution
  receipts remain valid. The Book of Forms evidence is rebuilt against this
  implementation; the owner-authorized construction remains distinct from all
  previously retained books.

## Fresh verification on the target VM

Oracle VM `ollama-a1`, Ubuntu 22.04 arm64, Python 3.13.17 / SQLite 3.53.1:

- [233 Python tests](../evidence/commissioning-2026-10-24/runtime-1.3-python.log)
  passed in 22.787 seconds.
- [22 JavaScript tests](../evidence/commissioning-2026-10-24/runtime-1.3-node.log)
  passed, exercising actual HTTP requests and interface event handlers.
- [Chromium 156.0.8078.4](../evidence/commissioning-2026-10-24/browser-1.3/report.json)
  passed fourteen checks against a real isolated HTTP/SQLite fixture. Desktop,
  mobile and captured-book screenshots are retained beside the report and were
  visually inspected. This is one browser on one host, not accessibility or
  cross-browser certification. Playwright is an external development dependency.
- [No-LLM checks](../evidence/commissioning-2026-10-24/runtime-1.3-nollm.json)
  passed runtime dependency/model-artifact inspection and intercepted-network/
  process execution of the seed, native, intake, Astra, rasm and PIA-042 checks.
- [Upgrade rehearsal](../evidence/commissioning-2026-10-24/upgrade-1.3-rehearsal.json)
  opened a consistent backup of the actual live revision-69 ledger first with
  installed 1.2, then candidate 1.3. The complete state was identical and integrity
  passed. The live database was not used as a test fixture.
- The Book of Forms's twelve exercises and all 62 topic identities were checked.
  An independent reviewer verified mission binding/replay, rasm and artifact
  HTTP/UI behavior, including two additional stale-response cases.

Review found a loaded context-manager wrapper binding gap and a durable rasm
recovery size mismatch. Both were reproduced, corrected and regression tested
before this release. A recovery envelope receives an explicit bounded allowance;
the total HTTP command remains capped at 64 KiB.

## Release and operation

The manifest deliberately advances from runtime 1.2 and retains its predecessor
digest. Original source bytes, source identities and historical receipts are
preserved. The source census is 1,038 files, including the owner clarification
and three new selected upstream files. Deployment, public HTTPS checks, an actual
PIA-042 acceptance and the resulting checkpoint are recorded separately after
installation; local tests do not claim those actions have happened.

The 1.2 execution notes described permanent ingress as a required gate. A full
source audit corrected that interpretation in live guidance at revision 67:
PIA-008/181 require actual authenticated TLS service and restart/readiness
evidence; PIA-037 requires address continuity for independent inspection. The
sources specify neither a permanent hostname nor a minimum uptime duration.
The current quick-tunnel address is real, but can change after tunnel restart.
The unsuccessful dedicated ingress attempt and its scoped rollback remain
recorded. This correction does not erase the operational continuity limitation.

Compiler quantitative contracts, constructive generators, broad inherited
subject/corpus acceptance, bounded sealed research/evolution and further mission
verifiers continue next. The University mandate remains pending the finite
commission certificate; this increment does not activate it.
