# POLYIA native grammar v0.1 (implemented subset)

```
commission = "(" "commission" { statement } ")" ;
statement  = "(" ("task" STRING | "require" STRING | "deny" STRING | "evidence" ("fixture"|"attested") | "budget" INTEGER) ")" ;
```

Source may contain `;` to end of line comments. String escapes are `\\`, `\\"`, `\\n`. The grammar is a deliberate **closed bounded subset**; unsupported declarations are compile errors, not ignored comments. The current reference compiler composes metadata-only operators, with fully typed port closure and negative grammar admission. It emits a readable PIR plan with `invoke` terms and metadata for a composed state machine. This is an *own grammar/compiler artifact*, not a JSON script interpreter. It is not a general Lisp/P9 implementation, and production needs a stable binary ABI and runtime validator.

Production language extensions must distinguish: `atom`, `grammar`, `tower`, `pillar`, `transduce`, `graph`, `effect`, `state`, `transition`, `verify`, `agency`, `emit`. Each added construct requires parser/typechecker/compiler/runtime conformance and independent rejection tests.
