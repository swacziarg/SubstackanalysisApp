
from app.ai.model_store import get_embedding_model
_model = get_embedding_model()

def embed_texts(texts: list[str]) -> list[list[float]]:
    vecs = _model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vecs]
