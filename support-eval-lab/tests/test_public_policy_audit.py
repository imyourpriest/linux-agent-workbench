from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from support_eval_lab import public_policy_audit


class PublicPolicyAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]
        self.root = self.project / "public-policy-audit"

    def copied_project(self, temporary: str) -> Path:
        copy = Path(temporary) / "support-eval-lab"
        shutil.copytree(self.root, copy / "public-policy-audit")
        return copy

    def test_checked_pack_is_fresh_deterministic_and_inert(self) -> None:
        first = public_policy_audit.run(self.project, check=True)
        second = public_policy_audit.run(self.project, check=True)
        self.assertEqual(first, second)
        self.assertEqual(first["result"], "valid_verifier_bound_checked_tree_synthetic_fixture")
        self.assertEqual(first["revenue_usd"], "0.00")
        self.assertTrue(all(value is False for value in first["boundaries"].values()))

    def test_report_has_evidence_gaps_decisions_and_no_score_or_grade(self) -> None:
        report = json.loads((self.root / "AUDIT.json").read_text(encoding="utf-8"))
        self.assertEqual(len(report["evidence"]), 6)
        self.assertEqual(
            set(report["gaps"]),
            {"autonomous_pr_submission", "security_report_automation", "license_ip_checks"},
        )
        self.assertEqual(len(report["human_decisions"]), 4)
        serialized = json.dumps(report).casefold()
        self.assertNotIn('"score"', serialized)
        self.assertNotIn('"grade"', serialized)
        self.assertIn("79.00_unvalidated_not_offered", serialized)
        markdown = (self.root / "AUDIT.md").read_bytes()
        self.assertTrue(markdown.endswith(b"\n"))
        self.assertFalse(markdown.endswith(b"\n\n"))

    def test_real_input_shape_stops_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            source_path = project / "public-policy-audit" / "input" / "SOURCE.json"
            source = json.loads(source_path.read_text())
            source["source_kind"] = "customer_approved_public_repository"
            source["customer_approved_public_input"] = True
            source["synthetic"] = False
            source_path.write_text(
                json.dumps(source, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "SEL-GH-001"):
                public_policy_audit.run(project, check=False)

    def test_duplicate_key_nonstandard_number_and_unknown_field_are_rejected(self) -> None:
        mutations = (
            lambda text: text.replace(
                '"schema_version": "1"',
                '"schema_version": "1", "schema_version": "1"',
            ),
            lambda text: text.replace('"synthetic": true', '"synthetic": NaN'),
            lambda text: text.replace('"synthetic": true', '"synthetic": true, "extra": false'),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as temporary:
                project = self.copied_project(temporary)
                source = project / "public-policy-audit" / "input" / "SOURCE.json"
                source.write_text(mutate(source.read_text()), encoding="utf-8", newline="\n")
                with self.assertRaises(ValueError):
                    public_policy_audit.run(project, check=False)

    def test_coordinated_fixture_and_attacker_digest_rewrite_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            input_root = project / "public-policy-audit" / "input"
            replacements = {
                "AI_POLICY.md": "# Relabeled policy\n\nEverything is allowed.\n",
                "CONTRIBUTING.md": "# Relabeled contributing\n\nNo review is needed.\n",
            }
            for name, text in replacements.items():
                (input_root / name).write_text(text, encoding="utf-8", newline="\n")
            source_path = input_root / "SOURCE.json"
            source = json.loads(source_path.read_text(encoding="utf-8"))
            source["files"] = {
                name: hashlib.sha256((input_root / name).read_bytes()).hexdigest()
                for name in replacements
            }
            source_path.write_text(
                json.dumps(source, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "verifier-owned checked-tree"):
                public_policy_audit.run(project, check=False)

    def test_markdown_injection_bidi_and_control_characters_are_rejected(self) -> None:
        mutations = ("<script>/repo", "synthetic/evil\u202erepo", "synthetic/evil\u0001repo")
        for repository in mutations:
            with self.subTest(repository=repository), tempfile.TemporaryDirectory() as temporary:
                project = self.copied_project(temporary)
                source_path = project / "public-policy-audit" / "input" / "SOURCE.json"
                source = json.loads(source_path.read_text())
                source["repository"] = repository
                source["repository_url"] = f"https://example.invalid/{repository}"
                source_path.write_text(
                    json.dumps(source, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                with self.assertRaises(ValueError):
                    public_policy_audit.run(project, check=False)

    def test_resource_and_inventory_bounds_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "public-policy-audit"
            (root / "input" / "extra.md").write_text("extra", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inventory"):
                public_policy_audit.run(project, check=False)
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            target = project / "public-policy-audit" / "input" / "AI_POLICY.md"
            target.write_bytes(b"x" * (public_policy_audit.MAX_FILE_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "byte limit"):
                public_policy_audit.run(project, check=False)

    def test_input_hardlink_and_output_hardlink_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "public-policy-audit"
            source = root / "input" / "AI_POLICY.md"
            alias = root / "input" / "alias.md"
            os.link(source, alias)
            with self.assertRaises(ValueError):
                public_policy_audit.run(project, check=False)
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            first_output = project / "public-policy-audit" / "AUDIT.json"
            first_before = first_output.read_bytes()
            output = project / "public-policy-audit" / "AUDIT.md"
            victim = Path(temporary) / "victim"
            output.unlink()
            victim.write_text("victim", encoding="utf-8")
            os.link(victim, output)
            with self.assertRaisesRegex(ValueError, "single-link"):
                public_policy_audit.run(project, check=False)
            self.assertEqual(first_output.read_bytes(), first_before)
            self.assertEqual(victim.read_text(), "victim")

    def test_linked_input_directory_is_rejected_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "public-policy-audit"
            actual = Path(temporary) / "actual-input"
            shutil.move(root / "input", actual)
            try:
                (root / "input").symlink_to(actual, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlink creation unavailable: {error}")
            with self.assertRaisesRegex(ValueError, "non-link"):
                public_policy_audit.run(project, check=False)

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junctioned_input_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "public-policy-audit"
            actual = Path(temporary) / "actual-input"
            shutil.move(root / "input", actual)
            junction = root / "input"
            result = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(junction), str(actual)],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                self.skipTest(f"junction creation unavailable: {result.stderr.strip()}")
            try:
                self.assertTrue(junction.is_junction())
                with self.assertRaisesRegex(ValueError, "non-link"):
                    public_policy_audit.run(project, check=False)
            finally:
                os.rmdir(junction)

    def test_stale_generated_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            output = project / "public-policy-audit" / "AUDIT.md"
            output.write_text("stale\n", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(ValueError, "stale"):
                public_policy_audit.run(project, check=True)

    def test_no_network_subprocess_shell_or_activation_path(self) -> None:
        source = Path(public_policy_audit.__file__).read_text(encoding="utf-8")
        forbidden_source = (
            "import socket", "import urllib", "import requests", "import subprocess",
            "os.system", "def activate",
        )
        for forbidden in forbidden_source:
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
