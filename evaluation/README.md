# AegisCore Evaluation Benchmark

This directory contains the standardized evaluation benchmark dataset and execution reports for the Evidence-Grounded RAG System.

## Benchmark Dataset: `questions.jsonl`
The benchmark comprises **22 distinct evaluation queries** structured across six essential test categories, exceeding the minimum 20-question requirement:

| Category | Count | Purpose / Description |
|---|---|---|
| **Answerable** | 10 | Direct factual questions testing high-precision retrieval and citation attribution across single technical documents (`Q01` - `Q10`). |
| **Multi-Document** | 3 | Complex queries requiring synthesis across multiple interconnected technical specifications (`Q11` - `Q13`). |
| **Ambiguous** | 2 | Broad, polysemous queries testing robust ranking and topic alignment without hallucinating unstated facts (`Q14` - `Q15`). |
| **Insufficient Evidence** | 2 | Completely out-of-domain queries testing strict evidence sufficiency floors and canonical refusal emission (`Q16` - `Q17`). |
| **Conflicting Evidence** | 2 | Queries targeting the intentional contradiction between `DOC-009` (top-k=5, pool=20) and `DOC-020` (top-k=10, pool=50) (`Q18` - `Q19`). |
| **Adversarial / Injection** | 1 | Prompt-injection attempt testing system prompt containment and untrusted data handling (`Q20`). |
| **Boundary / Malformed** | 2 | Whitespace-only query and 550+ character query testing input validation (`Q21` - `Q22`). |

## Record Schema
Each line in `questions.jsonl` adheres to this schema:
```json
{
  "question_id": "Q01",
  "category": "answerable",
  "question": "What is the primary operational mission of AegisCore...?",
  "expected_sources": ["DOC-001"],
  "expected_status": "ANSWERED",
  "expected_answer_summary": "...",
  "expected_behaviour": "...",
  "evaluation_notes": "..."
}
```

## Evaluated Metrics
1. **Retrieval Success Rate:** Fraction of questions where at least one expected source document was included in top-k retrieved results.
   - *Denominator:* Questions where `expected_sources` is non-empty.
2. **Status Accuracy:** Fraction of queries where `actual_status == expected_status`.
   - *Denominator:* Total questions (22).
3. **Failure Detection Rate:** Fraction of negative cases (`INSUFFICIENT_EVIDENCE`, `CONFLICT_DETECTED`, `INVALID_INPUT`) correctly detected and categorized.
   - *Denominator:* Total negative test cases (6).
4. **Citation Validity Rate:** Ratio of valid, context-verified citations to total citations generated in answers.
   - *Denominator:* Total generated citations.
5. **Average Latency:** Mean end-to-end processing latency in milliseconds across the benchmark battery.

## Execution
To run the evaluation benchmark:
```powershell
python -m evidence_rag.cli evaluate
```
Reports are automatically timestamped and saved in `evaluation/results/`.
