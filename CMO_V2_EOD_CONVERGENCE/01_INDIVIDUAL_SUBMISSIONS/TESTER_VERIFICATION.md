# Independent QA Verification Report — CMO Agent V2 EOD Convergence

| Field | Value |
|---|---|
| **Project** | CMO Agent V2 – EOD Convergence |
| **Independent Tester / Lead** | **Samsoorya Rajakumar** (Independent QA / Verification Lead) |
| **Testing Date / Window** | 2026-11-19, approx. 12:43–12:52 IST (+05:30). Matrix re-read at 13:02 IST after upstream commit `b91789d`. |
| **Repository (Actual)** | `C:\Users\pc44\evidence-grounded-rag`, origin `https://github.com/Rupam072006/evidence-grounded-rag.git` |
| **Branch** | `main` (up to date with `origin/main`) |
| **Commit Tested** | `0df099017fabdd1820cc2e681f502913f4dca8fe` (parent `db032d6`; code identical; docs-only diff) |
| **Environment** | Windows 11 (`Windows-11-10.0.26200`), Python `3.13.7`, pytest `8.3.3` (interpreter note: global Python 3.13) |
| **Scope** | Phases 1–10 of the tester brief |
| **Final Verdict** | **`CONDITIONAL PASS`** (non-production only) |
| **Conservative Score** | **`63 / 100`** |

---

## 1. Executive Summary & Verdict

The automated baseline reproduces cleanly: `python -m pytest tests -q --tb=short` gives **136 passed, 0 failed, 0 errors, 0 skipped, 116 warnings, exit code 0 in 3.96 s**. The 16 targeted approval tests also pass in 0.44 s.

The package is **honest about what is implemented**. There is no FastAPI app, no router, no Dockerfile, no MASTERDB client, and no TANTRA/VAJRA auth in `src/evidence_rag/`. Path B is correctly classified as `PROPOSED` or `BLOCKED`, the integration matrix does not claim any `VERIFIED LIVE` row, and the 36-capability registry is labeled `PROPOSED`.

Independent probing found problems the team's evidence does not show. They sit mostly in the approval and governance logic and in the UX prototype:
1. `DEF-REPRO-001` is reproduced exactly: **9 failed, 27 errors, and 100 passed** when pytest is run from another directory (relative path resolution).
2. The reviewer-placeholder gate is trivially bypassable (`QA-001`, High). `prof_evaluator`, `PROF_EVALUATOR`, `Prof_Evaluator` + zero-width, `.`, and `Anonymous` were all accepted.
3. A record in `INSUFFICIENT_EVIDENCE` can be moved to `APPROVED` (`QA-002`, High).
4. The approve/reject history event carries no `trace_id` (`QA-003`, Medium).
5. Unhandled corrupt store parse error causes prior records to be discarded on save (`QA-004`, Medium).
6. UX prototype has self-XSS via unescaped `innerHTML` (`QA-005`, Medium).
7. UX validation diverges from backend validation (`QA-006`, Medium).

**Overall Verdict:** **`CONDITIONAL PASS`** for accepting the package as a local, non-production, simulated convergence deliverable. **Conservative score: 63/100.** Nothing here supports production readiness.

---

## 2. Test Execution & Reproduction Summary

| Test ID | Test Area | Expected Result | Actual Result | Status |
|:---:|---|---|---|:---:|
| **T-01** | Git repo / branch | `evidence-grounded-rag`, `main` | Repo `evidence-grounded-rag`, branch `main` | **PASS** |
| **T-02** | Commit | `db032d6` | HEAD `0df0990`. `db032d6` is direct parent; zero code diff. | **PASS** |
| **T-03** | Working tree | clean | clean at start | **PASS** |
| **T-04** | Python version | `3.11.9` | `3.13.7` | **PARTIAL** (env mismatch) |
| **T-05** | Full test suite | 136 passed | **136 passed, 0 failed, 116 warnings, 3.96s, exit 0** | **PASS** |
| **T-06** | Targeted approval tests | all pass | **16 passed (4 acceptance + 12 integrity), 0.44s** | **PASS** |
| **T-07** | Suite leaves repo clean | no tracked file changes | 3 tracked files modified by test run (`QA-012`) | **FAIL** (restored) |
| **T-08** | Run from other CWD (`DEF-REPRO-001`) | same result | **9 failed, 27 errors, 100 passed** | **FAIL** (confirmed defect) |
| **T-10** | LinkedIn proposal JSON | `AWAITING_APPROVAL`, `approval: null` | Status `AWAITING_APPROVAL`, `approval: null`, zero execution event | **PASS** |
| **T-11** | Default reviewer sample | rejected | `Prof_Evaluator` rejected (`ValueError`), governance: BLOCKED | **PASS** |
| **T-12** | Blank reviewer sample | rejected | `""` rejected (`ValueError: Reviewer identity cannot be blank`) | **PASS** |
| **T-13** | Approved record | named reviewer, timestamp | Recorded `Pratik Bhuwad - CMO Product Owner`. Lacks `trace_id` in event (`QA-003`). | **PARTIAL** |
| **T-14** | Duplicate approval | blocked | `ValueError: Request already finalized` | **PASS** |
| **T-15** | Linear TV abstention | `INSUFFICIENT_EVIDENCE`, `null` metrics | Correctly abstains with `null` recommendations/metrics (`DEFECT-SEMANTIC-001`) | **PASS** |
| **T-16** | Trace ID consistency | single ID | `1833C82E` in JSON/log; `6C7BDA95` in older prose (`DEF-DOC-001` confirmed) | **FAIL** (confirmed) |
| **T-17** | Reviewer gate robustness | placeholder variants rejected | 5 of 6 variants accepted (`QA-001`) | **FAIL** (High defect) |
| **T-18** | Approval of abstained record | blocked | Abstained record accepted to `APPROVED` (`QA-002`) | **FAIL** (High defect) |
| **T-20** | Path B: FastAPI/Docker | absent (honest classification) | None found in repo; honestly labeled `PROPOSED` | **PASS** (honest) |
| **T-21** | MASTERDB adapter in runtime | absent | None found; honestly labeled `PROPOSED`/`BLOCKED` | **PASS** (honest) |
| **T-23** | UX five screens / navigation | all work | Works end-to-end (`SIMULATED`) | **PASS** |
| **T-24** | UX commercial safety | variance warning, abstention | Variance and abstention PASS | **PASS** |
| **T-25** | UX controls | pause/mute/revoke/inspect/delete | All functional. Pause is cosmetic (`QA-010`). | **PASS** / **PARTIAL** |
| **T-26** | UX security | safe rendering, zero external calls | **Self-XSS executed via unescaped innerHTML (`QA-005`). Zero external calls.** | **FAIL** (Medium/High) |
| **T-28** | Capability registry | 36 caps, 6 domains, 15 fields | 36 unique IDs, 6x6 domains, 15 populated columns, zero empty cells | **PASS** (structure) |
| **T-29** | Registry: no auto publish/spend | none | None claimed; zero autonomous spend | **PASS** |
| **T-32** | Integration matrix | 6 allowed statuses | Strictly uses allowed labels. Addressed in commit `b91789d`. | **PASS** |

---

## 3. Conservative Quality Score Breakdown (63 / 100)

| Category | Weight | Awarded | Rationale |
|---|:---:|:---:|---|
| **Automated test baseline** | 20 | **17** | 136/136 and 16/16 reproduced. -3 for python version mismatch, unclean interpreter, sklearn pickle mismatch, tests mutating tracked files. |
| **Reproducibility (CWD)** | 10 | **3** | `DEF-REPRO-001` reproduced. The suite fails 36 of 136 from another directory. |
| **Approval and commercial integrity** | 20 | **11** | Core path works and samples are consistent. -9 for `QA-001`, `QA-002`, `QA-003`, `QA-004`, and synthetic sample set. |
| **Architecture honesty (Path B)** | 10 | **9** | Classification is accurate and nothing proposed is claimed as live. -1 for unlisted direct-LLM path (`QA-016`). |
| **UX prototype** | 10 | **5** | Flows work. XSS (`QA-005`), validation mismatch (`QA-006`), invalid budgets (`QA-007`), modal accessibility (`QA-009`). |
| **Registry and orchestration** | 10 | **7** | Structurally complete (36/6/15, no autonomy). -3 for generic test references and design claims that code contradicts. |
| **Integration matrix** | 10 | **6** | Labels conservative. -4 for missing Path B and dependency rows, count mismatch (addressed in `b91789d`), and unverifiable MASTERDB local evidence. |
| **Defect and evidence consistency** | 10 | **5** | Register is honest about blockers. -5 for trace-ID mismatch, `DEF-DOC-002` unreproducible. |
| **Total** | **100** | **63** | **CONDITIONAL PASS. No credit given for proposed capabilities or unverified cloud environments.** |

---

## 4. Key Defects Identified by Tester (QA-001 to QA-016)

- **`QA-001` (High):** Reviewer placeholder gate is exact-match only (`workflow.py:443`, `cli.py:571,630`). Case variants (`prof_evaluator`, `PROF_EVALUATOR`, `Anonymous`, `.`) were accepted and recorded.
- **`QA-002` (High):** `record_store.record_decision` accepts a decision on non-approvable statuses (only logs warning on `INSUFFICIENT_EVIDENCE -> APPROVED`).
- **`QA-003` (Medium):** `HUMAN_APPROVED` / `HUMAN_REJECTED` history events have no `trace_id`.
- **`QA-004` (Medium):** Unhandled corrupt store parse error causes `_read_store` to return `{}` and overwrite prior records on next save.
- **`QA-005` (Medium / High):** UX self-XSS: reviewer and notes interpolated unescaped into `innerHTML` (lines 984–985).
- **`QA-006` (Medium):** UX/backend validation mismatch (placeholders, blank notes).
- **`QA-007` (Low):** UX accepts budget 0 and negative (-500) and outputs "APPROVE".
- **`QA-008` (Medium):** Budget >$50k gets "REJECT/ESCALATE" recommendation but approval form remained enabled.
- **`QA-009` (Medium):** Modal lacks Escape key handling and focus trap.
- **`QA-010` (Low):** "Pause AI" in UX was cosmetic only.
- **`QA-011` (Medium):** Environment differs from brief (Python 3.13 vs 3.11).
- **`QA-012` (Medium):** Test suite mutates tracked files (`records.json`, etc.).
- **`QA-013` (Low):** Stale samples beside V2 samples in `evidence_packet/`.
- **`QA-014` (Medium):** Citations have `quote: null` and truncated chunk statements.
- **`QA-015` (Medium):** Docs vs code alignment ("authenticated" reviewer vs unauthenticated free text).
- **`QA-016` (Medium - Opt-in):** `generation.py` contains direct Gemini/Groq/xAI client calls (opt-in).

---

## 5. Priority Fix Recommendations

- **P1 (Before Any Promotion or Staging Integration):**
  1. Fix `QA-001`: Normalize reviewer identity (NFKC, strip whitespace/zero-width, casefold) and share one validator between CLI and workflow.
  2. Fix `QA-002`: Block approval on any status other than `AWAITING_APPROVAL` or `RECOMMENDATION_READY`.
  3. Fix `DEF-REPRO-001`: Resolve paths from project root (`Path(__file__)`), removing CWD dependency.
  4. Fix `QA-005`: Escape or use `textContent` in the UX prototype and add CSP meta tag.
- **P2 (Hardening & Convergence):**
  5. Fix `QA-003`: Copy `record.trace_id` into every history event.
  6. Fix `QA-004`: Fail closed on corrupt records parse error + file locking.
  7. Fix `QA-006`–`QA-010`: Align UX validations, enforce budget $> 0$, block $> \$50k$ without exception, add modal focus handling.

---

## 6. Tester Declaration

I, **Samsoorya Rajakumar (Tester)**, declare that the results in this report come from independent testing of the repository state described in Section 1. Every PASS, FAIL, and PARTIAL here is backed by a command I ran or a file I read. Evidence is saved in `CMO_V2_EOD_CONVERGENCE/01_INDIVIDUAL_SUBMISSIONS/tester_evidence/`.
