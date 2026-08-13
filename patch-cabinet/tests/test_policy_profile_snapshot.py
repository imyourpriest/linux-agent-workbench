from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from patch_cabinet import policy_profile_catalog
from patch_cabinet.consent_catalog import load_catalog as load_consent_catalog


class PolicyProfileSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]
        self.profiles = self.project / "data" / "policy-profile-catalog" / "v1"
        self.consent = self.project / "data" / "consent-catalog" / "v1"

    def snapshot(self, as_of: date, filters: dict[str, str] | None = None) -> dict[str, object]:
        return policy_profile_catalog.build_snapshot(
            policy_profile_catalog.load_profiles(self.profiles, self.consent),
            load_consent_catalog(self.consent),
            as_of=as_of,
            filters=filters or {},
        )

    def test_snapshot_is_deterministic_neutral_and_complete(self) -> None:
        first = self.snapshot(date(2026, 8, 13))
        second = self.snapshot(date(2026, 8, 13))
        self.assertEqual(first, second)
        self.assertEqual(first["summary"]["matched_profiles"], 10)
        self.assertIn("not trust", first["claim_boundary"])
        self.assertNotIn("score", json.dumps(first).casefold())

    def test_seven_day_window_labels_fresh_stale_and_unknown(self) -> None:
        current = self.snapshot(date(2026, 8, 13))
        self.assertEqual(current["summary"]["freshness"], {"fresh": 10, "stale": 0, "unknown": 0})
        stale = self.snapshot(date(2026, 8, 21))
        self.assertGreater(stale["summary"]["freshness"]["stale"], 0)
        unknown = self.snapshot(date(2026, 8, 7))
        self.assertGreater(unknown["summary"]["freshness"]["unknown"], 0)
        self.assertTrue(
            all(item["age_days_at_as_of"] is None for item in unknown["profiles"])
        )

    def test_dimension_filters_are_exact_and_combined_with_and(self) -> None:
        filters = {"autonomous_pr_submission": "disallowed", "human_review": "required"}
        report = self.snapshot(date(2026, 8, 13), filters)
        self.assertGreater(report["summary"]["matched_profiles"], 0)
        for profile in report["profiles"]:
            self.assertEqual(profile["dimensions"]["autonomous_pr_submission"], "disallowed")
            self.assertEqual(profile["dimensions"]["human_review"], "required")

    def test_filter_parser_rejects_unknown_duplicate_and_malformed_values(self) -> None:
        invalid_filters = (
            ["unknown=value"],
            ["human_review=wrong"],
            ["human_review"],
            ["human_review=required=extra"],
            ["human_review=required", "human_review=recommended"],
        )
        for values in invalid_filters:
            with self.subTest(values=values), self.assertRaises(ValueError):
                policy_profile_catalog._parse_dimension_filters(values)

    def test_as_of_is_canonical(self) -> None:
        self.assertEqual(policy_profile_catalog._parse_as_of("2026-08-13"), date(2026, 8, 13))
        for value in ("2026-8-13", "2026-02-30", "tomorrow"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                policy_profile_catalog._parse_as_of(value)

    def test_cli_generates_exact_snapshot_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            json_out = Path(temporary) / "snapshot.json"
            md_out = Path(temporary) / "snapshot.md"
            result = policy_profile_catalog.main(
                [
                    str(self.profiles),
                    "--consent-records", str(self.consent),
                    "--as-of", "2026-08-13",
                    "--where", "autonomous_pr_submission=disallowed",
                    "--json-out", str(json_out),
                    "--markdown-out", str(md_out),
                ]
            )
            self.assertEqual(result, 0)
            parsed = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(parsed["filters"], {"autonomous_pr_submission": "disallowed"})
            self.assertIn("Historical", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
