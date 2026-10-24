import json,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'src'))
from rasm_state import *
result={
 'reference':'Arabic Timeless source-derived class tables; toy corpus and features separately scoped',
 'كتب':word_report('كتب'),
 'كتم':word_report('كتم'),
 'كتب_to_كتم':{'same_rasm':dotted_related('كتب','كتم'), 'change':'final ب→م',
            'path_type':'same-articulation-point, not ijam-only', 'articulation':phonetic_relation('ب','م')},
 'consonantal_feature_intersection':{'jahr_and_shiddah':sorted(JAHR&SHIDDAH),'qalqala_inventory':sorted(QALQALA),'excluded_hamza':sorted((JAHR&SHIDDAH)-QALQALA)},
 'standalone_qstr':QuantumString('كتب','كتم','articulation_substitution','FS-ART-01','classical-features','proposed','').address(),
 'distinction':'Hartley candidate count is combinatorial; actual Shannon entropy requires a probability model.'
}
path=pathlib.Path(__file__).resolve().parent/'results'/'demo.json'
path.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=list)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='كتب' and k!='كتم'},ensure_ascii=False,indent=2))
print('written:',path)
