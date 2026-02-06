import os
import re
import json
import hashlib
from groq import Groq

PROMPT_VERSION = "v1"
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-instruct")

_client = Groq(api_key=os.environ["GROQ_API_KEY"])


SYSTEM = """You analyze opinion articles neutrally. First determine if the article has a single coherent thesis.

If not, mark article_type = "multi_topic".

If yes, mark article_type = "argumentative".

Return STRICT JSON ONLY with this shape:
{
 "summary": "...",
 "main_claim": "...",
 "bias_score": -1 to 1,
 "confidence": 0 to 1,
 "arguments_for": ["..."],
 "arguments_against": ["..."],
 "notable_quotes": ["..."],
 "topics": ["..."],
 "entities": ["..."]
}
No markdown. No extra keys.
"""


# ---------- JSON extraction ----------


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    raw = match.group(0)

    # remove trailing commas
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)

    return json.loads(raw)


def repair_json(bad_output: str) -> dict:
    repair_prompt = f"""
Convert the following text into VALID JSON.

Return ONLY JSON. No explanation.

Required schema:
{{
 "summary": "...",
 "main_claim": "...",
 "bias_score": number,
 "confidence": number,
 "arguments_for": [],
 "arguments_against": [],
 "notable_quotes": [],
 "topics": [],
 "entities": []
}}

TEXT:
{bad_output}
"""

    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[{"role": "user", "content": repair_prompt}],
    )

    fixed = resp.choices[0].message.content.strip()
    return extract_json(fixed)


# ---------- Stable hash ----------


def compute_prompt_hash(payload: str) -> str:
    """
    Hash must depend ONLY on:
    - prompt version
    - system prompt
    - analyzed text (trimmed deterministically)
    - model
    """
    h = hashlib.sha256()
    h.update(PROMPT_VERSION.encode())
    h.update(MODEL.encode())
    h.update(SYSTEM.encode())
    h.update(payload.encode())
    return h.hexdigest()


# ---------- Main analysis ----------


def analyze_article(clean_text: str):
    """
    Returns:
        analysis_dict, model_name, prompt_hash
    """

    # deterministic truncation
    head = clean_text[:12000]
    tail = clean_text[-4000:] if len(clean_text) > 16000 else ""
    payload = head + ("\n\n[...]\n\n" + tail if tail else "")

    prompt_hash = compute_prompt_hash(payload)

    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": payload},
        ],
    )

    content = resp.choices[0].message.content.strip()

    try:
        analysis = extract_json(content)
    except Exception:
        print("Attempting JSON repair...")
        analysis = repair_json(content)

    return analysis, MODEL, prompt_hash
