from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from release_readiness.audit import Audit, Finding, audit_repository
from release_readiness.cli import render_markdown


SHA = "a" * 40


class AuditTests(unittest.TestCase):
    def write(self, root: Path, relative: str, content: str = "") -> None:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    def audit(self, root: Path):
        return audit_repository(
            root,
            repository_url="https://example.invalid/example/tool",
            commit_sha=SHA,
            observed_at="2026-08-07",
            unverified_demo=True,
        )

    def by_id(self, result):
        return {finding.identifier: finding for finding in result.findings}

    def test_incomplete_repo_reports_gaps_without_grade(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "README.md", "# Tool\n\n## Installation\n")
            self.write(root, "pyproject.toml", "[project]\nname='tool'\n")
            result = self.audit(root)
            findings = self.by_id(result)

            self.assertEqual(findings["package-metadata"].status, "signal_detected")
            self.assertEqual(findings["checksums"].status, "not_detected")
            report = render_markdown(result)
            self.assertIn("No aggregate grade", report)
            self.assertIn("Target code executed: no", report)
            self.assertIn("unverified_local_demo", report)
            self.assertIn("Declared commit", report)
            payload = result.to_dict()
            self.assertIn("declared_commit_sha", payload)
            self.assertNotIn("commit_sha", payload)

    def test_release_signals_are_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "LICENSE", "MIT")
            self.write(root, "go.mod", "module example.invalid/tool\n")
            self.write(root, "CHANGELOG.md", "# Changes\n")
            self.write(
                root,
                ".github/workflows/release.yml",
                "on: workflow_dispatch\n"
                "jobs:\n"
                "  release:\n"
                "    steps:\n"
                "      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567\n"
                "      - run: goreleaser release\n",
            )
            self.write(
                root,
                ".goreleaser.yml",
                "goos: [linux]\n"
                "goarch: [amd64, arm64]\n"
                "checksum: checksums.txt\n"
                "sboms: [archive]\n",
            )
            self.write(
                root,
                "README.md",
                "# Tool\n\n## Installation\ninstall it\n\n## Uninstall\nremove it\n",
            )
            self.write(root, "main_test.go", "package main\n")
            result = self.audit(root)
            findings = self.by_id(result)

            for identifier in (
                "license",
                "package-metadata",
                "changelog",
                "ci",
                "release-workflow",
                "linux-architectures",
                "checksums",
                "sbom",
                "install",
                "uninstall",
                "tests",
                "pinned-actions",
            ):
                self.assertEqual(findings[identifier].status, "signal_detected", identifier)

    def test_unpinned_action_is_reported_with_reference(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(
                root,
                ".github/workflows/ci.yml",
                "steps:\n  - uses: actions/checkout@v4\n",
            )
            result = self.audit(root)
            finding = self.by_id(result)["pinned-actions"]
            self.assertEqual(finding.status, "potential_gap")
            self.assertIn("actions/checkout@v4", finding.evidence[0])

    def test_mutable_container_action_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(
                root,
                ".github/workflows/ci.yml",
                "steps:\n  - uses: docker://alpine:latest\n",
            )
            finding = self.by_id(self.audit(root))["pinned-actions"]
            self.assertEqual(finding.status, "potential_gap")
            self.assertIn("docker://alpine:latest", finding.evidence[0])

    def test_documentation_mentions_do_not_fake_release_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(
                root,
                "README.md",
                "# Tool\n\n## Installation\nWe do not use GoReleaser, checksums, or an SBOM.\n",
            )
            findings = self.by_id(self.audit(root))
            for identifier in ("release-workflow", "checksums", "sbom"):
                self.assertEqual(findings[identifier].status, "not_detected", identifier)

    def test_total_text_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "README.md", "123456")
            with patch("release_readiness.audit.MAX_TOTAL_TEXT_BYTES", 5):
                with self.assertRaisesRegex(ValueError, "text audit limit"):
                    self.audit(root)

    def test_symlinked_file_is_not_read(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root.parent / f"{root.name}-outside.txt"
            outside.write_text("goreleaser linux amd64 arm64 sbom", encoding="utf-8")
            try:
                try:
                    os.symlink(outside, root / "linked.txt")
                except OSError as error:
                    self.skipTest(f"symlink creation unavailable: {error}")
                result = self.audit(root)
                self.assertEqual(result.files_considered, 0)
                self.assertEqual(self.by_id(result)["release-workflow"].status, "not_detected")
            finally:
                outside.unlink(missing_ok=True)

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junctioned_directory_is_not_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            container = Path(temporary)
            root = container / "root"
            outside = container / "outside"
            root.mkdir()
            outside.mkdir()
            self.write(outside, "release.yml", "goreleaser linux amd64 arm64 sbom")
            junction = root / "linked-release"
            result = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                self.skipTest(f"junction creation unavailable: {result.stderr.strip()}")
            try:
                audit = self.audit(root)
                self.assertEqual(audit.files_considered, 0)
                self.assertEqual(self.by_id(audit)["release-workflow"].status, "not_detected")
            finally:
                os.rmdir(junction)

    def test_invalid_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "40-character"):
                audit_repository(
                    Path(temporary),
                    repository_url="https://example.invalid/tool",
                    commit_sha="main",
                    observed_at="2026-08-07",
                    unverified_demo=True,
                )
            with self.assertRaisesRegex(ValueError, "40-character"):
                audit_repository(
                    Path(temporary),
                    repository_url="https://example.invalid/tool",
                    commit_sha="0" * 40,
                    observed_at="2026-08-07",
                    unverified_demo=True,
                )

    def test_invalid_url_and_date_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                audit_repository(
                    root,
                    repository_url="file:///private/repo",
                    commit_sha=SHA,
                    observed_at="2026-08-07",
                    unverified_demo=True,
                )
            with self.assertRaisesRegex(ValueError, "valid YYYY-MM-DD"):
                audit_repository(
                    root,
                    repository_url="https://example.invalid/tool",
                    commit_sha=SHA,
                    observed_at="2026-02-30",
                    unverified_demo=True,
                )

    def test_verified_mode_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "verified acquisition is not implemented"):
                audit_repository(
                    Path(temporary),
                    repository_url="https://example.invalid/tool",
                    commit_sha=SHA,
                    observed_at="2026-08-07",
                )

    def test_demo_requires_date_and_rejects_future_date(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "observed_at is required"):
                audit_repository(
                    root,
                    repository_url="https://example.invalid/tool",
                    commit_sha=SHA,
                    unverified_demo=True,
                )
            with self.assertRaisesRegex(ValueError, "cannot be in the future"):
                audit_repository(
                    root,
                    repository_url="https://example.invalid/tool",
                    commit_sha=SHA,
                    observed_at="2099-01-01",
                    unverified_demo=True,
                )

    def test_file_count_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "README.md", "small")
            with patch("release_readiness.audit.MAX_FILES", 0):
                with self.assertRaisesRegex(ValueError, "file audit limit"):
                    self.audit(root)

    def test_total_entry_limit_is_enforced_incrementally(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "README.md", "small")
            with patch("release_readiness.audit.MAX_ENTRIES", 0):
                with self.assertRaisesRegex(ValueError, "entry audit limit"):
                    self.audit(root)

    def test_target_files_are_never_executed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = root / "executed.txt"
            self.write(
                root,
                "setup.py",
                "from pathlib import Path\nPath('executed.txt').write_text('bad')\n",
            )
            self.write(root, "pyproject.toml", "[project]\nname='demo'\n")
            self.audit(root)
            self.assertFalse(marker.exists())

    def test_collector_does_not_invoke_git_or_a_subprocess(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "README.md", "# Tool\n")
            with patch("subprocess.Popen") as popen:
                result = self.audit(root)
            popen.assert_not_called()
            self.assertEqual(result.provenance_status, "unverified_local_demo")

    def test_composite_and_quoted_action_references_are_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(
                root,
                "action.yml",
                "runs:\n"
                "  using: 'composite'\n"
                "  steps:\n"
                "    - uses: \"actions/checkout@0123456789abcdef0123456789abcdef01234567\"\n",
            )
            finding = self.by_id(self.audit(root))["pinned-actions"]
            self.assertEqual(finding.status, "signal_detected")

    def test_markdown_escapes_repository_controlled_evidence(self):
        audit = Audit(
            repository_url="https://example.invalid/tool",
            commit_sha=SHA,
            observed_at="2026-08-07",
            observation_source="caller_supplied_for_unverified_demo",
            provenance_status="caller_supplied_unverified",
            provenance_details=("synthetic",),
            rules_sha256="f" * 64,
            files_considered=1,
            findings=(
                Finding(
                    identifier="hostile",
                    title="Static title",
                    status="signal_detected",
                    review_priority="manual_review",
                    evidence=("path.md\n# Forged <img src=x>\u202eTXT\u2028next",),
                    recommendation="Inspect manually.",
                ),
            ),
        )
        report = render_markdown(audit)
        self.assertNotIn("\n# Forged", report)
        self.assertNotIn("<img src=x>", report)
        self.assertIn("\\n# Forged &lt;img src=x&gt;", report)
        self.assertNotIn("\u202e", report)
        self.assertNotIn("\u2028", report)
        self.assertIn("\\u202e", report)
        self.assertIn("\\u2028", report)

    def test_architecture_evidence_is_sorted_before_truncation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("z-release.yml", "a-release.yml", "m-release.yml"):
                self.write(
                    root,
                    f".github/workflows/{name}",
                    "name: release linux amd64 arm64\n",
                )
            with patch("release_readiness.audit.MAX_EVIDENCE_ITEMS", 2):
                evidence = self.by_id(self.audit(root))["linux-architectures"].evidence
            self.assertTrue(evidence[0].startswith(".github/workflows/a-release.yml"))
            self.assertTrue(evidence[1].startswith(".github/workflows/m-release.yml"))
            self.assertIn("additional", evidence[2])

if __name__ == "__main__":
    unittest.main()
