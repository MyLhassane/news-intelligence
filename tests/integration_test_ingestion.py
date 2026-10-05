import unittest
from pathlib import Path

import psycopg

from news_intelligence.article_ingestion import insert_article
from news_intelligence.baseline_ingestion import ingest_feed


DATABASE_URL = "dbname=news_test user=hassan"
FIXTURE = Path("tests/fixtures/feeds/baseline.xml")


class TestArticleIngestion(unittest.TestCase):
    def test_insert_article(self):
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False

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

    def test_duplicate_article_is_ignored(self):
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False

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

                self.assertTrue(first_insert)
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

    def test_baseline_feed_ingestion(self):
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False

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
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False

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

        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False

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
            with psycopg.connect(DATABASE_URL) as conn:
                conn.autocommit = False

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


if __name__ == "__main__":
    unittest.main()
