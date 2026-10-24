"""UCG conformance suite (stdlib unittest).  python3 -m unittest discover -s tests -v"""
import json
import os
import sys
import unittest
from fractions import Fraction as Q

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucg import elements as E, forms as F, nomen as N, proleptic as P
from ucg import structures as S
from ucg.calc import C, D, X, add, d_orbit_rank, f, mul, orbit_class, pw, same
from ucg.integrate import Integrator


class Alphabet(unittest.TestCase):
    def test_positions_from_Z(self):
        T = {e["number"]: e for e in json.load(open(os.path.join(E.DATA, "periodic.json")))["elements"]}
        for Z in range(1, 119):
            p = E.position(Z)
            self.assertEqual(p["period"], T[Z]["period"], Z)
            self.assertEqual(p["block"], T[Z]["block"], Z)

    def test_madelung_exceptions_are_the_known_ones(self):
        r = json.load(open(os.path.join(os.path.dirname(E.DATA), "results", "e01.json")))
        self.assertIn("Cr", r["alphabet"]["config_exceptions"])
        self.assertIn("Cu", r["alphabet"]["config_exceptions"])
        self.assertNotIn("Fe", r["alphabet"]["config_exceptions"])

    def test_valence_and_ions(self):
        self.assertEqual(E.valences(8), [2])
        self.assertEqual(E.valences(16), [2, 4, 6])
        self.assertEqual(E.ionic_charge(11), 1)
        self.assertEqual(E.ionic_charge(17), -1)


class Forms(unittest.TestCase):
    def test_alkane_counts(self):
        self.assertEqual(F.alkane_skeletons(10)[0], [1, 1, 1, 2, 3, 5, 9, 18, 35, 75])

    def test_polya_matches_enumeration(self):
        rings = F.enumerate_rings(3, 5, "CNOS")
        for n in (3, 4, 5):
            self.assertEqual(sum(1 for v in rings.values() if v["n"] == n), F.polya_ring_count(n, 4, 2))

    def test_kekule_is_one_orbit(self):
        b = (("C", "="), ("C", "-")) * 3
        self.assertEqual(F.canon_ring(b), F.canon_ring(b[1:] + b[:1]))

    def test_huckel(self):
        benz = (("C", "="), ("C", "-")) * 3
        pyrrole = (("N", "-"), ("C", "="), ("C", "-"), ("C", "="), ("C", "-"))
        cpd = (("C", "-"), ("C", "="), ("C", "-"), ("C", "="), ("C", "-"))
        self.assertTrue(F.huckel(benz)[0])
        self.assertTrue(F.huckel(pyrrole)[0])
        self.assertFalse(F.huckel(cpd)[0])


class Nomenclature(unittest.TestCase):
    def test_element_names(self):
        self.assertEqual(N.element_name(118), "ununoctium")
        self.assertEqual(N.element_name(112), "ununbium")
        self.assertEqual(N.element_symbol(119), "Uue")
        for z in range(1, 1000):
            self.assertEqual(N.parse_element_name(N.element_name(z)), z)

    def test_alkane_name_roundtrip_and_normal_form(self):
        self.assertEqual(N.name_alkane(N.parse_alkane("2,2,4-trimethylpentane")), "2,2,4-trimethylpentane")
        self.assertEqual(N.name_alkane(N.parse_alkane("2-ethylpentane")), "3-methylhexane")
        with self.assertRaises(ValueError):
            N.parse_alkane("2,2,2-trimethylpropane")


class Calculus(unittest.TestCase):
    def test_derivative(self):
        self.assertTrue(same(D(mul(f("exp", X), f("sin", X))), add(mul(f("exp", X), f("sin", X)), mul(f("exp", X), f("cos", X)))))

    def test_orbits(self):
        self.assertEqual(orbit_class(f("exp", X))["class"], "periodic (complete)")
        self.assertEqual(orbit_class(pw(X, 3))["class"], "nilpotent (severed)")
        self.assertEqual(orbit_class(f("sin", X)).get("true_period"), 4)
        self.assertEqual(d_orbit_rank(f("sin", X), 6)[1], [1.0, 0.0, 1.0])
        self.assertIsNone(d_orbit_rank(f("ln", X), 6)[0])

    def test_integration_verified_or_refused(self):
        I = Integrator()
        for e in [mul(X, f("exp", X)), mul(C(2), X, f("cos", pw(X, 2))), pw(add(pw(X, 2), C(-1)), -1), mul(f("exp", X), f("sin", X)), f("atan", X)]:
            r = I.run(e)
            self.assertTrue(r["ok"], r["trace"])
            self.assertTrue(same(D(r["result"]), e))
        self.assertFalse(I.run(f("exp", mul(C(-1), pw(X, 2))))["ok"])


class Structures(unittest.TestCase):
    def test_butcher(self):
        self.assertEqual([len(S.rooted_trees(6)[n]) for n in range(1, 7)], [1, 1, 2, 4, 9, 20])
        self.assertEqual(S.tree_order(*S.TABLEAUX["rk4"])[0], 4)
        self.assertEqual(S.tree_order(*S.TABLEAUX["broken-rk4 (b perturbed)"])[0], 1)

    def test_groups(self):
        c, found = S.generate_groups(12, ("cyclic", "direct", "semidirect", "dicyclic", "semidirect_general"))
        self.assertEqual(c, [1, 1, 1, 2, 1, 2, 1, 5, 2, 2, 1, 5])
        self.assertTrue(all(G.is_group() for G in found.values()))

    def test_homology(self):
        self.assertEqual(S.betti(S.torus())[0], (1, 2, 1))
        self.assertEqual(S.betti(S.RP2)[0], (1, 0, 0))
        self.assertEqual(S.betti(S.RP2, 2)[0], (1, 1, 1))

    def test_linear_failures(self):
        self.assertEqual(S.solve_linear([[1, 2], [2, 4]], [3, 7])[0], "image failure")
        self.assertEqual(S.solve_linear([[1, 2], [2, 4]], [3, 6])[0], "kernel failure")


class Proleptics(unittest.TestCase):
    def test_ledger_verifies_and_seals_precede_witnesses(self):
        self.assertTrue(P.verify())
        lines = [json.loads(l) for l in P.LEDGER.read_text().splitlines()]
        sealed = set()
        for e in lines:
            if e["op"] == "SEAL":
                sealed.add(e["experiment"])
            else:
                self.assertIn(e["experiment"], sealed)


if __name__ == "__main__":
    unittest.main()
