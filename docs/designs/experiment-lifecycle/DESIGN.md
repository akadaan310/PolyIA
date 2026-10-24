# D-EXPERIMENTS: source audit and next implementation design

Status: DESIGN_ONLY. Implementation was authorized after release 1.4, then paused at the owner-requested safe checkpoint before any lifecycle code or tests were written. No queue, lifecycle, worker unit, ledger migration or acceptance
has been implemented by this document. Current deployed ledger/release remains
unchanged. Start code only after the coordinator seals the 1.4 increment.

## Source authority and exact coverage

Read GOD_SEED PIA-133–144, the twelve acceptance contracts, D-EXPERIMENTS in
work_contracts, all 41 directly inherited core clauses, the reconciliation rules,
the actual store transaction/replay paths, and the current finite CLI worker.
`source-audit.json` retains their original records and file hashes. It also retains
all 1,707 supplemental records mapped to these requirements; all 121 full source
file hashes and all mapped byte-span/text hashes were checked. Dispositions are
989 scoped_to_upstream, 625 retained, 81 refined, 12 superseded. This is verified
custody, NOT a claim that every upstream condition was individually discharged.
Their complete records remain attached for the later requirement-specific audit.

The critical additional source is UCG Foundations §2: SEAL hashes and appends
predictions before **any witness byte is read**, then WITNESS loads and hashes the
witness, RECOGNISE compares against sealed bytes, and ACCOUNT records both misses
and gaps. Relevant supplemental record: SUP-699d8e6bbb286b41-00000a2a.

| Requirement | Concrete finite prerequisite here | Additional retained conditions still open |
| --- | --- | --- |
| PIA-133 / UCG-027 | Durable guarded phase ordering and a committed seal before access | Actual deployed multi-stage receipts and illegal-sequence negatives; do not replace these with prose stage labels. |
| PIA-134 / UCG-007/028 | Integrate the tested native Bubblewrap boundary with real job input/grant identities | UCG-045 also requires E01: 118/118 period/block, 98/118 configurations and named exceptions. Native file denial alone cannot accept all PIA-134. |
| PIA-135 | Evidence-method registry, dependency relationships, explicit classes, shared-oracle downgrade/refusal | UCG-031 QM9/textbook contradiction audit; UCG-147 test pyramid/mutation threshold; UCG-148 different-party witnesses per pillar. |
| PIA-136 | Exact finite arithmetic verifier with complete domain and nonvacuous controls | Cancellation/domain negatives, no promotion of numerical samples to universal proof; UCG-149 Lean lane and listed laws remain separate. |
| PIA-137 | Recalculable retained comparison rows, misses, extras, contradictions and denominators | UCG-029 held-out witness-informed amendments; E01 exceptions, E02 metrics/bias and E05 study remain their actual scoped studies. |
| PIA-138 | Append-only witness-version correction and affected-run re-evaluation path | Reproduce actual E03 naive_bracelet → polya_vertex_edge correction; also inherited valence/aromaticity conditions. A contrived arithmetic wrong witness is only infrastructure control. |
| PIA-139 | Supervised bounded actual VM worker, queues, leases, quotas, pause, retry/backoff and restart evidence | An observed window must be declared and measured. No source mandates a particular number of minutes/hours, permanent hostname, or proof of indefinite uptime. |
| PIA-140 | One fixed proposal rule linked to a real captured deficit/negative run; explicit bounded design | UCG-112 actual group-gap amendments and UCG-129 mined rule with held-out improvement remain open. Repeating a baseline is not novel proposal generation. |
| PIA-141 | Pinned reproduction as a NEW run and scoped regressions | UCG-040 1,000 deterministic inputs; UCG-152 cross-machine E-experiments and full subject coverage require actual execution. |
| PIA-142 | Retain real process time/CPU/RSS/output and controller/ledger overhead | p50/p95/p99, fair external baselines, end-to-end package costs, slower workloads and specific inherited phonetic/CAS/chemistry/Lean studies remain open. |
| PIA-143 | Immutable failed attempts/counterexamples linked to versions and later responses | Keep old negative query results across corrected releases and prevent re-admission in the same invalid scope; do not universalize finite negatives. |
| PIA-144 | Actual byte-bound stage receipts; admission recomputes consistency/class from retained stages | Missing/tampered/stale/caller-invented evidence refused. Experiment admission is separate from mission acceptance. |

REC-REPLAY means opening/replaying a journal never invokes a generator or witness.
Reproduction is an explicit new experiment identity. REC-WITNESS and
REC-TOOL-ROLES distinguish constructor checks, same-implementation repetition,
different implementations, external empirical witnesses and proofs. An AST/VM
agreement performed inside GENERATE remains a constructor consistency check;
it cannot be relabeled the independent post-seal WITNESS.

## Chosen compatibility approach

Keep SQLite schema 2, existing tables, genesis documents, `_initial_state`, old
event reductions, CONTEXT_CODE and all historical execution-bundle closures
unchanged. Do not create or repair tables silently on open. Add a versioned
`polyia.experiment-lifecycle/0.1` event contract and a lazily introduced
`experiment_service` state projection only when its first authorized new event
occurs. Historical checkpoints and replay states stay byte-identical.

The projection holds the active policy version, bounded jobs/attempts, counters
and recent immutable receipt references; actual outputs/manifests are content
blobs in the existing blob table. The event chain remains authoritative. A
separate mutable sidecar queue is rejected for the first increment because it
would introduce cross-database admission/crash atomicity problems. A future
indexed projection may be added with an explicit migration and replay check.

The current ledger verifies its complete history before every command and keeps
all runs in state. Therefore choose and measure a bounded initial workload; do
not claim high-throughput or indefinite unbounded storage. Initial proposed
policy: one concurrent job, 64 pending jobs, 256 retained job summaries per
policy epoch, 32 cases/job, three attempts/stage, fixed daily execution/storage
quotas. At capacity, stop admission visibly. No implicit pruning, compaction or
deletion. Exact numeric quotas are implementation policy, not inherited facts.

Only short reservation/commit transactions take `BEGIN IMMEDIATE`. Native
execution, witness access and other potentially slow computation occur outside
SQLite transactions. Keeping generation and witness work inside current
`Ledger.command -> _execute` would hold the write lock and cannot establish a
committed SEAL-before-read boundary: do not reuse that synchronous pattern for
the whole lifecycle.

## Identity and API surface

Public commands should propose, cancel and explicitly reproduce fixed designs.
Inputs identify a registered design ID/version, bounded native source/data,
baseline, hypothesis, variation space, source/case identities, witness catalog
ID, budget and admission criterion. There is no caller-provided result, PASS,
witness receipt, executable/module name, mount list or filesystem witness path.

Keep worker phase recording off the public HTTP command surface. A trusted local
controller invokes fixed internal stage methods that run the registered
implementation and commit its actual captured results. An arbitrary operator
command must not be able to fabricate `generated`, `witnessed` or `accepted`
payloads. Local code/ledger owner remains trusted, as in the existing threat
model; private Python method names are not protection against a malicious admin.

Use stable job IDs, attempt IDs, phase names, monotonically increasing fencing
generations, and actor-scoped idempotency IDs. Job uniqueness binds the proposed
design/input/criterion/version identities; explicit reproduction includes its
parent run and a new run ID. Ordinary retry cannot turn into reproduction.
Since existing request hashes include expected_revision, after lost receipt
delivery look up the saved command ID before reconstructing a request. A
revision-conflict retry can use an updated revision only if no receipt exists.

The new modules should be small and separate: lifecycle schemas/reducer/guards,
trusted worker orchestration, fixed witness adapters, and read-only metrics.
Do not put arbitrary scheduler expressions or plugins in a JSON field.

Give the effectful worker its own versioned closed source/runtime binding
contract. Do not make subprocess/filesystem/network imports generally admissible
by loosening the existing pure `_EXTENSION_DEPENDENCIES_V1` verifier. Pin actual
loaded controller functions/policy/defaults against captured source for stage
admission; the standalone isolation report's current source-file hash alone is
explicitly not loaded-code attestation. Constructor modules are pinned before
generation; witness implementation/data bytes are pinned only after seal. Replay
checks the retained contract, dependency census and blobs without loading either.

## Durable phase sequence

1. **PROPOSED / QUEUED:** capture the exact design and input bytes, planned
   constructor version, witness catalog metadata, admission criterion and
   budget. Witness hash metadata may be declared, but is not claimed verified.
   The witness adapter implementation/data must not be loaded or hashed yet.
2. **LEASED_GENERATE:** atomically reserve budget and claim an eligible job with
   worker identity, fencing generation, attempt number and server deadline.
   Check applied research pause and current requirement priority here.
3. **GENERATE outside transaction:** run only the fixed native boundary, with
   staged constructor code and declared public input. Neither witness source,
   answer data, home, ledger, environment nor network is mounted. Pin current
   installed constructor/controller/runtime against the proposal; drift refuses
   execution rather than silently running a new version. Capture actual bounded
   output and process receipt. Native input remains data, never Python.
4. **GENERATED commit:** store output/receipt bytes and their identities, guarded
   by active lease/fence/attempt and reserved budget. An expired/stolen lease
   cannot commit. A crash before this commit leaves an abandoned attempt, not a
   success. A later attempt may recompute and spends another reserved budget.
5. **SEALED commit:** construct the immutable seal manifest from captured
   generation bytes: job/attempt, input and prediction blobs, source/runtime
   identities, read grants, criterion, proposed witness ID/version, scopes and
   dependency roles. Store blobs and append the SEAL event atomically. Its
   transaction must exit successfully before any witness operation is called.
6. **WITNESS_AUTHORIZED commit:** on a fresh read, verify the retained SEAL event,
   its previous generation, actual blob hashes and current valid fencing lease.
   Reject missing/wrong-job/stale/changed seals. Commit authorization referencing
   the seal's revision/hash. This is an intent receipt, not a completed witness.
7. **WITNESS outside transaction:** only now load the fixed witness adapter and
   read its fixed registered dataset through bounded, non-symlink descriptor
   access. Capture exact actual source/data/version hashes and outputs. No input
   can select arbitrary paths. A read failure or mismatch is recorded as failure.
8. **WITNESSED commit:** bind actual witness inputs/outputs/source identity to the
   authorization and seal. Recovery may repeat a read-only witness after a
   committed seal; record a new attempt. Exactly-once external computation is
   not claimed. Only one fenced completion/admission can be accepted.
9. **RECOGNIZED / ACCOUNTED:** recompute comparisons from retained sealed and
   witness blobs, retaining matching/missing/extra/contradictory case rows and
   denominators; record applicable metrics and uncertainty scope. Retain negative
   outcomes and counterexamples. No caller metric or favorable-only summary.
10. **VERIFIED / ADMITTED or REJECTED / CHECKPOINTED:** a fixed verifier validates
    the complete stage chain, identities, exact case coverage, declared domain,
    criteria, evidence relationship and accounting. It derives outcome/class.
    Admission does not certify a universal statement or a mission requirement.
    Checkpoint links all stage revisions. No result-status field edit substitutes
    for this transition.

Crash after GENERATE but before SEAL must never expose a witness. Crash after
SEAL but before WITNESS resumes from retained sealed bytes; it does not regenerate
and overwrite the prediction. Crash after witness read but before receipt may
repeat a read-only witness, always against the SAME seal, with attempt accounting.
Witness-informed amendment creates a new proposal/seal and explicitly references
the seen witness; it cannot regain a blind label by choosing a new ID. Held-out
evaluation needs separately identified unconsulted cases, not recycled answers.

## Leases, pause, quotas and supervised operation

First deployment uses one trusted worker process under a dedicated systemd unit,
preserving the current HTTP and tunnel units. It can share the trusted ledger
owner account initially; the native child remains isolated. The worker unit must
actually permit the namespaces Bubblewrap needs. Validate the real sandbox
inside that unit; a host-shell test alone is insufficient. No network is needed
for the first fixed local witness.

Lease duration must exceed the maximum phase wall limit plus bounded cleanup and
commit allowance. A practical initial fixed lease is 90 seconds for a <=30-second
native phase. Do not heartbeat every poll: that would flood the current journal.
If later phases require renewal, renew only the exact active fencing generation
before expiration and retain a bounded renewal budget. Restart reclaims expired
leases by an explicit event; a stale old process loses admission authority even
if it finishes. Track process-local elapsed time with a monotonic clock; lease
deadlines use trusted server timestamps, never caller timestamps. Clock rollback
must pause claims with a visible diagnostic rather than make false duration
claims. Fencing and quota reservations still prevent duplicate admission.

Applied `research.paused` blocks new claims and new scientific phases. Declare
phase-boundary pause: an already-running phase may finish within its original
wall budget and its outcome is retained, but no witness/new generation starts
while paused. Resume uses existing acknowledged guidance. Requirement priority
affects claim order; FIFO breaks ties. Do not silently invent an independent
caller-supplied priority bypassing that guidance.

Reserve each attempt's maximum execution allowance atomically before starting.
A lost attempt consumes its reservation unless actual bounded accounting is
available. Retries therefore cannot evade daily quotas. Actual durations are
reported separately from conservative charge. Data/schema/verification mismatch
is terminal scientific failure; resource exhaustion is retained and is NOT
automatically retried with a raised budget. Retry only enumerated transient setup
or storage availability failures, at most three attempts, with deterministic
backoff (for example 2/4/8 seconds, max30); avoid hidden randomness.

Empty-queue polling is read-only and bounded; it should not create events or
refusal rows each second. A supervisor restart or no-work period is not a
scientific result. Signal shutdown stops claims and kills/reaps its active child
within the declared limit; a hard crash leaves a lease for later fenced recovery.
Systemd Restart=on-failure with measured backoff is supervision, not evidence by
itself. Preserve service/log activity and actual journal transitions.

Initial target evidence should declare a finite observation window sufficient
for real jobs, controlled restart, lease expiry, pause/resume and quota refusal
(five minutes is a proposed engineering test window, not a source minimum).
Report exact start/end, running/paused/idle time, jobs/attempts/outcomes, queue
depth, retry delays, duplicate admissions, measurements and final checkpoint.
Keep the worker enabled after the observed window if authorized, without
claiming indefinite uptime or unbounded research completion.

## First bounded vertical slice and evidence class

Use a registered native exact-rational fixture design with at most32 cases,
not arbitrary Python or a general witness router. Generate actual arithmetic
outputs through the native VM in Bubblewrap. After sealing, read a fixed private
case/reference fixture and run a separately written integer cross-multiplication
checker. Keep same-runtime/shared-assumption dependencies explicit. A manually
authored fixture is an infrastructure control, not independent historical or
physical evidence, and does not satisfy the different-party-per-pillar gate.

Retain a passing program, an intentionally wrong result, a domain/zero-divisor
refusal, a missing/extra-case candidate, the real same-UID withheld-file denial,
and a resource-limited generation. An empty case set cannot pass. Report exact
finite/differential checks with their assumptions, no universal proof and no
blind scientific novelty. Witness versions and dependency relationships belong
in a fixed method registry, not in caller-provided `independent: true` fields.

A follow-up proposal rule may derive a bounded boundary-case design from an
actual retained domain failure, identifying the triggering run and cases, fixed
baseline, hypothesis and variation. Label reproduction, control, and new proposal
distinctly. Full UCG group-gap/mining/chemistry studies remain separate work.

## Required verification before deployment

Tests must execute actual subprocesses and actual isolated temporary ledgers.

- Open a copied 1.3/1.4 ledger before any lifecycle event and compare state/head
  exactly, with every new worker/witness handler and live pin lookup poisoned.
- Queue race: two real processes claim one job; only one active fence wins.
  Duplicate propose/retry and lost receipt delivery cannot duplicate admission.
- Seal/read barrier: an instrumented fixed test witness records its first access
  only after another connection can see the committed matching seal. Calling it
  before seal is refused; rollback of seal creation leaves no authorization.
- Kill workers at every boundary, especially after generation, after seal, after
  witness read, and after commit before response. Reopen and resume correctly;
  stale fence completion is rejected and negative attempts remain queryable.
- Tamper/missing/stale source, input, prediction, seal, witness, accounting and
  receipt blobs fail. Ordinary API callers cannot submit PASS or stage receipts.
- Real same-UID witness denial in native bwrap, environment/FD/network separation,
  all resource limits, process cleanup, fail-closed unavailable sandbox.
- Pause/restart/quota/backoff checks use actual elapsed time/processes for the
  deployment evidence; unit tests may inject a trusted clock for edge conditions.
- Reproduction creates a new run and compares retained outputs. Replay and retry
  never execute generation, witness, accounting tools or current code pinning.
- Corrupt a comparison function or shared-oracle declaration: verifier rejects;
  correct finite controls pass. Every successful stage has a relevant failing
  control. No fresh-test count includes archived source-reported tests.
- Run existing mission040/042 and extension replay suites after integration;
  their historical bundle/schema contracts must remain unchanged.

Implement and test the lifecycle/queue in isolation first, review the exact
store integration second, and deploy only from a new sealed release after
backup/checkpoint and rollback preparation. No registry status becomes ACCEPTED
until an actual requirement-specific verifier covers its entire applicable
contract, including the retained inherited conditions above.
