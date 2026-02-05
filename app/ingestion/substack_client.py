from substack_api import Newsletter, Post

class SubstackClient:
    def __init__(self, newsletter_url: str):
        self.newsletter_url = newsletter_url
        self.nl = Newsletter(newsletter_url)

    def get_posts(self, limit=20):
        return self.nl.get_posts(limit=limit)

    def get_post_html(self, url: str) -> str:
        return Post(url).get_content()  # HTML