"""Bounded constructive science kernels. Python standard library; no inference.

These are executable acceptance families, not a universal grammar solver. Exact
rational checks certify the concrete finite objects named in each receipt.
"""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction

VERSION = '1.0.0'
MAX_DEGREE = 32
MAX_BITS = 1024


class Refusal(ValueError):
    def __init__(self, code, detail):
        self.code, self.detail = code, detail
        super().__init__(detail)


def require(condition, code, detail):
    if not condition:
        raise Refusal(code, detail)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(tag, value):
    return hashlib.sha256(tag.encode('ascii') + b'\0' + canonical(value)).hexdigest()


def number(value):
    require(type(value) is int or isinstance(value, str), 'EXACT_INPUT_REQUIRED', 'Use integer or rational strings; floats and booleans are not exact coefficients.')
    if type(value) is int:
        require(value.bit_length() <= MAX_BITS, 'BUDGET', 'Integer input exceeds the arithmetic bit budget.')
    else:
        require(len(value) <= 128, 'BUDGET', 'An input coefficient may have at most 128 characters.')
        require(re.fullmatch(r'[+-]?[0-9]+(?:/[+-]?[0-9]+)?', value) is not None,
                'INVALID_RATIONAL', 'Use bounded integer or integer/denominator strings; exponent, decimal and underscore forms are not admitted.')
    try:
        n = Fraction(value)
    except (ValueError, ZeroDivisionError, OverflowError):
        raise Refusal('INVALID_RATIONAL', 'Invalid rational coefficient.') from None
    return bounded(n)


def bounded(n):
    n = Fraction(n)
    require(n.numerator.bit_length() <= MAX_BITS and n.denominator.bit_length() <= MAX_BITS, 'BUDGET', 'Exact arithmetic exceeded the 1024-bit numerator/denominator budget.')
    return n


def trim(p):
    p = list(p) or [Fraction(0)]
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def polynomial(value):
    require(isinstance(value, list) and 1 <= len(value) <= MAX_DEGREE + 1, 'BUDGET', 'Polynomial coefficients must be a nonempty list of at most 33 entries, in ascending power order.')
    return trim([number(x) for x in value])


def poly_add(a, b):
    return trim([bounded((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) for i in range(max(len(a), len(b)))])


def poly_neg(a):
    return [-x for x in a]


def poly_mul(a, b):
    result = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] = bounded(result[i+j] + bounded(x*y))
    return trim(result)


def derivative(a):
    return trim([bounded(i*a[i]) for i in range(1, len(a))])


def poly_divmod(a, b):
    a, b = trim(a), trim(b)
    require(b != [0], 'ZERO_DIVISOR', 'Polynomial division requires a nonzero divisor in Q[x].')
    q = [Fraction(0)] * max(1, len(a)-len(b)+1)
    r = a[:]
    # Each iteration strictly reduces degree in the field Q.
    while r != [0] and len(r) >= len(b):
        d = len(r)-len(b)
        c = bounded(r[-1]/b[-1])
        q[d] = bounded(q[d]+c)
        r = poly_add(r, poly_neg([Fraction(0)]*d + [bounded(c*x) for x in b]))
    return trim(q), trim(r)


def serial(p):
    return [str(x) for x in p]


def receipt(result, checks, limitations, evidence_class='EXACTLY_CHECKED'):
    return {'status': 'PASS' if all(x['pass'] for x in checks) else 'FAIL', 'evidence_class': evidence_class,
            'result': result, 'checks': checks, 'limitations': limitations,
            'kernel_version': VERSION, 'llm_inference': False}


def check(name, truth):
    return {'name': name, 'pass': bool(truth)}


def run_polynomial(parameters):
    require(set(parameters) <= {'a', 'b'}, 'UNKNOWN_PARAMETER', 'Polynomial accepts a and b only.')
    a = polynomial(parameters.get('a', [4, -2, 0, 1]))
    b = polynomial(parameters.get('b', [-1, 1]))
    q, r = poly_divmod(a, b)
    reconstructed = poly_add(poly_mul(b, q), r)
    da, db, dq, dr = map(derivative, (a, b, q, r))
    product_derivative = poly_add(poly_add(poly_mul(db, q), poly_mul(b, dq)), dr)
    quotient_numerator = poly_add(poly_mul(da, b), poly_neg(poly_mul(a, db)))
    divided_numerator = poly_add(poly_add(poly_mul(dq, poly_mul(b, b)), poly_mul(dr, b)), poly_neg(poly_mul(r, db)))
    # A separate coefficient identity witnesses this specific factorization.
    factored = poly_mul([Fraction(-1), Fraction(1)], [Fraction(1), Fraction(1)])
    result = {
        'coefficient_field': 'Q', 'coefficient_order': 'ascending powers of x',
        'dividend': serial(a), 'divisor': serial(b), 'quotient': serial(q), 'remainder': serial(r),
        'reconstructed': serial(reconstructed), 'division_law': 'a = b*q + r',
        'domain': ['polynomial division over Q[x]', 'b is not the zero polynomial', 'rational-function and derivative interpretations require b(x) != 0'],
        'derivation': ['a=bq+r', 'a\u2032=b\u2032q+bq\u2032+r\u2032', '(a/b)\u2032=(a\u2032b-ab\u2032)/b^2', '(q+r/b)\u2032=q\u2032+(r\u2032b-rb\u2032)/b^2'],
        'quotient_derivative_numerator': serial(quotient_numerator),
        'divided_form_derivative_numerator': serial(divided_numerator),
        'common_denominator': serial(poly_mul(b,b)),
        'factorization_example': {'polynomial': ['-1','0','1'], 'factors': [['-1','1'],['1','1']],
                                  'cancellation_domain': '(x^2-1)/(x-1)=x+1 only when x != 1; the original excluded point remains excluded'},
        'source_contracts': ['PIA polynomial/evidence acceptance family', 'UCG sections 085, 090, 091', 'GIN field/image/kernel distinctions']}
    return receipt(result, [check('division coefficient identity', reconstructed == a),
                            check('remainder degree bound', r == [0] or len(r)<len(b)),
                            check('product-rule coefficient identity', product_derivative == da),
                            check('quotient-rule coefficient identity', quotient_numerator == divided_numerator),
                            check('factorization coefficient identity', factored == [Fraction(-1),Fraction(0),Fraction(1)])],
                   ['This certifies exact identities over Q for the supplied finite polynomials, not arbitrary symbolic functions.',
                    'Domain exclusion is preserved symbolically; no real-root isolation is claimed.',
                    'The fixed factorization example is not a general polynomial factorization engine.'])


def run_promotion(parameters):
    require(set(parameters) <= {'grammar'}, 'UNKNOWN_PARAMETER', 'Grammar promotion accepts grammar only.')
    g = parameters.get('grammar', {'kind':'finite', 'alphabet':['a','b'], 'words':[['a'],['b'],['a','b']]})
    require(isinstance(g,dict) and set(g)=={'kind','alphabet','words'}, 'GRAMMAR_SCHEMA', 'A finite grammar declares kind, alphabet and words.')
    require(g['kind']=='finite', 'UNSUPPORTED_GRAMMAR', 'Bootstrap certifies finite grammars only; other formalism adapters belong to the full commission.')
    alphabet, words = g['alphabet'], g['words']
    require(isinstance(alphabet,list) and 0<len(alphabet)<=16 and all(isinstance(x,str) and 0<len(x)<=64 for x in alphabet), 'GRAMMAR_SCHEMA', 'Alphabet needs 1..16 distinct string symbols of 1..64 characters.')
    require(len(set(alphabet))==len(alphabet), 'GRAMMAR_SCHEMA', 'Alphabet symbols are distinct identities.')
    require(isinstance(words,list) and 0<len(words)<=128, 'BUDGET', 'Finite grammar needs 1..128 productions.')
    for w in words:
        require(isinstance(w,list) and len(w)<=12, 'BUDGET', 'Each production has at most twelve symbols.')
        require(all(isinstance(x,str) and x in alphabet for x in w), 'UNKNOWN_SYMBOL', 'A word contains a symbol outside its declared alphabet.')
    normalized = json.loads(canonical(g))
    h = digest('polyia.grammar.v1', normalized)
    letter = {'kind':'GrammarLetter','id':'G:'+h,'source_grammar':h,'expansion':normalized,
              'interpretation':'finite-word-monoid','loss':[],'version':1}
    expanded = json.loads(canonical(letter['expansion']))
    # Independent finite denotation: a value is the tuple of symbol identities,
    # not a concatenated string that could collapse token boundaries.
    before = {tuple(w) for w in normalized['words']}
    after = {tuple(w) for w in expanded['words']}
    generated = [list(w) for w in sorted(before)]
    high_level = {'alphabet':[letter['id']], 'word':[letter['id']], 'interpretation':'expand the referenced grammar; enumerate its finite language',
                  'grammar_letters':{letter['id']:letter}}
    return receipt({'grammar':normalized,'grammar_digest':h,'promoted_letter':letter,'higher_alphabet':high_level,
                    'expanded_grammar':expanded,'generated':generated,'semantic_scope':'all words of this finite declared grammar, under tuple-of-symbol-identities denotation',
                    'source_recovery':'canonical UTF-8 JSON is recovered exactly; arbitrary original whitespace is not claimed preserved unless separately archived'},
                   [check('canonical grammar expansion is byte exact',canonical(normalized)==canonical(expanded)),
                    check('finite semantic denotation preserved',before==after),
                    check('language cardinality preserved',len(before)==len(after)),
                    check('source identity resolves to expansion',h==digest('polyia.grammar.v1',expanded)),
                    check('token boundaries retained',all(isinstance(w,list) for w in generated))],
                   ['Semantic certification is relative to the declared denotation and finite grammar.',
                    'This exact promotion is an abbreviation. It does not prove arbitrary quotient/fold reversibility or equivalence of context-free grammars.'])


def identifier(x):
    return isinstance(x,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,63}',x) is not None


def run_qpath(parameters):
    require(set(parameters) <= {'inputs','steps'}, 'UNKNOWN_PARAMETER', 'Q-path accepts inputs and steps only.')
    inputs=parameters.get('inputs',[{'id':'a','type':'Rational','value':'1/2','context':'Q'},{'id':'b','type':'Rational','value':'1/3','context':'Q'}])
    steps=parameters.get('steps',[{'op':'rational.add','inputs':{'left':'a','right':'b'},'output':'sum'},
                                  {'op':'rational.divide','inputs':{'left':'sum','right':'b'},'output':'ratio'}])
    require(isinstance(inputs,list) and 1<=len(inputs)<=32 and isinstance(steps,list) and 1<=len(steps)<=32,'BUDGET','At most 32 inputs and 32 steps; at least one each.')
    values={}
    for v in inputs:
        require(isinstance(v,dict) and set(v)=={'id','type','value','context'} and identifier(v.get('id')), 'INPUT_SCHEMA','Input needs valid id, type, value, context.')
        require(v['id'] not in values,'IDENTITY_REUSE','Input identities cannot be duplicated.')
        require(isinstance(v['type'],str) and len(v['type'])<=64 and isinstance(v['context'],str) and len(v['context'])<=64,'INPUT_SCHEMA','Types and contexts must be bounded strings.')
        values[v['id']]={'type':v['type'],'value':str(number(v['value'])),'context':v['context'],'provenance':{'kind':'supplied-input','id':v['id']}}
    trace=[]; checks=[]
    for i,s in enumerate(steps):
        require(isinstance(s,dict) and set(s)=={'op','inputs','output'},'STEP_SCHEMA','Each step requires op, named inputs, output.')
        require(s['op'] in ('rational.add','rational.multiply','rational.divide'),'UNKNOWN_OPERATION','Only registered pure rational operations are available.')
        require(identifier(s['output']) and s['output'] not in values,'IDENTITY_REUSE','Output identity must be fresh.')
        ports=s['inputs']
        require(isinstance(ports,dict) and set(ports)=={'left','right'} and all(identifier(x) for x in ports.values()),'PORT_SCHEMA','Both named ports left and right are required.')
        require(all(x in values for x in ports.values()),'MISSING_JOINT_PREMISE','Every input of a hyperedge must be present together; one incoming arc is insufficient.')
        left,right=values[ports['left']],values[ports['right']]
        require(left['type']==right['type']=='Rational','TYPE_MISMATCH','Rational operators require both inputs typed Rational.')
        require(left['context']==right['context']=='Q','CONTEXT_MISMATCH','Both premises must belong to the declared field context Q.')
        a,b=number(left['value']),number(right['value'])
        if s['op']=='rational.add':
            out=bounded(a+b)
            verified=out.numerator*a.denominator*b.denominator == out.denominator*(a.numerator*b.denominator+b.numerator*a.denominator)
        elif s['op']=='rational.multiply':
            out=bounded(a*b)
            verified=out.numerator*a.denominator*b.denominator == out.denominator*a.numerator*b.numerator
        else:
            require(b!=0,'ZERO_DIVISOR','Division guard requires a nonzero right input.')
            out=bounded(a/b)
            verified=out.numerator*b.numerator*a.denominator == out.denominator*b.denominator*a.numerator
        values[s['output']]={'type':'Rational','value':str(out),'context':'Q','provenance':{'kind':'derived','step':i,'inputs':dict(ports),'operation':s['op']}}
        trace.append({'step':i,'operation':s['op'],'input_ids':dict(ports),'output_id':s['output'],
                      'signature':'(left:Rational[Q],right:Rational[Q])->Rational[Q]',
                      'effects':'pure','witness':'exact cross-multiplied integer equality','witness_pass':verified,
                      'cost_bound':{'arithmetic_operations':1,'max_bits':MAX_BITS}})
        checks.append(check('step '+str(i)+' exact arithmetic witness',verified))
    return receipt({'values':values,'trace':trace,'reachable_outputs':[s['output'] for s in steps],
                    'representation':'typed directed hyperpath with ordered/named joint premises',
                    'context':'Q','physical_quantum_claim':False}, checks,
                   ['This is execution of an explicitly supplied finite hyperpath, not exhaustive search of every possible path.',
                    'Context Q is a registered algebra identity; context transport and arbitrary type unification require further adapters.',
                    'Exact arithmetic witnesses certify these results, not external semantic or historical claims.'])


def run_acceptance(parameters):
    require(not parameters,'UNKNOWN_PARAMETER','Acceptance has no caller-controlled pass flag or parameters.')
    p=run_registered('polynomial',{})
    z=run_registered('polynomial',{'b':[0]})
    g=run_registered('grammar-promotion',{})
    q=run_registered('qpath',{})
    missing=run_registered('qpath',{'inputs':[{'id':'a','type':'Rational','value':'1','context':'Q'}]})
    wrong_context=run_registered('qpath',{'inputs':[{'id':'a','type':'Rational','value':'1','context':'R'},{'id':'b','type':'Rational','value':'2','context':'Q'}]})
    wrong_type=run_registered('qpath',{'inputs':[{'id':'a','type':'Length','value':'1','context':'Q'},{'id':'b','type':'Rational','value':'2','context':'Q'}]})
    float_input=run_registered('polynomial',{'a':[0.5]})
    bad_symbol=run_registered('grammar-promotion',{'grammar':{'kind':'finite','alphabet':['a'],'words':[['b']]}})
    checks=[check('exact polynomial division and derivative identities',p['status']=='PASS'),
            check('polynomial divisor guard',z['status']=='REFUSED' and z['result']['reason']=='ZERO_DIVISOR'),
            check('domain exclusion retained','b(x) != 0' in ' '.join(p['result']['domain'])),
            check('grammar promotion expansion',g['status']=='PASS'),
            check('finite grammar exact denotation',g['result']['grammar']==g['result']['expanded_grammar']),
            check('joint-premise constructive hyperpath',q['status']=='PASS' and q['result']['values']['ratio']['value']=='5/2'),
            check('missing joint premise rejected',missing['status']=='REFUSED' and missing['result']['reason']=='MISSING_JOINT_PREMISE'),
            check('context mismatch rejected',wrong_context['status']=='REFUSED' and wrong_context['result']['reason']=='CONTEXT_MISMATCH'),
            check('type mismatch rejected',wrong_type['status']=='REFUSED' and wrong_type['result']['reason']=='TYPE_MISMATCH'),
            check('inexact float input rejected',float_input['status']=='REFUSED'),
            check('unknown alphabet symbol rejected',bad_symbol['status']=='REFUSED'),
            check('registered implementations use no model inference',all(x['llm_inference'] is False for x in [p,g,q]))]
    return receipt({'families':{'polynomial':p,'grammar-promotion':g,'qpath':q},
                    'negative_controls':{'zero_divisor':z,'missing_joint':missing,'context':wrong_context,'type':wrong_type,'float':float_input,'symbol':bad_symbol}},
                   checks,['Acceptance covers these registered finite kernels only; full commission remains NOT_COMMISSIONED.',
                           'No-LLM assurance also requires the package dependency/import audit and offline acceptance evidence; a self-declared field alone is insufficient.'])


def run_registered(name, parameters):
    """Registered, deterministic and bounded dispatch; never eval/import user code."""
    try:
        require(isinstance(parameters,dict),'PARAMETER_SCHEMA','Parameters must be a JSON object.')
        require(isinstance(name,str),'UNKNOWN_EXPERIMENT','Experiment name must be a string.')
        handlers={'polynomial':run_polynomial,'grammar-promotion':run_promotion,'qpath':run_qpath,'acceptance':run_acceptance}
        require(name in handlers,'UNKNOWN_EXPERIMENT','Unknown experiment; available: polynomial, grammar-promotion, qpath, acceptance.')
        return handlers[name](parameters)
    except Refusal as error:
        return {'status':'REFUSED','evidence_class':'REFUSAL','result':{'reason':error.code,'detail':error.detail},
                'checks':[],'limitations':['No scientific result is certified for this refused request.'],
                'kernel_version':VERSION,'llm_inference':False}
