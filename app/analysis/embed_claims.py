from app.ai.embeddings import embed_texts
from sqlalchemy import text


def embed_missing_claims(engine):

    with engine.begin() as conn:
        rows = conn.execute(text("""
            select id, claim
            from belief_occurrences
            where embedding is null
        """)).fetchall()

    if not rows:
        return 0

    ids = [r[0] for r in rows]
    texts = [r[1] for r in rows]

    vectors = embed_texts(texts)

    with engine.begin() as conn:
        for i, vec in zip(ids, vectors):
            conn.execute(
                text("""
                update belief_occurrences
                set embedding = :vec
                where id = :id
            """),
                {"vec": vec, "id": i},
            )

    return len(rows)
