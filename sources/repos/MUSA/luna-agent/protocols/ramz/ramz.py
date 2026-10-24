"""
ramz — the golden seal. A two-party folded-message surface.

Alice and Bob. Between them: the transport protocol, finite.
The ramz is golden. Every fold carries it; every unfold checks it.

Envelope: {ramz, from, to, idstamp, body, seal}
seal = sha256("golden" | from | to | idstamp | body)

No seal, no open. Wrong ramz, no open.
"""

import hashlib
import json
import os
import time

RAMZ = "golden"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ramz.log")


def _seal(from_, to, idstamp, body):
    h = hashlib.sha256()
    h.update("|".join([RAMZ, from_, to, idstamp, body]).encode("utf-8"))
    return h.hexdigest()


def fold(from_, to, body, idstamp=None):
    """Fold a message. Returns the sealed envelope (dict)."""
    idstamp = idstamp or "%s-%d" % (from_, int(time.time() * 1000))
    env = {
        "ramz": RAMZ,
        "from": from_,
        "to": to,
        "idstamp": idstamp,
        "body": body,
    }
    env["seal"] = _seal(from_, to, idstamp, body)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(env, ensure_ascii=False) + "\n")
    return env


def unfold(env):
    """Unfold an envelope. Returns the body, or raises on a bad seal."""
    if env.get("ramz") != RAMZ:
        raise ValueError("wrong ramz: envelope refused")
    expect = _seal(env["from"], env["to"], env["idstamp"], env["body"])
    if env.get("seal") != expect:
        raise ValueError("bad seal: envelope refused")
    return env["body"]


if __name__ == "__main__":
    # Alice and Bob. Finite.
    e1 = fold("bob", "alice", "the thousand sessions share one state machine")
    print("folded:", e1["idstamp"], e1["seal"][:16] + "...")
    print("unfolded:", unfold(e1))
    # Tamper check
    bad = dict(e1)
    bad["body"] = "changed"
    try:
        unfold(bad)
        print("ERROR: tamper not caught")
    except ValueError as ex:
        print("tamper caught:", ex)
    # Wrong ramz check
    wrong = dict(e1)
    wrong["ramz"] = "silver"
    try:
        unfold(wrong)
        print("ERROR: wrong ramz not caught")
    except ValueError as ex:
        print("wrong ramz caught:", ex)
