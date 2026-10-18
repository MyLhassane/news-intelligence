import unittest

from news_intelligence.assessment_workflow import create_assessment


class TestAssessmentWorkflow(unittest.TestCase):
    def test_create_ai_proposal_assessment(self):
        new_item, history = create_assessment(
            claim_id=10,
            assessment_status="supported",
            actor_type="ai",
            actor_name="claude-model",
            reasoning="Evidence item 101 directly supports the claim.",
            assessment_role="proposal",
        )

        self.assertEqual(new_item["claim_id"], 10)
        self.assertEqual(new_item["assessment_status"], "supported")
        self.assertEqual(new_item["actor_type"], "ai")
        self.assertEqual(new_item["actor_name"], "claude-model")
        self.assertEqual(new_item["assessment_role"], "proposal")
        self.assertEqual(len(history), 1)

    def test_append_only_history_preservation(self):
        prior_history = [
            {
                "id": 1,
                "claim_id": 10,
                "assessment_status": "unclear",
                "actor_type": "rule",
                "actor_name": "baseline-rule",
                "reasoning": "Conflicting evidence present.",
                "assessment_role": "proposal",
                "created_at": "2026-01-01T00:00:00Z",
            }
        ]

        new_item, history = create_assessment(
            claim_id=10,
            assessment_status="supported",
            actor_type="human",
            actor_name="Lead Editor",
            reasoning="Reviewed conflict and verified independent source authority.",
            assessment_role="decision",
            existing_assessments=prior_history,
        )

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["assessment_status"], "unclear")
        self.assertEqual(history[1]["assessment_status"], "supported")
        self.assertEqual(history[1]["assessment_role"], "decision")
        self.assertEqual(history[1]["actor_type"], "human")

    def test_new_id_follows_highest_existing_id(self):
        prior_history = [
            {"id": 1, "claim_id": 10},
            {"id": 3, "claim_id": 10},
        ]

        new_item, history = create_assessment(
            claim_id=10,
            assessment_status="unclear",
            actor_type="rule",
            existing_assessments=prior_history,
        )

        self.assertEqual(new_item["id"], 4)
        self.assertEqual([item["id"] for item in history], [1, 3, 4])

    def test_invalid_actor_raises_error(self):
        with self.assertRaises(ValueError):
            create_assessment(
                claim_id=10,
                assessment_status="supported",
                actor_type="invalid_actor",
            )

    def test_invalid_role_raises_error(self):
        with self.assertRaises(ValueError):
            create_assessment(
                claim_id=10,
                assessment_status="supported",
                actor_type="human",
                assessment_role="invalid_role",
            )

    def test_invalid_status_raises_error(self):
        with self.assertRaises(ValueError):
            create_assessment(
                claim_id=10,
                assessment_status="not_a_status",
                actor_type="human",
            )


if __name__ == "__main__":
    unittest.main()
