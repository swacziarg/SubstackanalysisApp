from groq import Groq
import os
import json

client = Groq(api_key=os.environ["GROQ_API_KEY"])

PROMPT = """
You are summarizing a thinker's worldview.

Write a concise 3-5 sentence intellectual profile.

Focus on:
- what they believe about the world
- recurring reasoning patterns
- their general orientation (empirical, moral, pragmatic, skeptical, etc)

Beliefs:
{beliefs}

Topics:
{topics}

Bias score:
{bias}

Return JSON:
{{"summary": "..."}}
"""


def build_author_summary(beliefs, topics, bias):
    r = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        temperature=0.2,
        messages=[
            {
                "role": "user",
                "content": PROMPT.format(
                    beliefs="\n".join("- " + b for b in beliefs[:12]),
                    topics=", ".join(topics[:12]),
                    bias=bias,
                ),
            }
        ],
    )

    raw = r.choices[0].message.content

    try:
        return json.loads(raw)["summary"]
    except:
        return beliefs[0] if beliefs else "No summary available"