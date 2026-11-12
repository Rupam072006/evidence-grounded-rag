# Complete API and Interface Inventory

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System  
**Date:** 2026-11-11  

---

## 1. Interface Overview

The project provides two primary interface tiers:
1. **Command-Line Interface (CLI):** Powered by Click with Rich visual output and JSON export modes.
2. **Programmatic Python API:** Object-oriented service interfaces defined in `evidence_rag.pipeline`, `evidence_rag.workflow`, and `evidence_rag.record_store`.

> [!IMPORTANT]
> **No HTTP/REST Web Service Exists:** There are no FastAPI, Flask, Django, gRPC, or GraphQL services in this codebase. Integrations are invoked either as CLI sub-processes or imported as an in-process Python package.

---

## 2. Command-Line Interface (CLI) Inventory

The CLI is registered as console command `evidence-rag` or invocable via `python -m evidence_rag.cli`.

### 2.1 Core System Commands

| Command | Subcommands / Arguments | Options / Flags | Output Format | Description |
|---|---|---|---|---|
| `evidence-rag index` | None | `--config, -c <PATH>` | Terminal stdout | Reads documents from manifest, chunks text, fits vectorizer, and writes binary vectors to `data/index/`. |
| `evidence-rag query` | `<USER_QUERY>` *(Optional argument; prompts if omitted)* | `--config, -c <PATH>`<br>`--mode, -m [mock\|groq\|grok\|gemini]`<br>`--json-out` *(flag)* | Rich Panel & Tables OR JSON | Queries the RAG pipeline; returns answer, status, confidence score, retrieved evidence table, and verified citation table. |
| `evidence-rag verify` | None | `--config, -c <PATH>` | Rich status text | Verifies document manifest integrity, counts, SHA-256 hashes, and vector index loadability. |
| `evidence-rag evaluate` | None | `--questions, -q <PATH>` (default: `evaluation/questions.jsonl`)<br>`--output, -o <DIR>` (default: `evaluation/results`) | Rich Table | Executes standardized 22-question benchmark battery; computes status accuracy, retrieval success, and failure detection rates. |
| `evidence-rag demo` | None | None | Rich Panels & Excerpts | Runs scripted 3-query demonstration covering answerable, contradiction, and out-of-domain refusal scenarios. |

### 2.2 Workflow Governance Subcommands (`evidence-rag workflow <SUBCOMMAND>`)

| Subcommand | Arguments | Options / Flags | Output Format | Description |
|---|---|---|---|---|
| `evaluate` | `[PROPOSAL_ARG]` *(Optional positional text)* | `--preset [growth\|overspend\|incomplete\|conflict]`<br>`--request-id, -i <ID>`<br>`--title, -t <TITLE>`<br>`--proposal, -p <TEXT>`<br>`--department, -d <DEPT>`<br>`--budget, -b <FLOAT>`<br>`--submitted-by, -s <USER>`<br>`--interactive` *(flag)*<br>`--config, -c <PATH>`<br>`--json-out` *(flag)* | Rich Panel, Tables & Bulleted Lists OR JSON | Evaluates a marketing proposal against corporate policy. Synthesizes facts, inferences, assumptions, and unknowns. Stops at the Human Approval Gate (`AWAITING_APPROVAL`). |
| `ask` | `[QUESTION]` *(Optional argument; prompts if omitted)* | `--config, -c <PATH>`<br>`--mode, -m <MODE>`<br>`--json-out` *(flag)* | Rich Panel & Evidence Table OR JSON | Answers informational marketing policy questions directly without generating a proposal workflow record. |
| `approve` | `<REQUEST_ID>` *(Required)* | `--decision, -d [APPROVED\|REJECTED]` (default: `APPROVED`)<br>`--reviewer, -r <NAME>` (default: `Prof_Evaluator`)<br>`--notes, -n <TEXT>`<br>`--config, -c <PATH>`<br>`--json-out` *(flag)* | Rich Panel OR JSON | Submits binding human approval decision; records reviewer identity, timestamp, and notes in the audit trail. |
| `reject` | `<REQUEST_ID>` *(Required)* | `--reviewer, -r <NAME>` (default: `Prof_Evaluator`)<br>`--reason, -n <TEXT>`<br>`--config, -c <PATH>`<br>`--json-out` *(flag)* | Rich Panel OR JSON | Submits binding human rejection decision for a pending workflow proposal. |
| `show` | `<REQUEST_ID>` *(Required)* | `--config, -c <PATH>`<br>`--json-out` *(flag)* | Rich Multi-Panel Record OR JSON | Displays full audit history, verified facts, recommendation report, and approval sign-off for a specific request ID. |
| `list` / `list-records` | None | `--config, -c <PATH>` | Rich Table | Displays table of all stored workflow proposals, budgets, states, submitters, and reviewers. |
| `replay` | `<REQUEST_ID>` *(Required)* | `--config, -c <PATH>`<br>`--json-out` *(flag)* | Rich Comparison Panel OR JSON | Replays a past proposal against current corpus and index; reconstructs evidence and verifies deterministic reproducibility. |

---

## 3. Programmatic Python Class APIs

### 3.1 `evidence_rag.pipeline.RAGPipeline`

**Instantiated as:** `pipeline = RAGPipeline(config=None, base_dir=None)`

| Method | Parameters | Return Type | Description |
|---|---|---|---|
| `build_index()` | None | `VectorIndex` | Performs ingestion, chunking, and embedding generation; saves serialized index to disk. |
| `load_index()` | None | `VectorIndex` | Deserializes vector index and chunk catalog from disk. |
| `ensure_index(check_staleness=True)` | `check_staleness: bool` | `VectorIndex` | Loads existing index or rebuilds if absent or if corpus SHA-256 fingerprint has changed. |
| `validate_input(query)` | `query: str` | `Tuple[bool, Optional[str]]` | Validates query length (3 to 500 chars), whitespace, and control characters. |
| `query(user_query)` | `user_query: str` | `RAGResponse` | Master orchestrator: validates input, retrieves chunks, checks sufficiency, detects conflicts, generates answer, validates citations, and scores confidence. |

### 3.2 `evidence_rag.workflow.DecisionWorkflow`

**Instantiated as:** `wf = DecisionWorkflow(config=None, config_path=None, base_dir=None, record_store=None)`

| Method | Parameters | Return Type | Description |
|---|---|---|---|
| `ensure_index()` | None | `None` | Verifies underlying knowledge base index availability. |
| `ask_policy_question(question)` | `question: str` | `RAGResponse` | Queries the underlying pipeline for policy answers without persisting workflow records. |
| `validate_request(request)` | `request: WorkflowRequest` | `Tuple[bool, Optional[str]]` | Validates ID, title length (>=3), proposal text (>=10), and non-negative budget. |
| `evaluate_proposal(request)` | `request: WorkflowRequest` | `WorkflowRecord` | Executes end-to-end evaluation pipeline; halts at `AWAITING_APPROVAL` status. |
| `submit_approval(request_id, decision, reviewer, notes)` | `request_id: str`<br>`decision: str`<br>`reviewer: str`<br>`notes: str` | `WorkflowRecord` | Records human managerial decision (`APPROVED`/`REJECTED`) into the persistent ledger. |
| `get_record(request_id)` | `request_id: str` | `Optional[WorkflowRecord]` | Retrieves audit record by request ID. |
| `list_records()` | None | `List[WorkflowRecord]` | Lists all saved workflow records sorted by creation timestamp descending. |

### 3.3 `evidence_rag.record_store.RecordStore`

**Instantiated as:** `store = RecordStore(storage_dir=Path("data/workflow_records"))`

| Method | Parameters | Return Type | Description |
|---|---|---|---|
| `save_record(record)` | `record: WorkflowRecord` | `WorkflowRecord` | Persists or updates a workflow record with secret scrubbing. |
| `get_record(request_id)` | `request_id: str` | `Optional[WorkflowRecord]` | Retrieves record by key from `records.json`. |
| `list_records()` | None | `List[WorkflowRecord]` | Deserializes and returns all stored records. |
| `record_decision(request_id, decision)` | `request_id: str`<br>`decision: ApprovalDecision` | `Optional[WorkflowRecord]` | Enforces single-decision finality (DEFECT-003) and validates non-empty reviewer identity. |

---

## 4. Request and Response Data Contracts (Schemas)

All data structures are implemented using Pydantic v2 `BaseModel` models.

### 4.1 Workflow Request Contract (`WorkflowRequest`)
```json
{
  "request_id": "REQ-GROWTH-01",
  "title": "Q4 Enterprise Growth Initiative",
  "proposal_text": "Allocate $35,000 across Google search ads and content syndication aiming for 450 conversions with target CTR of 2.4%.",
  "department": "Marketing",
  "requested_budget": 35000.0,
  "submitted_by": "analyst",
  "created_at": "2026-11-11T10:00:00Z",
  "metadata": {}
}
```

### 4.2 Workflow Record Schema (`WorkflowRecord`)
```json
{
  "request_id": "REQ-GROWTH-01",
  "status": "AWAITING_APPROVAL",
  "request": { /* WorkflowRequest */ },
  "evidence_set": [
    {
      "chunk": {
        "chunk_id": "DOC-021-C001",
        "document_id": "DOC-021",
        "chunk_index": 0,
        "text": "Executive Summary...",
        "char_start": 0,
        "char_end": 395,
        "token_count": 55,
        "category": "business_proposal",
        "metadata": { "title": "Enterprise Growth Campaign Proposal" }
      },
      "score": 0.2850,
      "rank": 1,
      "raw_similarity": 0.2450
    }
  ],
  "citations": [
    {
      "document_id": "DOC-021",
      "chunk_id": "DOC-021-C001",
      "quote": null,
      "is_valid": true,
      "validation_reason": "Verified in retrieved context."
    }
  ],
  "conflict": null,
  "recommendation": {
    "summary": "Evaluated proposal 'Q4 Enterprise Growth Initiative' against authoritative Q4 marketing strategy...",
    "verified_facts": [
      {
        "statement": "The primary objective is to drive qualified product trials and expand enterprise pipeline opportunities.",
        "citation": { "document_id": "DOC-021", "chunk_id": "DOC-021-C001", "is_valid": true },
        "source_document_id": "DOC-021",
        "source_chunk_id": "DOC-021-C001"
      }
    ],
    "inferences": [
      "Requested budget of $35,000.00 is within the policy maximum cap of $50,000.00 [DOC-022]."
    ],
    "assumptions": [
      "Assumes audience response rates and CAC mirror historical performance benchmarks (CTR ~2.4%, CAC ~$32.00) [DOC-023]."
    ],
    "unknowns": [
      "Vendor rate fluctuations: Specific real-time CPM pricing from ad exchanges is subject to auction dynamics."
    ],
    "risk_assessment": "Low Risk: Proposal aligns with documented growth targets and financial ceilings.",
    "recommended_action": "APPROVE"
  },
  "approval": {
    "request_id": "REQ-GROWTH-01",
    "decision": "APPROVED",
    "reviewer": "Prof_Evaluator",
    "decision_notes": "Audited against policy; approved.",
    "decided_at": "2026-11-11T10:05:00Z"
  },
  "history": [
    { "action": "REQUEST_SUBMITTED", "by": "analyst", "timestamp": "2026-11-11T10:00:00Z" },
    { "action": "EVIDENCE_RETRIEVED", "chunk_count": 4, "timestamp": "2026-11-11T10:00:01Z" },
    { "action": "RECOMMENDATION_SYNTHESIZED", "action_proposed": "APPROVE", "timestamp": "2026-11-11T10:00:02Z" },
    { "action": "AWAITING_HUMAN_APPROVAL", "message": "PAUSED AT APPROVAL GATE", "timestamp": "2026-11-11T10:00:02Z" },
    { "action": "APPROVAL_DECISION_SUBMITTED", "decision": "APPROVED", "by": "Prof_Evaluator", "timestamp": "2026-11-11T10:05:00Z" }
  ],
  "created_at": "2026-11-11T10:00:00Z",
  "updated_at": "2026-11-11T10:05:00Z"
}
```

### 4.3 General RAG Response Schema (`RAGResponse`)
```json
{
  "query": "What character encoding is mandatory for all incoming documents in AegisCore?",
  "status": "ANSWERED",
  "answer": "All incoming files are enforced to use UTF-8 character encoding. [DOC-004:DOC-004-C003]...",
  "evidence": [ /* List of RetrievedChunk */ ],
  "source_document_ids": ["DOC-004", "DOC-005", "DOC-007"],
  "source_chunk_ids": ["DOC-004-C003", "DOC-005-C002", "DOC-007-C002"],
  "citations": [ /* List of Citation */ ],
  "confidence": 0.8420,
  "limitations": [
    "Confidence metric reflects lexical and semantic representation overlap; it is not a calibrated Bayesian posterior probability."
  ],
  "conflicting_evidence": null,
  "latency_ms": 14.2,
  "model_name": "deterministic_mock"
}
```

---

## 5. Authentication and Authorization

- **Internal Authorization:** None. There is no user authentication, session token, API key gate, or JWT validation on CLI commands or Python functions. The reviewer parameter in `submit_approval(reviewer="Alice")` is accepted as an unverified string.
- **External API Authentication:**
  - `Google Gemini`: API key passed via query parameter `?key={GEMINI_API_KEY}`.
  - `Groq Cloud`: HTTP header `Authorization: Bearer {GROQ_API_KEY}`.
  - `xAI Grok`: HTTP header `Authorization: Bearer {GROK_API_KEY}`.
  - **Audit Finding:** In the current runtime, **no API keys are set**. Running online modes results in `GENERATION_UNAVAILABLE`.

---

## 6. External Services & Remote Integrations

| External Service | Endpoint URL | Protocol | Authentication | Current Runtime Status |
|---|---|---|---|---|
| **Google Gemini API** | `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` | HTTPS / REST | API Key query param | **UNVERIFIED / INACTIVE** (No key configured) |
| **Groq Cloud API** | `https://api.groq.com/openai/v1/chat/completions` | HTTPS / REST | Bearer Token | **UNVERIFIED / INACTIVE** (No key configured) |
| **xAI Grok API** | `https://api.x.ai/v1/chat/completions` | HTTPS / REST | Bearer Token | **UNVERIFIED / INACTIVE** (No key configured) |

---

## 7. Logging and Observability

- **Logger:** Python standard `logging` configured via `src/evidence_rag/logging_config.py`.
- **Structured Formatting:** `[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s`.
- **Secret Redaction:** `SecretMaskingFilter` dynamically intercepts log records before output and replaces:
  - Google Gemini API keys (`AIzaSy...`) -> `[REDACTED_API_KEY]`
  - Bearer tokens (`Bearer ...`) -> `Bearer [REDACTED_TOKEN]`
  - Generic secrets/passwords -> `\1=[REDACTED]`
- **Log Destinations:**
  - Console: Standard error (stderr).
  - File: `logs/rag_system.log` (or `logs/workflow.log` in marketing config).
