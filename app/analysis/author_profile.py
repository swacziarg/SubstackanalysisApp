from collections import Counter
from app.utils.json_utils import ensure_list


def aggregate_topics(rows):
    counter = Counter()

    for r in rows:
        counter.update(ensure_list(r.get("topics")))

    return [t for t, _ in counter.most_common(8)]


def bias_stats(rows):
    scores = [r["bias_score"] for r in rows if r["bias_score"] is not None]
    confs = [r["confidence"] for r in rows if r["confidence"] is not None]

    if not scores:
        return None

    return {
        "mean": sum(scores) / len(scores),
        "confidence": sum(confs) / len(confs) if confs else 0,
    }


def recurring_claims(rows):
    claims = [r["main_claim"] for r in rows if r.get("main_claim")]

    # naive placeholder for now
    claims.sort(key=len, reverse=True)
    return claims[:5]
