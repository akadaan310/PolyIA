# Language Construction, Reverse Grammar, and Micro-Specialist Contracts

## A. Native source syntax

`.p9` is scanned, parsed, type checked, compiled to custom `P9BC` binary, and executed on a bounded VM. Minimal EBNF:

```ebnf
program      = { fn_decl | let_decl } ;
fn_decl      = "fn" ID "(" [params] ")" "->" type "{" {let_decl} return_decl "}" ;
params       = ID ":" type {"," ID ":" type} ;
let_decl     = "let" ID ":" type "=" expr ";" ;
return_decl  = "return" expr ";" ;
type         = "Int" | "String" ;
expr         = primary {("+" | "-" | "*") primary} ;  // precedence implemented: * > +,-
primary      = NUMBER | STRING | ID | ID "(" [expr {"," expr}] ")" | "(" expr ")" ;
```

Parentheses delimit invocation and grouping; braces delimit lexical function bodies; colon introduces a type. These are native syntax and can later be enriched through parenthology and pillar scopes. The compiler produces a bytecode **instruction sequence** rather than interpreting the source through JSON objects.

Limits: v0.1 has no arrays, user-defined classes, loops, modules, closure capture, floats, side effects, imports, closures, type inference, optimized code generation, concurrency, or FFI. Bytecode format is experimental. Repeated recursion is bounded by an instruction and depth budget. The runtime is **not a hardened sandbox**.

## B. Domain grammar before corpus

The WebGL universe is declared first in `corpus/webgl_grammar.p9g`:

```text
domain WebGL
slot geometry cube : cube | box
slot geometry triangle : triangle
slot motion spin : spin | spinning | rotate | rotating
slot motion still : still | stationary | static
slot color cyan : cyan | blue
slot color amber : amber | orange
slot color coral : coral | pink
require geometry
default motion still
default color cyan
deny geometry : sphere | torus | robot | pyramid
deny color : green | red | purple
```

Parsing this config validates alias uniqueness and required slots. Corpus ingestion is handled separately and admits only documents with explicit scope, origin, and license metadata. Positive rules alone were insufficient: the composite query “box sphere” initially bypassed the missing-geometry test. Declaring an explicit negative grammar corrected the observed case. Unknown strings not in deny rules can still be ignored; this limitation prevents production usage until a richer, typed parser is developed.

## C. Two-language specialist bridge

- Natural English surface extracts `geometry`, `motion`, `color` against a bounded lexicon.
- A scope-locked `WebGL` specialist resolves those slots and produces evidence content IDs per slot.
- The scene compiler accepts `.p9s` and emits a complete HTML page with WebGL shader templates.
- Output requires actual browser/GPU validation to be claimed rendered.

No LLM was used in these transitions. In a future system, a tiny language model could propose alternative parses and snippets, **but every proposal must pass admission and compilation gates**.

## D. G-ship routing

A grammar-ship is an edge with `src`, `dst`, `relation`, and `witness`. For instance:

`English --(bridge, WebGL grammar)--> WebGL --(compile, shader template)--> WebGLSource`

Because edges are typed, only matching endpoints and allowed relations compose. BFS finds a bounded route; the path's existence is a structural claim, not semantic correctness. To make this more expressive, next version should add type unification, versioned source hashes, path costs, negative-edge certificates, and explicit optional/alternative branches.

## E. Reverse grammar

`pillar9/reverse.py` uses Python's AST **without importing or executing the file**. It extracts function names, parameter lists, return annotations, and rough signature frequencies. A robust reverse-grammar engine should add Tree-sitter parsers for JavaScript, TypeScript, HTML, CSS, GLSL, SQL and Python; extract CST/AST, imports, side effects, data-flow, type relations and library manifests. It must preserve source links and counterexamples rather than pretending that AST shape reveals meaning.

## F. Future S-LLM

Model spec `M = (scope, tokenizer/grammar, prior, learned parameters?, proposal interface, verifier, budget, benchmark)`.

A scoped specialist might be purely symbolic, statistical, a small neural network, or a hybrid. Call it a *micro-LLM* only if it is actually an LLM, with an explicit architecture and trained weights. The graph router and grammar compiler can be shared across all specialist types.

**Suggested experiments:** (1) 1K/10K/100K-source indexing and cache measurements; (2) text→scene output under corpus vocabulary held-out tests; (3) parser coverage across JS/TS/GLSL; (4) symbolic-only vs small-transformer vs hybrid; (5) verify rendered pixels on real WebGL context; (6) intentional counterexamples that look semantically similar but compile differently; (7) evidence-poisoning tests; (8) memory footprints on Android.
