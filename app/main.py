from dotenv import load_dotenv

load_dotenv()  # must be first line

import os
from fastapi import FastAPI, Header, HTTPException
from app.worker import run_ingestion
from app.db.engine import get_engine
from app.db.queries import (
    list_author_urls,
    search_post_chunks,
    list_authors,
    list_posts_for_author,
    get_post,
    get_author_analyses,
    get_author_profile,
)
from app.ai.chat import answer_question
from app.ai.embeddings import embed_texts
from fastapi.middleware.cors import CORSMiddleware
from app.analysis.backfill_beliefs import backfill_author_beliefs
from app.db.cached_profiles import upsert_cached_profile
from app.db.queries import get_author_profile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
API_KEY = os.getenv("INGEST_SECRET", "dev-secret")
print("EXPECTED API KEY:", repr(API_KEY))


def verify(key: str | None):
    print("API KEY RECEIVED:", repr(key))
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/ingest/author")
def ingest_author_endpoint(
    url: str, x_api_key: str | None = Header(default=None, alias="x-api-key")
):
    verify(x_api_key)
    return run_ingestion([url])


@app.post("/ingest/update")
def ingest_all(x_api_key: str | None = Header(default=None, alias="x-api-key")):
    verify(x_api_key)

    engine = get_engine()
    urls = list_author_urls(engine)

    return run_ingestion(urls, limit=5)


from pydantic import BaseModel


class Question(BaseModel):
    question: str


@app.post("/posts/{post_id}/ask")
def ask(post_id: int, payload: Question):
    question = payload.question
    engine = get_engine()

    query_vec = embed_texts(question)
    contexts = search_post_chunks(engine, post_id, query_vec)

    if not contexts:
        return {"answer": "No content available for this article yet."}

    answer = answer_question(question, contexts)

    return {"answer": answer, "sources": contexts}


@app.get("/authors")
def get_authors():
    engine = get_engine()
    return list_authors(engine)


@app.get("/authors/{author_id}/posts")
def get_author_posts(author_id: int):
    engine = get_engine()
    return list_posts_for_author(engine, author_id)


@app.get("/posts/{post_id}")
def read_post(post_id: int):
    engine = get_engine()
    post = get_post(engine, post_id)
    if not post:
        raise HTTPException(404)
    return post

from app.db.cached_profiles import get_cached_profile

@app.get("/authors/{author_id}/profile")
def author_profile(author_id: int):
    engine = get_engine()

    cached = get_cached_profile(engine, author_id)
    if cached:
        return cached

    return {"status": "profile_not_computed"}

@app.get("/compare")
def compare(author_a: int, author_b: int):
    engine = get_engine()

    rows_a = get_author_analyses(engine, author_a)
    rows_b = get_author_analyses(engine, author_b)

    from app.analysis.author_compare import (
        disagreement,
        get_author_claims,
        get_author_topics,
        compare_topics,
    )

    topics = compare_topics(get_author_topics(rows_a), get_author_topics(rows_b))

    return {
        **topics,
        "disagreement": disagreement(
            get_author_claims(rows_a), get_author_claims(rows_b)
        ),
    }


@app.post("/admin/backfill_beliefs/{author_id}")
def backfill(author_id: int):
    engine = get_engine()
    return backfill_author_beliefs(engine, author_id)


@app.post("/admin/embed_claims")
def embed_claims():
    engine = get_engine()
    from app.analysis.embed_claims import embed_missing_claims

    return {"embedded": embed_missing_claims(engine)}


@app.post("/admin/build_beliefs/{author_id}")
def build_beliefs(author_id: int):
    engine = get_engine()
    from app.analysis.build_beliefs import build_author_beliefs

    return build_author_beliefs(engine, author_id)


@app.post("/admin/classify_claims")
def classify_claims():
    engine = get_engine()
    from app.analysis.classify_claims import classify_missing_claims

    return classify_missing_claims(engine)

@app.post("/admin/build_relations/{author_id}")
def build_relations_api(author_id: int):
    engine = get_engine()
    from app.analysis.belief_relations import build_relations

    result = build_relations(engine, author_id)

    profile = get_author_profile(engine, author_id)
    if profile:
        upsert_cached_profile(engine, author_id, profile)

    return result


@app.get("/authors/{author_id}/evolution")
def evolution(author_id: int):
    engine = get_engine()
    from app.analysis.belief_drift import detect_belief_changes

    return detect_belief_changes(engine, author_id)


@app.post("/authors/{author_id}/ask")
def ask_author(author_id: int, question: str):
    engine = get_engine()

    from app.db.queries import get_author_claims

    claims = get_author_claims(engine, author_id)

    if not claims:
        return {"answer": "Not enough data about this author yet."}

    from app.ai.chat import answer_question

    answer = answer_question(question, claims)

    return {"answer": answer}
