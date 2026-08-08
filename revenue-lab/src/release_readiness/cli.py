"""Linux Release Readiness Lab command-line interface."""

from __future__ import annotations

import argparse
import html
import json
import unicodedata
from pathlib import Path
from typing import Sequence

from .audit import REPORT_SCHEMA_VERSION, RULES_VERSION, Audit, audit_repository
from .version import __version__


DISCLAIMER = (
    "This report is a static maintenance-readiness observation with the provenance status "
    "shown above. Caller-supplied metadata does not establish repository or commit identity. "
    "The collector reads only the supplied trusted-local directory and invokes no network "
    "client, subprocess, Git command, or target code. It does not test deployed services or "
    "constitute a security audit, penetration test, certification, legal opinion, or guarantee. "
    "Findings may be incomplete or become stale."
)


def _visible(value: object) -> str:
    raw = str(value).encode("utf-8", errors="backslashreplace").decode("utf-8")
    pieces: list[str] = []
    for character in raw:
        if character == "\n":
            pieces.append("\\n")
        elif character == "\r":
            pieces.append("\\r")
        elif character == "\t":
            pieces.append("\\t")
        elif (
            unicodedata.category(character) in {"Cc", "Cf"}
            or character in {"\u2028", "\u2029"}
        ):
            codepoint = ord(character)
            if codepoint <= 0xFF:
                pieces.append(f"\\x{codepoint:02x}")
            elif codepoint <= 0xFFFF:
                pieces.append(f"\\u{codepoint:04x}")
            else:
                pieces.append(f"\\U{codepoint:08x}")
        else:
            pieces.append(character)
    return "".join(pieces)


def _code(value: object) -> str:
    return f"<code>{html.escape(_visible(value), quote=True)}</code>"


def _text(value: object) -> str:
    return html.escape(_visible(value), quote=True)


def render_markdown(audit: Audit) -> str:
    counts = {
        status: sum(finding.status == status for finding in audit.findings)
        for status in ("signal_detected", "not_detected", "potential_gap", "manual_review")
    }
    lines = [
        "# Linux release-readiness evidence report",
        "",
        f"- Report schema: {_code(REPORT_SCHEMA_VERSION)}",
        f"- Collector: {_code(f'linux-release-readiness {__version__}')}",
        f"- Rules: {_code(RULES_VERSION)}",
        f"- Rules source SHA-256: {_code(audit.rules_sha256)}",
        f"- Declared repository URL: {_code(audit.repository_url)}",
        f"- Declared commit: {_code(audit.commit_sha)}",
        f"- Declared observation date: {_code(audit.observed_at)}",
        f"- Observation source: {_code(audit.observation_source)}",
        f"- Provenance: {_code(audit.provenance_status)}",
        "- Provenance details:",
        *(f"  - {_code(detail)}" for detail in audit.provenance_details),
        f"- Files considered: {audit.files_considered}",
        "- Target code executed: no",
        "- Repository acquisition performed by the collector: no",
        "- Git or target-project commands invoked by the collector: no",
        "- Storage location verified as local rather than network-backed: no",
        "",
        f"> {DISCLAIMER}",
        "",
        "## Summary",
        "",
        f"- Signals detected: {counts['signal_detected']}",
        f"- Signals not detected: {counts['not_detected']}",
        f"- Potential gaps: {counts['potential_gap']}",
        f"- Manual-review-only results: {counts['manual_review']}",
        "",
        "No aggregate grade is assigned. Applicability and repair value require "
        "maintainer judgment.",
    ]
    for finding in audit.findings:
        lines.extend(
            [
                "",
                f"## {_text(finding.title)}",
                "",
                f"- ID: {_code(finding.identifier)}",
                f"- Status: {_code(finding.status)}",
                f"- Review priority: {_code(finding.review_priority)}",
                "- Evidence:",
            ]
        )
        lines.extend(f"  - {_code(item)}" for item in finding.evidence)
        if not finding.evidence:
            lines.append("  - none detected by the static collector")
        lines.append(f"- Next step: {_text(finding.recommendation)}")
    return "\n".join(lines) + "\n"


def _audit(args: argparse.Namespace) -> int:
    result = audit_repository(
        Path(args.path),
        repository_url=args.repository_url,
        commit_sha=args.commit_sha,
        observed_at=args.observed_at,
        unverified_demo=args.unverified_demo,
    )
    if args.json_out:
        destination = Path(args.json_out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result.to_dict(), indent=2) + "\n")
    if args.markdown_out:
        destination = Path(args.markdown_out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(render_markdown(result))
    if not args.json_out and not args.markdown_out:
        print(json.dumps(result.to_dict(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="release-readiness")
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="collect static release-readiness evidence")
    audit.add_argument("path", help="synthetic or trusted project-owned demo directory")
    audit.add_argument("--repository-url", required=True)
    audit.add_argument("--commit-sha", required=True)
    audit.add_argument(
        "--observed-at",
        required=True,
        help="declared YYYY-MM-DD date for this explicitly unverified demo",
    )
    audit.add_argument("--json-out")
    audit.add_argument("--markdown-out")
    audit.add_argument(
        "--unverified-demo",
        action="store_true",
        help="acknowledge that only a synthetic or trusted-local unverified demo is supported",
    )
    audit.set_defaults(handler=_audit)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
