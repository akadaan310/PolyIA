# Session program — cloud design-construct test

seurl://test/cloud-session?units=not-unit,composition,url-machine,ramz&mode=design

## Purpose
A design-construct test for the cloud session: the full math of what we
built, as one prompt-program. The session executes it and reports back
where the design holds and where it breaks.

## Staged
Needs the logged-in cloud seat. The seat login is pending (he holds that
step). Until then, this program waits — programmed, not sent.

## The prompt-program
---
You are a design-test session. You know nothing but the URL you were given.
Execute the following constructs and report: HOLDS / BREAKS / UNDECIDED,
with the exact step that decides it.

1. ¬-UNIT. The smallest composable thing: one operation, one id, one url.
   Specified by its nots (what it lacks); its iss (what it provides).
   Test: define three ¬-units (fetch, transform, store) and compose them
   by mapping nots to iss. Show the resolved program.

2. COMPOSITION. Programs are mappings, not writings: PROGRAM = { units,
   mapping: not → is, entry }. Test: take your composed program from (1)
   and use it as a unit inside a larger program. Show the nesting.

3. URL-MACHINE. N sessions, one state machine, different addresses. Verbs:
   START, SWITCH, WRITE, COMMIT, BUILD, TALK, PERTURB. Test: simulate three
   sessions writing units, talking nots/iss through the harness, and
   building one program-URL. Show the message log.

4. RAMZ. Every cross-party message folded with the golden seal; tamper and
   wrong-ramz refused. Test: fold a TALK message, tamper with it, show the
   refusal.

5. PROGRAM-URL. seurl://program/<mapping-id>?units=<ids>. Content-addressed:
   copy the URL, copy the program. Test: give the program-URL for your
   built program from (3).

Report format per construct: verdict, the deciding step, and the smallest
change that would flip the verdict.
---

## What it tests
Not whether the cloud *can* do it — whether the *design* survives contact
with a fresh session that knows nothing but the URL.
