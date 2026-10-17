# Confidence Scoring and Uncertainty Handling Framework

AegisCore features a transparent, multi-dimensional confidence assessment model. The system avoids deceptive pseudo-probabilistic percentages by distinguishing semantic similarity from factual sufficiency.

The Confidence Score (ranging from 0.0 to 1.0) is calculated as a composite metric:
Confidence = (0.50 * Top_Similarity_Score) + (0.30 * Mean_Top3_Similarity) + (0.20 * Query_Term_Coverage_Ratio).

Evidence Sufficiency Floor:
To prevent answering off-topic or out-of-domain queries, AegisCore establishes a strict evidence sufficiency floor of 0.25. If the highest similarity score among retrieved passages is below 0.25, the query is immediately categorized as unanswerable.
In such cases, the system returns status INSUFFICIENT_EVIDENCE with the canonical refusal:
"INSUFFICIENT EVIDENCE: The available knowledge base does not contain enough information to answer this question reliably."
No speculative generation is permitted when sufficiency criteria are unmet.