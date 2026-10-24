"""The geometric alphabet of organic forms (no chemistry assumed until the end).

Two form-alphabets, each with an explicit symmetry group (the 'poly way' of writing a form):

1. TREES (acyclic skeletons).  A form is an unlabelled free tree with max degree 4.
   Canonical letter: AHU code (Aho, Hopcroft & Ullman 1974) rooted at the tree's centre
   (Jordan 1869).  Witness: Cayley's alkane counts (OEIS A000602) and RDKit's
   independent canonicaliser.

2. POLYGONS (monocycles).  A ring of size n is a cyclic word
       a0 b0 a1 b1 ... a(n-1) b(n-1)        a_i in atom-letters, b_i in {-, =}
   read up to the dihedral group D_n (rotations and reflections of the polygon).
   Canonical letter: the lexicographically least word in its D_n orbit (a *bracelet*).
   Witness for the counting: Burnside's lemma.  Two Kekule words of benzene lie in one
   D_6 orbit, so 'resonance' here is literally a group-orbit identification (a declared fold).

Then chemistry enters only as admissibility (valence, from E01) and as Hueckel's
4k+2 rule for full conjugation [K: Hueckel 1931].
"""
from __future__ import annotations

import itertools
from math import gcd

from . import elements as E

# ----------------------------------------------------------------- trees
def ahu(adj, root, parent=-1):
    return "(" + "".join(sorted(ahu(adj, c, root) for c in adj[root] if c != parent)) + ")"


def centres(adj):
    n = len(adj)
    if n <= 2:
        return list(range(n))
    deg = [len(a) for a in adj]
    leaves = [i for i in range(n) if deg[i] <= 1]
    left = n
    while left > 2:
        left -= len(leaves)
        nxt = []
        for u in leaves:
            for w in adj[u]:
                deg[w] -= 1
                if deg[w] == 1:
                    nxt.append(w)
            deg[u] = 0
        leaves = nxt
    return leaves


def canon_tree(adj):
    return min(ahu(adj, c) for c in centres(adj))


def alkane_skeletons(nmax):
    """Grow trees by one leaf at a time; keep one representative per canonical code."""
    level = {canon_tree([[]]): [[]]}
    counts = [1]
    for n in range(2, nmax + 1):
        nxt = {}
        for adj in level.values():
            for u in range(len(adj)):
                if len(adj[u]) >= 4:  # the only chemical input: carbon has 4 bonds
                    continue
                new = [list(a) for a in adj] + [[u]]
                new[u].append(len(adj))
                c = canon_tree(new)
                if c not in nxt:
                    nxt[c] = new
        level = nxt
        counts.append(len(level))
    return counts, level


def tree_smiles(adj):
    def rec(u, p):
        kids = [c for c in adj[u] if c != p]
        return "C" + "".join(f"({rec(c, u)})" for c in kids[:-1]) + (rec(kids[-1], u) if kids else "")
    return rec(0, -1)


# ----------------------------------------------------------------- polygons
def dihedral_orbit(word):
    """word: tuple of (atom, bond) pairs around the ring."""
    n = len(word)
    out = []
    for r in range(n):
        rot = word[r:] + word[:r]
        out.append(rot)
        # reflection: reverse atom order; bond after atom i becomes bond before it
        atoms = [a for a, _ in rot][::-1]
        bonds = [b for _, b in rot]
        rb = [bonds[(-i - 2) % n] for i in range(n)]
        out.append(tuple(zip(atoms, rb)))
    return out


def canon_ring(word):
    return min(dihedral_orbit(tuple(word)))


def polya_ring_count(n, a, b):
    """Rings with a vertex colours and b edge colours up to D_n (Burnside):
    rotation r fixes (ab)^gcd(r,n); odd n: n reflections fix a^((n+1)/2) b^((n+1)/2);
    even n: n/2 vertex-axes fix a^(n/2+1) b^(n/2), n/2 edge-axes fix a^(n/2) b^(n/2+1)."""
    rot = sum((a * b) ** gcd(r, n) for r in range(n))
    if n % 2:
        refl = n * a ** ((n + 1) // 2) * b ** ((n + 1) // 2)
    else:
        refl = n // 2 * a ** (n // 2 + 1) * b ** (n // 2) + n // 2 * a ** (n // 2) * b ** (n // 2 + 1)
    assert (rot + refl) % (2 * n) == 0
    return (rot + refl) // (2 * n)


def burnside_bracelets(n, k):
    """Number of bracelets of length n over k colours (Burnside / Polya) [K]."""
    rot = sum(k ** gcd(i, n) for i in range(n)) / n
    if n % 2:
        refl = k ** ((n + 1) // 2)
    else:
        refl = (k ** (n // 2 + 1) + k ** (n // 2)) / 2
    return int((rot + refl) / 2)


ZOF = {"C": 6, "N": 7, "O": 8, "S": 16}


def ring_admissible(word):
    """Valence: ring-bond order sum at each atom <= primary valence; H fill the rest."""
    n = len(word)
    hs = []
    for i, (a, _) in enumerate(word):
        bo = (2 if word[i][1] == "=" else 1) + (2 if word[i - 1][1] == "=" else 1)
        v = E.valences(ZOF[a])[0]
        if bo > v:
            return False, None
        hs.append(v - bo)
    return True, hs


def huckel(word):
    """Fully conjugated monocycle with 4k+2 pi electrons -> aromatic.  Returns (aromatic, pi, reason)."""
    n = len(word)
    pi = 0
    for i, (a, _) in enumerate(word):
        dbl = word[i][1] == "=" or word[i - 1][1] == "="
        if word[i][1] == "=" and word[i - 1][1] == "=":
            return False, pi, "cumulated =C= : orthogonal pi bonds, not one conjugated cycle"
        if dbl:
            pi += 1
        elif a in "NOS":
            pi += 2  # lone pair donated (pyrrole/furan/thiophene type)
        else:
            return False, pi, "sp3 carbon breaks conjugation"
    if n > 7:
        return False, pi, "large ring: planarity not assumed"
    return (pi % 4 == 2), pi, ("4k+2" if pi % 4 == 2 else "4k (antiaromatic if planar)")


def ring_smiles(word):
    s = ""
    for i, (a, b) in enumerate(word):
        s += a + ("1" if i == 0 else "")
        if i < len(word) - 1:
            s += "=" if b == "=" else ""
    if word[-1][1] == "=":
        s = s.replace("1", "=1", 1) if False else s
        # closing double bond: write ring closure with explicit bond on the last atom
        s += "=1"
    else:
        s += "1"
    return s


def enumerate_rings(nmin=3, nmax=8, atoms="CNOS"):
    seen = {}
    for n in range(nmin, nmax + 1):
        for aw in itertools.product(atoms, repeat=n):
            for bw in itertools.product("-=", repeat=n):
                w = tuple(zip(aw, bw))
                c = canon_ring(w)
                if c in seen:
                    continue
                ok, hs = ring_admissible(c)
                seen[c] = {"n": n, "admissible": ok}
    return seen
