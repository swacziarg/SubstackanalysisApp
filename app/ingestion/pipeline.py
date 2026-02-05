import hashlib
from datetime import datetime
from sqlalchemy.engine import Engine

from app.db.queries import (
    upsert_author, upsert_post_shell, should_skip_processing,
    upsert_post_content, replace_chunks, upsert_analysis, set_post_processed
)
from app.ingestion.substack_client import SubstackClient
from app.ingestion.cleaner import html_to_text
from app.ingestion.chunker import chunk_text
from app.ai.embeddings import embed_texts
from app.ai.groq_analysis import analyze_article

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def parse_subdomain(newsletter_url: str) -> str:
    # https://astralcodexten.substack.com -> astralcodexten
    host = newsletter_url.replace("https://", "").replace("http://", "").split("/")[0]
    return host.split(".")[0]

def ingest_author(engine: Engine, newsletter_url: str, limit_posts: int = 10):
    client = SubstackClient(newsletter_url)
    subdomain = parse_subdomain(newsletter_url)

    # substack_api doesn’t always provide author nicely; use subdomain as fallback
    author_id = upsert_author(engine, subdomain=subdomain, name=subdomain, description=None)

    posts = client.get_posts(limit=limit_posts)

    for p in posts:
        # Defensive: library objects vary; grab what exists
        title = getattr(p, "title", None) or "Untitled"
        url = getattr(p, "url", None)
        published_at = getattr(p, "post_date", None)
        slug = getattr(p, "slug", None)

        if not url:
            continue

        # Normalize published_at
        if isinstance(published_at, str):
            try:
                published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except Exception:
                published_at = None

        shell = upsert_post_shell(
            engine,
            author_id=author_id,
            title=title,
            url=url,
            published_at=published_at,
            slug=slug,
            word_count=None
        )
        post_id = shell["id"]


        html = client.get_post_html(url)

        # Paywalled or unavailable
        if not html or "paywalled" in str(html).lower():
            print(f"Skipping paywalled post: {title}")
            continue

        clean = html_to_text(html)

        if not clean.strip():
            print(f"Skipping empty post: {title}")
            continue

        checksum = sha256_text(clean)

        if should_skip_processing(engine, post_id, checksum):
            continue

        upsert_post_content(engine, post_id, raw_html=html, clean_text=clean)

        chunks = chunk_text(clean)
        if not chunks:
            # still mark processed so we don't loop forever
            set_post_processed(engine, post_id, checksum)
            continue

        embeddings = embed_texts(chunks)
        replace_chunks(engine, post_id, chunks, embeddings)

        analysis = analyze_article(clean)
        upsert_analysis(engine, post_id, analysis)

        set_post_processed(engine, post_id, checksum)

    return {"author_id": author_id, "posts_seen": len(posts)}