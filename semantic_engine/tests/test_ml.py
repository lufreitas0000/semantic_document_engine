"""
TDD proofs for Machine Learning adapters.
"""
import random
from semantic_engine.core_interfaces.ml import TextEmbeddingPort

class FakeEmbeddingModel:
    """
    Simulates a neural network by returning a deterministic random vector.
    We use a fixed seed based on the text length so the same text yields the same vector.
    """
    def __init__(self, dimensions: int = 384):
        self.dimensions: int = dimensions

    def embed_text(self, text: str) -> list[float]:
        random.seed(len(text))
        return [random.uniform(-1.0, 1.0) for _ in range(self.dimensions)]

def test_fake_embedding_satisfies_protocol() -> None:
    # Mathematical proof of Liskov Substitution
    model: TextEmbeddingPort = FakeEmbeddingModel()
    vector: list[float] = model.embed_text("Quantum Physics")

    assert len(vector) == 384
    assert isinstance(vector[0], float)
