"""Strict offline normalization of manually reviewed contribution-policy facts."""

from __future__ import annotations

import argparse
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

from .consent_catalog import ConsentRecord, load_catalog as load_consent_catalog


PROFILE_COMPONENT_VERSION = "0.1.0"
PROFILE_SCHEMA_VERSION = "1"
MAX_FILE_BYTES = 65_536
MAX_PROFILES = 100
MAX_JSON_DEPTH = 12
MAX_NOTE_CHARS = 400
PROFILE_ID = re.compile(r"^github-[a-z0-9-]{1,150}-[0-9a-f]{12}-[0-9a-f]{12}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
POLICY_PATH = re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
REPOSITORY = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?/"
    r"[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?$"
)
THREE_WAY = {"allowed", "disallowed", "not_explicit"}
EXPECTATION = {"required", "recommended", "not_explicit"}
DIMENSION_VOCABULARIES = {
    "autonomous_issue_submission": THREE_WAY,
    "autonomous_pr_submission": THREE_WAY,
    "human_review": EXPECTATION,
    "disclosure": EXPECTATION,
    "human_accountability": EXPECTATION,
    "license_ip_checks": EXPECTATION,
    "good_first_issue_automation": THREE_WAY,
    "security_report_automation": THREE_WAY,
}
EXPECTED_FIELDS = {
    "schema_version",
    "profile_id",
    "consent_record_id",
    "repository",
    "commit_sha",
    "policy_path",
    "source_sha256",
    "dimensions",
    "semantic_review",
    "reviewer_basis",
    "supersedes",
    "notes",
}
CLAIM_BOUNDARY = (
    "Historical manually normalized facts only; no automatic prose interpretation or detection, "
    "current permission, candidate eligibility, contact, or submission authorization."
)
SNAPSHOT_COMPONENT_VERSION = "0.1.0"


@dataclass(frozen=True)
class PolicyProfile:
    profile_id: str
    consent_record_id: str
    repository: str
    commit_sha: str
    policy_path: str
    source_sha256: str
    dimensions: dict[str, str]
    supersedes: str | None
    notes: str

    def to_index_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "consent_record_id": self.consent_record_id,
            "repository": self.repository,
            "commit_sha": self.commit_sha,
            "policy_path": self.policy_path,
            "source_sha256": self.source_sha256,
            "dimensions": dict(self.dimensions),
            "semantic_review": "manual",
            "reviewer_basis": "manual_pinned_text_normalization",
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
    raise ValueError("JSON numbers are not part of the policy-profile schema")


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
        raise ValueError("profile cannot be inspected") from error
    if path.is_symlink() or not stat.S_ISREG(before.st_mode):
        raise ValueError("profiles must be nonsymlink regular files")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError("profile cannot be opened safely") from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("profile changed during safe open")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError(f"profile exceeds {MAX_FILE_BYTES} bytes")
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
        raise ValueError("profile contains unsafe control or formatting characters")
    if type(value) is dict:
        for key, child in value.items():
            _reject_unsafe_strings(key)
            _reject_unsafe_strings(child)
    elif type(value) is list:
        for child in value:
            _reject_unsafe_strings(child)


def _parse_profile(raw: dict[str, Any]) -> PolicyProfile:
    if set(raw) != EXPECTED_FIELDS or raw.get("schema_version") != PROFILE_SCHEMA_VERSION:
        raise ValueError("profile fields or schema version differ")
    _reject_unsafe_strings(raw)
    profile_id = raw["profile_id"]
    consent_record_id = raw["consent_record_id"]
    if (
        type(profile_id) is not str
        or PROFILE_ID.fullmatch(profile_id) is None
        or profile_id != consent_record_id
    ):
        raise ValueError("profile_id must equal the canonical consent_record_id")
    repository = raw["repository"]
    commit_sha = raw["commit_sha"]
    policy_path = raw["policy_path"]
    source_sha256 = raw["source_sha256"]
    if type(repository) is not str or REPOSITORY.fullmatch(repository) is None:
        raise ValueError("repository must be a canonical owner/name string")
    if type(commit_sha) is not str or COMMIT.fullmatch(commit_sha) is None:
        raise ValueError("commit_sha must be 40 lowercase hexadecimal characters")
    if type(source_sha256) is not str or DIGEST.fullmatch(source_sha256) is None:
        raise ValueError("source_sha256 must be 64 lowercase hexadecimal characters")
    if source_sha256 == "0" * 64:
        raise ValueError("source_sha256 cannot use the null digest sentinel")
    if (
        type(policy_path) is not str
        or len(policy_path) > 300
        or POLICY_PATH.fullmatch(policy_path) is None
        or any(part in {"", ".", ".."} for part in policy_path.split("/"))
    ):
        raise ValueError("policy_path must be a canonical ASCII repository-relative path")
    dimensions = raw["dimensions"]
    if type(dimensions) is not dict or set(dimensions) != set(DIMENSION_VOCABULARIES):
        raise ValueError("dimensions must contain exactly the eight defined dimensions")
    normalized: dict[str, str] = {}
    for name in DIMENSION_VOCABULARIES:
        value = dimensions[name]
        if type(value) is not str or value not in DIMENSION_VOCABULARIES[name]:
            raise ValueError(f"{name} is outside its controlled vocabulary")
        normalized[name] = value
    if raw["semantic_review"] != "manual":
        raise ValueError("semantic_review must remain manual")
    if raw["reviewer_basis"] != "manual_pinned_text_normalization":
        raise ValueError("reviewer_basis must disclose manual pinned-text normalization")
    supersedes = raw["supersedes"]
    if supersedes is not None and (
        type(supersedes) is not str or PROFILE_ID.fullmatch(supersedes) is None
    ):
        raise ValueError("supersedes must be null or a canonical profile_id")
    return PolicyProfile(
        profile_id=profile_id,
        consent_record_id=consent_record_id,
        repository=repository,
        commit_sha=commit_sha,
        policy_path=policy_path,
        source_sha256=source_sha256,
        dimensions=normalized,
        supersedes=supersedes,
        notes=_plain_text(raw["notes"], "notes"),
    )


def _load_profile(path: Path) -> PolicyProfile:
    payload = _safe_read(path)
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("profiles must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("profiles cannot contain a UTF-8 BOM")
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
        raise ValueError("profile is not valid strict JSON") from error
    if type(raw) is not dict:
        raise ValueError("profile must be a JSON object")
    profile = _parse_profile(raw)
    if path.name != f"{profile.profile_id}.json":
        raise ValueError("profile filename must equal its canonical profile_id")
    return profile


def _regular_json_paths(directory: Path) -> list[Path]:
    try:
        inspected = directory.lstat()
    except OSError as error:
        raise ValueError("profile directory cannot be inspected") from error
    if _unsafe_directory(directory, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("profile input must be a non-link regular directory")
    paths: list[Path] = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if len(paths) >= MAX_PROFILES:
                raise ValueError(f"catalog exceeds the {MAX_PROFILES}-profile limit")
            path = Path(entry.path)
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise ValueError("profile directory can contain only regular JSON profiles")
            if path.suffix != ".json":
                raise ValueError("profile directory can contain only .json profiles")
            paths.append(path)
    if not paths:
        raise ValueError("profile catalog must contain at least one profile")
    return sorted(paths, key=lambda item: item.name)


def load_profiles(profile_directory: Path, consent_directory: Path) -> list[PolicyProfile]:
    profiles = [_load_profile(path) for path in _regular_json_paths(profile_directory)]
    consent_records = load_consent_catalog(consent_directory)
    by_consent_id: dict[str, ConsentRecord] = {item.record_id: item for item in consent_records}
    by_profile_id = {item.profile_id: item for item in profiles}
    if len(by_profile_id) != len(profiles):
        raise ValueError("profile_id values must be unique")
    if len({item.consent_record_id for item in profiles}) != len(profiles):
        raise ValueError("each consent record can bind at most one profile")
    for profile in profiles:
        consent = by_consent_id.get(profile.consent_record_id)
        if consent is None:
            raise ValueError("profile must bind exactly one consent record")
        if (
            profile.repository != consent.repository
            or profile.commit_sha != consent.commit_sha
            or profile.policy_path != consent.policy_path
            or profile.source_sha256 != consent.source_sha256
        ):
            raise ValueError("profile provenance differs from its bound consent record")
        if profile.supersedes != consent.supersedes:
            raise ValueError("profile supersedes must exactly match its consent record")
    successor_counts: dict[str, int] = {}
    for profile in profiles:
        if profile.supersedes is None:
            continue
        if profile.supersedes == profile.profile_id or profile.supersedes not in by_profile_id:
            raise ValueError("supersedes must reference a different profile")
        previous = by_profile_id[profile.supersedes]
        current_consent = by_consent_id[profile.consent_record_id]
        if (
            previous.repository.casefold() != profile.repository.casefold()
            or previous.policy_path != profile.policy_path
            or current_consent.supersedes != previous.consent_record_id
        ):
            raise ValueError("profile successor crosses its consent lineage")
        successor_counts[profile.supersedes] = successor_counts.get(profile.supersedes, 0) + 1
        if successor_counts[profile.supersedes] > 1:
            raise ValueError("a profile cannot have multiple direct successors")
    for profile in profiles:
        seen: set[str] = set()
        current = profile
        while current.supersedes is not None:
            if current.profile_id in seen:
                raise ValueError("profile supersession cycle detected")
            seen.add(current.profile_id)
            current = by_profile_id[current.supersedes]
    return sorted(profiles, key=lambda item: (item.repository.casefold(), item.profile_id))


def build_index(profiles: list[PolicyProfile]) -> dict[str, object]:
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "component": {
            "name": "patch-policy-profile-catalog",
            "version": PROFILE_COMPONENT_VERSION,
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "summary": {"profiles": len(profiles)},
        "profiles": [profile.to_index_dict() for profile in profiles],
    }


def _parse_as_of(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("as-of must be a canonical YYYY-MM-DD date") from error
    if parsed.isoformat() != value:
        raise ValueError("as-of must be a canonical YYYY-MM-DD date")
    return parsed


def _parse_dimension_filters(values: list[str]) -> dict[str, str]:
    filters: dict[str, str] = {}
    for raw in values:
        if raw.count("=") != 1:
            raise ValueError("each dimension filter must use name=value")
        name, value = raw.split("=", 1)
        vocabulary = DIMENSION_VOCABULARIES.get(name)
        if vocabulary is None or value not in vocabulary:
            raise ValueError("dimension filter is outside the controlled vocabulary")
        if name in filters:
            raise ValueError("each dimension can be filtered at most once")
        filters[name] = value
    return filters


def build_snapshot(
    profiles: list[PolicyProfile],
    consent_records: list[ConsentRecord],
    *,
    as_of: date,
    filters: dict[str, str],
) -> dict[str, object]:
    """Build a neutral historical snapshot; it does not rank or authorize records."""
    consent_by_id = {record.record_id: record for record in consent_records}
    selected: list[dict[str, object]] = []
    freshness_counts = {"fresh": 0, "stale": 0, "unknown": 0}
    for profile in profiles:
        if any(profile.dimensions[name] != value for name, value in filters.items()):
            continue
        consent = consent_by_id[profile.consent_record_id]
        age_days = (as_of - consent.observed_at).days
        freshness = "unknown" if age_days < 0 else "fresh" if age_days <= 7 else "stale"
        freshness_counts[freshness] += 1
        item = profile.to_index_dict()
        item.update(
            {
                "observed_at": consent.observed_at.isoformat(),
                "freshness": freshness,
                "age_days_at_as_of": age_days if age_days >= 0 else None,
            }
        )
        selected.append(item)
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "component": {
            "name": "patch-policy-profile-catalog-snapshot",
            "version": SNAPSHOT_COMPONENT_VERSION,
        },
        "claim_boundary": (
            CLAIM_BOUNDARY
            + " Fresh, stale, and unknown are date-window labels only, not trust, readiness, "
            "ranking, current-permission, or authorization results."
        ),
        "as_of": as_of.isoformat(),
        "freshness_window_days": 7,
        "filters": dict(sorted(filters.items())),
        "summary": {"matched_profiles": len(selected), "freshness": freshness_counts},
        "profiles": selected,
    }


def _code(value: object) -> str:
    return f"<code>{html.escape(str(value), quote=True)}</code>"


def _inert_code(value: object) -> str:
    encoded = "".join(f"&#x{ord(character):x};" for character in str(value))
    return f"<code>{encoded}</code>"


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Patch Cabinet manual policy-profile catalog",
        "",
        f"> {html.escape(str(report['claim_boundary']))}",
        "",
        f"- Component: {_code(report['component']['name'] + ' ' + report['component']['version'])}",
        f"- Profiles: {report['summary']['profiles']}",
        "",
        "| Repository | Consent record | Human review | Accountability |",
        "|---|---|---|---|",
    ]
    for profile in report["profiles"]:
        lines.append(
            f"| {_code(profile['repository'])} | {_code(profile['consent_record_id'])} | "
            f"{_code(profile['dimensions']['human_review'])} | "
            f"{_code(profile['dimensions']['human_accountability'])} |"
        )
    for profile in report["profiles"]:
        lines.extend(["", f"## {_code(profile['repository'])}", ""])
        for name in DIMENSION_VOCABULARIES:
            lines.append(f"- {_code(name)}: {_code(profile['dimensions'][name])}")
        lines.append(f"- Manual normalization note: {_inert_code(profile['notes'])}")
    return "\n".join(lines) + "\n"


def render_snapshot_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Patch Cabinet historical policy-profile snapshot",
        "",
        f"> {html.escape(str(report['claim_boundary']))}",
        "",
        f"- As of: {_code(report['as_of'])}",
        f"- Freshness window: {_code(str(report['freshness_window_days']) + ' days')}",
        f"- Matched profiles: {report['summary']['matched_profiles']}",
        "- Filters: " + (
            ", ".join(f"{_code(name)}={_code(value)}" for name, value in report["filters"].items())
            if report["filters"] else "none"
        ),
        "",
        "| Repository | Observed | Freshness | Age days |",
        "|---|---|---|---:|",
    ]
    for profile in report["profiles"]:
        age = "unknown" if profile["age_days_at_as_of"] is None else profile["age_days_at_as_of"]
        lines.append(
            f"| {_code(profile['repository'])} | {_code(profile['observed_at'])} | "
            f"{_code(profile['freshness'])} | {age} |"
        )
    return "\n".join(lines) + "\n"


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


def _assert_output_paths(inputs: list[Path], outputs: list[Path]) -> None:
    resolved_inputs = [path.resolve(strict=True) for path in inputs]
    resolved_outputs = [path.resolve(strict=False) for path in outputs]
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise ValueError("JSON and Markdown outputs must use different paths")
    if any(
        output.is_relative_to(directory)
        for output in resolved_outputs
        for directory in resolved_inputs
    ):
        raise ValueError("outputs cannot be written inside either input directory")
    input_inodes: set[tuple[int, int]] = set()
    for directory in inputs:
        inspected_inputs = (path.lstat() for path in directory.iterdir())
        input_inodes.update((item.st_dev, item.st_ino) for item in inspected_inputs)
    for output in outputs:
        if output.exists():
            inspected = output.lstat()
            if output.is_symlink() or not stat.S_ISREG(inspected.st_mode):
                raise ValueError("existing output must be a nonsymlink regular file")
            if (inspected.st_dev, inspected.st_ino) in input_inodes:
                raise ValueError("output path aliases a catalog input")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patch_cabinet.policy_profile_catalog")
    parser.add_argument("profiles", help="directory containing strict policy-profile JSON files")
    parser.add_argument(
        "--consent-records", required=True, help="explicit consent-record directory"
    )
    parser.add_argument("--json-out", help="write the deterministic JSON index")
    parser.add_argument("--markdown-out", help="write the deterministic Markdown index")
    parser.add_argument(
        "--as-of",
        help="emit a neutral historical snapshot at canonical YYYY-MM-DD",
    )
    parser.add_argument(
        "--where",
        action="append",
        default=[],
        metavar="DIMENSION=VALUE",
        help="filter an explicit controlled dimension; repeat for an AND query",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    profile_directory = Path(args.profiles)
    consent_directory = Path(args.consent_records)
    outputs = [Path(value) for value in (args.json_out, args.markdown_out) if value]
    profiles = load_profiles(profile_directory, consent_directory)
    _assert_output_paths([profile_directory, consent_directory], outputs)
    if args.where and not args.as_of:
        raise ValueError("dimension filters require --as-of snapshot mode")
    if args.as_of:
        report = build_snapshot(
            profiles,
            load_consent_catalog(consent_directory),
            as_of=_parse_as_of(args.as_of),
            filters=_parse_dimension_filters(args.where),
        )
        markdown = render_snapshot_markdown(report)
    else:
        report = build_index(profiles)
        markdown = render_markdown(report)
    serialized = json.dumps(report, indent=2) + "\n"
    if args.json_out:
        _write_atomic(Path(args.json_out), serialized)
    if args.markdown_out:
        _write_atomic(Path(args.markdown_out), markdown)
    if not outputs:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
