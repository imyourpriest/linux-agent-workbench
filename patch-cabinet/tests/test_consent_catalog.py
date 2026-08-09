from __future__ import annotations

import copy
import html
import json
import os
import tempfile
import unittest
from datetime import date
from pathlib import Path

from patch_cabinet import consent_catalog


class ConsentCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.records = self.root / "records"
        self.records.mkdir()

    def _record(
        self,
        *,
        repository: str = "owner/project",
        commit: str = "a" * 40,
        digest: str = "b" * 64,
        observed: str = "2026-08-08",
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
            "observed_at": observed,
            "reviewed_at": observed,
            "reviewer_basis": "manual_pinned_text_review",
            "workflow_scope": "agent_selects_prepares_and_submits_with_disclosure",
            "classification": "insufficiently_explicit",
            "semantic_review": "manual",
            "supersedes": supersedes,
            "notes": "The pinned guide does not explicitly permit the exact workflow.",
        }

    def _write(self, record: dict[str, object], *, filename: str | None = None) -> Path:
        target = self.records / (filename or f"{record['record_id']}.json")
        target.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
        return target

    def test_valid_record_builds_deterministic_non_authorizing_index(self) -> None:
        record = self._record()
        self._write(record)
        loaded = consent_catalog.load_catalog(self.records)
        first = consent_catalog.build_index(loaded, as_of=date(2026, 8, 8))
        second = consent_catalog.build_index(loaded, as_of=date(2026, 8, 8))
        self.assertEqual(first, second)
        self.assertEqual(first["summary"]["current_for_7_day_candidate_window"], 1)
        self.assertNotIn("eligible", json.dumps(first).casefold())
        self.assertIn("not current permission", first["claim_boundary"])

    def test_staleness_boundary_is_explicit(self) -> None:
        self._write(self._record(observed="2026-08-01"))
        current = consent_catalog.build_index(
            consent_catalog.load_catalog(self.records), as_of=date(2026, 8, 8)
        )
        self._write(self._record(observed="2026-07-31"))
        stale = consent_catalog.build_index(
            consent_catalog.load_catalog(self.records), as_of=date(2026, 8, 8)
        )
        self.assertEqual(current["records"][0]["freshness"], "current_for_7_day_candidate_window")
        self.assertEqual(stale["records"][0]["freshness"], "stale")

    def test_repository_catalog_has_expected_conservative_counts(self) -> None:
        project = Path(__file__).resolve().parents[1]
        loaded = consent_catalog.load_catalog(project / "data" / "consent-catalog" / "v1")
        report = consent_catalog.build_index(loaded, as_of=date(2026, 8, 8))
        self.assertEqual(report["summary"]["records"], 4)
        self.assertEqual(report["summary"]["explicitly_allows"], 0)
        self.assertEqual(report["summary"]["explicitly_disallows"], 2)
        self.assertEqual(report["summary"]["insufficiently_explicit"], 2)

    def test_strict_json_rejects_duplicate_nonstandard_and_numeric_values(self) -> None:
        valid = json.dumps(self._record())
        probes = {
            "duplicate": valid.replace('"notes":', '"notes": "first", "notes":', 1),
            "constant": valid.replace('"supersedes": null', '"supersedes": NaN'),
            "integer": valid.replace('"schema_version": "1"', '"schema_version": 1'),
            "deep": "[" * 20 + "]" * 20,
        }
        for label, payload in probes.items():
            with self.subTest(label=label):
                for existing in self.records.iterdir():
                    existing.unlink()
                (self.records / "probe.json").write_text(payload, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "strict JSON"):
                    consent_catalog.load_catalog(self.records)

    def test_exact_fields_identity_hash_and_dates_fail_closed(self) -> None:
        transformations = {
            "unknown": lambda value: value.update({"extra": "x"}),
            "record-id": lambda value: value.update({"record_id": "github-wrong-a-b"}),
            "null-digest": lambda value: value.update({"source_sha256": "0" * 64}),
            "uppercase-commit": lambda value: value.update({"commit_sha": "A" * 40}),
            "date-order": lambda value: value.update({"reviewed_at": "2026-08-07"}),
            "future-observation": lambda value: value.update(
                {"observed_at": "2999-01-01", "reviewed_at": "2999-01-01"}
            ),
            "future-review": lambda value: value.update({"reviewed_at": "2999-01-01"}),
            "bidi-note": lambda value: value.update({"notes": "safe\u202eunsafe"}),
            "workflow": lambda value: value.update({"workflow_scope": "human_led_ai_assistance"}),
        }
        for label, transform in transformations.items():
            with self.subTest(label=label):
                value = self._record()
                transform(value)
                with self.assertRaises(ValueError):
                    consent_catalog._parse_record(value)

    def test_policy_url_rejects_wrong_scope_and_noncanonical_paths(self) -> None:
        record = self._record()
        urls = (
            "https://github.com/other/project/blob/" + "a" * 40 + "/CONTRIBUTING.md",
            "https://github.com/owner/project/blob/main/CONTRIBUTING.md",
            "https://github.com/owner/project/blob/" + "a" * 40 + "/%2e%2e/SECURITY.md",
            "https://github.com/owner/project/blob/" + "a" * 40 + "/docs\\POLICY.md",
            "https://github.com/owner/project/blob/" + "a" * 40 + "/CONTRIBUTING.md?raw=1",
        )
        for url in urls:
            with self.subTest(url=url):
                probe = copy.deepcopy(record)
                probe["policy_source_url"] = url
                with self.assertRaises(ValueError):
                    consent_catalog._parse_record(probe)

    def test_filename_and_inventory_are_strict(self) -> None:
        self._write(self._record(), filename="wrong.json")
        with self.assertRaisesRegex(ValueError, "filename"):
            consent_catalog.load_catalog(self.records)
        for existing in self.records.iterdir():
            existing.unlink()
        (self.records / "README.md").write_text("not a record", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "only .json"):
            consent_catalog.load_catalog(self.records)

    def test_record_file_symlink_is_rejected_when_supported(self) -> None:
        outside = self.root / "outside.json"
        outside.write_text(json.dumps(self._record()), encoding="utf-8")
        link = self.records / "linked.json"
        try:
            link.symlink_to(outside)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "regular JSON"):
            consent_catalog.load_catalog(self.records)

    def test_missing_forked_and_cyclic_successors_are_rejected(self) -> None:
        first = self._record()
        missing = self._record(commit="c" * 40, digest="d" * 64, supersedes="github-missing-" + "1" * 12 + "-" + "2" * 12)
        self._write(first)
        self._write(missing)
        with self.assertRaisesRegex(ValueError, "different catalog record"):
            consent_catalog.load_catalog(self.records)

        for existing in self.records.iterdir():
            existing.unlink()
        second = self._record(commit="c" * 40, digest="d" * 64)
        first["supersedes"] = second["record_id"]
        second["supersedes"] = first["record_id"]
        self._write(first)
        self._write(second)
        with self.assertRaisesRegex(ValueError, "cycle"):
            consent_catalog.load_catalog(self.records)

        for existing in self.records.iterdir():
            existing.unlink()
        previous = self._record(observed="2026-08-08")
        earlier_successor = self._record(
            commit="c" * 40,
            digest="d" * 64,
            observed="2026-08-07",
            supersedes=previous["record_id"],
        )
        self._write(previous)
        self._write(earlier_successor)
        with self.assertRaisesRegex(ValueError, "chronological"):
            consent_catalog.load_catalog(self.records)

    def test_manual_notes_are_rendered_as_inert_code(self) -> None:
        record = self._record()
        note = "safe [link](https://evil.invalid) ![image](https://evil.invalid/x) <script>"
        record["notes"] = note
        self._write(record)
        report = consent_catalog.build_index(
            consent_catalog.load_catalog(self.records), as_of=date(2026, 8, 8)
        )
        rendered = consent_catalog.render_markdown(report)
        note_line = next(line for line in rendered.splitlines() if "Manual review note" in line)
        self.assertNotIn("[link]", note_line)
        self.assertNotIn("https://evil.invalid", note_line)
        self.assertNotIn("<script>", note_line)
        encoded = note_line.split("<code>", 1)[1].split("</code>", 1)[0]
        self.assertEqual(html.unescape(encoded), note)
        self.assertEqual(rendered.count("[source](https://"), 1)

    def test_initial_acquisition_receipt_binds_every_catalog_record(self) -> None:
        project = Path(__file__).resolve().parents[1]
        records = consent_catalog.load_catalog(project / "data" / "consent-catalog" / "v1")
        receipt = json.loads(
            (project / "data" / "consent-catalog" / "ACQUISITION_RECEIPT.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            set(receipt),
            {"schema_version", "receipt_id", "retrieved_at", "method", "claim_boundary", "sources"},
        )
        self.assertEqual(receipt["schema_version"], "1")
        self.assertIn("not a signature", receipt["claim_boundary"])
        by_id = {item["record_id"]: item for item in receipt["sources"]}
        self.assertEqual(set(by_id), {item.record_id for item in records})
        for record in records:
            source = by_id[record.record_id]
            self.assertEqual(source["repository"], record.repository)
            self.assertEqual(source["commit_sha"], record.commit_sha)
            self.assertEqual(source["policy_path"], record.policy_path)
            self.assertEqual(source["source_sha256"], record.source_sha256)
            self.assertEqual(
                source["api_url"],
                f"https://api.github.com/repos/{record.repository}/contents/{record.policy_path}"
                f"?ref={record.commit_sha}",
            )
            self.assertRegex(source["git_blob_sha1"], r"^[0-9a-f]{40}$")
            self.assertGreater(source["source_bytes"], 0)

    def test_output_alias_and_catalog_directory_output_are_rejected(self) -> None:
        source = self._write(self._record())
        alias = self.root / "alias.json"
        try:
            os.link(source, alias)
        except OSError as error:
            self.skipTest(f"hard-link creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "aliases"):
            consent_catalog.main(
                [str(self.records), "--as-of", "2026-08-08", "--json-out", str(alias)]
            )
        with self.assertRaisesRegex(ValueError, "inside"):
            consent_catalog.main(
                [
                    str(self.records),
                    "--as-of",
                    "2026-08-08",
                    "--json-out",
                    str(self.records / "index.json"),
                ]
            )

    def test_cli_outputs_are_byte_deterministic_and_lf_only(self) -> None:
        self._write(self._record())
        json_out = self.root / "index.json"
        markdown_out = self.root / "index.md"
        arguments = [
            str(self.records),
            "--as-of",
            "2026-08-08",
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
        consent_catalog.main(arguments)
        first = (json_out.read_bytes(), markdown_out.read_bytes())
        consent_catalog.main(arguments)
        second = (json_out.read_bytes(), markdown_out.read_bytes())
        self.assertEqual(first, second)
        self.assertNotIn(b"\r\n", first[0] + first[1])


if __name__ == "__main__":
    unittest.main()
