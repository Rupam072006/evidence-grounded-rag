# Architecture Overview Report

**Project:** BHIV CMO Technical Execution Assignment v2 — Existing RAG System Architecture  
**Date:** 2026-11-11  

---

## 1. Architectural Philosophy & Design Principles

The existing system (**AegisCore**) implements a **Zero-Trust Evidence-Grounded Architecture**. Unlike conventional RAG systems that treat language models as generative synthesizers prone to parametric hallucination, this architecture enforces the following principles:

1. **Deterministic Attribution Syntax:** Every factual claim emitted must include a machine-verifiable citation token `[DOCUMENT_ID:CHUNK_ID]` referencing an exact retrieved passage.
2. **Mathematical Sufficiency Floors:** If semantic retrieval confidence fails to exceed configured similarity floors ($\ge 0.25$ for technical QA, $\ge 0.18$ for CMO proposals), generation is blocked immediately and a canonical refusal is emitted.
3. **Automated Conflict Interception:** Contradictory corporate policies or technical instructions are detected prior to response generation, surfacing tensions transparently rather than averaging contradictory facts.
4. **Mandatory Human Governance Gate:** For high-stakes CMO decisions (e.g. ad spend, creator contracts, growth initiatives), the automated pipeline terminates at state `AWAITING_APPROVAL`. The system cannot commit external funds or approve proposals autonomously.

---

## 2. Mermaid Architecture Diagrams

### 2.1 System Component Topology

```mermaid
flowchart TD
    subgraph ClientLayer["Interaction & Client Interfaces"]
        CLI["Click CLI Interface\n(evidence-rag)"]
        ScriptRunners["Operational Scripts\n(run_day3_scenarios.py, etc.)"]
        PySDK["Python SDK / Internal Consumers\n(RAGPipeline, DecisionWorkflow)"]
    end

    subgraph IngestionLayer["Ingestion & Indexing Engine"]
        ManifestValidator["IngestionEngine\n(Manifest & SHA-256 Validation)"]
        Sanitizer["TextCleaner\n(NFKC, PII & Tag Scrubbing)"]
        ChunkEngine["Chunker\n(Paragraph-Window, Overlap, Hashes)"]
        EmbedEngine["HybridTfidfEmbeddingEngine\n(512-dim / 256-dim Vectorizer)"]
        VecIndex["VectorIndex\n(vectors.npy, knowledge_index.json)"]
    end

    subgraph RetrievalLayer["Retrieval & Guardrail Engine"]
        RetrieverMod["Retriever\n(Cosine Similarity Search)"]
        DomainRouter["Domain Routing & Calibration\n(Keyword Boosts & Domain Multipliers)"]
        SufficiencyFloor["Evidence Sufficiency Guard\n(Floor Threshold: 0.25 / 0.18)"]
        ConflictDet["ConflictDetector\n(Pairwise & Keyword Contradiction)"]
    end

    subgraph GenerationLayer["Generation & Verification Engine"]
        ContextBuilderMod["ContextBuilder\n(1,500 Token Budget Cap)"]
        MockGen["DeterministicMockGenerator\n(Offline, Deterministic Extraction)"]
        CloudLLMs["Cloud LLM Providers\n(Gemini, Groq, Grok)"]
        CitationVal["CitationValidator\n(Provenance & Hallucination Check)"]
        ConfidenceMod["ConfidenceScorer\n(Continuous Uncertainty Rating)"]
    end

    subgraph WorkflowGovernance["CMO Decision Governance Gate"]
        DecisionWF["DecisionWorkflow Engine\n(Request Validation & Synthesis)"]
        ReportSynthesizer["RecommendationReport Synthesizer\n(Facts, Inferences, Assumptions, Unknowns)"]
        ApprovalGate{"Mandatory Human Approval Gate\n(AWAITING_APPROVAL)"}
        RecordStoreMod["RecordStore\n(Atomic File Store & Secret Scrubbing)"]
    end

    subgraph StorageLayer["Persistent Disk Storage"]
        DiskIndex["Persistent Index Directory\n(data/index/, data/marketing_index/)"]
        AuditLedger["Persistent Audit Ledger\n(data/workflow_records/records.json)"]
        CorpusDocs["Source Markdown Corpora\n(data/documents/, data/marketing_corpus/)"]
    end

    %% Wiring
    CLI --> PySDK
    ScriptRunners --> PySDK
    PySDK --> DecisionWF
    PySDK --> RAGPipelineMod["RAGPipeline"]

    CorpusDocs --> ManifestValidator
    ManifestValidator --> Sanitizer
    Sanitizer --> ChunkEngine
    ChunkEngine --> EmbedEngine
    EmbedEngine --> VecIndex
    VecIndex --> DiskIndex

    RAGPipelineMod --> RetrieverMod
    DiskIndex --> RetrieverMod
    RetrieverMod --> DomainRouter
    DomainRouter --> SufficiencyFloor
    SufficiencyFloor --> ConflictDet
    ConflictDet --> ContextBuilderMod
    ContextBuilderMod --> MockGen
    ContextBuilderMod --> CloudLLMs
    MockGen --> CitationVal
    CloudLLMs --> CitationVal
    CitationVal --> ConfidenceMod

    DecisionWF --> RetrieverMod
    DecisionWF --> ReportSynthesizer
    ReportSynthesizer --> ApprovalGate
    ApprovalGate -->|Human Sign-Off| RecordStoreMod
    RecordStoreMod --> AuditLedger
```

---

### 2.2 End-to-End Proposal Evaluation Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Submitter as Growth Lead / CMO Analyst
    participant CLI as CLI / Workflow API
    participant WF as DecisionWorkflow Engine
    participant Index as VectorIndex
    participant Ret as Retriever
    participant CD as ConflictDetector
    participant Synth as Recommendation Synthesizer
    participant Gate as Human Approval Gate
    actor Manager as CMO / Human Approver
    participant Ledger as RecordStore (records.json)

    Submitter->>CLI: Submit Proposal (title, budget, proposal_text)
    CLI->>WF: evaluate_proposal(WorkflowRequest)
    WF->>WF: validate_request() [Check title, text length, budget >= 0]
    WF->>Index: ensure_index() [Staleness & SHA-256 Check]
    WF->>Ret: retrieve(proposal_text)
    Ret->>Index: Cosine similarity search + Domain routing
    Index-->>Ret: Candidate Chunks
    Ret-->>WF: RetrievedChunk[]
    WF->>Ret: assess_evidence_sufficiency(RetrievedChunk[])
    alt Evidence Below Floor (< 0.18)
        WF->>Ledger: Save record (INSUFFICIENT_EVIDENCE)
        WF-->>CLI: Return refusal & missing evidence
    else Sufficient Evidence
        WF->>CD: detect_conflicts(proposal_text, chunks)
        alt Contradiction Detected
            CD-->>WF: ConflictEvidence
            WF->>Ledger: Save record (CONFLICT_DETECTED)
            WF-->>CLI: Surface conflicting policy guidelines
        else No Conflict
            WF->>Synth: synthesize_recommendation(request, chunks)
            Synth-->>WF: RecommendationReport + Citations
            WF->>Ledger: Save record (AWAITING_APPROVAL)
            WF-->>CLI: Display Recommendation & Risk Assessment
            Note over WF,Gate: Automated pipeline stops here.
            Manager->>CLI: workflow approve / reject (REQ-ID, reviewer, notes)
            CLI->>Gate: submit_approval(request_id, decision, reviewer, notes)
            Gate->>Ledger: record_decision() [Atomic write + secret scrub]
            Ledger-->>Gate: Updated WorkflowRecord
            Gate-->>CLI: Confirm APPROVED / REJECTED status
        end
    end
```

---

### 2.3 Human Governance Approval State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT : User Prepares Request
    DRAFT --> INVALID_REQUEST : Validation Failure (Length, Negative Budget)
    DRAFT --> VALIDATED : Field Constraints Satisfied
    VALIDATED --> INDEX_UNAVAILABLE : Index Missing or Corrupt
    VALIDATED --> INSUFFICIENT_EVIDENCE : Top Retrieval Score < Floor (0.18)
    VALIDATED --> CONFLICT_DETECTED : Policy Contradiction Intercepted
    VALIDATED --> AWAITING_APPROVAL : Evidence Sufficient & Conflict-Free
    
    AWAITING_APPROVAL --> APPROVED : Human Reviewer Signs Off (Legitimate Authority)
    AWAITING_APPROVAL --> REJECTED : Human Reviewer Rejects (Policy / Budget Constraint)
    
    APPROVED --> [*]
    REJECTED --> [*]
    INVALID_REQUEST --> [*]
    INSUFFICIENT_EVIDENCE --> [*]
    CONFLICT_DETECTED --> [*]
    INDEX_UNAVAILABLE --> [*]
```

---

### 2.4 Data Storage & Index Artifact Layout

```mermaid
flowchart LR
    subgraph RawData["Source Knowledge Layer"]
        Docs["Markdown Documents\n(DOC-001..DOC-026, DOC-MKT-001..004)"]
        Manifest["manifest.json\n(Document Metadata + SHA-256 Hashes)"]
    end

    subgraph ProcessedIndex["Persistent Vector Index Artifacts"]
        Vectors["vectors.npy\n(Float array: 348 x 512 or 43 x 256)"]
        Catalog["knowledge_index.json\n(Chunk text, offsets, IDs, tokens)"]
        ModelPickle["embedding_model.pkl\n(Fitted TfidfVectorizer vocabulary)"]
    end

    subgraph AuditStore["Decision Ledger"]
        LedgerJSON["records.json\n(JSON mapping: request_id -> record)"]
        TempAtomic["records.tmp\n(Atomic swap file with secret redaction)"]
    end

    Docs --> Manifest
    Manifest --> Catalog
    Catalog --> Vectors
    Catalog --> ModelPickle
    LedgerJSON -.-> TempAtomic
```

---

## 3. Subsystem Breakdown & Module Responsibilities

| Module | Core Classes / Functions | Primary Responsibility |
| :--- | :--- | :--- |
| `src/evidence_rag/ingestion.py` | `IngestionEngine` | Ingests documents declared in corpus `manifest.json`. Validates metadata completeness (8 required fields), detects duplicate IDs, and verifies SHA-256 content hashes. |
| `src/evidence_rag/cleaning.py` | `TextCleaner`, `clean_text` | 4-stage text preprocessing: Unicode NFKC normalization, HTML/script tag stripping, control character removal, PII/secret redaction, and whitespace consolidation. |
| `src/evidence_rag/chunking.py` | `Chunker` | Boundary-aware paragraph chunking with sentence splitting fallback for long passages. Enforces 400-char target size, 60-char overlap, and stable IDs (`CHUNK-{doc_id}-{index:03d}`). |
| `src/evidence_rag/embeddings.py` | `HybridTfidfEmbeddingEngine`, `BaseEmbeddingEngine` | Produces L2-normalized 512-dim (or 256-dim) representations using sublinear TF-IDF and n-grams (1, 2). Completely offline and deterministic. Supports optional neural embeddings. |
| `src/evidence_rag/indexing.py` | `VectorIndex` | In-memory and disk-backed vector storage. Computes exact cosine similarity matrix dot products. Serializes `vectors.npy`, `knowledge_index.json`, and `embedding_model.pkl`. |
| `src/evidence_rag/retrieval.py` | `Retriever` | Cosine similarity candidate retrieval with domain-aware routing (+0.05 domain boost, 0.60x cross-domain guard), exact keyword boost calibration, and mathematical sufficiency checking. |
| `src/evidence_rag/conflict_detection.py`| `ConflictDetector` | Scans retrieved passages for documented contradictory pairings (e.g. DOC-MKT-002 vs DOC-MKT-004 spend caps, DOC-009 vs DOC-020 pool sizes) using keyword/number heuristics. |
| `src/evidence_rag/context_builder.py` | `ContextBuilder` | Assembles retrieved evidence passages into formatted context blocks. Strictly enforces a 1,500 token budget cap to prevent context window overflow. |
| `src/evidence_rag/generation.py` | `DeterministicMockGenerator`, `GeminiGenerator`, `GroqGenerator`, `GrokGenerator` | Generates grounded responses with explicit citation tokens. Defaults to zero-latency offline mock extraction, with optional live LLM fallback. |
| `src/evidence_rag/evidence.py` | `CitationValidator` | Extracts citation tokens using regex and validates every cited chunk against the retrieved evidence set. Flags ungrounded citations. |
| `src/evidence_rag/confidence.py` | `ConfidenceScorer` | Calculates continuous confidence score (0.00 to 1.00) and compiles structured limitations list based on retrieval scores, margins, and conflict flags. |
| `src/evidence_rag/pipeline.py` | `RAGPipeline` | Master orchestrator for Task 1 technical question answering queries. |
| `src/evidence_rag/workflow.py` | `DecisionWorkflow` | Master orchestrator for Task 2 CMO proposal evaluation, recommendation synthesis, and managerial approval gate. |
| `src/evidence_rag/record_store.py` | `RecordStore` | Thread-safe, atomic disk storage for workflow transaction logs with automated API secret scrubbing. |
| `src/evidence_rag/cli.py` | Click command tree (`main`, `index`, `query`, `workflow`, etc.) | Rich terminal user interface providing human operators with query, evaluation, approval, and replay controls. |

---

## 4. Key Architectural Strengths & Structural Gaps

### Architectural Strengths
- **Decoupled Pipeline:** Clear separation of concerns between ingestion, indexing, retrieval, evaluation, and governance.
- **Deterministic Offline Replayability:** Offline test suite executes in ~6.3s without external API dependencies or network calls.
- **Fail-Safe Governance:** Built-in impossibility of automated spend authorization; proposals remain in `AWAITING_APPROVAL` until signed off.
- **Comprehensive Traceability:** Every recommendation records source document IDs, chunk IDs, and character offsets.

### Structural Gaps for Enterprise CMO Deployment
- **No HTTP / REST Web API:** Current interactions require local CLI or Python scripting. Cannot be consumed directly by external frontend portals without adding FastAPI/Starlette endpoints.
- **Unauthenticated Reviewer Identities:** Approval gate records plain text reviewer strings (`reviewer: str`) without cryptographic signatures or session tokens.
- **Heuristic Contradiction Detection:** Conflict detection is driven by registered pairs and keyword matching rather than general semantic Natural Language Inference (NLI).
