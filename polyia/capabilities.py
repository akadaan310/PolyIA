"""Fixed pure extensions to the original four scientific kernels.

These adapters add recorded executions, never blanket mission acceptance.
Dependencies are closed in store._EXTENSION_DEPENDENCIES_V1; the ledger pins
this adapter and each transitive project module before/after execution. No
caller selects Python modules, imports, functions or external effects.
"""

import json

VERSION = 'polyia.capabilities/0.1'
MAX_ADAPTER_RESULT_BYTES = 524288


def _refused(code, message):
    return {'status': 'REFUSED', 'evidence_class': 'REFUSAL',
            'result': {'reason': code, 'detail': message}, 'checks': [],
            'limitations': ['No result was admitted by the fixed capability adapter.'],
            'kernel_version': VERSION, 'llm_inference': False}


def _bounded_report(report):
    size = len(json.dumps(report, sort_keys=True, ensure_ascii=True, allow_nan=False).encode())
    if size <= MAX_ADAPTER_RESULT_BYTES:
        return report
    result = _refused('TRANSPORT_OUTPUT_LIMIT', 'The constructive result exceeds the 512 KiB command-plane report budget; use a smaller declared construction or its standalone interface.')
    result['status'] = 'RESOURCE_LIMIT'
    result['result']['computed_report_bytes'] = size
    return result


def run_registered(name, parameters):
    """Only fixed capability names are admitted; seed dispatch stays separate."""
    if type(parameters) is not dict:
        return _refused('PARAMETER_SCHEMA', 'Parameters must be an object.')
    if name == 'native':
        from . import native
        if set(parameters) != {'source'} or type(parameters['source']) is not str:
            return _refused('PARAMETER_SCHEMA', 'Native compilation accepts exactly a source string.')
        compiled = native.compile_program(parameters['source'])
        executed = native.execute_program(compiled['program']) if compiled['ok'] else compiled
        success = executed['ok'] is True
        return {'status': 'PASS' if success else 'REFUSED',
                'evidence_class': 'COMPILED_VM_DIFFERENTIAL_CHECK' if success else 'REFUSAL',
                'result': {'compilation': compiled, 'execution': executed},
                'checks': [{'name': 'typed native source admitted', 'pass': compiled['ok'] is True},
                           {'name': 'compiled and reference outputs agree', 'pass': success and executed['verification']['agreement'] is True}],
                'limitations': ['Bounded pure native profile only; general modules, external effects and full compiler acceptance remain open.',
                                'The VM and AST evaluator share frontend validation and exact rational dependencies; agreement is not a formal proof.'],
                'kernel_version': VERSION, 'llm_inference': False}
    if name == 'intake':
        from . import intake
        return intake.run_intake(parameters)
    if name == 'astra':
        from . import astra
        adapted = astra.run_adapter(parameters)
        checks = [{'name': item['name'], 'pass': item['verdict'] == 'PASS', 'source_check': item}
                  for item in adapted['checks']]
        return {'status': adapted['status'],
                'evidence_class': 'ASTRA_BOUNDED_ADAPTER_CHECK' if adapted['ok'] else 'REFUSAL',
                'result': adapted, 'checks': checks, 'limitations': adapted['limitations'],
                'kernel_version': VERSION, 'llm_inference': False}
    if name == 'rasm':
        from . import rasm
        return rasm.run_rasm(parameters)
    if name == 'forms':
        from . import forms
        observed = forms.run_forms(parameters)
        return _bounded_report({'status': 'REFUSED' if observed['status'] == 'UNSUPPORTED' else observed['status'],
            'evidence_class': observed['evidence_class'], 'result': observed,
            'checks': [{'name': check['name'], 'pass': check['passed'] is True} for check in observed['checks']],
            'limitations': observed['limitations'], 'kernel_version': VERSION, 'llm_inference': False})
    if name == 'generators':
        from . import generators
        if not {'card', 'request'} <= parameters.keys() <= {'card', 'request', 'style'}:
            return _refused('PARAMETER_SCHEMA', 'Generator execution requires a typed card, a request and optionally an explanation style.')
        if parameters.get('style', 'concise') not in ('concise', 'tutorial'):
            return _refused('PARAMETER_SCHEMA', 'Explanation style must be concise or tutorial.')
        compiled = generators.compile_model(parameters['card'])
        if not compiled['ok']:
            result = _refused(compiled['error']['code'], compiled['error']['detail'])
            if compiled['error']['code'] == 'RESOURCE_LIMIT': result['status'] = 'RESOURCE_LIMIT'
            return result
        model = compiled['model']
        execution = generators.run_model(model, parameters['request'])
        illustration, curriculum = None, None
        candidates = execution['result'].get('candidates', [])
        if candidates and 'style' in parameters:
            illustrated = generators.render_explanation(candidates[0], {'style': parameters['style']})
            if not illustrated['ok']:
                return _refused(illustrated['error']['code'], illustrated['error']['detail'])
            illustration = illustrated['view']
            if model['family'] == 'polynomial-division':
                taught = generators.build_curriculum(candidates[0])
                if not taught['ok']:
                    return _refused(taught['error']['code'], taught['error']['detail'])
                curriculum = taught['curriculum']
        return _bounded_report({'status': execution['status'], 'evidence_class': execution['evidence_class'],
            'result': {'model': model, 'execution': execution, 'illustration': illustration, 'curriculum': curriculum},
            'checks': [{'name': check['name'], 'pass': check['passed'] is True} for check in execution['checks']],
            'limitations': execution['limitations'] + ['An optional explanation/curriculum describes the first admitted candidate only.'],
            'kernel_version': VERSION, 'llm_inference': False})
    return _refused('UNKNOWN_EXPERIMENT', 'Only fixed native, intake, Astra, rasm, forms and generator extensions are registered.')
