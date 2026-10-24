#!/usr/bin/env python3
"""Offline metadata integrity checks. NOT Qur'an text collation; see SOURCES_AND_BOUNDARIES.md."""
import json
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent
sites=json.loads((P/'29_cipher_sites.json').read_text(encoding='utf-8'))['sites']
a=json.loads((P/'cipher_alphabets.json').read_text(encoding='utf-8'))
e=json.loads((P/'research_edges.json').read_text(encoding='utf-8'))['links']
U=[x for s in sites for x in s['units']]
seq=[x['sequence'] for x in U]
C=set(a['cipher_alphabet_14']); I=set(a['in_cipher_alphabet_14']); A=set(a['alphabet_28'])
assert len(sites)==29 and len(U)==30 and len(set(seq))==14
assert len(A)==28 and len(C)==14 and len(I)==14 and C.isdisjoint(I) and C|I==A
assert len(''.join(seq))==78 and set(''.join(seq))==C
assert Counter(''.join(seq))==Counter({k:int(v) for k,v in a['letter_frequencies_in_30_units'].items()})
sins=[u['verse_ref'] for u in U if 'س' in u['sequence']]
assert set(sins)=={'26:1','27:1','28:1','36:1','42:2'}
assert sum(x.endswith(':1') for x in sins)==4 and sum(x.endswith(':2') for x in sins)==1
assert next(s for s in sites if s['sura']==42)['units'][0]['sequence']=='حم'
assert next(s for s in sites if s['sura']==42)['units'][1]['sequence']=='عسق'
assert [s['sura'] for s in sites if s['opening'].startswith('حم')]==[40,41,42,43,44,45,46]
assert len({s['site_order'] for s in sites})==29
assert len({u['unit_id'] for u in U})==30
assert len({x['id'] for x in e})==len(e)
for item in e:
 assert item['from']['verse_ref'] and item['to']['verse_ref'] and item['epistemic_layer'] and item['relation']
for label in ['النمل','النحل','صنع','صرحا','الفتية','صنوان']:
 assert any(x['surface']==label for x in a['examples']),label
ex={x['surface']:x for x in a['examples']}
assert ex['النمل']['cipher_only'] and ex['النحل']['cipher_only'] and ex['صنع']['cipher_only'] and ex['صرحا']['cipher_only']
assert not ex['الفتية']['cipher_only'] and not ex['صنوان']['cipher_only']
print('PASS: 29 sites, 30 units, 14 unit types, 78 letter occurrences, 14/14 alphabet partition, 5 Sin occurrences, 7 Hawamim, 42:1-2 split')
print('NOTE: This checks packet metadata only. It DOES NOT validate canonical Quranic text; source-corpus integrity must be verified at build time.')
