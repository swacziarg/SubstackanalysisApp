from groq import Groq
import os
import json
import re

client = Groq(api_key=os.environ["GROQ_API_KEY"])

PROMPT = """
Determine how the author uses this statement.

ADVANCED = the author is proposing or arguing this idea (even tentatively)
DISCUSSED = the author describes others' beliefs or possibilities without endorsing
META = about the article, reactions, or writing process

Return JSON:
{"type":"ADVANCED"|"DISCUSSED"|"META"}

Statement:
"""

VALID = {"ADVANCED", "DISCUSSED", "META"}


def classify_claim(text: str) -> str:
    r = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        temperature=0,
        messages=[{"role": "user", "content": PROMPT + text}],
    )

    raw = r.choices[0].message.content.strip()

    # 1) try strict JSON
    try:
        t = json.loads(raw).get("type")
        if t in VALID:
            return t
    except:
        pass

    # 2) fallback: regex extraction
    match = re.search(r"(ADVANCED|DISCUSSED|META)", raw)
    if match:
        return match.group(1)

    # 3) final fallback (never None!)
    return "DISCUSSED"
