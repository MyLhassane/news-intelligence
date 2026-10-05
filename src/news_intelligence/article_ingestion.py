def insert_article(conn, source_id: int, feed_id: int, article: dict) -> bool:
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

    return row is not None
