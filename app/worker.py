import os
from app.db.engine import get_engine
from app.ingestion.pipeline import ingest_author


def run_ingestion(targets: list[str], limit: int = 10):
    engine = get_engine()
    results = []

    for url in targets:
        result = ingest_author(engine, url, limit_posts=limit)
        results.append({"url": url, "result": result})

    return results