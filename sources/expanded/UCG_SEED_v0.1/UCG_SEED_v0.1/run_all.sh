#!/bin/sh
# Reproduce every sealed result from scratch (fresh ledger), then run the conformance suite.
set -e
cd "$(dirname "$0")"
rm -f results/proleptic_ledger.jsonl results/*.sealed.json
for e in experiments/e0*.py; do echo "== $e"; python3 "$e" > "results/$(basename $e .py).log" 2>&1; tail -2 "results/$(basename $e .py).log"; done
python3 -m unittest discover -s tests
