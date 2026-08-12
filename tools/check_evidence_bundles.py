"""Verify immutable Patch Cabinet bundles through registered offline replay capsules."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from types import ModuleType


MAX_JSON_BYTES = 2_000_000
MAX_REGISTRY_BYTES = 200_000
MAX_REGISTERED_FILE_BYTES = 5_000_000
MAX_ENGINES = 20
MAX_BUNDLES = 100
STANDALONE_EVIDENCE_NARRATIVES = {
    "2026-08-12-no-ready-policy-gate.md": (
        "bbcb324bfe007d957bc177c2d3eedb6386b89eb1f3522a07744ba27f389fd077"
    )
}
REPLAY_TIMEOUT_SECONDS = 60
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SEMVER = re.compile(r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$")
ADAPTER_ID = re.compile(r"^replay-v[1-9][0-9]*$")
VERSION_TEXT = re.compile(r"^[0-9]+(?:\.[0-9]+){1,2}$")
SUPPORTED_OUTPUT_SCHEMAS = {"1", "2"}


@dataclass(frozen=True)
class Bundle:
    manifest_path: Path
    policy_path: Path
    markdown_path: Path
    engine_version: str


def _evidence_entry_limit(bundle_limit: int = MAX_BUNDLES) -> int:
    if type(bundle_limit) is not int or bundle_limit < 0:
        raise ValueError("bundle limit must be a nonnegative integer")
    return bundle_limit * 4 + len(STANDALONE_EVIDENCE_NARRATIVES)


def _reject_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key in evidence metadata")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant in evidence metadata")


def _load_json(path: Path, *, byte_limit: int = MAX_JSON_BYTES) -> object:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{path.name}: JSON input must be a nonsymlink regular file")
    with path.open("rb") as stream:
        payload = stream.read(byte_limit + 1)
    if len(payload) > byte_limit:
        raise ValueError(f"{path.name}: exceeds the JSON byte limit")
    return json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_object,
        parse_constant=_reject_constant,
    )


def _digest(path: Path, *, byte_limit: int = MAX_REGISTERED_FILE_BYTES) -> str:
    if path.stat().st_size > byte_limit:
        raise ValueError(f"{path.name}: exceeds the registered-file byte limit")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _scoped_directory(root: Path, relative: str) -> Path:
    if "\\" in relative:
        raise ValueError(f"{relative}: backslashes are forbidden in project paths")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"{relative}: directory path escapes its project scope")
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{relative}: project directory paths cannot contain symlinks")
    resolved_root = root.resolve(strict=True)
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(resolved_root) or not resolved.is_dir():
        raise ValueError(f"{relative}: project directory is outside the repository")
    return resolved


def _bounded_regular_entries(directory: Path, *, limit: int, label: str) -> list[Path]:
    entries: list[Path] = []
    for path in directory.iterdir():
        if len(entries) >= limit:
            raise ValueError(f"{label} exceeds its file limit")
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{label} accepts nonsymlink regular files only")
        entries.append(path)
    return entries


def _registered_file(
    root: Path,
    record: object,
    *,
    label: str,
    required_prefix: str,
    required_name: str | None = None,
) -> Path:
    if type(record) is not dict or set(record) != {"path", "sha256"}:
        raise ValueError(f"{label}: file record differs")
    relative = record["path"]
    expected_digest = record["sha256"]
    if type(relative) is not str or len(relative) > 300 or "\\" in relative:
        raise ValueError(f"{label}: path differs")
    pure = PurePosixPath(relative)
    if (
        pure.is_absolute()
        or not pure.parts
        or any(part in {"", ".", ".."} for part in pure.parts)
        or not relative.startswith(required_prefix)
        or (required_name is not None and pure.name != required_name)
    ):
        raise ValueError(f"{label}: path escapes its registered scope")
    if type(expected_digest) is not str or SHA256.fullmatch(expected_digest) is None:
        raise ValueError(f"{label}: SHA-256 differs")
    if expected_digest == "0" * 64:
        raise ValueError(f"{label}: zero SHA-256 is forbidden")

    scope = _scoped_directory(root, required_prefix.rstrip("/"))
    unresolved = root.joinpath(*pure.parts)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label}: registered paths cannot contain symlinks")
    resolved = unresolved.resolve(strict=True)
    if not resolved.is_relative_to(scope) or not resolved.is_file():
        raise ValueError(f"{label}: registered path is not a regular project file")
    if _digest(resolved) != expected_digest:
        raise ValueError(f"{label}: registered file digest differs")
    return resolved


def _load_registry(root: Path) -> dict[str, object]:
    registry_path = _scoped_directory(root, "patch-cabinet/verifiers") / "index.json"
    registry = _load_json(registry_path, byte_limit=MAX_REGISTRY_BYTES)
    expected_root = {
        "schema_version",
        "active_engine",
        "active_descriptor",
        "replay_adapters",
        "engines",
    }
    if type(registry) is not dict or set(registry) != expected_root:
        raise ValueError("verifier registry envelope differs")
    if registry["schema_version"] != "1":
        raise ValueError("verifier registry schema differs")

    adapters = registry["replay_adapters"]
    engines = registry["engines"]
    active_engine = registry["active_engine"]
    if type(adapters) is not dict or not adapters or len(adapters) > MAX_ENGINES:
        raise ValueError("verifier adapter registry differs")
    if type(engines) is not dict or not engines or len(engines) > MAX_ENGINES:
        raise ValueError("verifier engine registry differs")
    if type(active_engine) is not str or active_engine not in engines:
        raise ValueError("active verifier engine differs")

    for adapter_name, record in adapters.items():
        if type(adapter_name) is not str or ADAPTER_ID.fullmatch(adapter_name) is None:
            raise ValueError("replay adapter identity differs")
        _registered_file(
            root,
            record,
            label=f"adapter {adapter_name}",
            required_prefix="patch-cabinet/verifiers/",
        )

    active_count = 0
    for engine_version, engine in engines.items():
        if type(engine_version) is not str or SEMVER.fullmatch(engine_version) is None:
            raise ValueError("registered engine version differs")
        expected_engine_fields = {
            "engine_name",
            "engine_version",
            "output_schema_version",
            "mode",
            "replay_adapter",
            "python",
            "policy",
            "dependencies",
            "wheel",
            "requirements_lock",
            "capsule_note",
            "test_vector",
        }
        if type(engine) is not dict or set(engine) != expected_engine_fields:
            raise ValueError(f"engine {engine_version}: descriptor differs")
        if engine["engine_name"] != "patch-cabinet" or engine["engine_version"] != engine_version:
            raise ValueError(f"engine {engine_version}: identity differs")
        if engine["output_schema_version"] not in SUPPORTED_OUTPUT_SCHEMAS:
            raise ValueError(f"engine {engine_version}: output schema differs")
        if engine["mode"] not in {"active", "replay-only"}:
            raise ValueError(f"engine {engine_version}: mode differs")
        if engine["mode"] == "active":
            active_count += 1
            if engine_version != active_engine:
                raise ValueError(f"engine {engine_version}: active identity differs")
        elif engine_version == active_engine:
            raise ValueError(f"engine {engine_version}: active mode differs")
        if engine["replay_adapter"] not in adapters:
            raise ValueError(f"engine {engine_version}: replay adapter is unknown")

        python = engine["python"]
        if type(python) is not dict or set(python) != {"minimum", "maximum"}:
            raise ValueError(f"engine {engine_version}: Python range differs")
        if any(
            type(python[field]) is not str
            or re.fullmatch(r"^[0-9]+\.[0-9]+$", python[field]) is None
            for field in ("minimum", "maximum")
        ):
            raise ValueError(f"engine {engine_version}: Python version differs")
        minimum = tuple(int(piece) for piece in python["minimum"].split("."))
        maximum = tuple(int(piece) for piece in python["maximum"].split("."))
        if minimum > maximum:
            raise ValueError(f"engine {engine_version}: Python range is reversed")

        policy = engine["policy"]
        if type(policy) is not dict or set(policy) != {
            "version",
            "source_path",
            "source_sha256",
        }:
            raise ValueError(f"engine {engine_version}: policy descriptor differs")
        if type(policy["version"]) is not str or not policy["version"]:
            raise ValueError(f"engine {engine_version}: policy version differs")
        _registered_file(
            root,
            {"path": policy["source_path"], "sha256": policy["source_sha256"]},
            label=f"engine {engine_version} policy",
            required_prefix="patch-cabinet/verifiers/policies/",
            required_name="policy.py",
        )

        dependencies = engine["dependencies"]
        if (
            type(dependencies) is not dict
            or set(dependencies) != {"packaging"}
            or type(dependencies["packaging"]) is not str
            or VERSION_TEXT.fullmatch(dependencies["packaging"]) is None
        ):
            raise ValueError(f"engine {engine_version}: dependency descriptor differs")
        dependency_version = dependencies["packaging"]
        wheel_name = f"packaging-{dependency_version}-py3-none-any.whl"
        wheel = _registered_file(
            root,
            engine["wheel"],
            label=f"engine {engine_version} wheel",
            required_prefix=f"patch-cabinet/verifiers/{engine_version}/wheelhouse/",
            required_name=wheel_name,
        )
        lock = _registered_file(
            root,
            engine["requirements_lock"],
            label=f"engine {engine_version} requirements lock",
            required_prefix=f"patch-cabinet/verifiers/{engine_version}/",
            required_name="requirements.lock",
        )
        _registered_file(
            root,
            engine["capsule_note"],
            label=f"engine {engine_version} capsule note",
            required_prefix=f"patch-cabinet/verifiers/{engine_version}/",
            required_name="CAPSULE.md",
        )
        expected_lock = (
            f"packaging=={dependency_version} \\\n"
            f"    --hash=sha256:{_digest(wheel)}\n"
        )
        if lock.read_text(encoding="utf-8") != expected_lock:
            raise ValueError(f"engine {engine_version}: requirements lock content differs")

        vector = engine["test_vector"]
        if engine["mode"] == "active":
            if type(vector) is not dict or set(vector) != {"manifest", "policy", "markdown"}:
                raise ValueError(f"engine {engine_version}: active replay vector differs")
            _registered_file(
                root,
                vector["manifest"],
                label=f"engine {engine_version} vector manifest",
                required_prefix="patch-cabinet/data/candidates/",
                required_name="synthetic.json",
            )
            _registered_file(
                root,
                vector["policy"],
                label=f"engine {engine_version} vector policy",
                required_prefix="patch-cabinet/samples/",
                required_name="candidate-ranking.json",
            )
            _registered_file(
                root,
                vector["markdown"],
                label=f"engine {engine_version} vector Markdown",
                required_prefix="patch-cabinet/samples/",
                required_name="candidate-ranking.md",
            )
        elif vector is not None:
            raise ValueError(f"engine {engine_version}: replay-only engine cannot own an active vector")

    if active_count != 1:
        raise ValueError("verifier registry must contain exactly one active engine")
    _verify_active_descriptor(root, registry)
    return registry


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load registered module {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _verify_active_descriptor(root: Path, registry: dict[str, object]) -> None:
    engine_path = _registered_file(
        root,
        registry["active_descriptor"],
        label="active engine descriptor",
        required_prefix="patch-cabinet/src/patch_cabinet/",
        required_name="engine.py",
    )
    tree = ast.parse(engine_path.read_text(encoding="utf-8"), filename=str(engine_path))
    literal_names = {
        "ENGINE_NAME",
        "ENGINE_VERSION",
        "OUTPUT_SCHEMA_VERSION",
        "EXPECTED_DEPENDENCIES",
    }
    observed: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(
            node.value.value, str
        ):
            continue
        if isinstance(node, ast.ImportFrom):
            continue
        if isinstance(node, ast.FunctionDef) and node.name == "validate_runtime_dependencies":
            if node.decorator_list:
                raise ValueError("active engine descriptor function cannot have decorators")
            continue
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            raise ValueError("active engine descriptor contains unexpected executable syntax")
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in literal_names:
            raise ValueError("active engine descriptor contains an unexpected assignment")
        try:
            observed[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError) as error:
            raise ValueError("active engine descriptor contains a nonliteral identity") from error
    if set(observed) != literal_names:
        raise ValueError("active engine descriptor omits a literal identity")
    active_version = registry["active_engine"]
    active = registry["engines"][active_version]
    _registered_file(
        root,
        {
            "path": "patch-cabinet/src/patch_cabinet/policy.py",
            "sha256": active["policy"]["source_sha256"],
        },
        label="active policy source",
        required_prefix="patch-cabinet/src/patch_cabinet/",
        required_name="policy.py",
    )
    normalized = {
        "engine_name": observed["ENGINE_NAME"],
        "engine_version": observed["ENGINE_VERSION"],
        "output_schema_version": observed["OUTPUT_SCHEMA_VERSION"],
        "dependencies": observed["EXPECTED_DEPENDENCIES"],
    }
    expected = {
        "engine_name": active["engine_name"],
        "engine_version": active["engine_version"],
        "output_schema_version": active["output_schema_version"],
        "dependencies": active["dependencies"],
    }
    if normalized != expected:
        raise ValueError("active engine source differs from the verifier registry")


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


def _claim_bundle_paths(claimed_paths: set[str], stem: str) -> set[str]:
    expected = _expected_paths(stem)
    if claimed_paths & expected:
        raise ValueError("candidate evidence bundles reuse an artifact path")
    claimed_paths.update(expected)
    return expected


def _verify_inventory(root: Path, registry: dict[str, object]) -> list[Bundle]:
    candidate_dir = _scoped_directory(root, "patch-cabinet/data/candidates")
    evidence_dir = _scoped_directory(root, "patch-cabinet/evidence")
    evidence_entries = _bounded_regular_entries(
        evidence_dir,
        limit=_evidence_entry_limit(),
        label="evidence directory",
    )
    candidate_entries = _bounded_regular_entries(
        candidate_dir,
        limit=MAX_BUNDLES + 1,
        label="candidate directory",
    )
    unexpected_candidates = {
        path.name
        for path in candidate_entries
        if path.name != "synthetic.json" and path.suffix != ".json"
    }
    if unexpected_candidates:
        raise ValueError("candidate directory contains an unreceipted artifact")
    manifests = sorted(path for path in candidate_entries if path.name != "synthetic.json")
    if not manifests:
        raise ValueError("no current-candidate evidence manifest is present")
    if len(manifests) > MAX_BUNDLES:
        raise ValueError("candidate evidence inventory exceeds its bundle limit")
    if any(f"{manifest.stem}.md" in STANDALONE_EVIDENCE_NARRATIVES for manifest in manifests):
        raise ValueError("candidate bundle cannot share a reserved standalone narrative stem")

    bundles: list[Bundle] = []
    expected_evidence: set[str] = set()
    claimed_paths: set[str] = set()
    for manifest_path in manifests:
        if manifest_path.is_symlink() or not manifest_path.is_file():
            raise ValueError("candidate evidence manifests must be regular files")
        stem = manifest_path.stem
        expected_evidence.update(_expected_evidence_names(stem))
        expected = _claim_bundle_paths(claimed_paths, stem)
        receipt_path = evidence_dir / f"{stem}-receipt.json"
        receipt = _load_json(receipt_path)
        if type(receipt) is not dict or set(receipt) != {"schema_version", "bundle", "files"}:
            raise ValueError(f"{receipt_path.name}: malformed receipt")
        if receipt["schema_version"] != "1" or receipt["bundle"] != stem:
            raise ValueError(f"{receipt_path.name}: receipt identity differs")
        files = receipt["files"]
        if type(files) is not dict or set(files) != expected:
            raise ValueError(f"{receipt_path.name}: receipt file set differs")

        for relative, expected_digest in files.items():
            if (
                type(expected_digest) is not str
                or SHA256.fullmatch(expected_digest) is None
                or expected_digest == "0" * 64
            ):
                raise ValueError(f"{receipt_path.name}: invalid digest for {relative}")
            actual_digest = _digest(root / relative)
            if actual_digest != expected_digest:
                raise ValueError(f"{receipt_path.name}: digest differs for {relative}")

        policy_path = evidence_dir / f"{stem}-policy.json"
        policy = _load_json(policy_path)
        expected_policy_fields = {
            "schema_version",
            "engine",
            "policy",
            "dependencies",
            "source_label",
            "results",
        }
        if type(policy) is not dict or set(policy) != expected_policy_fields:
            raise ValueError(f"{policy_path.name}: policy envelope differs")
        if policy["source_label"] != manifest_path.name:
            raise ValueError(f"{policy_path.name}: policy source label differs")
        engine_identity = policy["engine"]
        if type(engine_identity) is not dict or set(engine_identity) != {"name", "version"}:
            raise ValueError(f"{policy_path.name}: engine identity differs")
        engine_version = engine_identity["version"]
        if type(engine_version) is not str or engine_version not in registry["engines"]:
            raise ValueError(f"{policy_path.name}: engine is not registered")
        registered = registry["engines"][engine_version]
        if engine_identity != {
            "name": registered["engine_name"],
            "version": registered["engine_version"],
        }:
            raise ValueError(f"{policy_path.name}: engine identity differs")
        if policy["schema_version"] != registered["output_schema_version"]:
            raise ValueError(f"{policy_path.name}: output schema differs")
        if policy["dependencies"] != registered["dependencies"]:
            raise ValueError(f"{policy_path.name}: dependency identity differs")
        policy_metadata = policy["policy"]
        expected_metadata_fields = {"version", "source_sha256", "as_of", "evaluation_mode"}
        if type(policy_metadata) is not dict or set(policy_metadata) != expected_metadata_fields:
            raise ValueError(f"{policy_path.name}: policy metadata differs")
        if policy_metadata["version"] != registered["policy"]["version"]:
            raise ValueError(f"{policy_path.name}: policy version differs")
        if policy_metadata["source_sha256"] != registered["policy"]["source_sha256"]:
            raise ValueError(f"{policy_path.name}: policy source digest differs")
        if policy_metadata["evaluation_mode"] not in {"live", "historical"}:
            raise ValueError(f"{policy_path.name}: evaluation mode differs")
        raw_as_of = policy_metadata["as_of"]
        try:
            as_of = date.fromisoformat(raw_as_of)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{policy_path.name}: invalid policy date") from error
        if type(raw_as_of) is not str or as_of.isoformat() != raw_as_of:
            raise ValueError(f"{policy_path.name}: policy date is not canonical")
        if type(policy["results"]) is not list:
            raise ValueError(f"{policy_path.name}: result envelope differs")

        bundles.append(
            Bundle(
                manifest_path=manifest_path,
                policy_path=policy_path,
                markdown_path=evidence_dir / f"{stem}-policy.md",
                engine_version=engine_version,
            )
        )

    actual_evidence = {
        path.name
        for path in evidence_entries
        if path.name not in STANDALONE_EVIDENCE_NARRATIVES
    }
    for path in evidence_entries:
        expected_narrative_digest = STANDALONE_EVIDENCE_NARRATIVES.get(path.name)
        if expected_narrative_digest is not None and _digest(path) != expected_narrative_digest:
            raise ValueError("standalone narrative digest differs from the exact allowlist")
    if actual_evidence != expected_evidence:
        raise ValueError("evidence directory contains an orphan or misses a receipted artifact")
    return bundles


def _sanitized_child_environment() -> dict[str, str]:
    allowed = ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR")
    environment = {key: os.environ[key] for key in allowed if key in os.environ}
    environment.update(
        {
            "PYTHONHASHSEED": "0",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    return environment


def _run_registered_replays(root: Path, engines: list[str]) -> None:
    script = Path(__file__).resolve(strict=True)
    for engine_version in engines:
        command = [
            sys.executable,
            "-I",
            str(script),
            "--root",
            str(root),
            "--replay-engine",
            engine_version,
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=root,
                env=_sanitized_child_environment(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=REPLAY_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ValueError(f"engine {engine_version}: replay timed out") from error
        if completed.returncode != 0:
            raise ValueError(f"engine {engine_version}: replay worker failed closed")
        print(f"Engine {engine_version} replay worker passed.")


def _replay_engine(root: Path, engine_version: str) -> int:
    registry = _load_registry(root)
    bundles = _verify_inventory(root, registry)
    if engine_version not in registry["engines"]:
        raise ValueError(f"engine {engine_version}: replay engine is not registered")
    engine = registry["engines"][engine_version]
    minimum = tuple(int(piece) for piece in engine["python"]["minimum"].split("."))
    maximum = tuple(int(piece) for piece in engine["python"]["maximum"].split("."))
    running = sys.version_info[:2]
    if running < minimum or running > maximum:
        raise ValueError(f"engine {engine_version}: Python runtime is outside the registry range")

    wheel = _registered_file(
        root,
        engine["wheel"],
        label=f"engine {engine_version} wheel",
        required_prefix=f"patch-cabinet/verifiers/{engine_version}/wheelhouse/",
        required_name=f"packaging-{engine['dependencies']['packaging']}-py3-none-any.whl",
    )
    sys.path.insert(0, str(wheel))

    import packaging

    imported_origin = str(Path(packaging.__file__))
    expected_prefixes = (str(wheel) + os.sep, str(wheel) + "/")
    if not imported_origin.startswith(expected_prefixes):
        raise ValueError(f"engine {engine_version}: dependency did not load from its wheel")
    if packaging.__version__ != engine["dependencies"]["packaging"]:
        raise ValueError(f"engine {engine_version}: imported dependency version differs")
    expected_policy = _registered_file(
        root,
        {
            "path": engine["policy"]["source_path"],
            "sha256": engine["policy"]["source_sha256"],
        },
        label=f"engine {engine_version} policy",
        required_prefix="patch-cabinet/verifiers/policies/",
        required_name="policy.py",
    )
    imported_policy = _load_module(
        expected_policy,
        f"patch_cabinet_policy_{engine_version.replace('.', '_')}",
    )

    adapter_record = registry["replay_adapters"][engine["replay_adapter"]]
    adapter_path = _registered_file(
        root,
        adapter_record,
        label=f"engine {engine_version} adapter",
        required_prefix="patch-cabinet/verifiers/",
    )
    adapter = _load_module(adapter_path, f"patch_cabinet_{engine_version.replace('.', '_')}_replay")
    matching = [bundle for bundle in bundles if bundle.engine_version == engine_version]
    if engine["mode"] == "replay-only" and not matching:
        raise ValueError(f"engine {engine_version}: replay-only registry entry has no bundle")
    for bundle in matching:
        adapter.replay_bundle(
            manifest_path=bundle.manifest_path,
            policy_path=bundle.policy_path,
            markdown_path=bundle.markdown_path,
            expected=engine,
            policy_module=imported_policy,
        )
    vector_count = 0
    if engine["test_vector"] is not None:
        vector = engine["test_vector"]
        adapter.replay_bundle(
            manifest_path=_registered_file(
                root,
                vector["manifest"],
                label=f"engine {engine_version} vector manifest",
                required_prefix="patch-cabinet/data/candidates/",
                required_name="synthetic.json",
            ),
            policy_path=_registered_file(
                root,
                vector["policy"],
                label=f"engine {engine_version} vector policy",
                required_prefix="patch-cabinet/samples/",
                required_name="candidate-ranking.json",
            ),
            markdown_path=_registered_file(
                root,
                vector["markdown"],
                label=f"engine {engine_version} vector Markdown",
                required_prefix="patch-cabinet/samples/",
                required_name="candidate-ranking.md",
            ),
            expected=engine,
            policy_module=imported_policy,
        )
        vector_count = 1
    print(
        f"Engine {engine_version} replay passed: {len(matching)} evidence bundle(s), "
        f"{vector_count} active vector(s)."
    )
    return len(matching)


def verify(root: Path) -> int:
    registry = _load_registry(root)
    bundles = _verify_inventory(root, registry)
    engines = sorted(registry["engines"])
    _run_registered_replays(root, engines)
    return len(bundles)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--replay-engine")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = (
        args.root.resolve(strict=True)
        if args.root is not None
        else Path(__file__).resolve(strict=True).parent.parent
    )
    if args.replay_engine:
        _replay_engine(root, args.replay_engine)
        return 0
    count = verify(root)
    print(f"Evidence-bundle review passed: {count} immutable candidate bundle(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
