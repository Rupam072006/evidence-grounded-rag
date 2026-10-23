# AegisCore Code Packet — Critical Architecture, Entry Points, and Logic

This document provides a concise, inspectable technical breakdown of critical files, entry points, and core algorithmic excerpts for technical audit and pair-programming review.

---

## 1. Critical File Hierarchy & Entry Points

```
evidence-grounded-rag/
├── src/evidence_rag/
│   ├── workflow.py            # [CRITICAL] Core decision-support workflow & human approval gate
│   ├── workflow_schemas.py    # [CRITICAL] Pydantic models (WorkflowRequest, RecommendationReport, WorkflowRecord)
│   ├── record_store.py        # [CRITICAL] Persistent, secret-scrubbed JSON audit ledger
│   ├── cli.py                 # [ENTRY POINT] Click command-line interface & workflow subcommands
│   ├── pipeline.py            # [CORE ENGINE] End-to-end RAG orchestrator & staleness manager
│   ├── conflict_detection.py  # [ALGORITHM] Cross-document contradiction detection engine
│   ├── evidence.py            # [VERIFIER] Citation parsing and content attribution validator
│   ├── retrieval.py           # [SEARCH] Cosine similarity retrieval & sufficiency floor evaluator
│   └── generation.py          # [GENERATOR] Grounded mock & cloud LLM with 429 exponential retry
├── data/
│   ├── documents/             # 20 standardized technical documents (DOC-001 - DOC-020)
│   ├── marketing_corpus/      # 4 synthetic campaign policy documents (DOC-MKT-001 - DOC-MKT-004)
│   └── workflow_records/      # Auditable JSON records database
├── tests/
│   ├── functional/
│   │   ├── test_workflow.py   # 8 workflow & approval gate tests
│   │   └── test_day3_scenarios.py # 10 failure & integration scenario tests
└── evaluation/
    ├── questions.jsonl        # 25 benchmark technical questions
    └── results/               # Empirical benchmark outputs
```

---

## 2. Key Logic & Excerpts

### A. The Human Approval Gate State Machine (`src/evidence_rag/workflow.py`)
Enforces the governance boundary where AI recommendations strictly halt for human review:

```python
def evaluate_proposal(self, request: WorkflowRequest) -> WorkflowRecord:
    # 1. Validation & Index Check
    is_valid, validation_err = self.validate_request(request)
    if not is_valid:
        return self._record_failure(request, WorkflowStatus.INVALID_REQUEST, validation_err)

    # 2. Retrieval & Sufficiency Assessment
    retrieved = self.retriever.retrieve(request.proposal_text)
    if not self.retriever.assess_evidence_sufficiency(retrieved, query=request.proposal_text):
        return self._record_failure(request, WorkflowStatus.INSUFFICIENT_EVIDENCE)

    # 3. Conflict Detection
    conflict = self.conflict_detector.detect_conflicts(request.proposal_text, retrieved)
    if conflict:
        return self._record_conflict(request, conflict)

    # 4. Recommendation Formulation (Separating Facts, Inferences, Assumptions, Unknowns)
    report, citations = self.synthesize_recommendation(request, retrieved)

    # 5. STRICT HALT AT HUMAN APPROVAL GATE
    record = WorkflowRecord(
        request_id=request.request_id,
        status=WorkflowStatus.AWAITING_APPROVAL, # Halts here; NO auto-approval
        request=request,
        evidence_set=retrieved,
        citations=citations,
        recommendation=report,
        approval=None # Requires human signature
    )
    return self.record_store.save_record(record)

def submit_approval(self, request_id: str, decision: str, reviewer: str, notes: str) -> WorkflowRecord:
    """Human approval gate: Records human managerial decision (APPROVED or REJECTED)."""
    approval = ApprovalDecision(
        request_id=request_id,
        decision=decision.upper(),
        reviewer=reviewer.strip(),
        decision_notes=notes.strip()
    )
    return self.record_store.record_decision(request_id, approval)
```

---

### B. Automated Secret Scrubbing (`src/evidence_rag/record_store.py`)
Ensures that no API keys, private tokens, or Bearer credentials can ever be saved into workflow audit files:

```python
def _scrub_secrets(self, text: str) -> str:
    """Recursively scrub high-entropy tokens, passwords, and API keys."""
    # Matches patterns like gsk_..., AIzaSy..., bearer tokens, etc.
    patterns = [
        r"(gsk_[A-Za-z0-9]{20,})",
        r"(AIzaSy[A-Za-z0-9_-]{33})",
        r"(sk-[A-Za-z0-9]{20,})",
        r"(bearer\s+[A-Za-z0-9\._-]{20,})"
    ]
    for pat in patterns:
        text = re.sub(pat, "[REDACTED_API_KEY]", text, flags=re.IGNORECASE)
    return text
```

---

### C. Corpus Fingerprint & Staleness Rebuilding (`src/evidence_rag/pipeline.py`)
Computes an aggregate SHA-256 over all sorted documents in the corpus to detect file changes or deletions:

```python
def compute_corpus_fingerprint(self) -> str:
    manifest_data = self.ingestion_engine.load_manifest()
    sorted_docs = sorted(manifest_data["documents"], key=lambda x: x["document_id"])
    hasher = hashlib.sha256()
    for doc in sorted_docs:
        file_path = self.base_dir / doc["source"]
        if file_path.exists():
            with open(file_path, "rb") as f:
                hasher.update(f.read())
    return hasher.hexdigest()

def is_index_stale(self, index: VectorIndex) -> bool:
    current_fingerprint = self.compute_corpus_fingerprint()
    return index.corpus_fingerprint != current_fingerprint
```

---

### D. Citation Attribution Regex (`src/evidence_rag/evidence.py`)
Supports standard brackets, unicode lenticular brackets, and sub-chunk identifiers:

```python
# Matches: [DOC-001:DOC-001-C001], [DOC-MKT-001:C001], 【DOC-001-C001】
CITATION_PATTERN = re.compile(
    r"[\[\u3010](DOC-(?:[A-Za-z0-9]+-)?\d{3})(?:[:-]([A-Za-z0-9\-_]+))?[\]\u3011]"
)
```
