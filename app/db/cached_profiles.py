from sqlalchemy import text
import json


def get_cached_profile(engine, author_id):
    with engine.begin() as conn:
        row = conn.execute(
            text("""
            select profile_json
            from author_cached_profiles
            where author_id = :a
        """),
            {"a": author_id},
        ).scalar()

    return row


def upsert_cached_profile(engine, author_id, profile):
    with engine.begin() as conn:
        conn.execute(
            text("""
            insert into author_cached_profiles(author_id, profile_json)
            values (:a, :p)
            on conflict (author_id) do update
            set profile_json = excluded.profile_json,
                computed_at = now()
        """),
            {"a": author_id, "p": json.dumps(profile)},
        )
