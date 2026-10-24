#!/usr/bin/env python3
"""Reproducible finite UCG-084/124 witnesses; measured timings are not replay hashes.

Only freshly compiled local pure programs reach the private VM/reference timing
entrypoints. This harness is an implementation diagnostic, not a service route.
"""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import sys
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from polyia import native

HARNESS_VERSION = 'polyia.native.quantitative/0.1'
DEFAULT_SEED = 20261024
BINDINGS = {'x': 'Rational', 'p': 'Polynomial', 'd': 'Division', 's': 'Text'}
PRELUDE = ('(let x Rational 3/7) (let p Polynomial (poly 1 -2 3)) '
           '(let d Division (divmod (poly 1 0 1) (poly 1 1))) (let s Text "xح")')
SOURCE_PINS = [
    ('sources/originals/UCG_CODEX_CONSTITUTIONAL_COMMISSION.md',
     '0cf03197777e19330ce36cf478bec9a5c4cad5459fd142c37eb4ae0e82bd6d7e',
     'UCG-084 lines 457–461; UCG-124 lines 627–631; UCG-132'),
    ('sources/recovered/CODEX_CONSTITUTION.md',
     'cfe0b88f9c701e139372d783db1d9568da272f6433f9e513d6475fe7985a2630',
     'POLY-C-017–024, 057–058, 064, 068–070, 074–080'),
]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def update_hash(digest, value):
    data = canonical(value)
    digest.update(len(data).to_bytes(8, 'big'))
    digest.update(data)


def literal(kind, value):
    return {'kind': 'literal', 'type': kind, 'value': str(value)}


def call(operation, kind, *args):
    return {'kind': 'call', 'operation': operation, 'type': kind, 'arguments': list(args)}


def generated_term(rng, kind, depth, force=False):
    names = {'Rational': 'x', 'Polynomial': 'p', 'Division': 'd', 'Text': 's'}
    if depth == 0 or not force and rng.randrange(5) == 0:
        if rng.randrange(4) == 0:
            return {'kind': 'reference', 'type': kind, 'name': names[kind]}
        if kind == 'Rational':
            return literal(kind, Fraction(rng.randrange(-32, 33), rng.randrange(1, 10)))
        if kind == 'Text':
            return literal(kind, rng.choice(['', 'a', 'كتب', 'é', 'é', 'أ', '"', '\\', '\n', '🙂']))
        if kind == 'Polynomial':
            return call('poly', kind, *(literal('Rational', rng.randrange(-9, 10)) for _ in range(rng.randrange(1, 5))))
        return call('divmod', kind, call('poly', 'Polynomial', literal('Rational', 1)),
                    call('poly', 'Polynomial', literal('Rational', 1)))
    child = lambda target: generated_term(rng, target, depth-1)
    if kind == 'Rational':
        op = rng.choice(['add', 'sub', 'mul', 'evaluate'])
        return call(op, kind, child('Polynomial') if op == 'evaluate' else child(kind), child(kind))
    if kind == 'Polynomial':
        op = rng.choice(['poly', 'padd', 'pmul', 'derivative', 'quotient', 'remainder'])
        if op == 'poly':
            return call(op, kind, *(child('Rational') for _ in range(rng.randrange(1, 5))))
        if op in ('padd', 'pmul'):
            return call(op, kind, child(kind), child(kind))
        return call(op, kind, child('Division' if op in ('quotient', 'remainder') else kind))
    if kind == 'Division':
        # A nonzero leading coefficient gives a constructive domain witness.
        divisor = call('poly', 'Polynomial', literal('Rational', rng.randrange(-5, 6)),
                       literal('Rational', rng.choice([-3, -2, -1, 1, 2, 3])))
        return call('divmod', kind, child('Polynomial'), divisor)
    if rng.randrange(2):
        return call('concat', kind, child(kind), child(kind))
    return call('replace', kind, child(kind), literal(kind, 'a'), child(kind))


def term_corpus(count, seed):
    rng, seen = random.Random(seed), set()
    kinds = ['Rational', 'Polynomial', 'Division', 'Text']
    for index in range(count):
        for attempt in range(200):
            term = generated_term(rng, kinds[index % 4], 3, force=True)
            key = canonical(term)
            if key not in seen:
                seen.add(key)
                yield term
                break
        else:
            raise RuntimeError('Term generation uniqueness budget exhausted')


def _quote(text):
    return json.dumps(text, ensure_ascii=False)


def _program(body):
    return '(commission (profile "polyia.native/0.1") ' + body + ')'


def _poly(values):
    return '(poly ' + ' '.join(map(str, values)) + ')'


def _trim(values):
    values = list(values)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return values


def machine_corpus(machine_id, count, seed):
    rng = random.Random(seed)
    for index in range(count):
        if machine_id == 'polynomial-division':
            divisor = [rng.randrange(-8, 9) for _ in range(rng.randrange(1, 6))]
            divisor[-1] = rng.choice([-7, -3, -1, 1, 3, 7])
            quotient = _trim([rng.randrange(-9, 10) for _ in range(rng.randrange(1, 6))])
            remainder = _trim([rng.randrange(-6, 7) for _ in range(len(divisor)-1)] or [0])
            dividend = [0] * (len(divisor)+len(quotient)-1)
            for i, a in enumerate(divisor):
                for j, b in enumerate(quotient):
                    dividend[i+j] += a*b
            for i, coefficient in enumerate(remainder):
                dividend[i] += coefficient
            inputs = {'dividend': dividend, 'divisor': divisor}
            source = _program('(emit result (divmod ' + _poly(dividend) + ' ' + _poly(divisor) + '))')
            expected = {'result': {'type': 'Division', 'value': {
                'quotient': list(map(str, quotient)), 'remainder': list(map(str, remainder))}}}
            witness = 'construct dividend = divisor * chosen quotient + chosen degree-bounded remainder'
        elif machine_id == 'derivative-evaluation':
            a, b, c = (Fraction(rng.randrange(-20, 21), rng.randrange(1, 8)) for _ in range(3))
            x = Fraction(rng.randrange(-20, 21), rng.randrange(1, 8))
            inputs = {'a': str(a), 'b': str(b), 'c': str(c), 'x': str(x)}
            source = _program('(emit result (evaluate (derivative ' + _poly([c, b, a]) + ') ' + str(x) + '))')
            expected = {'result': {'type': 'Rational', 'value': str(2*a*x+b)}}
            witness = 'closed quadratic-family identity D(c+b*x+a*x^2)(x)=b+2*a*x'
        else:
            segments = [rng.choice(['كتب', 'alpha', 'é', 'é', '"quote"', '\\', '\n', '', '🙂']) for _ in range(3)]
            # The alphabet excludes colon; the only pattern sites are these joins.
            pattern = '::'
            replacement = rng.choice(['β', '\n', '"', '', 'ح', '\\']) + str(index)
            text = pattern.join(segments)
            inputs = {'text': text, 'pattern': pattern, 'replacement': replacement}
            source = _program('(emit result (replace ' + ' '.join(_quote(value) for value in [text, pattern, replacement]) + '))')
            expected = {'result': {'type': 'Text', 'value': segments[0]+replacement+segments[1]+replacement+segments[2]}}
            witness = 'known two nonoverlapping pattern sites; expected text assembled without replace or split'
        yield inputs, source, expected, witness


def timing_summary(values):
    ordered = sorted(values)
    return {'samples': len(values), 'total': sum(values), 'min': ordered[0],
            **{name: ordered[math.ceil(q*len(ordered))-1] for name, q in [('p50', .5), ('p95', .95), ('p99', .99)]},
            'max': ordered[-1]}


def _timed(function, *args):
    start = perf_counter_ns()
    result = function(*args)
    return result, perf_counter_ns()-start


def _checked(result):
    if result.get('ok') is not True:
        raise AssertionError(result)
    return result


def run_checks(term_count=10000, inputs_per_machine=1000, seed=DEFAULT_SEED):
    for value, maximum in [(term_count, 10000), (inputs_per_machine, 1000)]:
        if type(value) is not int or not 1 <= value <= maximum:
            raise ValueError('Requested work must be a positive integer within the declared quantitative ceiling')
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise ValueError('Seed must be a uint64')
    report = {'schema': HARNESS_VERSION, 'status': 'PASS', 'thresholds_met': term_count == 10000 and inputs_per_machine == 1000,
              'mission_acceptance': False, 'evidence_class': 'FINITE_REPRODUCIBLE_DIFFERENTIAL_AND_CONSTRUCTIVE_CHECKS',
              'llm_inference': False, 'seed': seed, 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'environment': {'python': platform.python_version(), 'implementation': platform.python_implementation(),
                  'platform': platform.platform(), 'architecture': platform.machine(), 'hardware_hosts_tested': 1,
                  'clock': 'time.perf_counter_ns', 'cpu_governor': 'NOT_CONTROLLED',
                  'warmup': 'none; timings include natural first-call and warm effects; no performance superiority claimed'},
              'sources': [], 'implementation': [], 'failures': [], 'limitations': [
                  'Three computational machine templates on one host; no three-host replication or external hardware claim.',
                  'VM/reference share lexer, parser, typechecker, encoding and fractions.Fraction; differential agreement is not formal proof.',
                  'Generated machine inputs are specialized into closed source programs; there is no new dynamic input ABI.',
                  'Grammar-biased seeded corpus is not a uniform sample of all mathematical terms or all native programs.',
                  'Constructive expected values are made by this harness before compilation, not by a sealed blind external oracle.',
                  'Term normalization semantic checks use the same VM before and after; those checks are self-consistency evidence.',
                  'Partial normalization does not implement transcendental functions, general functions, rewriting theories or full common mathematics.',
                  'PILLAR9 binary backend, WASM/native compiler, generic GUC-card generators and wider mission acceptance remain open.',
                  'Runtime timings exclude OS-level isolation and do not establish memory, energy or cross-host performance.']}
    for path, digest, anchor in SOURCE_PINS:
        actual = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if actual != digest:
            raise AssertionError('Source pin mismatch: ' + path)
        report['sources'].append({'path': path, 'sha256': actual, 'anchor': anchor})
    for path in ['polyia/native.py', 'tools/check_native_quantitative.py']:
        report['implementation'].append({'path': path, 'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest()})
    compatibility = json.loads((ROOT/'tools/fixtures/native_packages.json').read_text())
    report['historical_package_compatibility'] = {'checked': len(compatibility), 'unchanged': True}
    for fixture in compatibility:
        compiled = _checked(native.compile_program(fixture['source']))
        if compiled['program']['package_sha256'] != fixture['package_sha256']:
            report['historical_package_compatibility']['unchanged'] = False
            report['status'] = 'FAIL'
    corpus_hash, result_hash = hashlib.sha256(), hashlib.sha256()
    terms = {'checked': 0, 'distinct': term_count, 'failures': 0, 'roundtrip_failures': 0, 'idempotence_failures': 0,
             'semantic_failures': 0, 'semantic_checks': 0, 'rewritten_terms': 0, 'rewrite_steps': 0}
    kinds, operations, depths = Counter(), Counter(), Counter()
    start = perf_counter_ns()
    for index, term in enumerate(term_corpus(term_count, seed)):
        update_hash(corpus_hash, {'bindings': BINDINGS, 'term': term})
        kinds[term['type']] += 1
        pending = [(term, 0)]
        maximum_depth = 0
        while pending:
            node, depth = pending.pop(); maximum_depth = max(maximum_depth, depth)
            if node['kind'] == 'call':
                operations[node['operation']] += 1
                pending.extend((child, depth+1) for child in node['arguments'])
        depths[maximum_depth] += 1
        try:
            printed = _checked(native.print_term(term, BINDINGS))['source']
            parsed = _checked(native.parse_term(printed, BINDINGS))['term']
            roundtrip = parsed == term and _checked(native.print_term(parsed, BINDINGS))['source'] == printed
            normalized = _checked(native.normalize_term(term, BINDINGS))
            again = _checked(native.normalize_term(normalized['term'], BINDINGS))
            idempotent = normalized['term'] == again['term'] and again['rewrites'] == 0
            normal_source = _checked(native.print_term(normalized['term'], BINDINGS))['source']
            before = _checked(native.compile_program(_program(PRELUDE+' (emit result '+printed+')')))['program']
            after = _checked(native.compile_program(_program(PRELUDE+' (emit result '+normal_source+')')))['program']
            left, _ = native._vm(before)
            right, _ = native._vm(after)
            semantics = left == right
            terms['semantic_checks'] += 1
            terms['roundtrip_failures'] += not roundtrip
            terms['idempotence_failures'] += not idempotent
            terms['semantic_failures'] += not semantics
            terms['rewritten_terms'] += normalized['rewrites'] > 0
            terms['rewrite_steps'] += normalized['rewrites']
            update_hash(result_hash, {'printed': printed, 'normalized': normalized['term'], 'outputs': left})
            if not (roundtrip and idempotent and semantics):
                raise AssertionError('Term law mismatch')
        except (AssertionError, native.Refusal) as error:
            terms['failures'] += 1
            report['status'] = 'FAIL'
            if len(report['failures']) < 10:
                report['failures'].append({'phase': 'terms', 'index': index, 'term': term, 'error': str(error)})
        terms['checked'] += 1
    terms.update(corpus_sha256=corpus_hash.hexdigest(), result_sha256=result_hash.hexdigest(),
                 elapsed_ns=perf_counter_ns()-start, root_types=dict(kinds), operations=dict(operations), depth_histogram=dict(depths))
    report['terms'], report['machines'] = terms, []
    for number, machine_id in enumerate(['polynomial-division', 'derivative-evaluation', 'literal-substitution']):
        timings = {key: [] for key in ['compile', 'vm', 'reference', 'admitted_execute']}
        corpus_hash, result_hash = hashlib.sha256(), hashlib.sha256()
        machine = {'id': machine_id, 'checked': 0, 'failures': 0, 'independent_witness_checks': 0,
                   'repeat_observable_checks': 0, 'samples': [],
                   'witness_class': 'CONSTRUCTIVE_EXPECTATION_NOT_EXTERNAL_ORACLE'}
        for index, (inputs, source, expected, witness) in enumerate(machine_corpus(machine_id, inputs_per_machine, seed+number+1)):
            update_hash(corpus_hash, {'inputs': inputs, 'source': source, 'expected': expected})
            try:
                compiled, elapsed = _timed(native.compile_program, source)
                timings['compile'].append(elapsed); program = _checked(compiled)['program']
                (actual, work), elapsed = _timed(native._vm, program); timings['vm'].append(elapsed)
                reference, elapsed = _timed(native._reference, program); timings['reference'].append(elapsed)
                admitted, elapsed = _timed(native.execute_program, program); timings['admitted_execute'].append(elapsed)
                repeated = _checked(admitted)['outputs']
                if not actual == reference == repeated == expected:
                    raise AssertionError('Compiled/reference/repeated/constructive-witness mismatch')
                machine['independent_witness_checks'] += 1
                machine['repeat_observable_checks'] += 1
                update_hash(result_hash, {'source_sha256': program['source_sha256'], 'outputs': actual, 'work': work})
                if index < 2:
                    machine['samples'].append({'inputs': inputs, 'source': source, 'outputs': actual,
                                               'package_sha256': program['package_sha256']})
            except (AssertionError, native.Refusal) as error:
                machine['failures'] += 1; report['status'] = 'FAIL'
                if len(report['failures']) < 10:
                    report['failures'].append({'phase': machine_id, 'index': index, 'error': str(error)})
            machine['checked'] += 1
        machine.update(corpus_sha256=corpus_hash.hexdigest(), result_sha256=result_hash.hexdigest(),
                       witness=witness, timings_ns={key: timing_summary(value) for key, value in timings.items() if value})
        report['machines'].append(machine)
    report['thresholds_met'] = report['thresholds_met'] and report['status'] == 'PASS'
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--terms', type=int, default=10000)
    parser.add_argument('--inputs-per-machine', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=DEFAULT_SEED)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = run_checks(args.terms, args.inputs_per_machine, args.seed)
    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
        print(json.dumps({'status': report['status'], 'thresholds_met': report['thresholds_met'],
                          'output': str(args.output), 'sha256': hashlib.sha256(encoded.encode()).hexdigest()}))
    else:
        print(encoded, end='')
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
