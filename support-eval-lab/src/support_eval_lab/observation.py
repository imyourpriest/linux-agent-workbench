"""Strict offline normalizer for manually recorded channel observations."""

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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence


COMPONENT_VERSION = "0.1.0"
SCHEMA_VERSION = "1"
MAX_FILE_BYTES = 262_144
MAX_JSON_DEPTH = 16
MAX_NODES = 2_000
MAX_PREVIEWS = 256
MAX_TRAFFIC = 32
MAX_ISSUES = 100
MAX_URL_CHARS = 500
IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{0,79}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}[A-Za-z0-9])?(?:\[bot\])?$")
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
TOPIC = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHECKPOINTS = {"activation", "day1", "day7", "day13", "day14-refresh"}
ROW_STATES = {"present", "absent", "not-checked"}
SOURCE_MODE = "operator_recorded_unverified"
CLAIM_BOUNDARY = (
    "Operator-recorded, unverified platform observations. This report does not prove identity, "
    "unique people, attribution, buyer intent, customer status, revenue, or authorization."
)
CONFIG_FIELDS = {
    "schema_version",
    "experiment_id",
    "repository",
    "owner_login",
    "target_commit",
    "entry_path",
    "entry_url",
    "expected_popular_path",
    "release_url",
    "window_start",
    "window_end",
    "final_capture_deadline",
    "entry_sha256",
    "release_body_sha256",
    "issue_form_sha256",
    "frozen_description",
    "frozen_topics",
}
OBSERVATION_FIELDS = {
    "schema_version",
    "record_id",
    "experiment_id",
    "source_mode",
    "captured_at",
    "configuration_observation",
    "owner_preview_events",
    "traffic_observations",
    "issue_observations",
}
CONFIGURATION_OBSERVATION_FIELDS = {
    "target_commit",
    "entry_sha256",
    "release_body_sha256",
    "issue_form_sha256",
    "frozen_description",
    "frozen_topics",
}
TRAFFIC_FIELDS = {
    "event_id",
    "checkpoint",
    "captured_at",
    "row_state",
    "captured_path",
    "raw_views",
    "retained_window_start",
    "retained_window_end",
}
KNOWN_EXPERIMENT_CONFIG_SHA256 = {
    "sel-gh-001": "264c8b90a6709bcced722c6e394f2beb7896d99d408bf20f628c56e83af4be51"
}


@dataclass(frozen=True)
class FileIdentity:
    device: int
    inode: int
    size: int
    modified_ns: int


@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    repository: str
    owner_login: str
    target_commit: str
    entry_path: str
    entry_url: str
    expected_popular_path: str
    release_url: str
    window_start: datetime
    window_end: datetime
    final_capture_deadline: datetime
    entry_sha256: str
    release_body_sha256: str
    issue_form_sha256: str
    frozen_description: str
    frozen_topics: tuple[str, ...]
    config_sha256: str
    source_identity: FileIdentity | None


def _reject_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key is not allowed")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant is not allowed")


def _bounded_integer(value: str) -> int:
    if len(value) > 9:
        raise ValueError("JSON integer exceeds the bounded decimal representation")
    return int(value)


def _reject_float(_value: str) -> object:
    raise ValueError("floating-point JSON numbers are not part of this schema")


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
            continue
        if character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise ValueError(f"JSON nesting exceeds the {MAX_JSON_DEPTH}-level limit")
        elif character in "]}":
            depth -= 1


def _count_nodes(value: object) -> int:
    if type(value) is dict:
        return 1 + sum(_count_nodes(key) + _count_nodes(item) for key, item in value.items())
    if type(value) is list:
        return 1 + sum(_count_nodes(item) for item in value)
    return 1


def _identity(metadata: os.stat_result) -> FileIdentity:
    return FileIdentity(
        device=metadata.st_dev,
        inode=metadata.st_ino,
        size=metadata.st_size,
        modified_ns=metadata.st_mtime_ns,
    )


def _safe_read(path: Path) -> tuple[bytes, FileIdentity]:
    try:
        before = path.lstat()
    except OSError as error:
        raise ValueError(f"{path.name}: input cannot be inspected") from error
    if path.is_symlink() or not stat.S_ISREG(before.st_mode):
        raise ValueError(f"{path.name}: input must be a nonsymlink regular file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError(f"{path.name}: input cannot be opened safely") from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or _identity(before) != _identity(opened)
        ):
            raise ValueError(f"{path.name}: input changed during safe open")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
        after = os.fstat(descriptor)
        if _identity(after) != _identity(opened):
            raise ValueError(f"{path.name}: input changed during safe read")
    finally:
        os.close(descriptor)
    try:
        path_after = path.lstat()
    except OSError as error:
        raise ValueError(f"{path.name}: input changed after safe read") from error
    if path.is_symlink() or _identity(path_after) != _identity(opened):
        raise ValueError(f"{path.name}: input path changed after safe read")
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError(f"{path.name}: input exceeds {MAX_FILE_BYTES} bytes")
    return payload, _identity(opened)


def _load_json(path: Path) -> tuple[dict[str, Any], str, FileIdentity]:
    payload, source_identity = _safe_read(path)
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{path.name}: input must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError(f"{path.name}: UTF-8 BOM is not allowed")
    try:
        _validate_depth(text)
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=_reject_constant,
            parse_int=_bounded_integer,
            parse_float=_reject_float,
        )
    except (json.JSONDecodeError, RecursionError, ValueError) as error:
        raise ValueError(f"{path.name}: invalid strict JSON") from error
    if type(parsed) is not dict:
        raise ValueError(f"{path.name}: top-level value must be an object")
    if _count_nodes(parsed) > MAX_NODES:
        raise ValueError(f"{path.name}: JSON node count exceeds {MAX_NODES}")
    return parsed, hashlib.sha256(payload).hexdigest(), source_identity


def _identifier(value: object, field: str) -> str:
    if type(value) is not str or IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"{field} must be a lowercase hyphenated identifier")
    return value


def _text(value: object, field: str, *, maximum: int = 500) -> str:
    if type(value) is not str or not value.strip() or value != value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be a nonempty bounded string")
    if any(unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"} for character in value):
        raise ValueError(f"{field} contains control or formatting characters")
    return value


def _timestamp(value: object, field: str) -> datetime:
    if type(value) is not str or UTC_TIMESTAMP.fullmatch(value) is None:
        raise ValueError(f"{field} must be a canonical second-precision UTC timestamp")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise ValueError(f"{field} must be a canonical second-precision UTC timestamp") from error
    return parsed


def _canonical_path(value: object, field: str, *, leading_slash: bool) -> str:
    maximum = 400
    if type(value) is not str or not value or len(value) > maximum:
        raise ValueError(f"{field} must be a bounded canonical path")
    if value.startswith("/") != leading_slash:
        raise ValueError(f"{field} uses the wrong leading-slash form")
    path = value[1:] if leading_slash else value
    if (
        not path
        or "%" in path
        or "\\" in path
        or "//" in path
        or any(part in {"", ".", ".."} for part in path.split("/"))
        or any(not character.isascii() for character in path)
    ):
        raise ValueError(f"{field} contains a noncanonical component")
    return value


def _canonical_https_url(value: object, field: str, expected: str) -> str:
    if type(value) is not str or len(value) > MAX_URL_CHARS or value != expected:
        raise ValueError(f"{field} differs from the exact experiment URL")
    if any(piece in value for piece in ("%", "\\", "?", "#", "@")):
        raise ValueError(f"{field} contains a noncanonical URL component")
    return value


def _digest(value: object, field: str) -> str:
    if type(value) is not str or DIGEST.fullmatch(value) is None or value == "0" * 64:
        raise ValueError(f"{field} must be a nonzero lowercase SHA-256 digest")
    return value


def _bounded_count(value: object, field: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum or value > 100_000_000:
        raise ValueError(f"{field} must be a bounded integer")
    return value


def _parse_experiment(
    record: dict[str, Any],
    *,
    config_sha256: str = "unregistered-test-configuration",
    source_identity: FileIdentity | None = None,
) -> Experiment:
    if set(record) != CONFIG_FIELDS or record["schema_version"] != SCHEMA_VERSION:
        raise ValueError("experiment fields or schema version differ")
    experiment_id = _identifier(record["experiment_id"], "experiment_id")
    repository = record["repository"]
    if type(repository) is not str or REPOSITORY.fullmatch(repository) is None:
        raise ValueError("repository must be owner/name")
    owner_login = record["owner_login"]
    if type(owner_login) is not str or LOGIN.fullmatch(owner_login) is None:
        raise ValueError("owner_login is not a canonical GitHub login")
    target_commit = record["target_commit"]
    if type(target_commit) is not str or COMMIT.fullmatch(target_commit) is None:
        raise ValueError("target_commit must be 40 lowercase hexadecimal characters")
    entry_path = _canonical_path(record["entry_path"], "entry_path", leading_slash=False)
    expected_popular = f"/{repository}/blob/{target_commit}/{entry_path}"
    expected_entry_url = f"https://github.com{expected_popular}"
    entry_url = _canonical_https_url(record["entry_url"], "entry_url", expected_entry_url)
    popular_path = _canonical_path(
        record["expected_popular_path"], "expected_popular_path", leading_slash=True
    )
    if popular_path != expected_popular:
        raise ValueError("expected_popular_path does not bind the exact entry URL")
    release_url = _canonical_https_url(
        record["release_url"],
        "release_url",
        f"https://github.com/{repository}/releases/tag/support-eval-starter-v0.1.0",
    )
    window_start = _timestamp(record["window_start"], "window_start")
    window_end = _timestamp(record["window_end"], "window_end")
    if window_end - window_start != timedelta(days=14):
        raise ValueError("experiment window must be exactly 14 days")
    final_capture_deadline = _timestamp(
        record["final_capture_deadline"], "final_capture_deadline"
    )
    if final_capture_deadline != window_end + timedelta(days=2):
        raise ValueError("final_capture_deadline must be exactly two days after the window")
    description = _text(record["frozen_description"], "frozen_description", maximum=200)
    raw_topics = record["frozen_topics"]
    if type(raw_topics) is not list or not raw_topics or len(raw_topics) > 20:
        raise ValueError("frozen_topics must be a bounded nonempty list")
    topics: list[str] = []
    for raw_topic in raw_topics:
        if type(raw_topic) is not str or TOPIC.fullmatch(raw_topic) is None:
            raise ValueError("frozen_topics contains an invalid topic")
        topics.append(raw_topic)
    if topics != sorted(set(topics)):
        raise ValueError("frozen_topics must be unique and sorted")
    return Experiment(
        experiment_id=experiment_id,
        repository=repository,
        owner_login=owner_login,
        target_commit=target_commit,
        entry_path=entry_path,
        entry_url=entry_url,
        expected_popular_path=popular_path,
        release_url=release_url,
        window_start=window_start,
        window_end=window_end,
        final_capture_deadline=final_capture_deadline,
        entry_sha256=_digest(record["entry_sha256"], "entry_sha256"),
        release_body_sha256=_digest(record["release_body_sha256"], "release_body_sha256"),
        issue_form_sha256=_digest(record["issue_form_sha256"], "issue_form_sha256"),
        frozen_description=description,
        frozen_topics=tuple(topics),
        config_sha256=config_sha256,
        source_identity=source_identity,
    )


def load_experiment(path: Path) -> Experiment:
    record, source_sha256, source_identity = _load_json(path)
    experiment_id = record.get("experiment_id")
    expected_sha256 = (
        KNOWN_EXPERIMENT_CONFIG_SHA256.get(experiment_id)
        if type(experiment_id) is str
        else None
    )
    if expected_sha256 is None or source_sha256 != expected_sha256:
        raise ValueError("experiment configuration is not the registered frozen document")
    experiment = _parse_experiment(
        record, config_sha256=source_sha256, source_identity=source_identity
    )
    repository_owner = experiment.repository.split("/", 1)[0]
    if repository_owner.casefold() != experiment.owner_login.casefold():
        raise ValueError("owner_login must match the user-owned repository namespace")
    return experiment


def _parse_preview(record: object, experiment: Experiment) -> dict[str, object]:
    fields = {"event_id", "captured_at", "path"}
    if type(record) is not dict or set(record) != fields:
        raise ValueError("owner preview fields differ")
    path = _canonical_path(record["path"], "owner preview path", leading_slash=True)
    if path != experiment.expected_popular_path:
        raise ValueError("owner preview path differs from the exact entry path")
    return {
        "event_id": _identifier(record["event_id"], "owner preview event_id"),
        "captured_at": _timestamp(record["captured_at"], "owner preview captured_at"),
        "path": path,
    }


def _parse_traffic(record: object, experiment: Experiment) -> dict[str, object]:
    if type(record) is not dict or set(record) != TRAFFIC_FIELDS:
        raise ValueError("traffic observation fields differ")
    checkpoint = record["checkpoint"]
    row_state = record["row_state"]
    if type(checkpoint) is not str or checkpoint not in CHECKPOINTS:
        raise ValueError("traffic checkpoint is outside the frozen schedule")
    if type(row_state) is not str or row_state not in ROW_STATES:
        raise ValueError("traffic row_state is outside the controlled vocabulary")
    captured_at = _timestamp(record["captured_at"], "traffic captured_at")
    if row_state == "present":
        path = _canonical_path(record["captured_path"], "captured_path", leading_slash=True)
        if path != experiment.expected_popular_path:
            raise ValueError("present traffic row path differs from the exact entry path")
        raw_views: int | None = _bounded_count(record["raw_views"], "raw_views", minimum=1)
    elif row_state == "absent":
        if record["captured_path"] is not None or record["raw_views"] is not None:
            raise ValueError("absent or unchecked traffic rows cannot carry path or view fields")
        path = None
        raw_views = None
    else:
        if record["captured_path"] is not None or record["raw_views"] is not None:
            raise ValueError("absent or unchecked traffic rows cannot carry path or view fields")
        path = None
        raw_views = None
    if row_state in {"present", "absent"}:
        retained_start = _timestamp(
            record["retained_window_start"], "retained_window_start"
        )
        retained_end = _timestamp(record["retained_window_end"], "retained_window_end")
        if retained_end != captured_at or retained_end - retained_start != timedelta(days=14):
            raise ValueError("checked traffic must bind one exact 14-day retained window")
    else:
        if record["retained_window_start"] is not None or record["retained_window_end"] is not None:
            raise ValueError("unchecked traffic cannot claim a retained window")
        retained_start = None
        retained_end = None
    return {
        "event_id": _identifier(record["event_id"], "traffic event_id"),
        "checkpoint": checkpoint,
        "captured_at": captured_at,
        "row_state": row_state,
        "captured_path": path,
        "raw_views": raw_views,
        "retained_window_start": retained_start,
        "retained_window_end": retained_end,
    }


def _parse_issue(record: object, experiment: Experiment) -> dict[str, object]:
    base = {"event_id", "issue_url", "issue_number", "created_at", "captured_at", "safety_disposition"}
    if type(record) is not dict or not base <= set(record):
        raise ValueError("issue observation base fields differ")
    disposition = record["safety_disposition"]
    issue_number = _bounded_count(record["issue_number"], "issue_number", minimum=1)
    expected_url = f"https://github.com/{experiment.repository}/issues/{issue_number}"
    issue_url = _canonical_https_url(record["issue_url"], "issue_url", expected_url)
    parsed: dict[str, object] = {
        "event_id": _identifier(record["event_id"], "issue event_id"),
        "issue_url": issue_url,
        "issue_number": issue_number,
        "created_at": _timestamp(record["created_at"], "issue created_at"),
        "captured_at": _timestamp(record["captured_at"], "issue captured_at"),
        "safety_disposition": disposition,
    }
    if disposition == "sensitive-or-uncertain":
        if set(record) != base:
            raise ValueError("sensitive issue records may contain only URL, time, and disposition")
        return parsed
    clear_fields = base | {
        "author_login",
        "actor_type",
        "form_source_sha256",
        "boundary_acknowledgement",
        "outcome_disposition",
        "intent",
    }
    if disposition != "clear" or set(record) != clear_fields:
        raise ValueError("clear issue fields or safety disposition differ")
    author = record["author_login"]
    if type(author) is not str or LOGIN.fullmatch(author) is None:
        raise ValueError("author_login is not a canonical GitHub login")
    actor_type = record["actor_type"]
    if actor_type not in {"user", "bot", "unknown"}:
        raise ValueError("actor_type is outside the controlled vocabulary")
    acknowledgement = record["boundary_acknowledgement"]
    if acknowledgement not in {"yes", "no", "unknown"}:
        raise ValueError("boundary_acknowledgement is outside the controlled vocabulary")
    outcome = record["outcome_disposition"]
    if outcome not in {"generic-in-scope", "out-of-scope", "unknown"}:
        raise ValueError("outcome_disposition is outside the controlled vocabulary")
    intent = record["intent"]
    if intent not in {"general-feedback", "future-private-route", "none", "unknown"}:
        raise ValueError("intent is outside the controlled vocabulary")
    parsed.update(
        {
            "author_login": author,
            "actor_type": actor_type,
            "form_source_sha256": _digest(record["form_source_sha256"], "form_source_sha256"),
            "boundary_acknowledgement": acknowledgement,
            "outcome_disposition": outcome,
            "intent": intent,
        }
    )
    return parsed


def _parse_configuration_observation(
    record: object, experiment: Experiment
) -> dict[str, object]:
    if type(record) is not dict or set(record) != CONFIGURATION_OBSERVATION_FIELDS:
        raise ValueError("configuration observation fields differ")
    target_commit = record["target_commit"]
    if type(target_commit) is not str or COMMIT.fullmatch(target_commit) is None:
        raise ValueError("observed target_commit must be lowercase hexadecimal")
    description = _text(
        record["frozen_description"], "observed frozen_description", maximum=200
    )
    raw_topics = record["frozen_topics"]
    if type(raw_topics) is not list or not raw_topics or len(raw_topics) > 20:
        raise ValueError("observed frozen_topics must be a bounded nonempty list")
    topics: list[str] = []
    for raw_topic in raw_topics:
        if type(raw_topic) is not str or TOPIC.fullmatch(raw_topic) is None:
            raise ValueError("observed frozen_topics contains an invalid topic")
        topics.append(raw_topic)
    if topics != sorted(set(topics)):
        raise ValueError("observed frozen_topics must be unique and sorted")
    values = {
        "target_commit": target_commit,
        "entry_sha256": _digest(record["entry_sha256"], "observed entry_sha256"),
        "release_body_sha256": _digest(
            record["release_body_sha256"], "observed release_body_sha256"
        ),
        "issue_form_sha256": _digest(
            record["issue_form_sha256"], "observed issue_form_sha256"
        ),
        "frozen_description": description,
        "frozen_topics": tuple(topics),
    }
    values["matches_frozen_configuration"] = values == {
        "target_commit": experiment.target_commit,
        "entry_sha256": experiment.entry_sha256,
        "release_body_sha256": experiment.release_body_sha256,
        "issue_form_sha256": experiment.issue_form_sha256,
        "frozen_description": experiment.frozen_description,
        "frozen_topics": experiment.frozen_topics,
    }
    return values


def load_observation(path: Path, experiment: Experiment) -> dict[str, object]:
    record, _source_sha256, source_identity = _load_json(path)
    if set(record) != OBSERVATION_FIELDS or record["schema_version"] != SCHEMA_VERSION:
        raise ValueError("observation fields or schema version differ")
    if record["experiment_id"] != experiment.experiment_id:
        raise ValueError("observation experiment_id differs from the configuration")
    if record["source_mode"] != SOURCE_MODE:
        raise ValueError("source_mode must disclose operator-recorded unverified evidence")
    expected_record_id = f"{experiment.experiment_id}-window-record"
    if record["record_id"] != expected_record_id:
        raise ValueError("record_id differs from the configured experiment identity")
    captured_at = _timestamp(record["captured_at"], "captured_at")
    configuration_observation = _parse_configuration_observation(
        record["configuration_observation"], experiment
    )
    raw_previews = record["owner_preview_events"]
    raw_traffic = record["traffic_observations"]
    raw_issues = record["issue_observations"]
    if type(raw_previews) is not list or len(raw_previews) > MAX_PREVIEWS:
        raise ValueError("owner_preview_events exceeds its bounded list schema")
    if type(raw_traffic) is not list or not raw_traffic or len(raw_traffic) > MAX_TRAFFIC:
        raise ValueError("traffic_observations must be a bounded nonempty list")
    if type(raw_issues) is not list or len(raw_issues) > MAX_ISSUES:
        raise ValueError("issue_observations exceeds its bounded list schema")
    previews = [_parse_preview(item, experiment) for item in raw_previews]
    traffic = [_parse_traffic(item, experiment) for item in raw_traffic]
    issues = [_parse_issue(item, experiment) for item in raw_issues]
    event_ids = [item["event_id"] for item in previews + traffic + issues]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError("event_id values must be unique across the observation record")
    checkpoints = [item["checkpoint"] for item in traffic]
    if len(checkpoints) != len(set(checkpoints)):
        raise ValueError("traffic checkpoints must be unique")
    issue_numbers = [item["issue_number"] for item in issues]
    issue_urls = [item["issue_url"] for item in issues]
    if len(issue_numbers) != len(set(issue_numbers)) or len(issue_urls) != len(set(issue_urls)):
        raise ValueError("each public issue may appear only once in an observation record")
    checkpoint_order = {
        "activation": 0,
        "day1": 1,
        "day7": 2,
        "day13": 3,
        "day14-refresh": 4,
    }
    orders = [checkpoint_order[value] for value in checkpoints]
    if orders != sorted(orders):
        raise ValueError("traffic checkpoints must follow the frozen schedule order")
    for items, label in ((previews, "preview"), (traffic, "traffic")):
        timestamps = [item["captured_at"] for item in items]
        if timestamps != sorted(timestamps) or len(timestamps) != len(set(timestamps)):
            raise ValueError(f"{label} events must have strictly increasing timestamps")
    for item in previews + traffic + issues:
        if item["captured_at"] > captured_at:
            raise ValueError("event timestamp cannot follow the observation capture time")
    for item in previews:
        if item["captured_at"] < experiment.window_start:
            raise ValueError("owner preview cannot precede experiment activation")
    for item in traffic:
        if item["captured_at"] < experiment.window_start:
            raise ValueError("traffic observation cannot precede experiment activation")
        if item["checkpoint"] == "day14-refresh" and item["captured_at"] < experiment.window_end:
            raise ValueError("day14-refresh traffic must be captured after the window ends")
        if (
            item["checkpoint"] == "day14-refresh"
            and item["captured_at"] > experiment.final_capture_deadline
        ):
            raise ValueError("day14-refresh traffic exceeded the frozen capture deadline")
        if item["checkpoint"] != "day14-refresh" and item["captured_at"] > experiment.window_end:
            raise ValueError("pre-final traffic checkpoint cannot follow the window end")
    for issue in issues:
        if issue["created_at"] > issue["captured_at"]:
            raise ValueError("issue creation cannot follow its capture time")
    return {
        "record_id": expected_record_id,
        "source_mode": SOURCE_MODE,
        "captured_at": captured_at,
        "configuration_observation": configuration_observation,
        "owner_preview_events": previews,
        "traffic_observations": traffic,
        "issue_observations": issues,
        "source_identity": source_identity,
    }


def build_report(
    experiment: Experiment, observation: dict[str, object], *, as_of: datetime
) -> dict[str, object]:
    if as_of < experiment.window_start or as_of < observation["captured_at"]:
        raise ValueError("as_of cannot precede activation or the observation capture")
    traffic = observation["traffic_observations"]
    latest = max(traffic, key=lambda item: item["captured_at"])
    if latest["retained_window_start"] is not None:
        preview_start = latest["retained_window_start"]
        preview_end = latest["retained_window_end"]
    else:
        preview_start = experiment.window_start
        preview_end = latest["captured_at"]
    preview_count = sum(
        preview_start <= item["captured_at"] <= preview_end
        for item in observation["owner_preview_events"]
    )
    raw_views = latest["raw_views"]
    if latest["row_state"] == "present":
        qualified_views: int | None = max(0, raw_views - preview_count)
        observability = "observed"
        traffic_warning = "owner previews exceeded raw views; qualified views saturated at zero" if preview_count > raw_views else None
    elif latest["row_state"] == "absent":
        qualified_views = None
        observability = "unobservable"
        traffic_warning = "exact path was absent from the retained Popular-content rows; this is not zero"
    else:
        qualified_views = None
        observability = "not-observed"
        traffic_warning = "Popular-content evidence was not checked at this checkpoint"

    unsafe = any(
        item["safety_disposition"] == "sensitive-or-uncertain"
        for item in observation["issue_observations"]
    )
    dispositions: list[dict[str, object]] = []
    seen_authors: set[str] = set()
    qualifying = 0
    commissioning = 0
    for item in sorted(
        observation["issue_observations"],
        key=lambda value: (value["created_at"], value["issue_number"]),
    ):
        if item["safety_disposition"] == "sensitive-or-uncertain":
            dispositions.append(
                {"issue_url": item["issue_url"], "qualifying": False, "reason": "privacy-halt"}
            )
            continue
        author_key = item["author_login"].casefold()
        reasons: list[str] = []
        if item["actor_type"] != "user":
            reasons.append("non-user-or-unknown-actor")
        if author_key == experiment.owner_login.casefold():
            reasons.append("repository-owner")
        if item["form_source_sha256"] != experiment.issue_form_sha256:
            reasons.append("frozen-form-mismatch")
        if item["boundary_acknowledgement"] != "yes":
            reasons.append("boundary-not-acknowledged")
        if item["outcome_disposition"] != "generic-in-scope":
            reasons.append("outcome-not-generic-in-scope")
        if not (experiment.window_start <= item["created_at"] < experiment.window_end):
            reasons.append("outside-window")
        if author_key in seen_authors:
            reasons.append("duplicate-account")
        is_qualifying = not reasons
        if is_qualifying:
            qualifying += 1
            if item["intent"] == "future-private-route":
                commissioning += 1
        seen_authors.add(author_key)
        dispositions.append(
            {
                "issue_url": item["issue_url"],
                "qualifying": is_qualifying,
                "reason": "qualifying-unverified-signal" if is_qualifying else ",".join(reasons),
            }
        )

    final = next(
        (item for item in traffic if item["checkpoint"] == "day14-refresh"), None
    )
    if unsafe:
        state = "privacy-halted"
        channel_result = "privacy-halted"
    elif not observation["configuration_observation"]["matches_frozen_configuration"]:
        state = "restart-required"
        channel_result = "restart-required"
    elif as_of < experiment.window_end:
        state = "active"
        channel_result = "observation-in-progress"
    elif final is None or final["row_state"] == "not-checked":
        state = "incomplete"
        channel_result = "missing-final-observation"
    else:
        state = "evaluated"
        final_preview_count = sum(
            final["retained_window_start"] <= item["captured_at"] <= final["retained_window_end"]
            for item in observation["owner_preview_events"]
        )
        final_views = (
            max(0, final["raw_views"] - final_preview_count)
            if final["row_state"] == "present"
            else None
        )
        if qualifying == 0 or (final_views is not None and final_views < 10):
            channel_result = "insufficient-signal"
        elif final["row_state"] == "absent":
            channel_result = "inconclusive-views"
        elif final["row_state"] == "present" and final_views >= 10:
            channel_result = "channel-threshold-met"
        else:
            channel_result = "missing-final-observation"

    return {
        "schema_version": SCHEMA_VERSION,
        "component": {"name": "support-channel-observation", "version": COMPONENT_VERSION},
        "claim_boundary": CLAIM_BOUNDARY,
        "experiment": {
            "experiment_id": experiment.experiment_id,
            "record_id": observation["record_id"],
            "source_mode": SOURCE_MODE,
            "repository": experiment.repository,
            "target_commit": experiment.target_commit,
            "entry_path": experiment.entry_path,
            "entry_url": experiment.entry_url,
            "release_url": experiment.release_url,
            "window_start": experiment.window_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "window_end": experiment.window_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "final_capture_deadline": experiment.final_capture_deadline.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "configuration_sha256": experiment.config_sha256,
            "configuration_matches": observation["configuration_observation"][
                "matches_frozen_configuration"
            ],
            "captured_at": observation["captured_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "as_of": as_of.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "state": state,
        "traffic": {
            "latest_checkpoint": latest["checkpoint"],
            "row_state": latest["row_state"],
            "raw_views": raw_views,
            "owner_previews_through_checkpoint": preview_count,
            "qualified_views": qualified_views,
            "view_observability": observability,
            "retained_window_start": (
                latest["retained_window_start"].strftime("%Y-%m-%dT%H:%M:%SZ")
                if latest["retained_window_start"] is not None
                else None
            ),
            "retained_window_end": (
                latest["retained_window_end"].strftime("%Y-%m-%dT%H:%M:%SZ")
                if latest["retained_window_end"] is not None
                else None
            ),
            "warning": traffic_warning,
        },
        "interest": {
            "raw_issue_observations": len(observation["issue_observations"]),
            "qualifying_unverified_signals": qualifying,
            "future_private_route_selections": commissioning,
            "dispositions": dispositions,
        },
        "channel_result": channel_result,
        "checkout_authorized": False,
    }


def _code(value: object) -> str:
    pieces: list[str] = []
    for character in str(value):
        if unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}:
            pieces.append(f"\\u{ord(character):04x}")
        else:
            pieces.append(character)
    return f"<code>{html.escape(''.join(pieces), quote=True)}</code>"


def render_markdown(report: dict[str, object]) -> str:
    traffic = report["traffic"]
    interest = report["interest"]
    json_sha256 = hashlib.sha256((json.dumps(report, indent=2) + "\n").encode("utf-8")).hexdigest()
    lines = [
        "# Support channel observation",
        "",
        f"> {html.escape(str(report['claim_boundary']))}",
        "",
        f"- Experiment: {_code(report['experiment']['experiment_id'])}",
        f"- State: **{html.escape(str(report['state']))}**",
        f"- Channel result: **{html.escape(str(report['channel_result']))}**",
        f"- Source mode: {_code(report['experiment']['source_mode'])}",
        f"- As of: {_code(report['experiment']['as_of'])}",
        f"- Canonical JSON SHA-256: {_code(json_sha256)}",
        f"- Traffic row: {_code(traffic['row_state'])}",
        f"- Raw views: {_code(traffic['raw_views'])}",
        f"- Qualified views: {_code(traffic['qualified_views'])}",
        f"- View observability: {_code(traffic['view_observability'])}",
        f"- Qualifying unverified signals: {interest['qualifying_unverified_signals']}",
        f"- Future-private-route selections: {interest['future_private_route_selections']}",
        "- Checkout authorized: **no**",
    ]
    if traffic["warning"]:
        lines.extend(["", f"> {html.escape(str(traffic['warning']))}"])
    if interest["dispositions"]:
        lines.extend(["", "| Public issue | Qualifying | Controlled reason |", "|---|---|---|"])
        for item in interest["dispositions"]:
            url = html.escape(str(item["issue_url"]), quote=True)
            lines.append(
                f"| [issue]({url}) | {'yes' if item['qualifying'] else 'no'} | "
                f"{_code(item['reason'])} |"
            )
    return "\n".join(lines) + "\n"


def _linklike(path: Path) -> bool:
    is_junction = getattr(os.path, "isjunction", lambda _value: False)
    return path.is_symlink() or bool(is_junction(path))


def _assert_safe_output_parent(parent: Path) -> None:
    absolute = Path(os.path.abspath(parent))
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        try:
            metadata = current.lstat()
        except OSError as error:
            raise ValueError("output parent must already exist") from error
        if _linklike(current):
            raise ValueError("output path cannot traverse a symlink or junction")
        if current == absolute and not stat.S_ISDIR(metadata.st_mode):
            raise ValueError("output parent must be a directory")


def _write_outputs_staged(outputs: list[tuple[Path, str]]) -> None:
    """Stage all outputs, then atomically replace each destination.

    There is no portable multi-file filesystem transaction. A replacement failure is returned to
    the caller, which must regenerate the complete pair; Markdown carries the canonical JSON hash
    so consumers can detect a mixed pair.
    """
    staged: list[tuple[str, Path]] = []
    try:
        for destination, content in outputs:
            _assert_safe_output_parent(destination.parent)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
            )
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            staged.append((temporary_name, destination))
        for _temporary_name, destination in staged:
            _assert_safe_output_parent(destination.parent)
            if destination.exists() and _linklike(destination):
                raise ValueError("existing output changed to a symlink or junction")
        for temporary_name, destination in staged:
            os.replace(temporary_name, destination)
    finally:
        for temporary_name, _destination in staged:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass


def _assert_paths(
    inputs: list[tuple[Path, FileIdentity]], outputs: list[Path]
) -> None:
    resolved_inputs = [path.resolve(strict=True) for path, _identity_value in inputs]
    resolved_outputs = [path.resolve(strict=False) for path in outputs]
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise ValueError("JSON and Markdown outputs must use different paths")
    input_inodes: set[tuple[int, int]] = set()
    for path, expected_identity in inputs:
        inspected = path.lstat()
        if (
            _linklike(path)
            or not stat.S_ISREG(inspected.st_mode)
            or _identity(inspected) != expected_identity
        ):
            raise ValueError("input changed after safe validation")
        input_inodes.add((inspected.st_dev, inspected.st_ino))
    for output, resolved in zip(outputs, resolved_outputs, strict=True):
        if resolved in resolved_inputs:
            raise ValueError("output path cannot replace an input")
        if output.exists():
            inspected = output.lstat()
            if output.is_symlink() or not stat.S_ISREG(inspected.st_mode):
                raise ValueError("existing output must be a nonsymlink regular file")
            if (inspected.st_dev, inspected.st_ino) in input_inodes:
                raise ValueError("output path aliases an input file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m support_eval_lab.observation")
    parser.add_argument("experiment", help="strict experiment configuration JSON")
    parser.add_argument("observation", help="strict cumulative observation JSON")
    parser.add_argument("--as-of", required=True, help="canonical second-precision UTC time")
    parser.add_argument("--json-out", help="write deterministic JSON report")
    parser.add_argument("--markdown-out", help="write deterministic Markdown report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_paths = [Path(args.experiment), Path(args.observation)]
    outputs = [Path(value) for value in (args.json_out, args.markdown_out) if value]
    experiment = load_experiment(input_paths[0])
    observation = load_observation(input_paths[1], experiment)
    _assert_paths(
        [
            (input_paths[0], experiment.source_identity),
            (input_paths[1], observation["source_identity"]),
        ],
        outputs,
    )
    report = build_report(experiment, observation, as_of=_timestamp(args.as_of, "as_of"))
    serialized = json.dumps(report, indent=2) + "\n"
    output_content: list[tuple[Path, str]] = []
    if args.json_out:
        output_content.append((Path(args.json_out), serialized))
    if args.markdown_out:
        output_content.append((Path(args.markdown_out), render_markdown(report)))
    if output_content:
        _write_outputs_staged(output_content)
    if not outputs:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
