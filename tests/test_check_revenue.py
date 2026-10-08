import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_revenue as cr


SUMMARY = {
    "mrr_snapshot": {
        "mrr_display": "$0.00 CAD",
        "mrr_cents": 0,
        "currency": "CAD",
        "paying_subscribers": 0,
        "unavailable": False,
    }
}
TRAJECTORY = {"signup_history_14d": [{"date": "2026-10-07", "signups": 1}, {"date": "2026-10-08", "signups": 0}]}


class CheckRevenueTest(unittest.TestCase):
    def test_extracts_owned_fields(self):
        mrr, paying = cr.mrr_fields(SUMMARY)
        self.assertEqual(mrr, "$0.00 CAD")
        self.assertEqual(paying, "0")
        self.assertEqual(cr.latest_signups(TRAJECTORY), "0 on 2026-10-08")

    def test_missing_snapshot_is_not_invented(self):
        mrr, paying = cr.mrr_fields({})
        self.assertEqual(mrr, "not returned by the API")
        self.assertEqual(paying, "not returned by the API")
        self.assertEqual(cr.latest_signups({}), "not returned by the API")
        self.assertEqual(cr.latest_signups({"signup_history_14d": []}), "empty (no days returned)")

    def test_report_states_the_delta(self):
        text = cr.render(
            SUMMARY,
            TRAJECTORY,
            {"mrr": "$0.00 CAD", "paying_subscribers": "0", "signups": "1 on 2026-10-07"},
        )
        self.assertIn("MRR: $0.00 CAD (unchanged)", text)
        self.assertIn("Paying subscribers: 0 (unchanged)", text)
        self.assertIn("Signups: 0 on 2026-10-08 (was 1 on 2026-10-07)", text)
        self.assertNotIn("send_group_message", text)

    def test_unavailable_snapshot(self):
        mrr, paying = cr.mrr_fields({"mrr_snapshot": {"unavailable": True}})
        self.assertEqual(mrr, "not returned by the API")
        self.assertEqual(paying, "not returned by the API")

    def test_cents_fallback_when_display_missing(self):
        mrr, _paying = cr.mrr_fields({"mrr_snapshot": {"mrr_cents": 2900, "currency": "CAD", "paying_subscribers": 1}})
        self.assertEqual(mrr, "29.00 CAD")
        self.assertEqual(json.loads(json.dumps(cr.snapshot(SUMMARY, TRAJECTORY)))["mrr"], "$0.00 CAD")


if __name__ == "__main__":
    unittest.main()
