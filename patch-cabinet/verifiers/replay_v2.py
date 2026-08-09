"""Immutable schema-2 replay adapter for Patch Cabinet evidence bundles."""

from __future__ import annotations

import hashlib
import html
import json
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any
from types import ModuleType


MAX_REPLAY_FILE_BYTES = 2_000_000


def _read_limited_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{path.name}: replay input must be a nonsymlink regular file")
    with path.open("rb") as stream:
        payload = stream.read(MAX_REPLAY_FILE_BYTES + 1)
    if len(payload) > MAX_REPLAY_FILE_BYTES:
        raise ValueError(f"{path.name}: replay input exceeds its byte limit")
    return payload


def _reject_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key in replay input")
        result[key] = value
    return result


def _reject_constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant in replay input")


def _load_json(path: Path) -> object:
    return json.loads(
        _read_limited_bytes(path).decode("utf-8"),
        object_pairs_hook=_reject_duplicate_object,
        parse_constant=_reject_constant,
    )


def _code(value: object) -> str:
    pieces: list[str] = []
    for character in str(value):
        if character == "\r":
            pieces.append("\\r")
        elif character == "\n":
            pieces.append("\\n")
        elif character == "\t":
            pieces.append("\\t")
        elif unicodedata.category(character) in {"Cc", "Cf"} or character in {
            "\u2028",
            "\u2029",
        }:
            pieces.append(
                f"\\u{ord(character):04x}"
                if ord(character) <= 0xFFFF
                else f"\\U{ord(character):08x}"
            )
        else:
            pieces.append(character)
    return f"<code>{html.escape(''.join(pieces), quote=True)}</code>"


def _render_markdown(
    evaluations: list[Any],
    *,
    source_label: str,
    engine_version: str,
    policy_version: str,
    as_of: str,
    evaluation_mode: str,
    policy_sha256: str,
) -> str:
    lines = [
        "# Patch Cabinet candidate ranking",
        "",
        f"Input label: {_code(source_label)}",
        f"Engine: {_code(f'patch-cabinet {engine_version}')}",
        f"Policy: {_code(policy_version)}",
        f"Policy as-of: {_code(as_of)}",
        f"Evaluation mode: {_code(evaluation_mode)}",
        f"Policy source SHA-256: {_code(policy_sha256)}",
        "",
        "> A score measures Season 1 fit, not project quality. Facts require manual verification.",
        "",
        "| Rank | Repository | Status | Score | Observed | Commit |",
        "|---:|---|---|---:|---|---|",
    ]
    for index, item in enumerate(evaluations, start=1):
        commit = str(item.evidence["commit_sha"])
        short_commit = commit[:12] if commit else "unrecorded"
        score = str(item.score) if item.eligible else "—"
        lines.append(
            f"| {index} | {_code(item.repository)} | {item.band} | {score} | "
            f"{_code(item.evidence['observed_at'])} | {_code(short_commit)} |"
        )

    for item in evaluations:
        lines.extend(["", f"## {_code(item.repository)}", ""])
        lines.append(f"- Eligibility: **{'yes' if item.eligible else 'no'}**")
        lines.append(f"- Band: {_code(item.band)}")
        lines.append(f"- Score: {_code(item.score)}")
        lines.append(f"- License: {_code(item.evidence['license_spdx'])}")
        lines.append(f"- Issue: {_code(item.evidence['issue_url'])}")
        lines.append("- Reasons:")
        lines.extend(f"  - {reason}" for reason in item.reasons)
        if item.cautions:
            lines.append("- Cautions:")
            lines.extend(f"  - {caution}" for caution in item.cautions)
        if item.score_trace:
            lines.append("- Score trace:")
            lines.extend(
                f"  - {html.escape(str(component['rule']))}: {component['delta']:+d}"
                for component in item.score_trace
            )

    return "\n".join(lines) + "\n"


def replay_bundle(
    *,
    manifest_path: Path,
    policy_path: Path,
    markdown_path: Path,
    expected: dict[str, Any],
    policy_module: ModuleType,
) -> None:
    """Replay one receipted bundle under its registered historical environment."""

    manifest = _load_json(manifest_path)
    recorded = _load_json(policy_path)
    if type(manifest) is not list or not manifest:
        raise ValueError(f"{manifest_path.name}: manifest must be a nonempty array")
    if type(recorded) is not dict:
        raise ValueError(f"{policy_path.name}: policy artifact must be an object")

    raw_as_of = recorded.get("policy", {}).get("as_of")
    if type(raw_as_of) is not str:
        raise ValueError(f"{policy_path.name}: policy date is not a string")
    try:
        fixed_day = date.fromisoformat(raw_as_of)
    except ValueError as error:
        raise ValueError(f"{policy_path.name}: invalid policy date") from error
    if fixed_day.isoformat() != raw_as_of:
        raise ValueError(f"{policy_path.name}: policy date is not canonical")

    class ReplayDate(date):
        @classmethod
        def today(cls) -> ReplayDate:
            return cls(fixed_day.year, fixed_day.month, fixed_day.day)

    policy_source = Path(policy_module.__file__).resolve(strict=True)
    policy_sha256 = hashlib.sha256(policy_source.read_bytes()).hexdigest()
    if policy_sha256 != expected["policy"]["source_sha256"]:
        raise ValueError(f"{policy_path.name}: registered policy source digest differs")

    original_date = policy_module.date
    policy_module.date = ReplayDate
    try:
        replay_as_of = ReplayDate(fixed_day.year, fixed_day.month, fixed_day.day)
        evaluations = policy_module.evaluate_candidates(
            manifest,
            excluded_repositories=(),
            as_of=replay_as_of,
            evaluation_mode=recorded["policy"]["evaluation_mode"],
        )
    finally:
        policy_module.date = original_date

    expected_envelope = {
        "schema_version": expected["output_schema_version"],
        "engine": {
            "name": expected["engine_name"],
            "version": expected["engine_version"],
        },
        "policy": {
            "version": expected["policy"]["version"],
            "source_sha256": policy_sha256,
            "as_of": raw_as_of,
            "evaluation_mode": recorded["policy"]["evaluation_mode"],
        },
        "dependencies": expected["dependencies"],
        "source_label": manifest_path.name,
        "results": [item.to_dict() for item in evaluations],
    }
    expected_json = (json.dumps(expected_envelope, indent=2) + "\n").encode("utf-8")
    if _read_limited_bytes(policy_path) != expected_json:
        raise ValueError(f"{policy_path.name}: canonical JSON does not replay exactly")

    expected_markdown = _render_markdown(
        evaluations,
        source_label=manifest_path.name,
        engine_version=expected["engine_version"],
        policy_version=expected["policy"]["version"],
        as_of=raw_as_of,
        evaluation_mode=recorded["policy"]["evaluation_mode"],
        policy_sha256=policy_sha256,
    ).encode("utf-8")
    if _read_limited_bytes(markdown_path) != expected_markdown:
        raise ValueError(f"{markdown_path.name}: canonical Markdown does not replay exactly")
