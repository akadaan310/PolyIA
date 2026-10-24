"""GIN-EXP-007  Multiplication and division circuits; what a divider does with 0.

Hypotheses: GIN-H-018 (the restoring array divider, which contains no test of the
divisor, outputs quotient 2^n − 1 and remainder = dividend when the divisor is 0 —
exactly the result the RISC-V M extension specifies for DIVU/REMU), GIN-H-019
(array multiplier and divider sizes grow quadratically in n).
"""
from common import write
from ginsdk import circuits as K, machine as M

data = {"sizes": [], "zero_divisor": {}, "exhaustive_errors": {}}
for n in range(1, 7):
    m, d = K.array_multiplier(n), K.restoring_divider(n)
    errs = 0
    zero_rows = []
    for x in range(2 ** n):
        for y in range(2 ** n):
            if K.int_of(K.apply_words(m, a=(x, n), b=(y, n))) != x * y:
                errs += 1
            q, r = K.run_divider(d, n, x, y)
            if y and (q, r) != divmod(x, y):
                errs += 1
        q, r = K.run_divider(d, n, x, 0)
        rv = M.divu_riscv(x, 0, n)
        zero_rows.append({"dividend": x, "circuit_q": q, "circuit_r": r, "riscv_q": rv.value, "riscv_r": rv.remainder,
                          "aarch64_q": M.div_aarch64(x, 0, n).value})
    data["exhaustive_errors"][n] = errs
    data["zero_divisor"][n] = {"all_equal_riscv": all(z["circuit_q"] == z["riscv_q"] and z["circuit_r"] == z["riscv_r"] for z in zero_rows),
                               "all_q_all_ones": all(z["circuit_q"] == 2 ** n - 1 for z in zero_rows),
                               "rows": zero_rows if n <= 3 else zero_rows[:4]}
for n in (1, 2, 4, 8, 16, 32):
    m, d = K.array_multiplier(n), K.restoring_divider(n)
    data["sizes"].append({"n": n, "multiplier_gates": m.size, "multiplier_depth": m.depth(),
                          "divider_gates": d.size, "divider_depth": d.depth(), "ripple_adder_gates": K.ripple_adder(n).size})
write("GIN-EXP-007", ["GIN-H-018", "GIN-H-019"], None, data)
print("EXP-007", data["exhaustive_errors"], {n: v["all_equal_riscv"] for n, v in data["zero_divisor"].items()})
for s in data["sizes"]:
    print(s)
