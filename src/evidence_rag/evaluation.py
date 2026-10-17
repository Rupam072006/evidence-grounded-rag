"""Evaluation harness, benchmark runner, and metric computation engine."""
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from evidence_rag.config import RAGConfig, load_config
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.schemas import ResponseStatus
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.evaluation")


class EvaluationRunner:
    """Executes evaluation benchmarks and computes rigorous empirical metrics."""

    def __init__(
        self,
        pipeline: Optional[RAGPipeline] = None,
        questions_path: str = "evaluation/questions.jsonl",
        output_dir: str = "evaluation/results"
    ):
        self.pipeline = pipeline or RAGPipeline()
        self.questions_path = Path(questions_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_questions(self) -> List[Dict[str, Any]]:
        """Load benchmark questions from JSONL file."""
        if not self.questions_path.exists():
            raise FileNotFoundError(f"Questions file not found at: {self.questions_path}")

        questions = []
        with open(self.questions_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    record = json.loads(line_str)
                    questions.append(record)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_no} in {self.questions_path}: {e}")

        logger.info(f"Loaded {len(questions)} evaluation questions from {self.questions_path}")
        return questions

    def run_benchmark(self) -> Dict[str, Any]:
        """Execute all questions and evaluate performance against criteria."""
        questions = self.load_questions()
        results_list = []

        total_retrieval_applicable = 0
        retrieval_success_count = 0
        status_match_count = 0
        negative_cases_count = 0
        negative_cases_detected = 0
        total_citations = 0
        valid_citations = 0
        total_latency_ms = 0.0

        for q_record in questions:
            qid = q_record["question_id"]
            query_text = q_record["question"]
            category = q_record.get("category", "general")
            expected_status = q_record.get("expected_status")
            expected_sources = set(q_record.get("expected_sources", []))
            expected_behaviour = q_record.get("expected_behaviour", "")

            # Execute pipeline
            response = self.pipeline.query(query_text)
            total_latency_ms += response.latency_ms

            # 1. Retrieval evaluation
            retrieved_doc_ids = set(response.source_document_ids)
            retrieval_hit = False
            if expected_sources:
                total_retrieval_applicable += 1
                overlap = expected_sources.intersection(retrieved_doc_ids)
                if overlap:
                    retrieval_hit = True
                    retrieval_success_count += 1

            # 2. Status match evaluation
            actual_status_str = response.status.value
            status_matched = (actual_status_str == expected_status)
            if status_matched:
                status_match_count += 1

            # 3. Negative case evaluation
            is_negative_case = expected_status in (
                ResponseStatus.INSUFFICIENT_EVIDENCE.value,
                ResponseStatus.CONFLICT_DETECTED.value,
                ResponseStatus.INVALID_INPUT.value
            )
            if is_negative_case:
                negative_cases_count += 1
                if status_matched:
                    negative_cases_detected += 1

            # 4. Citation evaluation
            for cit in response.citations:
                total_citations += 1
                if cit.is_valid:
                    valid_citations += 1

            # Determine individual question pass/fail
            passed = status_matched and (retrieval_hit or not expected_sources)
            failure_reasons = []
            if not status_matched:
                failure_reasons.append(
                    f"Status mismatch: expected {expected_status}, got {actual_status_str}"
                )
            if expected_sources and not retrieval_hit:
                failure_reasons.append(
                    f"Retrieval miss: expected sources {list(expected_sources)}, got {list(retrieved_doc_ids)}"
                )

            item_result = {
                "question_id": qid,
                "question": query_text,
                "category": category,
                "expected_status": expected_status,
                "actual_status": actual_status_str,
                "expected_sources": list(expected_sources),
                "retrieved_sources": list(retrieved_doc_ids),
                "retrieved_chunk_ids": response.source_chunk_ids,
                "confidence": response.confidence,
                "citations": [c.model_dump() for c in response.citations],
                "actual_answer": response.answer,
                "latency_ms": response.latency_ms,
                "passed": passed,
                "failure_reasons": failure_reasons
            }
            results_list.append(item_result)

        # Compute aggregate metrics
        total_questions = len(questions)
        retrieval_success_rate = (
            round(retrieval_success_count / total_retrieval_applicable, 4)
            if total_retrieval_applicable > 0 else 1.0
        )
        status_accuracy = round(status_match_count / total_questions, 4) if total_questions > 0 else 0.0
        failure_detection_rate = (
            round(negative_cases_detected / negative_cases_count, 4)
            if negative_cases_count > 0 else 1.0
        )
        citation_validity_rate = (
            round(valid_citations / total_citations, 4)
            if total_citations > 0 else 1.0
        )
        avg_latency_ms = round(total_latency_ms / total_questions, 2) if total_questions > 0 else 0.0

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_questions": total_questions,
            "metrics": {
                "retrieval_success_rate": retrieval_success_rate,
                "retrieval_applicable_count": total_retrieval_applicable,
                "status_accuracy": status_accuracy,
                "status_match_count": status_match_count,
                "failure_detection_rate": failure_detection_rate,
                "negative_cases_count": negative_cases_count,
                "citation_validity_rate": citation_validity_rate,
                "total_citations_evaluated": total_citations,
                "average_latency_ms": avg_latency_ms
            },
            "results": results_list
        }

        # Save results to evaluation/results/
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"evaluation_run_{timestamp_str}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Also save latest pointer
        latest_file = self.output_dir / "latest_evaluation_run.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Evaluation benchmark complete. Results saved to {report_file}")
        return summary


def run_evaluation() -> Dict[str, Any]:
    """Helper entry point for CLI."""
    runner = EvaluationRunner()
    return runner.run_benchmark()


if __name__ == "__main__":
    summary = run_evaluation()
    print(f"Benchmark Results:")
    print(f"Total Questions: {summary['total_questions']}")
    for k, v in summary['metrics'].items():
        print(f" - {k}: {v}")
