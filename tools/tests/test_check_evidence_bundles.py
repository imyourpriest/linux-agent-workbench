from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "tools" / "check_evidence_bundles.py"
SPEC = importlib.util.spec_from_file_location("evidence_checker_under_test", CHECKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load evidence checker")
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


class EvidenceBundleCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "patch-cabinet", self.root / "patch-cabinet")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def registry_path(self) -> Path:
        return self.root / "patch-cabinet" / "verifiers" / "index.json"

    @property
    def policy_path(self) -> Path:
        return (
            self.root
            / "patch-cabinet"
            / "evidence"
            / "2026-08-08-initial-shortlist-policy.json"
        )

    @property
    def receipt_path(self) -> Path:
        return (
            self.root
            / "patch-cabinet"
            / "evidence"
            / "2026-08-08-initial-shortlist-receipt.json"
        )

    def read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def write_json(self, path: Path, payload: object) -> None:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")

    def rebind_policy_receipt(self) -> None:
        receipt = self.read_json(self.receipt_path)
        relative = "patch-cabinet/evidence/2026-08-08-initial-shortlist-policy.json"
        receipt["files"][relative] = hashlib.sha256(self.policy_path.read_bytes()).hexdigest()
        self.write_json(self.receipt_path, receipt)

    def test_public_repository_replays_every_registered_engine(self) -> None:
        self.assertEqual(checker.verify(ROOT), 3)

    def test_exact_standalone_narrative_is_allowed_but_near_name_is_not(self) -> None:
        registry = checker._load_registry(self.root)
        self.assertEqual(len(checker._verify_inventory(self.root, registry)), 3)
        evidence = self.root / "patch-cabinet" / "evidence"
        exact = evidence / "2026-08-12-no-ready-policy-gate.md"
        exact.write_bytes(exact.read_bytes() + b"\nchanged narrative\n")
        with self.assertRaisesRegex(ValueError, "narrative digest"):
            checker._verify_inventory(self.root, registry)
        shutil.copy2(ROOT / "patch-cabinet" / "evidence" / exact.name, exact)
        near_name = evidence / "2026-08-12-no-ready-policy-gates.md"
        near_name.write_text("near-name orphan\n", encoding="utf-8", newline="\n")
        with self.assertRaisesRegex(ValueError, "orphan"):
            checker._verify_inventory(self.root, registry)

    def test_candidate_bundle_cannot_share_standalone_narrative_stem(self) -> None:
        candidate = self.root / "patch-cabinet" / "data" / "candidates"
        source = candidate / "2026-08-08-initial-shortlist.json"
        conflicting = candidate / "2026-08-12-no-ready-policy-gate.json"
        shutil.copy2(source, conflicting)
        with self.assertRaisesRegex(ValueError, "reserved standalone narrative stem"):
            checker._verify_inventory(self.root, checker._load_registry(self.root))

    def test_evidence_capacity_includes_only_exact_narrative_allowlist(self) -> None:
        self.assertEqual(
            checker._evidence_entry_limit(),
            checker.MAX_BUNDLES * 4 + len(checker.STANDALONE_EVIDENCE_NARRATIVES),
        )
        self.assertEqual(checker._evidence_entry_limit(0), 1)
        with self.assertRaises(ValueError):
            checker._evidence_entry_limit(True)

    def test_unknown_artifact_engine_fails_closed(self) -> None:
        policy = self.read_json(self.policy_path)
        policy["engine"]["version"] = "9.9.9"
        self.write_json(self.policy_path, policy)
        self.rebind_policy_receipt()
        registry = checker._load_registry(self.root)
        with self.assertRaisesRegex(ValueError, "not registered"):
            checker._verify_inventory(self.root, registry)

    def test_artifact_cannot_cross_into_another_engine(self) -> None:
        policy = self.read_json(self.policy_path)
        policy["engine"]["version"] = "0.2.0"
        self.write_json(self.policy_path, policy)
        self.rebind_policy_receipt()
        registry = checker._load_registry(self.root)
        with self.assertRaisesRegex(ValueError, "dependency identity"):
            checker._verify_inventory(self.root, registry)

    def test_registry_rejects_path_traversal(self) -> None:
        registry = self.read_json(self.registry_path)
        registry["replay_adapters"]["replay-v1"]["path"] = "../outside.py"
        self.write_json(self.registry_path, registry)
        with self.assertRaisesRegex(ValueError, "path escapes"):
            checker._load_registry(self.root)

    def test_registry_rejects_windows_backslash_traversal(self) -> None:
        registry = self.read_json(self.registry_path)
        registry["replay_adapters"]["replay-v1"]["path"] = (
            "patch-cabinet/verifiers/..\\..\\tools\\check_evidence_bundles.py"
        )
        self.write_json(self.registry_path, registry)
        with self.assertRaisesRegex(ValueError, "path differs|backslashes"):
            checker._load_registry(self.root)

    def test_registry_rejects_duplicate_keys(self) -> None:
        raw = self.registry_path.read_text(encoding="utf-8")
        raw = raw.replace(
            '"active_engine": "0.3.0",',
            '"active_engine": "0.1.0",\n  "active_engine": "0.3.0",',
            1,
        )
        self.registry_path.write_text(raw, encoding="utf-8", newline="\n")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            checker._load_registry(self.root)

    def test_missing_or_corrupt_capsule_file_fails(self) -> None:
        wheel = (
            self.root
            / "patch-cabinet"
            / "verifiers"
            / "0.1.0"
            / "wheelhouse"
            / "packaging-26.2-py3-none-any.whl"
        )
        wheel.unlink()
        with self.assertRaises((FileNotFoundError, ValueError)):
            checker._load_registry(self.root)

        shutil.copy2(
            ROOT
            / "patch-cabinet"
            / "verifiers"
            / "0.1.0"
            / "wheelhouse"
            / "packaging-26.2-py3-none-any.whl",
            wheel,
        )
        wheel.write_bytes(wheel.read_bytes() + b"tamper")
        with self.assertRaisesRegex(ValueError, "digest differs"):
            checker._load_registry(self.root)

    def test_adapter_lock_and_capsule_note_integrity_fail_closed(self) -> None:
        paths = [
            self.root / "patch-cabinet" / "verifiers" / "replay_v1.py",
            self.root / "patch-cabinet" / "verifiers" / "replay_v2.py",
            self.root / "patch-cabinet" / "verifiers" / "0.1.0" / "requirements.lock",
            self.root / "patch-cabinet" / "verifiers" / "0.1.0" / "CAPSULE.md",
        ]
        for path in paths:
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b"\ntamper\n")
                with self.assertRaisesRegex(ValueError, "digest differs"):
                    checker._load_registry(self.root)
                path.write_bytes(original)

    def test_dependency_spoof_in_artifact_fails(self) -> None:
        policy = self.read_json(self.policy_path)
        policy["dependencies"] = {"packaging": "26.3"}
        self.write_json(self.policy_path, policy)
        self.rebind_policy_receipt()
        registry = checker._load_registry(self.root)
        with self.assertRaisesRegex(ValueError, "dependency identity"):
            checker._verify_inventory(self.root, registry)

    def test_policy_source_tampering_fails(self) -> None:
        policy_source = (
            self.root
            / "patch-cabinet"
            / "verifiers"
            / "policies"
            / "season-1.2"
            / "policy.py"
        )
        policy_source.write_text(
            policy_source.read_text(encoding="utf-8") + "\n# tamper\n",
            encoding="utf-8",
            newline="\n",
        )
        with self.assertRaisesRegex(ValueError, "digest differs"):
            checker._load_registry(self.root)

    def test_registry_requires_historical_engine_coverage(self) -> None:
        registry = self.read_json(self.registry_path)
        del registry["engines"]["0.1.0"]
        self.write_json(self.registry_path, registry)
        loaded = checker._load_registry(self.root)
        with self.assertRaisesRegex(ValueError, "not registered"):
            checker._verify_inventory(self.root, loaded)

    def test_bundle_artifact_roles_cannot_collide(self) -> None:
        claimed: set[str] = set()
        checker._claim_bundle_paths(claimed, "example")
        with self.assertRaisesRegex(ValueError, "reuse an artifact path"):
            checker._claim_bundle_paths(claimed, "example-policy")

    def test_active_source_must_match_registry(self) -> None:
        engine_source = self.root / "patch-cabinet" / "src" / "patch_cabinet" / "engine.py"
        engine_source.write_text(
            engine_source.read_text(encoding="utf-8").replace('"0.3.0"', '"0.4.0"'),
            encoding="utf-8",
            newline="\n",
        )
        with self.assertRaisesRegex(ValueError, "digest differs"):
            checker._load_registry(self.root)

    def test_active_descriptor_is_never_executed_by_checker(self) -> None:
        engine_source = self.root / "patch-cabinet" / "src" / "patch_cabinet" / "engine.py"
        marker = self.root / "descriptor-executed.txt"
        engine_source.write_text(
            engine_source.read_text(encoding="utf-8")
            + f"\nopen({str(marker)!r}, 'w', encoding='utf-8').write('executed')\n",
            encoding="utf-8",
            newline="\n",
        )
        registry = self.read_json(self.registry_path)
        registry["active_descriptor"]["sha256"] = hashlib.sha256(
            engine_source.read_bytes()
        ).hexdigest()
        self.write_json(self.registry_path, registry)
        with self.assertRaisesRegex(ValueError, "unexpected executable syntax"):
            checker._load_registry(self.root)
        self.assertFalse(marker.exists())

    def test_active_policy_source_must_match_frozen_policy(self) -> None:
        policy_source = self.root / "patch-cabinet" / "src" / "patch_cabinet" / "policy.py"
        policy_source.write_text(
            policy_source.read_text(encoding="utf-8") + "\n# unversioned change\n",
            encoding="utf-8",
            newline="\n",
        )
        with self.assertRaisesRegex(ValueError, "active policy source.*digest differs"):
            checker._load_registry(self.root)

    def test_active_vector_is_semantically_replayed(self) -> None:
        vector = self.root / "patch-cabinet" / "samples" / "candidate-ranking.json"
        payload = self.read_json(vector)
        payload["results"][0]["score"] += 1
        self.write_json(vector, payload)
        registry = self.read_json(self.registry_path)
        registry["engines"]["0.3.0"]["test_vector"]["policy"]["sha256"] = hashlib.sha256(
            vector.read_bytes()
        ).hexdigest()
        self.write_json(self.registry_path, registry)
        with self.assertRaisesRegex(ValueError, "canonical JSON"):
            checker._replay_engine(self.root, "0.3.0")

    def test_symlinked_evidence_directory_fails_before_read(self) -> None:
        evidence = self.root / "patch-cabinet" / "evidence"
        actual = self.root / "patch-cabinet" / "evidence-actual"
        evidence.rename(actual)
        try:
            evidence.symlink_to(actual, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"directory symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "cannot contain symlinks"):
            checker._verify_inventory(self.root, checker._load_registry(self.root))

    def test_noncanonical_date_fails_before_replay(self) -> None:
        policy = self.read_json(self.policy_path)
        policy["policy"]["as_of"] = "20260808"
        self.write_json(self.policy_path, policy)
        self.rebind_policy_receipt()
        registry = checker._load_registry(self.root)
        with self.assertRaisesRegex(ValueError, "not canonical"):
            checker._verify_inventory(self.root, registry)

    def test_replay_timeout_fails_closed(self) -> None:
        timeout = subprocess.TimeoutExpired(cmd=["python"], timeout=1)
        with patch.object(checker.subprocess, "run", side_effect=timeout):
            with self.assertRaisesRegex(ValueError, "timed out"):
                checker._run_registered_replays(self.root, ["0.1.0"])


if __name__ == "__main__":
    unittest.main()
