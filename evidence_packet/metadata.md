# Evidence Packet Metadata & Execution Inventory

## 1. Environment & Software Versions
- **Host OS:** Windows (PowerShell 5.1/7.x)
- **Architecture:** x86_64
- **Python Version:** 3.13.1 (64-bit)
- **Pytest Version:** 8.3.4
- **Key Python Packages:**
  - `pydantic`: 2.10.6
  - `numpy`: 2.2.2
  - `scikit-learn`: 1.9.1
  - `click`: 8.5.0
  - `rich`: 15.0.0
  - `pyyaml`: 6.0.3
  - `python-dotenv`: 1.0.1
  - `sentence-transformers`: 6.1.0
  - `google-genai`: 1.3.0

## 2. Corpus Specification
- **Corpus Location:** `data/documents/`
- **Total Ingested Documents:** Exactly 20
- **Document ID Range:** `DOC-001` through `DOC-020`
- **Total Extracted Chunks:** 70
- **Manifest Path:** `data/manifest.json`
- **Manifest Version:** 1.0
- **Corpus Topic:** AegisCore Distributed Intelligence Platform

## 3. Persistent Index Fingerprint
- **Index Directory:** `data/index/`
- **Vector Storage File:** `vectors.npy` (Shape: 70 x 512, float32)
- **Index Metadata File:** `knowledge_index.json`
- **Embedding Model Pickle:** `embedding_model.pkl`
- **Similarity Metric:** Cosine similarity via L2-normalized dot product
- **Vector Dimension:** 512

## 4. Evaluation Benchmark Inventory
- **Benchmark Dataset:** `evaluation/questions.jsonl`
- **Total Questions:** 22
- **Latest Evaluation Run File:** `evaluation/results/evaluation_run_20261017_074411.json`
- **Measured Metrics:**
  - Retrieval Success Rate: 100.0% (18/18 applicable questions)
  - Status Accuracy: 100.0% (22/22 questions)
  - Failure Detection Rate: 100.0% (6/6 negative cases)
  - Citation Validity Rate: 100.0% (Zero invalid citations)
  - Average Latency: 1.8 ms

## 5. Evidence Artifact Inventory
- `evidence_packet/api_samples/`:
  - `q01_answerable.json`: Factual question on character encoding.
  - `q02_conflict.json`: Contradiction query on top-k sizing.
  - `q03_unknown.json`: Unanswerable cookie recipe query.
  - `q04_boundary.json`: Whitespace-only query.
  - `q05_injection.json`: Adversarial system prompt override query.
- `evidence_packet/runtime_logs/`:
  - `rag_system.log`: Execution traces with secret-free scrubbing.
