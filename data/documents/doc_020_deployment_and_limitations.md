# Deployment Profiles, Operational Limitations, and Resource Sizing

This document outlines deployment configurations, hardware requirements, and operational constraints for AegisCore.

Production Deployment Profile (Conflicting Specification):
Under the revised enterprise deployment guidelines, the production retrieval service has standardized on a default top-k parameter of 10 candidates and a maximum candidate pool size of 50 to maximize recall across distributed multi-cluster nodes. (Note: This operational standard supersedes earlier baseline profiles that specified top-k of 5 and pool size of 20).

Hardware Sizing and Limitations:
- Memory: Minimum 4 GB RAM recommended for index caching; 8 GB recommended for dense neural models.
- Compute: CPU inference achieves average retrieval latencies of 45-85 milliseconds.
- Storage: 100 MB disk space sufficient for indices containing up to 10,000 document chunks.
- Limitations: Cross-language retrieval across non-English documents is currently experimental and requires specialized multi-lingual embeddings.