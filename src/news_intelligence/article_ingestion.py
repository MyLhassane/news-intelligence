from news_intelligence.article_deduplication import classify_duplicate
from news_intelligence.story_workflow import process_article_story_matching


def insert_article(conn, source_id: int, feed_id: int, article: dict) -> tuple[bool, int | None]:
    """
    Insert an article into the database, incorporating deterministic deduplication
    classification (EXACT_DUPLICATE, NEAR_DUPLICATE, DISTINCT) against existing
    stored articles for the source before insertion.

    Rules:
    - EXACT_DUPLICATE: Classified prior to insertion and skipped (returns (False, None) without inserting).
    - NEAR_DUPLICATE: Same source, different URL, but matching normalized title.
      Preserved as a distinct record (no overwrite or deletion) while classified and inserted.
    - DISTINCT: Inserted normally.

    Returns:
        (inserted_bool, article_id_or_none)
    """
    # 1. Fetch existing articles for this source to run deduplication classification
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, source_id, title, url, summary, content, published_at, author, language
            FROM articles
            WHERE source_id = %s
            """,
            (source_id,),
        )
        rows = cur.fetchall()

    existing_articles = []
    for row in rows:
        existing_articles.append({
            "id": row[0],
            "source_id": row[1],
            "title": row[2],
            "url": row[3],
            "summary": row[4],
            "content": row[5],
            "published_at": row[6],
            "author": row[7],
            "language": row[8],
        })

    # 2. Check incoming article against existing articles using classifier
    incoming = {
        "source_id": source_id,
        "title": article["title"],
        "url": article["url"],
    }

    classification = "DISTINCT"
    for existing in existing_articles:
        res = classify_duplicate(existing, incoming)
        if res == "EXACT_DUPLICATE":
            classification = "EXACT_DUPLICATE"
            break
        elif res == "NEAR_DUPLICATE":
            classification = "NEAR_DUPLICATE"

    # 3. Explicitly govern insertion behavior based on classification result
    if classification == "EXACT_DUPLICATE":
        return False, None

    query = """
        INSERT INTO articles (
            source_id,
            feed_id,
            title,
            url,
            author,
            published_at,
            language,
            content,
            summary
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (source_id, url) DO NOTHING
        RETURNING id
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                source_id,
                feed_id,
                article["title"],
                article["url"],
                article.get("author"),
                article.get("published_at"),
                article.get("language"),
                article.get("content"),
                article.get("summary"),
            ),
        )

        row = cur.fetchone()

    if row is not None:
        article_id = row[0]
        # Automatically trigger story matching during ingestion as required by Stage 3
        # Let errors propagate explicitly; do not swallow silently
        process_article_story_matching(conn, article_id=article_id, article_title=article["title"])
        return True, article_id

    # If ON CONFLICT DO NOTHING triggered because of a raw URL conflict not caught earlier
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM articles WHERE source_id = %s AND url = %s",
            (source_id, article["url"]),
        )
        existing_row = cur.fetchone()
        if existing_row:
            return False, existing_row[0]

    return False, None
