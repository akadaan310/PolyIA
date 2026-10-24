"""GIN-EXP-005  Validating the IEEE 754 reference simulator against this CPU.

Hypotheses: GIN-H-014 (exact-rational evaluation followed by one round-to-nearest-even
step reproduces the hardware's binary32 and binary64 results bit for bit, including
±0, ±∞, NaN-ness and subnormals), GIN-H-015 (it also reproduces all five exception
flags, provided tininess is detected the way the host detects it).

Oracle: experiments/machine/fpharness.c compiled with gcc -O0 -frounding-math,
using SSE scalar instructions on x86-64 and fenv.h to read the flags.  NaN
payloads and signs are not compared (the simulator does not model them).
Inputs: random bit patterns, a biased stream of special and boundary values, and a
targeted family of products whose exact value lies just below the smallest normal
number but rounds up to it — the only cases where 'before' and 'after' tininess
differ.
"""
import os
import random
import subprocess
from fractions import Fraction

from common import HERE, tool_version, write
from ginsdk import ieee as I

SEED = 754
rng = random.Random(SEED)
exe = os.path.join(HERE, "machine", "build", "fpharness")
os.makedirs(os.path.dirname(exe), exist_ok=True)
subprocess.run(["gcc", "-O0", "-frounding-math", "-fno-fast-math", "-o", exe, os.path.join(HERE, "machine", "fpharness.c"), "-lm"], check=True)

FMT = {32: I.BINARY32, 64: I.BINARY64}
OPS = ["add", "sub", "mul", "div", "sqrt"]
SIM = {"add": I.add, "sub": I.sub, "mul": I.mul, "div": I.div}


def special(w):
    f = FMT[w]
    one = I.from_int(1, f)[0].bits()
    cands = [0, 1 << (w - 1), one, one | (1 << (w - 1)), 1, (1 << (f.p - 1)),          # ±0, ±1, min subnormal, min normal
             I.FP(f, "inf").bits(), I.FP(f, "inf", 1).bits(),                                       # ±inf
             I.FP(f, "finite", 0, f.max_finite).bits(), (1 << (f.p - 1)) - 1]                # max finite, max subnormal
    return [c for c in cands if c is not None]


def gen(w, n):
    sp = special(w)
    out = []
    for _ in range(n):
        k = rng.random()
        if k < 0.15:
            a, b = rng.choice(sp), rng.choice(sp)
        elif k < 0.3:
            a, b = rng.getrandbits(w), rng.choice(sp)
        elif k < 0.45:      # nearby exponents: cancellation and exact results
            a = rng.getrandbits(w)
            b = (a ^ rng.getrandbits(8)) if rng.random() < 0.5 else a + rng.randint(-3, 3)
            b &= (1 << w) - 1
        elif k < 0.6:       # small magnitudes: subnormal territory
            a = rng.getrandbits(w - 1 - 2) | (rng.getrandbits(1) << (w - 1))
            b = rng.getrandbits(w - 1) | (rng.getrandbits(1) << (w - 1))
        else:
            a, b = rng.getrandbits(w), rng.getrandbits(w)
        out.append((a, b))
    return out


def tininess_cases(w, n):
    """a·b whose exact value lies in (λ(1 − 2^-p), λ): rounds up to λ = min normal."""
    f = FMT[w]
    lam = f.min_normal
    cases = []
    tries = 0
    while len(cases) < n and tries < 200000:
        tries += 1
        ma = rng.randrange(2 ** (f.p - 1), 2 ** f.p)
        x = Fraction(ma, 2 ** (f.p - 1))                     # a in [1, 2)
        target = lam * (1 - Fraction(rng.randrange(1, 2 ** 20), 2 ** (f.p + 21)))
        y = target / x
        bfp, _ = I.round_exact(f, y)
        if bfp.cls != "finite" or bfp.mag == 0:
            continue
        prod = x * bfp.value()
        if lam * (1 - Fraction(1, 2 ** f.p)) < prod < lam:
            afp, _ = I.round_exact(f, x)
            cases.append((afp.bits(), bfp.bits()))
    return cases


def sim(op, w, a, b, tininess):
    f = FMT[w]
    x, y = I.from_bits(f, a), I.from_bits(f, b)
    if op == "sqrt":
        r, fl = I.sqrt(x)
    else:
        r, fl = SIM[op](x, y, tininess)
    return r, fl


def hw_run(lines):
    p = subprocess.run([exe], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
    return p.stdout.split("\n")


data = {"oracle": "gcc -O0 -frounding-math, SSE scalar arithmetic, fenv.h flags", "per_format": {}}
FLAG_ORDER = ["invalid", "divideByZero", "overflow", "underflow", "inexact"]
for w, N in ((32, 40000), (64, 40000)):
    f = FMT[w]
    cases = [(op, a, b) for op in OPS for (a, b) in gen(w, N // len(OPS))]
    tiny = [("mul", a, b) for (a, b) in tininess_cases(w, 300)]
    allc = cases + tiny
    out = hw_run([f"{op} {w} {a:x} {b:x}" for op, a, b in allc])
    stats = {}
    for tin in ("after", "before"):
        res_mis = flag_mis = 0
        examples = []
        tiny_flag_mis = 0
        for idx, ((op, a, b), line) in enumerate(zip(allc, out)):
            hr, hf = line.split()
            hr = int(hr, 16)
            r, fl = sim(op, w, a, b, tin)
            hfp = I.from_bits(f, hr)
            same = (hfp.is_nan and r.is_nan) or (not hfp.is_nan and not r.is_nan and hfp.bits() == r.bits())
            sflags = "".join("1" if k in fl else "0" for k in FLAG_ORDER)
            if not same:
                res_mis += 1
                if len(examples) < 5:
                    examples.append({"op": op, "a": hex(a), "b": hex(b), "hw": hex(hr), "sim": hex(r.bits())})
            if sflags != hf:
                flag_mis += 1
                if idx >= len(cases):
                    tiny_flag_mis += 1
                if len(examples) < 5:
                    examples.append({"op": op, "a": hex(a), "b": hex(b), "hw_flags": hf, "sim_flags": sflags})
        stats[f"tininess_{tin}"] = {"result_mismatches": res_mis, "flag_mismatches": flag_mis,
                                    "flag_mismatches_in_tininess_family": tiny_flag_mis, "examples": examples}
    hw_tiny_underflow = sum(1 for line in out[len(cases):len(allc)] if line.split()[1][3] == "1")
    data["per_format"][f.name] = {"random_and_special_cases": len(cases), "tininess_family_cases": len(tiny),
                                  "hardware_underflow_flag_in_tininess_family": hw_tiny_underflow, **stats}
fam = [(v["tininess_after"]["flag_mismatches_in_tininess_family"], v["tininess_before"]["flag_mismatches_in_tininess_family"])
       for v in data["per_format"].values()]
data["conclusion_host_tininess"] = ("after rounding" if all(a == 0 and b > 0 for a, b in fam) else
                                    "before rounding" if all(b == 0 and a > 0 for a, b in fam) else "undetermined")
write("GIN-EXP-005", ["GIN-H-014", "GIN-H-015"], SEED, data, {"gcc": tool_version(["gcc", "--version"])})
print("EXP-005", {k: (v["tininess_after"]["result_mismatches"], v["tininess_after"]["flag_mismatches"],
                     v["tininess_before"]["flag_mismatches"], v["tininess_family_cases"], v["hardware_underflow_flag_in_tininess_family"]) for k, v in data["per_format"].items()},
      data["conclusion_host_tininess"])
