#!/usr/bin/env python3
"""Audit the installed runtime and finite kernels, not inert upstream archives."""
import ast
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))

def audit():
    errors=[]; modules=[]; imports=[]
    for path in sorted((ROOT/'polyia').glob('*.py')):
        raw=path.read_bytes(); tree=ast.parse(raw,filename=str(path))
        modules.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()})
        for node in ast.walk(tree):
            names=[]
            if isinstance(node,ast.Import):names=[n.name.split('.')[0] for n in node.names]
            elif isinstance(node,ast.ImportFrom) and not node.level:names=[(node.module or '').split('.')[0]]
            for name in names:
                imports.append(name)
                if name not in sys.stdlib_module_names and name!='polyia':errors.append(f'Non-stdlib runtime dependency: {name} in {path.name}')
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'eval','exec','__import__'}:
                errors.append(f'Unbounded code-execution primitive: {node.func.id} in {path.name}')
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='_code_identity':
                if not node.args or not isinstance(node.args[0],ast.Constant) or node.args[0].value not in {'polyia.store','polyia.experiments'}:
                    errors.append(f'Unregistered module-identity import in {path.name}')
    weights=[str(p.relative_to(ROOT)) for p in (ROOT/'polyia').rglob('*') if p.suffix.lower() in {'.gguf','.pt','.pth','.safetensors','.onnx','.h5'}]
    if weights:errors.append('Unexpected model artifacts in runtime: '+','.join(weights))
    from polyia.experiments import run_registered
    from polyia.capabilities import run_registered as run_extension
    from polyia.mission_verifiers import run_capture_checks, run_guidance_checks
    def denied(*args,**kwargs):raise AssertionError('Offline kernel attempted a denied network/process operation')
    with patch.object(socket,'socket',denied),patch.object(subprocess,'Popen',denied),patch.object(urllib.request,'urlopen',denied):
        result=run_registered('acceptance',{})
        extensions=[]
        for name,parameters in [
            ('native',{'source':'(commission (profile "polyia.native/0.1") (emit answer (add 1/3 1/6)))'}),
            ('intake',{'text':'Teach polynomial division'}),
            ('astra',{'adapter_version':'POLYIA-ASTRA/0.1','source_version':'ASTRA/0.2',
                      'protocol':'ATOM-HANDOFF/0.1','operation':'atom.initialize'}),
            ('rasm',{'version':'polyia.rasm/0.1','chart':'timeless.rsa28/0.1',
                     'operation':'project','text':'كتب'}),
            ('forms',{'version':'polyia.forms/0.1','operation':'generate','index':10**20,
                      'alphabet':{'version':'polyia.alphabet/0.1','kind':'numeric',
                       'entity_id':'audit:N','interpretation':'Individual effective Naturals.',
                       'sources':[{'source':'tools/audit_no_llm.py','anchor':'finite offline fixture',
                                   'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}],
                       'generator':{'name':'naturals','start':0,'coordinates':'value'},
                       'group':{'elements':[{'id':'e','rule':'identity'}]}}}),
            ('generators',{'card':json.loads((ROOT/'examples/generators/protocol.card.json').read_text()),
                           'request':{'operation':'generate'},'style':'tutorial'})]:
            observed=run_extension(name,parameters)
            passed=(observed['status']=='PASS' and bool(observed['checks']) and
                    all(c['pass'] is True for c in observed['checks']) and observed['llm_inference'] is False)
            extensions.append({'name':name,'pass':passed,'result_sha256':hashlib.sha256(
                json.dumps(observed,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()})
            if not passed:errors.append('Offline registered extension failed: '+name)
        mission=run_capture_checks()
        if mission['status']!='PASS' or not mission['checks'] or not all(c['pass'] is True for c in mission['checks']):
            errors.append('Offline PIA-042 capture conformance failed')
        guidance=run_guidance_checks()
        if guidance['status']!='PASS' or not guidance['checks'] or not all(c['pass'] is True for c in guidance['checks']):
            errors.append('Offline PIA-040 guidance conformance failed')
    if result['status']!='PASS' or not result['checks'] or not all(c['pass'] for c in result['checks']):errors.append('Offline exact-kernel acceptance failed')
    return {'ok':not errors,'scope':'stdlib runtime source audit plus intercepted seed, native, intake, Astra, rasm, forms, generators, PIA-040 guidance and PIA-042 capture executions',
            'runtime_modules':modules,'imports':sorted(set(imports)),'model_artifacts':weights,'offline_checks':result['checks'],
            'offline_extensions':extensions,
            'offline_mission':mission,
            'offline_guidance':guidance,
            'errors':errors,'limitations':['Static imports plus intercepted kernel execution establish this finite bootstrap scope, not every future plugin.',
             'Archived upstream source is retained data, not imported into the running baseline.',
             'The fixed installed scientific module is compiled only to compare its code structure with loaded functions; that comparison object is never executed.',
             'The HTTP service necessarily uses a loopback socket; this audit disables networking for the scientific kernels.',
             'Full commission requires the broader no-inference process/tool/model-artifact gate as capabilities are added.']}

if __name__=='__main__':
    report=audit();print(json.dumps(report,indent=2));sys.exit(0 if report['ok'] else 1)
