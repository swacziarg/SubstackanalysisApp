from sentence_transformers import SentenceTransformer

# Small, fast, free, 384-dim vectors
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_texts(texts: list[str]) -> list[list[float]]:
    vecs = _model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vecs]
