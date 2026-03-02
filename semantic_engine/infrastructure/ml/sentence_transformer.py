"""
HuggingFace Sentence Transformers Adapter.
"""
import torch
from sentence_transformers import SentenceTransformer
from typing import Optional
from semantic_engine.core_interfaces.ml import TextEmbeddingPort

        # The first time this runs, it downloads ~80MB of weights to ~/.cache/huggingface
        # Subsequent runs load it directly from local disk into RAM.
        # .encode() passes the text through the neural network and returns a numpy array
        # Convert the numpy array back to standard Python floats for our Domain Protocol

class HuggingFaceEmbeddingModel(TextEmbeddingPort):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
        self.device: str
        # 1. Hardware Detection
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Loading {model_name} onto {self.device.upper()}...")

        # 2. Load model into RAM or VRAM
        self.model = SentenceTransformer(model_name, device=self.device)

    def embed_text(self, text: str) -> list[float]:
        # The model automatically executes the math on the target device
        embedding = self.model.encode(text)
        return embedding.tolist()
