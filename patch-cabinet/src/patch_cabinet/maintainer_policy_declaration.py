"""Strict offline cards for unauthenticated trusted-local policy declarations."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import stat
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence


COMPONENT_VERSION = "0.2.0"
SCHEMA_VERSION = "1"
MAX_FILE_BYTES = 65_536
MAX_RECORDS = 100
MAX_JSON_DEPTH = 12
MAX_TEXT_CHARS = 500
SYNTHETIC_REPOSITORY = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?/"
    r"[a-z0-9](?:[a-z0-9.-]{0,97}[a-z0-9])?$"
)
GITHUB_REPOSITORY = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?/"
    r"[A-Za-z0-9_.-]{1,100}$"
)
COMMIT = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
DECLARATION_ID = re.compile(r"^mpd-v1-[0-9a-f]{64}$")
POLICY_PATH = re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
RECORD_BASES = {
    "synthetic_example": "synthetic_example_not_a_maintainer_assertion",
    "unverified_project_declaration": "trusted_local_operator_supplied_unverified_declaration",
}
POLICY_VALUES = {"allowed", "conditional", "disallowed", "not_declared"}
EXPECTATION_VALUES = {"required", "recommended", "not_declared"}
DIMENSION_VOCABULARIES = {
    "ai_assisted_code": POLICY_VALUES,
    "ai_assisted_documentation": POLICY_VALUES,
    "ai_authored_issue_text": POLICY_VALUES,
    "ai_authored_pr_text": POLICY_VALUES,
    "autonomous_issue_submission": POLICY_VALUES,
    "autonomous_pr_submission": POLICY_VALUES,
    "automated_review_comments": POLICY_VALUES,
    "good_first_issue_automation": POLICY_VALUES,
    "security_report_automation": POLICY_VALUES,
    "disclosure": EXPECTATION_VALUES,
    "human_review": EXPECTATION_VALUES,
    "human_accountability": EXPECTATION_VALUES,
    "license_ip_checks": EXPECTATION_VALUES,
}
DISCLOSURE_LOCATIONS = {
    "pr_description",
    "commit_trailer",
    "either",
    "project_defined",
    "not_declared",
}
ENFORCEMENT_VALUES = {
    "close_or_reject",
    "request_changes",
    "label_or_flag",
    "maintainer_discretion",
    "not_declared",
}
EXPECTED_FIELDS = {
    "schema_version",
    "declaration_id",
    "record_kind",
    "assertion_basis",
    "repository",
    "repository_url",
    "commit_sha",
    "policy_source_url",
    "policy_path",
    "source_sha256",
    "observed_at",
    "dimensions",
    "disclosure_location",
    "enforcement",
    "supersedes",
    "notes",
}
CLAIM_BOUNDARY = (
    "Structural validation only. Project records are maintainer- or operator-supplied and "
    "unauthenticated/unverified. Validation does not verify supplier identity or authority, "
    "assertions, source truth, authorship, repository ownership, current policy, or permission "
    "to contact or submit."
)


@dataclass(frozen=True)
class Declaration:
    declaration_id: str
    record_kind: str
    assertion_basis: str
    repository: str
    repository_url: str
    commit_sha: str
    policy_source_url: str
    policy_path: str
    source_sha256: str
    observed_at: date
    dimensions: dict[str, str]
    disclosure_location: str
    enforcement: str
    supersedes: str | None
    notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "declaration_id": self.declaration_id,
            "record_kind": self.record_kind,
            "assertion_basis": self.assertion_basis,
            "repository": self.repository,
            "repository_url": self.repository_url,
            "commit_sha": self.commit_sha,
            "policy_source_url": self.policy_source_url,
            "policy_path": self.policy_path,
            "source_sha256": self.source_sha256,
            "observed_at": self.observed_at.isoformat(),
            "dimensions": dict(self.dimensions),
            "disclosure_location": self.disclosure_location,
            "enforcement": self.enforcement,
            "supersedes": self.supersedes,
            "notes": self.notes,
        }


def _reject_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key is not allowed")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant is not allowed")


def _reject_number(_value: str) -> object:
    raise ValueError("JSON numbers are not part of the declaration schema")


def _validate_json_depth(text: str) -> None:
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
            continue
        if character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise ValueError(f"JSON nesting exceeds the {MAX_JSON_DEPTH}-level limit")
        elif character in "]}":
            depth -= 1


def _unsafe_directory(path: Path, inspected: os.stat_result) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(inspected, "st_file_attributes", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def _safe_read(path: Path) -> bytes:
    try:
        before = path.lstat()
    except OSError as error:
        raise ValueError("declaration cannot be inspected") from error
    if path.is_symlink() or not stat.S_ISREG(before.st_mode):
        raise ValueError("declarations must be nonsymlink regular files")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError("declaration cannot be opened safely") from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("declaration changed during safe open")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError(f"declaration exceeds {MAX_FILE_BYTES} bytes")
    return payload


def _reject_unsafe_strings(value: object) -> None:
    if type(value) is str and any(
        unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"} for character in value
    ):
        raise ValueError("declaration contains unsafe control or formatting characters")
    if type(value) is dict:
        for key, child in value.items():
            _reject_unsafe_strings(key)
            _reject_unsafe_strings(child)
    elif type(value) is list:
        for child in value:
            _reject_unsafe_strings(child)


def _plain_text(value: object, field: str) -> str:
    if type(value) is not str or not value.strip() or len(value) > MAX_TEXT_CHARS:
        raise ValueError(f"{field} must be a nonempty bounded string")
    if value != value.strip():
        raise ValueError(f"{field} cannot have surrounding whitespace")
    return value


def _parse_date(value: object) -> date:
    if type(value) is not str:
        raise ValueError("observed_at must be a canonical local date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("observed_at must be a canonical local date") from error
    if parsed.isoformat() != value or parsed > date.today():
        raise ValueError("observed_at must be a non-future canonical local date")
    return parsed


def expected_declaration_id(
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


def _parse_declaration(raw: dict[str, Any]) -> Declaration:
    if set(raw) != EXPECTED_FIELDS or raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("declaration fields or schema version differ")
    _reject_unsafe_strings(raw)
    record_kind = raw["record_kind"]
    if type(record_kind) is not str or record_kind not in RECORD_BASES:
        raise ValueError("record_kind is outside the controlled vocabulary")
    if raw["assertion_basis"] != RECORD_BASES[record_kind]:
        raise ValueError("assertion_basis does not match record_kind")
    repository = raw["repository"]
    commit_sha = raw["commit_sha"]
    source_sha256 = raw["source_sha256"]
    repository_pattern = (
        SYNTHETIC_REPOSITORY
        if record_kind == "synthetic_example"
        else GITHUB_REPOSITORY
    )
    if type(repository) is not str or repository_pattern.fullmatch(repository) is None:
        raise ValueError("repository is outside the record-kind-specific owner/name grammar")
    if record_kind == "unverified_project_declaration":
        owner, name = repository.split("/", 1)
        if "--" in owner or name in {".", ".."}:
            raise ValueError("repository is outside canonical GitHub owner/name limits")
    if type(commit_sha) is not str or COMMIT.fullmatch(commit_sha) is None:
        raise ValueError("commit_sha must be 40 lowercase hexadecimal characters")
    if type(source_sha256) is not str or DIGEST.fullmatch(source_sha256) is None:
        raise ValueError("source_sha256 must be 64 lowercase hexadecimal characters")
    if source_sha256 == "0" * 64:
        raise ValueError("source_sha256 cannot use the null digest sentinel")
    policy_path = raw["policy_path"]
    if (
        type(policy_path) is not str
        or len(policy_path) > 300
        or POLICY_PATH.fullmatch(policy_path) is None
        or any(part in {"", ".", ".."} for part in policy_path.split("/"))
    ):
        raise ValueError("policy_path must be a canonical ASCII repository-relative path")
    declaration_id = raw["declaration_id"]
    expected_id = expected_declaration_id(
        repository, record_kind, commit_sha, policy_path, source_sha256
    )
    if (
        type(declaration_id) is not str
        or DECLARATION_ID.fullmatch(declaration_id) is None
        or declaration_id != expected_id
    ):
        raise ValueError("declaration_id does not match the canonical identity")
    repository_url = raw["repository_url"]
    if record_kind == "synthetic_example":
        expected_repository_url = f"https://example.invalid/{repository}"
        expected_url = (
            f"https://example.invalid/{repository}/blob/{commit_sha}/{policy_path}"
        )
    else:
        expected_repository_url = f"https://github.com/{repository}"
        expected_url = f"https://github.com/{repository}/blob/{commit_sha}/{policy_path}"
    if repository_url != expected_repository_url:
        raise ValueError("repository_url does not match the record-kind-specific canonical URL")
    source_url = raw["policy_source_url"]
    if type(source_url) is not str or source_url != expected_url:
        raise ValueError(
            "policy_source_url must match the record-kind-specific repository, commit, and path"
        )
    if any(value in source_url for value in ("%", "\\", "?", "#")):
        raise ValueError("policy_source_url contains a noncanonical component")
    dimensions = raw["dimensions"]
    if type(dimensions) is not dict or set(dimensions) != set(DIMENSION_VOCABULARIES):
        raise ValueError("dimensions must contain exactly the defined dimensions")
    normalized: dict[str, str] = {}
    for name in DIMENSION_VOCABULARIES:
        value = dimensions[name]
        if type(value) is not str or value not in DIMENSION_VOCABULARIES[name]:
            raise ValueError(f"{name} is outside its controlled vocabulary")
        normalized[name] = value
    disclosure_location = raw["disclosure_location"]
    if type(disclosure_location) is not str or disclosure_location not in DISCLOSURE_LOCATIONS:
        raise ValueError("disclosure_location is outside the controlled vocabulary")
    disclosure = normalized["disclosure"]
    if (disclosure == "not_declared") != (disclosure_location == "not_declared"):
        raise ValueError("disclosure and disclosure_location must be declared together")
    enforcement = raw["enforcement"]
    if type(enforcement) is not str or enforcement not in ENFORCEMENT_VALUES:
        raise ValueError("enforcement is outside the controlled vocabulary")
    supersedes = raw["supersedes"]
    if supersedes is not None and (
        type(supersedes) is not str or DECLARATION_ID.fullmatch(supersedes) is None
    ):
        raise ValueError("supersedes must be null or a canonical declaration_id")
    return Declaration(
        declaration_id=declaration_id,
        record_kind=record_kind,
        assertion_basis=raw["assertion_basis"],
        repository=repository,
        repository_url=repository_url,
        commit_sha=commit_sha,
        policy_source_url=source_url,
        policy_path=policy_path,
        source_sha256=source_sha256,
        observed_at=_parse_date(raw["observed_at"]),
        dimensions=normalized,
        disclosure_location=disclosure_location,
        enforcement=enforcement,
        supersedes=supersedes,
        notes=_plain_text(raw["notes"], "notes"),
    )


def _parse_declaration_payload(payload: bytes, path: Path) -> Declaration:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("declarations must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("declarations cannot contain a UTF-8 BOM")
    try:
        _validate_json_depth(text)
        raw = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=_reject_constant,
            parse_float=_reject_number,
            parse_int=_reject_number,
        )
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        raise ValueError("declaration is not valid strict JSON") from error
    if type(raw) is not dict:
        raise ValueError("declaration must be a JSON object")
    declaration = _parse_declaration(raw)
    if path.name != f"{declaration.declaration_id}.json":
        raise ValueError("declaration filename must equal its canonical declaration_id")
    return declaration


def _load_declaration_with_payload(path: Path) -> tuple[Declaration, bytes]:
    payload = _safe_read(path)
    return _parse_declaration_payload(payload, path), payload


def _load_declaration(path: Path) -> Declaration:
    declaration, _payload = _load_declaration_with_payload(path)
    return declaration


def build_validation_receipt(path: Path) -> dict[str, object]:
    declaration, payload = _load_declaration_with_payload(path)
    return {
        "schema_version": SCHEMA_VERSION,
        "component": {"name": "maintainer-policy-declaration", "version": COMPONENT_VERSION},
        "result": "structurally_valid",
        "claim_boundary": (
            CLAIM_BOUNDARY
            + " The record_file_sha256 is only a recomputable file fingerprint; it is not a "
            "signature, authentication, authorization, identity, currentness, or permission claim."
        ),
        "declaration": {
            "declaration_id": declaration.declaration_id,
            "record_kind": declaration.record_kind,
            "assertion_basis": declaration.assertion_basis,
            "repository": declaration.repository,
            "observed_at": declaration.observed_at.isoformat(),
            "source_sha256": declaration.source_sha256,
            "record_file_sha256": hashlib.sha256(payload).hexdigest(),
            "record_file_sha256_label": "recomputable_fingerprint_only",
        },
    }


def load_declarations(directory: Path) -> list[Declaration]:
    try:
        inspected = directory.lstat()
    except OSError as error:
        raise ValueError("declaration directory cannot be inspected") from error
    if _unsafe_directory(directory, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("declaration input must be a non-link regular directory")
    paths: list[Path] = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if len(paths) >= MAX_RECORDS:
                raise ValueError(f"catalog exceeds the {MAX_RECORDS}-record limit")
            path = Path(entry.path)
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise ValueError("directory can contain only regular JSON declarations")
            if path.suffix != ".json":
                raise ValueError("directory can contain only .json declarations")
            paths.append(path)
    if not paths:
        raise ValueError("declaration catalog must contain at least one record")
    records = [_load_declaration(path) for path in sorted(paths, key=lambda item: item.name)]
    by_id = {record.declaration_id: record for record in records}
    if len(by_id) != len(records):
        raise ValueError("declaration_id values must be unique")
    identities = [
        (
            item.repository.casefold(),
            item.record_kind,
            item.commit_sha,
            item.policy_path,
            item.source_sha256,
        )
        for item in records
    ]
    if len(identities) != len(set(identities)):
        raise ValueError("each exact declaration identity can occur only once")
    successor_counts: dict[str, int] = {}
    for record in records:
        if record.supersedes is None:
            continue
        if record.supersedes == record.declaration_id or record.supersedes not in by_id:
            raise ValueError("supersedes must reference a different declaration")
        previous = by_id[record.supersedes]
        if (
            previous.repository.casefold() != record.repository.casefold()
            or previous.policy_path != record.policy_path
            or previous.record_kind != record.record_kind
            or previous.assertion_basis != record.assertion_basis
            or record.observed_at <= previous.observed_at
        ):
            raise ValueError("successor must preserve lineage and use a later observation date")
        successor_counts[record.supersedes] = successor_counts.get(record.supersedes, 0) + 1
        if successor_counts[record.supersedes] > 1:
            raise ValueError("a declaration cannot have multiple direct successors")
    for record in records:
        seen: set[str] = set()
        current = record
        while current.supersedes is not None:
            if current.declaration_id in seen:
                raise ValueError("declaration supersession cycle detected")
            seen.add(current.declaration_id)
            current = by_id[current.supersedes]
    return sorted(records, key=lambda item: (item.repository.casefold(), item.declaration_id))


def build_index(records: list[Declaration]) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "component": {"name": "maintainer-policy-declaration", "version": COMPONENT_VERSION},
        "claim_boundary": CLAIM_BOUNDARY,
        "summary": {"records": len(records)},
        "records": [record.to_dict() for record in records],
    }


def _code(value: object) -> str:
    return f"<code>{html.escape(str(value), quote=True)}</code>"


def _inert_code(value: object) -> str:
    encoded = "".join(f"&#x{ord(character):x};" for character in str(value))
    return f"<code>{encoded}</code>"


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Maintainer policy declaration cards",
        "",
        f"> {html.escape(str(report['claim_boundary']))}",
        "",
        f"- Component: {_code(report['component']['name'] + ' ' + report['component']['version'])}",
        f"- Structurally validated records: {report['summary']['records']}",
        "",
    ]
    for record in report["records"]:
        lines.extend(
            [
                f"## {_code(record['repository'])}",
                "",
                f"- Record kind: {_code(record['record_kind'])}",
                f"- Assertion basis: {_code(record['assertion_basis'])}",
                f"- Declaration: {_code(record['declaration_id'])}",
                f"- Observed: {_code(record['observed_at'])}",
                (
                    f"- Synthetic source: {_inert_code(record['policy_source_url'])}"
                    if record["record_kind"] == "synthetic_example"
                    else "- Pinned source: "
                    f"[source]({html.escape(record['policy_source_url'], quote=True)})"
                ),
                f"- Disclosure location: {_code(record['disclosure_location'])}",
                f"- Enforcement: {_code(record['enforcement'])}",
                "",
                "| Dimension | Declared value |",
                "|---|---|",
            ]
        )
        for name in DIMENSION_VOCABULARIES:
            lines.append(f"| {_code(name)} | {_code(record['dimensions'][name])} |")
        lines.extend(["", f"- Notes: {_inert_code(record['notes'])}", ""])
    return "\n".join(lines).rstrip() + "\n"


def starter_template(record_kind: str) -> dict[str, object]:
    if record_kind not in RECORD_BASES:
        raise ValueError("starter record_kind is outside the controlled vocabulary")
    synthetic = record_kind == "synthetic_example"
    return {
        "schema_version": SCHEMA_VERSION,
        "declaration_id": "<replace-with-derived-declaration-id>",
        "record_kind": record_kind,
        "assertion_basis": RECORD_BASES[record_kind],
        "repository": "<owner/repository>",
        "repository_url": (
            "<https://example.invalid/owner/repository>"
            if synthetic
            else "<https://github.com/owner/repository>"
        ),
        "commit_sha": "<40-lowercase-hex-commit>",
        "policy_source_url": (
            "<https://example.invalid/owner/repository/blob/commit/path>"
            if synthetic
            else "<https://github.com/owner/repository/blob/commit/path>"
        ),
        "policy_path": "<repository-relative-policy-path>",
        "source_sha256": "<64-lowercase-hex-source-digest>",
        "observed_at": "<YYYY-MM-DD-local-date>",
        "dimensions": {
            name: f"<{'|'.join(sorted(values))}>"
            for name, values in DIMENSION_VOCABULARIES.items()
        },
        "disclosure_location": f"<{'|'.join(sorted(DISCLOSURE_LOCATIONS))}>",
        "enforcement": f"<{'|'.join(sorted(ENFORCEMENT_VALUES))}>",
        "supersedes": None,
        "notes": (
            "Starter only; not structurally validated until every placeholder is replaced. "
            "See MAINTAINER_POLICY_DECLARATION.md for field rules."
        ),
    }


def render_starter(record_kind: str) -> str:
    return json.dumps(starter_template(record_kind), indent=2) + "\n"


def _write_atomic(destination: Path, content: str) -> None:
    # Output parents are trusted local filesystems. Atomic replacement limits partial output but
    # does not claim resistance to adversarial parent replacement between validation and writing.
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


def _assert_output_paths(directory: Path, outputs: list[Path]) -> None:
    resolved_directory = directory.resolve(strict=True)
    resolved_outputs = [path.resolve(strict=False) for path in outputs]
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise ValueError("JSON and Markdown outputs must use different paths")
    if any(path.is_relative_to(resolved_directory) for path in resolved_outputs):
        raise ValueError("outputs cannot be written inside the declaration directory")
    input_inodes = {
        (inspected.st_dev, inspected.st_ino)
        for inspected in (path.lstat() for path in directory.iterdir())
    }
    output_inodes: set[tuple[int, int]] = set()
    for output in outputs:
        if not output.exists():
            continue
        inspected = output.lstat()
        is_junction = getattr(output, "is_junction", None)
        if (
            output.is_symlink()
            or (callable(is_junction) and is_junction())
            or not stat.S_ISREG(inspected.st_mode)
        ):
            raise ValueError("existing output must be a non-link regular file")
        identity = (inspected.st_dev, inspected.st_ino)
        if identity in input_inodes:
            raise ValueError("output path aliases a declaration input")
        if identity in output_inodes:
            raise ValueError("output paths cannot hardlink the same file")
        output_inodes.add(identity)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="maintainer-policy-declaration")
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render", help="render an explicit declaration directory")
    render.add_argument("records", help="directory containing declaration JSON files")
    render.add_argument("--json-out", help="write the deterministic JSON index")
    render.add_argument("--markdown-out", help="write the deterministic Markdown cards")
    starter = subparsers.add_parser(
        "starter", help="print an unvalidated deterministic starter template"
    )
    starter.add_argument("record_kind", choices=tuple(RECORD_BASES))
    validate = subparsers.add_parser(
        "validate", help="validate exactly one declaration and print a structural receipt"
    )
    validate.add_argument("record_file", help="one declaration JSON file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "starter":
        print(render_starter(args.record_kind), end="")
        return 0
    if args.command == "validate":
        receipt = build_validation_receipt(Path(args.record_file))
        print(json.dumps(receipt, indent=2) + "\n", end="")
        return 0
    directory = Path(args.records)
    outputs = [Path(value) for value in (args.json_out, args.markdown_out) if value]
    records = load_declarations(directory)
    _assert_output_paths(directory, outputs)
    report = build_index(records)
    serialized = json.dumps(report, indent=2) + "\n"
    if args.json_out:
        _write_atomic(Path(args.json_out), serialized)
    if args.markdown_out:
        _write_atomic(Path(args.markdown_out), render_markdown(report))
    if not outputs:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
