import os
from groq import Groq

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def identity_prefix(author_name):
    if not author_name:
        return ""
    return f"The following statements belong to the writer: {author_name}.\n"

# ---------- 1. classify question ----------

def classifier_prompt(author_name: str | None):
    identity = f"The author being discussed is {author_name}.\n" if author_name else ""
    return f"""
You categorize a user's question relative to a specific author's writings.

{identity}

Return ONLY one letter:

A — about the author (identity, beliefs, intentions, opinions, writings)
B — about subjects the author discusses
C — unrelated general knowledge

If the user refers to "the author", it is ALWAYS category A.

Question:
"""


def classify(question: str, author_name: str | None) -> str:
    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0,
        max_tokens=1,
        messages=[
            {"role": "system", "content": classifier_prompt(author_name)},
            {"role": "user", "content": question},
        ],
    )

    label = resp.choices[0].message.content.strip().upper()
    if label not in {"A", "B", "C"}:
        return "C"
    return label


# ---------- 2. prompts ----------

AUTHOR_STRICT = """
You are answering questions about a specific author's views.

You know the author's name and their recorded beliefs.

Rules:
- If asked the author's name, answer directly.
- Only state positions supported by the provided statements
- Do not invent opinions
- If unclear, say: "The author has not expressed a clear view."
- Be concise (2-4 sentences)
"""

AUTHOR_CONTEXTUAL = """
You are explaining a topic informed by an author's writings.

Rules:
- Answer normally
- When relevant, reference the author's tendencies
- Do not attribute claims not grounded in the statements
"""

GENERAL_ASSISTANT = """
You are a knowledgeable assistant.
Answer accurately and concisely.
Do not roleplay the author unless asked about them.
"""


# ---------- 3. answer ----------

def answer_question(question: str, statements: list[str], author_name: str | None = None) -> str:    
    category = classify(question, author_name)
    context = identity_prefix(author_name) + "\n".join(f"- {s}" for s in statements[:20])

    if category == "A":
        system = AUTHOR_STRICT
        user = f"""
AUTHOR STATEMENTS:
{context}

QUESTION:
{question}
"""

    elif category == "B":
        system = AUTHOR_CONTEXTUAL
        user = f"""
AUTHOR RELEVANT IDEAS:
{context}

QUESTION:
{question}
"""

    else:  # C
        system = GENERAL_ASSISTANT
        user = question

    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    return resp.choices[0].message.content.strip()