import unittest

from news_intelligence.claim_evidence_pipeline import trace_claim_provenance


class TestClaimEvidencePipeline(unittest.TestCase):
    def test_trace_claim_through_evidence_to_provenance(self):
        claim = {
            "id": 1,
            "claim_text": "Global carbon emissions decreased by 4% in 2025.",
            "claim_type": "statistical",
            "status": "supported",
        }

        evidence_items = [
            {
                "id": 10,
                "title": "IPCC Annual Emissions Report 2025",
                "type": "official_document",
                "relationship": "supports",
            }
        ]

        provenance_links = [
            {
                "evidence_id": 10,
                "source_id": 50,
                "source_name": "Intergovernmental Panel on Climate Change",
                "relationship": "producer",
            },
            {
                "evidence_id": 10,
                "source_id": 100,
                "source_name": "Reuters",
                "relationship": "publisher",
            },
        ]

        trace = trace_claim_provenance(claim, evidence_items, provenance_links)

        self.assertTrue(trace["traceable"])
        self.assertEqual(trace["claim_id"], 1)
        self.assertEqual(len(trace["evidence_chain"]), 1)

        chain = trace["evidence_chain"][0]
        self.assertEqual(chain["evidence_title"], "IPCC Annual Emissions Report 2025")
        self.assertEqual(len(chain["producers_or_issuers"]), 1)
        self.assertEqual(chain["producers_or_issuers"][0]["source_name"], "Intergovernmental Panel on Climate Change")
        self.assertEqual(chain["producers_or_issuers"][0]["relationship"], "producer")

        self.assertEqual(len(chain["publishers"]), 1)
        self.assertEqual(chain["publishers"][0]["source_name"], "Reuters")
        self.assertEqual(chain["publishers"][0]["relationship"], "publisher")
        self.assertTrue(chain["has_producer_or_issuer"])

    def test_trace_claim_with_missing_claim_raises_error(self):
        with self.assertRaises(ValueError):
            trace_claim_provenance({}, [], [])

    def test_trace_claim_with_contradicting_evidence(self):
        claim = {"id": 2, "claim_text": "The report is accurate."}
        evidence = [{"id": 20, "relationship": "contradicts"}]
        provenance = [{"evidence_id": 20, "source_id": 60, "relationship": "publisher"}]

        trace = trace_claim_provenance(claim, evidence, provenance)

        self.assertTrue(trace["traceable"])
        self.assertEqual(trace["evidence_chain"][0]["relationship"], "contradicts")
        self.assertFalse(trace["evidence_chain"][0]["has_producer_or_issuer"])

    def test_evidence_without_provenance_is_not_fully_traceable(self):
        claim = {"id": 3, "claim_text": "The report is accurate."}
        evidence = [{"id": 30, "relationship": "supports"}]

        trace = trace_claim_provenance(claim, evidence, [])

        self.assertFalse(trace["traceable"])
        self.assertEqual(len(trace["evidence_chain"]), 1)


if __name__ == "__main__":
    unittest.main()
