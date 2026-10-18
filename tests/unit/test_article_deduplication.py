import unittest

from news_intelligence.article_deduplication import classify_duplicate


class TestArticleDeduplication(unittest.TestCase):
    def test_exact_duplicate_same_source_and_normalized_url(self):
        existing = {
            "source_id": 1,
            "url": "https://example.org/article?utm_source=rss&id=123",
            "title": "Breaking News: Market Rally",
        }
        incoming = {
            "source_id": 1,
            "url": "https://example.org/article?id=123&utm_campaign=test",
            "title": "Breaking News: Market Rally",
        }

        classification = classify_duplicate(existing, incoming)
        self.assertEqual(classification, "EXACT_DUPLICATE")

    def test_exact_duplicate_case_insensitive_url_scheme_and_host(self):
        existing = {
            "source_id": 1,
            "url": "https://EXAMPLE.ORG/article",
            "title": "Test Title",
        }
        incoming = {
            "source_id": 1,
            "url": "HTTPS://example.org/article",
            "title": "Test Title",
        }

        classification = classify_duplicate(existing, incoming)
        self.assertEqual(classification, "EXACT_DUPLICATE")

    def test_near_duplicate_same_source_matching_normalized_title_different_url(self):
        existing = {
            "source_id": 1,
            "url": "https://example.org/story-version-1",
            "title": "  BREAKING:   Market Rally Continues  ",
        }
        incoming = {
            "source_id": 1,
            "url": "https://example.org/story-version-2",
            "title": "breaking: market rally continues",
        }

        classification = classify_duplicate(existing, incoming)
        self.assertEqual(classification, "NEAR_DUPLICATE")

    def test_distinct_different_sources_same_url(self):
        existing = {
            "source_id": 1,
            "url": "https://example.org/shared-wire",
            "title": "Shared Wire Story",
        }
        incoming = {
            "source_id": 2,
            "url": "https://example.org/shared-wire",
            "title": "Shared Wire Story",
        }

        classification = classify_duplicate(existing, incoming)
        self.assertEqual(classification, "DISTINCT")

    def test_distinct_different_urls_different_titles(self):
        existing = {
            "source_id": 1,
            "url": "https://example.org/article-a",
            "title": "First Article Title",
        }
        incoming = {
            "source_id": 1,
            "url": "https://example.org/article-b",
            "title": "Second Article Title",
        }

        classification = classify_duplicate(existing, incoming)
        self.assertEqual(classification, "DISTINCT")

    def test_distinct_same_url_different_source_and_title(self):
        existing = {
            "source_id": 1,
            "url": "https://example.org/common-link",
            "title": "Title One",
        }
        incoming = {
            "source_id": 2,
            "url": "https://example.org/common-link",
            "title": "Title Two",
        }

        classification = classify_duplicate(existing, incoming)
        self.assertEqual(classification, "DISTINCT")


if __name__ == "__main__":
    unittest.main()
