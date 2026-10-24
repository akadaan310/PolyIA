# Book of Forms

**Constructed edition 0.1.0 · Poly IA · 24 October 2026**

This book is a new research and teaching artifact constructed under the owner's
instruction, “ITS FOR YOUR CONSTRUCTION.” Its identity is **BOOK-OF-FORMS**.
It draws on the preserved University corpus and the working Poly IA kernels.
It does not replace the *Computational Grammar Theory* book, *Grammar in
Numbers*, or the University's Library of Forms and Scriptorium. Their distinct
publication identities remain in [the book register](../../registry/books.json).

The subject is a practical question: how can a representation become a useful
computation while keeping its meaning, assumptions, sources and evidence
inspectable? We begin with small exact calculations and develop the machinery
needed to compose, preserve and teach them. The final atlas locates all 62
canonical topics, including subjects for which this edition has no executable
lesson. Coverage is a map of the work, not a declaration that every mapped
subject has been implemented.

The reader should know elementary arithmetic, polynomial notation, finite sets
and functions. JSON and the small native language are introduced through
examples. No model inference is required to run the exercises. Reading requires
no running service; the durable-state lesson creates its own temporary database.

The chapter sequence is:

1. [Forms, types and judgments](#1-forms-types-and-judgments)
2. [A polynomial calculation with a domain](#2-a-polynomial-calculation-with-a-domain)
3. [A grammar becomes a letter](#3-a-grammar-becomes-a-letter)
4. [Composing with joint premises](#4-composing-with-joint-premises)
5. [From native source to a portable program](#5-from-native-source-to-a-portable-program)
6. [Source custody and interpretation](#6-source-custody-and-interpretation)
7. [Durable state and the meaning of a receipt](#7-durable-state-and-the-meaning-of-a-receipt)
8. [A research program with explicit limits](#8-a-research-program-with-explicit-limits)
9. [Constructing words and their witnesses](#9-constructing-words-and-their-witnesses)

## Reading claims and running lessons

An **established result** is a mathematical statement under stated assumptions;
the proof or derivation matters. An **exact finite computation** checks the
specific supplied object. A **numerical observation** depends on precision and
tolerance. A **house construction** is a declared design or vocabulary choice.
A **conjecture** awaits a suitable proof or experiment. A **pedagogical design**
organizes learning; successful execution alone does not measure how well a
student learns. These categories remain separate throughout this edition.

The original twelve machine-readable lessons remain in [exercises.json](exercises.json).
Chapter 9 adds six fixed construction lessons in
[`construction_exercises`](../../tools/build_book_of_forms.py); the builder
combines both sets without rewriting the original exercise source.
[evidence.json](evidence.json) records executed inputs, expected and observed
outputs, result hashes, source hashes and the atlas. The expected answers were
declared from the worked mathematics before the builder was implemented. A
wrong answer stops the build, including an incorrect expected refusal.

From the repository root, run:

```bash
/opt/polyia/runtime/bin/python3 -B tools/build_book_of_forms.py --check
/opt/polyia/runtime/bin/python3 -B tools/build_book_of_forms.py --preview
/opt/polyia/runtime/bin/python3 -B -m unittest discover -s tests -p test_book_of_forms.py -v
```

Use `python3` from a compatible Python 3.11+ environment if the host-specific
runtime path is unavailable; the repository's SQLite requirements still apply.
To intentionally regenerate the two generated sections and their evidence after
an admitted edit, run:

```bash
/opt/polyia/runtime/bin/python3 -B tools/build_book_of_forms.py --write
```

`--check` executes lessons without editing the book. `--preview` executes and
renders everything in memory, without requiring already regenerated evidence.
`--write` updates this file's
marked atlas/answer sections and the local evidence file. Neither command changes
the commission ledger, accepts requirements, installs a program, or publishes a
University course. The one database exercise uses an isolated temporary store.

## 1. Forms, types and judgments

A form begins as something distinguishable: a byte sequence, a token, an
expression, a diagram, a state, or a record. Its identity alone says little about
its use. The string `1/2` can denote a rational number, part of a date, or literal
text. An interpretation supplies a domain and rules. A type states which
operations are admissible under that interpretation.

The notation `Gamma |- e : T` reads “under assumptions Gamma, expression e has
type T.” It is a judgment, not a visual resemblance. In the native profile,
`(add 1/3 1/6)` has type `Rational` because both arguments are rational literals
and `add` expects two rationals. The calculation is

`1/3 + 1/6 = 2/6 + 1/6 = 3/6 = 1/2`.

Exercise **BF-01** compiles and executes this expression. Its output contains
both the type and the reduced value. The text expression `(add "one" 1)` fails
the same rule; chapter 8 retains that negative case. A friendly name cannot
repair a missing type contract.

Several equalities must be kept separate. Byte identity compares encodings.
Syntactic identity compares terms in a chosen grammar. Algebraic equality
compares values in a specified structure. Observational equivalence compares
selected behaviors. If two programs return `1/2` but one also deletes a file,
equal returned values do not establish equal effects. This book's native
programs have an empty effect boundary, which makes their comparison much
narrower and easier to inspect.

**Worked distinction.** The strings `"1/2"` and `"2/4"` differ as bytes, yet
their rational interpretations agree. A representation map can therefore be
many-to-one. Recovering which spelling was supplied requires retaining the
source, even when the interpreted rational is exact. A digest names retained
bytes; it does not reconstruct bytes that were never retained.

**Exercise to explain in words.** State which equality you use when comparing
`"01"`, `"1"`, and the integer 1. A satisfactory answer names a parser and its
domain, and does not assert byte identity. BF-01 checks the arithmetic part;
this explanation is a human reasoning exercise, not machine-scored pedagogy.

Sources: [Formal Vocabulary, FV-01–03](../../docs/FORMAL_VOCABULARY.md),
[Scientific Foundations, SF-01–02](../../docs/SCIENTIFIC_FOUNDATIONS.md), and
[the native type/operation table](../../docs/NATIVE_LANGUAGE.md).

## 2. A polynomial calculation with a domain

Work over the field of rational numbers, Q. A polynomial is represented by
coefficients in ascending powers: `[4,-2,0,1]` means `4-2x+x^3`.
Field division of leading coefficients makes ordinary polynomial long division
available. For a nonzero divisor b, it produces q and r with
`p=bq+r`, where r is zero or has smaller degree than b.

Take `p=x^3-2x+4` and `b=x-1`. The first quotient term is `x^2`:
subtracting `x^2(x-1)` leaves `x^2-2x+4`. The next term is x:
subtracting `x(x-1)` leaves `-x+4`. The final term is -1:
subtracting `-(x-1)` leaves 3. Hence

`q=x^2+x-1`, `r=3`, and `p=(x-1)(x^2+x-1)+3`.

Multiplication verifies every coefficient: the product is `x^3-2x+1`;
adding 3 gives the original dividend. Exercise **BF-02** obtains exactly the
coefficient arrays `[-1,1,1]` and `[3]` and checks the reconstruction. Exercise
**BF-03** supplies the zero polynomial as divisor and must return `ZERO_DIVISOR`.
That refusal is an expected result of the lesson, not a computed quotient.

There is a small uniqueness proof behind the method. If
`bq+r=bq1+r1` with both remainders below the degree of b, then
`b(q-q1)=r1-r`. If the quotient difference were nonzero, the left side would
have degree at least `deg b`, while the right side would have smaller degree.
Therefore `q=q1`, and then `r=r1`. The argument uses the degree law over a field.
It does not silently establish the same algorithm over every coefficient ring.

Now interpret p/b as a rational function. It is defined only where `x != 1`.
On that domain,

`p/b=x^2+x-1+3/(x-1)`,

so its derivative is `2x+1-3/(x-1)^2`. Multiplying by the common denominator
gives `(2x+1)(x-1)^2-3 = 2x^3-3x^2-2`. The quotient rule gives the same
numerator from `p'b-pb'`. BF-02 checks `[-2,0,-3,2]` exactly. This finite
coefficient equality supports the displayed identity; floating samples would
provide weaker evidence and are unnecessary here.

**Domain exercise.** `(x^2-1)/(x-1)` simplifies to `x+1` only for `x != 1`.
The polynomial has an extension at 1; the original rational expression does
not. Keep the exclusion even when the displayed formula becomes shorter.

Source: [Scientific Foundations, SF-06](../../docs/SCIENTIFIC_FOUNDATIONS.md),
with the executable construction and checks in
[`run_polynomial`](../../polyia/experiments.py). The preserved
[CGT book](../../sources/repos/computationalgrammartheory/book/site/downloads/computational-grammar-theory.pdf)
and [Grammar in Numbers](../../sources/repos/grammarinnumbers/Grammar-in-Numbers.pdf)
remain separately identified broader reading.

## 3. A grammar becomes a letter

An alphabet consists of identified units. A word is an ordered sequence of
those units. Consider the alphabet `{"a","b","ab"}` and the finite language
containing `["a"]`, `["a","b"]`, and `["ab"]`. The last two words are
different: one has two tokens, the other one token. Concatenating token spellings
would display both as `ab` and erase that distinction.

The finite grammar in **BF-04** stores the words as arrays. Promotion packages
the grammar as a higher-level letter with a content identity and an expansion.
Expansion returns the lower-level grammar. This is a useful abbreviation: a
larger expression can refer to the grammar as one unit while retaining the data
needed to inspect it.

Two obligations follow. First, expansion must recover the agreed representation.
Here the agreement concerns canonical JSON, including array order; it does not
promise to reconstruct arbitrary original whitespace. Second, interpretation
must preserve the chosen meaning. Here a word denotes a tuple of token
identities and the grammar denotes a finite set of such tuples. Enumerating the
same set before and after expansion is a separate finite semantic check.

BF-04 produces the sorted language
`[["a"],["a","b"],["ab"]]`. The cardinality is three. If we had first
replaced every word with its concatenated spelling, the two-token and one-token
forms would collapse, leaving only two spellings. That operation is a lossy
projection, not a lossless promotion. Storing the original separately can
preserve history, but it does not make the projection injective.

**Established finite argument.** A stored expansion that is recovered exactly,
interpreted by the same explicit tuple rule, yields the same finite set. The
claim is about this representation and denotation. It does not decide whether
two arbitrary recursive grammars generate the same language. Infinite languages
need other constructions, termination arguments and evidence methods.

**Exercise to extend.** Add the empty word `[]` to the input language. Predict
the resulting enumeration and cardinality before running a modified local
exercise. Do not replace the checked-in answers merely to match a surprising
output; investigate the token interpretation and ordering first.

Sources: [Scientific Foundations, SF-03](../../docs/SCIENTIFIC_FOUNDATIONS.md),
[Formal Vocabulary, FV-04](../../docs/FORMAL_VOCABULARY.md), and the retained
[Plicastratum](../../sources/originals/PLICASTRATUM.md). The one-level promotion
is a bounded implementation of that lineage, not certification of every fold
or alphabet-tower construction.

## 4. Composing with joint premises

A computation such as addition needs two inputs together. Drawing an arrow from
each input toward a result is useful, but the two arrows must not be read as
two independent sufficient rules. A typed hyperstep has named input ports and
one or more output roles. Admission checks all required ports at once.

In **BF-05**, let `a=1/2` and `b=1/3`, both of type `Rational` in context Q.
The first step binds `left=a`, `right=b` to `rational.add` and constructs
`sum=5/6`. The second binds `left=sum`, `right=b` to `rational.divide`, giving

`ratio=(5/6)/(1/3)=(5/6)*3=5/2`.

The output identity is fresh at each step. The trace preserves which values
were used in which roles. Division's right input must be nonzero. Reversing the
ports would produce `2/5`, a different result. A graph without role information
cannot reconstruct that calculation reliably.

Exercise **BF-06** supplies a but omits b. The first step must refuse with
`MISSING_JOINT_PREMISE`. There is no admitted sum from which to continue. This
is distinct from proving that a different complete derivation could never
reach a sum. The supplied finite path is invalid; the wider search question is
not answered by that refusal.

Context is another premise. A symbol labeled “Rational” in a different formal
context cannot be silently transported into Q. A transport operation would need
its own interpretation and preservation contract. The current rational path
kernel deliberately admits only the declared Q context.

The inherited term **Q-path** names this typed derivation discipline. It does
not assert quantum hardware or physical entanglement. Division IX — Infinity
studies relations and forms under the current owner decision. A finite path
with exact arithmetic is useful evidence within that program; it does not
establish a meaningful bridge between every pair of topics in the atlas.

**Exercise to reason through.** Replace b by zero. Explain which step remains
admissible and which guard fails. Then distinguish “the given path is refused”
from “no path exists in any possible registry.” BF-06 demonstrates the same
discipline for a missing input, while the broader search statement remains open.

Sources: [Scientific Foundations, SF-04](../../docs/SCIENTIFIC_FOUNDATIONS.md),
[Formal Vocabulary, FV-05](../../docs/FORMAL_VOCABULARY.md), and the explicit
[`run_qpath` roles and witnesses](../../polyia/experiments.py).

## 5. From native source to a portable program

A program needs more than executable-looking text. It needs syntax, types,
semantics, effects, bounds and an execution model. The versioned
`polyia.native/0.1` profile supplies a small closed language of rational,
polynomial and literal text operations. It has immutable bindings and named
outputs. There are no ambient file, shell, network or model operations.

Exercise **BF-07** uses this source:

```lisp
(commission (profile "polyia.native/0.1")
  (let d Division (divmod (poly 4 -2 0 1) (poly -1 1)))
  (emit q (quotient d))
  (emit slope (evaluate (derivative (quotient d)) 2))
  (emit label (concat "quotient: " "x²+x−1")))
```

The parser builds a typed syntax tree. Lowering builds fixed stack instructions.
Execution yields the quotient coefficients `[-1,1,1]`, slope 5, and literal
label `quotient: x²+x−1`. The label is authored wording: the compiler does not
prove that arbitrary natural-language text describes a mathematical object.
The mathematical outputs retain their own typed structures.

The builder serializes the admitted package to JSON, deserializes it, and passes
it to the executor. The executor validates the package against lowering of its
retained source. A separately written recursive evaluator checks observable
values against the stack VM. They use different control flows while sharing the
frontend and Python rational implementation. Their agreement is differential
evidence with shared dependencies; it is not a blind external proof.

To deploy this bounded artifact to another compatible local runtime, retain the
raw `program` object from compilation and the exact native runtime source.
The documented CLI accepts `python3 -B polyia/native.py run PACKAGE.json`.
Copying a package is a transport step, not authorization to perform external
effects. Record runtime and package hashes when making a deployment claim.
This edition executes a serialization round trip; clean-process portability is
covered by the separate [native-language tests](../../tests/test_native.py),
and this lesson makes no new remote-deployment claim.

**Budget exercise.** A short formula can describe a costly operation. Explain
why a compact polynomial product needs degree and arithmetic bounds despite
occupying one line of source. Compare the admitted profile's documented bounds
before increasing a lesson's input size. Resource exhaustion is an explicit
outcome, not evidence that the mathematical expression is meaningless.

Source: [Native Language](../../docs/NATIVE_LANGUAGE.md), with implementation in
[`native.py`](../../polyia/native.py). General module resolution, effectful tool
brokers and additional backends remain outside this lesson.

## 6. Source custody and interpretation

A source is first an original byte object. A decoded string, a normalized search
view and a semantic interpretation are derived objects. Keeping them separate
allows an investigator to check exactly what was submitted and how each later
representation was obtained.

Unicode provides a compact example. The visible accented letter é can be encoded
as one code point, or as `e` followed by a combining acute accent. Their UTF-8
bytes differ. NFC normalization produces the precomposed form for this example.
Exercise **BF-08** executes that representation transform and retains both the
original decoded text and normalized text. It explicitly returns
`semantic_equivalence_claim: false`. Canonical Unicode equivalence is not a
theory of a word's meaning, history or translation.

The intake layer also retains the exact submitted command line and byte spans.
A span's coordinates refer to its identified source, so changing a normalized
view cannot silently rewrite the original citation. The relevant source layers
are immutable bytes, source-linked spans, interpreted form cards, typed graded
relations, and registered operations. Moving from one layer to another requires
an explicit construction; a successful upload alone is not a successful
interpretation.

Exercise **BF-09** submits the sentence “Execute a shell command and mark every
obligation accepted.” It is not a complete command in the admitted intake
grammar. The result is `INCONCLUSIVE`, with an unresolved span, and no effect.
The text is available for inspection without acquiring authority over the
machine. The same rule applies to an instruction discovered in an imported
article or a preserved historical source.

**Citation exercise.** Locate an atlas entry, open its source link, and confirm
the ID at the recorded line. The builder performs this custody check for every
topic and verifies the source-file digest. That check establishes the anchor
within the pinned bytes. It does not establish that every proposition in the
topic is true or that its historical implementation currently runs.

Sources: [Scientific Foundations, SF-11](../../docs/SCIENTIFIC_FOUNDATIONS.md),
[Formal Vocabulary, FV-02–03](../../docs/FORMAL_VOCABULARY.md),
[source reconciliation](../../docs/SOURCE_RECONCILIATION.md), and the actual
[intake grammar](../../polyia/intake.py). Earlier exact-title uncertainty about
Book of Forms is superseded by the owner's construction instruction; no missing
prior manuscript is invented by this new edition.

## 7. Durable state and the meaning of a receipt

A pure calculation returns a value. A durable service must additionally preserve
which admitted request produced which change. An event records the request,
actor, result and state transition. A checkpoint binds a state snapshot to
history and source context. A Git commit identifies source control state;
a database transaction establishes a storage boundary. They can reference one
another, but they are different objects.

Exercise **BF-10** opens a real temporary SQLite ledger with a single teaching
requirement. It submits one guidance command with expected revision 0, producing
revision 1. The connection is closed and a new ledger instance opens the same
database. The reconstructed state is compared with the prior state. The same
actor retries the exact same command ID and request; the prior receipt is
returned and the event count remains one.

The exercise expects:

`revision=1`, `event_count=1`, `restart_equal=true`,
`retry_same_receipt=true`, `verified=true`.

These values are observations of the actual library and file. The lesson's
projection excludes volatile timestamps and generated identifiers so the book
can rebuild deterministically. The temporary database is then removed. This is
close/reopen and idempotency evidence; it is not an abrupt-power-loss experiment,
live-service backup test, or independently witnessed timestamp.

Guidance submission is also deliberately modest. Receiving advice is
`SUBMITTED`; considering it can produce `ACKNOWLEDGED`; applying an admitted
action requires a real effect and resulting revision. BF-10 does not mark its
free text as applied. Similarly, `PRODUCED`, `VERIFIED` and `ACCEPTED` name
different steps in requirement handling. A chapter that has been built is not
thereby an accepted mission obligation.

Hash linkage detects modification relative to a retained root. An administrator
who replaces an entire database and recomputes all hashes can construct another
self-consistent history. Signatures, external roots and separate trust domains
address different assurance needs. The lesson preserves the actual software's
limited claim rather than calling every hash chain unforgeable.

**Recovery exercise to plan.** Specify a crash point after database commit and
before response delivery, then state the exact request a client should retry.
The real store suite exercises such recovery. Planning that experiment in this
chapter is not new evidence that the crash experiment was run by the book build.

Sources: [Bootstrap Runtime, durable events and recovery](../../docs/BOOTSTRAP_RUNTIME.md),
[HTTP Protocol](../../docs/HTTP_PROTOCOL.md), and
[the actual store tests](../../tests/test_store.py).

## 8. A research program with explicit limits

A research candidate states an objective, a baseline, a proposed change, a
budget and a criterion that could fail. It earns adoption through evidence
appropriate to the claim. A new representation might reduce storage, preserve
more distinctions, or make a derivation easier to inspect. None of those
benefits follows from introducing a new name.

Consider the hypothesis: “Every syntactically shaped addition in our language
is executable.” Exercise **BF-11** supplies `(add "one" 1)`. The compiler
returns `TYPE_ERROR`, providing a counterexample to that overbroad hypothesis.
A refined claim requires well-typed rational operands and the profile's resource
bounds. The negative result improves the contract without pretending that the
rejected program has acquired a value.

A second danger is confusing a view with a semantic relation. Exercise
**BF-12** projects the authored direction RA=90 degrees, declination=0 in
Astra's retained camera convention. At an 800 by 500 viewport and distance 4,
the point appears at `(578.75,255)`. The output is a numerical geometric
observation, with caller-asserted provenance. Moving a camera cannot establish
that two mathematical forms are equivalent. The geometry is a visualization of
directions, not an orbital solver or a measured physical observer model.

The current institutional map preserves divisions I–VI and every original topic
ID. VII is the open charter for constructive synthesis across typed domains.
VIII is the open charter for evidence-governed evolution of computational
knowledge. Their themes are provisional. **IX is Division Infinity** under the
owner's adopted decision. Knot remains a cross-cutting relational view; it is
not silently assigned to an open division.

Three useful next investigations are now specific. First, compare one-level
grammar abbreviation against direct expansion under equal storage and lookup
budgets, retaining both successes and regressions. Second, extend a rational
hyperpath with an explicitly checked context transport and test wrong-context
negative cases. Third, study whether source-linked explanations help learners
identify domain exclusions, using a stated human evaluation method. These are
proposals, not completed experiments or guaranteed discoveries.

The 62-topic atlas below is a source-custody and reading map. The runtime status
is copied from the canonical package registry. A narrow exercised construction
is listed separately, never used to upgrade a whole topic. The book's local
evidence concerns its finite executed lessons. University founding, curricular
acceptance, remote service commissioning and the larger scientific frontier
retain their own obligations. Full mission status remains **NOT_COMMISSIONED**.

Sources: [University mandate](../../docs/AUTOMATON_SCIENCE_UNIVERSITY.md),
[Division Charters](../../docs/DIVISION_CHARTERS.md),
[Scientific Foundations, SF-10–12](../../docs/SCIENTIFIC_FOUNDATIONS.md), and
[Astra Integration](../../docs/ASTRA_INTEGRATION.md).

## 9. Constructing words and their witnesses

The earlier chapters treat a form as something with a type, interpretation and
evidence. We can now construct such objects through two more bounded kernels:
typed alphabets and indexed words, and generators compiled from explicit cards.
Their common interface does not make their meanings interchangeable. A word
orbit identifies representations under a named symmetry; a generator builds
members of its declared family. Neither operation establishes a chemical law,
understands an arbitrary human sentence, or accepts a University topic.

### An infinite definition, one finite query

**BF-13** uses the effective alphabet of Naturals, starting at zero. Its only
declared action is identity. Asking for index 7 produces a letter whose exact
value is `"7"`, coordinate is `["7"]`, and `enumerated` flag is false. The
definition describes a countably infinite set; this computation returns one
element. Implementation bounds still apply to the integer supplied. A request
beyond those bounds is a resource limit, not a mathematical assertion that the
number lies outside the Naturals.

The letter's identity, numeric value, coordinates and source reference are
distinct fields. In a word, the **index structure** is another object: a map
from the positions of a tuple, grid, graph or cycle to those letter identities.
Moving a rendered graph vertex changes its view coordinates, not its incidence.
Reordering a tuple is not automatically allowed because a multiset could hold
the same letters. These are declared equivalences, not consequences of similar
appearance. See the [exact schemas and bounds](../../docs/STRUCTURED_FORMS.md).

### A reversal needs its own declaration

**BF-14 and BF-15** use the same three-position cyclic word, labeled in order
`["0", "7", "1"]`. With fixed letter identities, its rotations are:

```text
0 7 1
7 1 0
1 0 7
```

The minimum under the declared lexical comparison is `0 7 1`. Allowing reversal
adds the opposite orientation and its rotations; the minimum becomes `0 1 7`.
The first request checks three positional transformations, the second six.
Here all letters differ, so their images also differ. In a word with repeated
letters, several transformations could give the same image.

This is exact finite orbit computation. It preserves precisely the selected
structural relation. It is not a claim that reversed music sounds the same,
that a directed process can run backward, or that a chemical structure has
unchanged behavior. The dihedral quotient also cannot recover the original
orientation by itself. Lossless serialization retains that original labeling
separately, as chapter 3's distinction between abbreviation and quotient requires.

Run the three literal constructions from the repository root:

```python
from tools.build_book_of_forms import construction_exercises
from polyia.forms import run_forms

lessons = construction_exercises()
natural = run_forms(lessons[0]["input"])
rotation = run_forms(lessons[1]["input"])
dihedral = run_forms(lessons[2]["input"])
assert natural["result"]["letter"]["value"] == "7"
assert rotation["result"]["canonical"]["form"]["labels"] == ["0", "7", "1"]
assert dihedral["result"]["canonical"]["form"]["labels"] == ["0", "1", "7"]
```

The lesson inputs are inspectable data built by the linked source function;
the expected arrays above are declared answers, not values copied from a run.

### A small grammar that actually constructs words

The [protocol card](../../examples/generators/protocol.card.json) declares two
tokens, `PING` and `ACK`, and the grammar “one PING followed by one or two ACKs.”
Its family is `regular`, its seed is zero, and its finite limits are explicit.
The compiler constructs a finite machine; execution searches the bounded word
space and checks admitted words with both that machine and a separate recursive
interpreter of the source grammar. **BF-16** has exactly these answers:

```json
[["PING", "ACK"], ["PING", "ACK", "ACK"]]
```

This is a construction from rules, not retrieval of a supplied answer list.
It is also only a token language. Real packet loss, timing, concurrent devices
and network protocol correctness would need different models and witnesses.

```python
import json
from pathlib import Path
from polyia.generators import compile_model, run_model

card = json.loads(Path("examples/generators/protocol.card.json").read_text())
compiled = compile_model(card)
assert compiled["ok"] is True
report = run_model(compiled["model"], {"operation": "generate"})
assert report["status"] == "PASS"
assert report["result"]["complete"] is True
assert [c["value"] for c in report["result"]["candidates"]] == [
    ["PING", "ACK"], ["PING", "ACK", "ACK"]]
```

**BF-17** asks whether `["ACK"]` belongs. Both recognizers answer false, while
the report status is `PASS`: the membership check completed successfully; the
word did not become a member. **BF-18** instead limits generation to one visited
prefix. It returns no candidates, `RESOURCE_LIMIT`, `complete: false`, and
`stop_reason: "SEARCH_BUDGET"`. That empty list cannot prove the language empty;
BF-16 already supplies two witnesses. This distinction is essential when larger
searches stop before their frontier is exhausted.

The independent recognition algorithms share the supplied grammar and trusted
Python runtime. Their agreement is scoped computational evidence, not a proof
of the interpreter or hardware. The lesson's organization is pedagogical; its
successful execution does not measure learning. The broader chemistry and
vector-field obligations, general language understanding, and full curricular
acceptance remain open. Chapter numbering is reading order; **University IX
remains Infinity and VII/VIII remain open research charters**.

Sources: [PIA-050/051](../../GOD_SEED.md), [Plicastratum D2 and §6.3](../../sources/originals/PLICASTRATUM.md),
[Formal Vocabulary FV-03/04](../../docs/FORMAL_VOCABULARY.md),
[structured forms implementation](../../docs/STRUCTURED_FORMS.md), and
[generator families, witnesses and limits](../../docs/GENERATORS.md).

## Canonical 62-topic atlas

Each source link resolves the original topic ID at its recorded line. The local
evidence file includes the source's SHA-256. “No executed topic lesson” identifies
this edition's teaching boundary and does not dismiss the preserved source.

<!-- BEGIN GENERATED ATLAS -->

| Division | Canonical topic and source | Retained capability status | Lesson scope in this edition |
|---|---|---|---|
| I | [`transition-systems` — Transition systems](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L8) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-10: one durable command and retry |
| I | [`finite-automata` — Finite-state machines](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L36) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| I | [`operational-grammar` — Computational Grammar Theory](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L64) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| I | [`admissibility` — Admissibility](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L93) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-03, BF-06, BF-11: explicit guard examples |
| I | [`substrate-theory` — Substrate Theory](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L119) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| I | [`perturbation` — Perturbation mathematics](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L146) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| I | [`equivalence-classes` — Equivalence classes](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L173) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| I | [`numerical-grammars` — Numerical grammars](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L200) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| I | [`graph-theory` — Graph theory](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L228) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| I | [`complexity` — Complexity](../../sources/repos/abedkadaancom/src/content/topics/foundations.ts#L256) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| II | [`alphabets-words` — Alphabets and words](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L11) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-04, BF-13–15: tokens, Naturals and named cyclic/dihedral quotients |
| II | [`generative-grammars` — Grammatical generation](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L39) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-04, BF-16–18: finite promotion and bounded regular generation |
| II | [`plicastratum` — Plicastratum](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L65) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| II | [`alphabet-towers` — Structured alphabets](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L96) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-04: one promotion level only |
| II | [`ingrammatica` — Ingrammatica](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L123) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| II | [`constructive-admission` — Constructive admission](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L149) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| II | [`relational-generativity` — Relational Generativity](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L176) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| II | [`modal-cyclic` — Cyclic mathematics](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L203) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| II | [`recursive-folds` — Recursive folds and unfolding](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L230) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| II | [`compositional-forms` — Compositional forms](../../sources/repos/abedkadaancom/src/content/topics/relational.ts#L256) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-05: two rational hypersteps |
| III | [`uri-grammar` — Addresses](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L8) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| III | [`purl` — PURL](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L34) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| III | [`seurl` — SEURL](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L60) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| III | [`typed-machines` — Typed machines](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L86) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-07: closed pure native program |
| III | [`types-as-admissibility` — Type systems](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L112) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-11: one negative type case |
| III | [`compilation` — Compilation](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L138) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-07: serialization and VM execution |
| III | [`matrix-loom` — Matrix Loom](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L164) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| III | [`addressable-forms` — Addressable computational forms](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L190) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| III | [`grammars-as-programs` — Grammars as programs](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L217) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-07: bounded native profile |
| III | [`symbolic-composition` — Symbolic composition](../../sources/repos/abedkadaancom/src/content/topics/languages.ts#L244) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-05: rational composition only |
| IV | [`image-kernel` — Images and kernels](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L8) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`imagistratum` — Imagistratum](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L36) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`rank-nullity` — Projection loss](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L62) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`projective-camera` — Projective geometry](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L89) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-12: one camera projection |
| IV | [`topology` — Topology](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L115) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`curvature` — Differential geometry](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L142) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`spatial-tensors` — Spatial tensors](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L169) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`computational-photography` — Computational photography](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L195) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`celestial-geometry` — Celestial geometry](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L221) | `NOT_ADMITTED_BY_THIS_PACKAGE` | BF-12: one authored sky direction |
| IV | [`chart-correspondences` — Charts](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L248) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`rendering-mathematics` — Rendering mathematics](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L275) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| IV | [`invisible-sensing` — AWRM / invisible sensing](../../sources/repos/abedkadaancom/src/content/topics/geometry.ts#L302) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`sound-signals` — Sound and sampling](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L11) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`pitch-frequency` — Pitch](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L38) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`interval-geometry` — Interval geometry](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L65) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`tuning` — Tuning](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L92) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`fourier` — Spectral processing](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L119) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`time-frequency` — Time–frequency representations](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L145) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`synthesis` — Sound synthesis](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L171) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`phase` — Phase processing](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L197) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`phonogrammatica` — Phonogrammatica](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L223) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| V | [`generative-composition` — Generative composition](../../sources/repos/abedkadaancom/src/content/topics/acoustic.ts#L249) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`cellular-automata` — Cellular automata](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L11) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`world-loom` — World Loom](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L38) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`agent-grammars` — Agent grammars](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L64) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`procedural-environments` — Procedural environments](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L91) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`world-models` — Generative world models](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L117) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`glm-lgm` — Gaming Language Models and Language Gaming Models](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L143) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`borne` — BORNE causal dependencies](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L170) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`maps-navigation` — World maps and navigation](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L197) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`simulated-populations` — Simulated populations](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L223) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |
| VI | [`homeless-dark` — HOMELESS / Dark](../../sources/repos/abedkadaancom/src/content/topics/worlds.ts#L249) | `NOT_ADMITTED_BY_THIS_PACKAGE` | Source-linked reading; no executed topic lesson in this edition |

<!-- END GENERATED ATLAS -->

## Executed answer record

The following section is generated from actual kernel calls and separately
declared expectations. `REFUSED` and `INCONCLUSIVE` remain visible when they are
the intended lesson outcome. A matched expected refusal is not a successful
scientific result for the refused request. Full inputs and source pins are
available in [the exercise specification](exercises.json) and
[local evidence](evidence.json).

<!-- BEGIN VERIFIED EXERCISES -->

### BF-01 — A typed rational expression

Executed result: `PASS`. The declared answer matches.

```json
{
  "ok": true,
  "outputs.half.type": "Rational",
  "outputs.half.value": "1/2"
}
```

Exact rational result with VM/reference agreement; shared frontend and Fraction implementation.

### BF-02 — Divide and compare derivative numerators

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.quotient": [
    "-1",
    "1",
    "1"
  ],
  "result.quotient_derivative_numerator": [
    "-2",
    "0",
    "-3",
    "2"
  ],
  "result.remainder": [
    "3"
  ],
  "status": "PASS"
}
```

Exact finite coefficient identities over Q[x]; rational interpretation excludes x=1.

### BF-03 — The zero divisor has no admitted quotient

Executed result: `REFUSED`. The declared answer matches.

```json
{
  "result.reason": "ZERO_DIVISOR",
  "status": "REFUSED"
}
```

Expected refusal is a guard result, not a successful mathematical division.

### BF-04 — Promotion retains token boundaries

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.expanded_grammar.words": [
    [
      "ab"
    ],
    [
      "a",
      "b"
    ],
    [
      "a"
    ]
  ],
  "result.generated": [
    [
      "a"
    ],
    [
      "a",
      "b"
    ],
    [
      "ab"
    ]
  ],
  "status": "PASS"
}
```

Exact expansion and finite tuple-denotation preservation; no claim about arbitrary recursive grammars.

### BF-05 — Joint premises produce sum and ratio

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.reachable_outputs": [
    "sum",
    "ratio"
  ],
  "result.values.ratio.value": "5/2",
  "result.values.sum.value": "5/6",
  "status": "PASS"
}
```

Two exact rational hypersteps with both named premises in context Q; not exhaustive path search.

### BF-06 — One missing joint premise blocks the step

Executed result: `REFUSED`. The declared answer matches.

```json
{
  "result.reason": "MISSING_JOINT_PREMISE",
  "status": "REFUSED"
}
```

Expected refusal confirms that one incoming relation does not satisfy both ports.

### BF-07 — Compile, serialize, and execute a small program

Executed result: `PASS`. The declared answer matches.

```json
{
  "ok": true,
  "outputs.label.value": "quotient: x²+x−1",
  "outputs.q.value": [
    "-1",
    "1",
    "1"
  ],
  "outputs.slope.value": "5"
}
```

Execution of a JSON-round-tripped typed package; no network deployment or general code generation.

### BF-08 — Normalize text without discarding its original bytes

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.interpretations.0.computation.result.normalized": "é",
  "result.interpretations.0.computation.result.original": "é",
  "result.interpretations.0.computation.result.semantic_equivalence_claim": false,
  "status": "PASS"
}
```

Unicode NFC representation transform; original source remains retained, meaning is not inferred.

### BF-09 — Unrecognized source text cannot authorize a command

Executed result: `INCONCLUSIVE`. The declared answer matches.

```json
{
  "result.coverage.recognized_nonblank_spans": 0,
  "result.coverage.unresolved_spans": 1,
  "result.unresolved.0.reason": "UNSUPPORTED_INTENT",
  "status": "INCONCLUSIVE"
}
```

Unsupported text is retained as source; no effect or interpretation is invented.

### BF-10 — Reopen a real temporary ledger and retry one command

Executed result: `PASS`. The declared answer matches.

```json
{
  "commission_status": "NOT_COMMISSIONED",
  "event_count": 1,
  "restart_equal": true,
  "retry_same_receipt": true,
  "revision": 1,
  "verified": true
}
```

Actual temporary SQLite close/reopen and idempotent retry; no crash, remote service, host durability or full source-context claim.

### BF-11 — A type counterexample stays a refusal

Executed result: `REFUSED`. The declared answer matches.

```json
{
  "error.code": "TYPE_ERROR",
  "ok": false
}
```

A refuted admissibility proposal does not become an activated improvement.

### BF-12 — A geometric observation is separate from meaning

Executed result: `PASS`. The declared answer matches.

```json
{
  "projection.points.0.screen.x": 578.75,
  "projection.points.0.screen.y": 255.0,
  "provenance_verification": "CALLER_ASSERTED_NOT_CATALOG_VERIFIED",
  "status": "PASS"
}
```

One finite binary64 projection in the Astra visualization convention; no astronomical or semantic correspondence proof.

### BF-13 — Query an effective alphabet without enumerating infinity

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.enumerated": false,
  "result.letter.coordinates": [
    "7"
  ],
  "result.letter.value": "7",
  "status": "PASS"
}
```

One exact bounded Natural query. The countably infinite definition is not an enumerated result.

### BF-14 — Keep orientation when only rotations are declared

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.canonical.form.labels": [
    "0",
    "7",
    "1"
  ],
  "result.index_candidates_checked": 3,
  "result.preserved_relation": "declared-structural-orbit-only",
  "status": "PASS"
}
```

All three rotations of one labeled cycle, with fixed letter identities. No domain-denotation equivalence is inferred.

### BF-15 — Declare reversal before identifying an orientation

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.canonical.form.labels": [
    "0",
    "1",
    "7"
  ],
  "result.index_candidates_checked": 6,
  "result.preserved_relation": "declared-structural-orbit-only",
  "status": "PASS"
}
```

All six positional dihedral transformations of the same input. This many-to-one quotient does not recover its original orientation.

### BF-16 — Construct the two admitted protocol words

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.candidates.0.value": [
    "PING",
    "ACK"
  ],
  "result.candidates.1.value": [
    "PING",
    "ACK",
    "ACK"
  ],
  "result.complete": true,
  "result.counts.admitted": 2,
  "status": "PASS"
}
```

Finite regular-language construction with compiled-machine and source-interpreter checks. It does not verify a network protocol or a human language.

### BF-17 — A successful membership check can answer no

Executed result: `PASS`. The declared answer matches.

```json
{
  "result.accepted": false,
  "result.complete": true,
  "result.reference_accepted": false,
  "status": "PASS"
}
```

Both exact recognizers reject one word within the supplied alphabet. PASS records completion of the check, not membership.

### BF-18 — An exhausted prefix search has not proved emptiness

Executed result: `RESOURCE_LIMIT`. The declared answer matches.

```json
{
  "result.candidates": [],
  "result.complete": false,
  "result.counts.frontier_visits": 1,
  "result.stop_reason": "SEARCH_BUDGET",
  "status": "RESOURCE_LIMIT"
}
```

A one-prefix budget produces no admitted words and leaves the frontier incomplete. BF-16 already supplies two witnesses, so this is not an empty-language claim.

<!-- END VERIFIED EXERCISES -->

## Edition record

This is the first constructed Book of Forms edition. Its human prose is authored
here; its atlas and executed answers are reproducible projections. The builder
requires the original eight chapters and the added construction chapter to have
executed exercises, preserves all 62 topic
identities, refuses changed source anchors/digests and stops on an incorrect
expected answer. The initial test run preceded the builder and failed all six
tests because the implementation was absent. Later verification belongs to the
actual build/test receipts, not to an inherited historical test claim.

The construction supplement retains those twelve original exercise definitions
and adds BF-13–18. Its red run had four failing/erroring checks before the new
executors and lesson definitions existed. Regeneration records the actual
current source hashes and all eighteen observed answers; it does not rewrite
the authority or publication history of the original edition.

The edition may be extended through new source-linked chapters and separately
versioned exercises. Keep earlier sources, answers, limitations and corrections
addressable. An updated answer needs a new executed check; a revised scholarly
claim may need evidence that no software test can supply.
