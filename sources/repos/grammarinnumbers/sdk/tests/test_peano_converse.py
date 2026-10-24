import math
import unittest
from fractions import Fraction

from ginsdk import converse as C
from ginsdk import peano as P
from ginsdk.cost import Cost


class TestPeano(unittest.TestCase):
    def test_terms(self):
        self.assertEqual(P.term(3), "S(S(S(0)))")
        for n in range(30):
            self.assertEqual(P.parse_term(P.term(n)), n)
        with self.assertRaises(ValueError):
            P.parse_term("S(S(0)")

    def test_rule_counts(self):
        for m in range(8):
            for n in range(8):
                c = Cost()
                self.assertEqual(P.add(m, n, c), m + n)
                self.assertEqual(c["rule"], n + 1)
                c = Cost()
                self.assertEqual(P.mul(m, n, c), m * n)
                self.assertEqual(c["rule"], n * m + 2 * n + 1)

    def test_monus_is_not_converse(self):
        self.assertEqual(P.monus(0, 1), 0)
        self.assertEqual(C.subtract(0, 1, "N").kind, C.NONE)

    def test_church(self):
        for n in range(10):
            self.assertEqual(P.unchurch(P.church(n)), n)

    def test_segments(self):
        self.assertTrue(P.parse_segment("0{1,2,3}4").ok)
        self.assertTrue(P.parse_segment("3{}4").ok)
        self.assertIn("misses [2]", P.parse_segment("0{1,3}4").diagnosis)
        self.assertIn("need a < b", P.parse_segment("4{}4").diagnosis)
        self.assertIn("order", P.parse_segment("0{2,1,3}4").diagnosis)
        s = P.Segment(0, 4)
        self.assertEqual(s.run(0, "SSSS"), 4)
        self.assertIsNone(s.run(0, "SSSSS"))
        self.assertIsNone(s.run(0, "P"))
        self.assertEqual(s.notation(), "0{1,2,3}4")


class TestConverse(unittest.TestCase):
    def test_division_trichotomy(self):
        self.assertEqual(C.divide(6, 3).value, 2)
        self.assertEqual(C.divide(0, 1).value, 0)
        self.assertEqual(C.divide(1, 0).kind, C.NONE)
        self.assertEqual(C.divide(0, 0).kind, C.MULTIPLE)
        self.assertEqual(C.divide(7, 2, "Z").kind, C.NONE)
        self.assertEqual(C.divide(7, 2, "Q").value, Fraction(7, 2))

    def test_ring_theorem_exhaustive(self):
        # GIN-THM-002: in Z/n, Sol(a, b) is empty or a coset of Ann(b), of size gcd(b, n)
        for n in range(1, 41):
            for b in range(n):
                ann = C.annihilator_mod(b, n)
                self.assertEqual(len(ann), math.gcd(b, n))
                for a in range(n):
                    brute = [c for c in range(n) if b * c % n == a]
                    s = C.divide_mod(a, b, n)
                    self.assertEqual(sorted(s.solutions), brute)
                    if brute:
                        self.assertEqual(sorted((brute[0] + t) % n for t in ann), brute)

    def test_roots_and_logs(self):
        self.assertEqual(C.square_root(-1, "R").kind, C.NONE)
        self.assertEqual(C.square_root(-1, "C").kind, C.MULTIPLE)
        self.assertEqual(C.square_root(2, "Q").kind, C.NONE)
        self.assertEqual(C.square_root(4, "Q").kind, C.MULTIPLE)
        self.assertEqual(C.square_root(4, "N").value, 2)
        self.assertEqual(C.logarithm(0, "C").kind, C.NONE)
        self.assertEqual(C.logarithm(1, "C").kind, C.MULTIPLE)
        self.assertEqual(C.modular_inverse(3, 7).value, 5)
        self.assertEqual(C.modular_inverse(2, 6).kind, C.NONE)

    def test_pairs_projective_line(self):
        inf, zero, one = C.pair_of("∞"), C.pair_of(0), C.pair_of(1)
        self.assertEqual(str(C.pair_div(one, zero)), "∞")
        for v in (C.pair_div(zero, zero), C.pair_mul(zero, inf), C.pair_add(inf, inf), C.pair_div(inf, inf)):
            self.assertEqual(v.kind, "null")
        self.assertEqual(str(C.pair_div(one, inf)), "0")
        self.assertTrue(C.related(C.Pair(1, 0), C.Pair(0, 0)) and C.related(C.Pair(0, 0), C.Pair(0, 1)))
        self.assertFalse(C.related(C.Pair(1, 0), C.Pair(0, 1)))

    def test_zero_inverse_collapses(self):
        for n in range(1, 30):
            has = C.zero_inverse_collapses(list(range(n)), lambda x, y: (x + y) % n, lambda x, y: x * y % n, 0, 1 % n)
            self.assertEqual(has, n == 1)


if __name__ == "__main__":
    unittest.main()
