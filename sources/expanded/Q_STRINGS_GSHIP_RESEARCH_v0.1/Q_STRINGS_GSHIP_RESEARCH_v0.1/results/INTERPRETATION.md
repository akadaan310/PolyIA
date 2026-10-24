# Q-String v0.1 measured Python microbenchmark

**Hardware/runtime:** CPython 3.13.5, Linux x86_64. Exact pair membership, 50% present and 50% absent, 3,600 queries per scale, 5 repetitions, median ns/query. Peak allocations are per separately built structure, not a cross-engine memory or total process RSS comparison.

| Relations | Adjacency scan | Ordinary tuple hash | Q-String indexed store | Q-String peak build alloc. |
|---:|---:|---:|---:|---:|
| 2,048 | 345.5 ns | 87.4 ns | 134.1 ns | 1.68 MiB |
| 8,192 | 623.1 ns | 95.7 ns | 146.7 ns | 5.83 MiB |
| 24,576 | 1267.4 ns | 121.2 ns | 210.6 ns | 17.82 MiB |

**Interpretation.** Q-String helps compared with the *unindexed* scan, but loses to a plain tuple-hash index on the same membership task. Indexing earns speed by paying construction/storage costs. Q-String provides versioned content identity, grammatical operator admission, forward/reverse reference indices and witnesses which the baseline does not store. These different capabilities make the memory comparison descriptive, not an equal-feature contest. No speedup over a conventional hash table is demonstrated. Exact numbers are microbenchmark samples, not a stable latency guarantee.

**Next required experiments:** persisted on-disk representation, cold/warm cache, 1M+ edges, p95/p99, mutations, proof/witness retrieval, multiway joins, DFA path queries, CSR, graph DB and strongly typed native implementation.
