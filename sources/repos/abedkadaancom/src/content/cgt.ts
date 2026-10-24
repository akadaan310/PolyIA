// Table of contents of the published Computational Grammar Theory book (Abed Kadaan,
// working edition 0.1), extracted from github.com/akadaan310/computationalgrammartheory
// book/content at commit bfe32fc. The book itself is served unmodified at /cgt/.
export const CGT = {
  "title": "Computational Grammar Theory",
  "subtitle": "Structure, Operation, and the Cost of Resolution",
  "author": "Abed Kadaan",
  "role": "Computational Substrate Scientist and Principal Researcher",
  "edition": "Working edition 0.1, October 2026",
  "status": "A research manuscript in progress. Not peer reviewed; proofs marked “proved here” are self-checked and await independent review.",
  "description": "A rigorous, interactive book on the formal grammars through which computational structures expose, constrain, compose and resolve their operations — and on exactly when such grammars change what computation costs.",
  "parts": [
    {
      "id": "I",
      "title": "What Is a Computational Structure?",
      "chapters": [
        {
          "slug": "01-structures",
          "title": "Structures, Representations, and Operations",
          "description": "Elements, relations, state, operations and machine models — and the three questions this book never lets collapse into one."
        },
        {
          "slug": "02-arrays",
          "title": "Arrays: Addresses You Can Compute",
          "description": "The array as the first and purest example of a grammar whose words are arithmetic — and what that costs when the array must grow, shift or become multidimensional."
        },
        {
          "slug": "03-sequences",
          "title": "Lists, Stacks, Queues, and Deques",
          "description": "Pointer-based sequences, and the first structure whose language of defined operation sequences is not regular."
        },
        {
          "slug": "04-associative",
          "title": "Hash Tables, Sets, Maps, and Tries",
          "description": "When names are not dense numbers — hashing computes an address anyway, at the price of collisions; tries turn keys into words read by an automaton."
        },
        {
          "slug": "05-trees",
          "title": "Trees, Heaps, Search Trees, and Forests",
          "description": "Tree addresses as words, the heap numeration and exactly when it gives constant-time navigation, search trees, and forests compressed by sharing."
        },
        {
          "slug": "06-graphs",
          "title": "Graphs and Paths",
          "description": "Graph representations, walks versus simple paths, and the relational semantics that makes \"a path is an edge followed by a path\" a theorem rather than a slogan."
        }
      ]
    },
    {
      "id": "II",
      "title": "Grammar as a Computational Object",
      "chapters": [
        {
          "slug": "07-operational-grammars",
          "title": "Operational Grammars",
          "description": "The formal object of Computational Grammar Theory — moves, relational semantics, admissibility languages, adequate representations, cost profiles — and the five mechanisms through which grammar can affect cost."
        },
        {
          "slug": "08-admissibility",
          "title": "Admissibility Languages and the Product Construction",
          "description": "How an admissibility language is compiled into an automaton, how a structure is searched under it, and exactly how much a constraint can help or hurt."
        }
      ]
    },
    {
      "id": "III",
      "title": "Classical Algorithms Reconstructed",
      "chapters": [
        {
          "slug": "09-search-sort",
          "title": "Searching and Sorting Reconstructed",
          "description": "Linear and binary search, four comparison sorts and counting sort — with invariants, counted costs, the comparison lower bound, and the one way around it."
        },
        {
          "slug": "10-graph-algorithms",
          "title": "Graph Algorithms Reconstructed",
          "description": "Traversal, ordering, components, shortest paths, spanning trees and closure — and the theorem that evaluating a path grammar is computing a closure, with cost depending on the grammar's shape."
        },
        {
          "slug": "11-ranges-dp-strings",
          "title": "Range Queries, Dynamic Programming, and Strings",
          "description": "Fenwick and segment trees as arithmetic addressing, sparse tables as precomputation, dynamic programming as shared derivations, and string matching as automata."
        }
      ]
    },
    {
      "id": "IV",
      "title": "Cost, Information, and the Limits of Grammar",
      "chapters": [
        {
          "slug": "12-cost-information",
          "title": "Cost Profiles, Preprocessing, and Information",
          "description": "When does precomputing pay? What is the least information a \"grammar of all answers\" must contain? And what happens when the structure changes?"
        },
        {
          "slug": "13-compilation",
          "title": "Compiling Operations: When Grammar Becomes Arithmetic",
          "description": "A move word of any length can be compiled into a constant-size operation on some structures and provably not on others. This chapter finds the line."
        },
        {
          "slug": "14-complexity-limits",
          "title": "The Limits: Advice, Restriction, and P versus NP",
          "description": "What a grammar can and cannot do to complexity classes — stated as precise challenges with their proof obligations, and answered."
        }
      ]
    },
    {
      "id": "V",
      "title": "PageRank, Search, and Information Retrieval",
      "chapters": [
        {
          "slug": "15-pagerank",
          "title": "PageRank from First Principles",
          "description": "The random surfer, stochastic matrices, dangling pages, damping, existence and uniqueness of the ranking, power iteration with certified error, solvers, sparse representations, updates and personalization."
        },
        {
          "slug": "16-pagerank-grammar",
          "title": "PageRank Through the Lens of Grammar",
          "description": "The random surfer as a probabilistic operational grammar, rankings constrained by admissibility languages, block structure as a structural grammar — and an honest list of what the grammatical view does not improve."
        }
      ]
    },
    {
      "id": "VI",
      "title": "Modern Computational Systems",
      "chapters": [
        {
          "slug": "17-ai-systems",
          "title": "Computation Graphs, Retrieval, and Agent Systems",
          "description": "Where computational grammars apply to modern AI systems — computation graphs, attention masks, retrieval pipelines, vector search and agent workflows — and where they do not."
        }
      ]
    },
    {
      "id": "VII",
      "title": "The Laboratory, the SDK, and Grammar as a Service",
      "chapters": [
        {
          "slug": "18-sdk",
          "title": "The CGT SDK",
          "description": "A tutorial for the executable companion to this book — structures, grammars, the three layers, cost models, comparisons, experiment records and extension points."
        },
        {
          "slug": "19-gaas",
          "title": "Grammar as a Service",
          "description": "A contract for requesting operations on versioned grammars, with layered rejection, quotas, determinism, provenance and cache validity — and an argument about what should run where."
        }
      ]
    },
    {
      "id": "VIII",
      "title": "Conclusions",
      "chapters": [
        {
          "slug": "20-conclusions",
          "title": "What Computational Grammar Theory Has Established",
          "description": "The confirmed contributions, the negative results, the open questions and the research agenda — without inflating any of them."
        }
      ]
    },
    {
      "id": "A",
      "title": "Appendices",
      "chapters": [
        {
          "slug": "a-notation",
          "title": "Notation and Conventions",
          "description": "The symbols, cost conventions and evidence labels used throughout the book."
        },
        {
          "slug": "b-reproducibility",
          "title": "Reproducing This Book",
          "description": "How to rerun every experiment, test, example and build step, and what reproducibility means for each."
        }
      ]
    }
  ]
} as const;
