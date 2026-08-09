from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from support_eval_lab import observation


class ObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config_path = self.root / "experiment.json"
        self.record_path = self.root / "observation.json"
        self.config = self._config()
        self.record = self._record()
        self._write_inputs()

    @staticmethod
    def _config() -> dict[str, object]:
        repository = "owner/project"
        commit = "a" * 40
        entry_path = "support-eval-lab/channels/example.md"
        popular = f"/{repository}/blob/{commit}/{entry_path}"
        return {
            "schema_version": "1",
            "experiment_id": "sel-gh-001",
            "repository": repository,
            "owner_login": "owner",
            "target_commit": commit,
            "entry_path": entry_path,
            "entry_url": f"https://github.com{popular}",
            "expected_popular_path": popular,
            "release_url": "https://github.com/owner/project/releases/tag/support-eval-starter-v0.1.0",
            "window_start": "2026-08-09T00:00:00Z",
            "window_end": "2026-08-23T00:00:00Z",
            "final_capture_deadline": "2026-08-25T00:00:00Z",
            "entry_sha256": "b" * 64,
            "release_body_sha256": "c" * 64,
            "issue_form_sha256": "d" * 64,
            "frozen_description": "A bounded test experiment",
            "frozen_topics": ["ai-evaluation", "software-testing"],
        }

    @staticmethod
    def _record() -> dict[str, object]:
        return {
            "schema_version": "1",
            "record_id": "sel-gh-001-window-record",
            "experiment_id": "sel-gh-001",
            "source_mode": "operator_recorded_unverified",
            "captured_at": "2026-08-09T00:10:00Z",
            "configuration_observation": {
                "target_commit": "a" * 40,
                "entry_sha256": "b" * 64,
                "release_body_sha256": "c" * 64,
                "issue_form_sha256": "d" * 64,
                "frozen_description": "A bounded test experiment",
                "frozen_topics": ["ai-evaluation", "software-testing"],
            },
            "owner_preview_events": [],
            "traffic_observations": [
                {
                    "event_id": "traffic-activation",
                    "checkpoint": "activation",
                    "captured_at": "2026-08-09T00:10:00Z",
                    "row_state": "not-checked",
                    "captured_path": None,
                    "raw_views": None,
                    "retained_window_start": None,
                    "retained_window_end": None,
                }
            ],
            "issue_observations": [],
        }

    def _write_inputs(self) -> None:
        self.config_path.write_text(
            json.dumps(self.config, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        self.record_path.write_text(
            json.dumps(self.record, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

    def _load_report(self, as_of: str = "2026-08-09T00:10:00Z") -> dict[str, object]:
        self._write_inputs()
        experiment = observation._parse_experiment(self.config)
        record = observation.load_observation(self.record_path, experiment)
        return observation.build_report(
            experiment, record, as_of=observation._timestamp(as_of, "as_of")
        )

    def _clear_issue(
        self,
        *,
        event: str = "issue-one",
        number: int = 1,
        author: str = "contributor",
        created: str = "2026-08-10T00:00:00Z",
        intent: str = "future-private-route",
    ) -> dict[str, object]:
        return {
            "event_id": event,
            "issue_url": f"https://github.com/owner/project/issues/{number}",
            "issue_number": number,
            "created_at": created,
            "captured_at": "2026-08-23T00:05:00Z",
            "safety_disposition": "clear",
            "author_login": author,
            "actor_type": "user",
            "form_source_sha256": "d" * 64,
            "boundary_acknowledgement": "yes",
            "outcome_disposition": "generic-in-scope",
            "intent": intent,
        }

    def _final_traffic(self, *, state: str, raw_views: int | None) -> dict[str, object]:
        return {
            "event_id": "traffic-final",
            "checkpoint": "day14-refresh",
            "captured_at": "2026-08-23T00:05:00Z",
            "row_state": state,
            "captured_path": self.config["expected_popular_path"] if state == "present" else None,
            "raw_views": raw_views,
            "retained_window_start": (
                "2026-08-09T00:05:00Z" if state in {"present", "absent"} else None
            ),
            "retained_window_end": (
                "2026-08-23T00:05:00Z" if state in {"present", "absent"} else None
            ),
        }

    def test_repository_activation_record_is_strict_and_truthfully_unobserved(self) -> None:
        project = Path(__file__).resolve().parents[1]
        experiment = observation.load_experiment(project / "experiments" / "sel-gh-001.json")
        record = observation.load_observation(
            project / "observations" / "sel-gh-001-window.json", experiment
        )
        report = observation.build_report(
            experiment,
            record,
            as_of=datetime(2026, 8, 9, 0, 50, 13, tzinfo=timezone.utc),
        )
        self.assertEqual(report["state"], "active")
        self.assertEqual(report["traffic"]["view_observability"], "not-observed")
        self.assertIsNone(report["traffic"]["qualified_views"])
        self.assertFalse(report["checkout_authorized"])
        self.assertEqual(
            report["experiment"]["configuration_sha256"],
            observation.KNOWN_EXPERIMENT_CONFIG_SHA256["sel-gh-001"],
        )

    def test_registered_configuration_is_hash_pinned_and_owner_scoped(self) -> None:
        project = Path(__file__).resolve().parents[1]
        configured = json.loads(
            (project / "experiments" / "sel-gh-001.json").read_text(encoding="utf-8")
        )
        for label, mutation in (
            ("entry-hash", lambda value: value.update({"entry_sha256": "f" * 64})),
            ("owner", lambda value: value.update({"owner_login": "different-owner"})),
        ):
            with self.subTest(label=label):
                probe = copy.deepcopy(configured)
                mutation(probe)
                path = self.root / f"{label}.json"
                path.write_text(json.dumps(probe, indent=2) + "\n", encoding="utf-8", newline="\n")
                with self.assertRaisesRegex(ValueError, "registered frozen document"):
                    observation.load_experiment(path)

    def test_present_row_subtracts_owner_previews_without_summing_snapshots(self) -> None:
        path = self.config["expected_popular_path"]
        self.record["captured_at"] = "2026-08-15T00:05:00Z"
        self.record["owner_preview_events"] = [
            {"event_id": "preview-one", "captured_at": "2026-08-10T00:00:00Z", "path": path},
            {"event_id": "preview-two", "captured_at": "2026-08-11T00:00:00Z", "path": path},
        ]
        self.record["traffic_observations"].append(
            {
                "event_id": "traffic-day1",
                "checkpoint": "day1",
                "captured_at": "2026-08-10T00:05:00Z",
                "row_state": "present",
                "captured_path": path,
                "raw_views": 10,
                "retained_window_start": "2026-07-27T00:05:00Z",
                "retained_window_end": "2026-08-10T00:05:00Z",
            }
        )
        self.record["traffic_observations"].append(
            {
                "event_id": "traffic-day7",
                "checkpoint": "day7",
                "captured_at": "2026-08-15T00:05:00Z",
                "row_state": "present",
                "captured_path": path,
                "raw_views": 20,
                "retained_window_start": "2026-08-01T00:05:00Z",
                "retained_window_end": "2026-08-15T00:05:00Z",
            }
        )
        report = self._load_report("2026-08-15T00:05:00Z")
        self.assertEqual(report["traffic"]["raw_views"], 20)
        self.assertEqual(report["traffic"]["qualified_views"], 18)

    def test_only_previews_inside_latest_retained_window_are_subtracted(self) -> None:
        path = self.config["expected_popular_path"]
        self.record["captured_at"] = "2026-08-23T00:05:00Z"
        self.record["owner_preview_events"] = [
            {"event_id": "before-retention", "captured_at": "2026-08-09T00:01:00Z", "path": path},
            {"event_id": "inside-retention", "captured_at": "2026-08-10T00:00:00Z", "path": path},
        ]
        self.record["traffic_observations"].append(
            self._final_traffic(state="present", raw_views=10)
        )
        report = self._load_report("2026-08-23T00:05:00Z")
        self.assertEqual(report["traffic"]["owner_previews_through_checkpoint"], 1)
        self.assertEqual(report["traffic"]["qualified_views"], 9)

    def test_absent_row_is_unobservable_not_zero(self) -> None:
        self.record["captured_at"] = "2026-08-10T00:05:00Z"
        self.record["traffic_observations"].append(
            {
                "event_id": "traffic-day1",
                "checkpoint": "day1",
                "captured_at": "2026-08-10T00:05:00Z",
                "row_state": "absent",
                "captured_path": None,
                "raw_views": None,
                "retained_window_start": "2026-07-27T00:05:00Z",
                "retained_window_end": "2026-08-10T00:05:00Z",
            }
        )
        report = self._load_report("2026-08-10T00:05:00Z")
        self.assertEqual(report["traffic"]["view_observability"], "unobservable")
        self.assertIsNone(report["traffic"]["raw_views"])
        self.assertIsNone(report["traffic"]["qualified_views"])
        self.assertIn("not zero", report["traffic"]["warning"])

    def test_owner_previews_saturate_at_zero_with_warning(self) -> None:
        path = self.config["expected_popular_path"]
        self.record["captured_at"] = "2026-08-10T00:05:00Z"
        self.record["owner_preview_events"] = [
            {"event_id": f"preview-{index}", "captured_at": f"2026-08-09T0{index}:00:00Z", "path": path}
            for index in range(1, 4)
        ]
        self.record["traffic_observations"].append(
            {
                "event_id": "traffic-day1",
                "checkpoint": "day1",
                "captured_at": "2026-08-10T00:05:00Z",
                "row_state": "present",
                "captured_path": path,
                "raw_views": 1,
                "retained_window_start": "2026-07-27T00:05:00Z",
                "retained_window_end": "2026-08-10T00:05:00Z",
            }
        )
        report = self._load_report("2026-08-10T00:05:00Z")
        self.assertEqual(report["traffic"]["qualified_views"], 0)
        self.assertIn("saturated", report["traffic"]["warning"])

    def test_final_state_machine_distinguishes_incomplete_insufficient_and_inconclusive(self) -> None:
        self.record["captured_at"] = "2026-08-23T00:05:00Z"
        incomplete = self._load_report("2026-08-23T00:05:00Z")
        self.assertEqual(incomplete["state"], "incomplete")

        self.record["traffic_observations"].append(self._final_traffic(state="present", raw_views=100))
        insufficient = self._load_report("2026-08-23T00:05:00Z")
        self.assertEqual(insufficient["channel_result"], "insufficient-signal")

        self.record["traffic_observations"][-1] = self._final_traffic(state="absent", raw_views=None)
        self.record["issue_observations"] = [self._clear_issue()]
        inconclusive = self._load_report("2026-08-23T00:05:00Z")
        self.assertEqual(inconclusive["channel_result"], "inconclusive-views")

    def test_unchecked_final_row_remains_incomplete(self) -> None:
        self.record["captured_at"] = "2026-08-23T00:05:00Z"
        self.record["traffic_observations"].append(
            self._final_traffic(state="not-checked", raw_views=None)
        )
        report = self._load_report("2026-08-23T00:05:00Z")
        self.assertEqual(report["state"], "incomplete")
        self.assertEqual(report["channel_result"], "missing-final-observation")

    def test_positive_channel_result_still_never_authorizes_checkout(self) -> None:
        self.record["captured_at"] = "2026-08-23T00:05:00Z"
        self.record["traffic_observations"].append(self._final_traffic(state="present", raw_views=12))
        self.record["issue_observations"] = [self._clear_issue()]
        report = self._load_report("2026-08-23T00:05:00Z")
        self.assertEqual(report["channel_result"], "channel-threshold-met")
        self.assertFalse(report["checkout_authorized"])

    def test_sensitive_issue_uses_minimal_schema_and_halts_without_author_output(self) -> None:
        self.record["captured_at"] = "2026-08-10T00:00:00Z"
        self.record["issue_observations"] = [
            {
                "event_id": "issue-sensitive",
                "issue_url": "https://github.com/owner/project/issues/9",
                "issue_number": 9,
                "created_at": "2026-08-10T00:00:00Z",
                "captured_at": "2026-08-10T00:00:00Z",
                "safety_disposition": "sensitive-or-uncertain",
            }
        ]
        report = self._load_report("2026-08-10T00:00:00Z")
        serialized = json.dumps(report)
        self.assertEqual(report["state"], "privacy-halted")
        self.assertNotIn("author_login", serialized)
        unsafe = copy.deepcopy(self.record["issue_observations"][0])
        unsafe["title"] = "must not enter schema"
        with self.assertRaises(ValueError):
            observation._parse_issue(unsafe, observation._parse_experiment(self.config))

    def test_frozen_change_requires_restart(self) -> None:
        self.record["configuration_observation"]["entry_sha256"] = "e" * 64
        report = self._load_report()
        self.assertEqual(report["state"], "restart-required")

    def test_duplicate_owner_bot_out_of_window_and_form_mismatch_do_not_qualify(self) -> None:
        self.record["captured_at"] = "2026-08-23T00:05:00Z"
        issues = [
            self._clear_issue(event="one", number=1, author="alice"),
            self._clear_issue(event="two", number=2, author="alice"),
            self._clear_issue(event="owner-issue", number=3, author="owner"),
            self._clear_issue(event="late", number=4, author="late", created="2026-08-23T00:00:00Z"),
        ]
        bot = self._clear_issue(event="bot", number=5, author="helper-bot")
        bot["actor_type"] = "bot"
        mismatch = self._clear_issue(event="mismatch", number=6, author="mismatch")
        mismatch["form_source_sha256"] = "e" * 64
        issues.extend([bot, mismatch])
        self.record["issue_observations"] = issues
        report = self._load_report("2026-08-23T00:05:00Z")
        self.assertEqual(report["interest"]["qualifying_unverified_signals"], 1)
        reasons = ",".join(item["reason"] for item in report["interest"]["dispositions"])
        for expected in ("duplicate-account", "repository-owner", "outside-window", "non-user", "frozen-form"):
            self.assertIn(expected, reasons)

    def test_duplicate_public_issue_identity_is_rejected(self) -> None:
        first = self._clear_issue(event="first", number=7, author="alice")
        second = self._clear_issue(event="second", number=7, author="bob")
        self.record["captured_at"] = "2026-08-23T00:05:00Z"
        self.record["issue_observations"] = [first, second]
        self._write_inputs()
        with self.assertRaisesRegex(ValueError, "only once"):
            observation.load_observation(
                self.record_path, observation._parse_experiment(self.config)
            )

    def test_strict_json_rejects_duplicates_constants_huge_numbers_depth_and_bom(self) -> None:
        valid = json.dumps(self.record)
        probes = (
            valid.replace('"record_id":', '"record_id": "first", "record_id":', 1),
            valid.replace('"raw_views": null', '"raw_views": NaN'),
            valid.replace('"raw_views": null', '"raw_views": 12345678901234567890'),
            "[" * 20 + "]" * 20,
            "\ufeff" + valid,
        )
        for index, payload in enumerate(probes):
            with self.subTest(index=index):
                self.record_path.write_text(payload, encoding="utf-8")
                with self.assertRaises(ValueError):
                    observation._load_json(self.record_path)

    def test_bool_view_count_wrong_path_and_duplicate_checkpoint_fail(self) -> None:
        experiment = observation._parse_experiment(self.config)
        base = self._final_traffic(state="present", raw_views=2)
        for mutation in ("bool", "wrong-path"):
            probe = copy.deepcopy(base)
            if mutation == "bool":
                probe["raw_views"] = True
            else:
                probe["captured_path"] = "/owner/project/blob/" + "a" * 40 + "/../wrong"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                observation._parse_traffic(probe, experiment)
        self.record["captured_at"] = "2026-08-23T00:05:00Z"
        self.record["traffic_observations"] += [base, copy.deepcopy(base)]
        self.record["traffic_observations"][-1]["event_id"] = "other-event"
        self._write_inputs()
        with self.assertRaisesRegex(ValueError, "checkpoints"):
            observation.load_observation(self.record_path, experiment)

    def test_checkpoint_order_and_final_timing_fail_closed(self) -> None:
        experiment = observation._parse_experiment(self.config)
        day7 = {
            "event_id": "traffic-day7",
            "checkpoint": "day7",
            "captured_at": "2026-08-16T00:00:00Z",
            "row_state": "absent",
            "captured_path": None,
            "raw_views": None,
            "retained_window_start": "2026-08-02T00:00:00Z",
            "retained_window_end": "2026-08-16T00:00:00Z",
        }
        day1 = copy.deepcopy(day7)
        day1.update(
            {
                "event_id": "traffic-day1",
                "checkpoint": "day1",
                "captured_at": "2026-08-17T00:00:00Z",
                "retained_window_start": "2026-08-03T00:00:00Z",
                "retained_window_end": "2026-08-17T00:00:00Z",
            }
        )
        self.record["captured_at"] = "2026-08-17T00:00:00Z"
        self.record["traffic_observations"] += [day7, day1]
        self._write_inputs()
        with self.assertRaisesRegex(ValueError, "schedule order"):
            observation.load_observation(self.record_path, experiment)

        self.record = self._record()
        self.record["captured_at"] = "2026-08-22T00:00:00Z"
        early_final = self._final_traffic(state="absent", raw_views=None)
        early_final["captured_at"] = "2026-08-22T00:00:00Z"
        early_final["retained_window_start"] = "2026-08-08T00:00:00Z"
        early_final["retained_window_end"] = "2026-08-22T00:00:00Z"
        self.record["traffic_observations"].append(early_final)
        self._write_inputs()
        with self.assertRaisesRegex(ValueError, "after the window"):
            observation.load_observation(self.record_path, experiment)

        self.record = self._record()
        self.record["captured_at"] = "2026-08-26T00:00:00Z"
        late_final = self._final_traffic(state="absent", raw_views=None)
        late_final["captured_at"] = "2026-08-26T00:00:00Z"
        late_final["retained_window_start"] = "2026-08-12T00:00:00Z"
        late_final["retained_window_end"] = "2026-08-26T00:00:00Z"
        self.record["traffic_observations"].append(late_final)
        self._write_inputs()
        with self.assertRaisesRegex(ValueError, "capture deadline"):
            observation.load_observation(self.record_path, experiment)

    def test_input_symlink_and_output_hardlink_are_rejected_when_supported(self) -> None:
        symlink = self.root / "linked.json"
        try:
            symlink.symlink_to(self.record_path)
        except OSError as error:
            self.skipTest(f"link creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "nonsymlink"):
            observation._load_json(symlink)
        project = Path(__file__).resolve().parents[1]
        actual_config = project / "experiments" / "sel-gh-001.json"
        actual_record = project / "observations" / "sel-gh-001-window.json"
        alias = self.root / "alias.json"
        os.link(actual_record, alias)
        with self.assertRaisesRegex(ValueError, "aliases"):
            observation.main(
                [
                    str(actual_config),
                    str(actual_record),
                    "--as-of",
                    "2026-08-09T00:50:13Z",
                    "--json-out",
                    str(alias),
                ]
            )

    def test_output_is_deterministic_lf_only_and_omits_author_login(self) -> None:
        project = Path(__file__).resolve().parents[1]
        json_out = self.root / "report.json"
        markdown_out = self.root / "report.md"
        args = [
            str(project / "experiments" / "sel-gh-001.json"),
            str(project / "observations" / "sel-gh-001-window.json"),
            "--as-of",
            "2026-08-09T00:50:13Z",
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
        observation.main(args)
        first = (json_out.read_bytes(), markdown_out.read_bytes())
        observation.main(args)
        second = (json_out.read_bytes(), markdown_out.read_bytes())
        self.assertEqual(first, second)
        self.assertNotIn(b"\r\n", first[0] + first[1])
        self.assertNotIn(b"author_login", first[0] + first[1])
        match = re.search(rb"Canonical JSON SHA-256: <code>([0-9a-f]{64})</code>", first[1])
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).decode("ascii"), hashlib.sha256(first[0]).hexdigest())


if __name__ == "__main__":
    unittest.main()
