#!/usr/bin/env python3
"""Verify actual source bytes, obligation coverage and optional release manifest.

No network, source execution, dependency install or model invocation occurs.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT=Path(__file__).resolve().parent.parent
def sha(data):return hashlib.sha256(data).hexdigest()
def read_json(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))

def release_paths():
    """Exact distributed file census, excluding documented local runtime output."""
    result=set()
    for p in ROOT.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        # Archived manifests and tracked upstream bytecode are original sources.
        # Local build-output exclusions must never remove those canonical bytes.
        if rel.parts[0]=='sources':
            result.add(str(rel));continue
        if str(rel)=='MANIFEST_SHA256.json':continue
        if any(part in {'.git','__pycache__','.polyia-state'} or part.startswith('bootstrap-demo-') for part in rel.parts):continue
        if p.suffix in {'.pyc','.pyo'}:continue
        result.add(str(rel))
    return result

def verify(require_release=False):
    errors=[];counts={}
    def check(value,message):
        if not value:errors.append(message)
    def safe(path):
        p=ROOT/path
        if not p.resolve().is_relative_to(ROOT):raise ValueError('Out-of-package path: '+str(path))
        return p
    sources=read_json('registry/sources.json')
    for f in sources['files']:
        p=safe(f['path'])
        check(p.is_file(),'Missing source '+f['path'])
        if p.is_file():
            raw=p.read_bytes();check(len(raw)==f['bytes'] and sha(raw)==f['sha256'],'Source bytes differ: '+f['path'])
    expected_source_paths={f['path'] for f in sources['files']}
    actual_source_paths={str(p.relative_to(ROOT)) for p in (ROOT/'sources').rglob('*') if p.is_file()}
    check(actual_source_paths==expected_source_paths,'Source census differs from actual files: '+str(sorted(actual_source_paths^expected_source_paths)[:10]))
    counts['source_files']=len(expected_source_paths)
    repos=read_json('registry/repositories.json')['repositories'];total_blobs=0
    for repo in repos:
        prefix=ROOT/'sources/repos'/repo['repository'].split('/')[-1]
        tracked={f['repository_path'] for f in repo['files']}
        actual={str(p.relative_to(prefix)) for p in prefix.rglob('*') if p.is_file()}
        check(actual==tracked,'Repository snapshot missing/extra file: '+repo['repository'])
        for f in repo['files']:
            p=safe(f['path'])
            if not p.is_file():continue
            raw=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            check(blob==f['git_blob'] and sha(raw)==f['sha256'],'Git blob mismatch '+f['path'])
        check(repo['file_count']==len(tracked) and repo['complete_tree'] and not repo['truncated'],'Incomplete Git tree '+repo['repository'])
        total_blobs+=len(tracked)
    counts.update(repository_snapshots=len(repos),repository_blobs=total_blobs)
    archives=read_json('registry/archives.json')['archives'];members=0
    for arc in archives:
        p=safe(arc['archive']);raw=p.read_bytes();check(sha(raw)==arc['sha256'],'Archive digest mismatch '+arc['archive'])
        with zipfile.ZipFile(p) as z:
            check(z.testzip() is None,'Bad archive CRC '+arc['archive'])
            check({i.filename for i in z.infolist() if not i.is_dir()}=={x['member'] for x in arc['members']},'Archive member census differs '+arc['archive'])
            for f in arc['members']:
                data=z.read(f['member']);check(sha(data)==f['sha256'] and data==safe(f['path']).read_bytes(),'Extracted member mismatch '+f['path'])
            members+=len(arc['members'])
    counts.update(unique_expanded_archives=len(archives),expanded_members=members)
    constitution=read_json('registry/constitution.json');req=constitution['requirements'];keys=[x['id'] for x in req]
    mission=[x for x in req if x['id'].startswith('PIA-')]
    check(len(keys)==len(set(keys)),'Duplicate obligation identity')
    check([x['id'] for x in mission]==[f'PIA-{i:03}' for i in range(1,193)],'Mission obligations are not exactly PIA-001..192')
    known_sources={x['id'] for x in sources['sources']}
    known_continuity={x['id'] for x in read_json('registry/continuity.json')['keys']}
    for r in mission:
        check(bool(r.get('mandate')) and bool(r.get('acceptance')),'Missing obligation contract '+r['id'])
        check(set(r['source_refs'])<=known_sources,'Unknown source reference '+r['id'])
        check(set(r['continuity'])<=known_continuity,'Unknown continuity key '+r['id'])
        check(r['verifier']=='commission-evidence','Mission verifier unexpectedly auto-accepts '+r['id'])
    god=(ROOT/'GOD_SEED.md').read_text()
    check(re.findall(r'^### (PIA-\d{3}) ·',god,re.M)==[x['id'] for x in mission],'God seed headings and registry disagree')
    core=read_json('registry/inherited_obligations.json')['obligations']
    origins={x['origin_id'] for x in core}
    check(origins=={f'POLY-C-{i:03}' for i in range(1,97)}|{f'UCG-{i:03}' for i in range(1,157)},'Core inherited origin census differs')
    for e in core:
        check(set(e['target_requirements'])<=set(keys) and bool(e['target_requirements']),'Unmapped core obligation '+e['origin_id'])
        raw=safe(e['source_path']).read_bytes();check(sha(raw)==e['source_sha256'],'Inherited source drift '+e['origin_id'])
        check(e['original_text'] in raw.decode('utf-8'),'Inherited text missing from source '+e['origin_id'])
        check(sha(e['original_text'].encode())==e['original_text_sha256'],'Inherited text digest differs '+e['origin_id'])
    counts.update(mission_obligations=len(mission),core_inherited_obligations=len(core))
    supplemental=ROOT/'registry/inherited_supplemental.json'
    check(supplemental.is_file(),'Supplemental inherited registry missing')
    if supplemental.is_file():
        data=json.loads(supplemental.read_text())
        by_digest=defaultdict(list);delegated=defaultdict(list);seen=set();span_origins=[]
        core_by_id={e['origin_id']:e for e in core}
        source_by_path={f['path']:f for f in sources['files']}
        selected_bytes=0;selected_paths=set();alias_paths=set()
        for e in data['records']:
            check(e['origin_id'] not in seen,'Duplicate supplemental origin '+e['origin_id']);seen.add(e['origin_id'])
            check(bool(e['target_obligations']) and set(e['target_obligations'])<=set(keys),'Unmapped supplemental target '+e['origin_id'])
            check(e['disposition'] in data['disposition_values'],'Invalid supplemental disposition '+e['origin_id'])
            by_digest[e['source_sha256']].append(e)
        for e in data['delegated_core_spans']:
            delegated[e['source_sha256']].append(e);span_origins.append(e['origin_clause'])
            check(e['origin_clause'] in core_by_id,'Unknown delegated core origin '+e['origin_clause'])
        doc_digests=[s['sha256'] for s in data['sources']]
        check(len(set(doc_digests))==len(doc_digests),'Duplicate supplemental document digest')
        check(set(by_digest)|set(delegated)==set(doc_digests),'Orphan or missing supplemental source')
        for s in data['sources']:
            raw=safe(s['canonical_path']).read_bytes();digest=s['sha256'];parts=[]
            check(sha(raw)==digest and len(raw)==s['bytes'],'Supplemental source bytes differ '+s['canonical_path'])
            check(s['canonical_path'] in source_by_path and source_by_path[s['canonical_path']]['sha256']==digest,'Supplemental source absent from source manifest')
            selected_bytes+=len(raw);selected_paths.update(s['selected_alias_paths']);alias_paths.update(s['all_byte_identical_alias_paths'])
            for e in by_digest[digest]:
                loc=e['locator'];a,b=loc['byte_start'],loc['byte_end_exclusive'];text=e['text_verbatim'].encode('utf-8')
                check(type(a) is int and type(b) is int and 0<=a<b<=len(raw),'Invalid supplemental byte range '+e['origin_id'])
                check(raw[a:b]==text and sha(text)==e['text_sha256'] and len(text)==e['byte_length'],'Supplemental text differs '+e['origin_id'])
                parts.append((a,b,text))
            for e in delegated[digest]:
                a,b=e['byte_start'],e['byte_end_exclusive'];text=raw[a:b]
                check(type(a) is int and type(b) is int and 0<=a<b<=len(raw),'Invalid core byte range '+e['origin_clause'])
                check(sha(text)==e['text_sha256'],'Delegated text digest differs '+e['origin_clause'])
                check(e['origin_clause'] in core_by_id and text.decode('utf-8') in core_by_id[e['origin_clause']]['original_text'],'Delegated core text differs '+e['origin_clause'])
                parts.append((a,b,text))
            end=0;reconstructed=[]
            for a,b,text in sorted(parts):
                check(a==end,'Supplemental partition gap/overlap '+s['canonical_path']+' at '+str(a));end=b;reconstructed.append(text)
            check(end==len(raw) and b''.join(reconstructed)==raw,'Supplemental reconstruction failed '+s['canonical_path'])
            check(set(s['supplemental_origin_ids'])=={e['origin_id'] for e in by_digest[digest]},'Supplemental source index differs')
            check(set(s['delegated_core_clause_ids'])=={e['origin_clause'] for e in delegated[digest]},'Delegated source index differs')
            for alias in s['all_byte_identical_alias_paths']:
                check(alias in source_by_path and safe(alias).read_bytes()==raw,'Supplemental alias differs '+alias)
        check(set(span_origins)==origins and len(span_origins)==len(core),'Delegated core coverage differs')
        derived={'unique_source_documents':len(doc_digests),'selected_paths':len(selected_paths),
                 'all_alias_paths':len(alias_paths),'supplemental_segments':len(seen),'delegated_core_clauses':len(span_origins),
                 'unique_selected_source_bytes':selected_bytes,'dispositions':dict(Counter(e['disposition'] for e in data['records']))}
        for key,value in derived.items():check(data['counts'][key]==value,'Supplemental declared count differs: '+key)
        check(not data['unresolved_originals'] and not data['read_errors'],'Unresolved supplemental custody error')
        counts.update(supplemental_documents=len(doc_digests),supplemental_segments=len(seen),
                      supplemental_partition_bytes=selected_bytes,supplemental_registry_bytes=supplemental.stat().st_size)
    uni=read_json('registry/university.json')
    check(len(uni['topics'])==62 and len({x['id'] for x in uni['topics']})==62,'Canonical topic identity mismatch')
    check(next(x for x in uni['divisions'] if x['id']=='infinity')['numeral']=='IX','Infinity current numeral mismatch')
    check(all(next(x for x in uni['divisions'] if x['numeral']==n)['status']=='open-research-charter' for n in ('VII','VIII')),'Open charter state mismatch')
    acceptance=read_json('registry/acceptance.json')
    check({x['requirement_id'] for x in acceptance['requirements']}=={x['id'] for x in mission},'Acceptance coverage incomplete')
    families={x['id'] for x in acceptance['families']}
    for row in acceptance['requirements']:check(set(row['families'])<=families,'Unknown acceptance family '+row['requirement_id'])
    works=read_json('registry/work_contracts.json')['contracts'];workids={x['id'] for x in works}
    for w in works:
        check(set(w['dependencies'])<=workids and set(w['obligations'])<=set(keys),'Invalid DODGE reference '+w['id'])
        for path in w['production_paths']:check(safe(path).exists(),'Missing DODGE production '+path)
    manifest=ROOT/'MANIFEST_SHA256.json'
    if manifest.is_file():
        md=json.loads(manifest.read_text());listed=set()
        for f in md['files']:
            p=safe(f['path']);listed.add(f['path']);check(p.is_file(),'Missing release file '+f['path'])
            if p.is_file():check(sha(p.read_bytes())==f['sha256'] and p.stat().st_size==f['bytes'],'Release file changed '+f['path'])
        check(len(listed)==len(md['files']),'Duplicate release manifest path')
        check(listed==release_paths(),'Release manifest census differs: '+str(sorted(listed^release_paths())[:10]))
        counts['release_manifest_files']=len(listed)
    elif require_release:errors.append('Release manifest is required but absent')
    return {'ok':not errors,'counts':counts,'errors':errors,'full_mission_status':'NOT_COMMISSIONED',
            'unresolved_source_identities':[x['id'] for x in sources['unresolved_inputs']],
            'scope':'Package byte custody, references and coverage; does not certify every source claim or full commission implementation.'}

def walk(value):
    yield value
    if isinstance(value,dict):
        for x in value.values():yield from walk(x)
    elif isinstance(value,list):
        for x in value:yield from walk(x)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--require-release-manifest',action='store_true');args=parser.parse_args()
    try:report=verify(args.require_release_manifest)
    except Exception as exc:report={'ok':False,'errors':[type(exc).__name__+': '+str(exc)]}
    print(json.dumps(report,indent=2));sys.exit(0 if report['ok'] else 1)
