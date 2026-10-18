from news_intelligence.title_normalization import normalize_title


def match_story(article: dict, existing_stories: list[dict], threshold: float = 0.6) -> dict:
    """
    Deterministically match an incoming article against a list of existing stories.

    Each item in existing_stories should be a dict with:
      - "id": int or str
      - "title": str (story title)

    Returns a dict with:
      - "outcome": "MATCH", "NEW_STORY", or "REVIEW"
      - "story_id": matched story id if MATCH, else None
      - "confidence": float or description
      - "reason": str
    """
    article_title = article.get("title")
    if not article_title:
        return {
            "outcome": "REVIEW",
            "story_id": None,
            "reason": "Article lacks a valid title for story matching.",
        }

    try:
        norm_article_title = normalize_title(article_title)
    except ValueError:
        return {
            "outcome": "REVIEW",
            "story_id": None,
            "reason": "Article title normalization failed.",
        }

    article_words = set(norm_article_title.split())
    if not article_words:
        return {
            "outcome": "REVIEW",
            "story_id": None,
            "reason": "Article title contains no indexable words after normalization.",
        }

    best_match = None
    best_score = 0.0
    second_best_score = 0.0

    for story in existing_stories:
        story_title = story.get("title")
        if not story_title:
            continue

        try:
            norm_story_title = normalize_title(story_title)
        except ValueError:
            continue

        story_words = set(norm_story_title.split())
        if not story_words:
            continue

        # Jaccard similarity / token overlap
        intersection = len(article_words.intersection(story_words))
        union = len(article_words.union(story_words))
        score = intersection / union if union > 0 else 0.0

        if score > best_score:
            second_best_score = best_score
            best_score = score
            best_match = story
        elif score > second_best_score:
            second_best_score = score

    # Decision logic respecting uncertainty (REVIEW)
    if best_score >= threshold:
        # Check for ambiguity (close scores between top two stories)
        if best_score - second_best_score < 0.15 and second_best_score >= threshold * 0.7:
            return {
                "outcome": "REVIEW",
                "story_id": None,
                "reason": f"Ambiguous match between stories with scores {best_score:.2f} and {second_best_score:.2f}.",
            }

        return {
            "outcome": "MATCH",
            "story_id": best_match.get("id"),
            "score": best_score,
            "reason": f"Matched story '{best_match.get('title')}' with similarity score {best_score:.2f}.",
        }

    if best_score > 0.25 and best_score < threshold:
        return {
            "outcome": "REVIEW",
            "story_id": None,
            "reason": f"Partial title overlap (score {best_score:.2f}) is below confidence threshold ({threshold}) but too high for a new story.",
        }

    return {
        "outcome": "NEW_STORY",
        "story_id": None,
        "score": best_score,
        "reason": f"No existing story sufficiently matches article (best similarity score {best_score:.2f}).",
    }
