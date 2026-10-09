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

    def test_trial_mode_reports_token_and_api(self):
        text = cr.render(SUMMARY, TRAJECTORY, None, trial=True)
        self.assertTrue(text.startswith("Task: /trial-report"))
        self.assertIn("Token: confirmed working", text)
        self.assertIn("API: reachable", text)
        self.assertIn("MRR: $0.00 CAD (no prior baseline)", text)
        self.assertIn("left disabled", text)
        self.assertNotIn("Token:", cr.render(SUMMARY, TRAJECTORY, None))

    def test_trial_flag_labels_failures(self):
        import io
        import os
        from contextlib import redirect_stdout
        from unittest import mock

        out = io.StringIO()
        with mock.patch.dict(os.environ, {"CORP_READONLY_TOKEN": ""}), \
                mock.patch.object(cr, "load_dotenv"), \
                mock.patch.object(cr.Path, "is_dir", return_value=False), \
                redirect_stdout(out):
            self.assertEqual(cr.main(["--trial"]), 1)
        self.assertIn("Task: /trial-report", out.getvalue())
        self.assertIn("CORP_READONLY_TOKEN is missing", out.getvalue())


if __name__ == "__main__":
    unittest.main()
