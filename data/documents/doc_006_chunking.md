# Chunking Strategies and Chunk Identity Specification

AegisCore implements a deterministic, boundary-aware paragraph sliding window chunking algorithm designed to optimize retrieval precision and contextual coherence.

The chunking algorithm operates with a target chunk size of 400 characters and a sliding overlap window of 60 characters. Unlike arbitrary character splitters, the AegisCore chunker respects natural text boundaries. It prefers splitting at double-newline paragraph breaks and sentence-ending punctuation marks (. ! ?). If a text segment is shorter than the minimum chunk length of 40 characters, it is merged into the adjacent chunk to prevent orphan fragments with low semantic density.

Every chunk is assigned a globally unique, deterministic Chunk ID using the format:
[DOCUMENT_ID]-C[SEQUENCE_NUMBER] (for example, DOC-006-C001, DOC-006-C002).
Each chunk object retains complete traceability metadata, including parent document_id, chunk_index, character_start, character_end, token_count, and content hash.