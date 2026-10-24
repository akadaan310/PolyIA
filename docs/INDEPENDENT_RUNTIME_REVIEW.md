# Independent runtime review

**Review date:** 2026-10-24.  
**Reviewer:** independent_runtime_review, dispatched separately from the runtime and interface implementers.  
**Review phase:** pre-remediation review of the integrated bootstrap.  
**Verdict:** **CHANGES REQUIRED** before claiming that the delivered bootstrap meets all of its stated integrity, resource-bound and source-linkage guarantees. The findings below concern the reviewed implementation; this document does not attest that later fixes have passed. The coordinator began addressing the arithmetic admission finding while this report was being completed.

The runtime is a real implementation: it commits SQLite events, receipts, immutable artifact bytes and materialized state; it does not merely set presentation badges. Its restricted experiment registry executes exact arithmetic without model inference. The current default registry contains **194 requirements: 192 full-commission obligations with the unsupported `commission-evidence` verifier, plus BOOT-001 and BOOT-002**. Full mission status remains `NOT_COMMISSIONED`. This is an important, correctly preserved limit on the package's claims.

## Scope and evidence standard

Reviewed `docs/APPROVED_DESIGN.md`, `docs/BOOTSTRAP_RUNTIME.md`, the relevant registry obligations, `polyia/store.py`, `polyia/cli.py`, `polyia/experiments.py`, `polyia/server.py`, related test implementations, `evidence/runtime-development.json`, and `docs/SCIENCE_AUTHOR_REPORT.md`. The interface assets and final source manifest were still being assembled. This review does not certify their final state, full source custody, remote deployment, performance under production load, or the scientific correctness of the inherited corpus.

The prior development report records an 84-test passing integration run. That report is **inherited development evidence**, not an independent rerun by this reviewer. To avoid repeating the same test suite, the reviewer executed only small reproductions of concrete concerns, using disposable SQLite databases and temporary workspace files. No implementation files, existing databases, upstream repositories or packages were changed. The arithmetic probe used `1e100000`, not an input large enough to threaten the host.

Function names below are the stable locators; line numbers describe the pre-remediation code and may move as fixes land.

## Findings

| ID | Severity | Area | Finding |
| --- | --- | --- | --- |
| IRR-01 | High | `store.Ledger._verify_locked` | Loose Python equality accepts changed JSON scalar types, allowing a corrupt materialization to pass verification and a subsequent command to commit a broken chain. |
| IRR-02 | High | `experiments.number` | The exact-number budget is enforced after `Fraction` constructs unbounded exponent values. |
| IRR-03 | High, specification gap | `store._definitions`, genesis and checkpoints | Checkpoints bind event history and produced artifacts but omit the active source manifest, complete constitution metadata and policy context. |
| IRR-04 | Medium | `store.Ledger._run_verifier` | Scientific acceptance names produced files as inputs but never binds their content to the code or report actually checked. |

### IRR-01 — Scalar type changes bypass integrity comparisons

**Locations:** `polyia/store.py`, `_verify_locked`, approximately lines 780–783, 802–805 and 811–816. `get_command` and the retry path return the stored receipt after these comparisons pass.

The materialized state comparison uses decoded Python dictionary equality. Python regards `5 == 5.0` and `True == 1` as equal, whereas the runtime's canonical JSON and hash function distinguish these values. The code compares the recorded materialized hash with the replayed state's hash, but does not recompute the hash of the actual decoded `state_json` being returned by `state()`.

**Reproduction, without recomputing any digest:**

1. Initialize a fresh ledger containing one requirement, whose default priority is integer `5`.
2. Change only `materialized.state_json` so that this priority is JSON `5.0`; leave `state_hash`, genesis and the journal unchanged.
3. `verify()` returns `ok: true`; `state()` returns a Python float for the priority.
4. Submit an ordinary revision-0 `checkpoint.create` command. It returns `ok: true` and commits revision 1.
5. `verify()` now fails with `Before-state digest mismatch at 1`.

This is more serious than detecting a formatting difference. A successful integrity check admits a corrupted in-memory starting state; a legitimate next command then makes the stored journal unreplayable. It does **not** require the administrator-level operation of replacing a database and recomputing its entire hash chain, which the documentation appropriately excludes from the threat model.

A second reproduction changed only a committed `receipt_json` from `ok: true, revision: 1` to `ok: 1, revision: 1.0`. Verification still passed, and retry returned the altered integer/float receipt. Thus the exact-original-receipt guarantee also has a demonstrated exception. Checkpoint state comparison uses the same weak equality pattern.

**Required fix:** compare canonical JSON values in a type-preserving way, and recompute the hash of the decoded materialized state and checkpoint state actually stored. Apply the same strict comparison to recorded requests, receipts, checkpoint metadata and configuration comparisons where JSON type identity matters. Preserve the existing rule that verification diagnoses corruption without repairing it.

**Focused regression evidence needed:** mutate integer↔float and boolean↔integer values separately in materialization, receipts, checkpoint state and stored request JSON. Each inconsistent record must fail verification and reopening. A subsequent command must be refused before advancing revision. A normal identical retry must continue returning the exact original receipt.

### IRR-02 — Rational parsing occurs before its resource guard

**Location:** `polyia/experiments.py`, `number`, pre-remediation lines 37–44. This is reached by polynomial coefficients and Q-path supplied values.

The parser permits any string of at most 128 characters and then calls `Fraction(value)`. `bounded()` checks the resulting numerator and denominator afterward. A short exponent string can therefore request an enormous power of ten before the claimed 1024-bit limit is checked. The ledger's outer parameter string and request byte budgets do not prevent this.

**Controlled reproduction:** instrumenting the `Fraction` boundary while using its real implementation showed that `"1e100000"` first constructed a numerator with **332,193 bits**, then returned the `BUDGET` refusal. This establishes that admission occurs too late. Much larger exponent strings remain small HTTP inputs. In the ledger path, parsing happens while the writer transaction and ledger lock are held, making the resource exposure relevant to other commands as well as the requesting run.

**Required fix:** validate syntax and size before invoking a numeric constructor that can expand exponents. A small exact integer/ratio-string grammar is sufficient for the documented seed contract. If decimal or exponent notation is retained, preflight its exponent and predicted numerator/denominator size first. For direct Python integer inputs, inspect `bit_length()` before decimal conversion so Python's string-conversion limit does not turn a budget refusal into an unexpected exception.

**Focused regression evidence needed:** an exponent input must be refused while a fault sentinel proves the `Fraction` constructor was not reached. Large direct integer input must yield a typed budget refusal before `str()` conversion. Existing exact integer/ratio inputs and the default acceptance family must still pass.

This finding concerns resource admission, not an incorrect accepted algebraic identity. The coordinator reported beginning this fix before the review concluded; fresh regression evidence is required to close it.

### IRR-03 — Checkpoints do not retain the promised source and obligation context

**Locations:** `polyia/store.py`, `_definitions` around line 111; initialization around lines 210–216; `checkpoint.create` around lines 519–523; checkpoint insertion around lines 413–415; `get_checkpoint` around lines 325–331.

The checkpoint correctly retains its event head, reducer state, artifact descriptors and previous checkpoint ID. However, `_definitions` discards every requirement field except `id`, `title` and `verifier`. In particular, the actual constitution's `mandate`, `acceptance`, `source_refs`, `continuity`, `authority` and `scope` are lost before genesis is created. Neither genesis nor checkpoint creation captures an active source manifest, the complete constitution document, governing policy revisions or a source-context descriptor.

**Reproduction:** create a requirement with `scope`, `acceptance`, `source_refs` and `authority`, produce evidence, and checkpoint it. The returned snapshot contains none of those fields. Its top-level keys are only `id`, `revision`, `head`, `state`, `state_hash`, and `previous_id`; the checkpoint event result contains only `checkpoint_id` and `previous_id`. A fresh reader cannot reconstruct the omitted obligation and source context from those retained bytes.

This is a concrete gap against the approved source-linked-snapshot deliverable and the precise definition in **PIA-020, “Source-linked checkpoints”**: bind the active source manifest, constitution and policy revisions together with state, artifacts, guidance and execution context. The existing test named `test_checkpoint_is_source_linked_and_tampering_is_detected` checks an event head and a produced artifact hash, which is valuable but does not test this stronger requirement.

**Required fix:** preserve the requirement metadata needed to interpret scope, authority and acceptance; capture bounded source-manifest, constitution and policy context as immutable bytes or explicitly versioned content-addressed objects; and include their identities in genesis/checkpoint state and hashes. Retain historical context when live files change. If an expected context item is missing, surface a named incomplete-context condition rather than claiming that a fully source-linked checkpoint exists. Keep runtime credentials and secrets outside the captured context.

The manifest can identify the complete package source set without embedding every large corpus file into every checkpoint. Its retained bytes must nevertheless resolve to a clear versioned package/source inventory. An event head alone is not a substitute for that binding.

**Focused regression evidence needed:** checkpoint, change live constitution/manifest/policy, and prove that the old checkpoint still resolves its original bytes and metadata. Corrupt or remove one captured context object and require verification to fail. Test explicit missing context and ensure full mission status remains uncommissioned.

### IRR-04 — Scientific acceptance is detached from produced artifacts

**Location:** `polyia/store.py`, `_run_verifier`, around lines 590–611, especially construction of `inputs` from artifact descriptors and execution of `run_registered("acceptance", {})`.

`scientific-contracts` checks that arbitrary produced blobs are intact, then runs the currently installed acceptance suite without reading those blobs as scientific input or comparing them with the executing code. It records the arbitrary artifact descriptors under `inputs` even though changing their content cannot affect the scientific result.

**Reproduction:** a fresh BOOT-002 requirement was produced from `irrelevant.txt`, containing only an unrelated 72-byte note. Verification returned `PASS`, reported that text file as its input, and `requirement.accept` changed the requirement to `ACCEPTED`. The ledger still verified successfully.

This is **not** evidence of a forged theorem or blanket commission acceptance. The installed kernels really ran, BOOT-002 is explicitly a kernel-contract requirement, and the documentation limits the verifier's meaning. The narrower defect is that the produce→verify→accept workflow does not establish a coherent relationship between the produced deliverable and the scientific check, despite advertising those files as verification inputs.

**Required fix:** bind scientific verification to a captured identity of the registered implementation actually checked, and distinguish those checked inputs from ancillary attachments. One workable bootstrap rule is to require captured `polyia/experiments.py` bytes whose digest matches the pinned executing kernel, optionally together with a strictly linked generated run receipt. Another is to have the verifier capture its own complete implementation/input/report evidence bundle, with clear source identities. Do not treat an uploaded report's self-declared PASS field as authority.

When implementing this binding, avoid assuming that hashing the current module file alone always identifies already-loaded Python code: a source-file edit during a long-running process can leave cached code executing. Pin the running implementation identity or require a restart/refuse a changed implementation before accepting new evidence.

**Focused regression evidence needed:** unrelated text, an altered implementation copy and a mismatched generated run receipt cannot satisfy the scientific production contract. A valid captured implementation/report path passes, records the exact evidence roles and digest identities, and remains replayable without re-executing science. Failed linkage must not change the requirement to VERIFIED or ACCEPTED.

## Contract assessment outside the findings

| Contract | Reviewed assessment |
| --- | --- |
| Durable event history | Real SQLite transaction design, WAL/FULL settings, complete requests/results and state hashes. IRR-01 must be fixed before its corruption-detection claims hold. |
| Idempotency and revisions | Actor-scoped request digest; exact retries checked before the stale revision guard; changed request reuse rejected. Serialized mutation prevents two writers accepting one revision. Stored receipt type identity needs IRR-01. |
| Produce / verify / accept | Captures actual immutable bytes, rejects unsafe paths and empty evidence, resets acceptance after reproduction, and refuses unsupported verifiers. Scientific attachment linkage needs IRR-04. |
| Acknowledged / applied guidance | Separate transitions, explicit actor/revision/effects, registered actions only, no free-text interpretation. Text-only guidance cannot become APPLIED. |
| Checkpoint history | Real append-only application snapshots with event/head/parent linkage. Complete source context needs IRR-03. |
| Replay and side effects | Reducer consumes recorded results and does not call experiments, network or subprocess execution. Existing replay-sentinel tests exercise the right property. |
| HTTP authority | Private routes require bearer authentication; read token cannot mutate; operator identity is server assigned; Host and Origin checks are explicit; loopback binding enforced. No concrete authority bypass was found in this review. |
| Exact polynomial science | Coefficient identities use rational arithmetic, enforce nonzero polynomial divisor, retain rational-function domain exclusions, and distinguish a fixed factorization example from a general solver. Resource admission needs IRR-02. |
| Grammar promotion | Preserves canonical expansion and finite tuple-of-symbol denotation with explicit finite scope and loss declaration. It does not claim general grammar equivalence. |
| Q-path science | Requires both named inputs, fresh outputs, matching Rational/Q contexts and nonzero divisor; records exact arithmetic witnesses. It does not conflate a lone incoming arc with a satisfied joint premise. |
| No-LLM execution | Reviewed registered runtime paths contain no model client, network inference, generated-code evaluation or caller-selected dynamic module execution. Optional external environments remain outside this assertion. |
| Completion honesty | Default full obligations remain unsupported and `NOT_COMMISSIONED`; kernel PASS, committed receipt success and full commission completion remain distinct. |

## Release follow-up

Resolve IRR-01 through IRR-04, add the narrow regression checks described above, and then run the coordinator's final integrated suite against the delivered files. Record exact fresh results and source identities in release evidence. Preserve this pre-remediation report and append a dated disposition for each finding rather than silently replacing the original observations with a blanket passing verdict.

An eventual passing bootstrap review must remain scoped to these implemented local contracts. It cannot certify the 192 full mission obligations, production operations, remote deployment or every inherited scientific claim.
