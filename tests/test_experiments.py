import json
import unittest
from fractions import Fraction
from unittest.mock import patch

from polyia.experiments import run_registered, poly_divmod, poly_add, poly_mul, derivative


class ScientificContracts(unittest.TestCase):
    def test_exact_division_fraction_coefficients(self):
        a=[Fraction(1,3),Fraction(-7,5),Fraction(2,7),Fraction(9,2)]
        b=[Fraction(-2,3),Fraction(5,9)]
        q,r=poly_divmod(a,b)
        self.assertEqual(poly_add(poly_mul(b,q),r),a)
        self.assertTrue(r==[0] or len(r)<len(b))

    def test_short_dividend_and_constant_divisor(self):
        self.assertEqual(poly_divmod([Fraction(2)],[Fraction(1),Fraction(1)]),([Fraction(0)],[Fraction(2)]))
        self.assertEqual(poly_divmod([Fraction(2),Fraction(4)],[Fraction(2)]),([Fraction(1),Fraction(2)],[Fraction(0)]))

    def test_divide_by_zero_refused(self):
        self.assertEqual(run_registered('polynomial',{'b':[0]})['status'],'REFUSED')

    def test_quotient_derivative_certificate(self):
        r=run_registered('polynomial',{})
        self.assertEqual(r['status'],'PASS')
        self.assertTrue(all(c['pass'] for c in r['checks']))
        self.assertIn('b(x) != 0',' '.join(r['result']['domain']))
        self.assertEqual(r['result']['quotient'],['-1','1','1'])
        self.assertEqual(r['result']['remainder'],['3'])

    def test_input_coefficients_not_float_or_bool(self):
        for bad in (True,0.5,float('nan'),'9'*1000):
            with self.subTest(bad=str(bad)[:20]):
                self.assertEqual(run_registered('polynomial',{'a':[bad]})['status'],'REFUSED')

    def test_degree_budget(self):
        self.assertEqual(run_registered('polynomial',{'a':[1]*34})['status'],'REFUSED')

    def test_exponent_denial_happens_before_fraction_construction(self):
        with patch('polyia.experiments.Fraction', side_effect=AssertionError('unsafe numeric parser reached')):
            for value in ('1e1000000000', '1.2', '1_000', '0x10'):
                result=run_registered('polynomial',{'a':[value]})
                self.assertEqual(result['status'],'REFUSED')
                self.assertEqual(result['result']['reason'],'INVALID_RATIONAL')

    def test_integer_budget_precedes_decimal_string_conversion(self):
        result=run_registered('polynomial',{'a':[10**10000]})
        self.assertEqual(result['status'],'REFUSED')
        self.assertEqual(result['result']['reason'],'BUDGET')

    def test_zero_polynomial_no_vacuous_numerical_pass(self):
        r=run_registered('polynomial',{'a':[0],'b':[1,1]})
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(r['result']['quotient'],['0'])
        self.assertIn('EXACT',r['evidence_class'])

    def test_finite_grammar_promoted_and_expanded(self):
        r=run_registered('grammar-promotion',{})
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(r['result']['grammar'],r['result']['expanded_grammar'])
        self.assertTrue(r['result']['semantic_scope'].startswith('all words'))
        self.assertGreater(len(r['result']['generated']),1)
        self.assertEqual(len(r['result']['grammar_digest']),64)

    def test_grammar_bad_symbol_rejected(self):
        grammar={'kind':'finite','alphabet':['a'],'words':[['b']]}
        self.assertEqual(run_registered('grammar-promotion',{'grammar':grammar})['status'],'REFUSED')

    def test_grammar_order_and_identity_do_not_depend_on_dict_order(self):
        a={'kind':'finite','alphabet':['a','b'],'words':[['a'],['b']]}
        b={'words':[['a'],['b']],'alphabet':['a','b'],'kind':'finite'}
        self.assertEqual(run_registered('grammar-promotion',{'grammar':a})['result']['grammar_digest'],run_registered('grammar-promotion',{'grammar':b})['result']['grammar_digest'])

    def test_qpath_joint_inputs_and_exact_result(self):
        r=run_registered('qpath',{})
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(r['result']['values']['ratio']['value'],'5/2')
        self.assertEqual(r['result']['trace'][0]['input_ids'],{'left':'a','right':'b'})

    def test_qpath_missing_joint_premise_is_not_reachable(self):
        r=run_registered('qpath',{'inputs':[{'id':'a','type':'Rational','value':'1/2','context':'Q'}]})
        self.assertEqual(r['status'],'REFUSED')
        self.assertEqual(r['result']['reason'],'MISSING_JOINT_PREMISE')

    def test_qpath_context_mismatch_refused(self):
        r=run_registered('qpath',{'inputs':[{'id':'a','type':'Rational','value':'1/2','context':'R'},{'id':'b','type':'Rational','value':'1/3','context':'Q'}]})
        self.assertEqual(r['result']['reason'],'CONTEXT_MISMATCH')

    def test_qpath_type_mismatch_refused(self):
        r=run_registered('qpath',{'inputs':[{'id':'a','type':'Length','value':'1/2','context':'Q'},{'id':'b','type':'Rational','value':'1/3','context':'Q'}]})
        self.assertEqual(r['result']['reason'],'TYPE_MISMATCH')

    def test_qpath_zero_divisor_and_overwrite_refused(self):
        r=run_registered('qpath',{'inputs':[{'id':'a','type':'Rational','value':'1','context':'Q'},{'id':'b','type':'Rational','value':'0','context':'Q'}]})
        self.assertEqual(r['result']['reason'],'ZERO_DIVISOR')
        r=run_registered('qpath',{'steps':[{'op':'rational.add','inputs':{'left':'a','right':'b'},'output':'a'}]})
        self.assertEqual(r['result']['reason'],'IDENTITY_REUSE')

    def test_unknown_or_executable_parameters_refused(self):
        self.assertEqual(run_registered('__import__',{})['status'],'REFUSED')
        self.assertEqual(run_registered('polynomial',{'code':'print(1)'})['status'],'REFUSED')
        self.assertEqual(run_registered('acceptance',{'force_pass':True})['status'],'REFUSED')

    def test_acceptance_has_real_positive_and_negative_checks(self):
        r=run_registered('acceptance',{})
        self.assertEqual(r['status'],'PASS')
        self.assertGreaterEqual(len(r['checks']),10)
        self.assertTrue(all(c['pass'] for c in r['checks']))
        self.assertEqual(r,json.loads(json.dumps(r)))
        self.assertEqual(r,run_registered('acceptance',{}))


if __name__=='__main__':unittest.main()
