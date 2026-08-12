from __future__ import annotations

import copy
import hashlib
import html
import json
import os
import re
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

from patch_cabinet import maintainer_policy_declaration as declaration


class MaintainerPolicyDeclarationTests(unittest.TestCase):
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
        observed: str = "2026-08-10",
        supersedes: str | None = None,
        kind: str = "unverified_project_declaration",
    ) -> dict[str, object]:
        policy_path = "CONTRIBUTING.md"
        record_id = declaration.expected_declaration_id(
            repository, kind, commit, policy_path, digest
        )
        host = "example.invalid" if kind == "synthetic_example" else "github.com"
        return {
            "schema_version": "1",
            "declaration_id": record_id,
            "record_kind": kind,
            "assertion_basis": declaration.RECORD_BASES[kind],
            "repository": repository,
            "repository_url": f"https://{host}/{repository}",
            "commit_sha": commit,
            "policy_source_url": (
                f"https://{host}/{repository}/blob/{commit}/{policy_path}"
            ),
            "policy_path": policy_path,
            "source_sha256": digest,
            "observed_at": observed,
            "dimensions": {
                name: "not_declared" for name in declaration.DIMENSION_VOCABULARIES
            },
            "disclosure_location": "not_declared",
            "enforcement": "not_declared",
            "supersedes": supersedes,
            "notes": "Trusted-local declaration supplied for structural testing only.",
        }

    def _write(
        self,
        value: dict[str, object],
        *,
        filename: str | None = None,
        text: str | None = None,
    ) -> Path:
        target = self.records / (filename or f"{value['declaration_id']}.json")
        target.write_text(
            text if text is not None else json.dumps(value, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return target

    def test_valid_record_builds_deterministic_structural_index(self) -> None:
        self._write(self._record())
        loaded = declaration.load_declarations(self.records)
        first = declaration.build_index(loaded)
        second = declaration.build_index(loaded)
        self.assertEqual(first, second)
        self.assertEqual(first["component"]["version"], "0.2.0")
        self.assertIn("Structural validation only", first["claim_boundary"])
        self.assertIn("does not verify", first["claim_boundary"])
        forbidden = {"eligible", "ready", "authorized", "candidate", "scoring"}

        def keys(value: object) -> set[str]:
            if type(value) is dict:
                return set(value) | {item for child in value.values() for item in keys(child)}
            if type(value) is list:
                return {item for child in value for item in keys(child)}
            return set()

        self.assertTrue(forbidden.isdisjoint(keys(first)))

    def test_repository_fixture_is_unmistakably_synthetic(self) -> None:
        project = Path(__file__).resolve().parents[1]
        record_dir = project / "data" / "maintainer-policy-declarations" / "synthetic" / "v1"
        loaded = declaration.load_declarations(record_dir)
        self.assertEqual(len(loaded), 1)
        record = loaded[0]
        self.assertEqual(record.record_kind, "synthetic_example")
        self.assertIn("reserved synthetic namespace", record.notes.casefold())
        self.assertTrue(all(value == "not_declared" for value in record.dimensions.values()))
        report = declaration.build_index(loaded)
        self.assertEqual(
            (project / "samples" / "maintainer-policy-declaration-index.json").read_bytes(),
            (json.dumps(report, indent=2) + "\n").encode(),
        )

        self.assertEqual(
            (project / "samples" / "maintainer-policy-declaration-index.md").read_bytes(),
            declaration.render_markdown(report).encode(),
        )
        self.assertEqual(
            (project / "samples" / "maintainer-policy-declaration-starter.json").read_bytes(),
            declaration.render_starter("unverified_project_declaration").encode(),
        )
        record_path = next(record_dir.glob("*.json"))
        self.assertEqual(
            (
                project / "samples" / "maintainer-policy-declaration-validation-receipt.json"
            ).read_bytes(),
            (
                json.dumps(declaration.build_validation_receipt(record_path), indent=2) + "\n"
            ).encode(),
        )

    def test_documented_component_version_matches_runtime(self) -> None:
        project = Path(__file__).resolve().parents[1]
        documentation = (project / "MAINTAINER_POLICY_DECLARATION.md").read_text(
            encoding="utf-8"
        )
        match = re.search(
            r"Component `maintainer-policy-declaration` version `([^`]+)`, schema `1`\.",
            documentation,
        )
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), declaration.COMPONENT_VERSION)

    def test_record_kind_and_assertion_basis_must_pair(self) -> None:
        for kind, basis in declaration.RECORD_BASES.items():
            with self.subTest(kind=kind):
                record = self._record(kind=kind)
                self.assertEqual(declaration._parse_declaration(record).assertion_basis, basis)
                record["assertion_basis"] = next(
                    value for value in declaration.RECORD_BASES.values() if value != basis
                )
                with self.assertRaisesRegex(ValueError, "does not match"):
                    declaration._parse_declaration(record)
        record = self._record()
        record["record_kind"] = "maintainer_verified"
        with self.assertRaises(ValueError):
            declaration._parse_declaration(record)

    def test_identity_uses_complete_canonical_fields_without_slug_collisions(self) -> None:
        common = ("unverified_project_declaration", "a" * 40, "CONTRIBUTING.md", "b" * 64)
        dotted = declaration.expected_declaration_id("owner/foo.bar", *common)
        dashed = declaration.expected_declaration_id("owner/foo-bar", *common)
        self.assertNotEqual(dotted, dashed)
        self.assertRegex(dotted, declaration.DECLARATION_ID)
        maximum = f"{'o' * 39}/{'r' * 100}"
        record = self._record(repository=maximum)
        self.assertRegex(record["declaration_id"], declaration.DECLARATION_ID)
        declaration._parse_declaration(record)
        invalid = self._record(repository="owner--name/project")
        with self.assertRaisesRegex(ValueError, "GitHub owner/name limits"):
            declaration._parse_declaration(invalid)

    def test_record_kinds_have_separate_provenance_namespaces(self) -> None:
        synthetic = self._record(kind="synthetic_example")
        declaration._parse_declaration(synthetic)
        synthetic["repository_url"] = "https://github.com/owner/project"
        synthetic["policy_source_url"] = (
            f"https://github.com/owner/project/blob/{synthetic['commit_sha']}/CONTRIBUTING.md"
        )
        with self.assertRaisesRegex(ValueError, "record-kind-specific"):
            declaration._parse_declaration(synthetic)
        project = self._record()
        project["repository_url"] = "https://example.invalid/owner/project"
        project["policy_source_url"] = (
            f"https://example.invalid/owner/project/blob/{project['commit_sha']}/CONTRIBUTING.md"
        )
        with self.assertRaisesRegex(ValueError, "record-kind-specific"):
            declaration._parse_declaration(project)

    def test_all_controlled_vocabularies_are_accepted_and_closed(self) -> None:
        for name, vocabulary in declaration.DIMENSION_VOCABULARIES.items():
            for value in vocabulary:
                with self.subTest(dimension=name, value=value):
                    record = self._record()
                    record["dimensions"][name] = value
                    if name == "disclosure" and value != "not_declared":
                        record["disclosure_location"] = "project_defined"
                    declaration._parse_declaration(record)
            record = self._record()
            record["dimensions"][name] = "unknown"
            with self.assertRaises(ValueError):
                declaration._parse_declaration(record)
        for value in declaration.DISCLOSURE_LOCATIONS - {"not_declared"}:
            record = self._record()
            record["dimensions"]["disclosure"] = "recommended"
            record["disclosure_location"] = value
            declaration._parse_declaration(record)
        for value in declaration.ENFORCEMENT_VALUES:
            record = self._record()
            record["enforcement"] = value
            declaration._parse_declaration(record)

    def test_disclosure_and_location_must_be_declared_together(self) -> None:
        first = self._record()
        first["dimensions"]["disclosure"] = "required"
        with self.assertRaisesRegex(ValueError, "declared together"):
            declaration._parse_declaration(first)
        second = self._record()
        second["disclosure_location"] = "pr_description"
        with self.assertRaisesRegex(ValueError, "declared together"):
            declaration._parse_declaration(second)

    def test_provenance_identity_fields_and_dates_fail_closed(self) -> None:
        transformations = {
            "unknown": lambda value: value.update({"extra": "x"}),
            "id": lambda value: value.update({"declaration_id": "mpd-v1-" + "0" * 64}),
            "repository-url": lambda value: value.update(
                {"repository_url": "https://github.com/other/project"}
            ),
            "source-url": lambda value: value.update(
                {
                    "policy_source_url": (
                        "https://github.com/other/project/blob/" + "a" * 40 + "/CONTRIBUTING.md"
                    )
                }
            ),
            "branch-url": lambda value: value.update(
                {"policy_source_url": "https://github.com/owner/project/blob/main/CONTRIBUTING.md"}
            ),
            "path": lambda value: value.update({"policy_path": "../POLICY.md"}),
            "null-digest": lambda value: value.update({"source_sha256": "0" * 64}),
            "uppercase-commit": lambda value: value.update({"commit_sha": "A" * 40}),
            "future": lambda value: value.update({"observed_at": "2999-01-01"}),
            "bidi": lambda value: value.update({"notes": "safe\u202eunsafe"}),
        }
        for label, transform in transformations.items():
            with self.subTest(label=label):
                value = self._record()
                transform(value)
                with self.assertRaises(ValueError):
                    declaration._parse_declaration(value)

    def test_strict_json_rejects_duplicates_constants_numbers_depth_bom_and_size(self) -> None:
        valid = json.dumps(self._record())
        probes = {
            "duplicate": valid.replace('"notes":', '"notes": "first", "notes":', 1),
            "constant": valid.replace('"supersedes": null', '"supersedes": NaN'),
            "integer": valid.replace('"schema_version": "1"', '"schema_version": 1'),
            "float": valid.replace('"schema_version": "1"', '"schema_version": 1.0'),
            "deep": "[" * 20 + "]" * 20,
            "bom": "\ufeff" + valid,
            "oversize": " " * (declaration.MAX_FILE_BYTES + 1),
        }
        for label, text in probes.items():
            with self.subTest(label=label):
                for existing in self.records.iterdir():
                    existing.unlink()
                self._write(self._record(), filename="probe.json", text=text)
                with self.assertRaises(ValueError):
                    declaration.load_declarations(self.records)

    def test_filename_inventory_count_and_subdirectories_are_strict(self) -> None:
        self._write(self._record(), filename="wrong.json")
        with self.assertRaisesRegex(ValueError, "filename"):
            declaration.load_declarations(self.records)
        for existing in self.records.iterdir():
            existing.unlink()
        (self.records / "README.md").write_text("not JSON", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "only .json"):
            declaration.load_declarations(self.records)
        (self.records / "README.md").unlink()
        (self.records / "nested").mkdir()
        with self.assertRaisesRegex(ValueError, "regular JSON"):
            declaration.load_declarations(self.records)
        (self.records / "nested").rmdir()
        for index in range(declaration.MAX_RECORDS + 1):
            (self.records / f"{index:03}.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "record limit"):
            declaration.load_declarations(self.records)

    def test_file_and_directory_links_are_rejected_when_supported(self) -> None:
        outside = self.root / "outside.json"
        outside.write_text(json.dumps(self._record()), encoding="utf-8")
        link = self.records / "linked.json"
        try:
            link.symlink_to(outside)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "regular JSON"):
            declaration.load_declarations(self.records)
        linked_dir = self.root / "linked-records"
        try:
            linked_dir.symlink_to(self.records, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"directory symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "non-link regular directory"):
            declaration.load_declarations(linked_dir)

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junctioned_input_directory_is_rejected(self) -> None:
        outside = self.root / "outside-records"
        outside.mkdir()
        junction = self.root / "junction-records"
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
                declaration.load_declarations(junction)
        finally:
            os.rmdir(junction)

    def test_successors_require_later_single_same_lineage_chain(self) -> None:
        first = self._record(observed="2026-08-08")
        second = self._record(
            commit="c" * 40,
            digest="d" * 64,
            observed="2026-08-09",
            supersedes=first["declaration_id"],
        )
        self._write(first)
        self._write(second)
        self.assertEqual(len(declaration.load_declarations(self.records)), 2)
        second["supersedes"] = "mpd-v1-" + "1" * 64
        self._write(second)
        with self.assertRaisesRegex(ValueError, "different declaration"):
            declaration.load_declarations(self.records)
        second["supersedes"] = first["declaration_id"]
        second["observed_at"] = first["observed_at"]
        self._write(second)
        with self.assertRaisesRegex(ValueError, "later observation"):
            declaration.load_declarations(self.records)

        for existing in self.records.iterdir():
            existing.unlink()
        other = self._record(
            repository="other/project",
            commit="e" * 40,
            digest="f" * 64,
            observed="2026-08-09",
            supersedes=first["declaration_id"],
        )
        self._write(first)
        self._write(other)
        with self.assertRaisesRegex(ValueError, "lineage"):
            declaration.load_declarations(self.records)

    def test_successors_cannot_transition_between_record_kinds(self) -> None:
        for first_kind, second_kind in (
            ("synthetic_example", "unverified_project_declaration"),
            ("unverified_project_declaration", "synthetic_example"),
        ):
            with self.subTest(first=first_kind, second=second_kind):
                for existing in self.records.iterdir():
                    existing.unlink()
                first = self._record(kind=first_kind, observed="2026-08-08")
                second = self._record(
                    kind=second_kind,
                    commit="c" * 40,
                    digest="d" * 64,
                    observed="2026-08-09",
                    supersedes=first["declaration_id"],
                )
                self._write(first)
                self._write(second)
                with self.assertRaisesRegex(ValueError, "lineage"):
                    declaration.load_declarations(self.records)

    def test_fork_and_cycle_are_rejected(self) -> None:
        first = self._record(observed="2026-08-08")
        second = self._record(
            commit="c" * 40,
            digest="d" * 64,
            observed="2026-08-09",
            supersedes=first["declaration_id"],
        )
        third = self._record(
            commit="e" * 40,
            digest="f" * 64,
            observed="2026-08-10",
            supersedes=first["declaration_id"],
        )
        for item in (first, second, third):
            self._write(item)
        with self.assertRaisesRegex(ValueError, "multiple direct successors"):
            declaration.load_declarations(self.records)
        for existing in self.records.iterdir():
            existing.unlink()
        first["supersedes"] = second["declaration_id"]
        self._write(first)
        self._write(second)
        with self.assertRaisesRegex(ValueError, "later observation|cycle"):
            declaration.load_declarations(self.records)

    def test_notes_are_inert_and_only_source_link_is_active(self) -> None:
        record = self._record()
        note = "safe [link](https://evil.invalid) ![image](x) <script>"
        record["notes"] = note
        self._write(record)
        report = declaration.build_index(declaration.load_declarations(self.records))
        rendered = declaration.render_markdown(report)
        note_line = next(line for line in rendered.splitlines() if line.startswith("- Notes:"))
        self.assertNotIn("[link]", note_line)
        self.assertNotIn("https://evil.invalid", note_line)
        self.assertNotIn("<script>", note_line)
        encoded = note_line.split("<code>", 1)[1].split("</code>", 1)[0]
        self.assertEqual(html.unescape(encoded), note)
        self.assertEqual(rendered.count("[source](https://"), 1)
        synthetic = self._record(kind="synthetic_example")
        report = declaration.build_index([declaration._parse_declaration(synthetic)])
        rendered = declaration.render_markdown(report)
        self.assertNotIn("](https://", rendered)
        self.assertIn("Synthetic source:", rendered)

    def test_output_paths_reject_aliases_hardlinks_devices_and_input_directory(self) -> None:
        source = self._write(self._record())
        alias = self.root / "alias.json"
        try:
            os.link(source, alias)
        except OSError as error:
            self.skipTest(f"hard-link creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "aliases"):
            declaration.main(
                ["render", str(self.records), "--json-out", str(alias)]
            )
        with self.assertRaisesRegex(ValueError, "inside"):
            declaration.main(
                ["render", str(self.records), "--json-out", str(self.records / "index.json")]
            )
        directory_output = self.root / "output-directory"
        directory_output.mkdir()
        with self.assertRaisesRegex(ValueError, "regular file"):
            declaration.main(
                ["render", str(self.records), "--json-out", str(directory_output)]
            )
        first = self.root / "first.json"
        first.write_text("existing", encoding="utf-8")
        second = self.root / "second.md"
        os.link(first, second)
        with self.assertRaisesRegex(ValueError, "hardlink"):
            declaration.main(
                [
                    "render",
                    str(self.records),
                    "--json-out",
                    str(first),
                    "--markdown-out",
                    str(second),
                ]
            )

    def test_cli_outputs_and_starter_are_deterministic_lf_only(self) -> None:
        self._write(self._record())
        json_out = self.root / "index.json"
        markdown_out = self.root / "index.md"
        arguments = [
            "render",
            str(self.records),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
        declaration.main(arguments)
        first = (json_out.read_bytes(), markdown_out.read_bytes())
        declaration.main(arguments)
        second = (json_out.read_bytes(), markdown_out.read_bytes())
        self.assertEqual(first, second)
        self.assertNotIn(b"\r\n", first[0] + first[1])
        starter = declaration.render_starter("unverified_project_declaration")
        self.assertEqual(starter, declaration.render_starter("unverified_project_declaration"))
        self.assertNotIn("\r\n", starter)
        with self.assertRaises(SystemExit):
            declaration.main(["starter"])

    def test_one_record_receipt_reuses_payload_and_has_narrow_claims(self) -> None:
        source = self._write(self._record(kind="synthetic_example"))
        receipt = declaration.build_validation_receipt(source)
        item = receipt["declaration"]
        self.assertEqual(receipt["result"], "structurally_valid")
        self.assertEqual(
            item["record_file_sha256"], hashlib.sha256(source.read_bytes()).hexdigest()
        )
        self.assertEqual(item["record_file_sha256_label"], "recomputable_fingerprint_only")
        boundary = receipt["claim_boundary"]
        for excluded_claim in ("not a signature", "authentication", "authorization", "currentness"):
            self.assertIn(excluded_claim, boundary)
        self.assertEqual(receipt, declaration.build_validation_receipt(source))

    def test_validate_command_rejects_directory_link_and_malformed_record(self) -> None:
        source = self._write(self._record(kind="synthetic_example"))
        with self.assertRaises(ValueError):
            declaration.main(["validate", str(self.records)])
        malformed = self.root / "wrong.json"
        malformed.write_text('{"schema_version":"1","schema_version":"1"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            declaration.main(["validate", str(malformed)])
        linked = self.root / source.name
        try:
            linked.symlink_to(source)
        except OSError:
            return
        with self.assertRaisesRegex(ValueError, "nonsymlink"):
            declaration.main(["validate", str(linked)])

    def test_starter_is_explicitly_unvalidated_until_replaced(self) -> None:
        starter = declaration.starter_template("unverified_project_declaration")
        self.assertEqual(starter["record_kind"], "unverified_project_declaration")
        self.assertEqual(
            starter["assertion_basis"],
            declaration.RECORD_BASES["unverified_project_declaration"],
        )
        self.assertIn("not structurally validated", starter["notes"])
        self.assertTrue(any("<" in str(value) for value in starter.values()))
        with self.assertRaises(ValueError):
            declaration._parse_declaration(starter)

    def test_module_is_isolated_and_imports_no_network_or_process_client(self) -> None:
        source = Path(declaration.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "import subprocess",
            "import socket",
            "import urllib",
            "import requests",
            "from .policy",
            "from .engine",
            "from .cli",
        ):
            self.assertNotIn(forbidden, source)
        project = Path(declaration.__file__).resolve().parent
        for filename in ("policy.py", "engine.py", "cli.py", "__init__.py"):
            self.assertNotIn("maintainer_policy_declaration", (project / filename).read_text())


if __name__ == "__main__":
    unittest.main()
