from sqlalchemy import text
from app.analysis.claim_filter import classify_claim

BATCH = 20  # keep small so you don't rate-limit


def classify_missing_claims(engine):

    updated = 0

    while True:
        with engine.begin() as conn:
            rows = (
                conn.execute(
                    text("""
                select id, claim
                from belief_occurrences
                where claim_type is null
                limit :batch
            """),
                    {"batch": BATCH},
                )
                .mappings()
                .all()
            )

        if not rows:
            break

        for r in rows:
            ctype = classify_claim(r["claim"])

            with engine.begin() as conn:
                conn.execute(
                    text("""
                    update belief_occurrences
                    set claim_type = :ctype
                    where id = :id
                """),
                    {"ctype": ctype, "id": r["id"]},
                )

            updated += 1
            print("classified:", r["id"], ctype)

    return {"classified": updated}
