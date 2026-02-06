from groq import Groq
import os
import json
import itertools

client = Groq(api_key=os.environ["GROQ_API_KEY"])

PROMPT = """
Determine the logical relationship between two beliefs held by the same author.

SUPPORTS = belief A strengthens or explains belief B
CONTRADICTS = both cannot be true simultaneously
UNRELATED = no clear logical interaction

Return JSON:
{{"relation":"SUPPORTS"|"CONTRADICTS"|"UNRELATED","confidence":0-1}}

Belief A:
{a}

Belief B:
{b}
"""


def classify_relation(a, b):
    r = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        temperature=0,
        messages=[{"role": "user", "content": PROMPT.format(a=a, b=b)}],
    )

    raw = r.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw)
        return {
            "relation": parsed.get("relation", "UNRELATED"),
            "confidence": float(parsed.get("confidence", 0.5)),
        }
    except:
        return {"relation": "UNRELATED", "confidence": 0.5}


def build_relations(engine, author_id):

    from sqlalchemy import text

    with engine.begin() as conn:
        beliefs = (
            conn.execute(
                text("""
            select canonical_claim
            from author_beliefs
            where author_id=:a
        """),
                {"a": author_id},
            )
            .scalars()
            .all()
        )

    pairs = list(itertools.combinations(beliefs, 2))

    inserted = 0

    for a, b in pairs:
        rel = classify_relation(a, b)

        with engine.begin() as conn:
            conn.execute(
                text("""
                insert into belief_relations
                (author_id, belief_a, belief_b, relation, confidence)
                values (:a,:ba,:bb,:r,:c)
            """),
                {
                    "a": author_id,
                    "ba": a,
                    "bb": b,
                    "r": rel["relation"],
                    "c": rel["confidence"],
                },
            )

        inserted += 1

    return {"relations": inserted}
