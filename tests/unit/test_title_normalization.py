import unittest

from news_intelligence.title_normalization import normalize_title


class TestTitleNormalization(unittest.TestCase):
    def test_normalizes_case(self):
        self.assertEqual(
            normalize_title("Breaking NEWS"),
            "breaking news",
        )

    def test_trims_and_collapses_whitespace(self):
        self.assertEqual(
            normalize_title("  Breaking   news \n today  "),
            "breaking news today",
        )

    def test_preserves_punctuation(self):
        self.assertNotEqual(
            normalize_title("Who won?"),
            normalize_title("Who won!"),
        )

    def test_handles_unicode_casefolding(self):
        self.assertEqual(
            normalize_title("STRASSE"),
            normalize_title("Straße"),
        )

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            normalize_title("   ")

    def test_equivalent_titles_have_same_normalized_value(self):
        first_title = "Breaking NEWS:  Major Update"
        second_title = "  breaking news: major   update  "

        self.assertEqual(
            normalize_title(first_title),
            normalize_title(second_title),
        )


if __name__ == "__main__":
    unittest.main()
