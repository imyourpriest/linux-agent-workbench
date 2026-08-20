from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from patch_cabinet import declaration_projection


class DeclarationProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]

    def copy_project(self, temporary: str) -> Path:
        project = Path(temporary) / "patch-cabinet"
        root = project / "interop/maintainer-policy-declaration/projection-contract-v1"
        shutil.copytree(self.project / "interop/maintainer-policy-declaration/projection-contract-v1", root)
        source = project / declaration_projection.SOURCE
        source.parent.mkdir(parents=True)
        shutil.copy2(self.project / declaration_projection.SOURCE, source)
        return project

    def test_projection_is_fresh_field_complete_and_digest_bound(self) -> None:
        receipt = declaration_projection.run(self.project, True)
        self.assertEqual(receipt["result"], "field_complete_projection_prepared")
        root = self.project / "interop/maintainer-policy-declaration/projection-contract-v1"
        contract = json.loads((root / "projection-contract.json").read_text())
        pointers = [item["pointer"] for item in contract["mappings"]]
        self.assertEqual(len(pointers), len(set(pointers)))
        self.assertEqual(len(pointers), 16 + 13)
        self.assertEqual(set(contract["non_established_claims"]), {"identity","authority","currentness","permission","enforcement_or_adoption"})

    def test_missing_duplicate_and_unknown_mappings_fail(self) -> None:
        for mutation, message in (("missing","missing"),("duplicate","duplicate"),("unknown","missing")):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                project = self.copy_project(temporary)
                path = project / "interop/maintainer-policy-declaration/projection-contract-v1/mapping.json"
                data = json.loads(path.read_text())
                if mutation == "missing": data["mappings"].pop()
                elif mutation == "duplicate": data["mappings"].append(dict(data["mappings"][0]))
                else: data["mappings"][0]["pointer"] = "/unknown"
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, message): declaration_projection.build(project)

    def test_not_declared_never_becomes_obligation_or_checklist(self) -> None:
        root = self.project / "interop/maintainer-policy-declaration/projection-contract-v1"
        contract = json.loads((root / "projection-contract.json").read_text())
        source = json.loads((self.project / declaration_projection.SOURCE).read_text())
        sensitive = {"disclosure","human_review","human_accountability","license_ip_checks"}
        for item in contract["mappings"]:
            if item["pointer"].split("/")[-1] in sensitive:
                self.assertEqual(item["source_value"], "not_declared")
                self.assertEqual(item["disposition"], "not_established_by_source")
                self.assertIsNone(item["target_evidence"])
        output = (root / "AI_POLICY.projected.md").read_text()
        self.assertNotIn("- [ ]", output)
        self.assertIn("never converted into a contributor obligation", output)
        self.assertEqual(source["dimensions"]["human_review"], "not_declared")

    def test_stale_output_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.copy_project(temporary)
            path = project / "interop/maintainer-policy-declaration/projection-contract-v1/AI_POLICY.projected.md"
            path.write_text("stale\n")
            with self.assertRaisesRegex(ValueError, "stale"): declaration_projection.run(project, True)


if __name__ == "__main__":
    unittest.main()
