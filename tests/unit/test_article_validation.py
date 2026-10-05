import unittest

from news_intelligence.article_validation import validate_article


class TestArticleValidation(unittest.TestCase):
    def test_valid_article(self):
        article = {
            "title": "Test Article",
            "url": "https://example.org/article",
            "author": "Test Author",
            "published_at": "Thu, 01 Oct 2026 09:00:00 GMT",
            "description": "Test description",
        }

        self.assertEqual(validate_article(article), [])

    def test_missing_title(self):
        article = {
            "title": None,
            "url": "https://example.org/article",
        }

        errors = validate_article(article)

        self.assertIn("title", errors)

    def test_missing_url(self):
        article = {
            "title": "Test Article",
            "url": None,
        }

        errors = validate_article(article)

        self.assertIn("url", errors)

    def test_optional_fields_can_be_missing(self):
        article = {
            "title": "Test Article",
            "url": "https://example.org/article",
        }

        self.assertEqual(validate_article(article), [])


if __name__ == "__main__":
    unittest.main()
