from semantic_engine.core_interfaces.ml import TextEmbeddingPort

def test_fake_embedding_satisfies_protocol(fake_ml) -> None:
    vector: list[float] = fake_ml.embed_text("Quantum Physics")
    assert len(vector) == 384
    assert isinstance(vector[0], float)
