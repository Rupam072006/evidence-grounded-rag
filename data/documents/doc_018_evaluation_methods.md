# RAG Evaluation Methodologies, Groundedness, and Observability

## Metadata
- **document_id:** DOC-018
- **title:** RAG Evaluation Methodologies, Groundedness, and Observability
- **source:** data/documents/evaluation_methods.md
- **source_type:** technical_guide
- **version:** 1.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-01-15T10:30:00Z
- **topic:** RAG Evaluation and Observability

## 1. Overview
Evaluating Retrieval-Augmented Generation systems requires measuring performance across both retrieval and generation stages. Evaluating generation without assessing retrieval produces misleading diagnostics because generative models cannot produce grounded answers from poor context. Conversely, high retrieval recall is wasted if generative synthesis hallucinates unsupported claims. In AegisCore, comprehensive evaluation encompasses retrieval relevance, answer groundedness, detection of unsupported questions, and structured JSON logging for continuous operational observability.

## 2. Main Concepts

### Retrieval Evaluation Metrics
- **Recall@k:** The percentage of gold-standard relevant documents captured within the top-$k$ retrieved candidates.
- **Mean Reciprocal Rank (MRR):** Measures how early the first relevant passage appears: $\text{MRR} = \frac{1}{|Q|} \sum \frac{1}{\text{rank}_i}$.
- **Normalized Discounted Cumulative Gain (NDCG@k):** Evaluates multi-grade relevance ranking, heavily penalizing relevant passages placed lower in candidate lists.

### Generation Evaluation Metrics
- **Answer Groundedness (Faithfulness):** The fraction of claims in generated text directly verifiable against retrieved source passages.
- **Answer Relevance:** The degree to which the generated answer addresses the user's specific query without digression.
- **Citation Precision:** The accuracy with which claims link to valid, supporting document chunks (e.g., verifying `[DOC-001:DOC-001-C001]` actually contains the asserted fact).

### Testing Unsupported and Out-of-Domain Questions
A critical test of RAG robustness is identifying questions that the knowledge base cannot answer. Systems that attempt to answer out-of-domain questions inevitably hallucinate. AegisCore explicitly benchmarks unsupported queries:
- Queries with max retrieval similarity below 0.25 (or lacking query term coverage) must trigger canonical refusals.
- Refusal benchmark suites ensure that unanswerable queries yield status `INSUFFICIENT_EVIDENCE` with 100% precision.

### Structured JSON Logging and Observability
To monitor production RAG performance and debug anomalies, AegisCore emits structured JSON log events for every query transaction:
- `query_id`: Unique trace identifier.
- `timestamp`: ISO-8601 UTC execution timestamp.
- `retrieved_chunks`: List of retrieved chunk IDs, document IDs, and similarity scores.
- `latency_ms`: Execution duration across retrieval and generation stages.
- `status`: Execution outcome (`ANSWERED`, `INSUFFICIENT_EVIDENCE`, `CONFLICT_DETECTED`, `INVALID_INPUT`).

## 3. Explanation of Important Terms
- **Faithfulness:** Absence of hallucinations relative to the retrieved context.
- **Canonical Refusal:** Standardized deterministic error or refusal message returned when evidence is insufficient.
- **Synthetic Test Benchmarks:** Curated sets of questions paired with expected sources, statuses, and summaries used for regression testing.

## 4. Practical Example
The following Python script illustrates logging structured evaluation events in JSON format:

```python
import json
import time

def log_rag_evaluation_event(query_id: str, query: str, retrieved_chunks: list, status: str, latency: float):
    event = {
        "query_id": query_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "query": query,
        "retrieved_chunk_count": len(retrieved_chunks),
        "top_similarity": retrieved_chunks[0]["score"] if retrieved_chunks else 0.0,
        "status": status,
        "latency_ms": round(latency * 1000, 2)
    }
    print(json.dumps(event, indent=2))

log_rag_evaluation_event(
    query_id="eval-001",
    query="What is the uptime SLA?",
    retrieved_chunks=[{"chunk_id": "DOC-001-C001", "score": 0.88}],
    status="ANSWERED",
    latency=0.045
)
```

## 5. Limitations or Common Mistakes
- **Evaluating Only the Final Answer:** If the final answer is wrong, debugging is impossible without inspecting retrieval recall and chunk scores.
- **Ignoring Refusal Calibration:** High accuracy on answerable benchmarks is dangerous if the system hallucinates wildly on unanswerable user questions.
- **Unstructured Plaintext Logs:** Plaintext log streams prevent automated metric aggregation, latency tracing, and alerting.

## 6. Source References
- Es, S., et al. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation: https://arxiv.org/abs/2309.15217
- Saad-Falcon, J., et al. (2023). ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems: https://arxiv.org/abs/2311.09476
- OpenTelemetry Documentation: Structured Logging and Traces: https://opentelemetry.io/docs/concepts/signals/logs/

