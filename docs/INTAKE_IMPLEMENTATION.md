# Source intake and human interface

`polyia.intake/0.1` implements a bounded source-preserving entry point for
PIA-121/122/124/169/180. It accepts supplied UTF-8 text or a complete native Poly IA
program. This increment does not claim arbitrary prose comprehension, URL/PDF
fetching, historical language attestation, or the full corpus commission.

Text is retained with a SHA-256 identity and byte-offset spans. NFC is a separate
projection; the original code points remain recoverable. Each complete nonblank
line is checked against a declared grammar. Supported lines are:

```
Teach polynomial division
divide polynomial [1,0,1] by [1,1]
normalize unicode "e\u0301"
```

The teaching command selects the declared SF-06 example; explicit coefficient
commands use their supplied exact integers/rational strings. The existing exact
polynomial kernel computes and checks the division and derivative identities,
retaining domain exclusions. Normalization establishes representation properties,
not meaning. Native format uses the lexer, typechecker, bytecode machine and
separate evaluator documented in [NATIVE_LANGUAGE.md](NATIVE_LANGUAGE.md).

Unmatched text stays unresolved. A recognized but refused computation stays
visible with its diagnostics. Inadmissible polynomial inputs can produce an
unexecuted regression proposal with a falsifiable expectation and one-run budget.
Changing concise/tutorial explanation changes the projection, not computed values.
Source links contain the preserved document digest and a named section.

## Durable use

Submit through `experiment.run` with name `intake` and parameters
`{text, format, style}`; `format` defaults to `text`, `style` to `concise`.
The dedicated browser form sends that same command and displays the latest
recorded result. Operator authorization, expected revision, stable command ID,
pause guidance and captured executing dependencies apply equally to API and UI.
Reads and replay do not rerun the interpreter. A rate limit during recovery keeps
the same pending command available, because an admission refusal cannot establish
whether an earlier request committed before its response was lost.

Submitted text is visible to the service's operator and observer roles. It is not
included in public discovery, static assets or HTTP audit logs. The source record
states unspecified rights and no public-export authorization. This two-role
service does not provide per-document or multi-tenant access isolation.

## Bounds and validation

Input is at most 16,384 UTF-8 bytes and 128 spans, with a 200-character title.
The whole native program is one span. The native compiler imposes its own syntax,
arithmetic, work and output bounds. Unknown parameters, malformed Unicode,
unsupported styles and formats refuse explicitly. Supported output remains a
scoped computation even when all checks pass.

`tests/test_intake.py` exercises exact values, unsupported suffixes, literal hostile
source text, byte-span recovery, style invariance, zero divisors and limits.
`tests/test_capabilities.py` checks actual journal capture, dependency identity,
restart/replay, pause and idempotency. `web/ui.test.mjs` exercises the actual form
handlers against a real Python HTTP service, including markup as inert text and
observer restrictions. These DOM checks do not certify browser layout or complete
accessibility; visual/browser review remains separate.
