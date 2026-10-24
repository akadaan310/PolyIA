import math
import random
import unittest

from ginsdk import expr as E
from ginsdk import numbertheory as T


class TestNumberTheory(unittest.TestCase):
    def test_euclid_and_lame(self):
        for a in range(0, 300):
            for b in range(0, 300):
                self.assertEqual(T.gcd(a, b), math.gcd(a, b))
        for k in range(1, 25):
            a, b = T.lame_worst_pair(k)
            self.assertEqual(T.euclid_steps(a, b), k)
        # Lamé: the smallest a with k steps (a > b > 0) is F_{k+2}
        best = {}
        for a in range(1, 400):
            for b in range(1, a):
                k = T.euclid_steps(a, b)
                best.setdefault(k, a)
        for k, a in best.items():
            self.assertEqual(a, T.fibonacci(k + 2))

    def test_bezout(self):
        r = random.Random(1)
        for _ in range(2000):
            a, b = r.randint(0, 10 ** 9), r.randint(0, 10 ** 9)
            if a == b == 0:
                continue
            g, s, t = T.bezout(a, b)
            self.assertEqual(g, math.gcd(a, b))
            self.assertEqual(s * a + t * b, g)

    def test_binary_gcd(self):
        r = random.Random(2)
        for _ in range(1000):
            a, b = r.getrandbits(64), r.getrandbits(64)
            self.assertEqual(T.binary_gcd_trace(a, b)[0], math.gcd(a, b))

    def test_crt(self):
        self.assertEqual(T.crt([2, 3, 2], [3, 5, 7]), (23, 105))
        self.assertIsNone(T.crt([1, 2], [4, 6]))
        self.assertEqual(T.crt([1, 3], [4, 6]), (9, 12))
        r = random.Random(4)
        for _ in range(500):
            ms = [r.randint(1, 30) for _ in range(3)]
            rs = [r.randint(0, m - 1) for m in ms]
            L = math.lcm(*ms)
            brute = [x for x in range(L) if all(x % m == rr for m, rr in zip(ms, rs))]
            got = T.crt(rs, ms)
            self.assertEqual(brute, [] if got is None else [got[0]])

    def test_powmod_program(self):
        for e in range(0, 300):
            v, rows = T.powmod_trace(7, e, 1000003)
            self.assertEqual(v, pow(7, e, 1000003))
            c = T.powmod_count(e)
            self.assertEqual(sum(1 for r in rows if "S" in r[1]), c["square"])
            self.assertEqual(sum(1 for r in rows if r[1] == "SM"), c["multiply"])

    def test_primes(self):
        ps = T.sieve(20000)
        self.assertEqual(len(ps), 2262)
        s = set(ps)
        for n in range(20001):
            self.assertEqual(T.is_prime(n), n in s)
            if n < 3000:
                self.assertEqual(T.is_prime_trial(n), n in s)
        self.assertTrue(T.fermat_test(341, 2))       # pseudoprime
        self.assertTrue(T.is_carmichael(561))
        self.assertFalse(T.strong_probable_prime(341, 2))
        self.assertEqual(T.factorize(2 ** 64 + 1), {274177: 1, 67280421310721: 1})

    def test_arith_functions(self):
        self.assertEqual(T.phi(36), 12)
        self.assertEqual(T.mobius(30), -1)
        self.assertEqual(T.mobius(12), 0)
        self.assertEqual(T.sigma(28), 56)


class TestExpr(unittest.TestCase):
    def test_canonical_examples(self):
        cases = {
            ("1 + 1", "N"): ("value", "2"), ("6 / 3", "Q"): ("value", "2"), ("0 / 1", "Q"): ("value", "0"),
            ("1 / 0", "Q"): ("no-solution", None), ("0 / 0", "Q"): ("non-unique", None),
            ("0 - 1", "N"): ("no-solution", None), ("0 - 1", "Z"): ("value", "-1"),
            ("1 / 0", "binary64"): ("special", "Infinity"), ("0 / 0", "binary64"): ("special", "NaN"),
            ("1 / -0", "binary64"): ("special", "-Infinity"),
            ("1 / 0", "Python"): ("exception", None), ("1 / 0", "int32 x86-64"): ("trap", None),
            ("1 / 0", "int32 AArch64"): ("value", "0"), ("1 / 0", "int32 RISC-V"): ("value", "-1"),
            ("1 / 0", "int32 C"): ("undefined", None), ("1 / 0", "int32 Java"): ("exception", None),
            ("2147483647 + 1", "int32 Java"): ("value", "-2147483648"),
            ("2147483647 + 1", "int32 C"): ("undefined", None),
            ("(-2147483647 - 1) / -1", "int32 x86-64"): ("trap", None),
            ("(-2147483647 - 1) / -1", "int32 RISC-V"): ("value", "-2147483648"),
            ("2 / 4", "Z/6"): ("non-unique", None), ("3 / 2", "Z/7"): ("value", "5"),
            ("1 + 1", "binary64"): ("value", "2"), ("0b1 + 0b1", "N"): ("value", "2"),
            ("x / x", "symbolic"): ("value", "1"), ("x / 0", "symbolic"): ("no-solution", None),
            ("sqrt(-1)", "C"): ("value", "i"), ("sqrt(-1)", "R"): ("no-solution", None),
            ("1 +", "Q"): ("syntax-error", None), ("0.5", "Z"): ("not-in-domain", None),
            ("2^3^2", "N"): ("value", "512"), ("-2^2", "Z"): ("value", "-4"),
            ("7 mod 3", "Z"): ("value", "1"), ("-7 // 2", "Z"): ("value", "-4"), ("-7 // 2", "Python"): ("value", "-4"),
            ("-7 / 2", "int32 x86-64"): ("value", "-3"),
            # regression (GIN-NEG-013): exponents are integers acting on the domain, not residues
            ("0^-1", "Z/6"): ("no-solution", None), ("3^-1", "Z/7"): ("value", "5"), ("2^-1", "Z/6"): ("no-solution", None),
            ("2^0.5", "Q"): ("not-in-domain", None), ("(2/3)^-2", "Q"): ("value", "9/4"),
        }
        for (src, dom), (status, disp) in cases.items():
            o = E.evaluate(src, dom)
            self.assertEqual(o.status, status, o.headline())
            if disp is not None:
                self.assertEqual(o.display, disp, o.headline())

    def test_every_failure_has_a_reason(self):
        for src in ["1/0", "0/0", "0-1", "sqrt(-4)", "7/2", "1+", "2147483647*2", "x/0", "0^-1"]:
            for o in E.compare(src):
                if o.status != "value":
                    self.assertTrue(o.reason, o.headline())
                    self.assertIsNotNone(o.layer)

    def test_parse_tree(self):
        t = E.parse("1 + 2 * 3").tree()
        self.assertEqual(t["label"], "+")
        self.assertEqual(t["children"][1]["label"], "*")


if __name__ == "__main__":
    unittest.main()
