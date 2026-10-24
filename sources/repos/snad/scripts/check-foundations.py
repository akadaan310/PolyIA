#!/usr/bin/env python3
"""Read-only independent checks of three pinned candidate foundation repos.

Usage: python scripts/check-foundations.py --references ../references
The references are optional research inputs, never SDK runtime dependencies.
"""
import argparse
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--references", type=Path, default=Path("../references"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    repositories = [
        ("computationalgrammartheory", "bfe32fc37f7fa61d50da50ecd2aa7fa97c0dd5a1", ["sdk/src/cgtsdk/grammar.py", "sdk/src/cgtsdk/automata.py", "sdk/src/cgtsdk/algorithms/automata.py", "sdk/src/cgtsdk/structures/graphs.py", "LITERATURE_REVIEW.md"]),
        ("grammarinnumbers", "2a94f8a6be686078a9dad88863be9aafc5e6379b", ["sdk/src/ginsdk/numerals.py", "sdk/src/ginsdk/converse.py", "sdk/src/ginsdk/expr.py", "LITERATURE_REVIEW.md"]),
        ("substrateIO", "7ace119a544fc736f0d4ec1d72cded9dad0a83e3", ["substrate/core.py", "substrate/graph.py", "substrate/trace.py", "substrate/projection.py", "substrate/epistemic.py", "research/literature/LITERATURE_MAP.md"]),
    ]
    sources = []
    for name, commit, files in repositories:
        repo = args.references / name
        actual = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        assert actual == commit, f"{name}: wrong revision {actual}"
        sys.path.insert(0, str(repo / "sdk/src" if name != "substrateIO" else repo))
        sources.append({"repository": f"https://github.com/akadaan310/{name}", "commit": commit,
                        "filesInspected": [{"path": path, "sha256": hashlib.sha256((repo/path).read_bytes()).hexdigest(),
                                            "url": f"https://github.com/akadaan310/{name}/blob/{commit}/{path}"} for path in files],
                        "license": "No LICENSE file found at inspected commit; ideas inspected, implementation not copied."})

    from cgtsdk.automata import compile_regex
    from cgtsdk.algorithms.automata import product_reach
    from cgtsdk.structures.graphs import GraphStructure
    from ginsdk.numerals import DigitGrammar
    from ginsdk.converse import divide, NONE, MULTIPLE, UNIQUE
    from substrate.projection import compatibility, coarsest_congruence, to_transitions, from_transitions

    # An independently enumerated finite-walk baseline for product reachability.
    automaton = compile_regex("a b")
    edges = [(0, "a", 1), (1, "b", 2), (0, "b", 3), (3, "b", 3)]
    graph = GraphStructure(4, edges)
    actual, explored = product_reach(graph, 0, automaton, return_explored=True)
    frontier, baseline = [(0, ())], set()
    for depth in range(4 * automaton.size):
        next_frontier = []
        for vertex, word in frontier:
            if automaton.accepts(word):
                baseline.add(vertex)
            next_frontier.extend((dst, word + (label,)) for src, label, dst in edges if src == vertex)
        frontier = next_frontier
    assert actual == baseline == {2} and explored <= 4 * automaton.size

    # Finite enumeration checks affine compilation against independent Horner evaluation.
    grammar = DigitGrammar(2, (0, 1))
    words = [w for n in range(4) for w in itertools.product((0, 1), repeat=n)]
    composition_checks = 0
    for u in words:
        for v in words:
            f = grammar.compile(u).then(grammar.compile(v))
            for start in (-3, 0, 5):
                expected = start
                for digit in u + v:
                    expected = 2 * expected + digit
                assert f(start) == expected
                composition_checks += 1
    inverse = {"1/0": divide(1, 0).kind, "0/0": divide(0, 0).kind, "6/3": divide(6, 3).kind}
    assert inverse == {"1/0": NONE, "0/0": MULTIPLE, "6/3": UNIQUE}

    # Projection can erase a distinction that affects the very next observation.
    table = [0, 1, 1, 3]
    projection = lambda x: x % 2
    counterexample = compatibility(table, projection)
    assert counterexample["compatible"] is False
    assert projection(0) == projection(2) and projection(table[0]) != projection(table[2])
    blocks = coarsest_congruence(table, projection)
    for a, b in itertools.product(range(4), repeat=2):
        if blocks[a] == blocks[b]:
            assert projection(a) == projection(b) and blocks[table[a]] == blocks[table[b]]
    sequence = [0, 1, 3, 2, 0]
    assert from_transitions(sequence[0], to_transitions(sequence)) == sequence

    report = {"schemaVersion": "snad.foundation-audit.v1", "date": "2026-10-18", "sources": sources,
              "independentReconstructions": [
                  {"id": "foundation-regular-path", "source": "CGT product_reach", "status": "reproduced-computationally", "acceptedEndpoints": sorted(actual), "exhaustiveBaselineEndpoints": sorted(baseline), "exploredProductStates": explored, "finiteBound": 4 * automaton.size},
                  {"id": "foundation-affine-composition", "source": "GiN DigitGrammar / Affine.then", "status": "reproduced-computationally", "checks": composition_checks, "inverseClassification": inverse},
                  {"id": "foundation-projection", "source": "SubstrateIO compatibility / coarsest_congruence", "status": "reproduced-computationally", "table": table, "projection": "x mod 2", "counterexample": {"equalProjectedStates": [0, 2], "differentNextObservations": [0, 1]}, "refinedBlocks": blocks, "xorRoundtrip": True}],
              "scope": "Small independent executable comparisons of inspected implementations, not new theorems, empirical linguistic validation, or physical discoveries.",
              "command": "python scripts/check-foundations.py --references ../references"}
    (root / "evidence/foundations-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["independentReconstructions"], indent=2))


if __name__ == "__main__":
    main()
