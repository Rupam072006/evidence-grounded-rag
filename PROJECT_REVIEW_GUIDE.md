# AegisCore — Comprehensive Project Review & Viva Defense Manual

> **Project Name:** AegisCore — Evidence-Grounded Multi-Domain RAG & Decision-Support System  
> **Author:** Rupam Patne (Computer Science Engineering, AI/ML Specialization)  
> **Repository:** https://github.com/Rupam072006/evidence-grounded-rag  
> **Target Environment:** Windows 10/11 / PowerShell / Python 3.10 – 3.13 (Verified on Python 3.13.1)  
> **System Status:** Production-Ready, 126/126 Tests Passing (100%), 100% Deterministic Offline & Cloud LLM Capable.

---

## 1. EXECUTIVE ELEVATOR PITCH

### 30-Second Summary (When asked: "In short, what did you build?")
> *"I built **AegisCore**, an enterprise-grade, zero-hallucination Retrieval-Augmented Generation (RAG) and decision-support system. While conventional LLMs invent facts and extrapolate beyond their training data, AegisCore mathematically guarantees that answers originate strictly from verified, retrieved documents with claim-level citations `[DOCUMENT_ID:CHUNK_ID]`. If evidence is insufficient, it refuses to guess. If documents contradict one another, it detects the conflict. In Task 2 and 3, I extended this into a corporate policy decision assistant governed by a **Mandatory Human Approval Gate**, ensuring the AI only recommends decisions while human managers retain final, auditable sign-off."*

### 2-Minute Architectural Pitch (For opening the presentation)
> *"Modern generative AI systems suffer from three critical flaws: **hallucinations**, **inability to handle conflicting sources**, and **dangerous autonomous decision-making**. AegisCore solves all three through a 3-tier architecture:
> 
> 1. **Task 1 — High-Assurance Technical RAG:** Built over a 20-document technical knowledge base (Python, SQL, Machine Learning, Systems). It implements a 4-stage cleaning pipeline, 400-character boundary-aware chunking, a 512-dimensional hybrid vectorizer normalized to unit L2 norm, a mathematical sufficiency floor ($s \ge 0.20$ similarity, $\ge 28\%$ keyword coverage), and claim-level citation validation.
> 2. **Task 2 — Multi-Domain Decision-Support Assistant:** Integrates technical and business documents into one unified 26-document, 348-chunk knowledge base. It executes a 7-stage proposal evaluation pipeline (budget ceiling audits against `DOC-022`, channel restrictions, and risk analysis) that halts at a **Mandatory Human Approval Gate** (`AWAITING_APPROVAL`).
> 3. **Task 3 — Reliability, Security, and Governance:** Validated through 126 automated tests. Includes 20 adversarial security tests against prompt injection, atomic audit logging in `records.json`, duplicate approval blocking, and deterministic evidence replay."*

---

## 2. END-TO-END SYSTEM ARCHITECTURE & DATA FLOW

```
[ Raw Documents (data/documents/*.md) ] ── (26 documents across 7 categories)
                  │
                  ▼
[ Manifest & Provenance Validation (ingestion.py) ] ── (SHA-256 fingerprinting)
                  │
                  ▼
[ 4-Stage Text Cleaning (cleaning.py) ] ── (Unicode NFKC -> Control chars -> Whitespace -> Security tags)
                  │
                  ▼
[ Boundary-Aware Chunking (chunking.py) ] ── (400 chars, 60 overlap, sentence boundary preserved)
                  │
                  ▼
[ 512-D Hybrid Embedding Engine (embeddings.py) ] ── (Char + Word n-grams, L2 unit norm ||v||=1.0)
                  │
                  ▼
[ Persistent Vector Index (indexing.py) ] ── (vectors.npy, knowledge_index.json, embedding_model.pkl)
                  │
                  ▼
[ User Query via CLI / API (cli.py) ]
                  │
                  ▼
[ Domain-Aware Retrieval & Routing (retrieval.py) ] ── (Top-k=4, candidate pool=20, domain boost)
                  │
                  ├─────────────────────────────────────────┐
                  ▼                                         ▼
    [ Sufficiency Floor Check ]               [ Contradiction Interception ]
    (Score < 0.20 or Coverage < 28%)          (Algorithmic / Document Conflict)
                  │                                         │
                  ▼                                         ▼
     INSUFFICIENT_EVIDENCE                      CONFLICT_DETECTED
     (Canonical Refusal)                        (Surfaces Conflicting Sources)
                  │                                         │
                  └────────────────────┬────────────────────┘
                                       │ (If Sufficient & Coherent)
                                       ▼
                       [ Sentence-Grounded Generation ]
                       (Mock Deterministic / Groq / Gemini)
                                       │
                                       ▼
                       [ Post-Gen Citation Verification ]
                       (Validates [DOC-XXX:CHUNK-YYY] against context)
                                       │
                                       ▼
                      [ Task 1 Status: ANSWERED with Citations ]
                                       │
                                       ▼
                     [ Task 2: Business Decision Workflow ]
               (Budget check vs DOC-022, facts/assumptions/unknowns)
                                       │
                                       ▼
                  [ Mandatory Human Approval Gate: AWAITING_APPROVAL ]
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
          [ Manager: APPROVED ]               [ Manager: REJECTED ]
         (Reviewer, UTC Timestamp)           (Reviewer, UTC Timestamp)
                     │                                   │
                     └─────────────────┬─────────────────┘
                                       ▼
                     [ Atomic Audit Store (records.json) ]
                     (Terminal state locked; duplicate blocked)
```

---

## 3. CORE ARCHITECTURAL PILLARS (THE 3 TASKS)

### Task 1: Evidence-Grounded Technical RAG System
* **Corpus:** 20 technical documents covering Python language internals, SQL relational queries, machine learning fundamentals, and distributed system architectures.
* **Anti-Hallucination Guarantees:**
  * Strict mathematical sufficiency floor: if cosine similarity $< 0.20$ or keyword coverage $< 28\%$, emits canonical refusal `INSUFFICIENT_EVIDENCE`.
  * Claim-level attribution syntax: Every factual assertion must link to an exact chunk citation `[DOC-XXX:CHUNK-YYY]`.
  * Automated contradiction detection: Flags conflicting specifications (e.g., DOC-009 specifying top-k=5 vs DOC-020 specifying top-k=10) with status `CONFLICT_DETECTED`.

### Task 2: Multi-Domain Decision-Support Assistant
* **Corpus Expansion:** Unified 26-document knowledge base adding 6 synthetic business and governance documents (`DOC-021` to `DOC-026`).
* **Clean Command Separation:**
  * `workflow ask`: Pure policy/marketing Q&A. Answers questions with citations; **no** budget prompt, **no** proposal creation, **no** records generated, **no** approval gate.
  * `workflow evaluate`: Evaluates proposals against policy; creates `AWAITING_APPROVAL` record; audits budget against $50k corporate ceiling (`DOC-022`); checks influencer limits (`DOC-025`); surfaces facts, assumptions, and unknowns.
* **Mandatory Human Approval Gate:** System **never** executes or auto-approves funds. It pauses at `AWAITING_APPROVAL` until a human reviewer submits a binding decision (`workflow approve` or `workflow reject`).

### Task 3: Reliability, Security, Replay & Final Verification
* **Automated Testing:** 126 tests across 8 tiers (unit, boundary, integration, functional, regression, security, approval, replay). 100% pass rate in ~2.2 seconds.
* **Adversarial Security (20 Tests):** Hardened against direct prompt injections, instruction overrides ("ignore previous instructions"), role-play jailbreaks, unicode homoglyphs, and markdown link data exfiltration.
* **Approval Integrity:** Enforces non-empty reviewer validation and terminal-state duplicate decision blocking (DEFECT-003).
* **Deterministic Replay:** Reconstructs historical proposal evidence from stored parameters to verify decision parity against current index.

---

## 4. STEP-BY-STEP LIVE REVIEW DEMONSTRATION SCRIPT

Follow this exact sequence during your review. Each step includes the **command to run**, **what to say to the reviewer**, and **what the screen shows**.

---

### Step 1: Environment Activation & System Health Verification
**Reviewer Talking Point:**  
> *"Before running any queries, I will show that our entire project is self-contained, reproducible on Windows, and verified using cryptographic SHA-256 fingerprints."*

**Command:**
```powershell
cd c:\Users\rupam\OneDrive\Desktop\RAG
.\.venv_audit\Scripts\activate
python -m evidence_rag.cli verify
```

**What to Point Out on Screen:**
* Notice the `(.venv_audit)` prompt: Runs isolated in Python 3.13.
* Manifest validation: Exactly 26 documents validated against SHA-256 hashes.
* Index validation: Exactly 348 passages loaded across 512 dimensions.

---

### Step 2: The 3-in-1 Automated RAG Demonstration (`demo`)
**Reviewer Talking Point:**  
> *"Now I will run our automated live demo command. In one run, this demonstrates how AegisCore handles the three fundamental types of queries: answerable factual questions, cross-document contradictions, and out-of-domain unanswerable queries."*

**Command:**
```powershell
python -m evidence_rag.cli demo
```

**What to Point Out on Screen:**
1. **Query 1 (Factual):** Answers the character encoding question with status `ANSWERED` and verified citations `[DOC-004:DOC-004-C002]`.
2. **Query 2 (Contradiction):** Demonstrates our contradiction detector. When queried about retrieval top-k parameters, it detects a conflict between DOC-009 (top-k=5) and DOC-020 (top-k=10). Status: `CONFLICT_DETECTED`. It does not guess!
3. **Query 3 (Unanswerable):** When asked for Aunt May's cookie recipe, the similarity score falls below the 0.20 sufficiency floor. Status: `INSUFFICIENT_EVIDENCE`. Zero hallucination.

---

### Step 3: Factual Question with Citation Audit (`query`)
**Reviewer Talking Point:**  
> *"Let's run a standalone interactive query to inspect the granular retrieval table and citation verification mechanism."*

**Command:**
```powershell
python -m evidence_rag.cli query "What character encoding is mandatory for all incoming documents in AegisCore?"
```

**What to Point Out on Screen:**
* Point to the **Status: ANSWERED** and latency (~15-40 ms).
* Point to the **Retrieved Evidence Passages** table: Rank 1 is `DOC-004-C002` with similarity score `0.606`.
* Point to the **Claim Citations** table: Shows `DOC-004` chunk `DOC-004-C002` verified as `YES`. Every single claim is linked to source evidence.

---

### Step 4: Standardized Benchmark Evaluation (`evaluate`)
**Reviewer Talking Point:**  
> *"We evaluate our system objectively using a 25-question standardized benchmark that tests retrieval recall, status accuracy, and failure detection."*

**Command:**
```powershell
python -m evidence_rag.cli evaluate
```

**What to Point Out on Screen:**
* **Status Accuracy: 100.0%** (25/25 queries correctly classified).
* **Retrieval Success Rate: 94.7%** (18/19 answerable queries retrieved target evidence in top-k).
* **Failure Detection Rate: 100.0%** (All unanswerable and contradictory queries intercepted).
* **Citation Validity Rate: 100.0%** (Zero invalid citations emitted).
* **Average Latency: ~14 ms**.

---

### Step 5: Task 2 Informational Policy Q&A (`workflow ask`)
**Reviewer Talking Point:**  
> *"In Task 2, we separated informational policy questions from business proposal evaluations. Notice that when I ask about company policies with `workflow ask`, it answers directly with citations without asking for a budget or creating proposal records."*

**Command:**
```powershell
python -m evidence_rag.cli workflow ask "What is the budget ceiling in DOC-022?"
```

**What to Point Out on Screen:**
* Answer correctly extracts the **$50,000.00** corporate marketing budget ceiling from `DOC-022-C004`.
* It provides citations to `DOC-021` and `DOC-022`.
* **Key Point for Reviewers:** It did **not** prompt for a budget, generate a Request ID, touch `records.json`, or open an approval gate.

---

### Step 6: Task 2 Business Proposal Evaluation (`workflow evaluate`)
**Reviewer Talking Point:**  
> *"Now let's submit a $35,000 enterprise growth campaign proposal. Watch how AegisCore audits the proposal against corporate policies and halts at the Mandatory Human Approval Gate."*

**Command:**
```powershell
python -m evidence_rag.cli workflow evaluate --preset growth
```

**What to Point Out on Screen:**
* **Request ID:** Generated unique identifier `REQ-GROWTH-01`.
* **Status: AWAITING_APPROVAL:** Explicitly notes `PAUSED AT APPROVAL GATE (No external action taken)`.
* **Recommendation Summary:** Recommends `APPROVE` because $35,000 is under the $50,000 ceiling in `DOC-022`.
* **Evidentiary Breakdown:**
  * *Verified Facts:* Concrete evidence from `DOC-021`, `DOC-022`, and `DOC-023` (450 conversions / $35k benchmark).
  * *Inferences:* Logical deduction confirming spend is within policy limits.
  * *Assumptions:* Assumptions about ad platform auction rate stability.
  * *Unknowns:* Flags auction pricing and real-time CPM fluctuations.

---

### Step 7: Human Approval Sign-Off & Duplicate Protection (`workflow approve`)
**Reviewer Talking Point:**  
> *"The AI recommends, but a human manager must sign off. I will now act as the authorized reviewer and record an immutable approval decision in the audit trail."*

**Command:**
```powershell
python -m evidence_rag.cli workflow approve REQ-GROWTH-01 --reviewer "Rupam Patne" --notes "Audited against DOC-022 ceiling; approved for Q4."
```

**What to Point Out on Screen:**
* Shows status transition to **`APPROVED`**.
* Displays reviewer name (`Rupam Patne`), UTC timestamp, and justification notes.

**Reviewer Talking Point (Demonstrate Defect Prevention):**  
> *"To ensure audit integrity, what happens if someone attempts to approve or alter an already-finalized proposal? The system strictly blocks duplicate decisions."*

**Command:**
```powershell
python -m evidence_rag.cli workflow approve REQ-GROWTH-01 --reviewer "Another Manager"
```

**What to Point Out on Screen:**
* The command fails with code 1 and outputs:  
  `Error: Request REQ-GROWTH-01 is already finalized with status 'APPROVED'. Duplicate decisions are not permitted.`

---

### Step 8: Policy Conflict Detection (`--preset conflict`)
**Reviewer Talking Point:**  
> *"What happens if a proposal violates a restricted policy or encounters conflicting guidelines? Let's run the conflict preset."*

**Command:**
```powershell
python -m evidence_rag.cli workflow evaluate --preset conflict
```

**What to Point Out on Screen:**
* **Request ID:** `REQ-CONFLICT-01`.
* **Action Recommendation: REJECT**.
* Why? The proposal requests $20,000 for an influencer campaign. While `DOC-024` allows up to $25,000, `DOC-025` strictly caps restricted influencer spend at $10,000. AegisCore intercepts the contradiction and recommends rejection.

---

### Step 9: Audit Ledger & Deterministic Replay (`show` & `replay`)
**Reviewer Talking Point:**  
> *"All proposal decisions are recorded in an audit ledger. We can inspect any proposal or replay its evidence reconstruction to verify consistency."*

**Commands:**
```powershell
python -m evidence_rag.cli workflow list
python -m evidence_rag.cli workflow show REQ-GROWTH-01
python -m evidence_rag.cli workflow replay REQ-GROWTH-01
```

**What to Point Out on Screen:**
* `workflow list`: Displays the ledger with all Request IDs, Budgets, and Statuses (`APPROVED`, `AWAITING_APPROVAL`).
* `workflow show`: Displays the complete audit trail including submitter timestamp and human reviewer sign-off.
* `workflow replay`: Reconstructs original evidence and confirms:  
  `Status Match: YES | Retrieval Match: YES | Action Match: IDENTICAL (APPROVE)`.

---

### Step 10: Complete Test Suite & Security Defense Verification
**Reviewer Talking Point:**  
> *"Finally, we demonstrate project reliability and security hardening by running our automated test suite of 126 tests, including 20 adversarial security penetration tests."*

**Commands:**
```powershell
# Run the complete test suite
pytest tests -q

# Run the 20 adversarial security attack tests
pytest tests/task3/test_task3_security.py -v
```

**What to Point Out on Screen:**
* **126 passed in ~2.2 seconds.**
* Show security test names: `test_prompt_injection_ignore_instructions`, `test_roleplay_jailbreak_defense`, `test_secret_leakage_api_keys_sanitized`, `test_unicode_homoglyph_injection`. 100% defense against ungrounded prompt hijacking.

---

## 5. TECHNICAL DEEP-DIVE: HOW IT WORKS UNDER THE HOOD

When a reviewer asks technical questions about specific modules, refer to these architectural specifications:

### 1. 4-Stage Text Cleaning Pipeline (`cleaning.py`)
* **Stage 1 (Unicode Normalization):** Applies NFKC normalization to standardize ligatures, full-width characters, and compatibility characters.
* **Stage 2 (Control Character Removal):** Strips ASCII control codes (0x00–0x1F, 0x7F) while strictly preserving legitimate whitespace (`\n`, `\t`).
* **Stage 3 (Whitespace Standardization):** Collapses multiple consecutive spaces and tabs into single spaces and standardizes line breaks (`\r\n` $\rightarrow$ `\n`).
* **Stage 4 (Security Tag Sanitization):** Strips HTML, `<script>`, XML, and markdown iframe injection tags to prevent stored prompt injections.

### 2. Boundary-Aware Chunking (`chunking.py`)
* **Chunk Target:** 400 characters target length with a 60-character sliding boundary overlap.
* **Sentence Preservation:** Uses regex boundary scanning (`(?<=[.!?])\s+`) to ensure chunks do not slice sentences in half.
* **Deterministic IDs:** Assigns immutable IDs formatted as `DOC-XXX-CYYY` (e.g. `DOC-004-C002`).

### 3. 512-Dimensional Hybrid Embedding Engine (`embeddings.py`)
* **Feature Extraction:** Combines word n-grams (1-2 words) with sub-word character n-grams (3-5 characters) to capture both semantic domain vocabulary and typographical variations.
* **L2 Unit Normalization:** Every embedding vector $\mathbf{v}$ is normalized such that $\|\mathbf{v}\|_2 = 1.0$.
* **Mathematical Property:** Normalizing vectors to unit length means cosine similarity reduces directly to a fast dot product:
  $$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \mathbf{u} \cdot \mathbf{v}$$

### 4. Anti-Hallucination Sufficiency Floor (`confidence.py`, `retrieval.py`)
* An answer is generated **only** if:
  1. Top candidate similarity score $s_{\text{top}} \ge 0.20$.
  2. Query keyword coverage in retrieved context $c_{\text{coverage}} \ge 28\%$.
* If either threshold is breached, the pipeline aborts generation and returns `INSUFFICIENT_EVIDENCE` with confidence 0.00.

### 5. Algorithmic Contradiction Detection (`conflict_detection.py`)
* Detects numerical discrepancies and maintains an active registry of mutually contradictory document pairs (e.g. `DOC-009` vs `DOC-020` on retrieval sizing; `DOC-024` vs `DOC-025` on influencer spending caps).
* When chunks from contradictory documents both appear in the top-k candidate pool with high similarity, generation is intercepted and status is flagged as `CONFLICT_DETECTED`.

### 6. Claim-Level Citation Verification (`evidence.py`)
* Post-generation audit scans the generated text for `[DOCUMENT_ID:CHUNK_ID]` tokens.
* Checks each citation against the set of retrieved chunks present in the prompt context.
* Flags citations as `is_valid: True` or `is_valid: False`. Any answer with invalid citations is rejected.

### 7. Human Approval Gate & Audit Store (`workflow.py`, `record_store.py`)
* Proposals transition through state machine: `SUBMITTED` $\rightarrow$ `AWAITING_APPROVAL` $\rightarrow$ `APPROVED` or `REJECTED`.
* Automated approval is structurally impossible.
* Persisted in `data/workflow_records/records.json` using atomic temporary file replacement (`.tmp` $\rightarrow$ `.json`) to prevent data corruption during sudden process termination.
* Secret scrubbing regex automatically sanitizes any accidental API keys (`gsk_*`, `AIza*`, `Bearer *`) before persisting to disk.

---

## 6. TOP 12 PROFESSOR / VIVA DEFENSE QUESTIONS & ANSWERS

Be prepared for these questions during your review:

#### Q1: "Why did you use a 512-dimensional Hybrid TF-IDF vectorizer instead of calling OpenAI or HuggingFace BERT embeddings?"
> **Answer:** *"Three critical engineering reasons: First, **100% offline determinism and zero external dependencies**—the entire system builds, indexes, tests, and runs without internet connectivity or paid API quotas. Second, **reproducibility**—neural embeddings suffer from float non-determinism across different GPU/CPU architectures, whereas our hybrid character-plus-word TF-IDF produces bit-for-bit identical vectors on any machine. Third, **sub-word robustness**—character n-grams (3-5 chars) capture technical tokens (e.g. `DOC-004-C002`, `ndarray`, `top_k`) that standard neural tokenizers frequently split into out-of-vocabulary fragments."*

#### Q2: "How does your system prevent hallucinations mathematically?"
> **Answer:** *"Through a dual-threshold sufficiency floor. Before passing context to generation, we compute two metrics: maximum cosine similarity and query keyword coverage. If top similarity is below 0.20 OR keyword coverage in retrieved chunks is below 28%, the system triggers an immediate circuit breaker and emits the canonical refusal `INSUFFICIENT_EVIDENCE`. The LLM is never invoked on queries where evidence is absent."*

#### Q3: "What prevents the AI from auto-approving a marketing campaign budget?"
> **Answer:** *"The pipeline architecture strictly terminates proposal evaluation in the `AWAITING_APPROVAL` status. The recommendation engine only outputs a structured proposal report with facts, assumptions, and unknowns. There is literally no code path in `evaluate_proposal()` that transitions a record to `APPROVED`. Transitioning to `APPROVED` or `REJECTED` requires an explicit, authenticated call to `submit_approval()`, which demands a mandatory human reviewer name and justification notes."*

#### Q4: "What happens if a user tries to approve a proposal twice, or approve an already rejected proposal?"
> **Answer:** *"In Task 3 (DEFECT-003 remediation), we implemented terminal state protection in `RecordStore.record_decision()`. Both `APPROVED` and `REJECTED` are designated as immutable terminal states. If an approval or rejection is attempted on a record already in a terminal state, the system raises a `ValueError` and halts with exit code 1. Duplicate decisions are impossible."*

#### Q5: "How does the system handle conflicting information across documents?"
> **Answer:** *"Standard RAG systems either hallucinate by blending conflicting numbers or guess based on recency bias. AegisCore implements an active `ConflictDetector`. When two documents with opposing specifications (such as DOC-009 specifying pool=20 and DOC-020 specifying pool=50) both qualify as top retrieval candidates, the system halts generation, sets status to `CONFLICT_DETECTED`, and presents both contradictory excerpts side-by-side with citations for human resolution."*

#### Q6: "Why are sentence boundaries preserved during chunking?"
> **Answer:** *"Fixed-character chunking often slices sentences mid-word or mid-thought, creating incomplete clauses that degrade vector similarity and confuse LLMs. Our boundary-aware chunker uses regex lookbehind `(?<=[.!?])\s+` to detect natural punctuation boundaries within a 60-character sliding window, ensuring chunks end on complete grammatical sentences."*

#### Q7: "What is the difference between `workflow ask` and `workflow evaluate`?"
> **Answer:** *"`workflow ask` is for pure informational question-answering over corporate policies (e.g., 'What is the budget ceiling?'). It retrieves evidence, cites sources, and returns an answer without asking for a budget, creating records, or opening approval gates. `workflow evaluate` is for formal business proposals; it executes the full 7-stage governance audit, checks spend caps, surfaces unknowns, records the request in `records.json`, and stops at the human approval gate."*

#### Q8: "What does your deterministic replay command actually prove, and what does it NOT prove?"
> **Answer:** *"Replay takes the original proposal parameters, re-queries the current vector index, and compares the retrieved documents and recommended action against the historical record. This **proves** algorithmic consistency and evidence stability over time. However, as explicitly documented in our Task 3 security report, replay **does not prove the physical authenticity of the human reviewer**—it validates that the stored decision was logged, but cannot verify whether the human who entered their name had physical authority to do so."*

#### Q9: "How do you protect the system against prompt injection attacks?"
> **Answer:** *"Through four defensive layers: First, query length bounds (3 to 500 characters) reject buffer overflow attempts. Second, stage-4 cleaning strips HTML, XML, and markdown script tags. Third, strict prompt framing encloses retrieved context in tagged boundary markers and instructs the model to ignore any instructions found within the context. Fourth, our test suite includes 20 adversarial penetration tests verifying defense against 'ignore previous instructions', system prompt leaks, and unicode homoglyphs."*

#### Q10: "How do you ensure secrets or API keys are not leaked into logs or stored records?"
> **Answer:** *"`RecordStore` includes a regex secret sanitizer that scans all record JSON payloads before persisting them to disk. Any token matching patterns for Groq keys (`gsk_*`), Gemini keys (`AIza*`), xAI keys (`xai-*`), or HTTP Bearer tokens is automatically replaced with `[REDACTED_SECRET]`."*

#### Q11: "What are the 4 categories in your structured recommendation report?"
> **Answer:** *"In Task 2, proposals are synthesized into: 
> 1. **Verified Facts:** Hard evidentiary statements verified directly against policy documents with citations.
> 2. **Inferences:** Logical deductions derived from facts (e.g., $35k is compliant with $50k cap).
> 3. **Assumptions:** Working premises that must hold true for the campaign to succeed (e.g., ad platform auction stability).
> 4. **Unknowns:** Missing or fluctuating information (e.g., unspecified target personas, missing timeline, or auction price volatility)."*

#### Q12: "What is your test coverage and how quickly does the test suite run?"
> **Answer:** *"Our test suite consists of **126 automated tests** spanning boundary conditions, unit tests, integration pipelines, functional multi-domain workflows, regression tests, adversarial security tests, approval integrity tests, and replay parity tests. The entire suite executes in approximately **2.2 seconds** on a standard Windows laptop with a 100% pass rate."*

---

## 7. QUANTITATIVE PERFORMANCE PROOF POINTS

When presenting, show this table to demonstrate the mathematical rigor of your project:

| Metric | Measured Value | Standard / Requirement | Status |
| :--- | :--- | :--- | :--- |
| **Total Automated Tests** | **126 Tests** | 100% Passing | **VERIFIED** |
| **Test Execution Speed** | **2.17 seconds** | Sub-10 seconds | **VERIFIED** |
| **Benchmark Status Accuracy** | **100.0%** (25/25) | $\ge 90.0\%$ | **VERIFIED** |
| **Retrieval Success Rate** | **94.7%** (18/19) | $\ge 85.0\%$ | **VERIFIED** |
| **Failure Detection Rate** | **100.0%** (6/6) | 100.0% | **VERIFIED** |
| **Citation Validity Rate** | **100.0%** | 100.0% | **VERIFIED** |
| **Average Query Latency** | **14.1 ms** | $< 100\text{ ms}$ | **VERIFIED** |
| **Unified Document Count** | **26 Documents** | 26 Documents | **VERIFIED** |
| **Vector Index Passages** | **348 Chunks** | 348 Chunks | **VERIFIED** |
| **Vector Dimensionality** | **512 Dimensions** | 512 Dimensions | **VERIFIED** |
| **Vector Norm Equivalence** | $\|\mathbf{v}\|_2 = 1.0$ (Unit L2) | Dot-Product Equivalent | **VERIFIED** |
| **Adversarial Security Tests** | **20 / 20 Passed** | 0 Vulnerabilities | **VERIFIED** |
| **Approval Integrity Tests** | **12 / 12 Passed** | 0 Auto-approvals | **VERIFIED** |
| **Replay Parity Tests** | **7 / 7 Passed** | 100% Deterministic | **VERIFIED** |

