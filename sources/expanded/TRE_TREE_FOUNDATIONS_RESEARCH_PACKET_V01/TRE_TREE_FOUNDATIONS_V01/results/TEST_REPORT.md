# Execution report — 2026-10-22

Commands executed in working container:

```sh
PYTHONPATH=. python -m unittest discover -s test -q
PYTHONPATH=. python examples/run.py
python -m json.tool schemas/TRE_CORE.contract.schema.json
python -m json.tool results/tree_fixture.json
```

Results: **36 unit tests passed**, no failures, no external dependencies. Fixture: 8 structural nodes, 3 typed coupling relations, maximum ancestry depth 4, one branch with 2 sibling leaves, 7 versioned events. Domain-separated state content ID and chain continuity verified by tests. Corpus wrapper rejected out-of-contract inputs and inadmissible bridges; object graph tamper detection tested.

Limits: no actual GL/GPU pixel measurement, no physics library compilation, no Android APK or IPA, no Unreal source checkout, no natural tree data, no multi-scale morphology comparison, no independent cryptographic audit, no full native PILLAR9 compiler integration. The sample's resource quantities are invented computational units and the output position rule uses a deterministic golden-angle heuristic; none is calibrated to biology.
