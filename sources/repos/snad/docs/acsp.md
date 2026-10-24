# Optional ACSP integration

The actual Agent Continuity & Session Protocol implementation is [akadaan310/NetGovComEduGovOrgEduGovComNet](https://github.com/akadaan310/NetGovComEduGovOrgEduGovComNet), despite its repository name. The inspected default commit is `9fcf2e1da3ce01a4e66eb5be5e2249b1f211878b`. Its source implements **ACSP/0.1**, not PURL's newer resource lifecycle. Discovery performed only repository reads and HTTP GETs; no ACSP resource was created, proposed to, or modified.

The appropriate initial SNAD adapter prepares an ACSP/0.1 **TOK append proposal** as a local artifact. A prepared request is not a submitted proposal; a submitted proposal is not an accepted TOK. The service's owner resolves proposals under separate authority.

## Actual source and branches

| Branch | Tip | Relevant contract |
| --- | --- | --- |
| `claude/agent-continuity-protocol-doi4bn` | `9fcf2e1da3ce01a4e66eb5be5e2249b1f211878b` | Default ACSP/0.1 resource, TOK, capability, proposal and checkpoint operations |
| `ccr-d0887a23-30wf63` | `e8d989afee2025e2315605b4349ccfa833db13bf` | Default lineage plus local server/migration support |
| `claude/acsp-program-001-k616hw` | `417da6c740de22aaa497e10a09251c4c2af7b948` | ACSP/0.1 Program 001 agent identity/embodiment/Scroll/transition-history extension |
| `claude/acsp-purl-composition-adsbn6` | `edd1963750d1fc839cc350797b6a9bc9da8f6a20` | ACSP/0.2 operation records; explicitly accepts 0.1 and 0.2 envelopes |

The Program 001 and composition branches are distinct histories. Do not combine their contracts merely because both extend ACSP. No explicit license file was observed in the inspected default tree.

The default source's [operation registry](https://github.com/akadaan310/NetGovComEduGovOrgEduGovComNet/blob/9fcf2e1da3ce01a4e66eb5be5e2249b1f211878b/src/protocol/operations.ts) supplies Zod payload schemas, operation discovery, required authority and HTTP invocation. [TOK records](https://github.com/akadaan310/NetGovComEduGovOrgEduGovComNet/blob/9fcf2e1da3ce01a4e66eb5be5e2249b1f211878b/src/research/tok.ts) define the research artifact shape. [The Next route](https://github.com/akadaan310/NetGovComEduGovOrgEduGovComNet/blob/9fcf2e1da3ce01a4e66eb5be5e2249b1f211878b/app/%5B%5B...path%5D%5D/route.ts) mounts a framework-independent Fetch handler. Runtime is Node >=20 with Next, Zod and Postgres; development can use embedded PGlite, while production refuses an absent database configuration.

## Verified HTTP discovery

On 2026-10-18 the following GETs were measured again, independently of historical PURL reports:

| URL | Result |
| --- | --- |
| `https://acsp-one.vercel.app/` | 200 JSON discovery, ACSP/0.1 |
| `https://acsp-one.vercel.app/.well-known/acsp` | 200, same discovery bytes |
| `https://acsp-one.vercel.app/protocol.json` | 200 machine-readable specification with operation JSON Schemas |
| `https://acsp-one.vercel.app/r/8N2RXG1MW79S?format=json` | 500 `internal_error`; current resource state unavailable |
| `https://acsp-one.vercel.app/r/8N2RXG1MW79S/transitions?format=json` | 404 |

The historical resource above is a discovery probe, not SNAD's identity or mutation target. A successful protocol GET does not establish database readiness. The live service does not disclose an exact deployed commit in the inspected discovery response; the source pin and HTTP observations are therefore recorded separately.

## Local export contract

An ACSP/0.1 mutation uses `POST /r/{id}/operations`, `Content-Type: application/json`, and this strict envelope:

```json
{
  "protocol": "ACSP/0.1",
  "operation": "propose",
  "actor": { "session_id": "snad-local-export", "kind": "agent" },
  "idempotency_key": "snad-artifact-0123456789abcdef",
  "payload": {
    "operation": "append",
    "payload": {
      "type": "reference",
      "title": "SNAD portable experiment artifact",
      "summary": "Prepared locally; not submitted or independently verified.",
      "content": "A compact artifact manifest, hashes, provenance and replay instructions belong here.",
      "stated_confidence": "unclassified",
      "refs": [ { "citation": "SNAD artifact manifest; exact content hash supplied by the exporter" } ]
    },
    "rationale": "Offer an attributable computational artifact for owner review."
  }
}
```

This is an illustrative request shape, not a record of a performed operation. A real exporter must fill actual content hashes and provenance from the artifact it receives. Preserve uncertainty and observed/derived/hypothesis status in its manifest; do not convert source confidence into verified truth.

The live `append.payload_schema` and `propose.payload_schema` are captured in [acsp-discovery.json](../evidence/acsp-discovery.json). The nested proposal payload must be validated again against the selected inner operation schema: the outer proposal's generic `payload` object alone is insufficient.

- TOK `type` is one of `observation`, `finding`, `hypothesis`, `question`, `constraint`, `decision`, `rejection`, `uncertainty`, `reference`, `task`, `delegation`, `closure`. Only `type` and a nonempty `title` are required.
- Title maximum is 200 characters, summary 2,000, content 20,000, and references 20. Confidence is `unclassified|low|medium|high`; it is explicitly the author's claim.
- A reference is strictly `{tok,note?}`, `{url,note?}` or `{citation}`. URLs must actually be HTTP(S), despite that custom source refinement not appearing in the emitted JSON Schema. Local paths belong in citation/content, not a fabricated URL.
- Actor session IDs use `[A-Za-z0-9._:@-]{1,128}`. Idempotency keys use `[A-Za-z0-9._:-]{8,128}`. Resource IDs are twelve Crockford-base32 characters. Do not invent a resource ID or capability when preparing an unbound local export.
- The request body is limited to 65,536 UTF-8 bytes. Do not silently truncate source evidence to fit. Export a compact manifest with exact hashes and linked portable artifacts, or reject an oversized export.
- `expected_version` is an optional positive integer for append/propose/checkpoint; if supplied it must match current state. It is mandatory for update, supersede, resolve_proposal and close.
- `append` requires an `append` or owner capability. `propose` needs read access plus a resource accepting proposals, and records asserted identity without an executing capability. A proposal still persists a mutation and must never be sent as part of read-only discovery.

Capabilities belong in `Authorization: Bearer ...` at execution time, never in public exported artifacts or URLs. Session attribution does not itself grant authority. The service supports read-only `?action=prepare_propose` intent documents; opening one does not submit it.

## Transition-history interoperability is separate

The Program 001 branch's `src/continuity/representation.ts:876` exports `GET /r/{id}/transitions` with format `acsp-transition-history/1`. Each transition carries event logical time `t`, chained versions, operation, actor session, identity assurance, embodiment, substrate, optional execution, checkpoint references, observation labels and wall-clock `occurred_at`. `deterministic_sha256` hashes canonical sorted-key transition JSON with only `occurred_at` removed.

The independent reader at [substrateIO commit 7ace119a544fc736f0d4ec1d72cded9dad0a83e3](https://github.com/akadaan310/substrateIO/blob/7ace119a544fc736f0d4ec1d72cded9dad0a83e3/substrate/acsp.py) verifies format, transition count, contiguous time, version chaining, actor sessions, observation vocabulary and this hash. Its four projection tests were executed and passed, including tampering detection. Its supplied 19-event fixture uses simulated actors; it is not a real model session study. Operation-label projection intentionally forgets execution outputs and should not be described as full-state equivalence.

SNAD's linguistic discourse transitions are not ACSP identity lifecycle events. Exporting them as fake `create`, `embody` or `execute` records would falsify provenance. Prepare a TOK describing a real SNAD artifact, or import a genuine ACSP history as a separately typed corpus. The current live 0.1 deployment returned 404 for the transition endpoint, so extension import availability must be discovered rather than assumed.

## Boundaries and next operation

Local schema-grounded preparation is available without an ACSP service dependency. Live publication remains unperformed: no SNAD ACSP resource ID, owner/delegated capability or successful resource-state read was established. The next remote operation would first inspect a separately authorized target resource and its advertised authority, then submit a reviewed prepared request if authorized, and read back the resulting proposal/TOK/event. Neither this source inspection nor PURL authorization grants authority over an existing ACSP identity.

## Working offline adapter

`scripts/integrations/acsp.mjs` exports `buildAcspProposal(input)` and `validateAcspProposal(envelope)`. The builder requires explicit `sessionId`, `idempotencyKey`, `title`, `summary`, `objective`, `analysis` and source `refs`; `expectedVersion` is optional. It stores the objective and unchanged finite JSON analysis in a reference TOK's opaque `content`, preserving source attribution without inventing protocol event semantics. The validator returns an array of issues. It checks the local credential-free propose-append subset, nested TOK/ref constraints and UTF-8 body size. It intentionally requires at least one source reference. It rejects non-JSON values and hidden properties instead of silently dropping evidence.

The executable entry point only reads/writes local JSON:

```bash
node scripts/integrations/acsp.mjs --input analysis-export.json --output proposal.json
```

Omitting `--output` prints the prepared envelope to stdout. Supply the builder input fields above in `analysis-export.json`. It has no network transport. An actual source-reconstruction example was generated at [acsp-proposal.json](../evidence/acsp-proposal.json), with an exact hash of the source-audit evidence and explicit unsubmitted status inside its content. That example was checked against both captured live JSON Schemas; this is offline shape validation, not server acceptance.

`tests/integrations.test.ts` was written and observed failing before implementation, then passed. It covers the real envelope/payload shape, preservation of uncertainty and provenance, deterministic snapshots, mutation isolation, service bounds, invalid references/credentials and executable CLI output. All five integration tests and the project's TypeScript check pass. The source evidence records the full-suite result at this integration checkpoint; final project-wide results belong to the main verification report.
