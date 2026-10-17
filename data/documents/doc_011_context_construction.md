# Context Construction and Passage Formatting Guidelines

Context construction is the critical bridge connecting retrieval to generative inference. The Context Builder synthesizes retrieved chunks into a structured, tamper-resistant prompt payload for the language model.

The builder processes the top-k retrieved passages according to strict formatting rules:
1. Context Budgeting: The total token budget allocated for context passages is capped at 1,500 tokens (approximately 6,000 characters). Passages exceeding the budget are excluded.
2. Passage Delimitation: Each passage is framed with explicit boundaries:
=== PASSAGE [CHUNK_ID] (SOURCE: [DOC_ID] | SCORE: [SCORE]) ===
[CHUNK_CONTENT]
=== END PASSAGE ===
3. Order of Presentation: Passages are presented in descending order of relevance score.
4. Redundancy Elimination: If two adjacent chunks from the same parent document exhibit significant textual overlap, the overlapping characters are deduplicated to conserve token budget.