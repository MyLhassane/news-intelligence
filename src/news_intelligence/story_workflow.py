from news_intelligence.story_matching import match_story


def process_article_story_matching(conn, article_id: int, article_title: str, threshold: float = 0.6) -> dict:
    """
    Process an article against persisted stories in the database using the
    deterministic match_story utility.

    Persists relationships in article_stories when outcome is MATCH, creates a new
    story when outcome is NEW_STORY, and leaves association undecided when REVIEW.

    Returns the matching result dictionary.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT id, title FROM stories WHERE status = 'active'")
        rows = cur.fetchall()

    existing_stories = [{"id": r[0], "title": r[1]} for r in rows]
    article = {"title": article_title}

    result = match_story(article, existing_stories, threshold=threshold)
    outcome = result["outcome"]

    with conn.cursor() as cur:
        if outcome == "MATCH":
            story_id = result["story_id"]
            cur.execute(
                """
                INSERT INTO article_stories (article_id, story_id, relation_type, is_primary)
                VALUES (%s, %s, 'coverage', true)
                ON CONFLICT DO NOTHING
                """,
                (article_id, story_id),
            )
        elif outcome == "NEW_STORY":
            cur.execute(
                """
                INSERT INTO stories (title, story_type, status)
                VALUES (%s, 'breaking_news', 'active')
                RETURNING id
                """,
                (article_title,),
            )
            story_id = cur.fetchone()[0]
            result["story_id"] = story_id

            cur.execute(
                """
                INSERT INTO article_stories (article_id, story_id, relation_type, is_primary)
                VALUES (%s, %s, 'coverage', true)
                ON CONFLICT DO NOTHING
                """,
                (article_id, story_id),
            )
        else:
            # REVIEW: association left undecided, no article_stories record inserted
            pass

    return result
