"""An actual tiny parenthesized source language: lexer -> AST -> typed commission.
This is a bounded subset and neither a general Lisp nor a disguised JSON executor.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Union
import re

@dataclass(frozen=True)
class Symbol:
    name: str
@dataclass(frozen=True)
class Node:
    items: tuple["Expr", ...]
Expr = Union[Symbol, str, int, Node]

class CompileError(ValueError): pass

_TOK = re.compile(r'\s*(?:(;[^\n]*)|([()])|("(?:\\.|[^"\\])*")|(-?\d+)|([A-Za-z_][A-Za-z0-9_./:-]*))', re.UNICODE)

def lex(source: str) -> list[Expr]:
    if len(source) > 120_000: raise CompileError('source budget exceeded')
    out: list[Expr] = []
    off=0
    while off < len(source):
        if source[off:].strip() == '': break
        m=_TOK.match(source,off)
        if not m: raise CompileError(f'illegal token at character {off}')
        off=m.end()
        if m[1]: continue
        if m[2]: out.append(Symbol(m[2]))
        elif m[3]:
            # No eval. Only two explicit string escapes are permitted.
            token=m[3][1:-1]
            if re.search(r'\\(?!["\\n])',token): raise CompileError('unsupported escape')
            out.append(token.replace('\\n','\n').replace('\\"','"').replace('\\\\','\\'))
        elif m[4]: out.append(int(m[4]))
        elif m[5]: out.append(Symbol(m[5]))
    if len(out)>20_000:raise CompileError('token budget exceeded')
    return out

def parse(source:str)->Node:
    tok=lex(source); pos=0
    def one(depth:int)->Expr:
        nonlocal pos
        if depth>40: raise CompileError('depth budget exceeded')
        if pos>=len(tok): raise CompileError('unexpected end')
        x=tok[pos];pos+=1
        if x==Symbol('('):
            arr=[]
            while pos<len(tok) and tok[pos]!=Symbol(')'):
                arr.append(one(depth+1))
            if pos>=len(tok): raise CompileError('missing closing parenthesis')
            pos+=1
            return Node(tuple(arr))
        if x==Symbol(')'):raise CompileError('unexpected closing parenthesis')
        return x
    result=one(0)
    if pos!=len(tok):raise CompileError('multiple top-level expressions')
    if not isinstance(result,Node):raise CompileError('top-level must be a list')
    return result

def canonical(x:Expr)->str:
    if isinstance(x,Node):return '('+' '.join(canonical(a) for a in x.items)+')'
    if isinstance(x,Symbol):return x.name
    if isinstance(x,int):return str(x)
    return '"'+x.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'

@dataclass(frozen=True)
class Commission:
    task:str
    capabilities:tuple[str,...]
    deny:tuple[str,...]
    budget:int
    evidence:str
    source:str

def compile_commission(source:str)->Commission:
    ast=parse(source)
    if not ast.items or ast.items[0]!=Symbol('commission'):raise CompileError('expected commission')
    data={}; caps=[];deny=[]
    for e in ast.items[1:]:
        if not isinstance(e,Node) or not e.items or not isinstance(e.items[0],Symbol):raise CompileError('malformed statement')
        key=e.items[0].name;args=e.items[1:]
        if key in {'task','evidence','budget'}:
            if key in data or len(args)!=1:raise CompileError('duplicate or invalid singleton')
            data[key]=args[0]
        elif key in {'require','deny'}:
            if len(args)!=1 or not isinstance(args[0],str):raise CompileError('require/deny expects string')
            (caps if key=='require' else deny).append(args[0])
        else: raise CompileError('unknown form: '+key)
    if not isinstance(data.get('task'),str) or not data['task']:raise CompileError('nonempty task required')
    if not isinstance(data.get('budget',64),int) or not 1<=data.get('budget',64)<=10000:raise CompileError('invalid budget')
    if isinstance(data.get('evidence'),Symbol):data['evidence']=data['evidence'].name
    if data.get('evidence','fixture') not in {'fixture','attested'}:raise CompileError('invalid evidence requirement')
    if not caps:raise CompileError('at least one capability required')
    if len(set(caps))!=len(caps):raise CompileError('duplicate capability')
    return Commission(data['task'],tuple(caps),tuple(deny),data.get('budget',64),data.get('evidence','fixture'),canonical(ast))
