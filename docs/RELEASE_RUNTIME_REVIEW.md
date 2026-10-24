# Release runtime review — remediation closure

**Date:** 24 October 2026. **Reviewer:** `release_runtime_review`, separate from the runtime, interface and scientific implementers. **Reviewed runtime:** 1.1.0, ledger schema 2.

**Verdict: PASS for the scoped bootstrap remediation review.** All four findings in the preserved [pre-remediation report](INDEPENDENT_RUNTIME_REVIEW.md) are closed for the reviewed code. No new release blocker was found within this scope. This report does not replace the coordinator's final integrated tests, source-custody verification or release manifest.

The reviewer executed **17 independent probe groups** and **four selected repository regression tests**. All passed. The probes used actual disposable SQLite files, captured source bytes, separate Python processes and deliberately corrupted records. They did not modify package runtime code, package tests, upstream repositories or an existing user ledger. The numerical refusal probes used constructor sentinels rather than allocating dangerous exponent values. Exact outputs, reviewed file hashes, environment versions and the principal independent probe program are retained in [release-review.json](../evidence/release-review.json).

## Finding dispositions

| Finding | Disposition | Fresh evidence |
| --- | --- | --- |
| IRR-01: JSON scalar type changes bypassed integrity checks | Closed | Seven independent mutations of materialization, stored requests, receipts and checkpoints were detected. Each blocked the next command before revision advancement and refused reopening. Exact ordinary retry still passed its selected regression. |
| IRR-02: rational parsing expanded exponent strings before resource admission | Closed | Exponent, decimal and underscore strings were refused before `Fraction` was called. A 20,001-bit integer was refused before construction/conversion. Ordinary exact rational inputs and all 12 registered acceptance checks still passed. |
| IRR-03: genesis/checkpoints omitted complete obligation and source context | Closed | Complete metadata survived restart. Two source-context versions retained distinct constitution, manifest and authority bytes. Historical replay did not reread live source files. Deleting an old authority object invalidated verification, commands and reopening. The default 194-requirement ledger captured 11 context objects with `SOURCED` and `MATCH`. |
| IRR-04: scientific verification accepted unrelated produced files | Closed | An unrelated note and altered kernel copy failed. A type-altered run record failed linkage. Exact kernel bytes plus a real committed run passed, with checked and ancillary roles distinguished. Source, loaded-code, constant and default mismatches were refused. Replay did not reexecute science. |

## 1. Type-preserving ledger integrity

The reviewed code compares canonical JSON through `_same_json`; it also recomputes the hash of the materialized and checkpoint state actually stored. Receipts are checked against the replayed event, and stored requests are checked against both their own digest and the original request. The former Python equality exception for `true`, `1` and `1.0` no longer admits the tested changes.

The independent probes changed an integer priority to a float, a boolean pause flag to an integer, a receipt's success flag to an integer, a receipt revision to a float, a stored request revision to a boolean or float, and a checkpoint priority to a float. These changes did not include recomputing any digest. Every changed ledger returned failed verification, refused a subsequent checkpoint with `INTEGRITY_ERROR`, retained its prior revision and refused reopening. The selected exact-retry regression continued to return the original receipt and reject changed reuse.

This establishes the repaired consistency boundary. It does not turn a hash chain into an externally anchored signature or prevent a sufficiently privileged administrator from replacing the entire database and recomputing every record.

## 2. Numerical admission before construction

`experiments.number` now admits only exact integer inputs and bounded integer/ratio strings. It checks a direct integer's bit length before construction and rejects unsupported string syntax before calling `Fraction`. The independent probes used `1e100000`, `1e999999999`, `1.25` and `1_000` with a sentinel that would raise if the constructor was reached. All four produced `INVALID_RATIONAL`, with zero constructor calls. An integer with 20,001 bits produced `BUDGET` with zero constructor calls.

The valid input `3/5`, a negative integer and the registered acceptance family passed. Thus the repaired admission does not obtain a refusal result only after creating the formerly unbounded intermediate. The result remains scoped to the bounded arithmetic grammar and registered kernels in this package.

## 3. Source-linked context and historical interpretation

Genesis now retains complete JSON requirement definitions. The source-context objects include the constitution, source manifest, authority, available repository pins and inherited obligations, plus the fixed runtime source files. Context records retain exact byte digests, version, capture revision, execution environment, manifest identity and the relationship between the captured constitution and the original genesis definitions. The fixed context allowlist excludes runtime credentials.

The independent history probe initialized explicit requirements with mandate, acceptance, scope, authority, source references and continuity metadata. It checkpointed them, then changed the live constitution, manifest and authority. The second checkpoint retained the new context bytes while the original checkpoint continued to resolve the previous bytes. The runtime correctly kept the original requirement definitions and reported the new constitution binding as `DIFFERENT`; it did not silently rewrite history.

Reopening under a sentinel that forbade source recapture succeeded, proving that this historical reconstruction consumed retained bytes. Deleting the authority object used by the earlier context caused verification and reopening to fail even though a later authority version existed. A separate default initialization bound the actual package registry to all 194 requirements. A custom ledger without its own registries remained explicitly `UNSOURCED`.

`SOURCED` describes the available captured control context. It does not mean that every external corpus byte was copied into the database, every scientific claim was proved or a changed constitution was automatically adopted. Corpus custody remains separately verifiable through the retained manifest and package files.

## 4. Scientific production and executing-code identity

The repaired scientific verifier requires captured bytes whose digest matches the pinned registered kernel. It never executes an uploaded Python file. Additional reports that claim to be scientific run evidence must exactly match a committed acceptance run or its full command receipt. Files that establish no scientific result are labelled ancillary.

The independent probe first produced an unrelated note and observed a retained `FAIL` with `PRODUCED_KERNEL_MISMATCH`; acceptance was refused. A modified kernel copy also failed. Next it produced the exact kernel with a run whose revision had been changed from integer to float. This failed with `UNLINKED_RUN_RECEIPT`. Finally, the exact kernel and genuine run passed, with `executing-kernel` and `recorded-run` roles. The unrelated note remained visibly ancillary. Reopening with a sentinel forbidding scientific execution replayed the accepted snapshot successfully.

The source pin now compares the already-loaded function code, positional/keyword defaults and module literal constants with the fixed installed source. It compiles that source only to construct a comparison object; the comparison object is never executed. The reviewer independently verified two default mismatch cases: changing the on-disk default after import but before the first pin, and changing the loaded function's default while leaving its source intact. Both were refused with `IMPLEMENTATION_CHANGED`.

The final selected regression run also passed the source-edit-after-pin, cached-constant-before-pin, cached-default-before-pin and exact-retry cases. This is an identity check for the registered kernel, not a general Python sandbox or a proof about arbitrary future modules and plugins.

## 5. Additional review and release boundary

The reviewer inspected the backup helper's read-only source opening, exclusive destination creation and explicit connection closing. No additional blocker was found in that inspection; the coordinator owns the final backup/restore demonstration. The no-LLM audit accurately limits its assertion to static bootstrap dependencies and intercepted execution of the registered exact kernels. It does not claim that a static scan proves all future extensions free of inference.

The review ran on Python **3.12.14** with SQLite **3.53.1**. The exact final file digests are in the evidence record. The main reviewed identities are:

- `polyia/store.py`: `dc88ea766ab2afe4f5426c00e729d228b656f6856f387f838a18d75a5749509a`
- `polyia/experiments.py`: `6b93831fb35876b519fc169cc39d8eb9e072ce5dfade167310bc8640231a6809`

No public URL, Oracle deployment, real-browser rendering, full scientific corpus validation, production load test or complete Poly IA application is certified by this review. The full mission remains **NOT_COMMISSIONED**. The coordinator must bind this review and its fresh integrated verification to the exact delivered release manifest before representing the package as verified.
