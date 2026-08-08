"""Command-line interface for the Patch Cabinet policy engine."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import unicodedata
from datetime import date
from pathlib import Path
from typing import Sequence

from . import __version__, policy as policy_module
from .engine import ENGINE_NAME, OUTPUT_SCHEMA_VERSION, validate_runtime_dependencies
from .policy import (
    REPOSITORY_NAME,
    Evaluation,
    SEASON_POLICY_VERSION,
    evaluate_candidates,
)


MAX_MANIFEST_BYTES = 2_000_000
MAX_CANDIDATES = 200
MAX_EXCLUSIONS_BYTES = 100_000
MAX_EXCLUSIONS = 1_000


def _code(value: object) -> str:
    pieces: list[str] = []
    for character in str(value):
        if character == "\r":
            pieces.append("\\r")
        elif character == "\n":
            pieces.append("\\n")
        elif character == "\t":
            pieces.append("\\t")
        elif unicodedata.category(character) in {"Cc", "Cf"} or character in {"\u2028", "\u2029"}:
            pieces.append(
                f"\\u{ord(character):04x}"
                if ord(character) <= 0xFFFF
                else f"\\U{ord(character):08x}"
            )
        else:
            pieces.append(character)
    return f"<code>{html.escape(''.join(pieces), quote=True)}</code>"


def _reject_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key is not allowed: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-standard JSON constant is not allowed: {value}")


def _render_markdown(
    evaluations: list[Evaluation],
    *,
    source_label: str,
    as_of: str,
    evaluation_mode: str,
    policy_sha256: str,
) -> str:
    lines = [
        "# Patch Cabinet candidate ranking",
        "",
        f"Input label: {_code(source_label)}",
        f"Engine: {_code(f'patch-cabinet {__version__}')}",
        f"Policy: {_code(SEASON_POLICY_VERSION)}",
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


def _score(args: argparse.Namespace) -> int:
    dependencies = validate_runtime_dependencies()
    source = Path(args.input)
    with source.open("rb") as stream:
        raw_payload = stream.read(MAX_MANIFEST_BYTES + 1)
    if len(raw_payload) > MAX_MANIFEST_BYTES:
        raise ValueError(f"candidate manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    payload = json.loads(
        raw_payload.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_object,
        parse_constant=_reject_json_constant,
    )
    if not isinstance(payload, list):
        raise ValueError("candidate file must contain a JSON array")
    if len(payload) > MAX_CANDIDATES:
        raise ValueError(f"candidate file exceeds the {MAX_CANDIDATES}-candidate limit")
    if not all(isinstance(item, dict) for item in payload):
        raise ValueError("every candidate must be a JSON object")

    try:
        policy_as_of = date.fromisoformat(args.as_of)
    except ValueError as error:
        raise ValueError("--as-of must be a valid YYYY-MM-DD date") from error
    if policy_as_of.isoformat() != args.as_of:
        raise ValueError("--as-of must use YYYY-MM-DD")
    if args.historical_demo:
        evaluation_mode = "historical"
    elif policy_as_of != date.today():
        raise ValueError("a past --as-of date requires --historical-demo")
    else:
        evaluation_mode = "live"

    exclusions: list[str] = []
    for exclusion_file in args.exclusions_file:
        exclusions.extend(_load_exclusions(Path(exclusion_file)))
    if not args.exclusions_file and not args.allow_no_local_exclusions:
        raise ValueError(
            "no operator-controlled exclusion file was supplied; pass the project's ignored "
            "file explicitly or use --allow-no-local-exclusions only for a public/synthetic "
            "context with no sponsor exclusions"
        )
    exclusions = sorted(set(exclusions))

    evaluations = evaluate_candidates(
        payload,
        excluded_repositories=exclusions,
        as_of=policy_as_of,
        evaluation_mode=evaluation_mode,
    )
    policy_sha256 = hashlib.sha256(Path(policy_module.__file__).read_bytes()).hexdigest()
    serialized = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": __version__},
        "policy": {
            "version": SEASON_POLICY_VERSION,
            "source_sha256": policy_sha256,
            "as_of": policy_as_of.isoformat(),
            "evaluation_mode": evaluation_mode,
        },
        "dependencies": dependencies,
        "source_label": source.name,
        "results": [item.to_dict() for item in evaluations],
    }

    if args.json_out:
        destination = Path(args.json_out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(serialized, indent=2) + "\n")
    if args.markdown_out:
        destination = Path(args.markdown_out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(
                _render_markdown(
                    evaluations,
                    source_label=source.name,
                    as_of=policy_as_of.isoformat(),
                    evaluation_mode=evaluation_mode,
                    policy_sha256=policy_sha256,
                )
            )
    if not args.json_out and not args.markdown_out:
        print(json.dumps(serialized, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patch-cabinet")
    subparsers = parser.add_subparsers(dest="command", required=True)
    score = subparsers.add_parser("score", help="evaluate a candidate evidence manifest")
    score.add_argument("input", help="path to a JSON array of candidates")
    score.add_argument("--as-of", required=True, help="deterministic policy date in YYYY-MM-DD")
    score.add_argument(
        "--historical-demo",
        action="store_true",
        help="allow a past as-of date; historical results can never be labeled ready",
    )
    score.add_argument("--json-out", help="write structured results to this path")
    score.add_argument("--markdown-out", help="write a human-readable cabinet to this path")
    score.add_argument(
        "--exclusions-file",
        action="append",
        default=[],
        help="operator-controlled ignored exclusion JSON; repeat to union additional files",
    )
    score.add_argument(
        "--allow-no-local-exclusions",
        action="store_true",
        help="permit a public/synthetic run only when no sponsor-local exclusion context exists",
    )
    score.set_defaults(handler=_score)
    return parser


def _load_exclusions(path: Path) -> list[str]:
    with path.open("rb") as stream:
        raw_payload = stream.read(MAX_EXCLUSIONS_BYTES + 1)
    if len(raw_payload) > MAX_EXCLUSIONS_BYTES:
        raise ValueError(f"exclusions file exceeds {MAX_EXCLUSIONS_BYTES} bytes")
    payload = json.loads(
        raw_payload.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_object,
        parse_constant=_reject_json_constant,
    )
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError("exclusions file must contain a JSON array of repository strings")
    if len(payload) > MAX_EXCLUSIONS:
        raise ValueError(f"exclusions file exceeds the {MAX_EXCLUSIONS}-entry limit")
    normalized: list[str] = []
    for item in payload:
        value = item.strip()
        if not REPOSITORY_NAME.fullmatch(value):
            raise ValueError("every exclusion must be a valid owner/name repository string")
        normalized.append(value.casefold())
    return normalized


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
