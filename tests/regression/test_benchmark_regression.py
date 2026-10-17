"""Regression tests for benchmark evaluation suite invariants."""
import pytest
from evidence_rag.evaluation import EvaluationRunner


def test_benchmark_regression_performance(indexed_pipeline, project_root):
    questions_file = project_root / "evaluation" / "questions.jsonl"
    results_dir = project_root / "evaluation" / "results"

    runner = EvaluationRunner(
        pipeline=indexed_pipeline,
        questions_path=str(questions_file),
        output_dir=str(results_dir)
    )

    summary = runner.run_benchmark()
    metrics = summary["metrics"]

    assert summary["total_questions"] >= 20
    # Mandatory benchmark acceptance invariants
    assert metrics["retrieval_success_rate"] >= 0.85
    assert metrics["status_accuracy"] >= 0.85
    assert metrics["failure_detection_rate"] >= 0.80
    assert metrics["citation_validity_rate"] == 1.0  # Zero hallucinated citations allowed
    assert metrics["average_latency_ms"] < 500.0   # Fast sub-second SLA
