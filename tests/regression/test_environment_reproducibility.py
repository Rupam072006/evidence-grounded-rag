"""Regression tests verifying environment reproducibility and core package imports (Task 2)."""
import sys
import importlib
import pytest


def test_required_runtime_dependencies_importable():
    """Verify that all core runtime and CLI dependencies are importable."""
    required_modules = [
        "sklearn",
        "sklearn.feature_extraction.text",
        "rich",
        "rich.console",
        "rich.panel",
        "rich.table",
        "pydantic",
        "numpy",
        "yaml",
        "click",
        "httpx",
        "dotenv",
        "evidence_rag",
        "evidence_rag.pipeline",
        "evidence_rag.workflow",
        "evidence_rag.record_store",
        "evidence_rag.embeddings",
        "evidence_rag.retrieval"
    ]
    for mod_name in required_modules:
        mod = importlib.import_module(mod_name)
        assert mod is not None, f"Module {mod_name} failed to import"


def test_hybrid_tfidf_embedding_engine_fit_and_encode():
    """Verify HybridTfidfEmbeddingEngine fits and encodes unit vectors."""
    from evidence_rag.embeddings import HybridTfidfEmbeddingEngine
    import numpy as np

    engine = HybridTfidfEmbeddingEngine(dimension=128)
    sample_texts = [
        "Marketing budget policy with $50,000 spend cap.",
        "Technical documentation regarding python exception handling.",
        "Conversion rate optimization and CTR metrics analysis."
    ]
    engine.fit(sample_texts)
    assert engine.is_fitted

    vectors = engine.encode(sample_texts)
    assert vectors.shape[0] == 3
    assert vectors.shape[1] == len(engine.vectorizer.vocabulary_)
    assert vectors.shape[1] <= 128
    assert vectors.dtype == np.float32

    # Verify unit normalization (L2 norm == 1.0)
    norms = np.linalg.norm(vectors, axis=1)
    np.testing.assert_allclose(norms, np.ones(3, dtype=np.float32), rtol=1e-5)


def test_clean_environment_rag_pipeline_smoke():
    """Smoke test ensuring RAGPipeline executes query without missing module errors."""
    from evidence_rag.pipeline import RAGPipeline
    from evidence_rag.schemas import ResponseStatus

    pipeline = RAGPipeline()
    pipeline.ensure_index()
    response = pipeline.query("What character encoding is mandatory for all incoming documents in AegisCore?")
    assert response.status == ResponseStatus.ANSWERED
    assert response.confidence > 0.0
    assert len(response.citations) > 0
    assert response.model_name == "deterministic_mock"


def test_clean_environment_decision_workflow_smoke():
    """Smoke test ensuring DecisionWorkflow evaluates proposals and pauses at approval gate."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowRequest, WorkflowStatus

    wf = DecisionWorkflow()
    req = WorkflowRequest(
        request_id="SMOKE-TEST-001",
        title="Smoke Test Proposal",
        proposal_text="Allocate $20,000 across digital acquisition channels targeting 250 conversions.",
        department="Marketing",
        requested_budget=20000.0,
        submitted_by="qa_engineer"
    )
    record = wf.evaluate_proposal(req)
    assert record.status == WorkflowStatus.AWAITING_APPROVAL
    assert record.recommendation is not None
    assert record.recommendation.recommended_action == "APPROVE"
    assert record.approval is None

