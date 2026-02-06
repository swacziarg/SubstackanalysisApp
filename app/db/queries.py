from sqlalchemy import text
from sqlalchemy.engine import Engine
import json


def search_post_chunks(engine, post_id: int, embedding: list[float], limit: int = 5):
    q = text("""
    select content
    from post_chunks
    where post_id = :post_id
    order by embedding <-> CAST(:embedding AS vector)
    limit :limit
    """)

    with engine.begin() as conn:
        rows = conn.execute(
            q,
            {
                "post_id": post_id,
                "embedding": json.dumps(embedding),  # important
                "limit": limit,
            },
        ).fetchall()

    return [r[0] for r in rows]


def upsert_author(
    engine: Engine, subdomain: str, name: str, description: str | None = None
):
    q = text("""
    insert into authors (subdomain, name, description)
    values (:subdomain, :name, :description)
    on conflict (subdomain) do update
    set name = excluded.name,
        description = coalesce(excluded.description, authors.description)
    returning id;
    """)
    with engine.begin() as conn:
        return conn.execute(
            q, {"subdomain": subdomain, "name": name, "description": description}
        ).scalar_one()


def upsert_post_shell(
    engine: Engine,
    author_id: int,
    title: str,
    url: str,
    published_at,
    slug: str | None,
    word_count: int | None,
):
    q = text("""
    insert into posts (author_id, title, url, published_at, slug, word_count)
    values (:author_id, :title, :url, :published_at, :slug, :word_count)
    on conflict (url) do update
    set title = excluded.title,
        published_at = excluded.published_at,
        slug = coalesce(excluded.slug, posts.slug),
        word_count = coalesce(excluded.word_count, posts.word_count)
    returning id, checksum, processed;
    """)
    with engine.begin() as conn:
        row = (
            conn.execute(
                q,
                {
                    "author_id": author_id,
                    "title": title,
                    "url": url,
                    "published_at": published_at,
                    "slug": slug,
                    "word_count": word_count,
                },
            )
            .mappings()
            .one()
        )
        return dict(row)


def should_skip_processing(engine: Engine, post_id: int, new_checksum: str) -> bool:
    q = text("select checksum, processed from posts where id = :post_id;")
    with engine.begin() as conn:
        row = conn.execute(q, {"post_id": post_id}).mappings().one()
    return bool(row["processed"]) and row["checksum"] == new_checksum


def set_post_processed(engine: Engine, post_id: int, checksum: str):
    q = text("""
    update posts
    set checksum = :checksum,
        processed = true
    where id = :post_id;
    """)
    with engine.begin() as conn:
        conn.execute(q, {"post_id": post_id, "checksum": checksum})


def upsert_post_content(engine: Engine, post_id: int, raw_html: str, clean_text: str):
    q = text("""
    insert into post_contents (post_id, raw_html, clean_text)
    values (:post_id, :raw_html, :clean_text)
    on conflict (post_id) do update
    set raw_html = excluded.raw_html,
        clean_text = excluded.clean_text;
    """)
    with engine.begin() as conn:
        conn.execute(
            q, {"post_id": post_id, "raw_html": raw_html, "clean_text": clean_text}
        )


def replace_chunks(
    engine: Engine, post_id: int, chunks: list[str], embeddings: list[list[float]]
):
    # delete old, insert new in a single transaction
    del_q = text("delete from post_chunks where post_id = :post_id;")
    ins_q = text("""
    insert into post_chunks (post_id, chunk_index, content, embedding)
    values (:post_id, :chunk_index, :content, (:embedding)::vector);
    """)
    with engine.begin() as conn:
        conn.execute(del_q, {"post_id": post_id})
        for i, (c, e) in enumerate(zip(chunks, embeddings)):
            conn.execute(
                ins_q,
                {
                    "post_id": post_id,
                    "chunk_index": i,
                    "content": c,
                    "embedding": e,  # SQLAlchemy will pass list -> text; cast handles it
                },
            )


def insert_analysis(engine, post_id: int, analysis: dict, model: str, prompt_hash: str):
    from sqlalchemy import text
    import json

    q = text("""
    insert into post_analysis (
      post_id, summary, main_claim, bias_score, confidence,
      arguments_for, arguments_against, notable_quotes, topics, entities,
      model, prompt_hash
    )
    values (
      :post_id, :summary, :main_claim, :bias_score, :confidence,
      :arguments_for, :arguments_against, :notable_quotes, :topics, :entities,
      :model, :prompt_hash
    )
    on conflict (post_id, prompt_hash) do nothing;
    """)

    with engine.begin() as conn:
        conn.execute(
            q,
            {
                "post_id": post_id,
                "summary": analysis.get("summary"),
                "main_claim": analysis.get("main_claim"),
                "bias_score": analysis.get("bias_score"),
                "confidence": analysis.get("confidence"),
                "arguments_for": json.dumps(analysis.get("arguments_for", [])),
                "arguments_against": json.dumps(analysis.get("arguments_against", [])),
                "notable_quotes": json.dumps(analysis.get("notable_quotes", [])),
                "topics": json.dumps(analysis.get("topics", [])),
                "entities": json.dumps(analysis.get("entities", [])),
                "model": model,
                "prompt_hash": prompt_hash,
            },
        )


def list_author_urls(engine):
    from sqlalchemy import text

    with engine.begin() as conn:
        rows = conn.execute(text("select subdomain from authors")).fetchall()
    return [f"https://{r[0]}.substack.com" for r in rows]


def list_authors(engine):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            select id, name, subdomain
            from authors
            order by name
        """))
        return [dict(r._mapping) for r in rows]


def list_posts_for_author(engine, author_id):
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
            select
                p.id,
                p.title,
                p.published_at,
                a.summary,
                a.bias_score,
                a.confidence
            from posts p
            left join post_analysis a on a.post_id = p.id
            where p.author_id = :author_id
            order by p.published_at desc
        """),
            {"author_id": author_id},
        )

        return [dict(r._mapping) for r in rows]


def get_post(engine, post_id):
    from sqlalchemy import text

    with engine.begin() as conn:
        row = conn.execute(
            text("""
            select
                p.id,
                p.title,
                p.url,
                c.raw_html,
                c.clean_text,
                a.summary,
                a.main_claim,
                a.bias_score,
                a.confidence,
                a.arguments_for,
                a.arguments_against,
                a.notable_quotes,
                a.topics,
                a.entities
            from posts p
            left join post_contents c on c.post_id = p.id
            left join lateral (
                select *
                from post_analysis pa
                where pa.post_id = p.id
                order by pa.analyzed_at desc
                limit 1
            ) a on true
            where p.id = :post_id
        """),
            {"post_id": post_id},
        ).mappings().first()

    if not row:
        return None

    return {
        "id": row["id"],
        "title": row["title"],
        "url": row["url"],
        "html": row["raw_html"],          # ← NEW
        "text": row["clean_text"],        # ← keep for embeddings/debug
        "analysis": {
            "summary": row["summary"],
            "main_claim": row["main_claim"],
            "bias": row["bias_score"],
            "confidence": row["confidence"],
            "topics": row["topics"],
        },
    }


def get_author_analyses(engine, author_id):
    from sqlalchemy import text

    q = text("""
    select distinct on (p.id)
        pa.summary,
        pa.main_claim,
        pa.topics,
        pa.bias_score,
        pa.confidence
    from post_analysis pa
    join posts p on p.id = pa.post_id
    where p.author_id = :author_id
    order by p.id, pa.analyzed_at desc
    """)

    with engine.begin() as conn:
        return [dict(r._mapping) for r in conn.execute(q, {"author_id": author_id})]


def upsert_author_profile(engine, author_id, summary, beliefs, topics, bias):
    from sqlalchemy import text
    import json

    q = text("""
    insert into author_profiles (author_id, summary, beliefs, recurring_topics, bias_overview)
    values (:author_id, :summary, :beliefs, :topics, :bias)
    on conflict (author_id) do update set
        summary = excluded.summary,
        beliefs = excluded.beliefs,
        recurring_topics = excluded.recurring_topics,
        bias_overview = excluded.bias_overview,
        computed_at = now();
    """)

    with engine.begin() as conn:
        conn.execute(
            q,
            {
                "author_id": author_id,
                "summary": summary,
                "beliefs": json.dumps(beliefs),
                "topics": json.dumps(topics),
                "bias": json.dumps(bias),
            },
        )


def get_author_profile(engine, author_id):
    from sqlalchemy import text

    with engine.begin() as conn:

        # ---- beliefs ----
        beliefs = (
            conn.execute(
                text("""
            select
                canonical_claim,
                support_count,
                avg_polarity,
                confidence
            from author_beliefs
            where author_id = :author_id
            order by support_count desc
        """),
                {"author_id": author_id},
            )
            .mappings()
            .all()
        )

        if not beliefs:
            return None

        # ---- topics + bias still derived from analyses ----
        analyses = (
            conn.execute(
                text("""
            select summary, topics, bias_score, confidence
            from post_analysis pa
            join posts p on p.id = pa.post_id
            where p.author_id = :author_id
        """),
                {"author_id": author_id},
            )
            .mappings()
            .all()
        )

    # topics
    from collections import Counter

    topic_counter = Counter()
    for r in analyses:
        if r["topics"]:
            topic_counter.update(r["topics"])

    # bias
    scores = [r["bias_score"] for r in analyses if r["bias_score"] is not None]
    confs = [r["confidence"] for r in analyses if r["confidence"] is not None]

    bias = None
    if scores:
        bias = {
            "mean": sum(scores) / len(scores),
            "confidence": sum(confs) / len(confs) if confs else 0,
        }

    tensions = get_author_tensions(engine, author_id)

    return {
        "summary": beliefs[0]["canonical_claim"],
        "beliefs": [b["canonical_claim"] for b in beliefs[:12]],
        "tensions": tensions[:8],
        "recurring_topics": [t for t, _ in topic_counter.most_common(8)],
        "bias_overview": bias,
    }


def insert_belief_occurrences(engine, author_id, post_id, occurred_at, claims):
    from sqlalchemy import text
    from datetime import datetime, timezone

    # fallback: if post has no publication date, use "now" once
    if occurred_at is None:
        occurred_at = datetime.now(timezone.utc)

    q = text("""
    insert into belief_occurrences
    (author_id, post_id, claim, polarity, confidence, occurred_at)
    values (:author_id, :post_id, :claim, :polarity, :confidence, :occurred_at)
    """)

    with engine.begin() as conn:
        for claim, polarity, conf in claims:
            conn.execute(
                q,
                {
                    "author_id": author_id,
                    "post_id": post_id,
                    "claim": claim,
                    "polarity": polarity,
                    "confidence": conf,
                    "occurred_at": occurred_at,
                },
            )


def get_author_beliefs(engine, author_id):
    from sqlalchemy import text

    q = text("""
    select
        canonical_claim,
        support_count,
        avg_polarity,
        confidence
    from author_beliefs
    where author_id = :author_id
    order by support_count desc
    """)

    with engine.begin() as conn:
        rows = conn.execute(q, {"author_id": author_id}).mappings().all()

    return [dict(r) for r in rows]


def get_author_tensions(engine, author_id):
    from sqlalchemy import text

    q = text("""
        select belief_a, belief_b, confidence
        from belief_relations
        where author_id = :a
        and relation = 'CONTRADICTS'
        order by confidence desc
    """)

    with engine.begin() as conn:
        rows = conn.execute(q, {"a": author_id}).mappings().all()

    return [dict(r) for r in rows]
