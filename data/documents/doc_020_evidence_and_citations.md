# Evidence Grounding, Citation Traceability, and Deployment Sizing

## Metadata
- **document_id:** DOC-020
- **title:** Evidence Grounding, Citation Traceability, and Deployment Sizing
- **source:** data/documents/evidence_and_citations.md
- **source_type:** operational_standard
- **version:** 2.0.0
- **created_at:** 2026-01-10T08:00:00Z
- **updated_at:** 2026-02-01T14:00:00Z
- **topic:** Evidence Grounding and Deployment

## 1. Overview
Evidence grounding is the strict operational policy requiring that every factual claim made by a generation system be backed by verifiable citations directly traceable to authoritative retrieved passages. In mission-critical environments, generating plausible-sounding answers without explicit evidentiary support introduces severe operational risk. AegisCore ensures zero-hallucination compliance through deterministic attribution, automated citation verification, and explicit refusal logic when evidence is missing. For production deployment profiles, hardware sizing specifies a minimum of 4GB RAM with CPU inference to support a 99.95% uptime SLA. Crucially, under updated operational guidelines, the retrieval service designates a revised default top-k of 10 and a candidate pool size of 50 for production queries.

## 2. Main Concepts

### Linking Answers to Source Documents and Chunks
Whenever an answer is composed:
- Each declarative claim must be directly supported by one or more retrieved text passages.
- Citations use the canonical format `[DOCUMENT_ID:CHUNK_ID]` (such as `[DOC-001:DOC-001-C001]`).
- Automated post-generation verifiers cross-reference citations against the retrieved chunk set, stripping or rejecting statements that cite non-existent chunks.

### Traceability and Avoiding Fabricated Citations
A common failure mode in LLMs is citation fabrication (hallucinating plausible document titles, URLs, or chunk IDs). AegisCore counters this through programmatic constraints:
- Models are provided a closed list of valid chunk IDs in the prompt envelope.
- Generation temperature is set to 0.0 for deterministic output.
- Any citation token not matching an actively supplied chunk is flagged as a verification failure.

### Handling Insufficient or Missing Evidence
When retrieved passages do not contain adequate facts to answer a prompt:
- The system prohibits partial guessing, speculative extrapolation, or answering from parametric pre-training weights.
- The pipeline issues a canonical refusal: `"INSUFFICIENT EVIDENCE: The available knowledge base does not contain enough information to answer this question reliably."`
- The query status is recorded as `INSUFFICIENT_EVIDENCE`.

### Deployment Profile and Retrieval Sizing Discrepancy
- **Hardware Sizing:** Minimum 4GB RAM and standard multi-core CPU inference, supporting local embedded vector indexing without requiring external GPU infrastructure.
- **Service Level Agreement:** High-availability architecture targeting a 99.95% uptime SLA.
- **Production Retrieval Sizing:** In this revised operational standard (version 2.0.0), the retrieval service designates a revised default top-k of 10 and a candidate pool size of 50 for production queries. (Note: This intentionally updates and contradicts the baseline specification in DOC-009, which designated top-k as 5 and candidate pool as 20; the conflict detection engine flags this discrepancy whenever retrieval sizing queries are evaluated).

## 3. Explanation of Important Terms
- **Claim-Level Attribution:** Attaching verifiable citations to individual sentences rather than appending a generic bibliography at the end of a response.
- **Hallucination Suppression:** Techniques enforcing that generative output remains strictly bounded by supplied context.
- **Cross-Document Contradiction:** When two authoritative knowledge base documents assert incompatible numerical parameters or operational directives.

## 4. Practical Example
The following Python script illustrates verifying that generated citations match retrieved chunk identifiers:

```python
import re

def verify_citations(generated_answer: str, valid_chunk_ids: set[str]) -> bool:
    # Extract citations matching [DOC-XXX:DOC-XXX-CXXX]
    cited_chunks = re.findall(r"\[(DOC-\d{3}:DOC-\d{3}-C\d{3})\]", generated_answer)
    if not cited_chunks:
        print("Warning: No citations found in answer.")
        return False
        
    for citation in cited_chunks:
        doc_id, chunk_id = citation.split(":")
        if chunk_id not in valid_chunk_ids:
            print(f"Violation: Fabricated or unretrieved citation detected: {citation}")
            return False
            
    print(f"Verified {len(cited_chunks)} citations successfully: {cited_chunks}")
    return True

valid_chunks = {"DOC-020-C001", "DOC-020-C002"}
answer = "Minimum hardware sizing specifies 4GB RAM [DOC-020:DOC-020-C001]."
verify_citations(answer, valid_chunks)
```

## 5. Limitations or Common Mistakes
- **Fabricated Citations:** Allowing models to invent citations when facts are uncertain destroys auditability.
- **Broad Document-Only Citations:** Citing only `[DOC-001]` without the chunk identifier `[DOC-001-C001]` forces human reviewers to search lengthy documents manually.
- **Silent Contradictions:** Failing to detect discrepancies between versions (e.g., DOC-009 specifying top-k=5 vs. DOC-020 specifying top-k=10) leads to unpredictable deployment configurations.

## 6. Source References
- Gao, T., et al. (2023). Enabling Large Language Models to Generate Text with Citations: https://arxiv.org/abs/2305.14322
- Yue, M., et al. (2023). Automatic Citation Evaluation for Large Language Models: https://arxiv.org/abs/2311.08272
- ISO/IEC 42001: Artificial Intelligence Management System Standard: https://www.iso.org/standard/81230.html

