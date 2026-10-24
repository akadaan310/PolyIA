"""Run with python -m atom.cli [command]."""
import argparse,json,sys
from pathlib import Path
from .core import Universe,AtomError

def entry():
    ap=argparse.ArgumentParser(prog='atomctl',description='Stepwise micro-automata, receipts and checkpoints')
    ap.add_argument('--root',default='.atom-state',help='Private project-owned state root')
    sub=ap.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('register');q.add_argument('name');q.add_argument('kind')
    q=sub.add_parser('advance');q.add_argument('--atom');q.add_argument('--params',default='{}')
    for command in ('status','verify','protocol','report','teach','demo','choose'):sub.add_parser(command)
    args=ap.parse_args();univ=Universe(Path(args.root))
    try:
        if args.cmd=='register':v=univ.register(args.name,args.kind)
        elif args.cmd=='advance':v=univ.advance(args.atom,json.loads(args.params))
        elif args.cmd=='status':v=univ.state()
        elif args.cmd=='verify':v=univ.verify()
        elif args.cmd=='protocol':v=univ.protocol()
        elif args.cmd=='report':v=univ.report()
        elif args.cmd=='choose':v=univ.choose()
        elif args.cmd=='teach':v={'lesson':[
            'One advance executes exactly one phase; stop after each invocation and inspect the JSON result.',
            'Register scoped atoms in OBSERVE; params are checked at ADMIT before effects are evaluated.',
            'Pass all advances through OBSERVE → PROPOSE → ADMIT → EXECUTE → VERIFY → CHECKPOINT → HOLD.',
            'Only a CHECKPOINT creates an immutable content-addressed state capture. Continue with one HOLD→OBSERVE advance.',
            'Never treat the receipt hash as a cryptographic signature or your tests as proof of real-world scientific truth.',
            'Report through atomctl report; the report has a stable schema for another harness to ingest.',
            'Do not give the harness arbitrary command execution; separate adapters and explicit approvals are required.'
        ],'example':['python -m atom.cli --root .atom-state register flight journey','python -m atom.cli --root .atom-state advance --atom flight --params \'{"destination":"Mars"}\'','python -m atom.cli --root .atom-state advance','python -m atom.cli --root .atom-state report']}
        elif args.cmd=='demo':
            if 'flight' not in univ.state()['atoms']:univ.register('flight','journey')
            r=[]
            for i in range(6):r.append(univ.advance('flight' if i==0 else None,{'destination':'Mars'} if i==0 else None))
            v={'trace':r,'report':univ.report()}
        print(json.dumps(v,ensure_ascii=False,indent=2))
    except (AtomError,ValueError,TypeError,KeyError) as e:
        print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
if __name__=='__main__':entry()
