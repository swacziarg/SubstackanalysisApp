from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

SIM_THRESHOLD = 0.78


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def normalize_topics(topics: list[str]) -> set[str]:
    """
    Collapse semantically similar topics into canonical representatives
    """

    if not topics:
        return set()

    embeddings = model.encode(topics)
    clusters = []

    for topic, emb in zip(topics, embeddings):
        placed = False

        for cluster in clusters:
            if cosine(emb, cluster["embedding"]) > SIM_THRESHOLD:
                cluster["items"].append(topic)
                placed = True
                break

        if not placed:
            clusters.append({
                "embedding": emb,
                "items": [topic]
            })

    # choose shortest phrase as canonical
    canonical = set(min(c["items"], key=len) for c in clusters)

    return canonical