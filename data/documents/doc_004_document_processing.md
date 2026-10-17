# Document Parsing and Structural Extraction

Document parsing converts raw file formats into canonical textual representations suitable for chunking and vector encoding. AegisCore implements format-specific extractors for Markdown, Plaintext, and structured JSON files.

The parser extracts both structural hierarchy and textual content. For Markdown documents, section headers (H1, H2, H3), code blocks, and bulleted lists are parsed while preserving logical block boundaries. Structural metadata, including primary section titles and hierarchical breadcrumbs, is extracted and associated with the underlying text sections.

All incoming files are enforced to use UTF-8 character encoding. Files containing invalid byte sequences or unsupported binary markers are rejected immediately with a DocumentParsingError. The parsing module strips non-printable control characters while retaining standard paragraph separators (double newlines) to assist downstream chunking.