import unittest
from pathlib import Path

import psycopg
from psycopg import conninfo

from news_intelligence.article_ingestion import insert_article
from news_intelligence.baseline_ingestion import ingest_feed


DATABASE_URL = "dbname=news_test user=hassan"
ALLOWED_DATABASE_NAMES = {"news_test"}


def require_test_database(database_url: str) -> None:
    parsed = conninfo.conninfo_to_dict(database_url)
    dbname = parsed.get("dbname")
    if dbname not in ALLOWED_DATABASE_NAMES:
        raise AssertionError(
            f"Integration tests must not run against database '{dbname}'. "
            f"Only {sorted(ALLOWED_DATABASE_NAMES)} is permitted."
        )


def require_connected_database_is_test(conn) -> None:
    actual_dbname = conn.info.dbname
    if actual_dbname not in ALLOWED_DATABASE_NAMES:
        raise AssertionError(
            f"Connected database '{actual_dbname}' is not permitted. "
            f"Only {sorted(ALLOWED_DATABASE_NAMES)} is permitted."
        )


FIXTURE = Path("tests/fixtures/feeds/baseline.xml")


class TestArticleIngestion(unittest.TestCase):
    def test_insert_article(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO source_feeds (
                            source_id,
                            type,
                            url,
                            section,
                            language
                        )
                        VALUES (
                            1,
                            'rss',
                            'https://example.org/test-feed',
                            'test',
                            'en'
                        )
                        RETURNING id
                        """
                    )

                    feed_id = cur.fetchone()[0]

                article = {
                    "title": "Integration Test Article",
                    "url": "https://example.org/integration-test-article",
                    "author": "Test Author",
                    "published_at": None,
                    "language": "en",
                    "content": None,
                    "summary": "Integration test summary",
                }

                inserted = insert_article(
                    conn,
                    source_id=1,
                    feed_id=feed_id,
                    article=article,
                )

                if isinstance(inserted, tuple): inserted = inserted[0]
                self.assertTrue(inserted)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            source_id,
                            feed_id,
                            title,
                            url,
                            author,
                            language,
                            summary
                        FROM articles
                        WHERE source_id = 1
                          AND url = %s
                        """,
                        (article["url"],),
                    )

                    row = cur.fetchone()

                self.assertIsNotNone(row)
                self.assertEqual(row[0], 1)
                self.assertEqual(row[1], feed_id)
                self.assertEqual(row[2], article["title"])
                self.assertEqual(row[3], article["url"])
                self.assertEqual(row[4], article["author"])
                self.assertEqual(row[5], article["language"])
                self.assertEqual(row[6], article["summary"])

            finally:
                conn.rollback()

    def test_exact_duplicate_with_differing_raw_url_formatting_is_rejected_by_classifier(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                article_v1 = {
                    "title": "Classification Routing Test",
                    "url": "https://example.org/path?b=2&a=1",
                    "author": "Author",
                    "summary": "Summary",
                }
                # Same normalized URL (different query parameter ordering and scheme casing)
                article_v2 = {
                    "title": "Classification Routing Test",
                    "url": "HTTPS://EXAMPLE.ORG/path?a=1&b=2",
                    "author": "Author",
                    "summary": "Summary",
                }

                res1 = insert_article(conn, source_id=1, feed_id=None, article=article_v1)
                res2 = insert_article(conn, source_id=1, feed_id=None, article=article_v2)

                if isinstance(res1, tuple): res1 = res1[0]
                self.assertTrue(res1)
                if isinstance(res2, tuple): res2 = res2[0]
                self.assertFalse(res2)  # Proves classify_duplicate governed and rejected insertion even with raw url differences

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        WHERE source_id = 1
                          AND title = 'Classification Routing Test'
                        """
                    )
                    count = cur.fetchone()[0]

                self.assertEqual(count, 1)

            finally:
                conn.rollback()

    def test_duplicate_article_is_ignored(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO source_feeds (
                            source_id,
                            type,
                            url,
                            section,
                            language
                        )
                        VALUES (
                            1,
                            'rss',
                            'https://example.org/test-feed-duplicate',
                            'test',
                            'en'
                        )
                        RETURNING id
                        """
                    )

                    feed_id = cur.fetchone()[0]

                article = {
                    "title": "Duplicate Test Article",
                    "url": "https://example.org/duplicate-test-article",
                    "author": "Original Author",
                    "published_at": None,
                    "language": "en",
                    "content": None,
                    "summary": "Original summary",
                }

                first_insert = insert_article(
                    conn,
                    source_id=1,
                    feed_id=feed_id,
                    article=article,
                )

                second_insert = insert_article(
                    conn,
                    source_id=1,
                    feed_id=feed_id,
                    article={
                        **article,
                        "title": "Changed Title",
                        "author": "Changed Author",
                        "summary": "Changed summary",
                    },
                )

                if isinstance(first_insert, tuple): first_insert = first_insert[0]
                self.assertTrue(first_insert)
                if isinstance(second_insert, tuple): second_insert = second_insert[0]
                self.assertFalse(second_insert)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            COUNT(*),
                            MIN(title),
                            MIN(author),
                            MIN(summary)
                        FROM articles
                        WHERE source_id = 1
                          AND url = %s
                        """,
                        (article["url"],),
                    )

                    count, title, author, summary = cur.fetchone()

                self.assertEqual(count, 1)
                self.assertEqual(title, "Duplicate Test Article")
                self.assertEqual(author, "Original Author")
                self.assertEqual(summary, "Original summary")

            finally:
                conn.rollback()

    def test_same_content_with_different_urls_is_allowed(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                article = {
                    "title": "Identical Content Test Article",
                    "author": "Test Author",
                    "published_at": None,
                    "language": "en",
                    "content": "Identical article content for deduplication testing.",
                    "summary": "Identical summary",
                }

                first_insert = insert_article(
                    conn,
                    source_id=1,
                    feed_id=None,
                    article={
                        **article,
                        "url": "https://example.org/content-copy-a",
                    },
                )

                second_insert = insert_article(
                    conn,
                    source_id=1,
                    feed_id=None,
                    article={
                        **article,
                        "url": "https://example.org/content-copy-b",
                    },
                )

                if isinstance(first_insert, tuple): first_insert = first_insert[0]
                self.assertTrue(first_insert)
                self.assertTrue(second_insert)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        WHERE source_id = 1
                          AND url IN (
                              'https://example.org/content-copy-a',
                              'https://example.org/content-copy-b'
                          )
                        """,
                    )

                    count = cur.fetchone()[0]

                self.assertEqual(count, 2)

            finally:
                conn.rollback()

    def test_same_title_with_different_content_is_allowed(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                base_article = {
                    "title": "Breaking News: Test Event",
                    "author": "Test Author",
                    "published_at": None,
                    "language": "en",
                    "summary": None,
                }

                first_insert = insert_article(
                    conn,
                    source_id=1,
                    feed_id=None,
                    article={
                        **base_article,
                        "url": "https://example.org/event-report-a",
                        "content": "The first report describes event A.",
                    },
                )

                second_insert = insert_article(
                    conn,
                    source_id=1,
                    feed_id=None,
                    article={
                        **base_article,
                        "url": "https://example.org/event-report-b",
                        "content": "The second report describes a different event.",
                    },
                )

                if isinstance(first_insert, tuple): first_insert = first_insert[0]
                self.assertTrue(first_insert)
                self.assertTrue(second_insert)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        WHERE source_id = 1
                          AND title = %s
                          AND url IN (
                              'https://example.org/event-report-a',
                              'https://example.org/event-report-b'
                          )
                        """,
                        (base_article["title"],),
                    )

                    count = cur.fetchone()[0]

                self.assertEqual(count, 2)

            finally:
                conn.rollback()

    def test_same_url_from_different_sources_is_allowed(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                article = {
                    "title": "Shared URL Test Article",
                    "url": "https://example.org/shared-url-test",
                    "author": None,
                    "published_at": None,
                    "language": "en",
                    "content": None,
                    "summary": None,
                }

                first_insert = insert_article(
                    conn,
                    source_id=1,
                    feed_id=None,
                    article=article,
                )

                second_insert = insert_article(
                    conn,
                    source_id=2,
                    feed_id=None,
                    article=article,
                )

                if isinstance(first_insert, tuple): first_insert = first_insert[0]
                self.assertTrue(first_insert)
                self.assertTrue(second_insert)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        WHERE url = %s
                          AND source_id IN (1, 2)
                        """,
                        (article["url"],),
                    )

                    count = cur.fetchone()[0]

                self.assertEqual(count, 2)

            finally:
                conn.rollback()

    def test_baseline_feed_ingestion(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO source_feeds (
                            source_id,
                            type,
                            url,
                            section,
                            language
                        )
                        VALUES (
                            1,
                            'rss',
                            'https://example.org/baseline-feed',
                            'test',
                            'en'
                        )
                        RETURNING id
                        """
                    )

                    feed_id = cur.fetchone()[0]

                result = ingest_feed(
                    conn,
                    FIXTURE,
                    source_id=1,
                    feed_id=feed_id,
                )

                self.assertEqual(result["parsed"], 3)
                self.assertEqual(result["inserted"], 3)
                self.assertEqual(result["skipped"], 0)
                self.assertEqual(result["rejected"], [])

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        WHERE source_id = 1
                          AND feed_id = %s
                        """,
                        (feed_id,),
                    )

                    count = cur.fetchone()[0]

                self.assertEqual(count, 3)

            finally:
                conn.rollback()

    def test_baseline_feed_rerun_skips_existing_articles(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO source_feeds (
                            source_id,
                            type,
                            url,
                            section,
                            language
                        )
                        VALUES (
                            1,
                            'rss',
                            'https://example.org/baseline-feed-rerun',
                            'test',
                            'en'
                        )
                        RETURNING id
                        """
                    )

                    feed_id = cur.fetchone()[0]

                first_result = ingest_feed(
                    conn,
                    FIXTURE,
                    source_id=1,
                    feed_id=feed_id,
                )

                second_result = ingest_feed(
                    conn,
                    FIXTURE,
                    source_id=1,
                    feed_id=feed_id,
                )

                self.assertEqual(first_result["parsed"], 3)
                self.assertEqual(first_result["inserted"], 3)
                self.assertEqual(first_result["skipped"], 0)
                self.assertEqual(first_result["rejected"], [])

                self.assertEqual(second_result["parsed"], 3)
                self.assertEqual(second_result["inserted"], 0)
                self.assertEqual(second_result["skipped"], 3)
                self.assertEqual(second_result["rejected"], [])

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        WHERE source_id = 1
                          AND feed_id = %s
                        """,
                        (feed_id,),
                    )

                    count = cur.fetchone()[0]

                self.assertEqual(count, 3)

            finally:
                conn.rollback()

    def test_invalid_articles_are_rejected(self):
        invalid_fixture = Path("tests/fixtures/feeds/invalid.xml")

        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO source_feeds (
                            source_id,
                            type,
                            url,
                            section,
                            language
                        )
                        VALUES (
                            1,
                            'rss',
                            'https://example.org/invalid-feed',
                            'test',
                            'en'
                        )
                        RETURNING id
                        """
                    )

                    feed_id = cur.fetchone()[0]

                result = ingest_feed(
                    conn,
                    invalid_fixture,
                    source_id=1,
                    feed_id=feed_id,
                )

                self.assertEqual(result["parsed"], 2)
                self.assertEqual(result["inserted"], 0)
                self.assertEqual(result["skipped"], 0)
                self.assertEqual(len(result["rejected"]), 2)

                rejected_errors = [
                    item["errors"]
                    for item in result["rejected"]
                ]

                self.assertIn(["title"], rejected_errors)
                self.assertIn(["url"], rejected_errors)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        WHERE feed_id = %s
                        """,
                        (feed_id,),
                    )

                    count = cur.fetchone()[0]

                self.assertEqual(count, 0)

            finally:
                conn.rollback()

    def test_malformed_feed_fails_before_insertion(self):
        malformed_fixture = Path("tests/fixtures/feeds/malformed.xml")

        malformed_fixture.write_text(
            "<rss><channel><item><title>Broken",
            encoding="utf-8",
        )

        try:
            require_test_database(DATABASE_URL)
            with psycopg.connect(DATABASE_URL) as conn:
                conn.autocommit = False
                require_connected_database_is_test(conn)

                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO source_feeds (
                                source_id,
                                type,
                                url,
                                section,
                                language
                            )
                            VALUES (
                                1,
                                'rss',
                                'https://example.org/malformed-feed',
                                'test',
                                'en'
                            )
                            RETURNING id
                            """
                        )

                        feed_id = cur.fetchone()[0]

                    with self.assertRaises(Exception):
                        ingest_feed(
                            conn,
                            malformed_fixture,
                            source_id=1,
                            feed_id=feed_id,
                        )

                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT COUNT(*)
                            FROM articles
                            WHERE feed_id = %s
                            """,
                            (feed_id,),
                        )

                        count = cur.fetchone()[0]

                    self.assertEqual(count, 0)

                finally:
                    conn.rollback()

        finally:
            malformed_fixture.unlink(missing_ok=True)


class FakeConnectionInfo:
    def __init__(self, dbname: str):
        self.dbname = dbname


class FakeConnection:
    def __init__(self, dbname: str):
        self.info = FakeConnectionInfo(dbname)


class TestDatabaseSafeguard(unittest.TestCase):
    def test_safeguard_rejects_production_database_name(self):
        production_url = "dbname=news user=hassan"
        with self.assertRaises(AssertionError) as context:
            require_test_database(production_url)

        self.assertIn("news", str(context.exception))
        self.assertIn("news_test", str(context.exception))

    def test_safeguard_rejects_arbitrary_non_test_database(self):
        arbitrary_url = "dbname=some_other_db user=hassan"
        with self.assertRaises(AssertionError):
            require_test_database(arbitrary_url)

    def test_safeguard_allows_news_test_database(self):
        require_test_database(DATABASE_URL)

    def test_connected_safeguard_rejects_production_database(self):
        with self.assertRaises(AssertionError) as context:
            require_connected_database_is_test(FakeConnection("news"))

        self.assertIn("news", str(context.exception))
        self.assertIn("news_test", str(context.exception))

    def test_connected_safeguard_rejects_arbitrary_non_test_database(self):
        with self.assertRaises(AssertionError):
            require_connected_database_is_test(FakeConnection("some_other_db"))

    def test_connected_safeguard_allows_news_test_database(self):
        require_connected_database_is_test(FakeConnection("news_test"))


if __name__ == "__main__":
    unittest.main()
