import re


def normalize_title(title: str) -> str:
    if not title or not title.strip():
        raise ValueError("title must not be empty")

    return re.sub(r"\s+", " ", title.casefold().strip())
