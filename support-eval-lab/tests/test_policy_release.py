from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support_eval_lab import policy_release


class PolicyReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]

    def copied_project(self, temporary: str) -> Path:
        copy = Path(temporary) / "support-eval-lab"
        shutil.copytree(self.project / "policy-starter", copy / "policy-starter")
        shutil.copytree(
            self.project / "policy-release-experiment", copy / "policy-release-experiment"
        )
        return copy

    def final_measurement(
        self,
        *,
        downloads: int = 10,
        feedback: int = 3,
        adoption: int = 2,
        customization: int = 0,
        budget: int = 0,
        result: str = "success",
    ) -> dict[str, object]:
        raw = json.loads(
            (self.project / "policy-release-experiment" / "MEASUREMENT_TEMPLATE.json").read_text()
        )
        raw.update(
            {
                "status": "final",
                "checkpoint_kind": "final_exact_14_day_checkpoint",
                "window_start_utc": "2026-08-25T01:00:00Z",
                "window_end_utc": "2026-09-08T01:00:00Z",
                "release_id": 123456,
                "release_asset_id": 789012,
                "feedback_form_route": "ai-policy-starter-feedback",
                "github_reported_download_count": downloads,
                "substantive_feedback_issues": feedback,
                "distinct_public_accounts": feedback,
                "intended_adoption_or_use_reports": adoption,
                "unsolicited_customization_requests": customization,
                "explicit_budget_signals": budget,
                "paid_signal": customization >= 1 or budget >= 1,
                "evaluation_result": result,
                "result_action": (
                    "future_decision_required_payment_disabled"
                    if result == "success"
                    else "no_payment_and_revise_or_retire"
                ),
            }
        )
        return raw

    def test_checked_artifacts_are_fresh_inert_and_deterministic(self) -> None:
        first = policy_release.validate(self.project)
        second = policy_release.validate(self.project)
        self.assertEqual(first, second)
        self.assertFalse(first["activation_authorized"])
        self.assertFalse(first["payment_enabled"])
        self.assertFalse(first["demand_validated"])
        self.assertEqual(first["revenue_usd"], "0.00")

    def test_time_never_becomes_authorization(self) -> None:
        source = Path(policy_release.__file__).read_text(encoding="utf-8")
        self.assertNotIn("datetime.now", source)
        self.assertNotIn("time.time", source)
        contract = json.loads((self.project / "policy-release-experiment" / "ACTIVATION_CONTRACT.json").read_text())
        self.assertFalse(contract["time_alone_authorizes_activation"])
        self.assertIn("new_future_control_task_decision", contract["required_gates"])

    def test_final_checkpoint_success_failure_and_inconclusive_are_disjoint(self) -> None:
        cases = (
            (self.final_measurement(), "success"),
            (self.final_measurement(downloads=4, feedback=3, adoption=2, result="failure"), "failure"),
            (self.final_measurement(downloads=10, feedback=0, adoption=0, result="failure"), "failure"),
            (self.final_measurement(downloads=9, feedback=3, adoption=2, result="inconclusive"), "inconclusive"),
            (self.final_measurement(downloads=10, feedback=2, adoption=2, result="inconclusive"), "inconclusive"),
            (self.final_measurement(downloads=10, feedback=3, adoption=1, result="inconclusive"), "inconclusive"),
        )
        for raw, expected in cases:
            with self.subTest(expected=expected, downloads=raw["github_reported_download_count"]):
                result = policy_release.evaluate_measurement(raw)
                self.assertEqual(result["evaluation_result"], expected)
                self.assertFalse(result["payment_enabled"])
                self.assertFalse(result["second_channel_allowed"])

    def test_success_and_paid_signal_remain_separate_and_payment_disabled(self) -> None:
        no_paid_signal = policy_release.evaluate_measurement(self.final_measurement())
        self.assertFalse(no_paid_signal["paid_signal"])
        with_paid_signal = policy_release.evaluate_measurement(
            self.final_measurement(customization=1)
        )
        self.assertTrue(with_paid_signal["paid_signal"])
        self.assertEqual(with_paid_signal["evaluation_result"], "success")
        self.assertFalse(with_paid_signal["payment_enabled"])
        self.assertEqual(
            with_paid_signal["result_action"],
            "future_decision_required_payment_disabled",
        )

    def test_final_measurement_mutations_fail_closed(self) -> None:
        probes = []
        for field, value in (
            ("window_end_utc", "2026-09-07T01:00:00Z"),
            ("release_id", True),
            ("release_asset_id", 0),
            ("release_tag", "other-tag"),
            ("asset_name", "other.zip"),
            ("asset_sha256", "0" * 64),
            ("download_source", "traffic_views"),
            ("feedback_form_route", "../route"),
            ("distinct_public_accounts", 2),
            ("intended_adoption_or_use_reports", 4),
            ("paid_signal", True),
            ("evaluation_result", "failure"),
            ("payment_enabled", True),
            ("second_channel_allowed", True),
        ):
            raw = self.final_measurement()
            raw[field] = value
            probes.append((field, raw))
        unknown = self.final_measurement()
        unknown["username"] = "not-allowed"
        probes.append(("unknown", unknown))
        for label, raw in probes:
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    policy_release.evaluate_measurement(raw)

    def test_relaxed_gate_and_unexpected_file_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "support-eval-lab"
            shutil.copytree(self.project / "policy-starter", copy / "policy-starter")
            shutil.copytree(self.project / "policy-release-experiment", copy / "policy-release-experiment")
            contract_path = copy / "policy-release-experiment" / "ACTIVATION_CONTRACT.json"
            contract = json.loads(contract_path.read_text())
            contract["time_alone_authorizes_activation"] = True
            contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(ValueError, "activation boundary"):
                policy_release.build(copy)
            (copy / "policy-release-experiment" / "extra").write_text("x")
            with self.assertRaisesRegex(ValueError, "inventory"):
                policy_release.validate(copy)

    def test_duplicate_json_unknown_fields_and_digest_mismatch_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "support-eval-lab"
            shutil.copytree(self.project / "policy-starter", copy / "policy-starter")
            shutil.copytree(self.project / "policy-release-experiment", copy / "policy-release-experiment")
            release = copy / "policy-release-experiment" / "RELEASE.json"
            release.write_text(
                release.read_text().replace('"status":', '"status": "first", "status":', 1),
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "strict JSON"):
                policy_release.build(copy)
            shutil.copy2(self.project / "policy-release-experiment" / "RELEASE.json", release)
            contract_path = copy / "policy-release-experiment" / "ACTIVATION_CONTRACT.json"
            contract = json.loads(contract_path.read_text())
            contract["asset_sha256"] = "0" * 64
            contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(ValueError, "asset digest"):
                policy_release.build(copy)

    def test_deep_json_and_oversized_input_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "support-eval-lab"
            shutil.copytree(self.project / "policy-starter", copy / "policy-starter")
            shutil.copytree(self.project / "policy-release-experiment", copy / "policy-release-experiment")
            contract = copy / "policy-release-experiment" / "ACTIVATION_CONTRACT.json"
            contract.write_text("[" * 20 + "]" * 20 + "\n", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(ValueError, "depth"):
                policy_release.build(copy)
            shutil.copy2(self.project / "policy-release-experiment" / "ACTIVATION_CONTRACT.json", contract)
            (copy / "policy-starter" / "README.md").write_bytes(
                b"x" * (policy_release.MAX_FILE_BYTES + 1)
            )
            with self.assertRaisesRegex(ValueError, "size limit"):
                policy_release.build(copy)

    def test_hardlink_and_network_or_activation_code_are_rejected_or_absent(self) -> None:
        source = Path(policy_release.__file__).read_text(encoding="utf-8")
        for forbidden in ("import socket", "import urllib", "import requests", "subprocess", "def activate"):
            self.assertNotIn(forbidden, source)
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "support-eval-lab"
            shutil.copytree(self.project / "policy-starter", copy / "policy-starter")
            shutil.copytree(self.project / "policy-release-experiment", copy / "policy-release-experiment")
            target = copy / "policy-release-experiment" / "README.md"
            alias = target.with_suffix(".alias")
            try:
                os.link(target, alias)
                with self.assertRaisesRegex(ValueError, "hard-link"):
                    policy_release.build(copy)
            finally:
                alias.unlink(missing_ok=True)

    def test_old_predictable_staging_path_is_never_touched(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = self.copied_project(temporary)
            experiment = copy / "policy-release-experiment"
            old = experiment / f".{policy_release.ASSET}.build"
            old.write_bytes(b"regular sentinel")
            policy_release.build(copy)
            self.assertEqual(old.read_bytes(), b"regular sentinel")
            old.unlink()
            victim = Path(temporary) / "victim"
            victim.write_bytes(b"hardlink victim")
            os.link(victim, old)
            policy_release.build(copy)
            self.assertEqual(victim.read_bytes(), b"hardlink victim")
            self.assertEqual(old.read_bytes(), b"hardlink victim")

    def test_old_predictable_symlink_is_untouched_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = self.copied_project(temporary)
            experiment = copy / "policy-release-experiment"
            victim = Path(temporary) / "victim"
            victim.write_bytes(b"symlink victim")
            old = experiment / f".{policy_release.ASSET}.build"
            try:
                old.symlink_to(victim)
            except OSError as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            policy_release.build(copy)
            self.assertTrue(old.is_symlink())
            self.assertEqual(victim.read_bytes(), b"symlink victim")

    def test_secure_asset_staging_is_unique_and_cleaned(self) -> None:
        created: list[Path] = []
        real_mkstemp = tempfile.mkstemp

        def capture(*args: object, **kwargs: object) -> tuple[int, str]:
            result = real_mkstemp(*args, **kwargs)
            if ".archive." in str(kwargs.get("prefix", "")):
                created.append(Path(result[1]))
            return result

        with tempfile.TemporaryDirectory() as temporary:
            copy = self.copied_project(temporary)
            with mock.patch.object(policy_release.tempfile, "mkstemp", side_effect=capture):
                policy_release.build(copy)
                policy_release.build(copy)
            self.assertEqual(len(created), 2)
            self.assertEqual(len(set(created)), 2)
            self.assertTrue(all(not path.exists() for path in created))

    def test_every_static_schema_stop_condition_and_release_field_is_exact(self) -> None:
        mutations = (
            ("ACTIVATION_CONTRACT.json", "schema_version", "999"),
            ("RELEASE.json", "schema_version", "999"),
            ("MEASUREMENT_TEMPLATE.json", "schema_version", "999"),
            ("RELEASE.json", "tag_name", "other-tag"),
            ("RELEASE.json", "name", "other name"),
            ("RELEASE.json", "body_path", "../RELEASE_BODY.md"),
            ("RELEASE.json", "asset_path", "https://evil.invalid/asset.zip"),
            ("RELEASE.json", "checksum_path", "nested/checksum.sha256"),
        )
        for filename, field, value in mutations:
            with self.subTest(filename=filename, field=field):
                with tempfile.TemporaryDirectory() as temporary:
                    copy = self.copied_project(temporary)
                    target = copy / "policy-release-experiment" / filename
                    raw = json.loads(target.read_text())
                    raw[field] = value
                    target.write_text(
                        json.dumps(raw, indent=2) + "\n", encoding="utf-8", newline="\n"
                    )
                    with self.assertRaises(ValueError):
                        policy_release.build(copy)
        for stop_conditions in ([], list(reversed(policy_release.STOP_CONDITIONS)), policy_release.STOP_CONDITIONS + ["extra"]):
            with self.subTest(stop_conditions=stop_conditions):
                with tempfile.TemporaryDirectory() as temporary:
                    copy = self.copied_project(temporary)
                    target = copy / "policy-release-experiment" / "ACTIVATION_CONTRACT.json"
                    raw = json.loads(target.read_text())
                    raw["stop_conditions"] = stop_conditions
                    target.write_text(
                        json.dumps(raw, indent=2) + "\n", encoding="utf-8", newline="\n"
                    )
                    with self.assertRaisesRegex(ValueError, "stop conditions"):
                        policy_release.build(copy)

    def test_manifest_checksum_and_receipt_mutations_fail_validation(self) -> None:
        mutations = (
            ("manifest.json", lambda path: path.write_text("{}\n", encoding="utf-8")),
            (
                policy_release.ASSET + ".sha256",
                lambda path: path.write_text("0" * 64 + "  wrong.zip\n", encoding="utf-8"),
            ),
            ("validation-receipt.json", lambda path: path.write_text("{}\n", encoding="utf-8")),
        )
        for filename, mutate in mutations:
            with self.subTest(filename=filename):
                with tempfile.TemporaryDirectory() as temporary:
                    copy = self.copied_project(temporary)
                    mutate(copy / "policy-release-experiment" / filename)
                    with self.assertRaises(ValueError):
                        policy_release.validate(copy)

    def test_stray_and_pycache_inventory_fail_before_materialization(self) -> None:
        for kind in ("stray", "pycache_file", "pycache_directory"):
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as temporary:
                    copy = self.copied_project(temporary)
                    experiment = copy / "policy-release-experiment"
                    if kind == "stray":
                        (experiment / "stray.txt").write_text("stray", encoding="utf-8")
                    elif kind == "pycache_file":
                        (experiment / "__pycache__").write_bytes(b"not ignored")
                    else:
                        cache = experiment / "__pycache__"
                        cache.mkdir()
                        (cache / "oversized.bin").write_bytes(
                            b"x" * (policy_release.MAX_TOTAL_BYTES + 1)
                        )
                    with self.assertRaisesRegex(ValueError, "inventory"):
                        policy_release.validate(copy)

    def test_linked_experiment_directory_is_rejected_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "support-eval-lab"
            shutil.copytree(self.project / "policy-starter", copy / "policy-starter")
            actual = Path(temporary) / "actual-experiment"
            shutil.copytree(self.project / "policy-release-experiment", actual)
            linked = copy / "policy-release-experiment"
            try:
                linked.symlink_to(actual, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlink creation unavailable: {error}")
            with self.assertRaisesRegex(ValueError, "non-link"):
                policy_release.validate(copy)

    def test_experiment_boundary_must_be_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "support-eval-lab"
            shutil.copytree(self.project / "policy-starter", copy / "policy-starter")
            (copy / "policy-release-experiment").write_bytes(b"not a directory")
            with self.assertRaisesRegex(ValueError, "directory"):
                policy_release.validate(copy)


if __name__ == "__main__":
    unittest.main()
