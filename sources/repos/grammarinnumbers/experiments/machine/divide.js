const out = {};
out["1/0"] = String(1 / 0);
out["-1/0"] = String(-1 / 0);
out["1/-0"] = String(1 / -0);
out["0/0"] = String(0 / 0);
out["0/1"] = String(0 / 1);
out["6/3"] = String(6 / 3);
out["7/2"] = String(7 / 2);
out["(2**31)|0"] = String((2 ** 31) | 0);
out["0.1+0.2"] = String(0.1 + 0.2);
out["2**53+1"] = String(2 ** 53 + 1);
for (const [k, f] of [["1n/0n", () => 1n / 0n], ["0n/0n", () => 0n / 0n], ["7n/2n", () => 7n / 2n], ["-7n/2n", () => -7n / 2n], ["(-(2n**31n))/-1n", () => (-(2n ** 31n)) / -1n]]) {
  try { out[k] = String(f()); } catch (e) { out[k] = e.constructor.name + ": " + e.message; }
}
console.log(JSON.stringify(out));
