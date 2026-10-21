# Vector Search, Indexing Architectures, and Confidence Calibration

## Metadata
- **document_id:** DOC-014
- **title:** Vector Search, Indexing Architectures, and Confidence Calibration
- **source:** data/documents/vector_search.md
- **source_type:** technical_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-01-15T10:30:00Z
- **topic:** Vector Search and Retrieval

## 1. Overview
Vector search enables high-dimensional nearest-neighbor retrieval over millions of dense embeddings in milliseconds. Unlike inverted indices that map discrete vocabulary tokens to document IDs, vector indices organize geometric spaces to locate passages sharing conceptual proximity with input queries. In the AegisCore RAG pipeline, vector search retrieves candidate chunks using cosine similarity. To protect against hallucinations on out-of-domain or unsupported queries, the system enforces an evidence sufficiency floor: queries scoring below the 0.25 similarity floor (or 0.20 score floor with 28% query term coverage) trigger a canonical refusal with status INSUFFICIENT_EVIDENCE.

## 2. Main Concepts

### Vector Indexes and Nearest Neighbor Search
Given a query vector $\mathbf{q}$ and a collection of $N$ document vectors $\mathbf{D} = \{\mathbf{d}_1, \dots, \mathbf{d}_N\}$, nearest neighbor search seeks the top-$k$ vectors maximizing similarity $S(\mathbf{q}, \mathbf{d}_i)$.
- **Exact (Flat) k-NN Search:** Computes brute-force distances between query and every vector in the index. Offers 100% recall at $O(N \cdot d)$ complexity, ideal for corpus sizes up to tens of thousands of chunks (as utilized in AegisCore's NumPy matrix engine).
- **Approximate Nearest Neighbors (ANN):** Trades small recall margins for logarithmic $O(\log N)$ search speed in massive million-scale corpora:
  - **HNSW (Hierarchical Navigable Small World):** Multi-layer graph traversal with fast convergence.
  - **IVF (Inverted File Index):** Partitions vector space into Voronoi cells using $k$-means clustering, probing only nearby centroid clusters during query execution.
  - **Product Quantization (PQ):** Compresses vectors into compact byte codes to fit indices into RAM.

### Top-k Retrieval Workflow
1. The incoming query is validated, cleaned, and embedded into vector $\mathbf{q}$.
2. The index computes similarity scores against all indexed chunk vectors.
3. Candidate chunks are sorted descending by similarity.
4. Top-$k$ chunks passing relevance thresholds are returned for context construction.

### Confidence Calibration and Evidence Sufficiency Floors
Not every user question can be answered by an enterprise knowledge base. If top-retrieved passages have weak semantic connection to the prompt, feeding them into a generative LLM leads to fabricated answers. AegisCore implements a multi-stage confidence filter:
- If max similarity $< 0.25$ (or $< 0.20$ score floor without 28% lexical term coverage), the query is declared unsupported.
- The pipeline immediately halts generation and returns: `"INSUFFICIENT EVIDENCE: The available knowledge base does not contain enough information to answer this question reliably."`

## 3. Explanation of Important Terms
- **Recall@k:** The fraction of relevant documents present in the top-$k$ retrieved candidates.
- **Evidence Sufficiency Floor:** A deterministic score threshold separating reliable supporting evidence from arbitrary noise.
- **Out-of-Domain Detection:** Identifying queries referring to concepts entirely absent from indexed enterprise documents.

## 4. Practical Example
The following Python script illustrates exact top-$k$ search with threshold-based confidence filtering:

```python
import numpy as np

# Simulate indexed corpus of 5 unit-normalized vectors (dim=4)
doc_matrix = np.array([
    [0.5, 0.5, 0.5, 0.5],
    [0.1, 0.9, 0.1, 0.39],
    [0.0, 0.2, 0.8, 0.57],
    [0.7, 0.1, 0.1, 0.7],
    [0.2, 0.2, 0.2, 0.94]
])

# Query vector
query = np.array([0.52, 0.48, 0.49, 0.51])
query = query / np.linalg.norm(query)

# Compute dot products (cosine similarities)
scores = np.dot(doc_matrix, query)

# Rank candidates descending
ranked_indices = np.argsort(scores)[::-1]
top_score = scores[ranked_indices[0]]

# Apply evidence sufficiency floor of 0.25
SUFFICIENCY_FLOOR = 0.25
if top_score < SUFFICIENCY_FLOOR:
    print(f"Status: INSUFFICIENT_EVIDENCE (Top score: {top_score:.3f})")
else:
    print(f"Top Candidate Index: {ranked_indices[0]} (Score: {top_score:.3f})")
```

## 5. Limitations or Common Mistakes
- **Oversized Candidate Pools:** Fetching excessively large candidate pools without reranking degrades downstream prompt precision.
- **Ignoring Low-Confidence Retrieval:** Blindly generating answers regardless of retrieval similarity scores causes catastrophic hallucinations.
- **Neglecting Term Overlap:** Relying purely on dense similarity without validating query term presence risks false semantic matches on generic phrases.

## 6. Source References
- Malkov, Yu A., & Yashunin, D. A. (2018). Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. IEEE TPAMI: https://arxiv.org/abs/1603.09320
- Johnson, J., Douze, M., & Jégou, H. (2019). Billion-scale similarity search with GPUs (FAISS). IEEE Big Data: https://arxiv.org/abs/1702.08734
- Pinecone Learning Center: Vector Search Basics: https://www.pinecone.io/learn/vector-search/

