def validate_article(article: dict) -> list[str]:
    errors = []

    if not article.get("title"):
        errors.append("title")

    if not article.get("url"):
        errors.append("url")

    return errors
