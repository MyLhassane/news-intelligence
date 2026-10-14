import unittest

from news_intelligence.url_normalization import normalize_url


class TestURLNormalization(unittest.TestCase):
    def test_trims_surrounding_whitespace(self):
        self.assertEqual(
            normalize_url("  https://example.org/article  "),
            "https://example.org/article",
        )

    def test_lowercases_scheme_and_hostname(self):
        self.assertEqual(
            normalize_url("HTTPS://EXAMPLE.ORG/article"),
            "https://example.org/article",
        )

    def test_removes_default_ports(self):
        self.assertEqual(
            normalize_url("http://example.org:80/article"),
            "http://example.org/article",
        )
        self.assertEqual(
            normalize_url("https://example.org:443/article"),
            "https://example.org/article",
        )

    def test_removes_known_tracking_parameters(self):
        self.assertEqual(
            normalize_url(
                "https://example.org/article"
                "?utm_source=newsletter&utm_campaign=weekly&id=42"
            ),
            "https://example.org/article?id=42",
        )

    def test_preserves_non_tracking_query_parameters(self):
        self.assertEqual(
            normalize_url("https://example.org/article?id=42&page=2"),
            "https://example.org/article?id=42&page=2",
        )

    def test_preserves_http_vs_https(self):
        self.assertNotEqual(
            normalize_url("http://example.org/article"),
            normalize_url("https://example.org/article"),
        )

    def test_rejects_empty_url(self):
        with self.assertRaises(ValueError):
            normalize_url("   ")

    def test_preserves_repeated_query_parameters(self):
        self.assertEqual(
            normalize_url(
                "https://example.org/article?tag=a&tag=b"
            ),
            "https://example.org/article?tag=a&tag=b",
        )

    def test_removes_tracking_parameters_case_insensitively(self):
        self.assertEqual(
            normalize_url(
                "https://example.org/article?UTM_SOURCE=feed&id=42"
            ),
            "https://example.org/article?id=42",
        )

    def test_preserves_encoded_path(self):
        self.assertEqual(
            normalize_url("https://example.org/news%2Fworld?id=42"),
            "https://example.org/news%2Fworld?id=42",
        )

    def test_rejects_urls_with_credentials(self):
        with self.assertRaises(ValueError):
            normalize_url("https://user:password@example.org/article")

    def test_removes_percent_encoded_tracking_parameter_name(self):
        self.assertEqual(
            normalize_url(
                "https://example.org/article?utm%5Fsource=feed&id=42"
            ),
            "https://example.org/article?id=42",
        )

if __name__ == "__main__":
    unittest.main()
