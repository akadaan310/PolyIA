import math
import random
import unittest

from ginsdk import bigint as B
from ginsdk import circuits as K
from ginsdk.cost import Cost


class TestCircuits(unittest.TestCase):
    def test_adders_exhaustive(self):
        for n in range(1, 7):
            for name, make in K.ADDERS.items():
                c = make(n)
                for x in range(2 ** n):
                    for y in range(2 ** n):
                        self.assertEqual(K.int_of(K.apply_words(c, a=(x, n), b=(y, n))), x + y, (name, n))

    def test_ripple_formulas(self):
        for n in range(2, 40):
            c = K.ripple_adder(n)
            self.assertEqual(c.size, 5 * n - 3)
            self.assertEqual(c.depth(), 2 * n - 1)

    def test_prefix_depth_logarithmic(self):
        for n in (8, 16, 32, 64):
            self.assertLessEqual(K.kogge_stone_adder(n).depth(), 2 * math.ceil(math.log2(n)) + 2)

    def test_full_adders(self):
        for c in (K.full_adder(), K.full_adder_nand()):
            for v in range(8):
                a, b, ci = v & 1, v >> 1 & 1, v >> 2
                self.assertEqual(c.run(dict(a=a, b=b, cin=ci)), [(a + b + ci) & 1, (a + b + ci) >> 1])
        self.assertEqual(K.full_adder_nand().size, 9)

    def test_carry_monoid(self):
        E = K.CARRY_ELEMENTS
        for x in E:
            for y in E:
                for z in E:
                    self.assertEqual(K.carry_compose(K.carry_compose(x, y), z), K.carry_compose(x, K.carry_compose(y, z)))
            self.assertEqual(K.carry_compose(x, "P"), x)
            self.assertEqual(K.carry_compose("P", x), x)
        r = random.Random(3)
        for _ in range(500):
            n = r.randint(1, 40)
            x, y = r.getrandbits(n), r.getrandbits(n)
            acc = "P"
            cs = K.carries(x, y, n)
            for i in range(n):
                acc = K.carry_compose(acc, K.carry_class(x >> i & 1, y >> i & 1))
                self.assertEqual({"K": 0, "G": 1, "P": 0}[acc], cs[i + 1])

    def test_mul_sub_div_exhaustive(self):
        for n in range(1, 6):
            m, s, d = K.array_multiplier(n), K.subtractor(n), K.restoring_divider(n)
            for x in range(2 ** n):
                for y in range(2 ** n):
                    self.assertEqual(K.int_of(K.apply_words(m, a=(x, n), b=(y, n))), x * y)
                    o = K.apply_words(s, a=(x, n), b=(y, n))
                    self.assertEqual((K.int_of(o[:n]), o[n]), ((x - y) % 2 ** n, int(x >= y)))
                    q, rem = K.run_divider(d, n, x, y)
                    self.assertEqual((q, rem), divmod(x, y) if y else (2 ** n - 1, x))

    def test_inadmissible_connection(self):
        c = K.Circuit("bad")
        c.input("a")
        with self.assertRaises(ValueError):
            c.gate("AND", "a", "nowhere")


class TestBigint(unittest.TestCase):
    def test_against_python(self):
        r = random.Random(5)
        for _ in range(1500):
            k = r.choice([8, 16, 32])
            a, b = r.getrandbits(r.randint(0, 500)), r.getrandbits(r.randint(0, 300))
            A, Bv = B.from_int(a, k), B.from_int(b, k)
            self.assertEqual(B.to_int(B.add(A, Bv, None, k), k), a + b)
            self.assertEqual(B.to_int(B.mul_school(A, Bv, None, k), k), a * b)
            self.assertEqual(B.to_int(B.mul_karatsuba(A, Bv, None, k, threshold=2), k), a * b)
            if b:
                q, rr = B.divmod_limbs(A, Bv, None, k)
                self.assertEqual((B.to_int(q, k), B.to_int(rr, k)), divmod(a, b))
            self.assertEqual(B.gcd_binary(a, b), math.gcd(a, b))

    def test_schoolbook_counts(self):
        for n in (1, 3, 10):
            c = Cost()
            B.mul_school([1] * n, [1] * n, c)
            self.assertEqual(c["mul"], n * n)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            B.divmod_limbs([5], [])


if __name__ == "__main__":
    unittest.main()
