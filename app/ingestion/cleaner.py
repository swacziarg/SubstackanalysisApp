from bs4 import BeautifulSoup

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines)