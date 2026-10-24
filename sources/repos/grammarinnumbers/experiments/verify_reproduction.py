"""Re-run all experiments into a temporary copy and compare counted fields with the
committed results.  Wall-clock fields (keys ending in '_s'), the environment block
and tool-version strings are ignored.  Exit status 1 on any difference."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if not k.endswith("_s") and k not in ("environment", "versions")}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def main():
    saved = tempfile.mkdtemp()
    for f in os.listdir(RES):
        shutil.copy(os.path.join(RES, f), saved)
    try:
        subprocess.run(["sh", os.path.join(HERE, "run_all.sh")], check=True, capture_output=True)
        diffs = []
        for f in sorted(os.listdir(saved)):
            if not f.endswith(".json"):
                continue
            old = strip(json.load(open(os.path.join(saved, f))))
            new = strip(json.load(open(os.path.join(RES, f))))
            if old != new:
                diffs.append(f)
        print("identical counted fields in all result files" if not diffs else f"DIFFERENCES in: {diffs}")
        return 1 if diffs else 0
    finally:
        for f in os.listdir(saved):
            shutil.copy(os.path.join(saved, f), RES)


if __name__ == "__main__":
    sys.exit(main())
