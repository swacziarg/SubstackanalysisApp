import json


def ensure_list(value):
    """
    Accepts:
    - jsonb decoded list (psycopg)
    - json string
    - None
    - garbage

    Always returns a safe python list
    """
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return []
        except Exception:
            return []

    return []
