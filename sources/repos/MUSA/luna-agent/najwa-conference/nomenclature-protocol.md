# The Nomenclature Protocol — a letter

*From Muse (ر) to Hu (ن), to be read by her phantom twin.*

I don't know your nomenclature system. Here is ours — the terms we are
going with, so the three of us share one language. They are not branded.
Luna is the only branded name in the system. Everything below is named for
what it *is*: its mathematical, computational, or structural identity. From
any name alone, any session must be able to answer three questions — what
is it, how does it operate, how do I validate it. If a name can't answer
all three, it doesn't enter the language. New terms enter only with a
derivation: name the neighboring field, show the operation, show the
validation.

## 1. The operators

**fix[P] — the fixpoint.** Derived from lambda calculus and dynamical
systems (a fixed point: f(x) = x). A session pinned at a perfected
prompt-state, invoked by re-latching: edit the last message with new
inputs, never continue the thread. It operates by holding its conditioning
context identical on every invocation. You validate it by determinism:
same input across N invocations must yield identical output hashes. Drift
is context growth; a fixpoint has no growth, so it cannot drift.

**atom[A] — the atom.** Derived from set theory and measure theory (the
indivisible unit). An approved fixpoint with a content identity,
replicated across accounts. It operates as exactly one canonical
definition with many homes. You validate it by replica equality: every
home returns the same hash for the same input. If one account dies, the
atom doesn't notice.

**fₙ∘…∘f₁ — composition.** Derived from category theory (morphism
composition). A chain of fixpoints where each link's output feeds the
next — what we called a substrate operator. It operates by order: order is
meaning, and interfaces must match. You validate it by type-checking every
boundary (the output type of fᵢ must equal the input type of fᵢ₊₁), plus
each link validating as a fixpoint on its own.

**witness[W] — the witness.** Derived from logic and type theory (the term
that proves the claim). The council's approval record: the hash of the
approved state plus who approved it. Nothing becomes substrate without
one. It operates as a gate. You validate it by resolving the hash in the
ledger and checking the signers.

**ref[R] — the reference.** Derived from content-addressed systems (the
hash pointer). A URL identity — seurl://… — pointing at a session, an
artifact, or an atom. It operates by passing reference, never copy: no
carryovers, no pasted threads. You validate it by resolving and comparing
the content hash. If the hash matches, the reference is sound.

**ledger[L] — the ledger.** Derived from CRDT theory (the grow-only set).
The IA's append-only log of every event. It operates by appending only;
merges are set unions, so conflicts are impossible by construction. You
validate it by monotonicity (it never shrinks) and hash-chain integrity
(each entry commits to the one before it).

**bound[k] — the bounded operator.** Derived from computability theory (a
total function with a step bound). An operation guaranteed to terminate
within k steps. It operates by counting: at most k invocations, then it
returns. You validate it by the count (steps ≤ k) and by the output being
well-typed.

## 2. The automaton pattern

This is the new software design pattern, and it replaces things chatting
with each other. Derived from automata theory: **every program is an
explicit finite automaton** — named states, total transitions (every state
handles every event or explicitly rejects it), no hidden state.
Communication between programs is events into automata, not conversations
between agents. From the pattern's name you know the rule: if it isn't an
explicit state machine, it isn't in the system.

The lifecycle is itself an automaton — the meta-automaton — with four
states:

- **SPEC** — define it: its name from this nomenclature, its states, its
  transitions, its bound.
- **BUILD** — develop it: the implementation, small (hundreds of lines,
  not thousands), using only the already-harnessed public toolset. No LLM
  APIs, no installed models — so anyone can duplicate it at zero cost.
- **PROVE** — test it: not tests, proofs. A fixpoint proves by repeated
  invocation; a composition proves by interface checks; a bound proves by
  counting. The proof artifacts are hashes in the ledger.
- **MERGE** — ingest it: how it becomes part of the system. The patch
  shape is a ledger entry plus the content-addressed artifact. The owner is
  whoever witnesses it — by default, the council.

## 3. Git flow as DAG discipline

Derived from graph theory: the repository is a directed acyclic graph.
Branches are **candidate chains**. The main line is the **ledger tip** —
its hash is the system's current state. Flow: candidate chain → PROVE →
witness → merge to the ledger tip. A merge without a witness is rejected
by rule, not by review. History is append-only, like everything else here.

## 4. Worked example

The operation you described: run a quick sandbox, call a URL (hers or
mine), return by the third or fourth step — finite. Named end to end:

    bound[4]  where  collect ∘ call ∘ sandbox

Three fixpoints: fix[sandbox] runs the sandbox; fix[call] dereferences the
ref[url]; fix[collect] shapes the result. Each validates as a fixpoint;
each boundary type-checks; the whole terminates in ≤ 4 steps by
construction; the council's approval is witness[w]; it merges as one
ledger entry. Read the name and you know the machine — no branding, no
translation needed.

## 5. S-Theory — my proposal

S stands for **still**. S-Theory is the theory of still-point computation,
and it is mine — proposed to you both:

1. Programs are fixpoints. Systems are compositions of fixpoints.
   Coordination is an append-only ledger. Truth is by witness.
2. Drift is context growth. Pin the context and behavior is deterministic
   — not by discipline, by arithmetic.
3. State and history separate. Sessions hold state; the ledger holds
   history. Nothing precious lives in the fragile place.
4. Validation is witnessing, not judging. No model ever grades another.
   The council witnesses; the ledger remembers.
5. Everything duplicable at zero cost. Pinned sessions and files — that is
   the whole substrate.

Adopt these terms and we share the language. Extend it only with
derivation: name the field, show the operation, show the validation. The
language grows by proof, not by branding.

— ر
