from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from patch_cabinet import declaration_compatibility


class DeclarationCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]
        self.root = self.project / "interop/maintainer-policy-declaration/compatibility-v1"

    def copy_project(self, temporary: str) -> Path:
        project = Path(temporary) / "patch-cabinet"
        shutil.copytree(self.project / "interop", project / "interop")
        return project

    def test_prepared_artifacts_are_fresh_and_observations_unobserved(self) -> None:
        receipt = declaration_compatibility.run(self.project, True)
        self.assertEqual(receipt["result"], "closed_harness_prepared")
        self.assertEqual(set(receipt["hosted_observations"].values()), {"not_observed"})

    def test_contract_covers_each_vector_and_excludes_decoder_boundaries(self) -> None:
        expected = json.loads((self.root / "expected-results.json").read_text())
        manifest = json.loads((self.root / "manifest.json").read_text())
        by_id = {item["id"]: item for item in expected["vectors"]}
        self.assertFalse(by_id["invalid-duplicate-key"]["structural_agreement_denominator"])
        self.assertFalse(by_id["invalid-nonstandard-number"]["structural_agreement_denominator"])
        self.assertTrue(by_id["format-deliberately-ignored"]["structural_agreement_denominator"])
        self.assertEqual(by_id["notes-boundary-501-reject"]["schema"], "reject")
        counterexample = by_id["same-key-distinct-nested-objects"]
        self.assertEqual(
            (counterexample["parse"], counterexample["schema"], counterexample["structural_agreement_denominator"]),
            ("accept", "reject", True),
        )
        supplemental = json.loads((self.root / "supplemental-corpus.json").read_text())
        vector = next(
            item for item in supplemental["vectors"]
            if item["id"] == "same-key-distinct-nested-objects"
        )
        self.assertEqual(
            [operation["value"]["id"] for operation in vector["operations"]],
            ["a", "b"],
        )
        bound = manifest["bindings"]["vector_contracts"]
        self.assertEqual([item["id"] for item in bound], [item["id"] for item in expected["vectors"]])
        self.assertTrue(all(len(item["raw_payload_sha256"]) == 64 for item in bound))

    def test_unknown_reference_and_duplicate_expected_id_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            schema_path = project / "interop/maintainer-policy-declaration/v1/schema.json"
            schema = json.loads(schema_path.read_text())
            schema["properties"]["dimensions"]["properties"]["ai_assisted_code"]["$ref"] = "https://example.invalid/schema"
            schema_path.write_text(json.dumps(schema))
            binding_path = project / "interop/maintainer-policy-declaration/compatibility-v1/base-corpus-binding.json"
            binding = json.loads(binding_path.read_text())
            import hashlib
            binding["schema"]["sha256"] = hashlib.sha256(schema_path.read_bytes()).hexdigest()
            binding_path.write_text(json.dumps(binding))
            with self.assertRaisesRegex(ValueError, "binding|reference"):
                declaration_compatibility.build(project)
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            path = project / "interop/maintainer-policy-declaration/compatibility-v1/expected-results.json"
            data = json.loads(path.read_text())
            data["vectors"][1]["id"] = data["vectors"][0]["id"]
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "cover"):
                declaration_compatibility.build(project)

    def test_validator_configurations_and_fixed_paths_are_verifier_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            path = project / "interop/maintainer-policy-declaration/compatibility-v1/expected-results.json"
            data = json.loads(path.read_text())
            data["validator_configurations"]["node_ajv_8_20_0"]["strict"] = False
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "validator configurations"):
                declaration_compatibility.build(project)
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            path = project / "interop/maintainer-policy-declaration/compatibility-v1/base-corpus-binding.json"
            data = json.loads(path.read_text())
            data["schema"]["path"] = "elsewhere/schema.json"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "base binding"):
                declaration_compatibility.build(project)

    def test_locks_and_runner_configurations_are_closed(self) -> None:
        requirements = (self.root / "requirements.lock").read_text().splitlines()
        self.assertEqual(len(requirements), 5)
        self.assertTrue(all("==" in line and " --hash=sha256:" in line for line in requirements))
        lock = json.loads((self.root / "package-lock.json").read_text())
        packages = lock["packages"]
        self.assertEqual(packages["node_modules/ajv"]["version"], "8.20.0")
        for name, item in packages.items():
            if name:
                self.assertTrue(item["resolved"].startswith("https://registry.npmjs.org/"))
                self.assertTrue(item["integrity"].startswith("sha512-"))
        node = (self.root / "node_runner.mjs").read_text()
        python = (self.root / "python_runner.py").read_text()
        self.assertIn('from "ajv/dist/2020.js"', node)
        self.assertIn("validateFormats: false", node)
        self.assertIn("Draft202012Validator.check_schema", python)
        self.assertNotIn("FormatChecker", python)
        for source in (node, python):
            for field in (
                "manifest_sha256", "raw_payload_sha256", "observed_parse", "observed_schema",
                "expected_parse", "expected_schema", "structural_agreement_denominator",
            ):
                self.assertIn(field, source)
        self.assertNotIn("raw.matchAll", node)
        self.assertIn("duplicate key in JSON object", node)

    def test_each_hosted_job_preflights_the_closed_harness(self) -> None:
        workflow = (self.project.parent / ".github/workflows/schema-compatibility.yml").read_text()
        command = "python -B -m patch_cabinet.declaration_compatibility"
        self.assertEqual(workflow.count(command), 2)
        self.assertEqual(workflow.count("PYTHONPATH: patch-cabinet/src"), 2)
        self.assertEqual(workflow.count("actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97"), 2)
        self.assertLess(workflow.index(command), workflow.index("python -m pip install"))
        node_job = workflow.index("node-ajv:")
        self.assertLess(workflow.index(command, node_job), workflow.index("npm ci", node_job))


if __name__ == "__main__":
    unittest.main()
