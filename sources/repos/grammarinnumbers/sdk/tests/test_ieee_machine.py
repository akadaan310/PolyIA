import math
import random
import struct
import unittest
from fractions import Fraction

from ginsdk import ieee as I
from ginsdk import machine as M


def f64(x):
    return I.from_float(x)[0]


class TestIEEE(unittest.TestCase):
    def test_roundtrip_bits(self):
        r = random.Random(7)
        for _ in range(5000):
            b = r.getrandbits(64)
            x = I.from_bits(I.BINARY64, b)
            if not x.is_nan:
                self.assertEqual(x.bits(), b)
        for b in range(1 << 16):
            x = I.from_bits(I.BINARY16, b)
            if not x.is_nan:
                self.assertEqual(x.bits(), b)
                self.assertEqual(I.to_float(x), struct.unpack("<e", struct.pack("<H", b))[0])

    def test_against_host_binary64(self):
        r = random.Random(11)
        def rnd():
            k = r.random()
            if k < 0.1:
                return r.choice([0.0, -0.0, 1.0, -1.0, 5e-324, 2.2250738585072014e-308, 1.7976931348623157e308, math.inf, -math.inf])
            return struct.unpack("<d", struct.pack("<Q", r.getrandbits(64)))[0]
        for _ in range(20000):
            a, b = rnd(), rnd()
            if math.isnan(a) or math.isnan(b):
                continue
            for op, fn in (("+", lambda x, y: x + y), ("-", lambda x, y: x - y), ("*", lambda x, y: x * y), ("/", lambda x, y: x / y)):
                if op == "/" and b == 0:
                    continue
                try:
                    host = fn(a, b)
                except OverflowError:
                    continue
                sim = I.to_float(I.OPS[op](f64(a), f64(b))[0])
                if math.isnan(host):
                    self.assertTrue(math.isnan(sim))
                else:
                    self.assertEqual(struct.pack("<d", host), struct.pack("<d", sim), (a, op, b))
            if a >= 0:
                self.assertEqual(struct.pack("<d", math.sqrt(a)), struct.pack("<d", I.to_float(I.sqrt(f64(a))[0])), a)

    def test_specials(self):
        one, zero, nzero = f64(1.0), f64(0.0), f64(-0.0)
        v, fl = I.div(one, zero)
        self.assertTrue(v.is_inf and v.sign == 0 and fl == {"divideByZero"})
        v, fl = I.div(one, nzero)
        self.assertTrue(v.is_inf and v.sign == 1)
        v, fl = I.div(zero, zero)
        self.assertTrue(v.is_nan and fl == {"invalid"})
        v, fl = I.mul(zero, I.div(one, zero)[0])
        self.assertTrue(v.is_nan and fl == {"invalid"})      # 0 · ∞ is not 1: ∞ does not solve 0·c = 1
        v, fl = I.add(f64(math.inf), f64(-math.inf))
        self.assertTrue(v.is_nan and "invalid" in fl)
        self.assertEqual(I.add(nzero, nzero)[0].sign, 1)
        self.assertEqual(I.add(zero, nzero)[0].sign, 0)

    def test_representation_boundary(self):
        p = I.BINARY64.p
        self.assertEqual(I.smallest_unrepresentable_integer(I.BINARY64), 2 ** 53 + 1)
        for n in range(2 ** p - 3, 2 ** p + 1):
            self.assertEqual(I.from_int(n)[0].value(), n)
        self.assertNotEqual(I.from_int(2 ** p + 1)[0].value(), 2 ** p + 1)
        v, fl = I.from_decimal("0.1")
        self.assertIn("inexact", fl)
        self.assertEqual(v.value(), Fraction(0.1))

    def test_overflow_underflow_flags(self):
        big = I.from_float(1.7976931348623157e308)[0]
        v, fl = I.add(big, big)
        self.assertTrue(v.is_inf and {"overflow", "inexact"} <= fl)
        tiny = I.from_float(5e-324)[0]
        v, fl = I.div(tiny, I.from_float(2.0)[0])
        self.assertTrue(v.is_zero and {"underflow", "inexact"} <= fl)


class TestMachine(unittest.TestCase):
    MIN = -(2 ** 31)

    def test_division_models(self):
        self.assertEqual(M.div_x86(1, 0).kind, "trap")
        self.assertEqual(M.div_x86(self.MIN, -1).kind, "trap")
        self.assertEqual(M.div_aarch64(1, 0).value, 0)
        self.assertEqual(M.div_aarch64(self.MIN, -1).value, self.MIN)
        self.assertEqual((M.div_riscv(7, 0).value, M.div_riscv(7, 0).remainder), (-1, 7))
        self.assertEqual((M.div_riscv(self.MIN, -1).value, M.div_riscv(self.MIN, -1).remainder), (self.MIN, 0))
        self.assertEqual(M.divu_riscv(7, 0).value, 2 ** 32 - 1)
        self.assertEqual(M.div_c(1, 0).kind, "undefined")
        self.assertEqual(M.div_java(self.MIN, -1).value, self.MIN)
        self.assertEqual(M.div_rust(self.MIN, -1).kind, "exception")
        self.assertEqual(M.div_python_floor(-7, 2).value, -4)
        self.assertEqual(M.div_x86(-7, 2).value, -3)

    def test_wrap(self):
        self.assertEqual(M.add_fixed(2 ** 31 - 1, 1, 32, "wrap").value, self.MIN)
        self.assertEqual(M.add_fixed(2 ** 31 - 1, 1, 32, "saturate").value, 2 ** 31 - 1)
        self.assertEqual(M.add_fixed(2 ** 31 - 1, 1, 32, "c-undefined").kind, "undefined")


if __name__ == "__main__":
    unittest.main()
