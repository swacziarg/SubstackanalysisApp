from sqlalchemy import text
from app.analysis.claim_extractor import extract_claims
from app.db.queries import insert_belief_occurrences


def backfill_author_beliefs(engine, author_id):

    q = text("""
        select
            p.id as post_id,
            p.published_at,
            pa.summary,
            pa.main_claim,
            pa.arguments_for,
            pa.arguments_against,
            pa.confidence
        from posts p
        join lateral (
            select *
            from post_analysis pa
            where pa.post_id = p.id
            order by pa.analyzed_at desc
            limit 1
        ) pa on true
        where p.author_id = :author_id
    """)

    inserted = 0

    with engine.begin() as conn:
        rows = conn.execute(q, {"author_id": author_id}).mappings().all()

    for r in rows:
        claims = extract_claims(r)

        insert_belief_occurrences(
            engine, author_id, r["post_id"], r["published_at"], claims
        )

        inserted += len(claims)

    return {"beliefs_inserted": inserted}
