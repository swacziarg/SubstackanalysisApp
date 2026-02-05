import os
from groq import Groq

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def answer_question(question: str, contexts: list[str]) -> str:
    joined = "\n\n---\n\n".join(contexts)

    prompt = f"""
Answer the user's question using ONLY the provided article excerpts.
If the answer is not contained, say you don't know.

ARTICLE EXCERPTS:
{joined}

QUESTION:
{question}
"""

    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}]
    )

    return resp.choices[0].message.content.strip()