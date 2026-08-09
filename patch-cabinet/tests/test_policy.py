from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from patch_cabinet.cli import main
from patch_cabinet.engine import (
    ENGINE_NAME,
    ENGINE_VERSION,
    EXPECTED_DEPENDENCIES,
    OUTPUT_SCHEMA_VERSION,
    validate_runtime_dependencies,
)
from patch_cabinet.policy import (
    evaluate_candidate as _evaluate_candidate,
    evaluate_candidates as _evaluate_candidates,
)


AS_OF = date.today()


def evaluate_candidate(candidate, **kwargs):
    kwargs.setdefault("as_of", AS_OF)
    kwargs.setdefault("evaluation_mode", "live")
    return _evaluate_candidate(candidate, **kwargs)


def evaluate_candidates(candidates, **kwargs):
    kwargs.setdefault("as_of", AS_OF)
    kwargs.setdefault("evaluation_mode", "live")
    return _evaluate_candidates(candidates, **kwargs)


BASE = {
    "repository": "example/tool",
    "url": "https://example.invalid/example/tool",
    "observed_at": AS_OF.isoformat(),
    "commit_sha": "a" * 40,
    "public": True,
    "archived": False,
    "license_spdx": "MIT",
    "linux_relevance": "direct",
    "maintainer_signal": "explicit_issue",
    "issue_url": "https://example.invalid/example/tool/issues/1",
    "task_type": "bugfix",
    "last_activity_at": (AS_OF - timedelta(days=10)).isoformat(),
    "estimated_hours": 2,
    "has_reproduction": True,
    "has_tests": True,
    "has_contributing": True,
    "ai_policy": "allows",
    "ai_policy_basis": "explicitly_allows_agent_submission",
    "ai_policy_source_url": (
        "https://github.com/example/tool/blob/" + "a" * 40 + "/CONTRIBUTING.md"
    ),
    "requires_human_attestation": False,
    "sensitive_subsystem": False,
    "requires_secrets": False,
    "requires_production_access": False,
    "requires_network_probe": False,
    "open_pull_requests": 2,
}


class CandidatePolicyTests(unittest.TestCase):
    def candidate(self, **changes):
        candidate = deepcopy(BASE)
        candidate.update(changes)
        if (
            "ai_policy_source_url" not in changes
            and ({"repository", "commit_sha"} & changes.keys())
        ):
            candidate["ai_policy_source_url"] = (
                "https://github.com/"
                + candidate["repository"]
                + "/blob/"
                + candidate["commit_sha"]
                + "/CONTRIBUTING.md"
            )
        return candidate

    def test_strong_candidate_is_ready(self):
        result = evaluate_candidate(self.candidate())
        self.assertTrue(result.eligible)
        self.assertEqual(result.score, 100)
        self.assertEqual(result.band, "ready")

    def test_frozen_repository_is_rejected_case_insensitively(self):
        result = evaluate_candidate(
            self.candidate(repository="HISTORICAL/frozen-demo")
        )
        self.assertFalse(result.eligible)
        self.assertIn("frozen", " ".join(result.reasons))

    def test_local_exclusion_is_applied_without_publicly_naming_it(self):
        private_name = "private/local-history"
        result = evaluate_candidate(
            self.candidate(repository=private_name),
            excluded_repositories=[private_name.upper()],
        )
        self.assertFalse(result.eligible)
        self.assertNotIn(private_name, json.dumps(result.to_dict()))

    def test_missing_license_is_rejected(self):
        result = evaluate_candidate(self.candidate(license_spdx="NOASSERTION"))
        self.assertFalse(result.eligible)
        self.assertIn("license", " ".join(result.reasons))

    def test_security_work_is_rejected(self):
        result = evaluate_candidate(self.candidate(sensitive_subsystem=True))
        self.assertFalse(result.eligible)
        self.assertIn("sensitive", " ".join(result.reasons))

    def test_unknown_task_type_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "task_type"):
            evaluate_candidate(self.candidate(task_type="security"))

    def test_secrets_or_external_access_are_rejected(self):
        for field in ("requires_secrets", "requires_production_access", "requires_network_probe"):
            with self.subTest(field=field):
                result = evaluate_candidate(self.candidate(**{field: True}))
                self.assertFalse(result.eligible)
                expected = field.removeprefix("requires_").replace("_", " ")
                self.assertIn(expected, " ".join(result.reasons))

    def test_upstream_ai_prohibition_is_rejected(self):
        result = evaluate_candidate(
            self.candidate(
                ai_policy="disallows",
                ai_policy_basis="disallows_agent_submission",
            )
        )
        self.assertFalse(result.eligible)
        self.assertIn("disallows", " ".join(result.reasons))

    def test_human_attestation_requires_investigation(self):
        result = evaluate_candidate(
            self.candidate(requires_human_attestation=True)
        )
        self.assertTrue(result.eligible)
        self.assertEqual(result.score, 90)
        self.assertEqual(result.band, "investigate")
        self.assertEqual(len(result.cautions), 1)

    def test_unknown_ai_policy_is_not_consent(self):
        result = evaluate_candidate(
            self.candidate(
                ai_policy="unknown",
                ai_policy_basis="no_explicit_workflow_rule",
            )
        )
        self.assertFalse(result.eligible)
        self.assertEqual(result.score, 0)
        self.assertEqual(result.band, "ineligible")
        self.assertIn("no explicit upstream policy permits", " ".join(result.reasons))

    def test_ai_policy_assertion_is_bound_to_matching_pinned_source(self):
        with self.assertRaisesRegex(ValueError, "ai_policy_basis"):
            evaluate_candidate(
                self.candidate(ai_policy_basis="no_explicit_workflow_rule")
            )
        for source in (
            "https://github.com/example/tool/blob/main/CONTRIBUTING.md",
            "https://github.com/another/tool/blob/" + "a" * 40 + "/CONTRIBUTING.md",
            "https://github.com/example/tool/blob/" + "b" * 40 + "/CONTRIBUTING.md",
            "https://github.com/example/tool/blob/" + "a" * 40 + "/../main/CONTRIBUTING.md",
            "https://github.com/example/tool/blob/" + "a" * 40 + "/%2e%2e/main/CONTRIBUTING.md",
            "https://github.com/example/tool/blob/" + "a" * 40 + "/docs%2f..%2fCONTRIBUTING.md",
            "https://github.com/example/tool/blob/" + "a" * 40 + "/docs\\CONTRIBUTING.md",
            "https://github.com//example/tool/blob/" + "a" * 40 + "/CONTRIBUTING.md",
        ):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, "pin a file|canonically pin"):
                    evaluate_candidate(self.candidate(ai_policy_source_url=source))

    def test_invalid_spdx_expression_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SPDX"):
            evaluate_candidate(self.candidate(license_spdx="TOTALLY-NOT-SPDX"))

    def test_source_available_and_custom_licenses_are_not_season_one_eligible(self):
        for license_expression in ("BUSL-1.1", "LicenseRef-Proprietary"):
            with self.subTest(license_expression=license_expression):
                result = evaluate_candidate(self.candidate(license_spdx=license_expression))
                self.assertFalse(result.eligible)
                self.assertIn("allowlist", " ".join(result.reasons))

    def test_generated_result_contains_inputs_and_score_trace(self):
        result = evaluate_candidate(self.candidate())
        serialized = result.to_dict()
        self.assertEqual(serialized["normalized_inputs"]["public"], True)
        self.assertEqual(
            serialized["evidence"]["ai_policy_basis"],
            "explicitly_allows_agent_submission",
        )
        self.assertIn("/blob/" + "a" * 40 + "/", serialized["evidence"]["ai_policy_source_url"])
        self.assertEqual(sum(item["delta"] for item in serialized["score_trace"]), result.score)

    def test_results_are_deterministic(self):
        lower = self.candidate(repository="zeta/tool", has_reproduction=False)
        equal_b = self.candidate(repository="beta/tool")
        equal_a = self.candidate(repository="alpha/tool")
        results = evaluate_candidates([lower, equal_b, equal_a])
        self.assertEqual(
            [item.repository for item in results],
            ["alpha/tool", "beta/tool", "zeta/tool"],
        )

    def test_missing_field_is_an_error(self):
        candidate = self.candidate()
        del candidate["commit_sha"]
        with self.assertRaisesRegex(ValueError, "commit_sha"):
            evaluate_candidate(candidate)

    def test_unexpected_fields_are_rejected_instead_of_published(self):
        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            evaluate_candidate(self.candidate(private_maintainer_note="do not publish"))

    def test_invalid_commit_and_date_are_errors(self):
        with self.assertRaisesRegex(ValueError, "40-character"):
            evaluate_candidate(self.candidate(commit_sha="main"))
        with self.assertRaisesRegex(ValueError, "40-character"):
            evaluate_candidate(self.candidate(commit_sha="0" * 40))
        with self.assertRaisesRegex(ValueError, "valid YYYY-MM-DD"):
            evaluate_candidate(self.candidate(observed_at="2026-02-30"))
        with self.assertRaisesRegex(ValueError, "as-of"):
            evaluate_candidate(
                self.candidate(observed_at=(AS_OF + timedelta(days=1)).isoformat()),
                as_of=AS_OF,
            )
        with self.assertRaisesRegex(ValueError, "last_activity_at"):
            evaluate_candidate(
                self.candidate(last_activity_at=(AS_OF + timedelta(days=1)).isoformat()),
                as_of=AS_OF,
            )

    def test_future_as_of_and_stale_observations_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "as_of cannot be in the future"):
            _evaluate_candidate(
                self.candidate(),
                as_of=AS_OF + timedelta(days=1),
                evaluation_mode="live",
            )
        stale_observation = AS_OF - timedelta(days=8)
        stale = self.candidate(
            observed_at=stale_observation.isoformat(),
            last_activity_at=(stale_observation - timedelta(days=1)).isoformat(),
        )
        with self.assertRaisesRegex(ValueError, "more than 7 days"):
            _evaluate_candidate(stale, as_of=AS_OF, evaluation_mode="live")

    def test_historical_evaluation_can_never_be_ready(self):
        historical_as_of = AS_OF - timedelta(days=1)
        historical = self.candidate(
            observed_at=historical_as_of.isoformat(),
            last_activity_at=(historical_as_of - timedelta(days=10)).isoformat(),
        )
        result = _evaluate_candidate(
            historical,
            as_of=historical_as_of,
            evaluation_mode="historical",
        )
        self.assertEqual(result.score, 100)
        self.assertEqual(result.band, "investigate")
        self.assertIn("historical", " ".join(result.cautions))

    def test_repository_and_url_injection_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "owner/name"):
            evaluate_candidate(self.candidate(repository="owner/repo|forged"))
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            evaluate_candidate(
                self.candidate(url="https://user:secret@example.invalid/owner/repo")
            )
        for hostile_url in (
            "https://localhost/repo",
            "https://127.0.0.1/repo",
            "https://./repo",
            "https://example.invalid:bad/repo",
            "https://" + ".".join(["a" * 63] * 4) + "/repo",
        ):
            with self.subTest(hostile_url=hostile_url):
                with self.assertRaisesRegex(ValueError, "HTTPS"):
                    evaluate_candidate(self.candidate(url=hostile_url))

    def test_cli_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "candidates.json"
            json_out = root / "out" / "results.json"
            markdown_out = root / "out" / "results.md"
            source.write_text(json.dumps([self.candidate()]), encoding="utf-8")

            result = main(
                [
                    "score",
                    str(source),
                    "--as-of",
                    AS_OF.isoformat(),
                    "--allow-no-local-exclusions",
                    "--json-out",
                    str(json_out),
                    "--markdown-out",
                    str(markdown_out),
                ]
            )

            self.assertEqual(result, 0)
            payload = json.loads(json_out.read_text())
            self.assertEqual(payload["schema_version"], OUTPUT_SCHEMA_VERSION)
            self.assertEqual(
                payload["engine"], {"name": ENGINE_NAME, "version": ENGINE_VERSION}
            )
            self.assertEqual(payload["dependencies"], EXPECTED_DEPENDENCIES)
            self.assertEqual(payload["policy"]["as_of"], AS_OF.isoformat())
            self.assertEqual(payload["policy"]["evaluation_mode"], "live")
            self.assertEqual(payload["results"][0]["score"], 100)
            markdown = markdown_out.read_text(encoding="utf-8")
            self.assertIn(AS_OF.isoformat(), markdown)
            self.assertIn("example/tool", markdown)
            self.assertNotIn(str(root), markdown)

    def test_active_engine_dependency_identity_matches_runtime(self):
        self.assertEqual(ENGINE_VERSION, "0.3.0")
        self.assertEqual(EXPECTED_DEPENDENCIES, {"packaging": "26.3"})
        self.assertEqual(validate_runtime_dependencies(), EXPECTED_DEPENDENCIES)

    def test_cli_requires_operator_exclusions_and_ignores_target_discovery(self):
        private_name = "private/local-history"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private = root / ".private"
            private.mkdir()
            exclusions = private / "patch-cabinet-exclusions.json"
            exclusions.write_text(json.dumps([private_name]), encoding="utf-8")
            source = root / "patch-cabinet" / "data" / "candidates.json"
            source.parent.mkdir(parents=True)
            nested_private = source.parent / ".private"
            nested_private.mkdir()
            (nested_private / "patch-cabinet-exclusions.json").write_text(
                "[]", encoding="utf-8"
            )
            source.write_text(
                json.dumps([self.candidate(repository=private_name)]), encoding="utf-8"
            )
            json_out = root / "out.json"
            markdown_out = root / "out.md"

            with self.assertRaisesRegex(ValueError, "operator-controlled exclusion"):
                main(
                    [
                        "score",
                        str(source),
                        "--as-of",
                        AS_OF.isoformat(),
                        "--json-out",
                        str(json_out),
                    ]
                )

            main(
                [
                    "score",
                    str(source),
                    "--as-of",
                    AS_OF.isoformat(),
                    "--exclusions-file",
                    str(exclusions),
                    "--json-out",
                    str(json_out),
                    "--markdown-out",
                    str(markdown_out),
                ]
            )

            self.assertNotIn(private_name, json_out.read_text(encoding="utf-8"))
            self.assertNotIn(private_name, markdown_out.read_text(encoding="utf-8"))

    def test_cli_rejects_duplicate_keys_and_nonstandard_constants(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "candidates.json"
            raw = json.dumps([self.candidate()])
            source.write_text(
                raw.replace(
                    '"requires_secrets": false',
                    '"requires_secrets": true, "requires_secrets": false',
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                main(
                    [
                        "score",
                        str(source),
                        "--as-of",
                        AS_OF.isoformat(),
                        "--allow-no-local-exclusions",
                    ]
                )

            source.write_text(
                raw.replace('"estimated_hours": 2', '"estimated_hours": NaN'),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "non-standard JSON constant"):
                main(
                    [
                        "score",
                        str(source),
                        "--as-of",
                        AS_OF.isoformat(),
                        "--allow-no-local-exclusions",
                    ]
                )

    def test_cli_enforces_manifest_and_candidate_limits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "candidates.json"
            source.write_text(json.dumps([self.candidate()]), encoding="utf-8")
            with patch("patch_cabinet.cli.MAX_MANIFEST_BYTES", 1):
                with self.assertRaisesRegex(ValueError, "manifest exceeds"):
                    main(
                        [
                            "score",
                            str(source),
                            "--as-of",
                            AS_OF.isoformat(),
                            "--allow-no-local-exclusions",
                        ]
                    )
            with patch("patch_cabinet.cli.MAX_CANDIDATES", 0):
                with self.assertRaisesRegex(ValueError, "candidate limit"):
                    main(
                        [
                            "score",
                            str(source),
                            "--as-of",
                            AS_OF.isoformat(),
                            "--allow-no-local-exclusions",
                        ]
                    )

    def test_historical_flag_always_forces_historical_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "candidates.json"
            output = root / "results.json"
            source.write_text(json.dumps([self.candidate()]), encoding="utf-8")
            main(
                [
                    "score",
                    str(source),
                    "--as-of",
                    AS_OF.isoformat(),
                    "--historical-demo",
                    "--allow-no-local-exclusions",
                    "--json-out",
                    str(output),
                ]
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["policy"]["evaluation_mode"], "historical")
            self.assertEqual(payload["results"][0]["band"], "investigate")


if __name__ == "__main__":
    unittest.main()
