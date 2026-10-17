# Text Cleaning, Sanitization, and PII Redaction

The Text Cleaning Pipeline prepares parsed document text for embedding generation by removing typographic noise, normalizing Unicode representations, and stripping potential injection vectors.

The cleaning process executes in four sequential stages:
1. Unicode Normalization: Converts all characters to NFKC (Compatibility Decomposition followed by Canonical Composition) to resolve disparate ligature and accent encodings.
2. Control Character Removal: Strips ASCII control codes 0 through 31, with the strict exceptions of horizontal tabs (ASCII 9), line feeds (ASCII 10), and carriage returns (ASCII 13).
3. Whitespace Consolidation: Replaces consecutive whitespace characters with a single space while standardizing multi-line paragraph breaks to double newlines.
4. Security Tag Stripping: Identifies and strips raw HTML tags, embedded Javascript script blocks, and XML directive tags to eliminate markup-based injection attempts.

Additionally, heuristic regex filters detect and mask sensitive identifiers such as API keys, private passwords, and personal email addresses with redacted placeholder tokens.