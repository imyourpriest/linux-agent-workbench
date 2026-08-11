"""Strict offline index for manually reviewed upstream contribution policies."""

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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence


CATALOG_COMPONENT_VERSION = "0.1.0"
CATALOG_SCHEMA_VERSION = "1"
MAX_FILE_BYTES = 65_536
MAX_RECORDS = 100
MAX_JSON_DEPTH = 12
MAX_NOTE_CHARS = 400
MAX_RECEIPT_BYTES = 262_144
MAX_RECEIPT_SOURCES = 100
MAX_SOURCE_BYTES = 10_000_000
REPOSITORY = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?/"
    r"[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?$"
)
COMMIT = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
RECORD_ID = re.compile(r"^github-[a-z0-9-]{1,150}-[0-9a-f]{12}-[0-9a-f]{12}$")
POLICY_PATH = re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
CLASSIFICATIONS = {
    "explicitly_allows",
    "explicitly_disallows",
    "insufficiently_explicit",
}
WORKFLOW_SCOPE = "agent_selects_prepares_and_submits_with_disclosure"
CLAIM_BOUNDARY = (
    "Pinned historical manual reviews; not current permission, automatic interpretation, "
    "candidate eligibility, or authorization to contact or submit upstream."
)
EXPECTED_FIELDS = {
    "schema_version",
    "record_id",
    "repository",
    "repository_url",
    "commit_sha",
    "policy_source_url",
    "policy_path",
    "source_sha256",
    "observed_at",
    "reviewed_at",
    "reviewer_basis",
    "workflow_scope",
    "classification",
    "semantic_review",
    "supersedes",
    "notes",
}
RECEIPT_FIELDS = {
    "schema_version",
    "receipt_id",
    "retrieved_at",
    "method",
    "claim_boundary",
}
RECEIPT_SOURCE_FIELDS = {
    "record_id",
    "repository",
    "commit_sha",
    "policy_path",
    "api_url",
    "git_blob_sha1",
    "source_bytes",
    "source_sha256",
}
RECEIPT_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class ConsentRecord:
    record_id: str
    repository: str
    repository_url: str
    commit_sha: str
    policy_source_url: str
    policy_path: str
    source_sha256: str
    observed_at: date
    reviewed_at: date
    classification: str
    supersedes: str | None
    notes: str

    def to_index_dict(self, *, as_of: date) -> dict[str, object]:
        age_days = (as_of - self.observed_at).days
        return {
            "record_id": self.record_id,
            "repository": self.repository,
            "repository_url": self.repository_url,
            "commit_sha": self.commit_sha,
            "policy_source_url": self.policy_source_url,
            "policy_path": self.policy_path,
            "source_sha256": self.source_sha256,
            "observed_at": self.observed_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat(),
            "workflow_scope": WORKFLOW_SCOPE,
            "classification": self.classification,
            "freshness": "current_for_7_day_candidate_window" if age_days <= 7 else "stale",
            "age_days_at_as_of": age_days,
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
    raise ValueError("JSON numbers are not part of the consent-record schema")


def _parse_receipt_integer(value: str) -> int:
    if len(value) > 8:
        raise ValueError("receipt integer exceeds the bounded digit limit")
    parsed = int(value)
    if parsed < 1 or parsed > MAX_SOURCE_BYTES:
        raise ValueError("receipt integer is outside the source-byte limit")
    return parsed


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


def _safe_read(path: Path) -> bytes:
    try:
        before = path.lstat()
    except OSError as error:
        raise ValueError("catalog record cannot be inspected") from error
    if path.is_symlink() or not stat.S_ISREG(before.st_mode):
        raise ValueError("catalog records must be nonsymlink regular files")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError("catalog record cannot be opened safely") from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("catalog record changed during safe open")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError(f"catalog record exceeds {MAX_FILE_BYTES} bytes")
    return payload


def _unsafe_directory(path: Path, inspected: os.stat_result) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(inspected, "st_file_attributes", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def _safe_read_receipt(path: Path) -> bytes:
    try:
        before = path.lstat()
    except OSError as error:
        raise ValueError("acquisition receipt cannot be inspected") from error
    if path.is_symlink() or not stat.S_ISREG(before.st_mode):
        raise ValueError("acquisition receipts must be nonsymlink regular files")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError("acquisition receipt cannot be opened safely") from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("acquisition receipt changed during safe open")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_RECEIPT_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_RECEIPT_BYTES:
        raise ValueError(f"acquisition receipt exceeds {MAX_RECEIPT_BYTES} bytes")
    return payload


def _parse_date(value: object, field: str) -> date:
    if type(value) is not str:
        raise ValueError(f"{field} must be a canonical YYYY-MM-DD date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field} must be a canonical YYYY-MM-DD date") from error
    if parsed.isoformat() != value:
        raise ValueError(f"{field} must be a canonical YYYY-MM-DD date")
    return parsed


def _plain_text(value: object, field: str) -> str:
    if type(value) is not str or not value.strip() or len(value) > MAX_NOTE_CHARS:
        raise ValueError(f"{field} must be a nonempty bounded string")
    if value != value.strip() or any(
        unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"} for character in value
    ):
        raise ValueError(f"{field} contains unsafe whitespace or formatting characters")
    return value


def _reject_unsafe_strings(value: object) -> None:
    if type(value) is str and any(
        unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"} for character in value
    ):
        raise ValueError("acquisition receipt contains unsafe control or formatting characters")
    if type(value) is dict:
        for key, child in value.items():
            _reject_unsafe_strings(key)
            _reject_unsafe_strings(child)
    elif type(value) is list:
        for child in value:
            _reject_unsafe_strings(child)


def _slug(repository: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", repository.casefold()).strip("-")


def expected_record_id(repository: str, commit_sha: str, source_sha256: str) -> str:
    return f"github-{_slug(repository)}-{commit_sha[:12]}-{source_sha256[:12]}"


def _parse_record(record: dict[str, Any]) -> ConsentRecord:
    if set(record) != EXPECTED_FIELDS or record.get("schema_version") != CATALOG_SCHEMA_VERSION:
        raise ValueError("consent record fields or schema version differ")
    repository = record["repository"]
    if type(repository) is not str or REPOSITORY.fullmatch(repository) is None:
        raise ValueError("repository must be a canonical owner/name string")
    commit_sha = record["commit_sha"]
    source_sha256 = record["source_sha256"]
    if type(commit_sha) is not str or COMMIT.fullmatch(commit_sha) is None:
        raise ValueError("commit_sha must be 40 lowercase hexadecimal characters")
    if type(source_sha256) is not str or DIGEST.fullmatch(source_sha256) is None:
        raise ValueError("source_sha256 must be 64 lowercase hexadecimal characters")
    if source_sha256 == "0" * 64:
        raise ValueError("source_sha256 cannot use the null digest sentinel")
    record_id = record["record_id"]
    expected_id = expected_record_id(repository, commit_sha, source_sha256)
    if (
        type(record_id) is not str
        or RECORD_ID.fullmatch(record_id) is None
        or record_id != expected_id
    ):
        raise ValueError("record_id does not match the canonical record identity")
    repository_url = record["repository_url"]
    if repository_url != f"https://github.com/{repository}":
        raise ValueError("repository_url must be the canonical GitHub repository URL")
    policy_path = record["policy_path"]
    if (
        type(policy_path) is not str
        or len(policy_path) > 300
        or POLICY_PATH.fullmatch(policy_path) is None
        or "//" in policy_path
        or any(part in {"", ".", ".."} for part in policy_path.split("/"))
    ):
        raise ValueError("policy_path must be a canonical ASCII repository-relative path")
    policy_source_url = record["policy_source_url"]
    expected_url = f"https://github.com/{repository}/blob/{commit_sha}/{policy_path}"
    if type(policy_source_url) is not str or policy_source_url != expected_url:
        raise ValueError("policy_source_url must bind the same repository, commit, and path")
    if any(value in policy_source_url for value in ("%", "\\", "?", "#")):
        raise ValueError("policy_source_url contains a noncanonical component")
    observed_at = _parse_date(record["observed_at"], "observed_at")
    reviewed_at = _parse_date(record["reviewed_at"], "reviewed_at")
    if reviewed_at < observed_at:
        raise ValueError("reviewed_at cannot precede observed_at")
    if observed_at > date.today() or reviewed_at > date.today():
        raise ValueError("observation and review dates cannot be in the future")
    if record["reviewer_basis"] != "manual_pinned_text_review":
        raise ValueError("reviewer_basis must disclose manual pinned-text review")
    if record["workflow_scope"] != WORKFLOW_SCOPE:
        raise ValueError("workflow_scope differs from the catalog's exact workflow")
    classification = record["classification"]
    if type(classification) is not str or classification not in CLASSIFICATIONS:
        raise ValueError("classification is outside the controlled vocabulary")
    if record["semantic_review"] != "manual":
        raise ValueError("semantic_review must remain manual")
    supersedes = record["supersedes"]
    if supersedes is not None and (
        type(supersedes) is not str or RECORD_ID.fullmatch(supersedes) is None
    ):
        raise ValueError("supersedes must be null or a canonical record_id")
    notes = _plain_text(record["notes"], "notes")
    return ConsentRecord(
        record_id=record_id,
        repository=repository,
        repository_url=repository_url,
        commit_sha=commit_sha,
        policy_source_url=policy_source_url,
        policy_path=policy_path,
        source_sha256=source_sha256,
        observed_at=observed_at,
        reviewed_at=reviewed_at,
        classification=classification,
        supersedes=supersedes,
        notes=notes,
    )


def _load_record(path: Path) -> ConsentRecord:
    payload = _safe_read(path)
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("catalog records must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("catalog records cannot contain a UTF-8 BOM")
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
        raise ValueError("catalog record is not valid strict JSON") from error
    if type(raw) is not dict:
        raise ValueError("catalog record must be a JSON object")
    parsed = _parse_record(raw)
    if path.name != f"{parsed.record_id}.json":
        raise ValueError("catalog filename must equal its canonical record_id")
    return parsed


def load_catalog(directory: Path) -> list[ConsentRecord]:
    try:
        inspected = directory.lstat()
    except OSError as error:
        raise ValueError("catalog directory cannot be inspected") from error
    if _unsafe_directory(directory, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("catalog input must be a non-link regular directory")
    paths: list[Path] = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if len(paths) >= MAX_RECORDS:
                raise ValueError(f"catalog exceeds the {MAX_RECORDS}-record limit")
            path = Path(entry.path)
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise ValueError("catalog directory can contain only regular JSON records")
            if path.suffix != ".json":
                raise ValueError("catalog directory can contain only .json records")
            paths.append(path)
    if not paths:
        raise ValueError("catalog must contain at least one record")
    records = [_load_record(path) for path in sorted(paths, key=lambda item: item.name)]
    by_id = {record.record_id: record for record in records}
    if len(by_id) != len(records):
        raise ValueError("catalog record_id values must be unique")
    identities = [
        (item.repository.casefold(), item.commit_sha, item.policy_path) for item in records
    ]
    if len(identities) != len(set(identities)):
        raise ValueError("catalog cannot duplicate a repository, commit, and policy path")
    successor_counts: dict[str, int] = {}
    for record in records:
        if record.supersedes is None:
            continue
        if record.supersedes == record.record_id or record.supersedes not in by_id:
            raise ValueError("supersedes must reference a different catalog record")
        previous = by_id[record.supersedes]
        if (
            previous.repository.casefold() != record.repository.casefold()
            or previous.policy_path != record.policy_path
            or record.observed_at < previous.observed_at
            or record.reviewed_at < previous.reviewed_at
        ):
            raise ValueError("supersession must preserve source identity and chronological order")
        successor_counts[record.supersedes] = successor_counts.get(record.supersedes, 0) + 1
        if successor_counts[record.supersedes] > 1:
            raise ValueError("a catalog record cannot have multiple direct successors")
    for record in records:
        seen: set[str] = set()
        current = record
        while current.supersedes is not None:
            if current.record_id in seen:
                raise ValueError("catalog supersession cycle detected")
            seen.add(current.record_id)
            current = by_id[current.supersedes]
    return sorted(
        records,
        key=lambda item: (item.repository.casefold(), item.reviewed_at, item.record_id),
    )


def _validate_receipt_source(
    source: object, *, records_by_id: dict[str, ConsentRecord]
) -> dict[str, object]:
    if type(source) is not dict or set(source) != RECEIPT_SOURCE_FIELDS:
        raise ValueError("acquisition receipt source fields differ")
    record_id = source["record_id"]
    if type(record_id) is not str or RECORD_ID.fullmatch(record_id) is None:
        raise ValueError("acquisition receipt record_id is not canonical")
    record = records_by_id.get(record_id)
    if record is None:
        raise ValueError("acquisition receipt references an unknown consent record")
    if (
        source["repository"] != record.repository
        or source["commit_sha"] != record.commit_sha
        or source["policy_path"] != record.policy_path
        or source["source_sha256"] != record.source_sha256
    ):
        raise ValueError("acquisition receipt provenance differs from its consent record")
    expected_api_url = (
        f"https://api.github.com/repos/{record.repository}/contents/{record.policy_path}"
        f"?ref={record.commit_sha}"
    )
    if type(source["api_url"]) is not str or source["api_url"] != expected_api_url:
        raise ValueError("acquisition receipt API URL is not canonically bound")
    if any(value in source["api_url"] for value in ("%", "\\", "#")):
        raise ValueError("acquisition receipt API URL contains a noncanonical component")
    blob = source["git_blob_sha1"]
    if type(blob) is not str or SHA1.fullmatch(blob) is None or blob == "0" * 40:
        raise ValueError("acquisition receipt Git blob SHA-1 is invalid")
    source_bytes = source["source_bytes"]
    if type(source_bytes) is not int or not 1 <= source_bytes <= MAX_SOURCE_BYTES:
        raise ValueError("acquisition receipt source_bytes is outside the bounded integer range")
    digest = source["source_sha256"]
    if type(digest) is not str or DIGEST.fullmatch(digest) is None or digest == "0" * 64:
        raise ValueError("acquisition receipt source SHA-256 is invalid")
    return dict(source)


def load_acquisition_receipt(
    path: Path,
    records: list[ConsentRecord],
    *,
    now_utc: datetime | None = None,
) -> dict[str, object]:
    payload = _safe_read_receipt(path)
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("acquisition receipts must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("acquisition receipts cannot contain a UTF-8 BOM")
    try:
        _validate_json_depth(text)
        raw = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=_reject_constant,
            parse_float=_reject_number,
            parse_int=_parse_receipt_integer,
        )
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        raise ValueError("acquisition receipt is not valid strict JSON") from error
    if type(raw) is not dict:
        raise ValueError("acquisition receipt must be a JSON object")
    _reject_unsafe_strings(raw)
    has_sources = "sources" in raw
    has_source = "source" in raw
    expected_fields = RECEIPT_FIELDS | ({"sources"} if has_sources else {"source"})
    if has_sources == has_source or set(raw) != expected_fields:
        raise ValueError("acquisition receipt envelope fields differ")
    if raw["schema_version"] != "1":
        raise ValueError("acquisition receipt schema version differs")
    receipt_id = raw["receipt_id"]
    if type(receipt_id) is not str or RECEIPT_ID.fullmatch(receipt_id) is None:
        raise ValueError("acquisition receipt_id is not canonical")
    retrieved_at = raw["retrieved_at"]
    if type(retrieved_at) is not str or UTC_TIMESTAMP.fullmatch(retrieved_at) is None:
        raise ValueError("acquisition receipt retrieved_at must be canonical UTC")
    try:
        retrieved = datetime.strptime(retrieved_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as error:
        raise ValueError("acquisition receipt retrieved_at is invalid") from error
    comparison_time = now_utc if now_utc is not None else datetime.now(timezone.utc)
    if comparison_time.tzinfo is None or comparison_time.utcoffset() != timedelta(0):
        raise ValueError("now_utc must be timezone-aware UTC")
    if retrieved > comparison_time:
        raise ValueError("acquisition receipt retrieved_at cannot be in the future")
    if raw["method"] != "github-contents-api-base64-decoded-source-bytes":
        raise ValueError("acquisition receipt method differs")
    _plain_text(raw["claim_boundary"], "claim_boundary")
    source_values = raw["sources"] if has_sources else [raw["source"]]
    if type(source_values) is not list or not 1 <= len(source_values) <= MAX_RECEIPT_SOURCES:
        raise ValueError("acquisition receipt source inventory is invalid")
    records_by_id = {record.record_id: record for record in records}
    sources = [
        _validate_receipt_source(source, records_by_id=records_by_id) for source in source_values
    ]
    source_ids = [source["record_id"] for source in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("acquisition receipt source record_ids must be unique")
    return dict(raw)


def build_index(records: list[ConsentRecord], *, as_of: date) -> dict[str, object]:
    if as_of > date.today():
        raise ValueError("as_of cannot be in the future")
    if any(as_of < item.observed_at or as_of < item.reviewed_at for item in records):
        raise ValueError("as_of cannot precede an observation or review date")
    indexed = [record.to_index_dict(as_of=as_of) for record in records]
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "component": {"name": "patch-consent-catalog", "version": CATALOG_COMPONENT_VERSION},
        "as_of": as_of.isoformat(),
        "claim_boundary": CLAIM_BOUNDARY,
        "summary": {
            "records": len(indexed),
            "current_for_7_day_candidate_window": sum(
                item["freshness"] == "current_for_7_day_candidate_window" for item in indexed
            ),
            "stale": sum(item["freshness"] == "stale" for item in indexed),
            "explicitly_allows": sum(
                item["classification"] == "explicitly_allows" for item in indexed
            ),
            "explicitly_disallows": sum(
                item["classification"] == "explicitly_disallows" for item in indexed
            ),
            "insufficiently_explicit": sum(
                item["classification"] == "insufficiently_explicit" for item in indexed
            ),
        },
        "records": indexed,
    }


def _code(value: object) -> str:
    pieces: list[str] = []
    for character in str(value):
        if unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}:
            pieces.append(f"\\u{ord(character):04x}")
        else:
            pieces.append(character)
    return f"<code>{html.escape(''.join(pieces), quote=True)}</code>"


def _inert_code(value: object) -> str:
    # Numeric entities preserve the displayed note while ensuring CommonMark/GFM never sees
    # link, image, autolink, raw-HTML, or emphasis punctuation inside the HTML code wrapper.
    encoded = "".join(f"&#x{ord(character):x};" for character in str(value))
    return f"<code>{encoded}</code>"


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Patch Cabinet contribution-consent catalog",
        "",
        f"> {html.escape(str(report['claim_boundary']))}",
        "",
        f"- Component: {_code(report['component']['name'] + ' ' + report['component']['version'])}",
        f"- Explicit as-of date: {_code(report['as_of'])}",
        f"- Records: {report['summary']['records']}",
        "",
        "| Repository | Classification | Observed | Freshness | Pinned source |",
        "|---|---|---|---|---|",
    ]
    for item in report["records"]:
        source = html.escape(str(item["policy_source_url"]), quote=True)
        lines.append(
            f"| {_code(item['repository'])} | {_code(item['classification'])} | "
            f"{_code(item['observed_at'])} | {_code(item['freshness'])} | "
            f"[source]({source}) |"
        )
    for item in report["records"]:
        lines.extend(
            [
                "",
                f"## {_code(item['repository'])}",
                "",
                f"- Record: {_code(item['record_id'])}",
                f"- Commit: {_code(item['commit_sha'])}",
                f"- Source SHA-256: {_code(item['source_sha256'])}",
                f"- Manual review note: {_inert_code(item['notes'])}",
            ]
        )
    return "\n".join(lines) + "\n"


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


def _assert_output_paths(directory: Path, outputs: list[Path]) -> None:
    resolved_directory = directory.resolve(strict=True)
    resolved = [path.resolve(strict=False) for path in outputs]
    if len(resolved) != len(set(resolved)):
        raise ValueError("JSON and Markdown outputs must use different paths")
    if any(path.is_relative_to(resolved_directory) for path in resolved):
        raise ValueError("outputs cannot be written inside the catalog record directory")
    input_stats = [path.lstat() for path in directory.iterdir()]
    input_inodes = {(item.st_dev, item.st_ino) for item in input_stats}
    for output in outputs:
        if output.exists():
            inspected = output.lstat()
            if output.is_symlink() or not stat.S_ISREG(inspected.st_mode):
                raise ValueError("existing output must be a nonsymlink regular file")
            if (inspected.st_dev, inspected.st_ino) in input_inodes:
                raise ValueError("output path aliases a catalog input")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patch_cabinet.consent_catalog")
    parser.add_argument("records", help="directory containing strict consent-record JSON files")
    parser.add_argument("--as-of", required=True, help="deterministic index date in YYYY-MM-DD")
    parser.add_argument("--json-out", help="write the deterministic JSON index")
    parser.add_argument("--markdown-out", help="write the deterministic Markdown index")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    as_of = _parse_date(args.as_of, "as_of")
    directory = Path(args.records)
    outputs = [Path(value) for value in (args.json_out, args.markdown_out) if value]
    records = load_catalog(directory)
    _assert_output_paths(directory, outputs)
    report = build_index(records, as_of=as_of)
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
