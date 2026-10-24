# Fixed native execution with a Linux read boundary

`polyia.isolation` is an explicit operator tool for running the bounded
`polyia.native/0.1` grammar in a new Bubblewrap process. A native program is data:
the interface accepts no Python, shell command, executable path, module name,
arbitrary mount, or environment grant. The core native compiler and ledger stay
portable standard-library Python. This optional boundary requires Linux,
Bubblewrap, and the separately installed `/opt/polyia/runtime`; it fails closed
when they or namespace setup are unavailable.

This increment provides actual filesystem read separation and resource controls.
It does not implement the proposal/generate/seal/witness lifecycle, worker queue,
HTTP admission, a scientific witness, or a mission acceptance adapter. `PASS`
means the fixed native program ran successfully under this policy. It does not
mean PIA-092, PIA-133, or PIA-134 is accepted.

## Source obligations and scope

The retained requirements are in `registry/constitution.json`, their contracts in
`registry/acceptance.json`, and the source dispositions in
`registry/inherited_obligations.json`.

| Record | Obligation addressed here | Work still required |
| --- | --- | --- |
| PIA-092 | Declare native compiler/VM and `fractions.Fraction` as constructor dependencies; the AST evaluator is a shared-dependency internal consistency check. | Full role enforcement across experiment families and independent post-seal witnessing. |
| PIA-133; UCG-027 | No lifecycle claim is made by this standalone runner. | Enforce the complete propose/generate/seal/witness/recognize/account/verify/checkpoint transitions and refusal of witness-before-seal. |
| PIA-134; UCG-028 | The generator sees fixed declared read grants. A fixed negative control attempts to open a host witness that is absent from its mount namespace and returns a typed denial naming only its path. | Bind the isolation receipt to actual produced experiment artifacts and their lifecycle, then add a scoped acceptance verifier and its controls. |
| UCG-007, refined by REC-TOOL-ROLES | Constructor and witness roles are distinguished; no witness library, answer dataset, workspace, or host environment is granted to native execution. | Apply the same declared roles and read boundaries when additional constructors or witnesses are introduced. |

`REC-TOOL-ROLES` in `docs/SOURCE_RECONCILIATION.md` permits declared constructor,
normalizer and filter dependencies; it does not turn such a dependency into an
independent witness. The original UCG text remains unchanged in
`sources/originals/UCG_CODEX_CONSTITUTIONAL_COMMISSION.md` (SHA-256
`0cf03197777e19330ce36cf478bec9a5c4cad5459fd142c37eb4ae0e82bd6d7e`).

## Exact policy: `polyia.native-bwrap/0.1`

The host controller captures and stages only `polyia/native.py`, the inert
`polyia/__init__.py`, the fixed `isolated_worker.py`, and one bounded JSON request.
The staged files are read-only. Native imports are checked against the fixed
standard-library constructor dependency list. The package initializer may contain
only its docstring and literal version assignment. The worker executes
`/runtime/bin/python3 -I -S -B /app/isolated_worker.py`; it never evaluates caller
Python. It compiles native input with the same bounded compiler and executes its
fixed VM and AST consistency check.

The Bubblewrap command declares these grants:

| Guest path | Grant |
| --- | --- |
| `/runtime` | Read-only `/opt/polyia/runtime`, including its standard library. |
| `/app` | Read-only staged native implementation, inert package initializer and fixed worker. |
| `/input` | Read-only request containing the native source or fixed control parameters and validated budgets. |
| `/lib/aarch64-linux-gnu`, `/lib/ld-linux-aarch64.so.1` | Read-only platform libraries and loader on the actual ARM64 host. |
| `/lib/x86_64-linux-gnu`, `/lib64/ld-linux-x86-64.so.2` | Alternative fixed Linux x86-64 library/loader paths; not exercised by the ARM64 integration run. |
| `/proc`, `/dev` | New private process view and minimal device setup created by Bubblewrap. |

The sandbox starts with an empty filesystem tree; its root is then remounted
read-only. No host root, home, workspace, ledger, witness directory, `/tmp`,
network interface, D-Bus socket, or other host socket is mounted. `/proc` and
`/dev` are private kernel views, not recursively read-only ordinary files. The
whole runtime and library directories are declared read grants: operators must
keep private data out of them.

`--unshare-all` plus explicit required user, PID and network namespace flags,
`--clearenv`, `--new-session`, `--die-with-parent`, and `--cap-drop ALL` establish
the process policy. The subprocess has `close_fds=True`, null stdin, bounded
stdout/stderr pipes and a new session. The only configured environment variable
is `LANG=C.UTF-8`; Bubblewrap also supplies the fixed sandbox working directory
as `PWD`. Namespace identities, visible descriptor numbers, effective capability
bits and network interface names are recorded by the worker. The observed fourth
descriptor is the transient directory listing of `/proc/self/fd`, not an inherited
host file grant.

The launcher requires the Bubblewrap executable, runtime root, interpreter and
platform grant roots to be root owned and neither group nor world writable.
These are checks of the grant paths, not a recursive integrity audit or a defense
against an administrator modifying dependencies. Root-controlled installation,
the kernel, Bubblewrap, runtime, standard library and OS libraries remain trusted.
There is no custom seccomp filter or VM boundary. As the
[official Bubblewrap README](https://github.com/containers/bubblewrap/blob/main/README.md)
explains, the application's arguments determine the security policy; Bubblewrap
alone is not a complete sandbox policy. The actual target uses Ubuntu's patched
Bubblewrap 0.6.1, not an assertion that every version or host is supported.

## Resource limits and reports

| Budget | Default | Accepted range |
| --- | --- | --- |
| Native input | 16 KiB UTF-8 | Fixed maximum; the complete encoded worker request must also fit 32 KiB. |
| Wall time | 5 seconds | 0.1–30 seconds, finite numeric value. |
| CPU | 2 seconds | Integer 1–10 seconds; hard limit is one second above the soft limit. |
| Virtual address space | 256 MiB | Integer 64–512 MiB. |
| Combined worker stdout/stderr | 256 KiB | Integer 1 KiB–4 MiB. |

The supervisor bounds process wall time and combined output. Reading a pipe can
observe up to one additional 4096-byte chunk, which is discarded rather than
retained beyond the output budget. It kills the launched process group on wall
or output exhaustion and waits for Bubblewrap. Bubblewrap's parent-death behavior
and private PID namespace terminate the worker. The supervisor also observes its
descendant PIDs and checks their disappearance with at most one second of cleanup
observation; cleanup is separate from the execution allowance. Failure of this
check produces `PROCESS_CLEANUP_INCOMPLETE`, not a successful execution report.

The fixed worker sets CPU, address-space, file-size, open-file and zero-core-dump
limits before native evaluation. CPU/address-space limits begin in the worker;
the parent wall/output limits also cover process startup. Host source capture and
staging occur before the process deadline. These are per-job bounds for fixed
code, not cgroup accounting, a process-fork quota, a concurrent-job admission
policy, a bound on every kernel allocation, or protection against kernel faults.

Results distinguish `PASS`, `REFUSED`, `READ_DENIED`, `RESOURCE_LIMIT`,
`UNAVAILABLE`, and `ERROR`. Resource reasons distinguish wall, CPU, memory and
output exhaustion. Raw stderr and exception text are not returned. The read
control emits `READ_DENIED` only for ENOENT/EACCES/EPERM; other open failures are
errors. If the protected file unexpectedly opens, the descriptor is closed
without reading and the result is `WITNESS_READ_ALLOWED`, never a denial.

Reports identify the host supervisor PID, observed descendants and cleanup,
worker PID/namespace identities, request hash, exact staged source hashes,
interpreter executable hash, Bubblewrap executable hash, architecture and worker
Python version. `controller` identifies the current `isolation.py` source file;
the loaded host controller remains trusted. These hashes are provenance, not
signed attestation or a hash of every runtime/library file. The child must echo
the expected input/source identities and a valid response shape. No output from
this tool is automatically accepted by the ledger.

## Operator use and actual controls

Run from the checkout or a release containing these modules:

```sh
/opt/polyia/runtime/bin/python3 -B -m polyia.isolation native < program.polyia
/opt/polyia/runtime/bin/python3 -B -m polyia.isolation probe --path /absolute/withheld/witness.txt
```

The CLI consumes native data on stdin and returns JSON. Exit status is zero only
for `PASS` or a successful `READ_DENIED` control. A probe path must identify an
existing host regular file outside all declared host grants and guest aliases.
The host runner inspects metadata without opening its content; the path is passed
as data and is never mounted. This control uses exactly the same process/mount
policy as native execution. It is a fixed adversarial file-open attempt, not a
caller-supplied script. `run_control('wall'|'cpu'|'memory'|'output', budgets=...)`
provides four similarly fixed resource controls through the Python API.

The focused integration command is:

```sh
/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -p test_isolation.py -v
```

Tests exercise actual namespaces, native arithmetic, a mode-0600 witness readable
by the same host UID outside the sandbox, no witness-content disclosure, no
inherited environment/file descriptor or host network, native `exec` refusal,
all four resource limits, descendant cleanup, actual failing mount setup with
redacted diagnostics, missing Bubblewrap, malformed protocol identity, platform
permission refusal, invalid paths/budgets, controller identity and the CLI. These
integration tests require the declared Linux runtime and Bubblewrap installation;
the optional API itself returns `UNAVAILABLE` on unsupported hosts. They neither
start PolyIA nor access or mutate the production ledger.
