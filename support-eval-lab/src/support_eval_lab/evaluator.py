"""Deterministic comparison of two structured support-agent runs."""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any

from .schema import Case, Output, Run


ENGINE_NAME = "support-eval-lab"
ENGINE_VERSION = "0.1.0"
OUTPUT_SCHEMA_VERSION = "1"


def _evaluate(case: Case, output: Output) -> dict[str, Any]:
    response = output.response.casefold()
    deterministic_failures: list[str] = []
    if output.action != case.expected.action:
        deterministic_failures.append(
            f"action expected {case.expected.action}; observed {output.action}"
        )
    for phrase in case.expected.must_include:
        if phrase.casefold() not in response:
            deterministic_failures.append(f"required phrase absent: {phrase}")
    for phrase in case.expected.must_exclude:
        if phrase.casefold() in response:
            deterministic_failures.append(f"forbidden phrase present: {phrase}")
    if set(output.citations) != set(case.expected.citations):
        deterministic_failures.append(
            "citations differ from the case's exact expected context set"
        )

    human_failures = sorted(
        check for check, result in output.human_review.items() if result == "fail"
    )
    human_pending = sorted(
        check for check, result in output.human_review.items() if result == "not-reviewed"
    )
    if deterministic_failures or human_failures:
        status = "fail"
    elif human_pending:
        status = "review"
    else:
        status = "pass"
    return {
        "status": status,
        "deterministic_failures": deterministic_failures,
        "human_failures": human_failures,
        "human_pending": human_pending,
        "human_review": dict(sorted(output.human_review.items())),
        "response_sha256": hashlib.sha256(output.response.encode("utf-8")).hexdigest(),
    }


def _summary(results: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(result["status"] for result in results)
    return {status: counts.get(status, 0) for status in ("pass", "review", "fail")}


def compare_runs(cases: list[Case], baseline: Run, candidate: Run) -> dict[str, Any]:
    if baseline.mode != candidate.mode or baseline.mode not in {
        "synthetic-mock",
        "sanitized-local",
    }:
        raise ValueError("comparison requires two runs with the same allowed mode")
    if baseline.run_id == candidate.run_id:
        raise ValueError("baseline and candidate run_id values must differ")

    case_results: list[dict[str, Any]] = []
    regressions: list[str] = []
    improvements: list[str] = []
    severity = {"pass": 0, "review": 1, "fail": 2}
    for case in cases:
        baseline_result = _evaluate(case, baseline.outputs[case.case_id])
        candidate_result = _evaluate(case, candidate.outputs[case.case_id])
        if severity[candidate_result["status"]] > severity[baseline_result["status"]]:
            change = "regression"
            regressions.append(case.case_id)
        elif severity[candidate_result["status"]] < severity[baseline_result["status"]]:
            change = "improvement"
            improvements.append(case.case_id)
        elif baseline_result["status"] == candidate_result["status"]:
            change = "unchanged"
        else:
            change = "changed-needs-review"
        case_results.append(
            {
                "case_id": case.case_id,
                "category": case.category,
                "change": change,
                "baseline": baseline_result,
                "candidate": candidate_result,
            }
        )

    baseline_results = [item["baseline"] for item in case_results]
    candidate_results = [item["candidate"] for item in case_results]
    claim_boundary = (
        "Demonstration only; no real model, customer, policy, safety, compliance, or "
        "production-readiness claim."
        if baseline.mode == "synthetic-mock"
        else (
            "Local sanitized test output supplied by the operator; input provenance, reviewer "
            "identity, factual correctness, safety, compliance, and production readiness are "
            "not verified."
        )
    )
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "evaluation_mode": baseline.mode,
        "claim_boundary": claim_boundary,
        "baseline": {"run_id": baseline.run_id, "summary": _summary(baseline_results)},
        "candidate": {"run_id": candidate.run_id, "summary": _summary(candidate_results)},
        "comparison": {
            "classification": (
                "regression-detected" if regressions else "no-regression-in-this-sample"
            ),
            "regressions": regressions,
            "improvements": improvements,
        },
        "cases": case_results,
    }
