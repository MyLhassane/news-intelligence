import unittest

import psycopg
from psycopg import conninfo

from news_intelligence.article_ingestion import insert_article


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


class IntegrationStoryMatchingTest(unittest.TestCase):
    def test_ingestion_triggers_story_matching_for_match_new_review(self):
        require_test_database(DATABASE_URL)
        with psycopg.connect(DATABASE_URL) as conn:
            conn.autocommit = False
            require_connected_database_is_test(conn)

            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO stories (title, story_type, status)
                        VALUES ('Climate Summit Agreement', 'breaking_news', 'active')
                        RETURNING id
                        """
                    )
                    existing_story_id = cur.fetchone()[0]
                    cur.execute(
                        """
                        INSERT INTO source_feeds (
                            source_id, type, url, section, language
                        )
                        VALUES (
                            1, 'rss', 'https://example.org/story-matching-feed',
                            'test', 'en'
                        )
                        RETURNING id
                        """
                    )
                    feed_id = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM stories")
                    initial_story_count = cur.fetchone()[0]

                # MATCH reuses the existing story and does not create another.
                match_inserted, match_article_id = insert_article(
                    conn,
                    source_id=1,
                    feed_id=feed_id,
                    article={
                        "title": "Climate Summit Agreement Reaches Milestone",
                        "url": "https://example.org/climate-agreement",
                        "author": "Editor",
                        "published_at": None,
                        "language": "en",
                        "content": None,
                        "summary": "Agreement milestone.",
                    },
                )
                self.assertTrue(match_inserted)
                self.assertIsNotNone(match_article_id)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT story_id, relation_type, is_primary
                        FROM article_stories
                        WHERE article_id = %s
                        """,
                        (match_article_id,),
                    )
                    match_links = cur.fetchall()
                    cur.execute("SELECT COUNT(*) FROM stories")
                    stories_after_match = cur.fetchone()[0]

                self.assertEqual(
                    match_links, [(existing_story_id, "coverage", True)]
                )
                self.assertEqual(stories_after_match, initial_story_count)

                # NEW_STORY creates one active story and one article relationship.
                new_inserted, new_article_id = insert_article(
                    conn,
                    source_id=1,
                    feed_id=feed_id,
                    article={
                        "title": "New Space Telescope Launch",
                        "url": "https://example.org/space-telescope",
                        "author": "Editor",
                        "published_at": None,
                        "language": "en",
                        "content": None,
                        "summary": "Telescope launch.",
                    },
                )
                self.assertTrue(new_inserted)
                self.assertIsNotNone(new_article_id)

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT s.id, s.title, s.status, a.relation_type, a.is_primary
                        FROM article_stories AS a
                        JOIN stories AS s ON s.id = a.story_id
                        WHERE a.article_id = %s
                        """,
                        (new_article_id,),
                    )
                    new_links = cur.fetchall()
                    cur.execute("SELECT COUNT(*) FROM stories")
                    stories_after_new_story = cur.fetchone()[0]

                self.assertEqual(len(new_links), 1)
                new_story_id, title, status, relation_type, is_primary = new_links[0]
                self.assertNotEqual(new_story_id, existing_story_id)
                self.assertEqual(title, "New Space Telescope Launch")
                self.assertEqual(status, "active")
                self.assertEqual(relation_type, "coverage")
                self.assertTrue(is_primary)
                self.assertEqual(stories_after_new_story, initial_story_count + 1)

                # REVIEW persists a valid, ambiguous-title article without a link.
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO stories (title, story_type, status)
                        VALUES
                            ('Election Results Show Tight Race in Capital',
                             'breaking_news', 'active'),
                            ('Election Results Show Tight Race in Suburbs',
                             'breaking_news', 'active')
                        """
                    )
                    cur.execute("SELECT COUNT(*) FROM stories")
                    stories_before_review = cur.fetchone()[0]

                review_inserted, review_article_id = insert_article(
                    conn,
                    source_id=1,
                    feed_id=feed_id,
                    article={
                        "title": "Election Results Show Tight Race",
                        "url": "https://example.org/review-test",
                        "author": "Editor",
                        "published_at": None,
                        "language": "en",
                        "content": None,
                        "summary": None,
                    },
                )
                self.assertTrue(review_inserted)
                self.assertIsNotNone(review_article_id)

                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT COUNT(*) FROM articles WHERE id = %s",
                        (review_article_id,),
                    )
                    article_count = cur.fetchone()[0]
                    cur.execute(
                        "SELECT COUNT(*) FROM article_stories WHERE article_id = %s",
                        (review_article_id,),
                    )
                    review_link_count = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM stories")
                    stories_after_review = cur.fetchone()[0]

                self.assertEqual(article_count, 1)
                self.assertEqual(review_link_count, 0)
                self.assertEqual(stories_after_review, stories_before_review)
            finally:
                conn.rollback()


if __name__ == "__main__":
    unittest.main()
