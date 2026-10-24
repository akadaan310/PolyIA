"""Proleptics: seal a prediction before the witness is opened.

prolepsis (Gk. πρόληψις, 'a taking-beforehand'): in Epicurean epistemology the
preconception that precedes the experience it later recognises.  Here it is a
protocol, not a doctrine:

  1. GENERATE  a grammar produces predictions with no access to the witness data;
  2. SEAL      the predictions are canonicalised, SHA-256 hashed and appended to a
               hash-chained ledger *before* any witness bytes are read;
  3. WITNESS   the witness source is loaded, its own hash recorded;
  4. RECOGNISE precision/recall/agreement are computed against the sealed bytes;
  5. ACCOUNT   misses (predicted, not witnessed) and gaps (witnessed, not predicted)
               are kept as data: misses are candidate *in-grammar* (what the world
               refuses that the grammar admits), gaps are grammar deficits.

The ledger order is the evidence that prediction preceded witness.  It is honest
about its limit: it proves order inside this run, not that the author never saw the
witness before (that is controlled by what the generating code is allowed to read,
which is declared in each experiment).
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "results" / "proleptic_ledger.jsonl"


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _head():
    if not LEDGER.exists():
        return "GENESIS"
    lines = LEDGER.read_text().strip().splitlines()
    return json.loads(lines[-1])["hash"] if lines else "GENESIS"


def _append(entry: dict) -> dict:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    entry = dict(entry, prev=_head(), t=round(time.time(), 3))
    entry["hash"] = sha(canon({k: v for k, v in entry.items() if k != "hash"}))
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return entry


def seal(experiment: str, predictions, grammar: str, reads: list[str]) -> dict:
    """reads: the data the generator was allowed to read (declared)."""
    blob = canon(predictions)
    out = LEDGER.parent / f"{experiment}.sealed.json"
    out.write_bytes(blob)
    return _append({"op": "SEAL", "experiment": experiment, "grammar": grammar, "generator_reads": reads,
                    "predictions_sha256": sha(blob), "n": len(predictions) if hasattr(predictions, "__len__") else None})


def witness(experiment: str, source: str, source_bytes: bytes, metrics: dict) -> dict:
    sealed = LEDGER.parent / f"{experiment}.sealed.json"
    if not sealed.exists():
        raise RuntimeError("refused: no sealed prediction for this experiment (witness before prediction)")
    lines = [json.loads(l) for l in LEDGER.read_text().splitlines()]
    s = [l for l in lines if l["op"] == "SEAL" and l["experiment"] == experiment]
    if not s or s[-1]["predictions_sha256"] != sha(sealed.read_bytes()):
        raise RuntimeError("refused: sealed predictions were altered after sealing")
    return _append({"op": "WITNESS", "experiment": experiment, "witness_source": source,
                    "witness_sha256": sha(source_bytes), "sealed_sha256": s[-1]["predictions_sha256"], "metrics": metrics})


def verify() -> bool:
    prev = "GENESIS"
    for l in LEDGER.read_text().splitlines():
        e = json.loads(l)
        h = e.pop("hash")
        if e["prev"] != prev or sha(canon(e)) != h:
            return False
        prev = h
    return True


def sealed(experiment: str):
    return json.loads((LEDGER.parent / f"{experiment}.sealed.json").read_bytes())
