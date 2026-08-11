from __future__ import annotations

import copy
import html
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from patch_cabinet import consent_catalog, policy_profile_catalog


class PolicyProfileCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.consents = self.root / "consents"
        self.profiles = self.root / "profiles"
        self.consents.mkdir()
        self.profiles.mkdir()

    def _consent(
        self,
        *,
        repository: str = "owner/project",
        commit: str = "a" * 40,
        digest: str = "b" * 64,
        supersedes: str | None = None,
    ) -> dict[str, object]:
        record_id = consent_catalog.expected_record_id(repository, commit, digest)
        return {
            "schema_version": "1",
            "record_id": record_id,
            "repository": repository,
            "repository_url": f"https://github.com/{repository}",
            "commit_sha": commit,
            "policy_source_url": (
                f"https://github.com/{repository}/blob/{commit}/CONTRIBUTING.md"
            ),
            "policy_path": "CONTRIBUTING.md",
            "source_sha256": digest,
            "observed_at": "2026-08-10",
            "reviewed_at": "2026-08-10",
            "reviewer_basis": "manual_pinned_text_review",
            "workflow_scope": "agent_selects_prepares_and_submits_with_disclosure",
            "classification": "insufficiently_explicit",
            "semantic_review": "manual",
            "supersedes": supersedes,
            "notes": "The pinned guide does not explicitly permit the exact workflow.",
        }

    def _profile(
        self, consent: dict[str, object], *, supersedes: str | None = None
    ) -> dict[str, object]:
        return {
            "schema_version": "1",
            "profile_id": consent["record_id"],
            "consent_record_id": consent["record_id"],
            "repository": consent["repository"],
            "commit_sha": consent["commit_sha"],
            "policy_path": consent["policy_path"],
            "source_sha256": consent["source_sha256"],
            "dimensions": {
                "autonomous_issue_submission": "not_explicit",
                "autonomous_pr_submission": "not_explicit",
                "human_review": "required",
                "disclosure": "not_explicit",
                "human_accountability": "required",
                "license_ip_checks": "not_explicit",
                "good_first_issue_automation": "not_explicit",
                "security_report_automation": "not_explicit",
            },
            "semantic_review": "manual",
            "reviewer_basis": "manual_pinned_text_normalization",
            "supersedes": supersedes,
            "notes": "The pinned guide requires human review and accountability.",
        }

    def _write_consent(self, value: dict[str, object]) -> Path:
        target = self.consents / f"{value['record_id']}.json"
        target.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
        return target

    def _write_profile(
        self, value: dict[str, object], *, filename: str | None = None, text: str | None = None
    ) -> Path:
        target = self.profiles / (filename or f"{value['profile_id']}.json")
        target.write_text(
            text if text is not None else json.dumps(value, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return target

    def _valid_pair(self) -> tuple[dict[str, object], dict[str, object]]:
        consent = self._consent()
        profile = self._profile(consent)
        self._write_consent(consent)
        self._write_profile(profile)
        return consent, profile

    def test_valid_profile_builds_deterministic_non_authorizing_index(self) -> None:
        self._valid_pair()
        loaded = policy_profile_catalog.load_profiles(self.profiles, self.consents)
        first = policy_profile_catalog.build_index(loaded)
        second = policy_profile_catalog.build_index(loaded)
        self.assertEqual(first, second)
        self.assertEqual(first["summary"], {"profiles": 1})
        self.assertIn("no automatic prose interpretation", first["claim_boundary"])
        self.assertNotRegex(json.dumps(first), r'"(?:eligible|ready|authorized)"')

    def test_repository_profiles_bind_all_five_consent_records(self) -> None:
        project = Path(__file__).resolve().parents[1]
        consent_dir = project / "data" / "consent-catalog" / "v1"
        profile_dir = project / "data" / "policy-profile-catalog" / "v1"
        loaded = policy_profile_catalog.load_profiles(profile_dir, consent_dir)
        self.assertEqual(len(loaded), 5)
        self.assertEqual(
            {item.consent_record_id for item in loaded},
            {item.record_id for item in consent_catalog.load_catalog(consent_dir)},
        )
        self.assertFalse(any("eligible" in item.to_index_dict() for item in loaded))

    def test_dimension_names_and_vocabularies_are_exact(self) -> None:
        consent = self._consent()
        base = self._profile(consent)
        probes = []
        extra = copy.deepcopy(base)
        extra["dimensions"]["extra"] = "not_explicit"
        probes.append(extra)
        missing = copy.deepcopy(base)
        del missing["dimensions"]["disclosure"]
        probes.append(missing)
        wrong_three_way = copy.deepcopy(base)
        wrong_three_way["dimensions"]["autonomous_pr_submission"] = "required"
        probes.append(wrong_three_way)
        wrong_expectation = copy.deepcopy(base)
        wrong_expectation["dimensions"]["human_review"] = "allowed"
        probes.append(wrong_expectation)
        for probe in probes:
            with self.subTest(probe=probe["dimensions"]):
                with self.assertRaises(ValueError):
                    policy_profile_catalog._parse_profile(probe)

    def test_strict_json_rejects_duplicate_nonstandard_numbers_depth_and_bom(self) -> None:
        consent = self._consent()
        self._write_consent(consent)
        valid = json.dumps(self._profile(consent))
        probes = {
            "duplicate": valid.replace('"notes":', '"notes": "first", "notes":', 1),
            "constant": valid.replace('"supersedes": null', '"supersedes": NaN'),
            "number": valid.replace('"schema_version": "1"', '"schema_version": 1'),
            "deep": "[" * 20 + "]" * 20,
            "bom": "\ufeff" + valid,
        }
        for label, text in probes.items():
            with self.subTest(label=label):
                for existing in self.profiles.iterdir():
                    existing.unlink()
                self._write_profile(self._profile(consent), filename="probe.json", text=text)
                with self.assertRaises(ValueError):
                    policy_profile_catalog.load_profiles(self.profiles, self.consents)

    def test_unknown_fields_controls_null_digest_and_noncanonical_ids_fail(self) -> None:
        consent = self._consent()
        base = self._profile(consent)
        probes = []
        unknown = copy.deepcopy(base)
        unknown["extra"] = "x"
        probes.append(unknown)
        control = copy.deepcopy(base)
        control["notes"] = "unsafe\u202evalue"
        probes.append(control)
        null_digest = copy.deepcopy(base)
        null_digest["source_sha256"] = "0" * 64
        probes.append(null_digest)
        wrong_id = copy.deepcopy(base)
        wrong_id["profile_id"] = "github-wrong-aaaaaaaaaaaa-bbbbbbbbbbbb"
        probes.append(wrong_id)
        wrong_basis = copy.deepcopy(base)
        wrong_basis["reviewer_basis"] = "automatic"
        probes.append(wrong_basis)
        for probe in probes:
            with self.subTest(profile=probe):
                with self.assertRaises(ValueError):
                    policy_profile_catalog._parse_profile(probe)

    def test_repeated_provenance_must_match_exactly_one_consent(self) -> None:
        consent = self._consent()
        self._write_consent(consent)
        for field, replacement in {
            "repository": "other/project",
            "commit_sha": "c" * 40,
            "policy_path": "docs/POLICY.md",
            "source_sha256": "d" * 64,
            "consent_record_id": "github-missing-aaaaaaaaaaaa-bbbbbbbbbbbb",
        }.items():
            with self.subTest(field=field):
                for existing in self.profiles.iterdir():
                    existing.unlink()
                profile = self._profile(consent)
                profile[field] = replacement
                if field == "consent_record_id":
                    profile["profile_id"] = replacement
                self._write_profile(profile)
                with self.assertRaises(ValueError):
                    policy_profile_catalog.load_profiles(self.profiles, self.consents)

    def test_filename_and_inventory_are_strict(self) -> None:
        consent = self._consent()
        self._write_consent(consent)
        self._write_profile(self._profile(consent), filename="wrong.json")
        with self.assertRaisesRegex(ValueError, "filename"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)
        for existing in self.profiles.iterdir():
            existing.unlink()
        (self.profiles / "README.md").write_text("not a profile", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "only .json"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)

    def test_file_size_and_profile_count_are_bounded(self) -> None:
        consent = self._consent()
        self._write_consent(consent)
        oversized = self.profiles / "oversized.json"
        oversized.write_bytes(b" " * (policy_profile_catalog.MAX_FILE_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "exceeds"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)
        oversized.unlink()
        for index in range(policy_profile_catalog.MAX_PROFILES + 1):
            (self.profiles / f"{index:03d}.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "profile limit"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)

    def test_profile_and_input_directory_symlinks_are_rejected_when_supported(self) -> None:
        consent = self._consent()
        self._write_consent(consent)
        outside = self.root / "outside.json"
        outside.write_text(json.dumps(self._profile(consent)), encoding="utf-8")
        try:
            (self.profiles / "linked.json").symlink_to(outside)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "regular JSON"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)
        linked_dir = self.root / "linked-profiles"
        linked_dir.symlink_to(self.profiles, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "non-link regular directory"):
            policy_profile_catalog.load_profiles(linked_dir, self.consents)

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junctioned_profile_directory_is_rejected(self) -> None:
        outside = self.root / "outside-profiles"
        outside.mkdir()
        junction = self.root / "linked-profiles"
        result = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            self.skipTest(f"junction creation unavailable: {result.stderr.strip()}")
        try:
            self.assertTrue(junction.is_junction())
            with self.assertRaisesRegex(ValueError, "non-link regular directory"):
                policy_profile_catalog.load_profiles(junction, self.consents)
        finally:
            os.rmdir(junction)

    def test_duplicate_consent_binding_is_rejected(self) -> None:
        consent = self._consent()
        self._write_consent(consent)
        first = self._profile(consent)
        self._write_profile(first)
        duplicate = copy.deepcopy(first)
        duplicate["profile_id"] = "github-other-aaaaaaaaaaaa-bbbbbbbbbbbb"
        self._write_profile(duplicate)
        with self.assertRaises(ValueError):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)

    def test_missing_forked_cyclic_and_cross_lineage_successors_are_rejected(self) -> None:
        first_consent = self._consent(repository="owner/project")
        second_consent = self._consent(
            repository="owner/project",
            commit="c" * 40,
            digest="d" * 64,
            supersedes=first_consent["record_id"],
        )
        self._write_consent(first_consent)
        self._write_consent(second_consent)
        first = self._profile(first_consent)
        second = self._profile(second_consent, supersedes=first["profile_id"])
        self._write_profile(first)
        self._write_profile(second)
        self.assertEqual(len(policy_profile_catalog.load_profiles(self.profiles, self.consents)), 2)

        second["supersedes"] = "github-missing-aaaaaaaaaaaa-bbbbbbbbbbbb"
        self._write_profile(second)
        with self.assertRaisesRegex(ValueError, "exactly match|different profile"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)

        second["supersedes"] = first["profile_id"]
        first["supersedes"] = second["profile_id"]
        self._write_profile(first)
        self._write_profile(second)
        with self.assertRaisesRegex(ValueError, "exactly match|lineage|cycle"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)

        for directory in (self.profiles, self.consents):
            for existing in directory.iterdir():
                existing.unlink()
        other_consent = self._consent(repository="other/project", commit="e" * 40, digest="f" * 64)
        self._write_consent(first_consent)
        self._write_consent(other_consent)
        first = self._profile(first_consent)
        other = self._profile(other_consent, supersedes=first["profile_id"])
        self._write_profile(first)
        self._write_profile(other)
        with self.assertRaisesRegex(ValueError, "exactly match|lineage"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)

    def test_consent_successor_requires_matching_profile_successor(self) -> None:
        first_consent = self._consent(repository="owner/project")
        second_consent = self._consent(
            repository="owner/project",
            commit="c" * 40,
            digest="d" * 64,
            supersedes=first_consent["record_id"],
        )
        self._write_consent(first_consent)
        self._write_consent(second_consent)
        self._write_profile(self._profile(first_consent))
        self._write_profile(self._profile(second_consent, supersedes=None))
        with self.assertRaisesRegex(ValueError, "exactly match"):
            policy_profile_catalog.load_profiles(self.profiles, self.consents)

    def test_manual_notes_are_rendered_as_inert_code(self) -> None:
        consent, profile = self._valid_pair()
        profile["notes"] = "safe [link](https://evil.invalid) ![image](x) <script>"
        self._write_profile(profile)
        report = policy_profile_catalog.build_index(
            policy_profile_catalog.load_profiles(self.profiles, self.consents)
        )
        rendered = policy_profile_catalog.render_markdown(report)
        note_line = next(line for line in rendered.splitlines() if "normalization note" in line)
        self.assertNotIn("[link]", note_line)
        self.assertNotIn("https://evil.invalid", note_line)
        self.assertNotIn("<script>", note_line)
        encoded = note_line.split("<code>", 1)[1].split("</code>", 1)[0]
        self.assertEqual(html.unescape(encoded), profile["notes"])

    def test_output_aliases_and_input_directory_outputs_are_rejected(self) -> None:
        _consent, profile = self._valid_pair()
        source = self.profiles / f"{profile['profile_id']}.json"
        alias = self.root / "alias.json"
        try:
            os.link(source, alias)
        except OSError as error:
            self.skipTest(f"hard-link creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "aliases"):
            policy_profile_catalog.main(
                [
                    str(self.profiles),
                    "--consent-records",
                    str(self.consents),
                    "--json-out",
                    str(alias),
                ]
            )
        with self.assertRaisesRegex(ValueError, "inside"):
            policy_profile_catalog.main(
                [
                    str(self.profiles),
                    "--consent-records",
                    str(self.consents),
                    "--json-out",
                    str(self.consents / "index.json"),
                ]
            )

    def test_cli_outputs_are_byte_deterministic_and_lf_only(self) -> None:
        self._valid_pair()
        json_out = self.root / "index.json"
        markdown_out = self.root / "index.md"
        arguments = [
            str(self.profiles),
            "--consent-records",
            str(self.consents),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
        policy_profile_catalog.main(arguments)
        first = (json_out.read_bytes(), markdown_out.read_bytes())
        policy_profile_catalog.main(arguments)
        second = (json_out.read_bytes(), markdown_out.read_bytes())
        self.assertEqual(first, second)
        self.assertNotIn(b"\r\n", first[0] + first[1])


if __name__ == "__main__":
    unittest.main()
