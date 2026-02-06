from substack_api import Newsletter, Post
import requests


class SubstackClient:
    def __init__(self, newsletter_url: str):
        self.newsletter_url = newsletter_url
        self.nl = Newsletter(newsletter_url)

    def get_posts(self, limit=20):
        return self.nl.get_posts(limit=limit)

    def get_post_html(self, url: str) -> str | None:
        return Post(url).get_content()  # may return paywall message

    def get_post_metadata(self, url: str) -> dict:
        p = Post(url)
        # p.endpoint is already in your debug output
        r = requests.get(p.endpoint, timeout=15)
        r.raise_for_status()
        return r.json()