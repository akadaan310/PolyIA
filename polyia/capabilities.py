"""Fixed pure extensions to the original four scientific kernels.

These adapters add recorded executions, never blanket mission acceptance.
Dependencies are closed in store._EXTENSION_DEPENDENCIES_V1; the ledger pins
this adapter and each transitive project module before/after execution. No
caller selects Python modules, imports, functions or external effects.
"""

VERSION = 'polyia.capabilities/0.1'


def _refused(code, message):
    return {'status': 'REFUSED', 'evidence_class': 'REFUSAL',
            'result': {'reason': code, 'detail': message}, 'checks': [],
            'limitations': ['No result was admitted by the fixed capability adapter.'],
            'kernel_version': VERSION, 'llm_inference': False}


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
    return _refused('UNKNOWN_EXPERIMENT', 'Only native, intake, astra and rasm extensions are registered.')
