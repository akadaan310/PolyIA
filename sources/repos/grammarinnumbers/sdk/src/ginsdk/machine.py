"""Machine and language semantics of integer arithmetic (GIN-DEF-033 … GIN-DEF-036).

"The machine" is not one thing.  This module models, *from their specifications*,
what several instruction sets and languages do with the same expression, in
particular with the two classical boundaries of fixed-width signed division:

    x / 0                     (division by zero)
    INT_MIN / −1              (the quotient 2^(w−1) is not representable)

Each model returns a :class:`MachineOutcome` that says whether a value was
produced, a trap/exception raised, or the behaviour is undefined, and cites the
specification clause it implements.  Models are validated against real executions
on the host where a toolchain exists (GIN-EXP-004); the AArch64 and RISC-V models
are *specification models only* (no hardware of those kinds was available).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MachineOutcome:
    kind: str               # 'value' | 'trap' | 'exception' | 'undefined' | 'special'
    value: object = None    # quotient (or result) when kind == 'value'
    remainder: object = None
    name: str = ""          # e.g. '#DE', 'ArithmeticException', 'SIGFPE'
    note: str = ""
    source: str = ""        # specification reference

    def __str__(self) -> str:
        if self.kind == "value":
            return f"{self.value}" + (f" (remainder {self.remainder})" if self.remainder is not None else "")
        return f"{self.kind}: {self.name}"


def wrap(x: int, w: int) -> int:
    """Two's-complement interpretation of x mod 2^w."""
    x &= (1 << w) - 1
    return x - (1 << w) if x >> (w - 1) else x


def trunc_div(a: int, b: int) -> tuple[int, int]:
    """Quotient rounded toward zero and the matching remainder (sign of the dividend)."""
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q, a - b * q


def floor_div(a: int, b: int) -> tuple[int, int]:
    return a // b, a % b


# ---------------------------------------------------------------------------
# signed integer division models, width w (default 32)
# ---------------------------------------------------------------------------
def div_x86(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "Intel SDM Vol. 2A, IDIV: #DE if the source operand is 0 or the quotient is too large"
    if b == 0:
        return MachineOutcome("trap", name="#DE (divide error)", note="hardware exception; Linux delivers SIGFPE", source=src)
    q, r = trunc_div(a, b)
    if q != wrap(q, w):
        return MachineOutcome("trap", name="#DE (divide error)", note="quotient not representable in w bits", source=src)
    return MachineOutcome("value", q, r, source=src)


def div_aarch64(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "Arm ARM (DDI 0487), SDIV: no divide-by-zero trap; result 0. INT_MIN/−1 returns INT_MIN"
    if b == 0:
        return MachineOutcome("value", 0, None, note="SDIV writes 0; no exception, no flag", source=src)
    q, r = trunc_div(a, b)
    return MachineOutcome("value", wrap(q, w), None, note="overflow wraps silently" if q != wrap(q, w) else "", source=src)


def div_riscv(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "RISC-V Unprivileged ISA, M extension: x/0 → −1 (all bits set), rem → x; overflow → −2^(w−1), rem 0"
    if b == 0:
        return MachineOutcome("value", -1, a, note="quotient has all bits set; remainder equals the dividend", source=src)
    q, r = trunc_div(a, b)
    if q != wrap(q, w):
        return MachineOutcome("value", wrap(q, w), 0, note="signed overflow: quotient −2^(w−1), remainder 0", source=src)
    return MachineOutcome("value", q, r, source=src)


def divu_riscv(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "RISC-V Unprivileged ISA, M extension (DIVU/REMU)"
    a &= (1 << w) - 1
    b &= (1 << w) - 1
    if b == 0:
        return MachineOutcome("value", (1 << w) - 1, a, note="quotient 2^w − 1, remainder = dividend", source=src)
    return MachineOutcome("value", a // b, a % b, source=src)


def div_c(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "ISO/IEC 9899 (C17) 6.5.5p5–6: behaviour undefined if the second operand is 0 or the quotient is not representable"
    if b == 0:
        return MachineOutcome("undefined", name="undefined behaviour", note="the program has no meaning; any outcome is permitted", source=src)
    q, r = trunc_div(a, b)
    if q != wrap(q, w):
        return MachineOutcome("undefined", name="undefined behaviour", note="INT_MIN / -1 overflows", source=src)
    return MachineOutcome("value", q, r, source=src)


def div_java(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "JLS §15.17.2: ArithmeticException on integer division by zero; Integer.MIN_VALUE / −1 == MIN_VALUE"
    if b == 0:
        return MachineOutcome("exception", name="ArithmeticException: / by zero", source=src)
    q, r = trunc_div(a, b)
    return MachineOutcome("value", wrap(q, w), wrap(r, w), source=src)


def div_rust(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "Rust reference, arithmetic operators: integer division by zero panics; i32::MIN / −1 panics (overflow)"
    if b == 0:
        return MachineOutcome("exception", name="panic: attempt to divide by zero", source=src)
    q, r = trunc_div(a, b)
    if q != wrap(q, w):
        return MachineOutcome("exception", name="panic: attempt to divide with overflow", source=src)
    return MachineOutcome("value", q, r, source=src)


def div_go(a: int, b: int, w: int = 32) -> MachineOutcome:
    src = "Go spec, Integer operators: run-time panic on division by zero; most negative / −1 == most negative (no panic)"
    if b == 0:
        return MachineOutcome("exception", name="panic: runtime error: integer divide by zero", source=src)
    q, r = trunc_div(a, b)
    return MachineOutcome("value", wrap(q, w), wrap(r, w), source=src)


def div_python_floor(a: int, b: int, w: int | None = None) -> MachineOutcome:
    src = "Python language reference, binary arithmetic operations: // floors; ZeroDivisionError on zero divisor"
    if b == 0:
        return MachineOutcome("exception", name="ZeroDivisionError: integer division or modulo by zero", source=src)
    q, r = floor_div(a, b)
    return MachineOutcome("value", q, r, note="unbounded integers: no overflow", source=src)


def div_js_bigint(a: int, b: int, w: int | None = None) -> MachineOutcome:
    src = "ECMAScript BigInt::divide: RangeError if the divisor is 0n; truncates toward zero"
    if b == 0:
        return MachineOutcome("exception", name="RangeError: Division by zero", source=src)
    q, r = trunc_div(a, b)
    return MachineOutcome("value", q, r, source=src)


INT_DIV_MODELS = {
    "x86-64 IDIV": div_x86,
    "AArch64 SDIV": div_aarch64,
    "RISC-V DIV": div_riscv,
    "ISO C (int)": div_c,
    "Java (int)": div_java,
    "Rust (i32)": div_rust,
    "Go (int32)": div_go,
    "Python (//)": div_python_floor,
    "JavaScript (BigInt)": div_js_bigint,
}


# ---------------------------------------------------------------------------
# fixed-width addition: wrap, trap, saturate, undefined
# ---------------------------------------------------------------------------
def add_fixed(a: int, b: int, w: int, policy: str) -> MachineOutcome:
    """Signed w-bit addition under an overflow policy: 'wrap', 'saturate', 'trap', 'c-undefined'."""
    exact = a + b
    lo, hi = -(1 << (w - 1)), (1 << (w - 1)) - 1
    if lo <= exact <= hi:
        return MachineOutcome("value", exact)
    if policy == "wrap":
        return MachineOutcome("value", wrap(exact, w), note="result reduced mod 2^w (overflow flag set on most ISAs)")
    if policy == "saturate":
        return MachineOutcome("value", hi if exact > hi else lo, note="clamped to the representable range")
    if policy == "trap":
        return MachineOutcome("exception", name="overflow", note="checked arithmetic (e.g. Rust debug build, C# checked)")
    if policy == "c-undefined":
        return MachineOutcome("undefined", name="undefined behaviour", note="C17 6.5p5: signed overflow is undefined")
    raise ValueError(policy)


def mod_hardware_word(a: int, b: int, w: int = 32) -> MachineOutcome:
    """Unsigned w-bit wraparound subtraction a − b: the Z/2^w answer to '0 − 1'."""
    return MachineOutcome("value", (a - b) % (1 << w), note=f"arithmetic in Z/2^{w}")
