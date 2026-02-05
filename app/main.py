from dotenv import load_dotenv
load_dotenv()   # must be first line

import os
from fastapi import FastAPI, Header, HTTPException
from app.worker import run_ingestion
from app.db.engine import get_engine
from app.db.queries import list_author_urls, search_post_chunks
from app.ai.chat import answer_question
from app.ai.embeddings import embed_texts
                          
app = FastAPI()

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