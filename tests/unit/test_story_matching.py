import unittest

from news_intelligence.story_matching import match_story


class TestStoryMatching(unittest.TestCase):
    def setUp(self):
        self.existing_stories = [
            {"id": 101, "title": "Global Climate Summit Reaches Landmark Agreement"},
            {"id": 102, "title": "Tech Giant Announces Breakthrough Quantum Processor"},
        ]

    def test_match_existing_story(self):
        article = {"title": "Global Climate Summit Reaches Historic Agreement"}
        result = match_story(article, self.existing_stories, threshold=0.5)

        self.assertEqual(result["outcome"], "MATCH")
        self.assertEqual(result["story_id"], 101)

    def test_new_story_when_no_overlap(self):
        article = {"title": "Local Bakery Wins National Award for Best Sourdough"}
        result = match_story(article, self.existing_stories, threshold=0.5)

        self.assertEqual(result["outcome"], "NEW_STORY")
        self.assertIsNone(result["story_id"])

    def test_review_outcome_on_ambiguous_match(self):
        stories = [
            {"id": 201, "title": "Election Results Show Tight Race in Capital"},
            {"id": 202, "title": "Election Results Show Tight Race in Suburbs"},
        ]
        article = {"title": "Election Results Show Tight Race"}
        result = match_story(article, stories, threshold=0.4)

        self.assertEqual(result["outcome"], "REVIEW")
        self.assertIsNone(result["story_id"])

    def test_review_outcome_on_partial_uncertain_overlap(self):
        article = {"title": "Global Climate Updates"}
        result = match_story(article, self.existing_stories, threshold=0.6)

        self.assertEqual(result["outcome"], "REVIEW")
        self.assertIsNone(result["story_id"])

    def test_missing_title_returns_review(self):
        article = {"title": ""}
        result = match_story(article, self.existing_stories)

        self.assertEqual(result["outcome"], "REVIEW")
        self.assertIsNone(result["story_id"])


if __name__ == "__main__":
    unittest.main()
