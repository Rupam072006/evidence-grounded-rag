# Citation Syntax, Claim Attribution, and Citation Validation

Citations in AegisCore represent verifiable audit trails linking generated statements to underlying knowledge sources. Every factual statement must carry explicit citations.

The required citation syntax is:
[DOCUMENT_ID:CHUNK_ID]
Example: "The system enforces a 400-character target chunk size [DOC-013:DOC-013-C001]."

AegisCore incorporates an automated post-generation Citation Validator. The validator executes the following checks:
1. Existence Verification: Verifies that every cited chunk ID actually existed in the retrieved context for that specific query. Invented or hallucinated chunk IDs trigger validation failure.
2. Source ID Consistency: Verifies that the document ID prefix matches the parent document of the cited chunk ID.
3. Content Overlap Verification: Confirms that key factual n-grams in the cited sentence share lexical overlap with the cited chunk body.

If any citation fails validation, the system flags the response with status CITATION_VALIDATION_FAILED and suppresses ungrounded claims.