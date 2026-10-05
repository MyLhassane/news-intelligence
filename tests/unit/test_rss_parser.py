import unittest
from pathlib import Path

from news_intelligence.rss_parser import parse_feed


FIXTURE = Path("tests/fixtures/feeds/baseline.xml")


class TestRSSParser(unittest.TestCase):
    def test_parse_baseline_feed(self):
        items = parse_feed(FIXTURE)

        self.assertEqual(len(items), 3)

        self.assertEqual(items[0]["title"], "Test Article One")
        self.assertEqual(
            items[0]["url"],
            "https://example.org/articles/one",
        )

        self.assertEqual(items[1]["title"], "Test Article Two")
        self.assertEqual(
            items[1]["url"],
            "https://example.org/articles/two",
        )

        self.assertEqual(items[2]["title"], "Test Article Three")
        self.assertEqual(
            items[2]["url"],
            "https://example.org/articles/three",
        )

    def test_parse_optional_fields(self):
        items = parse_feed(FIXTURE)

        self.assertEqual(items[0]["author"], "Test Author One")
        self.assertIsNone(items[1]["author"])
        self.assertEqual(items[2]["author"], "Test Author Three")

        self.assertIsNotNone(items[0]["description"])
        self.assertIsNotNone(items[1]["description"])
        self.assertIsNone(items[2]["description"])

    def test_malformed_feed_fails_clearly(self):
        malformed_feed = FIXTURE.parent / "malformed.xml"
        malformed_feed.write_text(
            "<rss><channel><item><title>Broken",
            encoding="utf-8",
        )

        try:
            with self.assertRaises(Exception):
                parse_feed(malformed_feed)
        finally:
            malformed_feed.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
