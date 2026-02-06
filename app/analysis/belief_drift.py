from sqlalchemy import text
from app.analysis.belief_relations import classify_relation


def detect_belief_changes(engine, author_id):

    with engine.begin() as conn:
        beliefs = (
            conn.execute(
                text("""
            select canonical_claim, min(occurred_at) first_seen, max(occurred_at) last_seen
            from belief_timeline
            where author_id=:a
            group by canonical_claim
        """),
                {"a": author_id},
            )
            .mappings()
            .all()
        )

    changes = []

    for i, a in enumerate(beliefs):
        for b in beliefs[i + 1 :]:
            rel = classify_relation(a["canonical_claim"], b["canonical_claim"])
            if rel["relation"] == "CONTRADICTS":
                changes.append(
                    {
                        "earlier": a["canonical_claim"],
                        "later": b["canonical_claim"],
                        "confidence": rel["confidence"],
                    }
                )

    return changes
