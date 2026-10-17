# Logging, Telemetry, and Observability Framework

AegisCore provides a centralized, structured logging and observability framework designed for enterprise auditing and performance diagnostics.

The logging framework writes structured log entries to logs/rag_system.log while emitting human-readable formatted summaries to standard output. Every query execution is assigned a unique UUIDv4 correlation ID (query_id), which is threaded across ingestion, retrieval, ranking, and generation stages.

Recorded metrics include:
- Ingestion metrics: Total documents indexed, chunk count, vocabulary size, index build duration.
- Retrieval metrics: Candidate search latency in milliseconds, top similarity score, score margin between rank 1 and rank 2.
- Generation metrics: Provider mode (mock vs gemini), prompt token count, generation latency, citation validity flag.
All loggers integrate secret scrubbing filters to ensure zero credential leakage in audit logs.