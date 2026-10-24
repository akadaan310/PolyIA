"""ginsdk — the executable companion to *Grammar in Numbers*.

Research program of Abed Kadaan (Founding Principal Researcher). Standard library only.

Modules
-------
numerals      numerals as operation expressions; addresses; affine compilation
peano         the successor grammar, primitive recursion with rule counts, segments a{I}b
converse      inverse operations as converse relations; solution-set admissibility
expr          arithmetic as a language: parse trees, typing, layered evaluation in 20+ domains
ieee          IEEE 754 binary formats, exact-rational reference simulator with flags
machine       integer semantics of x86-64, AArch64, RISC-V, C, Java, Rust, Python, JS
circuits      gate-level adders (ripple and prefix), carry monoid, multiplier, divider
bigint        limb arithmetic with counted word operations (bit complexity)
numbertheory  Euclid, Bézout, CRT, exponentiation, primality, factorization
cost          explicit cost counters
"""
from . import bigint, circuits, converse, cost, expr, ieee, machine, numbertheory, numerals, peano
from .converse import SolutionSet, divide, divide_mod, square_root, subtract
from .cost import Cost
from .expr import compare, evaluate, parse
from .numerals import BINARY, DECIMAL, UNARY, DigitGrammar, bijective, standard

__version__ = "0.1.0"
__all__ = ["bigint", "circuits", "converse", "cost", "expr", "ieee", "machine", "numbertheory", "numerals", "peano",
           "SolutionSet", "divide", "divide_mod", "square_root", "subtract", "Cost", "compare", "evaluate", "parse",
           "BINARY", "DECIMAL", "UNARY", "DigitGrammar", "bijective", "standard"]
