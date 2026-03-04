"""
Machine Learning Protocols (The Membrane).
Defines the boundaries for AI and NLP operations.
We must define the structural contract for a Machine Learning model.
"""
from typing import Protocol

class TextEmbeddingPort(Protocol):
    """
    Translates human language into a continuous mathematical vector space.
    """
    def embed_text(self, text: str) -> list[float]:
        ...
# change name to generate_embedding
