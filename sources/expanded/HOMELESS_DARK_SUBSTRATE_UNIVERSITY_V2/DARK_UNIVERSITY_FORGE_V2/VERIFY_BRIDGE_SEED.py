import json
from pathlib import Path
p=Path(__file__).with_name("UNIVERSITY_DARK_BRIDGE_SEED.json")
d=json.loads(p.read_text())
ids=[i["id"] for i in d["divisions"]]
assert ids==["foundations","relational","languages","geometry","acoustic","worlds"]
assert len(set(x["dark_module"] for x in d["divisions"]))==6
assert all(x["source"].endswith(".ts") and x["witness"] for x in d["divisions"])
print("6/6 university division bridge mappings present (schema smoke test; implementation not verified)")
