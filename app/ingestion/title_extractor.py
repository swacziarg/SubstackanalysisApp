from bs4 import BeautifulSoup

def extract_title_from_html(html: str) -> str | None:
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Substack titles are always inside first h1
    h1 = soup.find("h1")
    if not h1:
        return None

    text = h1.get_text(strip=True)
    if not text:
        return None

    # reject junk titles
    if len(text) < 3:
        return None

    return text