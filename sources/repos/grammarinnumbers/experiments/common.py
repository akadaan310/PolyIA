"""Shared harness for Grammar-in-Numbers experiments.

Every experiment writes ``results/expNNN.json`` with: the experiment id, the
hypotheses it tests, the seed, the environment, and its data.  Counted fields are
deterministic; fields whose names end in ``_s`` (seconds) are wall-clock and
vary by machine (GIN-D-003).
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "sdk", "src"))
RESULTS = os.path.join(HERE, "results")


def tool_version(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = (p.stdout or p.stderr).strip().splitlines()
        out = [l for l in out if not l.startswith("Picked up JAVA_TOOL_OPTIONS")]
        return out[0] if out else "unknown"
    except Exception:  # pragma: no cover - environment dependent
        return "unavailable"


def environment(extra: dict | None = None) -> dict:
    env = {"python": platform.python_version(), "implementation": platform.python_implementation(),
           "machine": platform.machine(), "system": f"{platform.system()} {platform.release()}"}
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    env["cpu"] = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    env.update(extra or {})
    return env


def write(exp_id: str, hypotheses: list[str], seed, data: dict, env_extra: dict | None = None) -> str:
    os.makedirs(RESULTS, exist_ok=True)
    doc = {"experiment": exp_id, "hypotheses": hypotheses, "seed": seed, "environment": environment(env_extra), "data": data}
    path = os.path.join(RESULTS, exp_id.lower().replace("gin-", "").replace("-", "") + ".json")
    with open(path, "w", encoding="utf8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False, sort_keys=False, default=str)
        f.write("\n")
    return path


class Timer:
    def __enter__(self):
        self.t = time.perf_counter()
        return self

    def __exit__(self, *a):
        self.s = time.perf_counter() - self.t
