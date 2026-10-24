from pathlib import Path
from json import dumps
from tre.core import run_fixture
r=run_fixture(seed='TRE/TREE/2026-10-22')
out=Path(__file__).resolve().parent.parent/'results'/'tree_fixture.json'
out.write_text(dumps(r,indent=2,ensure_ascii=False)+'\n')
print(dumps({'passed':r['invariants_ok'],'topology':r['topology'],'fixture':str(out)},indent=2))
