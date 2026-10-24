"""The periodic table as an alphabet whose letters are computed, not memorised.

Lettered alphabet Σ_E (non-phonetic): symbols H, He, Li, ...  A letter's *coordinates*
are derived from one integer Z by a grammar over orbital letters (aufbau / Madelung
n+l rule, [K]: Madelung 1936; Klechkowski):

    Z  ->  configuration word over {1s, 2s, 2p, 3s, 3p, 4s, 3d, ...}
       ->  (period, block, group)           -- the position in the table
       ->  valence electrons e_v
       ->  admissible valences  V(Z)         -- octet rule + expanded octet for period >= 3
       ->  electronegativity rank            -- read from the table's position (left->right, bottom->top)

Nothing here reads chemical compounds.  The only external numbers used by the
generator are the ones the user named as the alphabet's printed face: Z, and (for
ordering only) Pauling electronegativity.  Group/period/block/valence are *derived*
and then witnessed against the printed table (Bowserinator JSON) and RDKit's curated
valence lists.
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
L = "spdf"
CAP = {"s": 2, "p": 6, "d": 10, "f": 14}


def madelung_order(nmax=8):
    subs = [(n, l) for n in range(1, nmax + 1) for l in range(0, min(n, 4))]
    return sorted(subs, key=lambda x: (x[0] + x[1], x[0]))


ORDER = madelung_order()


def configuration(Z: int) -> list[tuple[int, str, int]]:
    """Aufbau filling.  Returns [(n, l-letter, electrons)] in filling order."""
    out, left = [], Z
    for n, l in ORDER:
        if left <= 0:
            break
        k = min(left, CAP[L[l]])
        out.append((n, L[l], k))
        left -= k
    return out


def config_word(Z: int) -> str:
    return " ".join(f"{n}{l}{k}" for n, l, k in sorted(configuration(Z), key=lambda x: (x[0], L.index(x[1]))))


def position(Z: int) -> dict:
    """Period, block and IUPAC group (1-18) derived from the configuration alone."""
    conf = configuration(Z)
    period = max(n for n, _, _ in conf)
    n_last, l_last, k_last = conf[-1]
    block = l_last
    if Z == 2:  # helium: s2 but placed with the noble gases -- a declared exception of the *table layout*
        return {"period": 1, "block": "s", "group": 18, "layout_exception": True}
    if block == "s":
        group = k_last
    elif block == "p":
        group = 12 + k_last
    elif block == "d":
        group = 2 + k_last
    else:
        group = None  # f-block: no IUPAC group number (3 by some conventions)
    if Z == 1:
        group = 1
    return {"period": period, "block": block, "group": group, "layout_exception": False}


def valence_electrons(Z: int) -> int:
    p = position(Z)
    g = p["group"]
    if g is None:
        return 3
    if p["block"] == "d":
        return g if g <= 12 else g - 10
    return g if g <= 2 else (g - 10 if g >= 13 else g)


def valences(Z: int) -> list[int]:
    """Admissible covalent valences: octet  v0 = min(e, 8-e) (H: 1, He/noble: 0);
    period >= 3 p-block may expand by pairs up to e (hypervalence)."""
    p = position(Z)
    e = valence_electrons(Z)
    if Z == 1:
        return [1]
    if p["group"] == 18:
        base = [0]
        if p["period"] >= 5:  # expanded: Xe compounds
            base += [2, 4, 6, 8]
        return base
    if p["block"] in "s":
        return [e]
    if p["block"] == "p":
        v0 = min(e, 8 - e)
        vs = [v0]
        if p["period"] >= 3 and e > 4:
            v = v0 + 2
            while v <= e:
                vs.append(v)
                v += 2
        return vs
    return [e]  # d/f: not used by the covalent grammar (declared limit)


def ionic_charge(Z: int) -> int | None:
    """Main-group ion charge from position: lose e if e <= 3, gain 8-e if e >= 5."""
    p = position(Z)
    if p["block"] not in "sp" or p["group"] == 18 or Z == 1:
        return None
    e = valence_electrons(Z)
    if e <= 3:
        return +e
    if e >= 5:
        return -(8 - e)
    return None


class Table:
    def __init__(self):
        raw = json.load(open(DATA / "periodic.json"))["elements"]
        self.by_Z = {e["number"]: e for e in raw}
        self.by_sym = {e["symbol"]: e for e in raw}

    def en(self, sym):
        return self.by_sym[sym].get("electronegativity_pauling")

    def Z(self, sym):
        return self.by_sym[sym]["number"]
