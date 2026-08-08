"""Verify immutable Patch Cabinet evidence bundles and canonical policy output."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from importlib.metadata import version
from pathlib import Path


MAX_JSON_BYTES = 2_000_000
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _reject_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key in evidence bundle")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant in evidence bundle")


def _load_json(path: Path) -> object:
    payload = path.read_bytes()
    if len(payload) > MAX_JSON_BYTES:
        raise ValueError(f"{path.name}: exceeds the JSON byte limit")
    return json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_object,
        parse_constant=_reject_constant,
    )


def _expected_paths(stem: str) -> set[str]:
    return {
        f"patch-cabinet/data/candidates/{stem}.json",
        f"patch-cabinet/evidence/{stem}.md",
        f"patch-cabinet/evidence/{stem}-policy.json",
        f"patch-cabinet/evidence/{stem}-policy.md",
    }


def _expected_evidence_names(stem: str) -> set[str]:
    return {
        f"{stem}.md",
        f"{stem}-policy.json",
        f"{stem}-policy.md",
        f"{stem}-receipt.json",
    }


def _load_policy_engine(root: Path):
    source = root / "patch-cabinet" / "src"
    sys.path.insert(0, str(source))
    from patch_cabinet import __version__
    from patch_cabinet import policy as policy_module
    from patch_cabinet.cli import _render_markdown
    from patch_cabinet.policy import SEASON_POLICY_VERSION, evaluate_candidates

    return (
        __version__,
        policy_module,
        _render_markdown,
        SEASON_POLICY_VERSION,
        evaluate_candidates,
    )


def _verify_canonical_policy_output(
    *, root: Path, manifest_path: Path, evidence_dir: Path, manifest: object, policy: object
) -> None:
    if type(manifest) is not list or not manifest:
        raise ValueError(f"{manifest_path.name}: manifest must be a nonempty array")
    if type(policy) is not dict:
        raise ValueError(f"{manifest_path.name}: policy artifact must be an object")
    expected_root_fields = {
        "schema_version",
        "engine",
        "policy",
        "dependencies",
        "source_label",
        "results",
    }
    if set(policy) != expected_root_fields or policy["schema_version"] != "1":
        raise ValueError(f"{manifest_path.name}: policy envelope differs")
    if policy["source_label"] != manifest_path.name:
        raise ValueError(f"{manifest_path.name}: policy source label differs")

    (
        engine_version,
        policy_module,
        render_markdown,
        season_policy_version,
        evaluate_candidates,
    ) = _load_policy_engine(root)
    if policy["engine"] != {"name": "patch-cabinet", "version": engine_version}:
        raise ValueError(f"{manifest_path.name}: engine identity differs")
    if policy["dependencies"] != {"packaging": version("packaging")}:
        raise ValueError(f"{manifest_path.name}: dependency identity differs")

    policy_metadata = policy["policy"]
    expected_policy_fields = {"version", "source_sha256", "as_of", "evaluation_mode"}
    if type(policy_metadata) is not dict or set(policy_metadata) != expected_policy_fields:
        raise ValueError(f"{manifest_path.name}: policy metadata differs")
    policy_sha256 = hashlib.sha256(Path(policy_module.__file__).read_bytes()).hexdigest()
    if policy_metadata["version"] != season_policy_version:
        raise ValueError(f"{manifest_path.name}: policy version differs")
    if policy_metadata["source_sha256"] != policy_sha256:
        raise ValueError(f"{manifest_path.name}: policy source digest differs")
    if policy_metadata["evaluation_mode"] not in {"live", "historical"}:
        raise ValueError(f"{manifest_path.name}: evaluation mode differs")
    raw_as_of = policy_metadata["as_of"]
    try:
        as_of = date.fromisoformat(raw_as_of)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{manifest_path.name}: invalid policy date") from error
    if type(raw_as_of) is not str or as_of.isoformat() != raw_as_of:
        raise ValueError(f"{manifest_path.name}: policy date is not canonical")

    evaluations = evaluate_candidates(
        manifest,
        excluded_repositories=(),
        as_of=as_of,
        evaluation_mode=policy_metadata["evaluation_mode"],
    )
    expected_results = [evaluation.to_dict() for evaluation in evaluations]
    if policy["results"] != expected_results:
        raise ValueError(f"{manifest_path.name}: policy results do not replay exactly")

    expected_markdown = render_markdown(
        evaluations,
        source_label=manifest_path.name,
        as_of=as_of.isoformat(),
        evaluation_mode=policy_metadata["evaluation_mode"],
        policy_sha256=policy_sha256,
    ).encode("utf-8")
    policy_markdown_path = evidence_dir / f"{manifest_path.stem}-policy.md"
    if policy_markdown_path.read_bytes() != expected_markdown:
        raise ValueError(f"{manifest_path.name}: policy Markdown does not replay exactly")


def verify(root: Path) -> int:
    candidate_dir = root / "patch-cabinet" / "data" / "candidates"
    evidence_dir = root / "patch-cabinet" / "evidence"
    manifests = sorted(path for path in candidate_dir.glob("*.json") if path.stem != "synthetic")
    if not manifests:
        raise ValueError("no current-candidate evidence manifest is present")

    expected_evidence: set[str] = set()
    for manifest_path in manifests:
        stem = manifest_path.stem
        expected_evidence.update(_expected_evidence_names(stem))
        receipt_path = evidence_dir / f"{stem}-receipt.json"
        receipt = _load_json(receipt_path)
        if type(receipt) is not dict or set(receipt) != {"schema_version", "bundle", "files"}:
            raise ValueError(f"{receipt_path.name}: malformed receipt")
        if receipt["schema_version"] != "1" or receipt["bundle"] != stem:
            raise ValueError(f"{receipt_path.name}: receipt identity differs")
        files = receipt["files"]
        expected = _expected_paths(stem)
        if type(files) is not dict or set(files) != expected:
            raise ValueError(f"{receipt_path.name}: receipt file set differs")

        for relative, expected_digest in files.items():
            if (
                type(expected_digest) is not str
                or SHA256.fullmatch(expected_digest) is None
                or expected_digest == "0" * 64
            ):
                raise ValueError(f"{receipt_path.name}: invalid digest for {relative}")
            actual_digest = hashlib.sha256((root / relative).read_bytes()).hexdigest()
            if actual_digest != expected_digest:
                raise ValueError(f"{receipt_path.name}: digest differs for {relative}")

        manifest = _load_json(manifest_path)
        policy = _load_json(evidence_dir / f"{stem}-policy.json")
        _verify_canonical_policy_output(
            root=root,
            manifest_path=manifest_path,
            evidence_dir=evidence_dir,
            manifest=manifest,
            policy=policy,
        )

    actual_evidence = {path.name for path in evidence_dir.iterdir() if path.is_file()}
    if actual_evidence != expected_evidence:
        raise ValueError("evidence directory contains an orphan or is missing a receipted artifact")
    if any(not path.is_file() for path in evidence_dir.iterdir()):
        raise ValueError("evidence directory accepts regular files only")
    return len(manifests)


def main() -> int:
    root = Path(__file__).resolve(strict=True).parent.parent
    count = verify(root)
    print(f"Evidence-bundle review passed: {count} immutable candidate bundle(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
