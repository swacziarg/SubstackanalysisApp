def author(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "substack": f"https://{row['subdomain']}.substack.com",
    }


def post_preview(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "published_at": row["published_at"],
        "summary": row["summary"],
        "bias": row["bias_score"],
        "confidence": row["confidence"],
    }


def post_detail(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "url": row["url"],
        "content": row["clean_text"],
        "analysis": {
            "summary": row["summary"],
            "main_claim": row["main_claim"],
            "bias": row["bias_score"],
            "confidence": row["confidence"],
            "arguments_for": row["arguments_for"],
            "arguments_against": row["arguments_against"],
            "quotes": row["notable_quotes"],
            "topics": row["topics"],
            "entities": row["entities"],
        },
    }
