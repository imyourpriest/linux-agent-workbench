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
from datetime import date
from pathlib import Path
from typing import Any, Sequence


CATALOG_COMPONENT_VERSION = "0.1.0"
CATALOG_SCHEMA_VERSION = "1"
MAX_FILE_BYTES = 65_536
MAX_RECORDS = 100
MAX_JSON_DEPTH = 12
MAX_NOTE_CHARS = 400
REPOSITORY = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?/[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?$")
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
    if type(record_id) is not str or RECORD_ID.fullmatch(record_id) is None or record_id != expected_id:
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
    if directory.is_symlink() or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("catalog input must be a nonsymlink directory")
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
    identities = [(item.repository.casefold(), item.commit_sha, item.policy_path) for item in records]
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
    return sorted(records, key=lambda item: (item.repository.casefold(), item.reviewed_at, item.record_id))


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
