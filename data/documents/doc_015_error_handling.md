# Error Handling Protocols, Fault Resilience, and Fallbacks

AegisCore is designed for resilient operation across transient faults, missing dependencies, and external service outages. The architecture establishes a dedicated hierarchy of typed exceptions.

The core exception hierarchy includes:
- RAGException (Base system exception)
  - CorpusError (Missing documents directory, corrupt manifest, invalid document IDs)
  - IndexNotFoundError (Index missing, vector dimension mismatch, unbuilt index)
  - RetrievalError (Similarity calculation failure, empty candidate pool)
  - GenerationProviderError (API timeouts, authentication errors, quota exceeded)
  - InputValidationError (Malformed input, length violations, forbidden characters)

When an external LLM provider encounters a 403 PERMISSION_DENIED, 429 RATE_LIMIT, or network timeout, the pipeline activates its deterministic offline generation fallback. This guarantees that basic evidence extraction, conflict detection, and evaluation pipelines can execute without crashing.