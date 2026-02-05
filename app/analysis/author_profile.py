from collections import Counter
import json


def _ensure_list(value):
    """Accept jsonb, json string, or None and normalize to list"""
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return []

    return []


def aggregate_topics(rows):
    counter = Counter()

    for r in rows:
        topics = _ensure_list(r.get("topics"))
        counter.update(topics)

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