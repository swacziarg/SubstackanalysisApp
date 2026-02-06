from sentence_transformers import SentenceTransformer
from functools import lru_cache


@lru_cache(maxsize=1)
def get_embedding_model():
    print("Loading embedding model ONCE...")
    return SentenceTransformer("all-MiniLM-L6-v2")
