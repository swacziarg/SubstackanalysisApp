import numpy as np
from sqlalchemy import text
from sklearn.metrics.pairwise import cosine_similarity


def parse_pgvector(v):
    if isinstance(v, list):
        return np.array(v, dtype=float)
    if isinstance(v, str):
        return np.fromstring(v.strip("[]"), sep=",")
    raise ValueError("Unknown vector format")


def build_author_beliefs(engine, author_id):

    # ---------- load claim embeddings ----------
    with engine.begin() as conn:
        rows = (
            conn.execute(
                text("""
                select id, claim, polarity, confidence, embedding
                from belief_occurrences
                where author_id = :author_id
                and embedding is not null
                and claim_type = 'ADVANCED'
            """),
                {"author_id": author_id},
            )
            .mappings()
            .all()
        )

    if not rows:
        return {"beliefs": 0}

    X = np.vstack([parse_pgvector(r["embedding"]) for r in rows])

    # ---------- semantic grouping (NOT density clustering) ----------
    sim = cosine_similarity(X)

    groups = []
    used = set()
    THRESH = 0.72  # belief similarity threshold

    for i in range(len(rows)):
        if i in used:
            continue

        group_idx = [i]
        used.add(i)

        for j in range(i + 1, len(rows)):
            if j in used:
                continue
            if sim[i][j] >= THRESH:
                group_idx.append(j)
                used.add(j)

        groups.append([rows[k] for k in group_idx])

    # ---------- write beliefs ----------
    with engine.begin() as conn:
        conn.execute(
            text("delete from author_beliefs where author_id=:a"),
            {"a": author_id},
        )

        inserted = 0

        for group in groups:
            canonical = max(group, key=lambda x: len(x["claim"]))["claim"]
            support = len(group)
            polarity = sum(x["polarity"] for x in group) / support
            confidence = sum(x["confidence"] for x in group) / support

            conn.execute(
                text("""
                    insert into author_beliefs
                    (author_id, canonical_claim, support_count, avg_polarity, confidence)
                    values (:a,:c,:s,:p,:conf)
                """),
                {
                    "a": author_id,
                    "c": canonical,
                    "s": support,
                    "p": polarity,
                    "conf": confidence,
                },
            )

            inserted += 1

    return {"beliefs": inserted}
