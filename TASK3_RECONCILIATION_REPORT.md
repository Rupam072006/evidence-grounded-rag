# TASK3_RECONCILIATION_REPORT.md
## AegisCore — Historical Reconciliation Report
**Date:** 2026-11-05  
**Commit:** 3703c514418f76586a08a30cf341c6d14f441fff  
**Evidence:** `evidence_packet/reconciliation_summary.json`

---

## Reconciliation Summary Table

| Area | Historical Claim | Verified Value | Difference | Root Cause | Correction | Evidence |
|---|---|---|---|---|---|---|
| Test count | 46 (T1), 47 (T2 audit), 55/65 (reports), 77 (T2 end) | **116** | +70 from T1 baseline | Tests grew over lifecycle: 46 (T1) -> 47 (T2 audit) -> 77 (T2) -> 116 (T3 final) | Canonical count 116 established and verified | test_execution_summary.json, test_inventory.csv |
| Benchmark status accuracy | 88% (22/25) Task 1; 100% claimed later | **100.0% (25/25) verified** | Different corpus states | T1 had 20 docs; T2/T3 have 26 docs, expanding answerability. Mock mode is 100% deterministic. | Both results correct for their corpus versions | benchmark_reconciliation.json, latest_evaluation_run.json |
| Corpus document count | 20 (T1), 24 (T2 baseline) | **26** | +6 from T1, +2 from T2 claim | DOC-024, DOC-025, DOC-026 added beyond original 4-doc plan | Canonical count 26 from manifest.json | corpus_index_manifest.json |
| Chunk count | 301 | **348** | +47 | 6 additional marketing documents chunked | Index rebuilt with 26 docs | corpus_index_manifest.json |
| Vector count | 299 (2 missing) | **348 (0 missing)** | Historic 2-vector gap resolved | Earlier build bug; index rebuilt from full 26-doc corpus | No missing vectors in current index | corpus_index_manifest.json |
| Embedding dimensions | 256 (some docs), 512 (arch doc) | **512** | Documentation inconsistency | 256 was a draft spec; actual TF-IDF engine uses 512-dim SVD | Verified 512; all docs corrected | vectors.npy shape=(348,512) |
| httpx dependency | Missing in early commit | **Present: httpx>=0.24.0** | Fixed in T2 audit | Added during ab16a4c | Already fixed; both requirements files updated | requirements.txt, pyproject.toml |
| Corpus fingerprint | May hash only first doc | **Hashes ALL docs (sorted join)** | Historical concern was incorrect | Implementation uses load_corpus() → all docs | No fix needed; verified correct | pipeline.py:compute_corpus_fingerprint() |
| Index failure status | Incorrect status | **INDEX_UNAVAILABLE present** | Fixed in T2 audit | Status added to both ResponseStatus and WorkflowStatus enums | Already fixed; regression test passes | schemas.py, workflow_schemas.py |
| Unicode citation parsing | Bug reported | **Fixed and tested** | Fixed in T2 audit | Unicode normalization in cleaning.py + safe_text() in cli.py | test_alternate_citation_delimiters PASSED | test_citation_validation.py |
| HTTP 429 handling | Missing in early version | **Bounded backoff implemented** | Fixed in T2 audit | generation.py has retry with max_retries config | Already implemented | generation.py |
| Contradiction detection | Hardcoded pairs only | **Extensible + heuristic** | Fixed in T2 audit | register_conflict_pair() + numerical parameter detection | Already improved | conflict_detection.py |

---

## Detailed Reconciliation

### DISC-001 — Test Count Reconciliation

**Historical claims:**
- Commit `fbc65ff` (Task 1): 46 tests
- Commit `ab16a4c` (Task 2 audit): 47 tests
- Later Task 2 reports: 55, 65, and 77 tests

**Verified value:** **116 tests** from `pytest --collect-only` across 24 test files on HEAD commit.

**Root cause:** Test counts grew steadily across all development and audit phases:
- 46 tests: Task 1 initial baseline (unit, integration, boundary, and functional)
- +1 test: Task 2 Day 1 audit defect regression fix (commit `ab16a4c`) -> 47 tests
- +12 tests: `test_task2_multi_domain.py` (cross-domain and multi-domain evaluation)
- +10 tests: `test_day3_scenarios.py` (Task 2 Day 3 scenario testing)
- +8 tests: `test_workflow.py` (decision-support workflow and approval gate) -> 77 tests
- +12 tests: `tests/task3/test_task3_approval_integrity.py` (human approval integrity & duplicate prevention)
- +20 tests: `tests/task3/test_task3_security.py` (adversarial scenarios S01 through S20)
- +7 tests: `tests/task3/test_task3_replay.py` (proposal reconstruction and audit replay)
- **Total: 77 + 39 = 116 tests** (all 116 PASSED).

The 55 and 65 figures cited in intermediate notes were preliminary counts before all functional files were committed.

**Status: RESOLVED**

---

### DISC-002 — Benchmark Metrics Reconciliation

**Historical claims:**
- Retrieval: 100%, Status accuracy: 88% (22/25) — Task 1 (20-doc corpus)
- Later claim: 100% deterministic evaluation

**Verified values:**
- Retrieval Success Rate: **94.7%** (18/19 applicable questions retrieved target docs)
- Status Accuracy: **100.0%** (25/25 status match across all expected statuses)
- Failure Detection Rate: **100.0%** (8/8 unanswerable/negative queries refused)
- Citation Validity Rate: **100.0%** (45/45 citations verified against candidate pool)
- Average Latency: **33.7 ms**

**Explanation:**
The 88% figure (22/25) was real and accurate for the 20-document Task 1 corpus; three questions queried marketing topics that were not yet indexed. Once the six marketing documents (`DOC-021` to `DOC-026`) were added in Task 2 and the index was rebuilt, those questions became answerable. The "100% deterministic evaluation" claim in Task 2 referred to the mock generator's deterministic sentence selection. In the full 25-question re-run under Task 3, all 25 questions match their expected status. Both historical 88% and current 100% are accurate for their respective corpus versions.

**Status: RESOLVED**

---

### DISC-003 — Corpus Document Count Reconciliation

| Phase | Planned | Actual |
|---|---|---|
| Task 1 | 20 technical docs | DOC-001 to DOC-020 (20 docs) ✓ |
| Task 2 | +4 marketing docs = 24 total | +6 marketing docs = 26 total |
| Task 3 current | 26 | 26 ✓ |

The original Task 2 plan specified 4 marketing documents. Implementation added 6:
- DOC-021: Campaign proposal
- DOC-022: Budget policy  
- DOC-023: Performance metrics
- DOC-024: Influencer policy (standard)
- DOC-025: Influencer policy (restricted) — intentional conflict pair
- DOC-026: Incomplete proposal

**Status: RESOLVED**

---

### DISC-004 & DISC-005 — Chunk/Vector Count Reconciliation

| Metric | Historical | Current |
|---|---|---|
| Chunk count | 301 | **348** |
| Vector count | 299 | **348** |
| Missing vectors | 2 | **0** |
| Orphan vectors | unknown | **0** |

The historical 301/299 figures were from an index built with fewer documents. After Task 2 corpus expansion and index rebuild with all 26 documents, the count became 348 chunks with 348 corresponding vectors. The 2-vector discrepancy was resolved during index rebuild.

**Status: RESOLVED**

---

### DISC-006 — Git and Documentation Consistency

**Git history (chronological):**

```
f36dfef — initial release
c25bf9c — Grok/Groq online generator support
7748d84 — enterprise README + flowcharts
fbc65ff — Task 1 complete: 20 docs, 46 tests
ab16a4c — Task 2 Day 1 audit: 6 defect fixes, 47 tests
141ef13 — Task 2 Day 2: decision-support workflow
1a189f1 — Task 2 Day 3: CLI exposure, staleness check
139ba6a — Task 2 Day 4: benchmark, evaluation, review packet
3703c51 — README rewrite: comprehensive demo guide (HEAD)
```

**Key observation:** Marketing documents DOC-021 to DOC-026 exist on disk but were never committed to git (they appear in `git status` as untracked files). This is a discrepancy — the documents exist and are indexed but are not tracked in version control.

**Correction required:** Add marketing documents to git.

---

## Evidence Files

All reconciliation data is in `evidence_packet/reconciliation_summary.json`.

| File | Contents |
|---|---|
| `reconciliation_summary.json` | 11 discrepancy records with status, root cause, evidence |
| `corpus_index_manifest.json` | Verified document/chunk/vector counts and fingerprint |
| `test_execution_summary.json` | Verified test count: 116 (77 original + 39 new) |
| `clean_test_output.txt` | Full pytest -v output |

