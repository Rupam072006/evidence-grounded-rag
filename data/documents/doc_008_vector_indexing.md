# Vector Indexing, Storage Layout, and Index Persistence

AegisCore maintains a persistent, file-backed vector index located in data/index/. The indexing subsystem is engineered for atomic persistence, rapid deserialization, and complete state verification.

The storage architecture consists of two tightly coupled components:
1. Vector Matrix (vectors.npy): A dense NumPy binary array storing the complete matrix of unit-normalized chunk embeddings with shape (N, D), where N is the total chunk count and D is the vector dimensionality.
2. Knowledge Index Metadata (knowledge_index.json): A structured JSON record containing the index manifest, creation timestamp, embedding provider details, chunk lookup tables, document-to-chunk index mappings, and SHA-256 fingerprint hashes.

During startup, the index loader verifies that the hash of the indexed corpus matches the current documents manifest. If index corruption or version drift is detected, the loader raises an IndexCorruptionError and prompts an automatic index rebuild.