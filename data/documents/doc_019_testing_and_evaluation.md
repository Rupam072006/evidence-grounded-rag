# Testing Pyramid, Quality Assurance, and Evaluation Standards

The AegisCore Quality Assurance framework enforces a multi-tier testing pyramid to guarantee deterministic behavior, regression resistance, and specification compliance.

Testing Layers:
1. Unit Tests: Validate isolated components including Unicode text cleaning, chunk boundary splitting, stable chunk ID generation, vector dot products, and input validation bounds.
2. Integration Tests: Verify cross-module workflows including index creation, serialization to disk, index reload, candidate retrieval matching, and context payload construction.
3. Functional Tests: Validate complete end-to-end question answering, citation attribution, and refusal responses on answerable and unanswerable queries.
4. Boundary & Security Tests: Exercise edge conditions including empty queries, 500+ character inputs, injection payloads, corrupt indices, and missing corpus files.
5. Benchmark Evaluation: Executes a standardized test battery of at least 20 evaluation queries to quantitatively measure retrieval precision, grounded answer accuracy, and latency.