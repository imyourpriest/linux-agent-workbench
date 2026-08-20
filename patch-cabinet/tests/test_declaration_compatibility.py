from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from patch_cabinet import (
    declaration_compatibility,
    declaration_compatibility_v2,
    maintainer_policy_declaration,
)


class DeclarationCompatibilityTests(unittest.TestCase):
    V1_BASELINE = {
        "base-corpus-binding.json": (472, "2fb480e9c62c5b08d02951d97ff2870287a19a226ff4382f3613796b2b24848b"),
        "expected-results.json": (4723, "b0a34e4101026be4daf4683ad6f319f15e1ad6dc9d3f95783d2c77912308c0b5"),
        "manifest.json": (13599, "9e016ab3a1c19c90434d838ded04ddde0cc440759f7ff10eb012ad4b541e69f6"),
        "node_runner.mjs": (8063, "8d4f7233905b6b640a65d536f6c52a19a7c79c78c45fedafa55246a2df808e04"),
        "package-lock.json": (1620, "58fffd062e7152bd07a1dfefb91082a1715126094e9d2321fd034a3a266cf543"),
        "package.json": (161, "144e118542bec9d8ccfd24800f733b0f487e1e2846223bc40fc2b8eac0913fab"),
        "prepared-receipt.json": (1282, "0ebfacfc5ef0a32201eb55f87305dfd9dbed2f4ad6ef8f9a3359a27f7aaf3cd1"),
        "python_runner.py": (6117, "182c674dc7fb0f583a316e9cef95136ebe9d354a6bc3efbd843b58b85576d777"),
        "README.md": (1574, "2b19da00eac6f8b138d383ef185632d302b7c8abe2917fae259bb878e81f7ced"),
        "requirements.lock": (502, "05bae31857a05a9c7a8a2cd779caf2b54b2705e975a15d36dce8f1040dea12ae"),
        "supplemental-corpus.json": (5539, "2d92b036bf285269260f4dc222f77ca087a41fcf28a93823a66d76c82ad23e2c"),
    }

    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]
        self.root = self.project / "interop/maintainer-policy-declaration/compatibility-v1"
        self.v2_root = self.project / "interop/maintainer-policy-declaration/compatibility-v2"

    def copy_project(self, temporary: str) -> Path:
        project = Path(temporary) / "patch-cabinet"
        shutil.copytree(self.project / "interop", project / "interop")
        return project

    def test_prepared_artifacts_are_fresh_and_observations_unobserved(self) -> None:
        receipt = declaration_compatibility.run(self.project, True)
        self.assertEqual(receipt["result"], "closed_harness_prepared")
        self.assertEqual(set(receipt["hosted_observations"].values()), {"not_observed"})

    def test_v1_bytes_match_the_published_baseline(self) -> None:
        actual = {}
        for path in sorted(self.root.iterdir(), key=lambda item: item.name):
            self.assertTrue(path.is_file())
            payload = path.read_bytes()
            actual[path.name] = (len(payload), hashlib.sha256(payload).hexdigest())
        self.assertEqual(actual, self.V1_BASELINE)

    def test_v2_prepared_artifacts_are_fresh_and_observations_unobserved(self) -> None:
        receipt = declaration_compatibility_v2.run(self.project, True)
        self.assertEqual(receipt["result"], "closed_harness_prepared")
        self.assertEqual(set(receipt["hosted_observations"].values()), {"not_observed"})
        manifest = json.loads((self.v2_root / "manifest.json").read_text())
        self.assertEqual(
            manifest["component"],
            {"name": "maintainer-policy-declaration-compatibility", "version": "2"},
        )

    def test_v2_preserves_the_v1_schema_corpus_and_result_semantics(self) -> None:
        for name in (
            "base-corpus-binding.json",
            "supplemental-corpus.json",
            "expected-results.json",
            "requirements.lock",
        ):
            self.assertEqual((self.v2_root / name).read_bytes(), (self.root / name).read_bytes())

    def test_v2_node_dependency_tuple_and_inventory_are_exact(self) -> None:
        lock = json.loads((self.v2_root / "package-lock.json").read_text())
        self.assertEqual(
            lock["packages"]["node_modules/ajv"]["version"],
            "8.20.0",
        )
        self.assertEqual(
            lock["packages"]["node_modules/fast-uri"],
            {
                "version": "3.1.5",
                "resolved": "https://registry.npmjs.org/fast-uri/-/fast-uri-3.1.5.tgz",
                "integrity": "sha512-gHwA1O9LDIcKunMKhObS/HimwtehO1nPUECKAu5TpKgaO19fcWEl4bliWe1jWxVFvIXztJjjQ4L8XQ1EU9f7Jw==",
            },
        )
        evidence = json.loads((self.v2_root / "node-dependency-evidence.json").read_text())
        self.assertEqual(evidence, declaration_compatibility_v2.EXPECTED_NODE_DEPENDENCY_EVIDENCE)
        self.assertEqual(evidence["registry_shasum"], "610f37419a030270430cecd68d74e3d4d96725d0")
        self.assertEqual(evidence["license"], "BSD-3-Clause")
        self.assertEqual(
            evidence["registry_metadata_source"],
            "https://registry.npmjs.org/fast-uri/3.1.5",
        )
        self.assertEqual(evidence["observed_at"], "2026-08-20")
        self.assertFalse(evidence["install_script_observed"])
        self.assertFalse(evidence["engines_field_observed"])
        node = (self.v2_root / "node_runner.mjs").read_text()
        matches = re.findall(r"^const required = (\{[^\r\n]+\});$", node, re.MULTILINE)
        self.assertEqual(len(matches), 1)
        required = json.loads(matches[0])
        lock_inventory = {
            name.removeprefix("node_modules/"): item["version"]
            for name, item in lock["packages"].items()
            if name
        }
        self.assertEqual(required, lock_inventory)
        guard = node.index("const required = ")
        dynamic_import = node.index('await import("ajv/dist/2020.js")')
        construction = node.index("new Ajv2020(")
        self.assertLess(guard, dynamic_import)
        self.assertLess(dynamic_import, construction)
        self.assertNotIn('import Ajv2020 from "ajv/dist/2020.js"', node)

    def test_v2_dependency_tampering_fails_closed(self) -> None:
        mutations = (
            ("ajv resolved", "node_modules/ajv", "resolved", "https://registry.npmjs.org/ajv/-/ajv-other.tgz"),
            ("ajv integrity", "node_modules/ajv", "integrity", "sha512-tampered"),
            (
                "ajv dependency map",
                "node_modules/ajv",
                "dependencies",
                {"fast-deep-equal": "^3.1.3", "fast-uri": "^3.0.2", "json-schema-traverse": "^1.0.0", "require-from-string": "^2.0.2"},
            ),
            ("fast-deep-equal", "node_modules/fast-deep-equal", "version", "3.1.2"),
            ("fast-uri", "node_modules/fast-uri", "version", "3.1.4"),
            ("json-schema-traverse", "node_modules/json-schema-traverse", "version", "1.0.1"),
            ("require-from-string", "node_modules/require-from-string", "version", "2.0.1"),
        )
        for label, package, field, replacement in mutations:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                project = self.copy_project(temporary)
                path = project / "interop/maintainer-policy-declaration/compatibility-v2/package-lock.json"
                lock = json.loads(path.read_text())
                lock["packages"][package][field] = replacement
                path.write_text(json.dumps(lock))
                with self.assertRaisesRegex(ValueError, "exact v1-derived successor"):
                    declaration_compatibility_v2.build(project)

    def test_v2_runner_tampering_and_decoys_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            path = project / "interop/maintainer-policy-declaration/compatibility-v2/node_runner.mjs"
            payload = path.read_bytes()
            old = b'"fast-uri":"3.1.5"'
            self.assertEqual(payload.count(old), 1)
            payload = payload.replace(old, b'"fast-uri":"3.1.4"', 1)
            payload += b'// decoy only: "fast-uri":"3.1.5"\n'
            path.write_bytes(payload)
            with self.assertRaisesRegex(ValueError, "Node runner differs"):
                declaration_compatibility_v2.build(project)
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            path = project / "interop/maintainer-policy-declaration/compatibility-v2/python_runner.py"
            payload = path.read_bytes()
            self.assertEqual(payload.count(b'"compatibility-v2"'), 1)
            path.write_bytes(payload.replace(b'"compatibility-v2"', b'"compatibility-v3"', 1))
            with self.assertRaisesRegex(ValueError, "Python runner differs"):
                declaration_compatibility_v2.build(project)

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

    def test_dot_segment_structural_accept_is_exact_and_bound(self) -> None:
        identifier = "policy-path-dot-segment-structural-accept"
        obsolete = "policy-path-pattern-reject"
        supplemental = json.loads((self.root / "supplemental-corpus.json").read_text())
        expected = json.loads((self.root / "expected-results.json").read_text())
        manifest = json.loads((self.root / "manifest.json").read_text())
        vector = next(item for item in supplemental["vectors"] if item["id"] == identifier)
        self.assertEqual(
            vector["operations"],
            [
                {"op": "set", "pointer": "/policy_path", "value": "../POLICY.md"},
                {
                    "op": "set",
                    "pointer": "/policy_source_url",
                    "value": "https://example.invalid/synthetic/maintainer-policy-declaration-demo/blob/0123456789abcdef0123456789abcdef01234567/../POLICY.md",
                },
                {
                    "op": "set",
                    "pointer": "/declaration_id",
                    "value": "mpd-v1-210fdb5e9a2767e702e231035be4bf447d93eb6b2d93cb9a16c04729ba831f36",
                },
            ],
        )
        expected_by_id = {item["id"]: item for item in expected["vectors"]}
        self.assertEqual(
            expected_by_id[identifier],
            {
                "id": identifier,
                "parse": "accept",
                "schema": "accept",
                "structural_agreement_denominator": True,
            },
        )
        self.assertNotIn(obsolete, {item["id"] for item in supplemental["vectors"]})
        self.assertNotIn(obsolete, expected_by_id)
        payload = copy.deepcopy(supplemental["base_payload"])
        for operation in vector["operations"]:
            payload[operation["pointer"][1:]] = operation["value"]
        expected_source_url = (
            f"https://example.invalid/{payload['repository']}/blob/"
            f"{payload['commit_sha']}/{payload['policy_path']}"
        )
        self.assertEqual(payload["policy_source_url"], expected_source_url)
        identity = "\0".join(
            (
                "mpd-v1",
                payload["repository"].casefold(),
                payload["record_kind"],
                payload["commit_sha"],
                payload["policy_path"],
                payload["source_sha256"],
            )
        )
        expected_declaration_id = f"mpd-v1-{hashlib.sha256(identity.encode('utf-8')).hexdigest()}"
        self.assertEqual(payload["declaration_id"], expected_declaration_id)
        with self.assertRaisesRegex(
            ValueError, "policy_path must be a canonical ASCII repository-relative path"
        ):
            maintainer_policy_declaration._parse_declaration(payload)
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        bound_by_id = {
            item["id"]: item for item in manifest["bindings"]["vector_contracts"]
        }
        self.assertEqual(
            bound_by_id[identifier],
            {
                "id": identifier,
                "raw_payload_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                "parse_expected": "accept",
                "schema_expected": "accept",
                "structural_agreement_denominator": True,
            },
        )

    def test_unknown_reference_and_duplicate_expected_id_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            schema_path = project / "interop/maintainer-policy-declaration/v1/schema.json"
            schema = json.loads(schema_path.read_text())
            schema["properties"]["dimensions"]["properties"]["ai_assisted_code"]["$ref"] = "https://example.invalid/schema"
            schema_path.write_text(json.dumps(schema))
            binding_path = project / "interop/maintainer-policy-declaration/compatibility-v1/base-corpus-binding.json"
            binding = json.loads(binding_path.read_text())
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
        workflow_bytes = (
            self.project.parent / ".github/workflows/schema-compatibility.yml"
        ).read_bytes()
        self.assertEqual(
            hashlib.sha256(workflow_bytes).hexdigest(),
            "0f3c3d1cef5481e8dc23295c84efad6f5c4f2db84926e07705e82a475767d802",
        )
        workflow = workflow_bytes.decode("utf-8", errors="strict")
        trigger = workflow[workflow.index("on:\n"):workflow.index("\npermissions:")]
        self.assertEqual(trigger, "on:\n  pull_request:\n  push:\n    branches: [main]\n")
        python_header = (
            "\n  python-jsonschema:\n"
            "    name: Python jsonschema 4.26.0 structural compatibility\n"
        )
        node_header = (
            "\n  node-ajv:\n"
            "    name: Node Ajv 8.20.0 structural compatibility\n"
        )
        self.assertEqual(workflow.count(python_header), 1)
        self.assertEqual(workflow.count(node_header), 1)
        command = (
            "python -B patch-cabinet/src/patch_cabinet/declaration_compatibility_v2.py\n"
            "          --project patch-cabinet\n"
            "          --check"
        )
        self.assertEqual(workflow.count(command), 2)
        self.assertNotIn("-m patch_cabinet.declaration_compatibility", workflow)
        self.assertNotIn("PYTHONPATH", workflow)
        self.assertNotIn("compatibility-v1", workflow)
        for path in (
            "compatibility-v2/requirements.lock",
            "compatibility-v2/python_runner.py",
            "compatibility-v2/package-lock.json",
            "compatibility-v2/node_runner.mjs",
        ):
            self.assertEqual(workflow.count(path), 1)
        setup_python = "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97"
        self.assertEqual(workflow.count(setup_python), 2)
        python_job = workflow[workflow.index("python-jsonschema:"):workflow.index("node-ajv:")]
        node_job = workflow[workflow.index("node-ajv:"):]
        self.assertEqual(python_job.count(setup_python), 1)
        self.assertEqual(node_job.count(setup_python), 1)
        self.assertEqual(python_job.count(command), 1)
        self.assertLess(python_job.index(command), python_job.index("python -m pip install"))
        self.assertEqual(node_job.count(command), 1)
        self.assertLess(node_job.index(command), node_job.index("npm ci"))

    def test_ci_retains_v1_and_adds_independent_v2_freshness_routes(self) -> None:
        workflow = (self.project.parent / ".github/workflows/ci.yml").read_text()
        v1 = "python -m patch_cabinet.declaration_compatibility --project . --check"
        v2 = "python -m patch_cabinet.declaration_compatibility_v2 --project . --check"
        projection = "python -m patch_cabinet.declaration_projection --project . --check"
        self.assertEqual(workflow.count(v1), 1)
        self.assertEqual(workflow.count(v2), 1)
        self.assertLess(workflow.index(v1), workflow.index(v2))
        self.assertLess(workflow.index(v2), workflow.index(projection))


if __name__ == "__main__":
    unittest.main()
