from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from patch_cabinet import declaration_interop


class DeclarationInteropTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]
        self.root = self.project / "interop" / "maintainer-policy-declaration" / "v1"

    def copied_project(self, temporary: str) -> Path:
        project = Path(temporary) / "patch-cabinet"
        shutil.copytree(self.root, project / "interop" / "maintainer-policy-declaration" / "v1")
        return project

    def test_checked_artifacts_are_fresh_and_deterministic(self) -> None:
        first = declaration_interop.run(self.project, True)
        second = declaration_interop.run(self.project, True)
        self.assertEqual(first, second)
        self.assertEqual(first["result"], "corpus_matches_authoritative_parser_expectations")
        self.assertFalse(first["independent_json_schema_validator_tested"])

    def test_profile_identifies_draft_2020_12_without_claiming_semantics(self) -> None:
        schema = json.loads((self.root / "schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(
            declaration_interop.run(self.project, True)["independent_json_schema_validator_tested"]
        )
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        boundaries = ("duplicate keys", "byte", "canonical ID", "authority", "current permission")
        for boundary in boundaries:
            self.assertIn(boundary, readme)

    def test_valid_invalid_and_ambiguous_vectors_are_exercised(self) -> None:
        receipt = declaration_interop.run(self.project, True)
        by_id = {item["id"]: item for item in receipt["vectors"]}
        self.assertEqual(by_id["valid-reserved-synthetic"]["strict_parser_observed"], "accept")
        self.assertEqual(by_id["invalid-missing-notes"]["strict_parser_observed"], "reject")
        self.assertEqual(by_id["ambiguous-derived-id"]["classification"], "ambiguous")
        self.assertEqual(by_id["ambiguous-derived-id"]["strict_parser_observed"], "reject")
        self.assertEqual(by_id["invalid-duplicate-key"]["strict_parser_observed"], "reject")

    def test_projection_preserves_unknowns_and_is_non_authorizing(self) -> None:
        policy = (self.root / "AI_POLICY.draft.md").read_text(encoding="utf-8")
        fragment = (self.root / "PULL_REQUEST_TEMPLATE.fragment.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(policy.count("`not_declared`"), 14)
        self.assertIn("`conditional`", policy)
        self.assertIn("Non-authorizing lossy projection", policy)
        self.assertIn("including unknowns", fragment)
        self.assertIn("makes no statement about whether they are required", fragment)
        self.assertNotIn("does not require", fragment.casefold())
        self.assertNotIn("- [ ]", fragment)
        self.assertNotIn("ruleset", fragment.casefold())
        fragment_bytes = (
            self.root / "PULL_REQUEST_TEMPLATE.fragment.md"
        ).read_bytes()
        self.assertTrue(fragment_bytes.endswith(b"\n"))
        self.assertFalse(fragment_bytes.endswith(b"\n\n"))

    def test_mutated_expectation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            corpus_path = (
                project / "interop" / "maintainer-policy-declaration" / "v1" / "corpus.json"
            )
            corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
            corpus["vectors"][0]["strict_parser_expectation"] = "reject"
            corpus_path.write_text(
                json.dumps(corpus, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "strict parser result differs"):
                declaration_interop.run(project, False)

    def test_accepted_projection_vector_cannot_be_reclassified(self) -> None:
        for classification in ("invalid", "ambiguous"):
            with self.subTest(classification=classification), tempfile.TemporaryDirectory() as temp:
                project = self.copied_project(temp)
                corpus_path = (
                    project / "interop" / "maintainer-policy-declaration" / "v1" / "corpus.json"
                )
                corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
                corpus["vectors"][0]["classification"] = classification
                corpus_path.write_text(
                    json.dumps(corpus, indent=2) + "\n", encoding="utf-8", newline="\n"
                )
                with self.assertRaisesRegex(ValueError, "tuple differs"):
                    declaration_interop.run(project, False)

    def test_mismatched_classification_expectation_tuple_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            corpus_path = (
                project / "interop" / "maintainer-policy-declaration" / "v1" / "corpus.json"
            )
            corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
            corpus["vectors"][1]["structural_profile_expectation"] = "accept"
            corpus_path.write_text(
                json.dumps(corpus, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            with self.assertRaisesRegex(ValueError, "tuple differs"):
                declaration_interop.run(project, False)

    def test_iterative_structure_walker_rejects_deep_byte_bounded_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            schema_path = (
                project / "interop" / "maintainer-policy-declaration" / "v1" / "schema.json"
            )
            deep: object = "leaf"
            for _ in range(declaration_interop.MAX_STRUCTURE_DEPTH + 2):
                deep = [deep]
            schema_path.write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "deep": deep,
                    }
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            self.assertLess(schema_path.stat().st_size, declaration_interop.MAX_FILE_BYTES)
            with self.assertRaisesRegex(ValueError, "depth limit"):
                declaration_interop.run(project, False)

    def test_duplicate_corpus_key_and_stale_output_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "interop" / "maintainer-policy-declaration" / "v1"
            corpus = root / "corpus.json"
            corpus.write_text(corpus.read_text().replace("{", '{"schema_version":"1",', 1))
            with self.assertRaisesRegex(ValueError, "strict JSON"):
                declaration_interop.run(project, False)
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            output = (
                project
                / "interop"
                / "maintainer-policy-declaration"
                / "v1"
                / "AI_POLICY.draft.md"
            )
            output.write_text("stale\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stale"):
                declaration_interop.run(project, True)

    def test_hardlinked_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "interop" / "maintainer-policy-declaration" / "v1"
            schema = root / "schema.json"
            victim = Path(temporary) / "schema-victim.json"
            victim.write_bytes(schema.read_bytes())
            schema.unlink()
            os.link(victim, schema)
            try:
                with self.assertRaisesRegex(ValueError, "single-link"):
                    declaration_interop.run(project, False)
            finally:
                schema.unlink(missing_ok=True)

    def test_unexpected_inventory_and_output_alias_fail_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "interop" / "maintainer-policy-declaration" / "v1"
            (root / "extra.txt").write_text("extra", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inventory"):
                declaration_interop.run(project, False)
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copied_project(temporary)
            root = project / "interop" / "maintainer-policy-declaration" / "v1"
            first = root / "AI_POLICY.draft.md"
            before = first.read_bytes()
            output = root / "validation-receipt.json"
            victim = Path(temporary) / "victim"
            output.unlink()
            victim.write_bytes(b"victim")
            os.link(victim, output)
            with self.assertRaisesRegex(ValueError, "single-link"):
                declaration_interop.run(project, False)
            self.assertEqual(first.read_bytes(), before)
            self.assertEqual(victim.read_bytes(), b"victim")

    def test_module_has_no_network_subprocess_or_platform_write_path(self) -> None:
        source = Path(declaration_interop.__file__).read_text(encoding="utf-8")
        forbidden_source = (
            "import socket", "import urllib", "import requests", "subprocess", "ruleset"
        )
        for forbidden in forbidden_source:
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
