def extract_claims(row):
    """
    Convert analysis row into normalized claims.
    Returns list of (text, polarity, confidence)
    """

    claims = []

    if row.get("main_claim"):
        claims.append((row["main_claim"], 1.0, row.get("confidence", 0.5)))

    for a in row.get("arguments_for") or []:
        claims.append((a, 0.7, row.get("confidence", 0.5)))

    for a in row.get("arguments_against") or []:
        claims.append((a, -0.7, row.get("confidence", 0.5)))

    return claims
