from app.utils.json_utils import ensure_list

def get_author_claims(rows):
    return [r["main_claim"] for r in rows if r.get("main_claim")]
from app.utils.json_utils import ensure_list
from app.analysis.topic_normalizer import normalize_topics

def get_author_topics(rows):
    raw = []
    for r in rows:
        raw.extend(ensure_list(r.get("topics")))

    return normalize_topics(raw)

from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")


def _cosine_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-12)
    b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-12)
    return a @ b.T


def compare_topics(a_topics: set[str], b_topics: set[str], threshold: float = 0.78):
    """
    Semantic compare:
    - agreement: pairs of topics that are semantically the same
    - unique_to_a: topics in A with no close match in B
    - unique_to_b: topics in B with no close match in A
    """

    a_list = sorted([t for t in a_topics if t])
    b_list = sorted([t for t in b_topics if t])

    if not a_list or not b_list:
        return {
            "agreement": [],
            "unique_to_a": a_list,
            "unique_to_b": b_list,
        }

    a_emb = np.asarray(_model.encode(a_list))
    b_emb = np.asarray(_model.encode(b_list))

    sims = _cosine_matrix(a_emb, b_emb)

    # greedy matching: best available pairs first
    used_a = set()
    used_b = set()
    pairs = []

    # flatten (i,j,sim) sort by sim desc
    candidates = []
    for i in range(sims.shape[0]):
        for j in range(sims.shape[1]):
            candidates.append((i, j, float(sims[i, j])))
    candidates.sort(key=lambda x: x[2], reverse=True)

    for i, j, sim in candidates:
        if sim < threshold:
            break
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)

        # pick a canonical label (shorter string) but preserve both
        a_t = a_list[i]
        b_t = b_list[j]
        canonical = a_t if len(a_t) <= len(b_t) else b_t

        pairs.append({
            "canonical": canonical,
            "a": a_t,
            "b": b_t,
            "similarity": round(sim, 3),
        })

    unique_a = [a_list[i] for i in range(len(a_list)) if i not in used_a]
    unique_b = [b_list[j] for j in range(len(b_list)) if j not in used_b]

    return {
        "agreement": pairs,
        "unique_to_a": unique_a,
        "unique_to_b": unique_b,
    }


NEG = {"not", "never", "unlikely", "wrong", "bad", "fail"}
POS = {"will", "likely", "good", "important", "necessary"}


def polarity(text):
    words = set(text.lower().split())
    score = sum(w in POS for w in words) - sum(w in NEG for w in words)
    return score


def disagreement(claims_a, claims_b):
    out = []
    for a in claims_a:
        for b in claims_b:
            if any(word in b for word in a.split()[:3]):
                if polarity(a) * polarity(b) < 0:
                    out.append((a, b))
    return out[:5]