import unittest
from tourism_enrichment.quality_gate import assess, normalize_name

BASE = {"name_th": "หาดบางแสน", "province": "ชลบุรี", "latitude": 13.28, "longitude": 100.92, "source": "wikidata", "source_id": "Q-test", "source_url": "https://www.wikidata.org/wiki/Q-test"}

class QualityGateTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize_name("  หาด  บางแสน "), "หาด บางแสน")
    def test_valid_candidate_needs_review(self):
        r = assess([BASE])
        self.assertEqual((r["approved"], r["needs_review"]), (0, 1))
    def test_invalid_coordinates_rejected(self):
        r = assess([{**BASE, "latitude": 51.0}])
        self.assertEqual(r["rejected"], 1)
    def test_duplicate_against_existing(self):
        r = assess([BASE], [BASE])
        self.assertIn("duplicate_source_id", r["decisions"][0]["issues"])
    def test_duplicate_within_batch(self):
        r = assess([BASE, BASE])
        self.assertIn("duplicate_source_id", r["decisions"][1]["issues"])
    def test_missing_provenance(self):
        r = assess([{**BASE, "source_url": ""}])
        self.assertIn("missing_source_url", r["decisions"][0]["issues"])

if __name__ == "__main__":
    unittest.main()
