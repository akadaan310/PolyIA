#!/bin/sh
# Reproduce every Grammar-in-Numbers experiment (Python >= 3.10, stdlib only;
# EXP-004/005 also need gcc, and optionally clang, javac/java, rustc, go, node).
set -e
cd "$(dirname "$0")"
for f in exp0*.py; do
  echo "== $f"
  python3 "$f"
done
python3 check_theorems.py
python3 analyze.py
