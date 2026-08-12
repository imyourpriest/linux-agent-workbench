"""Strict offline verifier for the bounded synthetic policy-starter pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
import unicodedata
from pathlib import Path
from typing import Sequence


COMPONENT_VERSION = "0.1.0"
MAX_FILE_BYTES = 65_536
MAX_TOTAL_BYTES = 262_144
MAX_FILES = 9
MAX_JSON_DEPTH = 12
DIGEST = re.compile(r"^[0-9a-f]{64}$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,119}$")
MANIFEST_FIELDS = {
    "schema_version",
    "pack_id",
    "status",
    "provenance",
    "price_hypothesis",
    "boundaries",
    "inventory",
}
BOUNDARY_FIELDS = {
    "synthetic_only",
    "activated",
    "accepts_private_input",
    "identity_or_authority_verified",
    "legal_advice",
    "ai_use_detection",
    "compliance_or_certification",
    "enforcement_guarantee",
    "payment_or_checkout",
}
CLAIM_BOUNDARY = (
    "Structural and hash-consistency validation of a bounded reserved example.invalid synthetic "
    "pack only. Manifest and file SHA-256 values are recomputable consistency fingerprints, not "
    "signatures, authentication, authorization, identity, ownership, policy adoption or "
    "currentness, legal advice, AI-use detection, compliance, enforcement, safety, payment, "
    "customer, demand, or production-readiness evidence. The verifier-owned canonical SHA-256 "
    "constants bind this checked-tree example only; they are not signatures or an external trust "
    "anchor."
)
CANONICAL_REPOSITORY = "reserved/policy-starter"
CANONICAL_RECORD_KIND = "synthetic_example"
CANONICAL_COMMIT_SHA = "1" * 40
CANONICAL_POLICY_PATH = "CONTRIBUTING.md"
CANONICAL_CONTRIBUTING_SHA256 = (
    "6ec40971a70a44c550f485719d06c57b8520e89a2c4468247830b35b69ae28bd"
)


def _derive_declaration_id(
    repository: str,
    record_kind: str,
    commit_sha: str,
    policy_path: str,
    source_sha256: str,
) -> str:
    identity = "\0".join(
        ("mpd-v1", repository.casefold(), record_kind, commit_sha, policy_path, source_sha256)
    )
    return f"mpd-v1-{hashlib.sha256(identity.encode('utf-8')).hexdigest()}"


DECLARATION_ID = _derive_declaration_id(
    CANONICAL_REPOSITORY,
    CANONICAL_RECORD_KIND,
    CANONICAL_COMMIT_SHA,
    CANONICAL_POLICY_PATH,
    CANONICAL_CONTRIBUTING_SHA256,
)
DECLARATION_NAME = f"{DECLARATION_ID}.json"
EXPECTED_CONTENT_SHA256 = {
    "ASYNC_HANDOFF.md": "3e14b80b1954091b7e7631d6d75b5da731506546ef46de1fa951a2bc9dd7a24b",
    "AUDIT.md": "aa508d6b54a10bf69ab2ea4c1495b658b57a170ba71ea340cd9f55bd220d9acc",
    "CONTRIBUTING.md": CANONICAL_CONTRIBUTING_SHA256,
    "DECISION_MATRIX.md": "4ba802ef135cc38396b0deb89e64c5045f1ec826964efb9d8bbf44ce54be2430",
    "ISSUE_PR_CHECKLIST.md": (
        "7bcb5c45de7cfe54adf285b93d6f4825cd476bb4e6c308773176d6f44d6ab066"
    ),
    "README.md": "182f03509fa6641e7f7a0ac9a22c0a7505e2399a75364fdf3e549e526f8ff3f0",
    "SCOPE.md": "5cd975948e37da195a679c5d4eda33597a838deddb99c2491b78644286fbbff8",
    DECLARATION_NAME: "19f5af9b1897e771742f36f10adff74f7406ed92b2a26f46ee91d70bef044e3d",
}
EXPECTED_CONTENT = set(EXPECTED_CONTENT_SHA256)
EXPECTED_FILES = EXPECTED_CONTENT | {"manifest.json"}


def _duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key is not allowed")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant is not allowed")


def _reject_number(_value: str) -> object:
    raise ValueError("JSON numbers are not part of the pack schema")


def _validate_depth(text: str) -> None:
    depth = 0
    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise ValueError("JSON nesting exceeds the bounded limit")
        elif character in "]}":
            depth -= 1


def _unsafe_path(path: Path, inspected: os.stat_result) -> bool:
    is_junction = getattr(path, "is_junction", None)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(inspected, "st_file_attributes", 0)
    return (
        path.is_symlink()
        or (callable(is_junction) and is_junction())
        or bool(reparse and attributes & reparse)
    )


def _safe_read(path: Path) -> bytes:
    try:
        before = path.lstat()
    except OSError as error:
        raise ValueError("pack file cannot be inspected") from error
    if _unsafe_path(path, before) or not stat.S_ISREG(before.st_mode):
        raise ValueError("pack entries must be non-link regular files")
    if before.st_nlink != 1:
        raise ValueError("pack entries cannot have hard-link aliases")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError("pack file cannot be opened safely") from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("pack file changed or aliases another file")
        chunks: list[bytes] = []
        remaining = MAX_FILE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("pack file exceeds the per-file byte limit")
    return payload


def _safe_text(payload: bytes) -> str:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("pack files must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("pack files cannot contain a UTF-8 BOM")
    if any(
        unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
        and character != "\n"
        for character in text
    ):
        raise ValueError("pack contains unsafe control, bidi, or formatting characters")
    return text


def _strict_json(payload: bytes) -> object:
    text = _safe_text(payload)
    _validate_depth(text)
    try:
        return json.loads(
            text,
            object_pairs_hook=_duplicate_object,
            parse_constant=_reject_constant,
            parse_float=_reject_number,
            parse_int=_reject_number,
        )
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        raise ValueError("pack JSON is not valid strict JSON") from error


def _validate_manifest(raw: object) -> list[dict[str, str]]:
    if type(raw) is not dict or set(raw) != MANIFEST_FIELDS:
        raise ValueError("manifest fields differ from the strict schema")
    exact = {
        "schema_version": "1",
        "pack_id": "policy-starter-synthetic-v1",
        "status": "non_activated_synthetic_hypothesis",
        "provenance": "reserved_example_invalid_only",
        "price_hypothesis": "$79_unvalidated_hypothesis",
    }
    if any(raw.get(name) != value for name, value in exact.items()):
        raise ValueError("manifest identity, provenance, status, or price hypothesis differs")
    boundaries = raw["boundaries"]
    if type(boundaries) is not dict or set(boundaries) != BOUNDARY_FIELDS:
        raise ValueError("manifest boundaries differ from the strict schema")
    for name in BOUNDARY_FIELDS:
        expected = name == "synthetic_only"
        if type(boundaries[name]) is not bool or boundaries[name] is not expected:
            raise ValueError("manifest boundary booleans cannot be relaxed or imitated")
    inventory = raw["inventory"]
    if type(inventory) is not list or len(inventory) != len(EXPECTED_CONTENT):
        raise ValueError("manifest inventory count differs")
    normalized: list[dict[str, str]] = []
    for item in inventory:
        if type(item) is not dict or set(item) != {"path", "sha256"}:
            raise ValueError("inventory item fields differ")
        path, digest = item["path"], item["sha256"]
        if (
            type(path) is not str
            or SAFE_NAME.fullmatch(path) is None
            or "/" in path
            or "\\" in path
            or path in {".", ".."}
        ):
            raise ValueError("inventory paths must be single canonical ASCII filenames")
        if type(digest) is not str or DIGEST.fullmatch(digest) is None:
            raise ValueError("inventory SHA-256 is not canonical")
        normalized.append({"path": path, "sha256": digest})
    names = [item["path"] for item in normalized]
    if names != sorted(EXPECTED_CONTENT) or len(names) != len(set(names)):
        raise ValueError("manifest inventory must be the exact sorted bounded inventory")
    for item in normalized:
        if item["sha256"] != EXPECTED_CONTENT_SHA256[item["path"]]:
            raise ValueError("manifest digest differs from the verifier-owned canonical digest")
    return normalized


def _validate_declaration(raw: object, contributing_digest: str) -> None:
    if type(raw) is not dict:
        raise ValueError("declaration must be an object")
    required = {
        "schema_version", "declaration_id", "record_kind", "assertion_basis", "repository",
        "repository_url", "commit_sha", "policy_source_url", "policy_path", "source_sha256",
        "observed_at", "dimensions", "disclosure_location", "enforcement", "supersedes", "notes",
    }
    if set(raw) != required:
        raise ValueError("declaration fields differ")
    expected = {
        "schema_version": "1",
        "record_kind": CANONICAL_RECORD_KIND,
        "assertion_basis": "synthetic_example_not_a_maintainer_assertion",
        "repository": CANONICAL_REPOSITORY,
        "repository_url": "https://example.invalid/reserved/policy-starter",
        "commit_sha": CANONICAL_COMMIT_SHA,
        "policy_source_url": (
            "https://example.invalid/reserved/policy-starter/blob/"
            + CANONICAL_COMMIT_SHA
            + "/CONTRIBUTING.md"
        ),
        "policy_path": CANONICAL_POLICY_PATH,
        "source_sha256": contributing_digest,
        "observed_at": "2026-08-12",
        "supersedes": None,
        "disclosure_location": "pr_description",
        "enforcement": "maintainer_discretion",
        "notes": (
            "Reserved example.invalid fixture for structural testing; not an adopted policy or "
            "maintainer assertion."
        ),
    }
    if any(raw.get(name) != value for name, value in expected.items()):
        raise ValueError("declaration is not the reserved synthetic record")
    derived_id = _derive_declaration_id(
        raw["repository"],
        raw["record_kind"],
        raw["commit_sha"],
        raw["policy_path"],
        raw["source_sha256"],
    )
    if raw.get("declaration_id") != derived_id or derived_id != DECLARATION_ID:
        raise ValueError("declaration_id does not match its canonical semantic payload")
    if "example.invalid" not in raw.get("policy_source_url", ""):
        raise ValueError("declaration source must use reserved synthetic provenance")
    expected_dimensions = {
        "ai_assisted_code": "conditional",
        "ai_assisted_documentation": "conditional",
        "ai_authored_issue_text": "conditional",
        "ai_authored_pr_text": "conditional",
        "autonomous_issue_submission": "not_declared",
        "autonomous_pr_submission": "not_declared",
        "automated_review_comments": "not_declared",
        "good_first_issue_automation": "not_declared",
        "security_report_automation": "disallowed",
        "disclosure": "required",
        "human_review": "required",
        "human_accountability": "required",
        "license_ip_checks": "required",
    }
    if raw.get("dimensions") != expected_dimensions:
        raise ValueError("declaration dimensions differ from the reserved synthetic record")


def validate_pack(directory: Path) -> dict[str, object]:
    try:
        inspected = directory.lstat()
    except OSError as error:
        raise ValueError("pack directory cannot be inspected") from error
    if _unsafe_path(directory, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("pack input must be a non-link regular directory")
    entries: list[Path] = []
    with os.scandir(directory) as scanned:
        for entry in scanned:
            if len(entries) >= MAX_FILES:
                raise ValueError("pack exceeds the exact file-count limit")
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise ValueError("pack cannot contain subdirectories or non-files")
            entries.append(Path(entry.path))
    names = {path.name for path in entries}
    if names != EXPECTED_FILES or len(entries) != MAX_FILES:
        raise ValueError("pack contains missing or unexpected files")
    payloads = {path.name: _safe_read(path) for path in entries}
    if sum(map(len, payloads.values())) > MAX_TOTAL_BYTES:
        raise ValueError("pack exceeds the total byte limit")
    for name, payload in payloads.items():
        if name.endswith(".md"):
            _safe_text(payload)
    inventory = _validate_manifest(_strict_json(payloads["manifest.json"]))
    actual = {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()}
    for item in inventory:
        if actual[item["path"]] != item["sha256"]:
            raise ValueError("manifest file SHA-256 does not match the safe-open payload")
        if actual[item["path"]] != EXPECTED_CONTENT_SHA256[item["path"]]:
            raise ValueError("safe-open payload differs from the verifier-owned canonical file")
    _validate_declaration(
        _strict_json(payloads[DECLARATION_NAME]), actual["CONTRIBUTING.md"]
    )
    return {
        "schema_version": "1",
        "component": {"name": "policy-starter-pack-verifier", "version": COMPONENT_VERSION},
        "result": "structurally_valid_synthetic_pack",
        "claim_boundary": CLAIM_BOUNDARY,
        "pack_id": "policy-starter-synthetic-v1",
        "status": "non_activated_synthetic_hypothesis",
        "canonical_binding": "verifier_owned_checked_tree_sha256_constants",
        "manifest_sha256": actual["manifest.json"],
        "manifest_sha256_label": "recomputable_consistency_fingerprint_only",
        "files": [
            {
                "path": item["path"],
                "sha256": actual[item["path"]],
                "sha256_label": "recomputable_consistency_fingerprint_only",
            }
            for item in inventory
        ],
        "boundaries": {
            "activated": False,
            "payment_or_checkout": False,
            "private_input": False,
            "identity_or_authority_verified": False,
            "legal_or_compliance_result": False,
            "ai_use_detection": False,
            "enforcement_guarantee": False,
        },
    }


def _write_atomic(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m support_eval_lab.policy_starter")
    parser.add_argument("pack", nargs="?", default="policy-starter")
    parser.add_argument("--json-out")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    directory = Path(args.pack)
    if args.json_out:
        output = Path(args.json_out)
        if output.resolve(strict=False).is_relative_to(directory.resolve(strict=True)):
            raise ValueError("receipt output cannot be inside the verified pack")
    serialized = json.dumps(validate_pack(directory), indent=2) + "\n"
    if args.json_out:
        _write_atomic(Path(args.json_out), serialized)
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
