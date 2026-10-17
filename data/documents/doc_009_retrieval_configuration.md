# Retrieval Configuration, Filter Policies, and Candidate Limits

The AegisCore query retrieval service governs candidate passage selection and filtering policies. Production systems implement strict operational thresholds to balance recall with context window economy.

Under standard operational policy, the retrieval service executes with a default top-k parameter of 5 candidates and caps the candidate evaluation pool at a maximum of 20 raw chunks. Queries apply a relevance cosine similarity threshold of 0.18. Any passage scoring below this similarity threshold is pruned prior to ranking.

The retrieval pipeline supports metadata filtering allowing queries to constrain candidate pools by topic, document version, or source type. When tenant or topic constraints are active, non-matching documents are discarded during the pre-ranking phase before similarity calculation occurs.