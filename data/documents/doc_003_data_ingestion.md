# Data Ingestion Protocols and Manifest Validation

The AegisCore Ingestion Subsystem governs the entry of technical documents into the knowledge base. Documents are ingested from the designated data repository using automated file scanning and manifest verification protocols.

Every document file must correspond to an entry in the machine-readable manifest (manifest.json). During the ingestion cycle, the subsystem performs SHA-256 cryptographic hashing on each document to verify file provenance and detect unauthorized tampering or bitrot. The ingestion engine enforces strict metadata validation, verifying that required fields—including document_id, title, source, source_type, version, created_at, updated_at, and topic—are present and non-empty.

If a document exists in the filesystem without a corresponding manifest entry, or if manifest metadata fails schema validation, the ingestion process halts with an IngestionValidationError. Ingested documents are assigned immutable internal timestamps and registered in the corpus registry.