# Similarity Scoring Metrics and Candidate Ranking Heuristics

Candidate scoring in AegisCore quantifies the semantic relevance between the user query vector q and each stored chunk vector c_i. Because all vectors in the index are unit-normalized (||q|| = 1 and ||c_i|| = 1), the cosine similarity metric simplifies to the vector dot product:

Cosine_Similarity(q, c_i) = q · c_i = sum(q_j * c_ij) for j = 1 to D.

Raw cosine scores range from 0.0 (orthogonal) to 1.0 (identical direction). To improve ranking robustness, AegisCore applies a score calibration heuristic:
1. Exact keyword overlap boost: Passages containing exact case-insensitive matches for critical query terms receive an additive boost factor of up to 0.05.
2. Density penalty: Excessively short or repetitive chunks receive a small damping penalty.

Candidates are sorted in descending order of calibrated score. In cases where two chunks produce identical similarity scores, tie-breaking defaults to document version precedence followed by chunk sequence order.