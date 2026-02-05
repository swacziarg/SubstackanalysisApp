from dotenv import load_dotenv
load_dotenv()   # must be first line

import os
from fastapi import FastAPI, Header, HTTPException
from app.worker import run_ingestion
from app.db.engine import get_engine
from app.db.queries import list_author_urls, search_post_chunks, list_authors,list_posts_for_author, get_post, get_author_analyses,get_author_profile
from app.ai.chat import answer_question
from app.ai.embeddings import embed_texts
from fastapi.middleware.cors import CORSMiddleware

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
    url: str,
    x_api_key: str | None = Header(default=None, alias="x-api-key")
):
    verify(x_api_key)
    return run_ingestion([url])

@app.post("/ingest/update")
def ingest_all(
    x_api_key: str | None = Header(default=None, alias="x-api-key")
):
    verify(x_api_key)

    engine = get_engine()
    urls = list_author_urls(engine)

    return run_ingestion(urls, limit=5)


@app.post("/posts/{post_id}/ask")
def ask(post_id: int, question: str):
    engine = get_engine()

    query_vec = embed_texts(question)
    contexts = search_post_chunks(engine, post_id, query_vec)

    if not contexts:
        return {"answer": "No content available for this article yet."}

    answer = answer_question(question, contexts)

    return {
        "answer": answer,
        "sources": contexts
    }

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

@app.get("/authors/{author_id}/profile")
def author_profile(author_id: int):
    engine = get_engine()
    profile = get_author_profile(engine, author_id)

    if not profile:
        return {"status": "profile_not_computed"}

    return profile

@app.get("/compare")
def compare(author_a: int, author_b: int):
    engine = get_engine()

    rows_a = get_author_analyses(engine, author_a)
    rows_b = get_author_analyses(engine, author_b)

    from app.analysis.author_compare import disagreement, get_author_claims, get_author_topics, compare_topics, polarity

    topics = compare_topics(get_author_topics(rows_a), get_author_topics(rows_b))

    return {
        **topics,
        "disagreement": disagreement(get_author_claims(rows_a), get_author_claims(rows_b))
    }