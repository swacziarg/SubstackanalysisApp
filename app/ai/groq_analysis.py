import json
import os
from groq import Groq


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

import re
import json

def extract_json(text: str) -> dict:
    """
    Attempts to safely extract JSON object from LLM output.
    """

    # 1) find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    raw = match.group(0)

    # 2) remove trailing commas
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)

    # 3) try parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("BAD JSON FROM MODEL:\n", raw[:1000])
        raise

def repair_json(bad_output: str) -> dict:
    """
    Ask the model to convert its previous answer into strict JSON.
    Very cheap + extremely reliable.
    """

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
        messages=[{"role": "user", "content": repair_prompt}]
    )

    fixed = resp.choices[0].message.content.strip()
    return extract_json(fixed)

def analyze_article(clean_text: str) -> dict:
    # Keep token usage sane: analyze only the first ~12k chars + last ~4k chars
    head = clean_text[:12000]
    tail = clean_text[-4000:] if len(clean_text) > 16000 else ""
    payload = head + ("\n\n[...]\n\n" + tail if tail else "")

    resp = _client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": payload}
        ]
    )
    content = resp.choices[0].message.content.strip()

    try:
        return extract_json(content)
    except Exception:
        print("Attempting JSON repair...")
        return repair_json(content)