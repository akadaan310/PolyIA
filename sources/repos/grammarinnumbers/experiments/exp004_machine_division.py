"""GIN-EXP-004  The machine behind the symbol: what this host does with x / y.

Hypotheses: GIN-H-011 ("division by zero" is not one behaviour: the same expression
is a compile-time error, a hardware trap, a language exception, an IEEE special
value, undefined behaviour, or an ordinary-looking number, depending on language
and ISA), GIN-H-012 (the SDK's machine models agree with every behaviour that can
be measured on this host), GIN-H-013 (instruction selection maps the one symbol '/'
to different instructions per ISA and type).

Everything here is *measured on this host* except the clang cross-compilations,
which show instruction selection only (the AArch64 and RISC-V code is not run).
"""
import ast
import dis
import json
import os
import re
import shutil
import signal
import subprocess
import sys

from common import HERE, tool_version, write
from ginsdk import machine as M

SRC = os.path.join(HERE, "machine")
BUILD = os.path.join(SRC, "build")
os.makedirs(BUILD, exist_ok=True)


def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, **kw)
    sig = -p.returncode if p.returncode < 0 else None
    shown = " ".join(os.path.relpath(c, HERE) if os.path.isabs(c) else c for c in cmd)
    return {"cmd": shown, "exit": p.returncode,
            "signal": signal.Signals(sig).name if sig else None, "stdout": p.stdout.strip(),
            "stderr": _first_line(p.stderr)}


def _first_line(s):
    s = s.replace(HERE + os.sep, "")
    s = re.sub(r"thread '(\w+)' \(\d+\)", r"thread '\1'", s)
    lines = [l for l in s.strip().splitlines() if l.strip() and not l.startswith("Picked up JAVA_TOOL_OPTIONS")]
    keep = [l.strip() for l in lines if re.search(r"error|panic|Exception|warning|divide|division|zero|overflow", l, re.I)]
    return " | ".join((keep or lines or [""])[:2])[:300]


def have(t):
    return shutil.which(t) is not None


versions = {"gcc": tool_version(["gcc", "--version"]), "clang": tool_version(["clang", "--version"]),
            "java": tool_version(["java", "-version"]), "rustc": tool_version(["rustc", "--version"]),
            "go": tool_version(["go", "version"]), "node": tool_version(["node", "--version"])}
data = {"versions": versions}

# ---------------------------------------------------------------- C (gcc), measured
c = {}
for opt in ("-O0", "-O2"):
    exe = os.path.join(BUILD, f"divide{opt}")
    subprocess.run(["gcc", opt, "-o", exe, os.path.join(SRC, "divide.c"), "-lm"], check=True)
    c[opt] = {
        "int 6/3": run([exe, "int", "6", "3"]), "int 1/0": run([exe, "int", "1", "0"]),
        "int 0/0": run([exe, "int", "0", "0"]), "int INT_MIN/-1": run([exe, "int", "INT_MIN", "-1"]),
        "int -7/2": run([exe, "int", "-7", "2"]),
        "double 1/0": run([exe, "double", "1", "0"]), "double -1/0": run([exe, "double", "-1", "0"]),
        "double 1/-0": run([exe, "double", "1", "-0"]), "double 0/0": run([exe, "double", "0", "0"]),
        "double 0/1": run([exe, "double", "0", "1"]), "double 1/3": run([exe, "double", "1", "3"]),
        "double 1e308/1e-10": run([exe, "double", "1e308", "1e-10"]), "double 1e-310/1e10": run([exe, "double", "1e-310", "1e10"]),
        "sqrt -1": run([exe, "sqrt", "-1", "x"]),
    }
data["c_gcc"] = c

# does the optimizer delete the zero check after the division?
guard = {}
for cc, opt in (("gcc", "-O0"), ("gcc", "-O2"), ("clang", "-O2"), ("clang", "-O3")):
    asm = subprocess.run([cc, opt, "-S", "-o", "-", os.path.join(SRC, "guard.c")], capture_output=True, text=True).stdout
    body = [l.strip().split("#")[0].strip() for l in asm.splitlines() if l.startswith("\t") and not l.strip().startswith(".")]
    body = [b for b in body if b]
    guard[f"{cc} {opt}"] = {"instructions": body, "has_compare_or_test": any(re.match(r"(cmp|test)", l) for l in body),
                  "returns_minus_one_path": any("$-1" in l for l in body)}
data["c_guard_after_division"] = guard

# compile-time behaviour of a constant 1/0
ct = {}
ct["C (gcc -Wall)"] = run(["gcc", "-Wall", "-o", os.path.join(BUILD, "constc"), os.path.join(SRC, "const_div.c")])
if os.path.exists(os.path.join(BUILD, "constc")):
    ct["C (gcc) at run time"] = run([os.path.join(BUILD, "constc")])
if have("go"):
    ct["Go"] = run(["go", "build", "-o", os.path.join(BUILD, "constgo"), os.path.join(SRC, "const_div.go")])
if have("rustc"):
    ct["Rust"] = run(["rustc", "-o", os.path.join(BUILD, "constrs"), os.path.join(SRC, "const_div.rs")])
if have("javac"):
    ct["Java (javac)"] = run(["javac", "-d", BUILD, os.path.join(SRC, "ConstDiv.java")])
    ct["Java at run time"] = run(["java", "-cp", BUILD, "ConstDiv"])
data["constant_one_over_zero"] = ct

# ---------------------------------------------------------------- Java, Rust, Go, JS
if have("javac"):
    subprocess.run(["javac", "-d", BUILD, os.path.join(SRC, "Divide.java")], check=True, capture_output=True)
    J = lambda *a: run(["java", "-cp", BUILD, "Divide", *a])
    data["java"] = {"int 6/3": J("int", "6", "3"), "int 1/0": J("int", "1", "0"), "int MIN/-1": J("min", "0", "-1"),
                    "int -7/2": J("int", "-7", "2"), "double 1/0": J("dbl", "1", "0"), "double 0/0": J("dbl", "0", "0"),
                    "double -1/0": J("dbl", "-1", "0")}
if have("rustc"):
    for prof, flags in (("debug", []), ("release", ["-O"])):
        exe = os.path.join(BUILD, f"divide_rs_{prof}")
        subprocess.run(["rustc", *flags, "-o", exe, os.path.join(SRC, "divide.rs")], check=True, capture_output=True)
        R = lambda *a: run([exe, *a])
        data[f"rust_{prof}"] = {"div 6/3": R("div", "6", "3"), "div 1/0": R("div", "1", "0"), "div MIN/-1": R("div", "MIN", "-1"),
                                "checked 1/0": R("checked", "1", "0"), "checked MIN/-1": R("checked", "MIN", "-1"),
                                "wrapping MIN/-1": R("wrapping", "MIN", "-1"), "f64 1/0": R("f64", "1", "0"), "f64 0/0": R("f64", "0", "0")}
if have("go"):
    exe = os.path.join(BUILD, "divide_go")
    subprocess.run(["go", "build", "-o", exe, os.path.join(SRC, "divide.go")], check=True, capture_output=True)
    data["go"] = {"int32 6/3": run([exe, "int", "6", "3"]), "int32 1/0": run([exe, "int", "1", "0"]),
                  "int32 MIN/-1": run([exe, "min", "0", "-1"]), "float64 1/0": run([exe, "f64", "1", "0"]),
                  "float64 0/0": run([exe, "f64", "0", "0"])}
if have("node"):
    p = subprocess.run(["node", os.path.join(SRC, "divide.js")], capture_output=True, text=True)
    data["javascript"] = json.loads(p.stdout)

# ---------------------------------------------------------------- Python, in process
py = {}
for src in ["6/3", "6//3", "7/2", "7//2", "-7//2", "-7%2", "1/0", "1.0/0.0", "0/0", "0.0/0.0", "1//0", "(-2**31)//-1",
            "0.1+0.2", "2**53+1.0", "float(2**1024)", "10**400/10**399"]:
    try:
        v = eval(src)
        py[src] = repr(v)
    except Exception as e:
        py[src] = f"{type(e).__name__}: {e}"
tree = ast.parse("x / y", mode="eval")
py["ast of 'x / y'"] = ast.dump(tree.body)
py["bytecode of 'x / y'"] = [f"{i.opname} {i.argrepr}".strip() for i in dis.get_instructions(compile(tree, "<expr>", "eval"))]
data["python"] = py

# ---------------------------------------------------------------- instruction selection (clang)
isel = {}
for target in ("x86_64-linux-gnu", "aarch64-linux-gnu", "riscv64-linux-gnu"):
    p = subprocess.run(["clang", "-O2", "-S", "--target=" + target, "-o", "-", os.path.join(SRC, "isel.c")],
                       capture_output=True, text=True)
    funcs, cur = {}, None
    for line in p.stdout.splitlines():
        m = re.match(r"^(idiv|udiv|fdiv):", line)
        if m:
            cur = m.group(1)
            funcs[cur] = []
            continue
        if cur and line.startswith("\t") and not line.strip().startswith(".") and not line.strip().startswith("#"):
            ins = line.strip().split("#")[0].strip()
            if ins:
                funcs[cur].append(ins)
        if cur and re.match(r"^\.Lfunc_end|^\s*\.size", line):
            cur = None
    isel[target] = funcs if p.returncode == 0 else {"error": _first_line(p.stderr)}
data["instruction_selection"] = isel

# ---------------------------------------------------------------- models vs measurement
agree = {}
MIN = -(2 ** 31)
meas_x86 = {"1/0": c["-O0"]["int 1/0"]["signal"], "MIN/-1": c["-O0"]["int INT_MIN/-1"]["signal"]}
agree["x86 model: 1/0 traps"] = (M.div_x86(1, 0).kind == "trap") == (meas_x86["1/0"] == "SIGFPE")
agree["x86 model: MIN/-1 traps"] = (M.div_x86(MIN, -1).kind == "trap") == (meas_x86["MIN/-1"] == "SIGFPE")
agree["x86 model: -7/2 = -3"] = c["-O0"]["int -7/2"]["stdout"] == str(M.div_x86(-7, 2).value)
if "java" in data:
    agree["Java model: MIN/-1 = MIN"] = data["java"]["int MIN/-1"]["stdout"] == str(M.div_java(MIN, -1).value)
    agree["Java model: 1/0 exception"] = "ArithmeticException" in data["java"]["int 1/0"]["stdout"]
if "rust_debug" in data:
    agree["Rust model: 1/0 panics"] = "divide by zero" in data["rust_debug"]["div 1/0"]["stderr"]
    agree["Rust model: MIN/-1 panics (debug)"] = "overflow" in data["rust_debug"]["div MIN/-1"]["stderr"]
    agree["Rust model: MIN/-1 panics (release)"] = "overflow" in data["rust_release"]["div MIN/-1"]["stderr"]
if "go" in data:
    agree["Go model: 1/0 panics"] = "divide by zero" in data["go"]["int32 1/0"]["stderr"]
    agree["Go model: MIN/-1 = MIN"] = data["go"]["int32 MIN/-1"]["stdout"] == str(M.div_go(MIN, -1).value)
agree["Python model: -7//2 = -4"] = py["-7//2"] == str(M.div_python_floor(-7, 2).value)
agree["Python model: 1//0 raises"] = py["1//0"].startswith("ZeroDivisionError")
if "javascript" in data:
    agree["JS BigInt model: 1n/0n RangeError"] = data["javascript"]["1n/0n"].startswith("RangeError")
    agree["JS BigInt model: -7n/2n = -3"] = data["javascript"]["-7n/2n"] == str(M.div_js_bigint(-7, 2).value)
data["model_agreement"] = agree

write("GIN-EXP-004", ["GIN-H-011", "GIN-H-012", "GIN-H-013"], None, data, {"toolchains": versions})
print("EXP-004 done; model agreement:", agree)
