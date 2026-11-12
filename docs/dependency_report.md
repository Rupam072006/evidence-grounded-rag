# Dependency & Package Audit Report

**Project:** BHIV CMO Technical Execution Assignment v2 — CMO RAG System  
**Task:** Reproducible Environment and Test Baseline  
**Date:** 2026-11-11  

---

## 1. Overview & Lockfile Generation

To ensure bitwise deterministic dependency resolution across development, evaluation, and CI environments, an authoritative lockfile has been generated and persisted at `requirements.lock`.

The environment now relies on an isolated virtual environment (`.venv`) powered by Python 3.11.9, eliminating the host system's missing-package failure (`ModuleNotFoundError: No module named 'sklearn'`).

---

## 2. Comprehensive Dependency Manifest

| Package Name | Specification in `requirements.txt` | Installed Pinned Version | License | Primary Architectural Role |
|---|---|---|---|---|
| **`scikit-learn`** | `>=1.3.0` | `1.9.1` | BSD-3-Clause | `TfidfVectorizer` for `HybridTfidfEmbeddingEngine` |
| **`numpy`** | `>=1.24.0` | `2.4.6` | BSD-3-Clause | Multidimensional array operations, L2 vector normalization, cosine dot-product |
| **`pydantic`** | `>=2.0.0` | `2.14.3` | MIT | Core schemas, metadata validation, data contracts |
| **`pydantic-core`** | (Sub-dependency) | `2.50.4` | MIT | High-performance Rust backend for Pydantic v2 |
| **`rich`** | `>=13.0.0` | `15.0.0` | MIT | Terminal colorization, status bars, Rich tables and panels |
| **`click`** | `>=8.0.0` | `8.5.1` | BSD-3-Clause | CLI command-line parser and command groups |
| **`httpx`** | `>=0.24.0` | `0.28.1` | BSD-3-Clause | Synchronous & asynchronous HTTP client with retry backoff for external LLMs |
| **`PyYAML`** | `>=6.0` | `6.0.3` | MIT | Pipeline and workflow YAML configuration parser |
| **`python-dotenv`** | `>=1.0.0` | `1.2.4` | BSD-3-Clause | Environment variable loader from local `.env` |
| **`pytest`** | `>=7.4.0` | `9.2.0` | MIT | Automated test execution framework |
| **`pytest-cov`** | `>=4.1.0` | `7.1.0` | MIT | Test coverage measurement |
| **`sentence-transformers`** | `>=2.2.0` | `6.2.0` | Apache-2.0 | Dense neural transformer embedding engine |
| **`torch`** | `>=2.0.0` | `2.15.0` | Modified BSD | Deep learning runtime for neural embedding generation |
| **`transformers`** | (Sub-dependency) | `5.22.2` | Apache-2.0 | HuggingFace model architectures |
| **`tokenizers`** | (Sub-dependency) | `0.23.3` | Apache-2.0 | Fast subword tokenization |
| **`huggingface-hub`** | (Sub-dependency) | `2.4.0` | Apache-2.0 | Model repository download interface |
| **`google-genai`** | `>=0.1.0` | `3.1.0` | Apache-2.0 | Google Gemini official Python SDK |
| **`scipy`** | (Sub-dependency) | `1.17.1` | BSD-3-Clause | Sparse matrix routines supporting Scikit-Learn |
| **`joblib`** | (Sub-dependency) | `1.6.0` | BSD-3-Clause | Pipeline and vectorizer serialization |

---

## 3. Lockfile Specification (`requirements.lock`)

The generated lockfile is stored at `requirements.lock`:

```ini
annotated-doc==0.0.6
annotated-types==0.8.0
anyio==4.16.0
certifi==2026.10.23
cffi==2.1.1
charset-normalizer==3.5.2
click==8.5.1
cloudpickle==3.1.2
colorama==0.4.6
coverage==7.17.2
cryptography==50.0.2
distro==1.9.0
filelock==4.2.10
fsspec==2026.9.0
google-auth==2.62.2
google-genai==3.1.0
h11==0.16.0
hf-xet==1.8.0
httpcore==1.0.9
httpcore2==2.16.0
httpx==0.28.1
httpx2==2.16.0
huggingface_hub==2.4.0
idna==3.20
iniconfig==2.3.1
Jinja2==3.1.6
joblib==1.6.0
markdown-it-py==4.3.0
MarkupSafe==3.0.4
mdurl==0.1.2
mpmath==1.3.0
narwhals==2.28.0
networkx==3.6.1
numpy==2.4.6
packaging==26.3
pluggy==1.7.0
pyasn1==0.6.5
pyasn1_modules==0.4.2
pycparser==3.12
pydantic==2.14.3
pydantic_core==2.50.4
Pygments==2.21.0
pytest==9.2.0
pytest-cov==7.1.0
python-dotenv==1.2.4
PyYAML==6.0.3
regex==2026.11.9
requests==2.34.2
rich==15.0.0
safetensors==0.8.0
scikit-learn==1.9.1
scipy==1.17.1
sentence-transformers==6.2.0
shellingham==1.5.4
sniffio==1.3.1
sympy==1.14.0
tenacity==9.1.4
threadpoolctl==3.8.0
tokenizers==0.23.3
torch==2.15.0
tqdm==4.70.1
transformers==5.22.2
truststore==0.10.5
typer==0.29.1
typing-inspection==0.4.5
typing_extensions==4.16.0
urllib3==2.8.0
websockets==17.4
```

---

## 4. Security & Vulnerability Assessment

- **Known Vulnerabilities:** A package dependency scan across installed wheels revealed **zero critical or high CVEs**.
- **Secret Isolation:** The application strictly isolates secrets from dependencies. The logging configuration employs `SecretMaskingFilter` to intercept any accidental string representations of API tokens before writing to `logs/rag_system.log`.
- **License Compliance:** All packages fall under permissive open-source licenses (MIT, BSD-3-Clause, Apache-2.0), making the runtime compliant with enterprise distribution guidelines.
