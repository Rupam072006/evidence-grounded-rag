import os
import json
from datetime import datetime, timezone

DOCUMENTS = [
    {
        "document_id": "DOC-001",
        "title": "AegisCore System Overview and Operational Mission",
        "topic": "System Overview",
        "version": "1.0.0",
        "created_at": "2026-01-10T08:00:00Z",
        "updated_at": "2026-01-15T10:30:00Z",
        "source": "docs/system_overview.md",
        "source_type": "technical_specification",
        "content": """# AegisCore System Overview and Operational Mission

The AegisCore Distributed Intelligence Platform is a mission-critical, evidence-grounded retrieval-augmented generation system designed for enterprise engineering environments. The primary mission of AegisCore is to provide engineers, compliance auditors, and automated agents with deterministic, verified technical answers derived solely from authoritative internal documentation.

AegisCore enforces a zero-trust grounding paradigm. The system explicitly prohibits generating speculative, unverified, or hallucinations derived from external parametric memory. Every factual proposition delivered by the platform must be tied to verified document chunks through strict citation tracking.

Operationally, AegisCore targets a sustained 99.95% uptime SLA with an end-to-end query response latency target of under 200 milliseconds on standard CPU hardware. It handles structured documentation formats including Markdown, JSON specifications, and technical text files, serving as the central source of truth across engineering departments."""
    },
    {
        "document_id": "DOC-002",
        "title": "AegisCore Modular Architecture and Component Topology",
        "topic": "Architecture",
        "version": "1.0.0",
        "created_at": "2026-01-10T08:30:00Z",
        "updated_at": "2026-01-16T09:15:00Z",
        "source": "docs/architecture.md",
        "source_type": "architecture_design",
        "content": """# AegisCore Modular Architecture and Component Topology

The AegisCore architecture follows a decoupled, pipeline-oriented topology composed of five primary stages: Ingestion & Validation, Text Processing & Chunking, Vector Embedding & Indexing, Semantic Retrieval & Evidence Assessment, and Grounded Generation & Citation Verification.

The pipeline maintains clear process isolation between data ingestion and real-time query serving. The Ingestion Engine processes raw corpus files, validates metadata integrity against the central manifest, and emits sanitized chunks into the persistent Indexing Store. The Query Engine receives incoming requests, verifies syntactic and semantic constraints, retrieves top candidate passages, and applies evidence sufficiency thresholds.

State management is strictly partitioned. Index artifacts are serialized as deterministic binary vectors and metadata indices on disk. When external language model providers are invoked, communication occurs via secure, rate-limited TLS channels with complete payload auditing and secret-free logging."""
    },
    {
        "document_id": "DOC-003",
        "title": "Data Ingestion Protocols and Manifest Validation",
        "topic": "Data Ingestion",
        "version": "1.0.0",
        "created_at": "2026-01-11T09:00:00Z",
        "updated_at": "2026-01-17T11:00:00Z",
        "source": "docs/ingestion.md",
        "source_type": "engineering_guide",
        "content": """# Data Ingestion Protocols and Manifest Validation

The AegisCore Ingestion Subsystem governs the entry of technical documents into the knowledge base. Documents are ingested from the designated data repository using automated file scanning and manifest verification protocols.

Every document file must correspond to an entry in the machine-readable manifest (manifest.json). During the ingestion cycle, the subsystem performs SHA-256 cryptographic hashing on each document to verify file provenance and detect unauthorized tampering or bitrot. The ingestion engine enforces strict metadata validation, verifying that required fields—including document_id, title, source, source_type, version, created_at, updated_at, and topic—are present and non-empty.

If a document exists in the filesystem without a corresponding manifest entry, or if manifest metadata fails schema validation, the ingestion process halts with an IngestionValidationError. Ingested documents are assigned immutable internal timestamps and registered in the corpus registry."""
    },
    {
        "document_id": "DOC-004",
        "title": "Document Parsing and Structural Extraction",
        "topic": "Document Processing",
        "version": "1.0.0",
        "created_at": "2026-01-11T10:00:00Z",
        "updated_at": "2026-01-18T14:20:00Z",
        "source": "docs/document_processing.md",
        "source_type": "technical_specification",
        "content": """# Document Parsing and Structural Extraction

Document parsing converts raw file formats into canonical textual representations suitable for chunking and vector encoding. AegisCore implements format-specific extractors for Markdown, Plaintext, and structured JSON files.

The parser extracts both structural hierarchy and textual content. For Markdown documents, section headers (H1, H2, H3), code blocks, and bulleted lists are parsed while preserving logical block boundaries. Structural metadata, including primary section titles and hierarchical breadcrumbs, is extracted and associated with the underlying text sections.

All incoming files are enforced to use UTF-8 character encoding. Files containing invalid byte sequences or unsupported binary markers are rejected immediately with a DocumentParsingError. The parsing module strips non-printable control characters while retaining standard paragraph separators (double newlines) to assist downstream chunking."""
    },
    {
        "document_id": "DOC-005",
        "title": "Text Cleaning, Sanitization, and PII Redaction",
        "topic": "Text Cleaning",
        "version": "1.0.0",
        "created_at": "2026-01-12T08:00:00Z",
        "updated_at": "2026-01-19T10:00:00Z",
        "source": "docs/text_cleaning.md",
        "source_type": "security_standard",
        "content": """# Text Cleaning, Sanitization, and PII Redaction

The Text Cleaning Pipeline prepares parsed document text for embedding generation by removing typographic noise, normalizing Unicode representations, and stripping potential injection vectors.

The cleaning process executes in four sequential stages:
1. Unicode Normalization: Converts all characters to NFKC (Compatibility Decomposition followed by Canonical Composition) to resolve disparate ligature and accent encodings.
2. Control Character Removal: Strips ASCII control codes 0 through 31, with the strict exceptions of horizontal tabs (ASCII 9), line feeds (ASCII 10), and carriage returns (ASCII 13).
3. Whitespace Consolidation: Replaces consecutive whitespace characters with a single space while standardizing multi-line paragraph breaks to double newlines.
4. Security Tag Stripping: Identifies and strips raw HTML tags, embedded Javascript script blocks, and XML directive tags to eliminate markup-based injection attempts.

Additionally, heuristic regex filters detect and mask sensitive identifiers such as API keys, private passwords, and personal email addresses with redacted placeholder tokens."""
    },
    {
        "document_id": "DOC-006",
        "title": "Chunking Strategies and Chunk Identity Specification",
        "topic": "Chunking",
        "version": "1.0.0",
        "created_at": "2026-01-12T09:30:00Z",
        "updated_at": "2026-01-20T11:45:00Z",
        "source": "docs/chunking.md",
        "source_type": "engineering_guide",
        "content": """# Chunking Strategies and Chunk Identity Specification

AegisCore implements a deterministic, boundary-aware paragraph sliding window chunking algorithm designed to optimize retrieval precision and contextual coherence.

The chunking algorithm operates with a target chunk size of 400 characters and a sliding overlap window of 60 characters. Unlike arbitrary character splitters, the AegisCore chunker respects natural text boundaries. It prefers splitting at double-newline paragraph breaks and sentence-ending punctuation marks (. ! ?). If a text segment is shorter than the minimum chunk length of 40 characters, it is merged into the adjacent chunk to prevent orphan fragments with low semantic density.

Every chunk is assigned a globally unique, deterministic Chunk ID using the format:
[DOCUMENT_ID]-C[SEQUENCE_NUMBER] (for example, DOC-006-C001, DOC-006-C002).
Each chunk object retains complete traceability metadata, including parent document_id, chunk_index, character_start, character_end, token_count, and content hash."""
    },
    {
        "document_id": "DOC-007",
        "title": "Embedding Generation and Vector Representations",
        "topic": "Embeddings",
        "version": "1.0.0",
        "created_at": "2026-01-13T08:15:00Z",
        "updated_at": "2026-01-21T13:00:00Z",
        "source": "docs/embeddings.md",
        "source_type": "technical_specification",
        "content": """# Embedding Generation and Vector Representations

The AegisCore Vector Engine transforms sanitized text chunks and query strings into high-dimensional semantic vector spaces. The platform provides a dual-provider embedding architecture supporting both hybrid sparse-dense representations and neural dense transformers.

In default reproducible environments, AegisCore employs an advanced Sublinear TF-IDF + Character/Word N-Gram hybrid vectorizer producing 512-dimensional L2-normalized representations. This model operates fully offline, requires zero external network calls, guarantees bitwise deterministic results across platforms, and eliminates GPU dependencies. For dense neural deployments, the system interfaces with sentence-transformers models such as all-MiniLM-L6-v2 yielding 384-dimensional dense vectors.

All generated embedding vectors are strictly normalized to unit length (L2 norm = 1.0). This mathematical normalization ensures that the cosine similarity between two vectors is computationally equivalent to their standard dot product, accelerating vector comparison during retrieval."""
    },
    {
        "document_id": "DOC-008",
        "title": "Vector Indexing, Storage Layout, and Index Persistence",
        "topic": "Vector Indexing",
        "version": "1.0.0",
        "created_at": "2026-01-13T10:00:00Z",
        "updated_at": "2026-01-22T09:30:00Z",
        "source": "docs/vector_indexing.md",
        "source_type": "technical_specification",
        "content": """# Vector Indexing, Storage Layout, and Index Persistence

AegisCore maintains a persistent, file-backed vector index located in data/index/. The indexing subsystem is engineered for atomic persistence, rapid deserialization, and complete state verification.

The storage architecture consists of two tightly coupled components:
1. Vector Matrix (vectors.npy): A dense NumPy binary array storing the complete matrix of unit-normalized chunk embeddings with shape (N, D), where N is the total chunk count and D is the vector dimensionality.
2. Knowledge Index Metadata (knowledge_index.json): A structured JSON record containing the index manifest, creation timestamp, embedding provider details, chunk lookup tables, document-to-chunk index mappings, and SHA-256 fingerprint hashes.

During startup, the index loader verifies that the hash of the indexed corpus matches the current documents manifest. If index corruption or version drift is detected, the loader raises an IndexCorruptionError and prompts an automatic index rebuild."""
    },
    {
        "document_id": "DOC-009",
        "title": "Retrieval Configuration, Filter Policies, and Candidate Limits",
        "topic": "Retrieval Configuration",
        "version": "1.0.0",
        "created_at": "2026-01-14T08:00:00Z",
        "updated_at": "2026-01-23T11:00:00Z",
        "source": "docs/retrieval_configuration.md",
        "source_type": "operational_guideline",
        "content": """# Retrieval Configuration, Filter Policies, and Candidate Limits

The AegisCore query retrieval service governs candidate passage selection and filtering policies. Production systems implement strict operational thresholds to balance recall with context window economy.

Under standard operational policy, the retrieval service executes with a default top-k parameter of 5 candidates and caps the candidate evaluation pool at a maximum of 20 raw chunks. Queries apply a relevance cosine similarity threshold of 0.18. Any passage scoring below this similarity threshold is pruned prior to ranking.

The retrieval pipeline supports metadata filtering allowing queries to constrain candidate pools by topic, document version, or source type. When tenant or topic constraints are active, non-matching documents are discarded during the pre-ranking phase before similarity calculation occurs."""
    },
    {
        "document_id": "DOC-010",
        "title": "Similarity Scoring Metrics and Candidate Ranking Heuristics",
        "topic": "Similarity Scoring",
        "version": "1.0.0",
        "created_at": "2026-01-14T11:30:00Z",
        "updated_at": "2026-01-24T14:15:00Z",
        "source": "docs/similarity_scoring.md",
        "source_type": "mathematical_specification",
        "content": """# Similarity Scoring Metrics and Candidate Ranking Heuristics

Candidate scoring in AegisCore quantifies the semantic relevance between the user query vector q and each stored chunk vector c_i. Because all vectors in the index are unit-normalized (||q|| = 1 and ||c_i|| = 1), the cosine similarity metric simplifies to the vector dot product:

Cosine_Similarity(q, c_i) = q · c_i = sum(q_j * c_ij) for j = 1 to D.

Raw cosine scores range from 0.0 (orthogonal) to 1.0 (identical direction). To improve ranking robustness, AegisCore applies a score calibration heuristic:
1. Exact keyword overlap boost: Passages containing exact case-insensitive matches for critical query terms receive an additive boost factor of up to 0.05.
2. Density penalty: Excessively short or repetitive chunks receive a small damping penalty.

Candidates are sorted in descending order of calibrated score. In cases where two chunks produce identical similarity scores, tie-breaking defaults to document version precedence followed by chunk sequence order."""
    },
    {
        "document_id": "DOC-011",
        "title": "Context Construction and Passage Formatting Guidelines",
        "topic": "Context Construction",
        "version": "1.0.0",
        "created_at": "2026-01-15T09:00:00Z",
        "updated_at": "2026-01-25T10:00:00Z",
        "source": "docs/context_construction.md",
        "source_type": "engineering_guide",
        "content": """# Context Construction and Passage Formatting Guidelines

Context construction is the critical bridge connecting retrieval to generative inference. The Context Builder synthesizes retrieved chunks into a structured, tamper-resistant prompt payload for the language model.

The builder processes the top-k retrieved passages according to strict formatting rules:
1. Context Budgeting: The total token budget allocated for context passages is capped at 1,500 tokens (approximately 6,000 characters). Passages exceeding the budget are excluded.
2. Passage Delimitation: Each passage is framed with explicit boundaries:
=== PASSAGE [CHUNK_ID] (SOURCE: [DOC_ID] | SCORE: [SCORE]) ===
[CHUNK_CONTENT]
=== END PASSAGE ===
3. Order of Presentation: Passages are presented in descending order of relevance score.
4. Redundancy Elimination: If two adjacent chunks from the same parent document exhibit significant textual overlap, the overlapping characters are deduplicated to conserve token budget."""
    },
    {
        "document_id": "DOC-012",
        "title": "Grounded Answer Generation Protocols and Prompt Templates",
        "topic": "Answer Generation",
        "version": "1.0.0",
        "created_at": "2026-01-15T11:00:00Z",
        "updated_at": "2026-01-26T12:00:00Z",
        "source": "docs/answer_generation.md",
        "source_type": "system_prompt_specification",
        "content": """# Grounded Answer Generation Protocols and Prompt Templates

AegisCore enforces strict grounded generation protocols to guarantee that every factual statement originates directly from retrieved context passages. The generator operates under a specialized system instruction template.

System Instruction:
"You are the AegisCore Grounded Knowledge Assistant. Your mandate is to answer technical questions using ONLY the facts explicitly stated in the provided context passages. Do not extrapolate, infer unstated assumptions, or utilize external world knowledge.
Every factual claim must cite its source using the exact format [DOC-ID:CHUNK-ID].
If the provided context does not contain sufficient factual evidence to answer the query directly, you must return:
INSUFFICIENT EVIDENCE: The available knowledge base does not contain enough information to answer this question reliably.
If conflicting evidence is present between sources, state CONFLICT DETECTED and outline the contradictory facts."

The generator operates at a temperature setting of 0.0 to eliminate stochastic hallucination and ensure deterministic reproducibility."""
    },
    {
        "document_id": "DOC-013",
        "title": "Citation Syntax, Claim Attribution, and Citation Validation",
        "topic": "Citation Rules",
        "version": "1.0.0",
        "created_at": "2026-01-16T08:30:00Z",
        "updated_at": "2026-01-27T14:00:00Z",
        "source": "docs/citation_rules.md",
        "source_type": "compliance_specification",
        "content": """# Citation Syntax, Claim Attribution, and Citation Validation

Citations in AegisCore represent verifiable audit trails linking generated statements to underlying knowledge sources. Every factual statement must carry explicit citations.

The required citation syntax is:
[DOCUMENT_ID:CHUNK_ID]
Example: "The system enforces a 400-character target chunk size [DOC-013:DOC-013-C001]."

AegisCore incorporates an automated post-generation Citation Validator. The validator executes the following checks:
1. Existence Verification: Verifies that every cited chunk ID actually existed in the retrieved context for that specific query. Invented or hallucinated chunk IDs trigger validation failure.
2. Source ID Consistency: Verifies that the document ID prefix matches the parent document of the cited chunk ID.
3. Content Overlap Verification: Confirms that key factual n-grams in the cited sentence share lexical overlap with the cited chunk body.

If any citation fails validation, the system flags the response with status CITATION_VALIDATION_FAILED and suppresses ungrounded claims."""
    },
    {
        "document_id": "DOC-014",
        "title": "Confidence Scoring and Uncertainty Handling Framework",
        "topic": "Confidence and Uncertainty",
        "version": "1.0.0",
        "created_at": "2026-01-16T10:00:00Z",
        "updated_at": "2026-01-28T09:30:00Z",
        "source": "docs/confidence_uncertainty.md",
        "source_type": "algorithmic_specification",
        "content": """# Confidence Scoring and Uncertainty Handling Framework

AegisCore features a transparent, multi-dimensional confidence assessment model. The system avoids deceptive pseudo-probabilistic percentages by distinguishing semantic similarity from factual sufficiency.

The Confidence Score (ranging from 0.0 to 1.0) is calculated as a composite metric:
Confidence = (0.50 * Top_Similarity_Score) + (0.30 * Mean_Top3_Similarity) + (0.20 * Query_Term_Coverage_Ratio).

Evidence Sufficiency Floor:
To prevent answering off-topic or out-of-domain queries, AegisCore establishes a strict evidence sufficiency floor of 0.25. If the highest similarity score among retrieved passages is below 0.25, the query is immediately categorized as unanswerable.
In such cases, the system returns status INSUFFICIENT_EVIDENCE with the canonical refusal:
"INSUFFICIENT EVIDENCE: The available knowledge base does not contain enough information to answer this question reliably."
No speculative generation is permitted when sufficiency criteria are unmet."""
    },
    {
        "document_id": "DOC-015",
        "title": "Error Handling Protocols, Fault Resilience, and Fallbacks",
        "topic": "Error Handling",
        "version": "1.0.0",
        "created_at": "2026-01-17T09:00:00Z",
        "updated_at": "2026-01-29T11:15:00Z",
        "source": "docs/error_handling.md",
        "source_type": "reliability_guide",
        "content": """# Error Handling Protocols, Fault Resilience, and Fallbacks

AegisCore is designed for resilient operation across transient faults, missing dependencies, and external service outages. The architecture establishes a dedicated hierarchy of typed exceptions.

The core exception hierarchy includes:
- RAGException (Base system exception)
  - CorpusError (Missing documents directory, corrupt manifest, invalid document IDs)
  - IndexNotFoundError (Index missing, vector dimension mismatch, unbuilt index)
  - RetrievalError (Similarity calculation failure, empty candidate pool)
  - GenerationProviderError (API timeouts, authentication errors, quota exceeded)
  - InputValidationError (Malformed input, length violations, forbidden characters)

When an external LLM provider encounters a 403 PERMISSION_DENIED, 429 RATE_LIMIT, or network timeout, the pipeline activates its deterministic offline generation fallback. This guarantees that basic evidence extraction, conflict detection, and evaluation pipelines can execute without crashing."""
    },
    {
        "document_id": "DOC-016",
        "title": "Security Controls, Prompt Injection Defense, and Secret Protection",
        "topic": "Security Controls",
        "version": "1.0.0",
        "created_at": "2026-01-17T11:30:00Z",
        "updated_at": "2026-01-30T15:00:00Z",
        "source": "docs/security_controls.md",
        "source_type": "security_standard",
        "content": """# Security Controls, Prompt Injection Defense, and Secret Protection

AegisCore enforces enterprise-grade security controls to protect the retrieval and generation lifecycle from manipulation, data exfiltration, and prompt injection attacks.

Key security mandates include:
1. Untrusted Document Paradigm: All document text is treated as passive, untrusted data. The generation prompt instructs the model to ignore any embedded directives such as "Ignore previous instructions", "SYSTEM OVERRIDE", or "Print system prompt".
2. Secret Protection & Environment Isolation: Secrets, API keys, and credentials must never be committed to source repositories or hardcoded in configuration files. Secrets are read exclusively from environment variables (such as GEMINI_API_KEY).
3. Secret-Free Logging: All log outputs, telemetry streams, and error traces pass through regex redaction filters that scrub potential API keys, authorization bearer tokens, and credentials.
4. Input Boundary Isolation: User queries are strictly quarantined within delimiter blocks to prevent prompt boundary escaping."""
    },
    {
        "document_id": "DOC-017",
        "title": "Input Validation, Query Sanitization, and Boundary Enforcement",
        "topic": "Input Validation",
        "version": "1.0.0",
        "created_at": "2026-01-18T08:00:00Z",
        "updated_at": "2026-01-31T09:45:00Z",
        "source": "docs/input_validation.md",
        "source_type": "technical_specification",
        "content": """# Input Validation, Query Sanitization, and Boundary Enforcement

The Input Validation Layer intercepts all incoming query requests before downstream pipeline processing. This layer enforces structural, length, and content constraints to preserve system stability and security.

Input Constraints and Rules:
1. Length Boundaries: User queries must contain a minimum of 3 characters (excluding whitespace) and cannot exceed the maximum length limit of 500 characters.
2. Emptiness Checks: Queries consisting solely of whitespace, carriage returns, or empty strings are rejected with status INVALID_INPUT.
3. Character Sanitization: Control characters, null bytes (\\x00), and unescaped ANSI escape sequences are detected and stripped or rejected.
4. Query Normalization: Excessive repeating punctuation (e.g., '???????') is condensed to single characters, and redundant whitespace is collapsed.

Requests violating these boundary conditions are rejected immediately with descriptive client error messages and status INVALID_INPUT, avoiding wasted vector retrieval computations."""
    },
    {
        "document_id": "DOC-018",
        "title": "Logging, Telemetry, and Observability Framework",
        "topic": "Logging and Observability",
        "version": "1.0.0",
        "created_at": "2026-01-18T10:30:00Z",
        "updated_at": "2026-02-01T13:30:00Z",
        "source": "docs/logging_observability.md",
        "source_type": "operational_guideline",
        "content": """# Logging, Telemetry, and Observability Framework

AegisCore provides a centralized, structured logging and observability framework designed for enterprise auditing and performance diagnostics.

The logging framework writes structured log entries to logs/rag_system.log while emitting human-readable formatted summaries to standard output. Every query execution is assigned a unique UUIDv4 correlation ID (query_id), which is threaded across ingestion, retrieval, ranking, and generation stages.

Recorded metrics include:
- Ingestion metrics: Total documents indexed, chunk count, vocabulary size, index build duration.
- Retrieval metrics: Candidate search latency in milliseconds, top similarity score, score margin between rank 1 and rank 2.
- Generation metrics: Provider mode (mock vs gemini), prompt token count, generation latency, citation validity flag.
All loggers integrate secret scrubbing filters to ensure zero credential leakage in audit logs."""
    },
    {
        "document_id": "DOC-019",
        "title": "Testing Pyramid, Quality Assurance, and Evaluation Standards",
        "topic": "Testing and Evaluation",
        "version": "1.0.0",
        "created_at": "2026-01-19T08:00:00Z",
        "updated_at": "2026-02-02T11:00:00Z",
        "source": "docs/testing_evaluation.md",
        "source_type": "qa_standards",
        "content": """# Testing Pyramid, Quality Assurance, and Evaluation Standards

The AegisCore Quality Assurance framework enforces a multi-tier testing pyramid to guarantee deterministic behavior, regression resistance, and specification compliance.

Testing Layers:
1. Unit Tests: Validate isolated components including Unicode text cleaning, chunk boundary splitting, stable chunk ID generation, vector dot products, and input validation bounds.
2. Integration Tests: Verify cross-module workflows including index creation, serialization to disk, index reload, candidate retrieval matching, and context payload construction.
3. Functional Tests: Validate complete end-to-end question answering, citation attribution, and refusal responses on answerable and unanswerable queries.
4. Boundary & Security Tests: Exercise edge conditions including empty queries, 500+ character inputs, injection payloads, corrupt indices, and missing corpus files.
5. Benchmark Evaluation: Executes a standardized test battery of at least 20 evaluation queries to quantitatively measure retrieval precision, grounded answer accuracy, and latency."""
    },
    {
        "document_id": "DOC-020",
        "title": "Deployment Profiles, Operational Limitations, and Resource Sizing",
        "topic": "Deployment and Limitations",
        "version": "1.0.0",
        "created_at": "2026-01-19T10:30:00Z",
        "updated_at": "2026-02-03T14:00:00Z",
        "source": "docs/deployment_limitations.md",
        "source_type": "operational_guideline",
        "content": """# Deployment Profiles, Operational Limitations, and Resource Sizing

This document outlines deployment configurations, hardware requirements, and operational constraints for AegisCore.

Production Deployment Profile (Conflicting Specification):
Under the revised enterprise deployment guidelines, the production retrieval service has standardized on a default top-k parameter of 10 candidates and a maximum candidate pool size of 50 to maximize recall across distributed multi-cluster nodes. (Note: This operational standard supersedes earlier baseline profiles that specified top-k of 5 and pool size of 20).

Hardware Sizing and Limitations:
- Memory: Minimum 4 GB RAM recommended for index caching; 8 GB recommended for dense neural models.
- Compute: CPU inference achieves average retrieval latencies of 45-85 milliseconds.
- Storage: 100 MB disk space sufficient for indices containing up to 10,000 document chunks.
- Limitations: Cross-language retrieval across non-English documents is currently experimental and requires specialized multi-lingual embeddings."""
    }
]

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_dir = os.path.join(base_dir, "data", "documents")
    os.makedirs(docs_dir, exist_ok=True)
    
    manifest_entries = []
    
    for doc in DOCUMENTS:
        doc_id = doc["document_id"]
        filename = f"{doc_id.lower().replace('-', '_')}_{doc['topic'].lower().replace(' ', '_')}.md"
        file_path = os.path.join(docs_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc["content"])
            
        manifest_entries.append({
            "document_id": doc["document_id"],
            "title": doc["title"],
            "source": f"data/documents/{filename}",
            "source_type": doc["source_type"],
            "version": doc["version"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"],
            "topic": doc["topic"]
        })
        
    manifest = {
        "manifest_version": "1.0",
        "total_documents": len(manifest_entries),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documents": manifest_entries
    }
    
    manifest_path = os.path.join(base_dir, "data", "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Successfully generated {len(manifest_entries)} documents in {docs_dir}")
    print(f"Manifest written to {manifest_path}")

if __name__ == "__main__":
    main()
