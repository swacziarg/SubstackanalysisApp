import os
from groq import Groq

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM = """
You are reconstructing an author's beliefs.

Rules:
- Only use the provided statements
- Do NOT speculate
- Do NOT generalize beyond the text
- If unclear, say: "The author has not expressed a clear view."

Answer in 2–4 sentences max.
"""


def answer_question(question: str, statements: list[str]) -> str:
    context = "\n".join(f"- {s}" for s in statements)

    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": f"""
AUTHOR STATEMENTS:
{context}

QUESTION:
{question}
""",
            },
        ],
    )

    return resp.choices[0].message.content.strip()
