import unittest
from datetime import datetime, timezone

from news_intelligence.article_normalization import normalize_article


class TestArticleNormalization(unittest.TestCase):
    def test_normalize_article_fields(self):
        article = {
            "title": "Test Article",
            "url": "https://example.org/article",
            "author": "Test Author",
            "published_at": "Thu, 01 Oct 2026 09:00:00 GMT",
            "description": "Test summary",
        }

        normalized = normalize_article(article)

        self.assertEqual(normalized["title"], "Test Article")
        self.assertEqual(
            normalized["url"],
            "https://example.org/article",
        )
        self.assertEqual(normalized["author"], "Test Author")
        self.assertEqual(normalized["summary"], "Test summary")
        self.assertIsNone(normalized["content"])

        self.assertEqual(
            normalized["published_at"],
            datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
        )

    def test_optional_fields_can_be_missing(self):
        article = {
            "title": "Test Article",
            "url": "https://example.org/article",
            "published_at": None,
            "author": None,
            "description": None,
        }

        normalized = normalize_article(article)

        self.assertEqual(normalized["title"], "Test Article")
        self.assertEqual(
            normalized["url"],
            "https://example.org/article",
        )
        self.assertIsNone(normalized["author"])
        self.assertIsNone(normalized["published_at"])
        self.assertIsNone(normalized["summary"])
        self.assertIsNone(normalized["content"])


if __name__ == "__main__":
    unittest.main()
