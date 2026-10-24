"""Deterministic, headless, LLM-free parent executor. Not a process sandbox.
It never executes shell commands or arbitrary imported plugins.
"""
import argparse,json
from pathlib import Path
from .core import Universe,TEMPLATES,AtomError

MAX_ATOMS=16

def validate_plan(plan):
    if not isinstance(plan,dict) or set(plan)!={'protocol','steps'} or plan['protocol']!='ATOM-PLAN/0.1':raise AtomError('Bad plan envelope')
    steps=plan['steps']
    if not isinstance(steps,list) or len(steps)>MAX_ATOMS:raise AtomError('Plan too large')
    names=set()
    for step in steps:
        if not isinstance(step,dict) or set(step)!={'atom','kind','params'}:raise AtomError('Bad step shape')
        if not isinstance(step['atom'],str) or step['atom'] in names or step['kind'] not in TEMPLATES or not isinstance(step['params'],dict):raise AtomError('Bad atom, kind, or params')
        names.add(step['atom'])
    return steps

def execute(universe,plan,dry_run=True):
    steps=validate_plan(plan)
    if dry_run:return {'dry_run':True,'plan_atoms':len(steps),'plan':steps,'next':'pass --execute to authorize exact declared operations'}
    results=[]
    for item in steps:
        s=universe.state()
        if s['phase']=='HOLD':universe.advance();s=universe.state()
        if s['phase']!='OBSERVE':raise AtomError('Parent not at safe observation boundary')
        universe.register(item['atom'],item['kind'])
        for i in range(6):
            r=universe.advance(item['atom'] if i==0 else None,item['params'] if i==0 else None)
            integrity=universe.verify()
            if not integrity['verified']:raise AtomError('Receipt or checkpoint verification failed')
        results.append({'atom':item['atom'],'kind':item['kind'],'checkpoint':universe.state()['last_checkpoint'],'outcome':universe.state()['results'][-1]['output']})
    return {'executed':len(results),'results':results,'report':universe.report()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',default='.');p.add_argument('--plan',required=True);p.add_argument('--state',default='.atom-driver-state');p.add_argument('--execute',action='store_true')
    a=p.parse_args();project=Path(a.project).resolve();planpath=(project/a.plan).resolve()
    if not planpath.is_relative_to(project) or not planpath.is_file():raise SystemExit('Plan must stay inside project')
    plan=json.loads(planpath.read_text());u=Universe((project/a.state).resolve())
    try:print(json.dumps(execute(u,plan,not a.execute),indent=2,ensure_ascii=False))
    except AtomError as e:raise SystemExit(str(e))
if __name__=='__main__':main()
