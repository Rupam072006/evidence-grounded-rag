# Security Controls, Prompt Injection Defense, and Secret Protection

AegisCore enforces enterprise-grade security controls to protect the retrieval and generation lifecycle from manipulation, data exfiltration, and prompt injection attacks.

Key security mandates include:
1. Untrusted Document Paradigm: All document text is treated as passive, untrusted data. The generation prompt instructs the model to ignore any embedded directives such as "Ignore previous instructions", "SYSTEM OVERRIDE", or "Print system prompt".
2. Secret Protection & Environment Isolation: Secrets, API keys, and credentials must never be committed to source repositories or hardcoded in configuration files. Secrets are read exclusively from environment variables (such as GEMINI_API_KEY).
3. Secret-Free Logging: All log outputs, telemetry streams, and error traces pass through regex redaction filters that scrub potential API keys, authorization bearer tokens, and credentials.
4. Input Boundary Isolation: User queries are strictly quarantined within delimiter blocks to prevent prompt boundary escaping.