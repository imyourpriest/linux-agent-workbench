from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from support_eval_lab import policy_successor


class PolicySuccessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]

    def copy_project(self, temporary: str) -> Path:
        project = Path(temporary) / "support-eval-lab"
        shutil.copytree(self.project / policy_successor.ROOT_NAME, project / policy_successor.ROOT_NAME)
        shutil.copytree(
            self.project / policy_successor.PREDECESSOR_RELEASE_ROOT,
            project / policy_successor.PREDECESSOR_RELEASE_ROOT,
        )
        shutil.copy2(self.project / "candidate-registry.json", project / "candidate-registry.json")
        return project

    def test_bundle_is_fresh_deterministic_and_inert(self) -> None:
        first = policy_successor.build(self.project)
        second = policy_successor.build(self.project)
        self.assertEqual(first, second)
        receipt = policy_successor.run(self.project, True)
        self.assertEqual(receipt["result"], "valid_inert_direct_successor_bundle")
        self.assertEqual(receipt["revenue_usd"], "0.00")

    def test_registry_has_one_direct_successor_and_no_selection(self) -> None:
        registry = json.loads((self.project / "candidate-registry.json").read_text())
        policy_successor._validate_registry(registry)
        self.assertIsNone(registry["selected_for_activation"])
        self.assertEqual(len(registry["candidates"]), 2)
        self.assertEqual(
            registry["candidates"][0]["experiment_id"], "policy-release-r004"
        )
        self.assertEqual(
            registry["predecessor_release"], policy_successor.PREDECESSOR_RELEASE_BINDING
        )
        self.assertEqual(sum(item["predecessor_id"] == "policy-starter-synthetic-v1" for item in registry["candidates"]), 1)

    def test_fork_cycle_activation_and_extra_files_fail(self) -> None:
        for field, value in (("selected_for_activation","maintainer-ai-policy-clarity-synthetic-v1"),):
            with tempfile.TemporaryDirectory() as temporary:
                project=self.copy_project(temporary); path=project/"candidate-registry.json"; data=json.loads(path.read_text()); data[field]=value; path.write_text(json.dumps(data))
                with self.assertRaises(ValueError): policy_successor.build(project)
        with tempfile.TemporaryDirectory() as temporary:
            project=self.copy_project(temporary); (project/policy_successor.ROOT_NAME/"EXTRA.md").write_text("extra")
            with self.assertRaisesRegex(ValueError,"inventory"): policy_successor.build(project)
        with tempfile.TemporaryDirectory() as temporary:
            project=self.copy_project(temporary); path=project/"candidate-registry.json"; data=json.loads(path.read_text()); third=dict(data["candidates"][1]); third["candidate_id"]="fork-candidate"; data["candidates"].append(third); path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"predecessor and one successor"): policy_successor.build(project)
        with tempfile.TemporaryDirectory() as temporary:
            project=self.copy_project(temporary); path=project/policy_successor.ROOT_NAME/"MEASUREMENT_CONTRACT.json"; data=json.loads(path.read_text()); data["activation"]=True; path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"source|measurement"): policy_successor.build(project)

    def test_frozen_predecessor_release_bytes_and_semantics_are_bound(self) -> None:
        policy_successor._verify_predecessor_release(
            self.project, policy_successor.PREDECESSOR_RELEASE_BINDING
        )
        mutations = (
            ("README.md", lambda path: path.write_bytes(path.read_bytes() + b"mutated\n"), "file binding"),
            ("ISSUE_FORM_DRAFT.yml", lambda path: path.write_bytes(path.read_bytes() + b"mutated\n"), "file binding"),
            ("RELEASE_BODY.md", lambda path: path.write_bytes(path.read_bytes() + b"mutated\n"), "file binding"),
            ("ai-policy-starter-v0.1.0.zip.sha256", lambda path: path.write_bytes(("0" * 64 + "  ai-policy-starter-v0.1.0.zip\n").encode()), "checksum"),
            ("RELEASE.json", self._mutate_tag, "file binding|tag"),
            ("manifest.json", self._mutate_experiment, "file binding|experiment"),
        )
        for name, mutation, message in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                project = self.copy_project(temporary)
                mutation(project / policy_successor.PREDECESSOR_RELEASE_ROOT / name)
                with self.assertRaisesRegex(ValueError, message):
                    policy_successor.build(project)

    @staticmethod
    def _mutate_tag(path: Path) -> None:
        data = json.loads(path.read_text())
        data["tag_name"] = "wrong-tag"
        path.write_text(json.dumps(data))

    @staticmethod
    def _mutate_experiment(path: Path) -> None:
        data = json.loads(path.read_text())
        data["experiment_id"] = "wrong-experiment"
        path.write_text(json.dumps(data))

    def test_archive_inventory_metadata_and_payloads_are_exact(self) -> None:
        archive = self.project / policy_successor.ROOT_NAME / policy_successor.ARCHIVE
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(bundle.namelist(), sorted(policy_successor.STATIC_FILES))
            for info in bundle.infolist():
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(info.date_time, policy_successor.FIXED_TIME)
                self.assertFalse((info.external_attr >> 16) & 0o111)
                self.assertEqual(bundle.read(info), (self.project/policy_successor.ROOT_NAME/info.filename).read_bytes())

    def test_staging_alias_and_unsafe_archive_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project=self.copy_project(temporary); root=project/policy_successor.ROOT_NAME
            (root/f".{policy_successor.ARCHIVE}.build").write_text("sentinel")
            with self.assertRaisesRegex(ValueError, "inventory"):
                policy_successor.run(project, False)
            self.assertEqual((root/f".{policy_successor.ARCHIVE}.build").read_text(), "sentinel")
            payload=policy_successor.build(self.project)[policy_successor.ARCHIVE]
            sources={name:(self.project/policy_successor.ROOT_NAME/name).read_bytes() for name in policy_successor.STATIC_FILES}
            policy_successor._validate_archive(payload,sources)
            bad=Path(temporary)/"bad.zip"
            with zipfile.ZipFile(bad,"w") as bundle: bundle.writestr("../escape",b"x")
            with self.assertRaises(ValueError): policy_successor._validate_archive(bad.read_bytes(),sources)


if __name__ == "__main__": unittest.main()
