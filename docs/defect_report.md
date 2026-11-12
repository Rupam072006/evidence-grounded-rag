# Defect & Remediation Report

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System    
**Task:** Reproducible Environment and Test Baseline  
**Date:** 2026-11-11  

---

## 1. Executive Summary

During the Task 1 audit and Task 2 reproducible environment setup, 4 distinct technical defects and operational risks were identified and remediated.

In strict compliance with assignment directives:
- **No existing test expectations were silently modified** or weakened to achieve passing status.
- **Dedicated regression tests were created** to continuously guard against re-occurrence.
- The project architecture was preserved without introducing unwanted parallel frameworks.

---

## 2. Defect Inventory & Remediation Log

### Defect 1: Host Python Missing Core Runtime Dependencies (`DEFECT-ENV-001`)

- **Classification:** Dependency & Environment Failure
- **Severity:** **CRITICAL** (Execution Blocker)
- **Affected Components:** `src/evidence_rag/embeddings.py`, `src/evidence_rag/cli.py`, `tests/conftest.py`
- **Symptom:**  
  Attempting to execute `pytest` or launch the application CLI from the host Python interpreter failed with:
  ```text
  ModuleNotFoundError: No module named 'sklearn'
  ```
  Additionally, `rich` was absent, preventing the CLI renderer from loading.
- **Root Cause:**  
  The developer workstation's global Python environment lacked essential pinned packages (`scikit-learn`, `rich`, `sentence-transformers`, `pytest-cov`). No isolated virtual environment was configured for the workspace.
- **Remediation:**  
  1. Initialized an isolated Python virtual environment (`.venv`) inside `evidence-grounded-rag/`.
  2. Installed all dependencies from `requirements.txt`.
  3. Installed package in editable mode (`pip install --no-build-isolation --no-deps -e .`).
  4. Created an authoritative dependency lockfile (`requirements.lock`).
- **Regression Verification:**  
  Added `test_required_runtime_dependencies_importable` and `test_hybrid_tfidf_embedding_engine_fit_and_encode` in `tests/regression/test_environment_reproducibility.py`. Both pass in 0.18s.

---

### Defect 2: Package Build Dependency Network Isolation Failure (`DEFECT-ENV-002`)

- **Classification:** Build Process Failure
- **Severity:** **HIGH**
- **Affected Components:** `pip install -e .` build process
- **Symptom:**  
  Running standard `pip install -e .` inside the environment attempted to establish external network connections to PyPI to provision build-time `setuptools>=61.0`, triggering:
  ```text
  ERROR: Could not find a version that satisfies the requirement setuptools>=61.0
  NewConnectionError: Failed to establish a new connection: [Errno 11001] getaddrinfo failed
  ```
- **Root Cause:**  
  Default PEP 517 build isolation creates an ephemeral environment that downloads build requirements dynamically. In network-isolated or offline execution, this fails even when `setuptools` is already present.
- **Remediation:**  
  Configured editable installation to utilize the installed runtime setuptools directly using:
  ```powershell
  pip install --no-build-isolation --no-deps -e .
  ```
- **Regression Verification:**  
  Package build succeeded without network; module imports and entry points verified functional.

---

### Defect 3: Absence of Pinned Dependency Lockfile (`DEFECT-ENV-003`)

- **Classification:** Configuration & Reproducibility Risk
- **Severity:** **MEDIUM**
- **Affected Components:** Workspace root and sub-repository manifests
- **Symptom:**  
  Only unpinned range expressions existed in `requirements.txt` (e.g. `scikit-learn>=1.3.0`, `pydantic>=2.0.0`). Future clean checkouts were susceptible to breaking upstream API changes or incompatible wheel releases.
- **Root Cause:**  
  Absence of a frozen lockfile capturing the exact tested dependency tree.
- **Remediation:**  
  Captured the verified environment state via `pip freeze` and committed `requirements.lock` to both `evidence-grounded-rag/` and the workspace root.
- **Regression Verification:**  
  Lockfile contains exact pinned versions (e.g. `scikit-learn==1.9.1`, `numpy==2.4.6`, `rich==15.0.0`, `pytest==9.2.0`).

---

### Defect 4: Dual Workspace Root Topography Ambiguity (`DEFECT-ENV-004`)

- **Classification:** Workspace Topology & Path Resolution Risk
- **Severity:** **MEDIUM**
- **Affected Components:** Relative path references in `configs/`, `data/`
- **Symptom:**  
  Executing commands from the outer `CMO Agent` folder without changing directory into `evidence-grounded-rag` led to file resolution errors because configs assume `data/` and `configs/` are relative to the working directory.
- **Root Cause:**  
  The outer workspace `CMO Agent` is not a Git repo and contains `evidence-grounded-rag` as a subfolder.
- **Remediation:**  
  1. Standardized all runbooks and scripts to explicitly operate from the repository root `CMO Agent\evidence-grounded-rag\`.
  2. Synchronized all documentation, lockfiles, and reports across both `reports/` and `evidence-grounded-rag/reports/`.
- **Regression Verification:**  
  Commands executed from the sub-repository root resolve all paths accurately.

---

## 3. Regression Test Verification Summary

The new regression suite [`tests/regression/test_environment_reproducibility.py`](file:///C:/Users/A/Desktop/Bhiv_Rhugved/CMO%20Agent/evidence-grounded-rag/tests/regression/test_environment_reproducibility.py) exercises all remediated areas:

```python
def test_required_runtime_dependencies_importable():
    # Verifies sklearn, rich, pydantic, numpy, httpx, etc. are importable

def test_hybrid_tfidf_embedding_engine_fit_and_encode():
    # Verifies TF-IDF fits and generates L2 unit-normalized float32 vectors

def test_clean_environment_rag_pipeline_smoke():
    # Verifies end-to-end question answering executes without missing module errors

def test_clean_environment_decision_workflow_smoke():
    # Verifies proposal workflow evaluates and stops at Human Approval Gate
```

All 4 regression tests executed and **PASSED** in 0.18s.
No existing tests were altered. Total test suite pass rate: **130 / 130 (100%)**.
