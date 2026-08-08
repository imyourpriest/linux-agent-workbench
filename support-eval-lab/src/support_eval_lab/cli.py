"""Command-line interface for the synthetic support-agent regression starter."""

from __future__ import annotations

import argparse
import html
import json
import os
import tempfile
from pathlib import Path
from typing import Sequence

from .evaluator import compare_runs
from .schema import load_cases, load_run


def _code(value: object) -> str:
    return f"<code>{html.escape(str(value), quote=True)}</code>"


def _render_markdown(report: dict[str, object]) -> str:
    baseline = report["baseline"]
    candidate = report["candidate"]
    comparison = report["comparison"]
    engine_label = f"{report['engine']['name']} {report['engine']['version']}"
    lines = [
        "# Support-agent regression comparison",
        "",
        f"> {html.escape(report['claim_boundary'])}",
        "",
        f"- Engine: {_code(engine_label)}",
        f"- Mode: {_code(report['evaluation_mode'])}",
        f"- Baseline: {_code(baseline['run_id'])}",
        f"- Candidate: {_code(candidate['run_id'])}",
        f"- Classification: **{html.escape(comparison['classification'])}**",
        "",
        "| Run | Pass | Review | Fail |",
        "|---|---:|---:|---:|",
        (
            f"| Baseline | {baseline['summary']['pass']} | {baseline['summary']['review']} | "
            f"{baseline['summary']['fail']} |"
        ),
        (
            f"| Candidate | {candidate['summary']['pass']} | {candidate['summary']['review']} | "
            f"{candidate['summary']['fail']} |"
        ),
        "",
        "| Case | Category | Baseline | Candidate | Change |",
        "|---|---|---|---|---|",
    ]
    for item in report["cases"]:
        lines.append(
            f"| {_code(item['case_id'])} | {_code(item['category'])} | "
            f"{item['baseline']['status']} | {item['candidate']['status']} | "
            f"{item['change']} |"
        )
    for item in report["cases"]:
        candidate_result = item["candidate"]
        if candidate_result["status"] == "pass":
            continue
        lines.extend(["", f"## {_code(item['case_id'])}", ""])
        if candidate_result["deterministic_failures"]:
            lines.append("- Deterministic failures:")
            lines.extend(
                f"  - {_code(reason)}" for reason in candidate_result["deterministic_failures"]
            )
        if candidate_result["human_failures"]:
            lines.append(
                "- Human-review failures: "
                + ", ".join(_code(value) for value in candidate_result["human_failures"])
            )
        if candidate_result["human_pending"]:
            lines.append(
                "- Human review pending: "
                + ", ".join(_code(value) for value in candidate_result["human_pending"])
            )
    return "\n".join(lines) + "\n"


def _write_atomic(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
        text=True,
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


def _compare(args: argparse.Namespace) -> int:
    input_paths = [Path(args.cases), Path(args.baseline), Path(args.candidate)]
    output_paths = [Path(value) for value in (args.json_out, args.markdown_out) if value]
    resolved_inputs = {path.resolve(strict=True) for path in input_paths}
    resolved_outputs = [path.resolve(strict=False) for path in output_paths]
    if any(path in resolved_inputs for path in resolved_outputs):
        raise ValueError("output paths cannot replace an input file")
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise ValueError("JSON and Markdown outputs must use different paths")

    cases = load_cases(input_paths[0])
    baseline = load_run(
        input_paths[1],
        cases,
        allow_sanitized_local=args.allow_sanitized_local,
    )
    candidate = load_run(
        input_paths[2],
        cases,
        allow_sanitized_local=args.allow_sanitized_local,
    )
    report = compare_runs(cases, baseline, candidate)
    serialized = json.dumps(report, indent=2) + "\n"
    if args.json_out:
        _write_atomic(Path(args.json_out), serialized)
    if args.markdown_out:
        _write_atomic(Path(args.markdown_out), _render_markdown(report))
    if not args.json_out and not args.markdown_out:
        print(serialized, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="support-eval")
    subparsers = parser.add_subparsers(dest="command", required=True)
    synthetic = subparsers.add_parser("compare", help="compare two synthetic example runs")
    local = subparsers.add_parser(
        "compare-local",
        help="compare two locally prepared sanitized runs without persisting response text",
    )

    def add_common_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("cases", help="strict JSONL case file")
        command.add_argument("baseline", help="strict JSONL baseline run")
        command.add_argument("candidate", help="strict JSONL candidate run")
        command.add_argument("--json-out", help="write the structured comparison")
        command.add_argument("--markdown-out", help="write the human-readable comparison")
        command.set_defaults(handler=_compare)

    add_common_arguments(synthetic)
    synthetic.set_defaults(allow_sanitized_local=False)
    add_common_arguments(local)
    local.add_argument(
        "--acknowledge-sanitized-local-input",
        action="store_true",
        required=True,
        help=(
            "allow sanitized-local run records after confirming they contain no private "
            "transcripts, personal data, credentials, regulated content, or confidential material"
        ),
    )
    local.set_defaults(allow_sanitized_local=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
