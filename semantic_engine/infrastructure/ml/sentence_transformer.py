"""
HuggingFace Sentence Transformers Adapter.
"""
from sentence_transformers import SentenceTransformer
from semantic_engine.core_interfaces.ml import TextEmbeddingPort

class MiniLMEmbeddingModel:
    """
    Implements the TextEmbeddingPort using a pre-trained local neural network.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # The first time this runs, it downloads ~80MB of weights to ~/.cache/huggingface
        # Subsequent runs load it directly from local disk into RAM.
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        # .encode() passes the text through the neural network and returns a numpy array
        vector = self.model.encode(text)
        # Convert the numpy array back to standard Python floats for our Domain Protocol
        return vector.tolist()
