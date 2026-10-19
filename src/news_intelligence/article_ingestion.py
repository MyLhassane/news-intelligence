from news_intelligence.article_deduplication import classify_duplicate


def insert_article(conn, source_id: int, feed_id: int, article: dict) -> bool:
    """
    Insert an article into the database, incorporating deterministic deduplication
    classification (EXACT_DUPLICATE, NEAR_DUPLICATE, DISTINCT) against existing
    stored articles for the source before insertion.

    Rules:
    - EXACT_DUPLICATE: Classified prior to insertion and skipped (returns False without inserting).
      This handles both raw matching and normalized URL matches (e.g. differing casing/query parameter ordering).
    - NEAR_DUPLICATE: Same source, different URL, but matching normalized title.
      Preserved as a distinct record (no overwrite or deletion) while classified and inserted.
    - DISTINCT: Inserted normally.
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
        # When classified as an exact duplicate (whether raw URL match or normalized URL match),
        # skip insertion entirely and return False.
        return False

    # For NEAR_DUPLICATE and DISTINCT, insertion is permitted.
    # Note: If normalized URL matches an existing article but raw URL differs slightly without being caught
    # by classify_duplicate, ON CONFLICT DO NOTHING handles raw uniqueness safely.
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

    inserted = row is not None

    return inserted
