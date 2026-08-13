"""Deterministic non-authorizing interoperability companion for declaration schema 1."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Sequence

from .maintainer_policy_declaration import Declaration, _parse_declaration_payload


COMPONENT_VERSION = "0.1.0"
PROFILE_VERSION = "1"
MAX_FILE_BYTES = 65_536
MAX_VECTORS = 20
MAX_PAYLOAD_BYTES = 16_384
MAX_NODES = 2_000
MAX_STRUCTURE_DEPTH = 64
STATIC_FILES = ("README.md", "schema.json", "corpus.json")
GENERATED_FILES = (
    "AI_POLICY.draft.md",
    "PULL_REQUEST_TEMPLATE.fragment.md",
    "manifest.json",
    "validation-receipt.json",
)
EXPECTED_FILES = set(STATIC_FILES) | set(GENERATED_FILES)
BOUNDARY = (
    "Prototype structural interoperability evidence only; the strict Python parser is "
    "authoritative. No standard, independent-validator conformance, source truth, identity, "
    "authority, current permission, authorization, detection, or enforcement is established."
)


def _duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key is not allowed")
        result[key] = value
    return result


def _constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant is not allowed")


def _safe_read(path: Path) -> bytes:
    try:
        before = path.lstat()
    except OSError as error:
        raise ValueError("interop input cannot be inspected") from error
    if path.is_symlink() or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("interop inputs must be single-link nonsymlink regular files")
    if before.st_size > MAX_FILE_BYTES:
        raise ValueError("interop input exceeds the byte limit")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("interop input changed or aliases another path")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("interop input exceeds the byte limit")
    return payload


def _unsafe_directory(path: Path, inspected: os.stat_result) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return True
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(inspected, "st_file_attributes", 0) & flag)


def _check_directory_chain(project: Path, root: Path) -> None:
    """Reject links/reparse points from the trusted project boundary through root."""
    project = project.absolute()
    root = root.absolute()
    try:
        relative = root.relative_to(project)
    except ValueError as error:
        raise ValueError("interop directory must remain inside the project boundary") from error
    current = project
    for part in (Path(), *relative.parts):
        if part != Path():
            current /= part
        try:
            inspected = current.lstat()
        except OSError as error:
            raise ValueError("interop directory chain cannot be inspected") from error
        if _unsafe_directory(current, inspected) or not stat.S_ISDIR(inspected.st_mode):
            raise ValueError("interop directory chain must contain only regular directories")


def _check_root(project: Path, root: Path, *, check: bool) -> None:
    _check_directory_chain(project, root)
    try:
        inspected = root.lstat()
    except OSError as error:
        raise ValueError("interop directory cannot be inspected") from error
    if _unsafe_directory(root, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("interop boundary must be a non-link regular directory")
    actual = {entry.name for entry in os.scandir(root)}
    if not actual.issubset(EXPECTED_FILES) or not set(STATIC_FILES).issubset(actual):
        raise ValueError("interop inventory differs")
    if check and actual != EXPECTED_FILES:
        raise ValueError("interop inventory differs")


def _check_outputs(root: Path) -> None:
    for name in GENERATED_FILES:
        path = root / name
        if not path.exists():
            continue
        inspected = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1:
            raise ValueError("existing generated output must be a single-link regular file")


def _strict_json(payload: bytes, label: str) -> object:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError(f"{label} cannot contain a BOM")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_duplicates,
            parse_constant=_constant,
        )
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise ValueError(f"{label} is not strict JSON") from error
    return value


def _validate_structure_bounds(value: object) -> None:
    """Bound nodes and depth iteratively so hostile nesting cannot recurse in this walker."""
    nodes = 0
    pending: list[tuple[object, int]] = [(value, 1)]
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if nodes > MAX_NODES:
            raise ValueError("JSON structure exceeds the node limit")
        if depth > MAX_STRUCTURE_DEPTH:
            raise ValueError("JSON structure exceeds the depth limit")
        if type(current) is dict:
            pending.extend((key, depth + 1) for key in current)
            pending.extend((child, depth + 1) for child in current.values())
        elif type(current) is list:
            pending.extend((child, depth + 1) for child in current)


def _unsafe_text(value: object) -> bool:
    return type(value) is str and any(
        unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
        for character in value
    )


def _validate_corpus(raw: object) -> list[dict[str, str]]:
    if type(raw) is not dict or set(raw) != {"schema_version", "profile", "vectors"}:
        raise ValueError("corpus fields differ")
    if raw["schema_version"] != PROFILE_VERSION or raw["profile"] != (
        "maintainer-policy-declaration-structural-profile-v1"
    ):
        raise ValueError("corpus version differs")
    vectors = raw["vectors"]
    if type(vectors) is not list or not 1 <= len(vectors) <= MAX_VECTORS:
        raise ValueError("corpus vector count is outside bounds")
    expected_fields = {
        "id", "classification", "structural_profile_expectation",
        "strict_parser_expectation", "payload",
    }
    normalized: list[dict[str, str]] = []
    identifiers: set[str] = set()
    for vector in vectors:
        if type(vector) is not dict or set(vector) != expected_fields:
            raise ValueError("corpus vector fields differ")
        if any(type(value) is not str or _unsafe_text(value) for value in vector.values()):
            raise ValueError("corpus vector strings are unsafe")
        if vector["classification"] not in {"valid", "invalid", "ambiguous"}:
            raise ValueError("corpus classification differs")
        if vector["structural_profile_expectation"] not in {"accept", "reject", "ambiguous"}:
            raise ValueError("structural expectation differs")
        if vector["strict_parser_expectation"] not in {"accept", "reject"}:
            raise ValueError("strict parser expectation differs")
        if not vector["id"].replace("-", "").isalnum() or vector["id"] in identifiers:
            raise ValueError("corpus vector identifiers must be unique canonical tokens")
        if len(vector["payload"].encode("utf-8")) > MAX_PAYLOAD_BYTES:
            raise ValueError("corpus payload exceeds the byte limit")
        identifiers.add(vector["id"])
        normalized.append(dict(vector))
    _validate_structure_bounds(raw)
    return normalized


def _exercise(vectors: list[dict[str, str]]) -> tuple[list[dict[str, object]], Declaration]:
    results: list[dict[str, object]] = []
    projection_sources: list[Declaration] = []
    allowed_tuples = {
        ("valid", "accept", "accept", "accept"),
        ("invalid", "reject", "reject", "reject"),
        ("invalid", "ambiguous", "reject", "reject"),
        ("ambiguous", "accept", "reject", "reject"),
    }
    for vector in vectors:
        payload = vector["payload"].encode("utf-8")
        filename = Path(f"{vector['id']}.json")
        try:
            loose = json.loads(vector["payload"])
            if type(loose) is dict and type(loose.get("declaration_id")) is str:
                filename = Path(f"{loose['declaration_id']}.json")
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            declaration = _parse_declaration_payload(payload, filename)
            observed = "accept"
        except ValueError:
            observed = "reject"
        if observed != vector["strict_parser_expectation"]:
            raise ValueError(f"strict parser result differs for {vector['id']}")
        result_tuple = (
            vector["classification"],
            vector["structural_profile_expectation"],
            vector["strict_parser_expectation"],
            observed,
        )
        if result_tuple not in allowed_tuples:
            raise ValueError(f"classification and expectation tuple differs for {vector['id']}")
        if result_tuple == ("valid", "accept", "accept", "accept"):
            projection_sources.append(declaration)
        results.append(
            {
                "id": vector["id"],
                "classification": vector["classification"],
                "structural_profile_expectation": vector["structural_profile_expectation"],
                "strict_parser_expected": vector["strict_parser_expectation"],
                "strict_parser_observed": observed,
                "payload_sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    if len(projection_sources) != 1:
        raise ValueError("corpus must contain exactly one explicit valid projection source")
    return results, projection_sources[0]


def _projection(declaration: Declaration) -> tuple[str, str]:
    policy_lines = [
        "# AI contribution policy draft",
        "",
        "> Non-authorizing lossy projection from a structurally validated declaration.",
        "> Human review is required. This draft does not establish identity, authority, adoption,",
        "> currentness,",
        "> permission, or platform enforcement.",
        "",
        f"- Declaration: `{declaration.declaration_id}`",
        f"- Repository label: `{declaration.repository}`",
        "",
        "## Declared dimensions",
        "",
    ]
    policy_lines.extend(f"- `{key}`: `{value}`" for key, value in declaration.dimensions.items())
    policy_lines.extend(
        [
            "",
            f"- `disclosure_location`: `{declaration.disclosure_location}`",
            f"- `enforcement`: `{declaration.enforcement}`",
            "",
            "Unknown and conditional values are intentionally preserved. Provenance, notes, date,",
            "source digest, and lineage require review in the source declaration and are not",
            "converted",
            "into rules or permissions.",
        ]
    )
    pr_lines = [
        "<!-- Non-authorizing draft fragment; maintainers must review and adopt explicitly. -->",
        "## Maintainer proposals for review",
        "",
        "The declaration records disclosure, human review, and human accountability as",
        "`not_declared`; it makes no statement about whether they are required.",
        "No contributor obligation is projected from `not_declared` values.",
        "A maintainer may independently choose to add requirements after human review.",
        "",
        "Declared source values (including unknowns):",
    ]
    pr_lines.extend(f"- `{key}`: `{value}`" for key, value in declaration.dimensions.items())
    return "\n".join(policy_lines) + "\n", "\n".join(pr_lines) + "\n"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def build_artifacts(root: Path) -> dict[str, bytes]:
    static = {name: _safe_read(root / name) for name in STATIC_FILES}
    schema = _strict_json(static["schema.json"], "schema")
    if (
        type(schema) is not dict
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
    ):
        raise ValueError("schema is not the declared Draft 2020-12 profile")
    _validate_structure_bounds(schema)
    vectors = _validate_corpus(_strict_json(static["corpus.json"], "corpus"))
    results, declaration = _exercise(vectors)
    policy, pr_fragment = _projection(declaration)
    artifacts: dict[str, bytes] = {
        "AI_POLICY.draft.md": policy.encode("utf-8"),
        "PULL_REQUEST_TEMPLATE.fragment.md": pr_fragment.encode("utf-8"),
    }
    manifest = {
        "schema_version": PROFILE_VERSION,
        "component": {
            "name": "maintainer-policy-declaration-interop",
            "version": COMPONENT_VERSION,
        },
        "profile": "JSON Schema Draft 2020-12 structural profile",
        "authoritative_validator": "patch_cabinet.maintainer_policy_declaration",
        "independent_json_schema_validator_tested": False,
        "claim_boundary": BOUNDARY,
        "files": [
            {"path": name, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
            for name, payload in sorted({**static, **artifacts}.items())
        ],
    }
    artifacts["manifest.json"] = _json_bytes(manifest)
    receipt = {
        "schema_version": PROFILE_VERSION,
        "component": manifest["component"],
        "result": "corpus_matches_authoritative_parser_expectations",
        "independent_json_schema_validator_tested": False,
        "claim_boundary": BOUNDARY,
        "schema_sha256": hashlib.sha256(static["schema.json"]).hexdigest(),
        "corpus_sha256": hashlib.sha256(static["corpus.json"]).hexdigest(),
        "manifest_sha256": hashlib.sha256(artifacts["manifest.json"]).hexdigest(),
        "vectors": results,
    }
    artifacts["validation-receipt.json"] = _json_bytes(receipt)
    return artifacts


def _write_atomic(project: Path, root: Path, path: Path, payload: bytes) -> None:
    _check_directory_chain(project, root)
    if path.exists():
        inspected = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1:
            raise ValueError("existing generated output must be a single-link regular file")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _check_directory_chain(project, root)
        if path.exists():
            inspected = path.lstat()
            if path.is_symlink() or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1:
                raise ValueError("generated output changed before replacement")
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def run(project: Path, check: bool) -> dict[str, object]:
    project = project.absolute()
    root = project / "interop" / "maintainer-policy-declaration" / "v1"
    _check_root(project, root, check=check)
    artifacts = build_artifacts(root)
    if check:
        for name, payload in artifacts.items():
            if _safe_read(root / name) != payload:
                raise ValueError(f"generated interop artifact is stale: {name}")
    else:
        _check_outputs(root)
        for name, payload in artifacts.items():
            _write_atomic(project, root, root / name, payload)
    return json.loads(artifacts["validation-receipt.json"])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m patch_cabinet.declaration_interop")
    parser.add_argument("--project", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run(Path(args.project), args.check), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
