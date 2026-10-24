# First mission acceptance adapter

`commission-evidence` dispatches only PIA-042 to the fixed
`PIA-042/capture-v1` adapter. Every other mission requirement remains unsupported.
This does not change schema 2, the genesis requirement definitions, historical
source-context capture, existing execution bundles or `NOT_COMMISSIONED` status.
No mission requirement is automatically produced, verified or accepted.

## Candidate and invocation

Produce exactly these four paths, containing the bytes of the installed package:

```
polyia/__init__.py
polyia/store.py
polyia/experiments.py
polyia/mission_verifiers.py
```

The operator stages them beneath the configured artifact workspace, then submits
the ordinary `requirement.produce`, `requirement.verify` and
`requirement.accept` commands for `PIA-042`, each using its current revision and
distinct stable command ID. VERIFY accepts only `requirement_id`; it accepts no
caller descriptor, report, command, pass flag, dependency path or executable code.
Extra artifacts and missing or mismatched source files refuse verification.

These sources are the implementation under test, not evidence that merely
exists. The adapter compares their captured bytes with the installed source and
binds the actual loaded functions, defaults, declared policies and import aliases.
The scientific dependency retains its existing loaded-code pinning contract.
Compilation for identity comparison does not execute captured or installed source.

## Exact obligation and source binding

The adapter supports one exact immutable PIA-042 definition and acceptance row,
identified by canonical JSON hashes in its source. It also pins the complete
current acceptance, core-inheritance and supplemental-inheritance registry byte
hashes. It reads all 252 core records and 3,706 supplemental records and selects
records targeting PIA-042. Both applicable sets are empty in this version. It
does not infer applicability from filenames or omit inherited records by sampling.

A generated contract blob retains the exact definition, acceptance row,
applicability method/results/counts and the registry byte identities. The receipt
binds this blob, the source-context digest, producer, production revision,
captured artifact identities and the loaded implementation bundle. This is a
new versioned receipt field; historical context and bundle definitions are not
expanded retroactively. Full inherited registry bytes remain in the preserved
release package; their identities and applicable subset are retained in the blob.

A registry change, even an unrelated formatting change, requires deliberate
review and a new supported adapter contract. It cannot silently broaden the
accepted scope. ACCEPT repeats input, loaded implementation and contract binding;
it does not rerun the fixtures. A changed source-context checkpoint likewise
requires fresh verification before acceptance.

## Fresh conformance experiment

Each VERIFY creates private temporary SQLite stores and fixture files. The
production ledger is used only to read its immutable inputs and to commit the
verification receipt and generated contract blob. Fixture commands cannot target
the production database. The finite experiment checks:

- Actual captured bytes, path, size, digest, production revision, producer and
  requirement semantic scope/version.
- Changed and missing workspace files are reported as drift while original
  evidence remains resolvable, including after close/reopen.
- Explicit reproduction creates a different candidate and removes its previous
  current verification/acceptance; historical accepted checkpoints and blobs stay
  resolvable.
- Stale acceptance, caller-supplied PASS, empty and missing files, symlink escape,
  path traversal and oversize capture are refused without changing accepted state.
- A failed multi-file capture rolls back; corrupt captured bytes fail integrity
  checks and prevent reopen.

The fixture has a fixed number of commands and files, bounded input bytes, one
sparse oversize-file negative control, no subprocess/tool/network execution and
no user-directed loops. Temporary files are removed on completion. The operation
runs synchronously inside the existing command transaction; it holds the writer
lock while checking. It does not claim an operating-system-enforced CPU deadline
or protection against a failed filesystem/interpreter hanging the process.

Successful evidence is `SOFTWARE_CONFORMANCE`: finite checks of this exact
implementation and contract on the observed Python/SQLite/POSIX environment.
It does not establish scientific truth of arbitrary captured content, all crash
schedules, all filesystems, deployment readiness or any other mission obligation.
The interpreter, standard library, installed verifier and privileged host remain
trusted. A privileged administrator able to replace code and recompute an entire
ledger is outside the hash-chain assurance boundary.

## Replay and validation

Replay validates retained binding structure, production identities, contract and
implementation blob hashes, and report consistency. It never imports the mission
adapter, reads current acceptance registries, pins current implementation or reruns
fixtures. Accepted historical evidence therefore survives later implementation
changes. New acceptance still requires the current supported binding.

`tests/test_mission_verifiers.py` exercises real produce/verify/accept/reopen,
unrelated and forged submissions, missing/changed dependencies, source and registry
drift, loaded-runner/policy replacement, corrupt retained contract bytes and stale
acceptance after reproduction. An isolated package with a deliberately broken
drift implementation demonstrates a real failed check rather than a pass inferred
from fixture file existence. These checks are independent of live service state.
