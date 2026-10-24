"""Grammars of higher mathematics: Runge-Kutta methods as trees, groups from constructions,
homology from chains.

1. BUTCHER TREES [K: Butcher 1963, 2016].  A Runge-Kutta method is a word (A, b, c).
   Its order is decided by a grammar of rooted trees: the method has order p iff
   Phi(t) = 1/gamma(t) for every rooted tree t with |t| <= p.  Rooted trees are counted
   by OEIS A000081 (1, 1, 2, 4, 9, 20, 48, ...).  Prediction: order from trees (sealed);
   witness: empirical convergence slope on a test ODE.

2. GROUPS FROM A CONSTRUCTION GRAMMAR.  Productions:
       G -> Z_n | G x G | Z_m (x)_r Z_k   (semidirect, r^k = 1 mod m)
   Each production yields a Cayley table; isomorphism classes are separated by an
   invariant word (order, abelian, sorted element orders, centre size, number of
   order-2 elements).  Witness: number of groups of order n (OEIS A000001).
   The *gaps* (groups the grammar cannot produce) are predicted to be the non-split
   extensions, e.g. the quaternion group Q8; the grammar is then extended (dicyclic
   production) and re-witnessed.

3. SIMPLICIAL HOMOLOGY.  Chains are words over simplices; the boundary operator is a
   grammar rule with the law  d o d = 0  (checked).  Betti numbers over Q and over F2
   are ranks of boundary matrices.  Witness: the known homology of S^2, T^2, RP^2, K.
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction as Q

import numpy as np


# ======================================================================= Butcher
def rooted_trees(nmax):
    """Rooted trees as canonical nested tuples (children sorted)."""
    by = {1: [()]}
    for n in range(2, nmax + 1):
        out = set()
        # a tree of size n = root + multiset of subtrees whose sizes sum to n-1
        def parts(total, maxsize, prefix):
            if total == 0:
                yield prefix
                return
            for s in range(min(total, maxsize), 0, -1):
                for t in by[s]:
                    if prefix and (s, t) > prefix[-1]:
                        continue
                    yield from parts(total - s, s, prefix + [(s, t)])
        for ps in parts(n - 1, n - 1, []):
            out.add(tuple(sorted(t for _, t in ps)))
        by[n] = sorted(out)
    return by


def tsize(t):
    return 1 + sum(tsize(c) for c in t)


def gamma(t):
    return tsize(t) * math.prod(gamma(c) for c in t)


def phi(t, A, b, c):
    """Elementary weight Phi(t) = sum_i b_i * g_i(t), g_i(()) = 1, g_i(t) = prod_children sum_j a_ij g_j(child)."""
    s = len(b)
    def g(tree):
        return [math.prod(sum(A[i][j] * g(ch)[j] for j in range(s)) for ch in tree) if tree else Q(1) for i in range(s)]
    return sum(b[i] * g(t)[i] for i in range(s))


TABLEAUX = {
    "euler": ([[0]], [1], [0]),
    "midpoint": ([[0, 0], [Q(1, 2), 0]], [0, 1], [0, Q(1, 2)]),
    "heun2": ([[0, 0], [1, 0]], [Q(1, 2), Q(1, 2)], [0, 1]),
    "ralston2": ([[0, 0], [Q(2, 3), 0]], [Q(1, 4), Q(3, 4)], [0, Q(2, 3)]),
    "kutta3": ([[0, 0, 0], [Q(1, 2), 0, 0], [-1, 2, 0]], [Q(1, 6), Q(2, 3), Q(1, 6)], [0, Q(1, 2), 1]),
    "rk4": ([[0, 0, 0, 0], [Q(1, 2), 0, 0, 0], [0, Q(1, 2), 0, 0], [0, 0, 1, 0]], [Q(1, 6), Q(1, 3), Q(1, 3), Q(1, 6)], [0, Q(1, 2), Q(1, 2), 1]),
    "3/8-rule": ([[0, 0, 0, 0], [Q(1, 3), 0, 0, 0], [Q(-1, 3), 1, 0, 0], [1, -1, 1, 0]], [Q(1, 8), Q(3, 8), Q(3, 8), Q(1, 8)], [0, Q(1, 3), Q(2, 3), 1]),
    "broken-rk4 (b perturbed)": ([[0, 0, 0, 0], [Q(1, 2), 0, 0, 0], [0, Q(1, 2), 0, 0], [0, 0, 1, 0]], [Q(1, 6), Q(1, 3), Q(1, 4), Q(1, 4)], [0, Q(1, 2), Q(1, 2), 1]),
}


def tree_order(A, b, c, pmax=5, trees=None):
    trees = trees or rooted_trees(pmax)
    failed = None
    for n in range(1, pmax + 1):
        for t in trees[n]:
            if phi(t, A, b, c) != Q(1, gamma(t)):
                return n - 1, t
    return pmax, None


def rk_step(A, b, c, fn, x, y, h):
    s = len(b)
    k = []
    for i in range(s):
        yi = y + h * sum(float(A[i][j]) * k[j] for j in range(i))
        k.append(fn(x + float(c[i]) * h, yi))
    return y + h * sum(float(b[i]) * k[i] for i in range(s))


def empirical_order(A, b, c):
    """y' = y cos x, y(0)=1 -> y = exp(sin x); integrate to x=1 at h, h/2, ... ; slope of log error."""
    fn = lambda x, y: y * math.cos(x)
    exact = math.exp(math.sin(1.0))
    errs = []
    for N in (8, 16, 32, 64):
        h, x, y = 1.0 / N, 0.0, 1.0
        for _ in range(N):
            y = rk_step(A, b, c, fn, x, y, h)
            x += h
        errs.append(abs(y - exact))
    slopes = [math.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1) if errs[i + 1] > 0]
    return round(slopes[-1], 2), errs


# ======================================================================= groups
class Group:
    def __init__(self, n, mul, name):
        self.n, self.T, self.name = n, mul, name   # T[a][b] = a*b, identity 0

    def order(self, a):
        k, x = 1, a
        while x != 0:
            x = self.T[x][a]
            k += 1
        return k

    def invariant(self):
        n, T = self.n, self.T
        ab = all(T[a][b] == T[b][a] for a in range(n) for b in range(n))
        orders = sorted(self.order(a) for a in range(n))
        centre = sum(1 for a in range(n) if all(T[a][b] == T[b][a] for b in range(n)))
        squares = len({T[a][a] for a in range(n)})
        return (n, ab, tuple(orders), centre, squares)

    def is_group(self):
        n, T = self.n, self.T
        if any(T[0][a] != a or T[a][0] != a for a in range(n)):
            return False
        if any(sorted(row) != list(range(n)) for row in T):
            return False
        return all(T[T[a][b]][c] == T[a][T[b][c]] for a in range(n) for b in range(n) for c in range(n))


def cyclic(n):
    return Group(n, [[(a + b) % n for b in range(n)] for a in range(n)], f"Z{n}")


def direct(G, H):
    idx = {(g, h): i for i, (g, h) in enumerate(itertools.product(range(G.n), range(H.n)))}
    pairs = list(idx)
    T = [[idx[(G.T[a[0]][b[0]], H.T[a[1]][b[1]])] for b in pairs] for a in pairs]
    return Group(G.n * H.n, T, f"{G.name}x{H.name}")


def semidirect(m, k, r):
    """Z_m x|_r Z_k with (a,b)(c,d) = (a + r^b c mod m, b + d mod k), requires r^k = 1 mod m."""
    if pow(r, k, m) != 1 % m:
        return None
    pairs = list(itertools.product(range(m), range(k)))
    idx = {p: i for i, p in enumerate(pairs)}
    T = [[idx[((a + pow(r, b, m) * c) % m, (b + d) % k)] for (c, d) in pairs] for (a, b) in pairs]
    return Group(m * k, T, f"Z{m}x|{r}Z{k}")


def dicyclic(n):
    """Dic_n of order 4n: <a, x | a^(2n)=1, x^2=a^n, x a x^-1 = a^-1>.  Elements a^i x^j, j in {0,1}."""
    m = 2 * n
    pairs = [(i, j) for j in range(2) for i in range(m)]
    idx = {p: t for t, p in enumerate(pairs)}
    def mulp(p, q):
        (i, j), (k, l) = p, q
        if j == 0:
            return ((i + k) % m, l)
        # x a^k = a^-k x ;  x * x = a^n
        if l == 0:
            return ((i - k) % m, 1)
        return ((i - k + n) % m, 0)
    T = [[idx[mulp(p, q)] for q in pairs] for p in pairs]
    return Group(4 * n, T, f"Dic{n}")


def automorphisms(N):
    n = N.n
    out = []
    for perm in itertools.permutations(range(1, n)):
        s_ = (0,) + perm
        if all(s_[N.T[a][b]] == N.T[s_[a]][s_[b]] for a in range(n) for b in range(n)):
            out.append(s_)
    return out


def semidirect_general(N, k, sigma):
    """N x|_sigma Z_k, (a,i)(b,j) = (a * sigma^i(b), i+j mod k), sigma^k = id."""
    n = N.n
    powers = [tuple(range(n))]
    for _ in range(k):
        powers.append(tuple(sigma[x] for x in powers[-1]))
    if powers[k] != tuple(range(n)):
        return None
    pairs = list(itertools.product(range(n), range(k)))
    idx = {p: t for t, p in enumerate(pairs)}
    T = [[idx[(N.T[a][powers[i][b]], (i + j) % k)] for (b, j) in pairs] for (a, i) in pairs]
    return Group(n * k, T, f"{N.name}x|Z{k}")


def generate_groups(nmax, productions=("cyclic", "direct", "semidirect")):
    found = {}
    def put(G):
        if G and G.n <= nmax:
            found.setdefault(G.invariant(), G)
    for n in range(1, nmax + 1):
        put(cyclic(n))
    if "semidirect" in productions:
        for m in range(2, nmax + 1):
            for k in range(2, nmax // m + 1):
                for r in range(2, m):
                    put(semidirect(m, k, r))
    if "dicyclic" in productions:
        for n in range(2, nmax // 4 + 1):
            put(dicyclic(n))
    if "direct" in productions:
        for _ in range(2):
            gs = list(found.values())
            for G, H in itertools.product(gs, gs):
                if G.n > 1 and H.n > 1 and G.n * H.n <= nmax:
                    put(direct(G, H))
    if "semidirect_general" in productions:
        for N in list(found.values()):
            if 2 <= N.n <= 7:
                auts = automorphisms(N)
                for k in range(2, nmax // N.n + 1):
                    for sg in auts:
                        put(semidirect_general(N, k, sg))
            elif 2 <= N.n <= 7:
                pass
    if "direct" in productions:
        gs = list(found.values())
        for G, H in itertools.product(gs, gs):
            if G.n > 1 and H.n > 1 and G.n * H.n <= nmax:
                put(direct(G, H))
    counts = [0] * (nmax + 1)
    for inv in found:
        counts[inv[0]] += 1
    return counts[1:], found


# ======================================================================= homology
def complex_from_triangles(tris):
    tris = [tuple(sorted(t)) for t in tris]
    edges = sorted({e for t in tris for e in itertools.combinations(t, 2)})
    verts = sorted({v for t in tris for v in t})
    return verts, edges, sorted(set(tris))


def boundary(simplices_hi, simplices_lo):
    idx = {s: i for i, s in enumerate(simplices_lo)}
    M = np.zeros((len(simplices_lo), len(simplices_hi)), dtype=np.int64)
    for j, s in enumerate(simplices_hi):
        for k in range(len(s)):
            face = s[:k] + s[k + 1:]
            M[idx[face], j] += (-1) ** k
    return M


def rank_mod(M, p=None):
    """Rank over Q (p=None, exact fractions) or over F_p."""
    A = [[Q(int(v)) if p is None else int(v) % p for v in row] for row in M.tolist()]
    rows, cols = len(A), len(A[0]) if A else 0
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = (1 / A[r][c]) if p is None else pow(A[r][c], -1, p)
        for i in range(rows):
            if i != r and A[i][c] != 0:
                f = A[i][c] * inv
                A[i] = [(a - f * b) if p is None else (a - f * b) % p for a, b in zip(A[i], A[r])]
        r += 1
    return r


def betti(tris, p=None):
    V, E, F = complex_from_triangles(tris)
    d1 = boundary(E, [(v,) for v in V])
    d2 = boundary(F, E)
    assert not (d1 @ d2).any(), "law d o d = 0 violated"
    r1, r2 = rank_mod(d1, p), rank_mod(d2, p)
    b0 = len(V) - r1
    b1 = len(E) - r1 - r2
    b2 = len(F) - r2
    return (b0, b1, b2), len(V) - len(E) + len(F), bool(not (d1 @ d2).any())


def torus(n=3):
    v = lambda i, j: (i % n) * n + (j % n)
    return [t for i in range(n) for j in range(n) for t in ((v(i, j), v(i + 1, j), v(i + 1, j + 1)), (v(i, j), v(i, j + 1), v(i + 1, j + 1)))]


def klein(n=3):
    def v(i, j):
        if i >= n:   # wrap in i with a flip in j
            i, j = i - n, -j
        return (i % n) * n + (j % n)
    return [t for i in range(n) for j in range(n) for t in ((v(i, j), v(i + 1, j), v(i + 1, j + 1)), (v(i, j), v(i, j + 1), v(i + 1, j + 1)))]


SPHERE = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
RP2 = [(1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 5, 6), (1, 6, 2), (2, 3, 5), (3, 4, 6), (4, 5, 2), (5, 6, 3), (6, 2, 4)]


def is_closed_surface(tris):
    V, E, F = complex_from_triangles(tris)
    from collections import Counter
    c = Counter(e for t in F for e in itertools.combinations(t, 2))
    return all(c[e] == 2 for e in E) and len(F) == len(tris)


# ======================================================================= linear systems
def solve_linear(A, b):
    """Gauss-Jordan over Q as a machine: returns ('unique', x) | ('kernel failure', particular, nullity)
    | ('image failure', inconsistent_row).  The same two failures as 1/0 and 0/0 (GIN-THM-001)."""
    M = [[Q(v) for v in row] + [Q(bi)] for row, bi in zip(A, b)]
    rows, cols = len(M), len(A[0])
    piv, r = [], 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        M[r] = [v / M[r][c] for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                M[i] = [a - M[i][c] * bb for a, bb in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    for i in range(r, rows):
        if M[i][-1] != 0:
            return ("image failure", i)
    x = [Q(0)] * cols
    for i, c in enumerate(piv):
        x[c] = M[i][-1]
    if len(piv) < cols:
        return ("kernel failure", x, cols - len(piv))
    return ("unique", x)
