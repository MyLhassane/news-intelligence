from datetime import datetime
from email.utils import parsedate_to_datetime


def normalize_article(article: dict) -> dict:
    published_at = article.get("published_at")

    if published_at:
        published_at = parsedate_to_datetime(published_at)

    return {
        "title": article.get("title"),
        "url": article.get("url"),
        "author": article.get("author"),
        "published_at": published_at,
        "summary": article.get("description"),
        "content": None,
    }
