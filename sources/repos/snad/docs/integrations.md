# Optional PURL, ACSP and CGIT integration

SNAD runs without remote services. The integration transports attributable mission state and artifacts; it does not infer speaker intent or certify scientific results. The exact discovery record is [service-discovery.json](../evidence/service-discovery.json). Captured service JSON and reconstructed request schemas are in [schemas](../schemas/).

The independent live SNAD mission is <https://purls-production.up.railway.app/p/resource_bd80f9093ac5fb3b2d176291>. Its initial published checkpoint is version 7. Creation, compilation, one declared identity test, durable execution, checkpoint and publication succeeded; anonymous replay returned `valid:true`. Execution `execution_dfda93eb6d9675f51cdffb33` produced artifact `artifact_9d6745ef1e313dd7bf8b25c1`. Sanitized operation outcomes and read-backs are in [evidence/purl-live](../evidence/purl-live/). This checkpoint precedes scientific implementation; inspect the current continuity state for later evidence.

## Observed products and source

Read-only discovery began on **2026-10-18 at 19:57 UTC**, before SNAD implementation. The supplied prior mission page, manifest, continuity, PURL home and CGIT home all returned HTTP 200. The prior mission was version 15 with anonymous authority `{principal_id:null,owner:false,rights:["read"]}`. All mutation operations were unavailable. Its nine embedded document hashes independently matched; 38 recorded objective nodes and 59 dependencies were present. Recorded PASS states remain author assertions. That mission was never mutated or forked as SNAD's identity.

The delivery branch `codex/purls-cgit-consumer` resolved to **375529019fbbe467303645d5ccde5f783946a78a**. Both live `/api/runtime` responses reported deployed API commit **367e8ed063065cb8bc9ebb8c9fc55235b4828723**, Node 22.14.0, x64 and Supabase persistence. The seven inspected SDK/compiler/identity/resource/HTTP/CGIT/schema files were byte-identical between those commits. HANDOFF.txt reports worker commit **3b2784b7f9bb217954ef75c5f8e4985c748e4627**; this worker revision is a handoff claim, not an independently queried worker runtime.

Source: <https://github.com/akadaan310/purl/tree/codex/purls-cgit-consumer>. The initial handoff and discovery outcomes are retained. No source license grant was established during this contract inspection; the integration utility downloads and verifies the inspected SDK at runtime rather than redistributing its implementation.

## Authentication and authority

Both products advertise `PURL/launch-1` at `/.well-known/purl`. Public GET does not authorize POST. Unauthenticated `/api/identity/me` and CGIT `/api/cgit/repos` returned HTTP 401; a guessed `/api/identity/session` returned 404 and is not the supported flow.

Verified OIDC login was unavailable: `PURL_OIDC_ISSUER`, `PURL_OIDC_CLIENT_ID` and `PURL_OIDC_CLIENT_SECRET` were unconfigured. `guest_available:true` exposed the explicit unverified preview flow. The managed environment had current observations, enforced unrestricted HTTP policy and no secret bindings, runtime variables or outbound identities. Proxy and TLS verification were preserved.

Supported preview sequence:

1. GET `/api/identity/config`, retaining its bootstrap cookie and bound CSRF value privately.
2. POST `/api/identity/guest` using matching Origin, bootstrap cookie and `x-csrf-token`.
3. Retain the returned session cookie and session CSRF only in private process memory; GET `/api/identity/me` and inspect scopes.
4. PURL guest scopes include `resources:read` and `resources:write`. Direct CGIT previews include `cgit:read` and `cgit:write`. Guest principals are explicitly unverified.

Guest sessions last **1800 seconds**. No guest refresh, recovery or delegation route was observed; `/api/agents/create` requires a verified human. Public resources remain readable after expiry. A fresh participant must authenticate under their own principal and fork a public SNAD mission using its current `expected_version`. They cannot edit the expired guest owner's original resource. Do not put credentials in URLs, artifacts, exports or logs.

## Native lifecycle

The inspected dependency-free SDK is served at `/sdk/launch.js`, SHA-256 **7e195c72e3db43f52bc1af07a4ec77b491dd2f30d942a3a88fdaa769254893d0**. The package export is `purl/launch`; the package's default client targets a different, older API. The SDK retains cookies/CSRF, rejects cross-origin operations and authenticated redirects, and exposes `preview`, `me`, `createResource`, `inspect` and typed `operation` methods.

There are no separate launch `prepare` or `typecheck` endpoints. Preparation means assembling bounded typed state locally. Compile performs parse, normalization, compositional type, effect and capability checks. GET `/api/compiler` describes a pure POST `/api/compiler` operation; owned `/compile` also persists the compilation.

The actual owned-resource sequence is:

1. POST `/api/resources` with title, `kind:"mission"`, `language:"purl"`, initially private visibility, native source, typed input/output schemas, finite state and declared input/expected tests. The service assigns the resource ID and owner. Read back its manifest and verify ownership.
2. POST `/:id/compile`, then `/:id/build`, each with the latest `expected_version`. Build executes at most 20 declared tests and creates an immutable build. Inspect actual test results; HTTP 200 alone does not mean the build passed.
3. POST `/:id/run` with current version, typed input and integer seed. A successful admission returns HTTP 202 and a durable execution ID. Poll `/:id/executions/:executionId` until terminal status. Inspect artifact and receipt. Worker completion may advance the resource version; GET it again before the next write.
4. POST `/:id/checkpoint` with nonempty summary, evidence references and next operations. Checkpoints explicitly retain `evidence_verified:false`.
5. POST `/:id/publish` with current version and public visibility after a passing build. Read back manifest, continuity, release and replay anonymously. Every persisted write must have a read-back. A conflict requires reinspection; do not guess versions.

Paths after the initial create are under `/api/resources`. `Idempotency-Key` binds path and exact payload; keys are 1–128 characters. Native operations are `source`, `compile`, `build`, `run`, `publish`, `checkpoint`, `fork`, `propose`, `commit`. Source changes invalidate the active build. State-only updates also need a new run to publish current-state execution evidence. Only the owner can mutate the resource or decide proposals. Proposal access is scoped even for public resources.

[live-session.mjs](../scripts/integrations/live-session.mjs) implements this procedure using the downloaded, checksum-verified SDK. It keeps credentials in process memory and saves sanitized evidence. Start with inherited proxy/CA settings:

```sh
NODE_USE_ENV_PROXY=1 node scripts/integrations/live-session.mjs
```

Send a JSON line with `{"op":"initialize","stateFile":"scripts/integrations/initial-mission-state.json"}` to create a distinct mission, or use `update` in that same live process with a new state file. Initialization is a real remote write and public publication; run it only for an authorized independent mission. It never targets the prior mission. `inspect` and `cgitCommit` are additional explicit commands. Closing the process loses its preview credentials by design.

The SNAD native source is **`input json`**. Its declared test and worker execution prove typed JSON transport, immutable artifact creation and replay. They do not run SNAD's attribution algorithms remotely. Scientific tests and corpus results are standalone artifacts with their own evidence.

## Limits that affect package design

| Surface | Observed or source-confirmed bound |
| --- | --- |
| Native source, state, run input, artifact | 65,536 bytes each |
| Resource history | 200 versions; export or fork before exhaustion |
| Declared tests | 20; 65,536 serialized bytes total; cost × test count ≤50,000 |
| Checkpoint | 32,768 bytes; summary 1–6000 characters |
| Stored row / owner scope | 262,144 bytes / 10 MiB; 4096 records |
| HTTP default body / mutation rate | 262,144 bytes / 120 per minute per actor or address |
| Product schemas | Bounded JSON Schema subset; `$ref` and `pattern` rejected |
| Native execution | Closed pure interpreter; authored JS/TS disabled |
| Proposals | 200 per resource, 20 per actor |

The whole 6236-ayah corpus does not belong in one PURL state object. Publish portable files and their hashes, then reference their actual retrievable locations. Resource snapshots and repeated execution history also consume the shared owner quota. A native `mission.inspect` operator separately caps objective graphs at 256 nodes; it treats recorded status as claims. SNAD's current source uses identity transport instead.

## CGIT and ACSP compatibility

CGIT is an independent content-addressed artifact product, **not Git wire protocol**. Direct CGIT preview provides separate product consent; PURL-side integration instead requires explicit `/api/identity/activate` `{product:"cgit",consent:true}` and a validated scoped grant. Reusing a PURL cookie on a different origin is not supported.

Supported repository/artifact operations:

| Request | Body / result |
| --- | --- |
| GET `/api/cgit/repos` | Owned repositories |
| POST `/api/cgit/repos/create` | `{name}` → repository with `branches.main:null` |
| GET `/api/cgit/repos/:id` | Repository, head, artifacts and resume cursor |
| POST `/api/cgit/repos/:id/commit` | `{branch,expectedHead,message,artifacts:[{path,type,content,provenance}]}` |
| POST `/:id/branch`, `/:id/release`, `/:id/fork` | Branch/release names and exact SHA-256 commit references |
| GET `/:id/export` | `cgit-export/1` content-hashed snapshot |
| POST `/api/cgit/import` | Validated owner-matching snapshot |
| POST `/api/cgit/github/index` | Read-only public GitHub `{url,ref?}` lens pinned to actual upstream SHA |

Repository limits: 20 repositories, 180 immutable objects each, 128 tree paths, 12 artifacts per commit, 200 KiB content per artifact, 32 branches/releases. Types are code, conversation, research, proof, program, decision, trace and checkpoint. Conversation artifacts require explicit consent. Imports allow 8 MiB; artifact commit HTTP bodies allow 3 MiB. Shared owner quotas remain stricter aggregate bounds. Commits enforce exact `expectedHead` CAS; content hashes are SHA-256 and differ from Git commit identities.

All observed CGIT repositories are owner-scoped; no public publication endpoint was found. A CGIT export copied into the portable package can survive guest expiry. A private CGIT URL alone cannot serve an anonymous fresh-context participant. No private transcript or token is sent to CGIT.

The initial real artifact backup uses repository `bc38de95-d5d6-4e40-a56f-ac60a292e989`, SHA-256 commit `7ea2c06c9bb83aa6da050a5c36756352a3d4c39be08201bf941bdf3736152793`, with four code/schema/docs/discovery artifacts. Its [export](../evidence/purl-live/cgit-export.json) and [persistence summary](../evidence/purl-live/cgit-summary.json) are portable. The standalone [export verifier](../scripts/integrations/verify-cgit-export.mjs) independently checked wrapper, blobs, commits, parents, tree references and branch heads; a tampered export was rejected. Run `node scripts/integrations/verify-cgit-export.mjs evidence/purl-live/cgit-export.json`. Hash integrity grants no ownership transfer: the observed remote importer requires snapshot ownership to match the authenticated principal.

ACSP continuity, authority, proposal and checkpoint concepts are present in the native resource lifecycle. This PURL-focused inspection did not establish a separate ACSP launch package. A subsequent independent [ACSP audit](acsp.md) identified the actual ACSP/0.1 source and live schemas at `acsp-one.vercel.app`. SNAD includes an [offline proposal builder](../scripts/integrations/acsp.mjs) and unsubmitted schema-checked example; no remote ACSP acceptance or mutation is claimed. Imported research terminology is a candidate foundation, not proof of mathematical laws.

## Offline publication and fresh-context procedure

The portable mission package is authoritative when credentials, networking or hosting fail. Retain its manifest, schema versions, byte hashes, exact source commits, artifacts, tests, blockers and permitted next operations. Verify hashes before running code. Publish that package through an actually available host; never record a planned URL as live.

For later native publication, inspect current discovery/runtime/contracts again, authenticate through a supported flow, create a distinct private mission (or fork the public SNAD continuation), insert only public state and artifact references, then compile/build/run/checkpoint/publish with read-back after each transition. Preserve an old published mission as historical evidence if its preview owner expires. A new scoped mission can link that checkpoint without claiming its identity.

The fresh participant should receive only the actual new mission PURL or explicit offline package location. They must reconstruct objective graph, code location, artifacts, hashes, evidence status and blockers, then identify a permitted operation. Reading is always permitted on a public resource. Mutation requires a newly authenticated owned fork; public reading never transfers ownership. Record inaccessible artifacts and failed reconstruction steps alongside successful checks.
