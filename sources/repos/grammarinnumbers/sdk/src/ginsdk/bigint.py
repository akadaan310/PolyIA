"""Arbitrary-precision integers on w-bit limbs, with counted word operations.

This module exists to make *bit complexity* observable (GIN-D-004).  Python's own
``int`` is arbitrary precision too, but it hides its cost; here every limb-level
primitive is charged to a :class:`~ginsdk.cost.Cost`:

    add   one add/subtract-with-carry of two limbs
    mul   one limb × limb → two-limb product
    div   one two-limb ÷ one-limb quotient estimate
    cmp   one limb comparison

Numbers are little-endian lists of limbs in base B = 2^k (default k = 32), with no
leading (most significant) zero limbs; zero is the empty list.  Every function is
checked against Python's ``int`` in the tests.

Algorithms: schoolbook addition, subtraction and comparison (Θ(n)); schoolbook
multiplication (Θ(n²)); Karatsuba multiplication (Θ(n^log₂3)); Knuth's Algorithm D
for division (Θ(n·m)) — all classical [Knuth, TAOCP vol. 2, §4.3].
"""
from __future__ import annotations

from .cost import Cost, charge

K = 32


def from_int(x: int, k: int = K) -> list[int]:
    if x < 0:
        raise ValueError("limb numbers are nonnegative")
    out, mask = [], (1 << k) - 1
    while x:
        out.append(x & mask)
        x >>= k
    return out


def to_int(a: list[int], k: int = K) -> int:
    x = 0
    for limb in reversed(a):
        x = (x << k) | limb
    return x


def _trim(a: list[int]) -> list[int]:
    while a and a[-1] == 0:
        a.pop()
    return a


def compare(a: list[int], b: list[int], cost: Cost | None = None) -> int:
    if len(a) != len(b):
        charge(cost, "cmp")
        return -1 if len(a) < len(b) else 1
    for i in range(len(a) - 1, -1, -1):
        charge(cost, "cmp")
        if a[i] != b[i]:
            return -1 if a[i] < b[i] else 1
    return 0


def add(a: list[int], b: list[int], cost: Cost | None = None, k: int = K) -> list[int]:
    if len(a) < len(b):
        a, b = b, a
    B = 1 << k
    out, carry = [], 0
    for i in range(len(a)):
        s = a[i] + (b[i] if i < len(b) else 0) + carry
        charge(cost, "add")
        out.append(s % B)
        carry = s // B
    if carry:
        out.append(carry)
    return out


def sub(a: list[int], b: list[int], cost: Cost | None = None, k: int = K) -> list[int]:
    """a − b for a ≥ b (the converse of addition is admissible only then, in N)."""
    B = 1 << k
    out, borrow = [], 0
    for i in range(len(a)):
        d = a[i] - (b[i] if i < len(b) else 0) - borrow
        charge(cost, "add")
        borrow = 1 if d < 0 else 0
        out.append(d + B if d < 0 else d)
    if borrow:
        raise ValueError("sub: a < b has no solution in N")
    return _trim(out)


def mul_school(a: list[int], b: list[int], cost: Cost | None = None, k: int = K) -> list[int]:
    if not a or not b:
        return []
    B = 1 << k
    out = [0] * (len(a) + len(b))
    for i, x in enumerate(a):
        carry = 0
        for j, y in enumerate(b):
            t = out[i + j] + x * y + carry
            charge(cost, "mul")
            charge(cost, "add")
            out[i + j] = t % B
            carry = t // B
        out[i + len(b)] += carry
    return _trim(out)


def _shift(a: list[int], m: int) -> list[int]:
    return [0] * m + a if a else []


def mul_karatsuba(a: list[int], b: list[int], cost: Cost | None = None, k: int = K, threshold: int = 16) -> list[int]:
    """Karatsuba–Ofman multiplication; falls back to schoolbook below ``threshold`` limbs."""
    if min(len(a), len(b)) <= threshold:
        return mul_school(a, b, cost, k)
    m = max(len(a), len(b)) // 2
    a0, a1 = _trim(a[:m]), a[m:]
    b0, b1 = _trim(b[:m]), b[m:]
    z0 = mul_karatsuba(a0, b0, cost, k, threshold)
    z2 = mul_karatsuba(a1, b1, cost, k, threshold)
    z1 = mul_karatsuba(add(a0, a1, cost, k), add(b0, b1, cost, k), cost, k, threshold)
    z1 = sub(sub(z1, z0, cost, k), z2, cost, k)
    return add(add(z0, _shift(z1, m), cost, k), _shift(z2, 2 * m), cost, k)


def divmod_limbs(u: list[int], v: list[int], cost: Cost | None = None, k: int = K) -> tuple[list[int], list[int]]:
    """Knuth's Algorithm D. Raises ZeroDivisionError for v = 0 (no admissible quotient)."""
    if not v:
        raise ZeroDivisionError("division by the empty (zero) limb vector: b·c = a has no unique solution")
    B = 1 << k
    if compare(u, v, cost) < 0:
        return [], list(u)
    if len(v) == 1:
        d, q, r = v[0], [0] * len(u), 0
        for i in range(len(u) - 1, -1, -1):
            t = r * B + u[i]
            charge(cost, "div")
            q[i], r = divmod(t, d)
        return _trim(q), _trim([r])
    n, m = len(v), len(u) - len(v)
    s = k - v[-1].bit_length()                     # normalize: top bit of v set
    vn = from_int(to_int(v, k) << s, k)
    un = from_int(to_int(u, k) << s, k)
    un += [0] * (len(u) + 1 - len(un))
    q = [0] * (m + 1)
    for j in range(m, -1, -1):
        num = un[j + n] * B + un[j + n - 1]
        charge(cost, "div")
        qhat, rhat = divmod(num, vn[n - 1])
        while qhat >= B or qhat * vn[n - 2] > rhat * B + un[j + n - 2]:
            charge(cost, "mul")
            qhat -= 1
            rhat += vn[n - 1]
            if rhat >= B:
                break
        borrow = carry = 0
        for i in range(n):                          # multiply and subtract
            p = qhat * vn[i] + carry
            charge(cost, "mul")
            carry = p >> k
            t = un[i + j] - (p & (B - 1)) - borrow
            charge(cost, "add")
            borrow = 1 if t < 0 else 0
            un[i + j] = t % B
        t = un[j + n] - carry - borrow
        borrow = 1 if t < 0 else 0
        un[j + n] = t % B
        if borrow:                                  # qhat was one too large: add back
            qhat -= 1
            carry = 0
            for i in range(n):
                t = un[i + j] + vn[i] + carry
                charge(cost, "add")
                un[i + j] = t % B
                carry = t >> k
            un[j + n] = (un[j + n] + carry) % B
        q[j] = qhat
    r = to_int(_trim(un[:n]), k) >> s
    return _trim(q), from_int(r, k)


def gcd_euclid(a: list[int], b: list[int], cost: Cost | None = None, k: int = K) -> tuple[list[int], int]:
    """Euclid's algorithm on limbs. Returns (gcd, number of division steps)."""
    steps = 0
    while b:
        _, r = divmod_limbs(a, b, cost, k)
        a, b = b, r
        steps += 1
    return a, steps


def gcd_binary(x: int, y: int, cost: Cost | None = None, k: int = K) -> int:
    """Stein's binary gcd, charging ⌈bits/k⌉ ``add`` per subtraction and per shift pass.

    (Operates on Python ints; the charges are those of the limb-level implementation.)
    """
    if x == 0:
        return y
    if y == 0:
        return x
    shift = ((x | y) & -(x | y)).bit_length() - 1
    x >>= (x & -x).bit_length() - 1
    while y:
        charge(cost, "add", -(-y.bit_length() // k))
        y >>= (y & -y).bit_length() - 1
        if x > y:
            x, y = y, x
        charge(cost, "add", -(-y.bit_length() // k))
        y -= x
    return x << shift


def powmod(base: int, e: int, m: int, cost: Cost | None = None, k: int = K, karatsuba: bool = False) -> int:
    """Left-to-right square-and-multiply modulo m on limbs."""
    mulf = mul_karatsuba if karatsuba else mul_school
    M = from_int(m, k)
    x = from_int(base % m, k)
    r = from_int(1 % m, k)
    for bit in bin(e)[2:] if e else "":
        r = divmod_limbs(mulf(r, r, cost, k), M, cost, k)[1]
        if bit == "1":
            r = divmod_limbs(mulf(r, x, cost, k), M, cost, k)[1]
    return to_int(r, k)


def word_ops(cost: Cost) -> int:
    return cost.total("add", "mul", "div", "cmp")
