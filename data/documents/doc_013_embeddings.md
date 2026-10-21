# Dense Text Embeddings, Semantic Representation, and Citation Rules

## Metadata
- **document_id:** DOC-013
- **title:** Dense Text Embeddings, Semantic Representation, and Citation Rules
- **source:** data/documents/embeddings.md
- **source_type:** technical_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-01-15T10:30:00Z
- **topic:** Embeddings and Semantic Representation

## 1. Overview
Dense text embeddings map textual units (sentences, passages, or queries) into dense continuous vector spaces $\mathbb{R}^d$ where geometric proximity corresponds to conceptual and semantic similarity. Unlike sparse lexical representations that rely on exact keyword matches, embeddings capture synonyms, contextual intent, and polysemous meanings. In the AegisCore RAG system, embeddings power vector retrieval and semantic indexing. Furthermore, every retrieved passage maintains strict provenance: generated claims must cite their exact source using the standardized syntax `[DOCUMENT_ID:CHUNK_ID]`.

## 2. Main Concepts

### What Embeddings Represent
An embedding model encodes arbitrary text sequences into fixed-dimensional numerical vectors (typically 384, 512, 768, or 1536 dimensions). During training (often using contrastive objectives like InfoNCE or cosine margin losses), the encoder aligns embeddings such that semantically related phrases map to nearby points in vector space, while unrelated phrases are repelled.

### Semantic Search Mechanisms
Traditional keyword search (e.g., BM25 or TF-IDF) fails when queries use terms different from indexed documents (the vocabulary mismatch problem). Dense embeddings overcome this limitation:
- Query text is projected into vector $\mathbf{q} \in \mathbb{R}^d$.
- Document chunks are pre-embedded and indexed as vectors $\mathbf{d}_i \in \mathbb{R}^d$.
- Semantic relevance is computed using geometric similarity measures (such as cosine similarity or inner product).

### Similarity Measures and Properties
1. **Cosine Similarity:**
   $$\cos(\theta) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|_2 \|\mathbf{d}\|_2}$$
2. **Inner Product Equivalence:**
   When all document and query vectors are normalized to unit L2 length ($\|\mathbf{v}\|_2 = 1.0$), cosine similarity reduces to simple dot product: $\cos(\theta) = \mathbf{q} \cdot \mathbf{d}$, which accelerates matrix multiplication dramatically.
3. **Euclidean (L2) Distance:**
   Measures straight-line distance in Euclidean space: $\|\mathbf{q} - \mathbf{d}\|_2 = \sqrt{2 - 2(\mathbf{q} \cdot \mathbf{d})}$ for unit-normalized vectors.

## 3. Explanation of Important Terms
- **Dense Vector:** A vector where almost all elements are non-zero floating-point values representing distributed features.
- **Contrastive Learning:** A self-supervised training paradigm pulling positive pairs closer and pushing negative pairs apart.
- **Citation Syntax:** In AegisCore, claim attribution requires the exact format `[DOCUMENT_ID:CHUNK_ID]`. This syntax allows automated verifiers and human auditors to trace assertions directly back to specific document chunks.

## 4. Practical Example
The following Python script illustrates generating unit-normalized embeddings and computing cosine similarity via dot product using NumPy:

```python
import numpy as np

# Simulate two embedding vectors
vec_query = np.array([0.4, 0.7, 0.2, 0.1, 0.5])
vec_doc = np.array([0.38, 0.72, 0.19, 0.08, 0.53])

# Normalize to unit length (L2 norm = 1.0)
norm_query = vec_query / np.linalg.norm(vec_query)
norm_doc = vec_doc / np.linalg.norm(vec_doc)

# Compute cosine similarity via dot product
similarity = np.dot(norm_query, norm_doc)
print(f"Cosine Similarity (Dot Product): {similarity:.4f}")
```

## 5. Limitations or Common Mistakes
- **Negation and Polarity Blindness:** Dense embeddings can sometimes struggle with fine-grained logical negation (e.g., "features that are supported" vs. "features that are not supported" can produce high cosine similarity).
- **Domain Mismatch:** Embeddings trained on general web text often underperform on specialized legal, biomedical, or proprietary software architectures without fine-tuning.
- **Unverified Citations:** Emitting conversational answers without structured citations like `[DOCUMENT_ID:CHUNK_ID]` violates auditability requirements.

## 6. Source References
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks: https://arxiv.org/abs/1908.10084
- OpenAI Embeddings Guide: https://platform.openai.com/docs/guides/embeddings
- Karpukhin, V., et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering (DPR): https://arxiv.org/abs/2004.04906

