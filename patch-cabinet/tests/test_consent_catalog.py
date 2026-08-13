from __future__ import annotations

import copy
import html
import json
import os
import subprocess
import tempfile
import unittest
from datetime import date, datetime, timezone
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
        report = consent_catalog.build_index(loaded, as_of=date(2026, 8, 13))
        self.assertEqual(report["summary"]["records"], 10)
        self.assertEqual(report["summary"]["explicitly_allows"], 0)
        self.assertEqual(report["summary"]["explicitly_disallows"], 4)
        self.assertEqual(report["summary"]["insufficiently_explicit"], 6)

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

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junctioned_catalog_directory_is_rejected(self) -> None:
        outside = self.root / "outside-records"
        outside.mkdir()
        junction = self.root / "linked-records"
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
                consent_catalog.load_catalog(junction)
        finally:
            os.rmdir(junction)

    def test_missing_forked_and_cyclic_successors_are_rejected(self) -> None:
        first = self._record()
        missing = self._record(
            commit="c" * 40,
            digest="d" * 64,
            supersedes="github-missing-" + "1" * 12 + "-" + "2" * 12,
        )
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

    def test_acquisition_receipts_bind_every_catalog_record(self) -> None:
        project = Path(__file__).resolve().parents[1]
        records = consent_catalog.load_catalog(project / "data" / "consent-catalog" / "v1")
        now_utc = datetime(2026, 8, 13, 16, 0, 0, tzinfo=timezone.utc)
        receipt = consent_catalog.load_acquisition_receipt(
            project / "data" / "consent-catalog" / "ACQUISITION_RECEIPT.json",
            records,
            now_utc=now_utc,
        )
        self.assertEqual(
            set(receipt),
            {"schema_version", "receipt_id", "retrieved_at", "method", "claim_boundary", "sources"},
        )
        self.assertEqual(receipt["schema_version"], "1")
        self.assertIn("not a signature", receipt["claim_boundary"])
        by_id = {item["record_id"]: item for item in receipt["sources"]}
        initial_names = {
            "HoungDev/creator-toolkit-cli", "rxdt/loopgate_harness",
            "huggingface/transformers", "stanfordnlp/dspy",
        }
        initial_records = [item for item in records if item.repository in initial_names]
        self.assertEqual(set(by_id), {item.record_id for item in initial_records})
        for record in initial_records:
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

        ruff_receipt = consent_catalog.load_acquisition_receipt(
            project / "data" / "consent-catalog" / "RUFF_SOURCE_ACQUISITION_RECEIPT.json",
            records,
            now_utc=now_utc,
        )
        self.assertEqual(
            set(ruff_receipt),
            {"schema_version", "receipt_id", "retrieved_at", "method", "claim_boundary", "source"},
        )
        self.assertIn("not a signature", ruff_receipt["claim_boundary"])
        ruff = next(item for item in records if item.repository == "astral-sh/ruff")
        source = ruff_receipt["source"]
        self.assertEqual(source["record_id"], ruff.record_id)
        self.assertEqual(source["repository"], ruff.repository)
        self.assertEqual(source["commit_sha"], ruff.commit_sha)
        self.assertEqual(source["policy_path"], ruff.policy_path)
        self.assertEqual(source["source_sha256"], ruff.source_sha256)
        self.assertEqual(source["git_blob_sha1"], "3ebd8d449be8fb8ac25e971c51bd76745a4e84e8")
        self.assertEqual(source["source_bytes"], 50349)
        source_ids = [item["record_id"] for item in receipt["sources"]]
        source_ids.append(ruff_receipt["source"]["record_id"])
        r004_receipt = consent_catalog.load_acquisition_receipt(
            project / "data" / "consent-catalog" / "R004_SOURCE_ACQUISITION_RECEIPT.json",
            records,
            now_utc=now_utc,
        )
        self.assertEqual(len(r004_receipt["sources"]), 5)
        self.assertIn("not a signature", r004_receipt["claim_boundary"])
        source_ids.extend(item["record_id"] for item in r004_receipt["sources"])
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(set(source_ids), {record.record_id for record in records})

    def test_acquisition_receipt_strict_json_and_fields_fail_closed(self) -> None:
        project = Path(__file__).resolve().parents[1]
        records = consent_catalog.load_catalog(project / "data" / "consent-catalog" / "v1")
        now_utc = datetime(2026, 8, 11, 1, 0, 0, tzinfo=timezone.utc)
        source_path = project / "data" / "consent-catalog" / "RUFF_SOURCE_ACQUISITION_RECEIPT.json"
        valid_text = source_path.read_text(encoding="utf-8")
        valid = json.loads(valid_text)
        probes: dict[str, bytes] = {
            "duplicate": valid_text.replace(
                '"method":', '"method": "duplicate", "method":', 1
            ).encode(),
            "constant": valid_text.replace('"source_bytes": 50349', '"source_bytes": NaN').encode(),
            "float": valid_text.replace('"source_bytes": 50349', '"source_bytes": 1.5').encode(),
            "number-field": valid_text.replace(
                '"schema_version": "1"', '"schema_version": 1'
            ).encode(),
            "deep": ("[" * 20 + "]" * 20).encode(),
            "bom": b"\xef\xbb\xbf" + valid_text.encode(),
            "oversize": b" " * (consent_catalog.MAX_RECEIPT_BYTES + 1),
        }
        wrong_field = copy.deepcopy(valid)
        wrong_field["source"]["extra"] = "unexpected"
        probes["wrong-field"] = json.dumps(wrong_field).encode()
        wrong_url = copy.deepcopy(valid)
        wrong_url["source"]["api_url"] = (
            "https://api.github.com/repos/astral-sh/.github/contents/AI_POLICY.md?ref=main"
        )
        probes["wrong-url"] = json.dumps(wrong_url).encode()
        zero_digest = copy.deepcopy(valid)
        zero_digest["source"]["git_blob_sha1"] = "0" * 40
        probes["zero-digest"] = json.dumps(zero_digest).encode()
        unsafe = copy.deepcopy(valid)
        unsafe["claim_boundary"] = "safe\u202eunsafe"
        probes["unsafe-control"] = json.dumps(unsafe).encode()
        for label, payload in probes.items():
            with self.subTest(label=label):
                path = self.root / f"{label}.json"
                path.write_bytes(payload)
                with self.assertRaises(ValueError):
                    consent_catalog.load_acquisition_receipt(path, records, now_utc=now_utc)

    def test_acquisition_receipt_rejects_future_utc_timestamp(self) -> None:
        project = Path(__file__).resolve().parents[1]
        records = consent_catalog.load_catalog(project / "data" / "consent-catalog" / "v1")
        source_path = project / "data" / "consent-catalog" / "RUFF_SOURCE_ACQUISITION_RECEIPT.json"
        receipt = json.loads(source_path.read_text(encoding="utf-8"))
        receipt["retrieved_at"] = "2026-08-11T01:00:01Z"
        mutated = self.root / "future.json"
        mutated.write_text(json.dumps(receipt), encoding="utf-8")
        now_utc = datetime(2026, 8, 11, 1, 0, 0, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "future"):
            consent_catalog.load_acquisition_receipt(mutated, records, now_utc=now_utc)
        with self.assertRaisesRegex(ValueError, "timezone-aware UTC"):
            consent_catalog.load_acquisition_receipt(
                mutated,
                records,
                now_utc=datetime(2026, 8, 11, 1, 0, 2),
            )

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
