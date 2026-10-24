# Versioned mission acceptance adapters

`commission-evidence` dispatches PIA-042 to `PIA-042/capture-v1` and PIA-040 to
`PIA-040/guidance-effects-v1`. Every other mission requirement remains unsupported.
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
`requirement.accept` commands for the supported requirement, each using its current revision and
distinct stable command ID. VERIFY accepts only `requirement_id`; it accepts no
caller descriptor, report, command, pass flag, dependency path or executable code.
Extra artifacts and missing or mismatched source files refuse verification.

These sources are the implementation under test, not evidence that merely
exists. The adapter compares their captured bytes with the installed source and
binds the actual loaded functions, defaults, declared policies and import aliases.
The scientific dependency retains its existing loaded-code pinning contract.
Compilation for identity comparison does not execute captured or installed source.

## Exact obligation and source binding

The capture adapter supports one exact immutable PIA-042 definition and acceptance row,
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

## PIA-040: applied guidance and actual effects

The added adapter implements the exact PIA-040 mandate in `GOD_SEED.md`:
only an acknowledged, admitted typed action may apply; its exact effects and
applied revision must be retained; acknowledging text does not execute it.
Its definition of done requires real priority, pause and resume effects and
separate ACKNOWLEDGED/APPLIED receipts. This adapter does not also certify
PIA-038/039/041, HTTP behavior, browser rendering or Codex's polling workflow.

The independent fixture driver uses literal expected priorities, pause flags,
effect paths and revision relationships. It submits actual commands to two
connections of a temporary ledger; it does not use the production reducer to
compute its expected answers. It verifies:

- Submission and acknowledgement do not apply an action; applying priority
  changes 5 to 7 with the exact effect record, actor and revision.
- Exact retries return the original receipt without applying twice. New apply
  commands for applied, unacknowledged, deferred or rejected guidance refuse.
- Acknowledged free text cannot execute; unregistered export effects, mismatched
  targets, boolean priorities and read-scope mutations refuse.
- Pause changes actual state and blocks an actual registered polynomial run;
  restart preserves that pause, guidance history and checkpoint. Resume changes
  state back and permits a fresh successful computation.
- Two simultaneous connections apply competing acknowledged priorities at the
  same revision. Exactly one commits, the other gets a revision conflict, and
  the winning receipt matches the observed priority. The complete history verifies.

Each normal run performs 21 named checks. The driver uses two threads with a
five-second barrier timeout and bounded joins; the store retains its SQLite
busy timeout. These finite controls are not an operating-system-enforced deadline.
Only the disposable ledger is exercised. The caller's guidance, pause state and
experiment history remain unchanged by verification.

### Inherited applicability remains explicit

PIA-040 has no mapped core clauses. Its 75 supplemental records comprise
64 `scoped_to_upstream`, eight `retained` and three `refined` dispositions.
Unlike PIA-042, this is not an empty applicability set. Every record, complete
verbatim text, original disposition and locator is retained in the contract blob,
alongside a per-record classification and rationale. Before verification and
acceptance, the adapter checks all mapped byte spans and text hashes against
their 33 actual source files and checks those files' full recorded hashes.

The two directly exercised integrated conditions are:

- `SUP-9e3a285a12be4eb4-00000a12`: the versioned application boundary, exercised
  through revision guards, actor scope and repeat-safe commands.
- `SUP-48c38a2a24128513-00000a8a`: explicit stateful lifecycle effects,
  concurrency and replay. ABI/WIT composition is not claimed by these actions.

Other integrated records preserve PHONEX export/rights and language-object
contracts, typed pack joins, mathematical structure conditions, QIA historical
test accounts, Arabic authored examples, Grammar in Ciphers source/campus scope
and DK0 ontology conditions. Priority and research pause/resume do not construct,
export or certify those objects. The classifier names each conditional capability
or historical claim explicitly; it does not mark those broader duties complete.

Upstream records retain their own enforcement scopes. CIA Browser frame epochs,
tab consent and broker HOLD, PURL endpoint/header/error semantics, SNAD ACSP
publication, DARK physical actions, Astra device gates and the other upstream
products are not exercised by this local guidance action set. Their exact clauses
remain conditions of those adapters/products. This follows the supplemental
registry's mapping policy; no general upstream acceptance waiver is introduced.

The binding remains versioned per adapter. Adding PIA-040 leaves the original
PIA-042 contract shape, requirement identity, applicability interpretation and
receipt replay rules intact. Historical PIA-042 receipts resolve their retained
contract/source bytes; they do not acquire the new guidance checks. New acceptance
for either adapter still checks the current implementation and its exact contract.

Regression controls run isolated, coherent copies of the package with the
acknowledgement guard or research-pause guard deliberately removed. The fresh
driver must fail the corresponding behavioral check. Other tests cover changed
inherited source bytes, stale acceptance after reproduction, current-candidate
acceptance and nonexecuting replay. Historical source-reported tests contribute
no fresh-pass count.
