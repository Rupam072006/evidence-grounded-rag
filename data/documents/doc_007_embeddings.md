# Embedding Generation and Vector Representations

The AegisCore Vector Engine transforms sanitized text chunks and query strings into high-dimensional semantic vector spaces. The platform provides a dual-provider embedding architecture supporting both hybrid sparse-dense representations and neural dense transformers.

In default reproducible environments, AegisCore employs an advanced Sublinear TF-IDF + Character/Word N-Gram hybrid vectorizer producing 512-dimensional L2-normalized representations. This model operates fully offline, requires zero external network calls, guarantees bitwise deterministic results across platforms, and eliminates GPU dependencies. For dense neural deployments, the system interfaces with sentence-transformers models such as all-MiniLM-L6-v2 yielding 384-dimensional dense vectors.

All generated embedding vectors are strictly normalized to unit length (L2 norm = 1.0). This mathematical normalization ensures that the cosine similarity between two vectors is computationally equivalent to their standard dot product, accelerating vector comparison during retrieval.