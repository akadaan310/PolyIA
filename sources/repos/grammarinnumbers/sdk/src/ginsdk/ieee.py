"""A reference simulator for IEEE 754 binary floating point (GIN-DEF-030 … GIN-DEF-032).

Every operation is computed *exactly* on rationals (``fractions.Fraction``) and then
rounded once to the target format with round-to-nearest, ties-to-even — the
default rounding attribute of IEEE 754-2019 — which is what the standard requires of
+, −, ×, ÷ and √.  Special values (±0, ±∞, NaN) and the five exception flags are
modelled explicitly:

    invalid, divideByZero, overflow, underflow, inexact

Scope and deliberate simplifications (stated, not hidden):

* Only round-to-nearest-even.  The other rounding-direction attributes are not modelled.
* NaN payloads and the sign of a generated NaN are not modelled; when comparing with
  hardware, any two NaNs are treated as equal.  Signaling NaNs *are* modelled to the
  extent that matters for flags: an operation on a signaling NaN raises ``invalid``
  and returns a quiet NaN (an omission found by GIN-EXP-005, then fixed).
* Tininess is detected *after rounding* by default (measured to be the behaviour of
  x86-64 SSE in GIN-EXP-005); ``tininess="before"`` is available (Arm, for example,
  documents detection before rounding).  IEEE 754 permits either for binary
  formats.  Under default exception handling, underflow is signalled when the result
  is tiny **and** inexact.

The simulator is validated against the host's hardware (binary32 and binary64,
results and flags) in GIN-EXP-005.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from fractions import Fraction

FLAGS = ("invalid", "divideByZero", "overflow", "underflow", "inexact")


@dataclass(frozen=True)
class Format:
    """A binary interchange-style format with ``ebits`` exponent bits and precision ``p``
    (significand bits including the hidden bit)."""

    name: str
    ebits: int
    p: int

    @property
    def emax(self) -> int:
        return 2 ** (self.ebits - 1) - 1

    @property
    def emin(self) -> int:
        return 1 - self.emax

    @property
    def bias(self) -> int:
        return self.emax

    @property
    def width(self) -> int:
        return 1 + self.ebits + self.p - 1

    @property
    def max_finite(self) -> Fraction:
        return Fraction(2 ** self.p - 1) * Fraction(2) ** (self.emax - self.p + 1)

    @property
    def min_normal(self) -> Fraction:
        return Fraction(2) ** self.emin

    @property
    def min_subnormal(self) -> Fraction:
        return Fraction(2) ** (self.emin - self.p + 1)


BINARY16 = Format("binary16", 5, 11)
BINARY32 = Format("binary32", 8, 24)
BINARY64 = Format("binary64", 11, 53)
MINI8 = Format("binary8 (1-4-3 teaching format)", 4, 4)


@dataclass(frozen=True)
class FP:
    """A floating-point datum: class ∈ {'finite', 'inf', 'nan'}, a sign bit, and for
    finite data an exact nonnegative magnitude (0 for signed zeros)."""

    fmt: Format
    cls: str
    sign: int = 0
    mag: Fraction = Fraction(0)
    signaling: bool = False

    # -- inspection ------------------------------------------------------------
    @property
    def is_nan(self) -> bool:
        return self.cls == "nan"

    @property
    def is_inf(self) -> bool:
        return self.cls == "inf"

    @property
    def is_zero(self) -> bool:
        return self.cls == "finite" and self.mag == 0

    def value(self) -> Fraction:
        """The exact rational value (finite data only)."""
        if self.cls != "finite":
            raise ValueError(f"{self} has no rational value")
        return -self.mag if self.sign else self.mag

    def __str__(self) -> str:
        if self.cls == "nan":
            return "NaN"
        if self.cls == "inf":
            return "-Infinity" if self.sign else "Infinity"
        if self.mag == 0:
            return "-0" if self.sign else "0"
        v = self.value()
        if v.denominator == 1 and abs(v.numerator) < 2 ** 53:
            return str(v.numerator)
        if self.fmt.p <= 53:
            return _shortest(self)
        return _short_decimal(v)

    def __repr__(self) -> str:
        return f"FP<{self.fmt.name} {self}>"

    # -- encoding ----------------------------------------------------------------
    def bits(self) -> int:
        f = self.fmt
        frac_bits = f.p - 1
        if self.cls == "nan":
            return (((1 << f.ebits) - 1) << frac_bits) | (1 << (frac_bits - 1))  # canonical quiet NaN, sign 0
        if self.cls == "inf":
            return (self.sign << (f.width - 1)) | (((1 << f.ebits) - 1) << frac_bits)
        if self.mag == 0:
            return self.sign << (f.width - 1)
        e = _floor_log2(self.mag)
        if e < f.emin:                                   # subnormal
            m = self.mag / Fraction(2) ** (f.emin - frac_bits)
            assert m.denominator == 1
            return (self.sign << (f.width - 1)) | int(m)
        m = self.mag / Fraction(2) ** (e - frac_bits)
        assert m.denominator == 1
        return (self.sign << (f.width - 1)) | ((e + f.bias) << frac_bits) | (int(m) - (1 << frac_bits))

    def fields(self) -> dict:
        """Sign, biased exponent and fraction fields as bit strings."""
        f = self.fmt
        b = self.bits()
        s = format(b, f"0{f.width}b")
        return {"sign": s[0], "exponent": s[1:1 + f.ebits], "fraction": s[1 + f.ebits:]}


def from_bits(fmt: Format, b: int) -> FP:
    frac_bits = fmt.p - 1
    sign = b >> (fmt.width - 1) & 1
    E = b >> frac_bits & ((1 << fmt.ebits) - 1)
    F = b & ((1 << frac_bits) - 1)
    if E == (1 << fmt.ebits) - 1:
        if F:
            return FP(fmt, "nan", sign, signaling=not (F >> (frac_bits - 1)) & 1)
        return FP(fmt, "inf", sign)
    if E == 0:
        return FP(fmt, "finite", sign, F * Fraction(2) ** (fmt.emin - frac_bits))
    return FP(fmt, "finite", sign, ((1 << frac_bits) + F) * Fraction(2) ** (E - fmt.bias - frac_bits))


def from_float(x: float, fmt: Format = BINARY64) -> tuple[FP, set]:
    """Convert a Python float (binary64) to ``fmt`` with correct rounding."""
    d = from_bits(BINARY64, struct.unpack("<Q", struct.pack("<d", x))[0])
    if fmt == BINARY64 or d.cls != "finite":
        return FP(fmt, d.cls, d.sign, d.mag), set()
    return round_exact(fmt, d.value(), d.sign)


def to_float(x: FP) -> float:
    """Exact conversion to a Python float (always possible for formats no wider than binary64)."""
    if x.is_nan:
        return math.nan
    if x.is_inf:
        return -math.inf if x.sign else math.inf
    v = float(x.mag)
    return -v if x.sign else v


def from_decimal(text: str, fmt: Format = BINARY64) -> tuple[FP, set]:
    """Correctly rounded conversion of a decimal literal such as '0.1'."""
    q = Fraction(text)
    return round_exact(fmt, q, 1 if text.strip().startswith("-") else 0)


def from_int(n: int, fmt: Format = BINARY64) -> tuple[FP, set]:
    return round_exact(fmt, Fraction(n), 1 if n < 0 else 0)


# ---------------------------------------------------------------------------
# rounding
# ---------------------------------------------------------------------------
def _floor_log2(x: Fraction) -> int:
    """⌊log₂ x⌋ for x > 0, exactly."""
    e = x.numerator.bit_length() - x.denominator.bit_length()
    if Fraction(2) ** e > x:
        e -= 1
    elif Fraction(2) ** (e + 1) <= x:
        e += 1
    return e


def _core(x: Fraction, p: int, emin: int | None) -> tuple[int, int, int]:
    """Round x > 0 to precision p with exponent floor emin (None: unbounded).

    Returns (m, qe, cmp) with result m·2^qe, where cmp is the sign of the discarded
    part relative to the rounding point (−1: exact... see below). We return
    (m, qe, inexact) with m possibly equal to 2^p after a carry (normalized by caller).
    """
    e = _floor_log2(x)
    if emin is not None:
        e = max(e, emin)
    qe = e - (p - 1)
    scaled = x / Fraction(2) ** qe
    m = scaled.numerator // scaled.denominator
    rem = scaled - m
    inexact = 1 if rem else 0
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and m % 2 == 1):
        m += 1
    if m == 2 ** p:
        m, qe = 2 ** (p - 1), qe + 1
    return m, qe, inexact


def round_exact(fmt: Format, q: Fraction, zero_sign: int = 0, tininess: str = "after") -> tuple[FP, set]:
    """Round the exact rational ``q`` to ``fmt`` (round to nearest, ties to even).

    ``zero_sign`` gives the sign of the result when q == 0 (the caller knows the
    IEEE rule that applies). Returns (datum, flags).
    """
    flags: set = set()
    if q == 0:
        return FP(fmt, "finite", zero_sign, Fraction(0)), flags
    sign = 1 if q < 0 else 0
    x = abs(q)
    m, qe, inexact = _core(x, fmt.p, fmt.emin)
    mag = m * Fraction(2) ** qe
    if inexact:
        flags.add("inexact")
    if mag >= Fraction(2) ** (fmt.emax + 1):
        flags |= {"overflow", "inexact"}
        return FP(fmt, "inf", sign), flags
    if tininess == "before":
        tiny = x < fmt.min_normal
    else:
        mu, qu, _ = _core(x, fmt.p, None)
        tiny = mu * Fraction(2) ** qu < fmt.min_normal
    if tiny and inexact:
        flags.add("underflow")
    return FP(fmt, "finite", sign, mag), flags


# ---------------------------------------------------------------------------
# operations
# ---------------------------------------------------------------------------
def _nan(fmt: Format) -> FP:
    return FP(fmt, "nan")


def _nan_operands(*xs: FP) -> tuple[FP, set]:
    """Quiet NaN result; ``invalid`` iff some operand is a signaling NaN."""
    return _nan(xs[0].fmt), ({"invalid"} if any(x.is_nan and x.signaling for x in xs) else set())


def add(x: FP, y: FP, tininess: str = "after") -> tuple[FP, set]:
    f = x.fmt
    if x.is_nan or y.is_nan:
        return _nan_operands(x, y)
    if x.is_inf and y.is_inf:
        if x.sign != y.sign:
            return _nan(f), {"invalid"}          # ∞ − ∞
        return x, set()
    if x.is_inf:
        return x, set()
    if y.is_inf:
        return y, set()
    q = x.value() + y.value()
    if q == 0:
        # exact zero sum: −0 only if both operands are −0 (round-to-nearest rule)
        zs = 1 if (x.is_zero and y.is_zero and x.sign and y.sign) else 0
        return FP(f, "finite", zs, Fraction(0)), set()
    return round_exact(f, q, tininess=tininess)


def neg(x: FP) -> FP:
    """Negation is a sign-bit operation: exact, no flags, NaNs keep their kind."""
    return FP(x.fmt, x.cls, 1 - x.sign, x.mag, x.signaling)


def sub(x: FP, y: FP, tininess: str = "after") -> tuple[FP, set]:
    if x.is_nan or y.is_nan:
        return _nan_operands(x, y)
    return add(x, neg(y), tininess)


def mul(x: FP, y: FP, tininess: str = "after") -> tuple[FP, set]:
    f = x.fmt
    s = x.sign ^ y.sign
    if x.is_nan or y.is_nan:
        return _nan_operands(x, y)
    if (x.is_inf and y.is_zero) or (y.is_inf and x.is_zero):
        return _nan(f), {"invalid"}              # 0 × ∞
    if x.is_inf or y.is_inf:
        return FP(f, "inf", s), set()
    if x.is_zero or y.is_zero:
        return FP(f, "finite", s, Fraction(0)), set()
    return round_exact(f, x.value() * y.value(), s, tininess)


def div(x: FP, y: FP, tininess: str = "after") -> tuple[FP, set]:
    f = x.fmt
    s = x.sign ^ y.sign
    if x.is_nan or y.is_nan:
        return _nan_operands(x, y)
    if x.is_inf and y.is_inf:
        return _nan(f), {"invalid"}              # ∞ / ∞
    if x.is_zero and y.is_zero:
        return _nan(f), {"invalid"}              # 0 / 0
    if x.is_inf:
        return FP(f, "inf", s), set()
    if y.is_inf:
        return FP(f, "finite", s, Fraction(0)), set()
    if y.is_zero:
        return FP(f, "inf", s), {"divideByZero"}  # finite nonzero / 0
    if x.is_zero:
        return FP(f, "finite", s, Fraction(0)), set()
    return round_exact(f, x.value() / y.value(), s, tininess)


def sqrt(x: FP) -> tuple[FP, set]:
    f = x.fmt
    if x.is_nan:
        return _nan_operands(x)
    if x.is_zero:
        return x, set()                           # √(±0) = ±0
    if x.sign:
        return _nan(f), {"invalid"}              # √(negative), including −∞
    if x.is_inf:
        return x, set()
    v = x.mag
    e = _floor_log2(v) // 2
    e = max(e, f.emin)
    qe = e - (f.p - 1)
    scaled = v / Fraction(4) ** qe               # (√v / 2^qe)² = scaled
    m = math.isqrt(scaled.numerator // scaled.denominator)
    half = (Fraction(2 * m + 1, 2)) ** 2
    inexact = scaled != m * m
    if scaled > half or (scaled == half and m % 2 == 1):
        m += 1
    if m == 2 ** f.p:
        m, qe = 2 ** (f.p - 1), qe + 1
    flags = {"inexact"} if inexact else set()
    return FP(f, "finite", 0, m * Fraction(2) ** qe), flags


OPS = {"+": add, "-": sub, "*": mul, "/": div}


def _shortest(x: "FP") -> str:
    """Shortest decimal string that rounds back to the same datum of x's format."""
    v = x.value()
    for digits in range(1, 18):
        txt = f"{float(v):.{digits}g}"
        if round_exact(x.fmt, Fraction(txt))[0].mag == x.mag:
            return txt.replace("e+", "e")
    return repr(float(v))


def _short_decimal(v: Fraction, digits: int = 9) -> str:
    return f"{float(v):.{digits}g}"


def ulp(x: FP) -> Fraction:
    """Unit in the last place of a finite datum (gap to the next larger magnitude)."""
    f = x.fmt
    if x.cls != "finite":
        raise ValueError("ulp of a non-finite datum")
    if x.mag == 0:
        return f.min_subnormal
    e = max(_floor_log2(x.mag), f.emin)
    return Fraction(2) ** (e - f.p + 1)


def smallest_unrepresentable_integer(fmt: Format) -> int:
    """The least positive integer not exactly representable: 2^p + 1 (GIN-PROP-030)."""
    return 2 ** fmt.p + 1
