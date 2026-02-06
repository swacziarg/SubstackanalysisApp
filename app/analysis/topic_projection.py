import numpy as np

from app.ai.model_store import get_embedding_model

_model = get_embedding_model()

# anchor domains — shared intellectual space
ANCHORS = [
    "artificial intelligence",
    "human cognition",
    "education",
    "psychology",
    "economics",
    "politics",
    "technology",
    "philosophy",
    "culture",
    "forecasting and prediction",
    "social behavior",
    "epistemology",
]

_anchor_emb = _model.encode(ANCHORS)


def project_to_domains(topics: list[str], threshold=0.55):
    if not topics:
        return set()

    emb = _model.encode(topics)

    result = set()

    for t, vec in zip(topics, emb):
        sims = np.dot(_anchor_emb, vec) / (
            np.linalg.norm(_anchor_emb, axis=1) * np.linalg.norm(vec) + 1e-9
        )

        best = sims.argmax()
        if sims[best] >= threshold:
            result.add(ANCHORS[best])

    return result
