def get_author_claims(rows):
    return [r["main_claim"] for r in rows if r["main_claim"]]


def get_author_topics(rows):
    import json

    topics = []
    for r in rows:
        if r["topics"]:
            topics.extend(json.loads(r["topics"]))
    return set(topics)


def compare_topics(a_topics, b_topics):
    return {
        "agreement": list(a_topics & b_topics),
        "unique_to_a": list(a_topics - b_topics),
        "unique_to_b": list(b_topics - a_topics),
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
