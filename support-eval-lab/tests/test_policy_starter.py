from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from support_eval_lab import policy_starter


class PolicyStarterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]
        self.source = self.project / "policy-starter"
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.pack = self.root / "policy-starter"
        shutil.copytree(self.source, self.pack)
        self.pack_generation = 0

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def manifest(self) -> dict[str, object]:
        return json.loads((self.pack / "manifest.json").read_text(encoding="utf-8"))

    def write_manifest(self, value: object) -> None:
        (self.pack / "manifest.json").write_text(
            json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

    def reset_pack(self) -> None:
        self.pack_generation += 1
        self.pack = self.root / f"policy-starter-{self.pack_generation}"
        shutil.copytree(self.source, self.pack)

    def rebind_manifest_file(self, path: Path) -> None:
        manifest = self.manifest()
        item = next(item for item in manifest["inventory"] if item["path"] == path.name)
        item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.write_manifest(manifest)

    def test_repository_pack_and_sample_receipt_are_fresh_and_deterministic(self) -> None:
        first = policy_starter.validate_pack(self.source)
        second = policy_starter.validate_pack(self.source)
        self.assertEqual(first, second)
        self.assertEqual(first["result"], "structurally_valid_synthetic_pack")
        self.assertFalse(first["boundaries"]["activated"])
        self.assertEqual(
            first["canonical_binding"], "verifier_owned_checked_tree_sha256_constants"
        )
        sample = self.project / "samples" / "policy-starter-validation-receipt.json"
        self.assertEqual(sample.read_bytes(), (json.dumps(first, indent=2) + "\n").encode())
        self.assertNotIn(b"\r\n", sample.read_bytes())

    def test_receipt_labels_hashes_only_as_consistency_fingerprints(self) -> None:
        receipt = policy_starter.validate_pack(self.pack)
        self.assertEqual(
            receipt["manifest_sha256_label"],
            "recomputable_consistency_fingerprint_only",
        )
        self.assertTrue(
            all(
                item["sha256_label"] == "recomputable_consistency_fingerprint_only"
                for item in receipt["files"]
            )
        )
        for phrase in ("not signatures", "authentication", "authorization", "legal advice"):
            self.assertIn(phrase, receipt["claim_boundary"])
        self.assertIn("not signatures or an external trust anchor", receipt["claim_boundary"])

    def test_each_markdown_is_bound_independently_of_mutable_manifest(self) -> None:
        markdown_names = sorted(
            name for name in policy_starter.EXPECTED_CONTENT_SHA256 if name.endswith(".md")
        )
        self.assertEqual(len(markdown_names), 7)
        for name in markdown_names:
            with self.subTest(name=name):
                self.reset_pack()
                target = self.pack / name
                target.write_bytes(target.read_bytes() + b"\nmutated checked-tree content\n")
                self.rebind_manifest_file(target)
                with self.assertRaisesRegex(ValueError, "verifier-owned canonical"):
                    policy_starter.validate_pack(self.pack)

    def test_declaration_semantics_are_bound_beyond_manifest_digest(self) -> None:
        mutations = {
            "repository": "other/policy-starter",
            "observed_at": "2026-08-11",
            "enforcement": "request_changes",
            "dimension": "recommended",
        }
        for name, replacement in mutations.items():
            with self.subTest(name=name):
                self.reset_pack()
                declaration = self.pack / policy_starter.DECLARATION_NAME
                raw = json.loads(declaration.read_text(encoding="utf-8"))
                if name == "dimension":
                    raw["dimensions"]["human_review"] = replacement
                else:
                    raw[name] = replacement
                declaration.write_text(
                    json.dumps(raw, indent=2) + "\n", encoding="utf-8", newline="\n"
                )
                self.rebind_manifest_file(declaration)
                with self.assertRaisesRegex(ValueError, "verifier-owned canonical"):
                    policy_starter.validate_pack(self.pack)

    def test_consistent_contributing_source_id_and_manifest_rewrite_still_fails(self) -> None:
        contributing = self.pack / "CONTRIBUTING.md"
        contributing.write_bytes(contributing.read_bytes() + b"\nSynthetic mutation.\n")
        source_digest = hashlib.sha256(contributing.read_bytes()).hexdigest()
        declaration = self.pack / policy_starter.DECLARATION_NAME
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        raw["source_sha256"] = source_digest
        raw["declaration_id"] = policy_starter._derive_declaration_id(
            raw["repository"],
            raw["record_kind"],
            raw["commit_sha"],
            raw["policy_path"],
            source_digest,
        )
        rewritten = self.pack / f"{raw['declaration_id']}.json"
        declaration.unlink()
        rewritten.write_text(
            json.dumps(raw, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        manifest = self.manifest()
        for item in manifest["inventory"]:
            if item["path"] == "CONTRIBUTING.md":
                item["sha256"] = source_digest
            elif item["path"] == policy_starter.DECLARATION_NAME:
                item["path"] = rewritten.name
                item["sha256"] = hashlib.sha256(rewritten.read_bytes()).hexdigest()
        manifest["inventory"] = sorted(manifest["inventory"], key=lambda item: item["path"])
        self.write_manifest(manifest)
        with self.assertRaises(ValueError):
            policy_starter.validate_pack(self.pack)

    def test_declaration_id_is_derived_from_semantic_payload(self) -> None:
        declaration = self.pack / policy_starter.DECLARATION_NAME
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        self.assertEqual(
            raw["declaration_id"],
            policy_starter._derive_declaration_id(
                raw["repository"],
                raw["record_kind"],
                raw["commit_sha"],
                raw["policy_path"],
                raw["source_sha256"],
            ),
        )
        raw["declaration_id"] = "mpd-v1-" + "0" * 64
        with self.assertRaisesRegex(ValueError, "semantic payload"):
            policy_starter._validate_declaration(raw, raw["source_sha256"])

    def test_missing_unexpected_subdirectory_and_oversized_files_fail_closed(self) -> None:
        (self.pack / "README.md").unlink()
        with self.assertRaises(ValueError):
            policy_starter.validate_pack(self.pack)
        shutil.copy2(self.source / "README.md", self.pack / "README.md")
        (self.pack / "unexpected.txt").write_text("unexpected", encoding="utf-8")
        with self.assertRaises(ValueError):
            policy_starter.validate_pack(self.pack)
        (self.pack / "unexpected.txt").unlink()
        (self.pack / "nested").mkdir()
        with self.assertRaises(ValueError):
            policy_starter.validate_pack(self.pack)
        (self.pack / "nested").rmdir()
        (self.pack / "README.md").write_bytes(b"x" * (policy_starter.MAX_FILE_BYTES + 1))
        with self.assertRaises(ValueError):
            policy_starter.validate_pack(self.pack)

    def test_wrong_hash_and_non_reserved_declaration_fail_closed(self) -> None:
        (self.pack / "README.md").write_text("changed\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            policy_starter.validate_pack(self.pack)
        shutil.copy2(self.source / "README.md", self.pack / "README.md")
        declaration = self.pack / policy_starter.DECLARATION_NAME
        raw = json.loads(declaration.read_text(encoding="utf-8"))
        raw["repository"] = "real/project"
        declaration.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8", newline="\n")
        manifest = self.manifest()
        next(item for item in manifest["inventory"] if item["path"] == declaration.name)[
            "sha256"
        ] = hashlib.sha256(declaration.read_bytes()).hexdigest()
        self.write_manifest(manifest)
        with self.assertRaises(ValueError):
            policy_starter.validate_pack(self.pack)

    def test_duplicate_unknown_nonstandard_numeric_depth_and_controls_fail_closed(self) -> None:
        original = (self.pack / "manifest.json").read_text(encoding="utf-8")
        probes = (
            original.replace('"schema_version":', '"schema_version": "1", "schema_version":', 1),
            original.replace('"pack_id":', '"unknown": "x", "pack_id":', 1),
            original.replace('"schema_version": "1"', '"schema_version": NaN', 1),
            original.replace('"schema_version": "1"', '"schema_version": 1', 1),
            "[" * 20 + "]" * 20,
            original.replace("policy-starter-synthetic-v1", "policy-starter\u202e-synthetic-v1"),
        )
        for index, payload in enumerate(probes):
            with self.subTest(index=index):
                (self.pack / "manifest.json").write_text(payload, encoding="utf-8")
                with self.assertRaises(ValueError):
                    policy_starter.validate_pack(self.pack)

    def test_traversal_backslash_and_lookalike_or_relaxed_booleans_fail_closed(self) -> None:
        for field, value in (
            ("path", "../README.md"),
            ("path", "nested\\README.md"),
            ("boundary", "false"),
            ("boundary", True),
        ):
            with self.subTest(field=field, value=value):
                manifest = copy.deepcopy(json.loads((self.source / "manifest.json").read_text()))
                if field == "path":
                    manifest["inventory"][0]["path"] = value
                else:
                    manifest["boundaries"]["activated"] = value
                self.write_manifest(manifest)
                with self.assertRaises(ValueError):
                    policy_starter.validate_pack(self.pack)

    def test_symlink_fails_when_supported(self) -> None:
        target = self.pack / "README.md"
        target.unlink()
        try:
            target.symlink_to(self.source / "README.md")
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "non-files|non-link"):
            policy_starter.validate_pack(self.pack)

    def test_hardlink_alias_fails(self) -> None:
        target = self.pack / "README.md"
        target.unlink()
        os.link(self.source / "README.md", target)
        with self.assertRaisesRegex(ValueError, "hard-link"):
            policy_starter.validate_pack(self.pack)

    def test_module_has_no_network_model_or_subprocess_runtime(self) -> None:
        source = Path(policy_starter.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "import socket",
            "import subprocess",
            "import urllib",
            "import requests",
            "openai",
        ):
            self.assertNotIn(forbidden, source)

    def test_output_cannot_be_written_inside_pack(self) -> None:
        with self.assertRaisesRegex(ValueError, "inside"):
            policy_starter.main([str(self.pack), "--json-out", str(self.pack / "receipt.json")])


if __name__ == "__main__":
    unittest.main()
