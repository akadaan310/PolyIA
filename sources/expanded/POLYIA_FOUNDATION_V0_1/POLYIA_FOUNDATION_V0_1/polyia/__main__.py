import argparse,json
from pathlib import Path
from .lang import compile_commission
from .compiler import compose
from .automaton import make_artifact,to_dot,to_html
from .harness import init,load,advance,verify

def main():
    p=argparse.ArgumentParser(description='POLYIA deterministic agency reference')
    sp=p.add_subparsers(dest='cmd',required=True)
    d=sp.add_parser('compile');d.add_argument('source');d.add_argument('--out',default='build')
    h=sp.add_parser('harness');h.add_argument('action',choices=['init','status','advance','verify']);h.add_argument('--dir',default='.polyia-state');h.add_argument('--receipt')
    a=p.parse_args()
    if a.cmd=='compile':
        c=compile_commission(Path(a.source).read_text(encoding='utf8'))
        plan=compose(c);artifact=make_artifact(c,plan)
        out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
        (out/'automaton.json').write_text(json.dumps(artifact,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (out/'automaton.dot').write_text(to_dot(artifact),encoding='utf8')
        (out/'automaton.html').write_text(to_html(artifact),encoding='utf8')
        (out/'plan.pir').write_text('(polyia-plan "'+plan.digest+'"\n'+'\n'.join('  (invoke "'+atom.id+'" ('+' '.join(atom.inputs)+') ('+' '.join(atom.outputs)+'))' for atom in plan.steps)+'\n)\n')
        print('Compiled '+str(len(plan.steps))+' typed modules; plan SHA-256 '+plan.digest+'; outputs at '+str(out))
    elif a.action=='init':print(json.dumps(init(Path(a.dir)),indent=2))
    elif a.action=='status':print(json.dumps(load(Path(a.dir)),indent=2))
    elif a.action=='verify':print('verified' if verify(Path(a.dir)) else 'INVALID')
    elif a.action=='advance':
        if not a.receipt:p.error('--receipt required')
        print(json.dumps(advance(Path(a.dir),json.loads(Path(a.receipt).read_text())),indent=2))
if __name__=='__main__':main()
