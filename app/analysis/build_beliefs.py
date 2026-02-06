from sklearn.cluster import DBSCAN
import numpy as np
from sqlalchemy import text


def parse_pgvector(v):
    """
    Convert Postgres vector text -> numpy array
    Example:
    "[0.1,0.2,0.3]" -> np.array([0.1,0.2,0.3])
    """
    if isinstance(v, list):
        return np.array(v, dtype=float)

    if isinstance(v, str):
        return np.fromstring(v.strip("[]"), sep=",")

    raise ValueError("Unknown vector format")


def build_author_beliefs(engine, author_id):

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

    clustering = DBSCAN(eps=0.35, min_samples=2, metric="cosine").fit(X)

    clusters = {}
    for label, r in zip(clustering.labels_, rows):
        if label == -1:
            continue
        clusters.setdefault(label, []).append(r)

    # replace beliefs
    with engine.begin() as conn:
        conn.execute(
            text("delete from author_beliefs where author_id=:a"), {"a": author_id}
        )

        for group in clusters.values():
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

    return {"beliefs": len(clusters)}


def record_timeline(conn, author_id, canonical_claim, post_ids):
    from sqlalchemy import text

    rows = (
        conn.execute(
            text("""
        select published_at
        from posts
        where id = any(:ids)
    """),
            {"ids": post_ids},
        )
        .scalars()
        .all()
    )

    for t in rows:
        conn.execute(
            text("""
            insert into belief_timeline(author_id, canonical_claim, occurred_at)
            values (:a,:c,:t)
        """),
            {"a": author_id, "c": canonical_claim, "t": t},
        )
