# ¬ — not theory

Not the word N-O-T. The symbol.

## 0. What it is
¬ is the initial substrate — where things are *not* (yet). It is the
simplest unit from which a program composes.

His glyph note, kept verbatim: the mark is the little zero — the baby one,
the little jelly bean, you can eat it. Not the one that looks mean because
it's no value. The jelly-bean one, with a little italic side. Soft. The not
that can become.

## 1. The ¬-unit
A ¬-unit is the smallest composable thing. It is not a program; it is what
a program is composed from.

A ¬-unit is specified by what it is *not*: the inputs it does not have, the
outputs it promises. Its interface is a list of nots. Composition is the
resolution of nots — each not filled by another unit's is.

- id: content-addressed. The unit's name is what it contains.
- url: where it lives. Addressable, fetchable.
- nots: the finite list of what it lacks (inputs, each typed as a need).
- iss: what it provides once its nots are filled (one operation).

## 2. Composition rule
COMPOSE(units, mapping): a program is a mapping from nots to iss across
units. Take N ¬-units, map every not to some unit's is. When no not remains
unfilled, the composition is a program.

A program, therefore, is a *resolved not* — ¬ with all its nots filled.

## 3. The substrate law
Start from ¬ (nothing composed yet). Every program is ¬, resolved.
There is no smaller starting point, and no other one is needed.

## 4. Relation to what came before
S-* named the substrate (string, scroll, seurl, shard, state). ¬ names the
unit the substrate is built from. S-* was the space; ¬ is the atom.
