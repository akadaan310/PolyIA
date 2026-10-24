"""Nomenclature as an executable grammar: names are programs that build structures.

(a) IUPAC systematic element names (IUPAC 1978 recommendations, [K]):
      Z digits -> roots  0 nil 1 un 2 bi 3 tri 4 quad 5 pent 6 hex 7 sept 8 oct 9 enn
      name = roots + 'ium', elisions: 'bi'/'tri' + 'ium' -> 'bium'/'trium'; 'enn' + 'nil' -> 'ennil'
      symbol = first letters of the roots, capitalised.   A bijection Z <-> name (tested).
(b) Acyclic alkane names (IUPAC 2013 P-44 rules, the subset needed for C1..C8):
      parent = longest chain; tie -> more substituents; numbering -> lowest locant set;
      tie -> first-cited (alphabetical) substituent gets the lower locant;
      prefixes multiplied (di, tri, tetra), alphabetised ignoring multipliers.
    and the inverse: a parser name -> tree (so a name is literally a program).
(c) The morphemes as operators, with their language of origin recorded (Greek/Latin/house),
    because 'non-' (Latin nonus) sits among Greek numerals and 'undec-' is a hybrid:
    a nomenclature's chain of custody is data (WAZNOMIA discipline).
"""
from __future__ import annotations

import itertools
import re

ROOTS = ["nil", "un", "bi", "tri", "quad", "pent", "hex", "sept", "oct", "enn"]


def element_name(Z: int) -> str:
    parts = [ROOTS[int(d)] for d in str(Z)]
    s = ""
    for i, p in enumerate(parts):
        if i > 0 and s.endswith("nn") and p == "nil":
            s = s[:-1]
        s += p
    if s.endswith("bi") or s.endswith("tri"):
        s += "um"
    else:
        s += "ium"
    return s


def element_symbol(Z: int) -> str:
    return "".join(ROOTS[int(d)][0] for d in str(Z)).capitalize()


def parse_element_name(name: str) -> int:
    """Inverse of element_name.  Tries both readings of the final 'i' and keeps the one
    whose regeneration reproduces the name exactly (so the parse is witnessed, not guessed)."""
    s0 = name.lower()
    if not s0.endswith("um"):
        raise ValueError("image failure: not a systematic name (no -ium/-um ending)")
    found = []
    for s in {s0[:-2], s0[:-3] if s0.endswith("ium") else None} - {None}:
        try:
            z = _roots_to_int(s)
        except ValueError:
            continue
        if element_name(z) == s0:
            found.append(z)
    if len(found) != 1:
        raise ValueError("image failure" if not found else "kernel failure: ambiguous name")
    return found[0]


def _roots_to_int(s: str) -> int:
    digits = ""
    while s:
        for i, r in sorted(enumerate(ROOTS), key=lambda x: -len(x[1])):
            if s.startswith(r):
                digits += str(i)
                s = s[len(r):]
                break
            if r == "nil" and s.startswith("il") and digits.endswith("9"):  # 'ennil' elision
                digits += "0"
                s = s[2:]
                break
        else:
            raise ValueError(f"image failure: '{s}' is not a root sequence")
    if not digits:
        raise ValueError("image failure: empty")
    return int(digits)


# --------------------------------------------------------------------- alkanes
STEM = {1: "meth", 2: "eth", 3: "prop", 4: "but", 5: "pent", 6: "hex", 7: "hept", 8: "oct", 9: "non", 10: "dec", 11: "undec", 12: "dodec"}
MULT = {2: "di", 3: "tri", 4: "tetra", 5: "penta", 6: "hexa"}
ORIGIN = {"meth": "Greek methy (wine) + hyle (wood), via methylene (1834) -- historical", "eth": "from ether (Greek aither)",
          "prop": "from propionic (Greek protos + pion: first fat)", "but": "from butyric (Latin butyrum: butter)",
          "pent": "Greek pente", "hex": "Greek hex", "hept": "Greek hepta", "oct": "Greek okto / Latin octo",
          "non": "Latin nonus (not Greek ennea)", "dec": "Greek deka", "undec": "Latin un(us) + Greek deka (hybrid)",
          "dodec": "Greek dodeka", "di": "Greek di-", "tri": "Greek tri-", "tetra": "Greek tetra-", "-ane": "suffix of saturation (Hofmann 1866 vowel series)",
          "-yl": "Greek hyle (matter, wood) via methyl"}


def _paths(adj):
    n = len(adj)
    best = []
    for s in range(n):
        st = [(s, [s])]
        while st:
            u, p = st.pop()
            ext = False
            for w in adj[u]:
                if w not in p:
                    st.append((w, p + [w]))
                    ext = True
            if not ext:
                best.append(p)
    L = max(len(p) for p in best)
    return [p for p in best if len(p) == L]


def _sub_name(adj, root, parent):
    """Name of the substituent tree hanging at root (attached to parent).  C1..C3 + isopropyl."""
    nodes, st = [], [(root, parent)]
    while st:
        u, p = st.pop()
        nodes.append(u)
        st += [(w, u) for w in adj[u] if w != p]
    k = len(nodes)
    if k <= 3:
        branched = any(len([w for w in adj[u] if w != parent or u != root]) > 2 for u in nodes) or \
                   len([w for w in adj[root] if w != parent]) >= 2
        if k == 3 and branched:
            return "isopropyl"
        return STEM[k] + "yl"
    if k == 4 and len([w for w in adj[root] if w != parent]) == 3:
        return "tert-butyl"
    raise ValueError(f"substituent of size {k} outside the declared C1..C8 grammar")


def name_alkane(adj) -> str:
    n = len(adj)
    if n == 1:
        return "methane"
    cands = []
    for path in _paths(adj):
        subs = []
        on = set(path)
        for i, u in enumerate(path):
            for w in adj[u]:
                if w not in on:
                    subs.append((i + 1, _sub_name(adj, w, u)))
        cands.append((path, subs))
    nsub = max(len(s) for _, s in cands)
    cands = [c for c in cands if len(c[1]) == nsub]   # P-44.1.1: more substituents
    def key(c):
        _, subs = c
        locs = sorted(l for l, _ in subs)
        alpha = sorted(subs, key=lambda x: (x[1].replace("tert-", ""), x[0]))
        return (locs, [l for l, _ in alpha])
    path, subs = min(cands, key=key)
    groups = {}
    for l, s in subs:
        groups.setdefault(s, []).append(l)
    parts = []
    for s in sorted(groups, key=lambda x: x.replace("tert-", "")):
        ls = sorted(groups[s])
        parts.append(",".join(map(str, ls)) + "-" + (MULT[len(ls)] if len(ls) > 1 else "") + s)
    return "-".join(parts) + STEM[len(path)] + "ane"


SUBSIZE = {"methyl": [[]], "ethyl": None, "propyl": None, "isopropyl": None, "tert-butyl": None}


def parse_alkane(name: str):
    """Name -> tree adjacency.  The inverse grammar; refuses what it cannot read."""
    m = re.fullmatch(r"((?:[\d,]+-(?:di|tri|tetra)?(?:tert-butyl|isopropyl|methyl|ethyl|propyl)-?)*)([a-z]+?)ane", name)
    if not m:
        raise ValueError("image failure: not an alkane name in the declared grammar")
    stem = m.group(2)
    inv = {v: k for k, v in STEM.items()}
    if stem not in inv:
        raise ValueError(f"image failure: unknown parent stem '{stem}'")
    N = inv[stem]
    adj = [[] for _ in range(N)]
    for i in range(N - 1):
        adj[i].append(i + 1)
        adj[i + 1].append(i)

    def add(parent, kind):
        def node(p):
            adj.append([p])
            adj[p].append(len(adj) - 1)
            return len(adj) - 1
        if kind in ("methyl", "ethyl", "propyl"):
            p = parent
            for _ in range({"methyl": 1, "ethyl": 2, "propyl": 3}[kind]):
                p = node(p)
        elif kind == "isopropyl":
            c = node(parent); node(c); node(c)
        elif kind == "tert-butyl":
            c = node(parent); node(c); node(c); node(c)
    for loc, mult, kind in re.findall(r"([\d,]+)-(di|tri|tetra)?(tert-butyl|isopropyl|methyl|ethyl|propyl)", m.group(1)):
        locs = [int(x) for x in loc.split(",")]
        if mult and len(locs) != {"di": 2, "tri": 3, "tetra": 4}[mult]:
            raise ValueError("kernel failure: multiplier does not match locant count")
        for l in locs:
            if not 1 <= l <= N:
                raise ValueError("image failure: locant outside the parent chain")
            add(l - 1, kind)
    if any(len(a) > 4 for a in adj):
        raise ValueError("inadmissible: a carbon would carry more than 4 bonds")
    return adj
