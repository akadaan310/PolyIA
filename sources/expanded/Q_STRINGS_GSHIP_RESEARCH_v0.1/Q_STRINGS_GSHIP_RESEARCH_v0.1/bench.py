"""Microbenchmark comparable query tasks: adjacency scan, ordinary triple hash, Q-String index.
Note: Python process overhead and serialization, not an optimized systems-language benchmark.
"""
import random,time,sys,json,platform,gc,tracemalloc,statistics
from collections import defaultdict
from src.qstrings import QStore,QString,Rule

def memory_build(fn):
    gc.collect();tracemalloc.start();obj=fn();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop();return obj,peak

def bench_check(fn,qs):
    for q in qs[:min(25,len(qs))]:fn(*q)
    gc.disable()
    try:
        times=[]
        for _ in range(5):
            t0=time.perf_counter_ns()
            x=sum(1 for q in qs if fn(*q))
            times.append((time.perf_counter_ns()-t0)/len(qs))
        return {'ns_per_query_median':round(statistics.median(times),1),'hits':x,'runs':5}
    finally:
        gc.enable()

def main():
    results=[]
    for n,m in [(128,2048),(256,8192),(512,24576)]:
        rng=random.Random(89+n)
        edges=set()
        while len(edges)<m:
            edges.add((rng.randrange(n),rng.randrange(n),rng.choice(('next','depends','supports'))))
        edges=sorted((str(a),str(b),r) for a,b,r in edges)
        queries=rng.sample(edges,min(1800,len(edges)))+[(a,b,'missing') for a,b,_ in rng.sample(edges,min(1800,len(edges)))]
        rng.shuffle(queries)
        # Same key workload. Two baselines differ only in indexing strategy.
        def adjacency_build():
            adj=defaultdict(list)
            for a,b,r in edges:adj[a].append((b,r))
            return adj
        def triple_build():
            return {e: True for e in edges}
        def q_build():
            st=QStore()
            for i in range(n):st.sort(str(i),'Node')
            for r in ('next','depends','supports'): st.rule(Rule(r,'Node','Node','edges'))
            for a,b,r in edges: st.insert(QString(a,b,r,'edges'))
            return st
        adjacency,ma=memory_build(adjacency_build)
        triple,mt=memory_build(triple_build)
        qstore,mq=memory_build(q_build)
        ans1=lambda a,b,r:(b,r) in adjacency.get(a,())
        ans2=lambda a,b,r:(a,b,r) in triple
        ans3=lambda a,b,r:qstore.has(a,b,r)
        sampled_hits=[sum(bool(f(*x)) for x in queries) for f in (ans1,ans2,ans3)]
        assert len(set(sampled_hits))==1
        row={'nodes':n,'relations':m,'queries':len(queries),'correct_hits':sampled_hits[0],
             'adjacency_scan':{'peak_allocated_bytes':ma,**bench_check(ans1,queries)},
             'ordinary_triple_hash':{'peak_allocated_bytes':mt,**bench_check(ans2,queries)},
             'qstring_index_and_payload':{'peak_allocated_bytes':mq,**bench_check(ans3,queries)}}
        results.append(row)
    report={'environment':{'python':sys.version.split()[0],'implementation':platform.python_implementation(),
         'machine':platform.machine(),'os':platform.system()},
         'warning':'Peak tracemalloc build allocations per independent structure; Python-specific, includes unequal payload and index semantics; hash-table performance expected O(1) average, not guaranteed. No evidence of general QIA speedup.',
         'rows':results}
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
