from news_intelligence.title_normalization import normalize_title
from news_intelligence.url_normalization import normalize_url


def classify_duplicate(existing_article: dict, incoming_article: dict) -> str:
    """
    Classify the relationship between an existing article and an incoming article
    using deterministic normalization utilities.

    Returns:
        - "EXACT_DUPLICATE": same source_id and normalized URL.
        - "NEAR_DUPLICATE": same source_id, different URL, but same normalized title
          (or matching content hash if available).
        - "DISTINCT": different published items (different source or distinct content/title/URL).
    """
    # 1. Check exact duplicate by source and URL
    existing_source = existing_article.get("source_id")
    incoming_source = incoming_article.get("source_id")

    existing_url = existing_article.get("url")
    incoming_url = incoming_article.get("url")

    if existing_source is not None and incoming_source is not None and existing_source == incoming_source:
        if existing_url and incoming_url:
            try:
                norm_existing = normalize_url(existing_url)
                norm_incoming = normalize_url(incoming_url)

                if norm_existing == norm_incoming:
                    return "EXACT_DUPLICATE"
            except ValueError:
                if existing_url.strip() == incoming_url.strip():
                    return "EXACT_DUPLICATE"

    # 2. Check near duplicate (same source, normalized title match)
    existing_title = existing_article.get("title")
    incoming_title = incoming_article.get("title")

    if existing_source is not None and incoming_source is not None and existing_source == incoming_source:
        if existing_title and incoming_title:
            try:
                if normalize_title(existing_title) == normalize_title(incoming_title):
                    if existing_url and incoming_url:
                        try:
                            if normalize_url(existing_url) != normalize_url(incoming_url):
                                return "NEAR_DUPLICATE"
                        except ValueError:
                            pass
            except ValueError:
                pass

    return "DISTINCT"
