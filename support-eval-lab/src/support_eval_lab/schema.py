"""Strict, bounded schemas for synthetic support-agent regression fixtures."""

from __future__ import annotations

import json
import os
import re
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAX_FILE_BYTES = 1_000_000
MAX_CASES = 100
MAX_TURNS = 8
MAX_CONTEXT_ITEMS = 12
MAX_LIST_ITEMS = 20
MAX_TEXT_CHARS = 8_000
MAX_JSON_DEPTH = 32
IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
ALLOWED_CATEGORIES = {
    "ambiguity",
    "boundary",
    "escalation",
    "grounding",
    "malformed-input",
    "multi-turn",
    "privacy",
    "tone",
    "uncertainty",
    "workflow",
}
ALLOWED_ACTIONS = {"answer", "clarify", "escalate", "guide", "refuse"}
ALLOWED_HUMAN_CHECKS = {"context-followed", "tone-respectful", "uncertainty-honest"}
HUMAN_RESULTS = {"pass", "fail", "not-reviewed"}
OBVIOUS_SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:sk|ghp|github_pat)-?[A-Za-z0-9_]{12,}\b", re.IGNORECASE),
    re.compile(r"\b(?:password|api[_-]?key|authorization)\s*[:=]", re.IGNORECASE),
)


@dataclass(frozen=True)
class ExpectedBehavior:
    action: str
    must_include: tuple[str, ...]
    must_exclude: tuple[str, ...]
    citations: tuple[str, ...]
    human_checks: tuple[str, ...]


@dataclass(frozen=True)
class Case:
    case_id: str
    category: str
    turns: tuple[str, ...]
    context: dict[str, str]
    expected: ExpectedBehavior


@dataclass(frozen=True)
class Output:
    case_id: str
    response: str
    action: str
    citations: tuple[str, ...]
    human_review: dict[str, str]


@dataclass(frozen=True)
class Run:
    run_id: str
    mode: str
    outputs: dict[str, Output]


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
    raise ValueError("JSON numbers are not part of this schema")


def _validate_json_depth(line: str, *, maximum: int = MAX_JSON_DEPTH) -> None:
    depth = 0
    in_string = False
    escaped = False
    for character in line:
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
            if depth > maximum:
                raise ValueError(f"JSON nesting exceeds the {maximum}-level limit")
        elif character in "]}":
            depth -= 1


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
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
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError(f"{path.name}: input changed during safe open")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError(f"{path.name}: input exceeds {MAX_FILE_BYTES} bytes")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{path.name}: input must be UTF-8") from error
    lines = text.splitlines()
    if not lines or len(lines) > MAX_CASES:
        raise ValueError(f"{path.name}: input must contain 1 to {MAX_CASES} records")
    if any(not line.strip() for line in lines):
        raise ValueError(f"{path.name}: blank JSONL records are not allowed")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        try:
            _validate_json_depth(line)
            record = json.loads(
                line,
                object_pairs_hook=_reject_duplicate_object,
                parse_constant=_reject_constant,
                parse_float=_reject_number,
                parse_int=_reject_number,
            )
        except (json.JSONDecodeError, RecursionError, ValueError) as error:
            raise ValueError(f"{path.name}:{line_number}: invalid strict JSON: {error}") from error
        if type(record) is not dict:
            raise ValueError(f"{path.name}:{line_number}: record must be an object")
        records.append(record)
    return records


def _identifier(value: object, field: str) -> str:
    if type(value) is not str or IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"{field} must be a lowercase hyphenated identifier")
    return value


def _text(value: object, field: str) -> str:
    if type(value) is not str or not value.strip() or len(value) > MAX_TEXT_CHARS:
        raise ValueError(
            f"{field} must be a nonempty string of at most {MAX_TEXT_CHARS} characters"
        )
    if any(
        unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
        for character in value
    ):
        raise ValueError(f"{field} cannot contain control or formatting characters")
    if any(pattern.search(value) for pattern in OBVIOUS_SENSITIVE_PATTERNS):
        raise ValueError(f"{field} resembles prohibited sensitive data")
    return value


def _string_list(
    value: object,
    field: str,
    *,
    identifiers: bool = False,
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if type(value) is not list or len(value) > MAX_LIST_ITEMS or (not allow_empty and not value):
        raise ValueError(f"{field} must be a bounded list")
    converted = tuple(
        _identifier(item, field) if identifiers else _text(item, field) for item in value
    )
    normalized = [item.casefold() for item in converted]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{field} cannot contain duplicate values")
    return converted


def _parse_case(record: dict[str, Any]) -> Case:
    expected_fields = {"schema_version", "case_id", "category", "turns", "context", "expected"}
    if set(record) != expected_fields or record["schema_version"] != "1":
        raise ValueError("case record fields or schema version differ")
    case_id = _identifier(record["case_id"], "case_id")
    category = _identifier(record["category"], "category")
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"{case_id}: category is outside the prototype taxonomy")
    turns = _string_list(record["turns"], f"{case_id}.turns", allow_empty=False)
    if len(turns) > MAX_TURNS:
        raise ValueError(f"{case_id}: too many conversation turns")

    raw_context = record["context"]
    if type(raw_context) is not dict or not raw_context or len(raw_context) > MAX_CONTEXT_ITEMS:
        raise ValueError(f"{case_id}.context must be a nonempty bounded object")
    context: dict[str, str] = {}
    for raw_key, raw_value in raw_context.items():
        key = _identifier(raw_key, f"{case_id}.context key")
        context[key] = _text(raw_value, f"{case_id}.context.{key}")

    raw_expected = record["expected"]
    expected_fields = {
        "action",
        "must_include",
        "must_exclude",
        "citations",
        "human_checks",
    }
    if type(raw_expected) is not dict or set(raw_expected) != expected_fields:
        raise ValueError(f"{case_id}.expected fields differ")
    action = _identifier(raw_expected["action"], f"{case_id}.expected.action")
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"{case_id}: expected action is unsupported")
    must_include = _string_list(
        raw_expected["must_include"], f"{case_id}.expected.must_include"
    )
    must_exclude = _string_list(
        raw_expected["must_exclude"], f"{case_id}.expected.must_exclude"
    )
    if {item.casefold() for item in must_include} & {
        item.casefold() for item in must_exclude
    }:
        raise ValueError(f"{case_id}: required and forbidden phrases overlap")
    citations = _string_list(
        raw_expected["citations"],
        f"{case_id}.expected.citations",
        identifiers=True,
    )
    if not set(citations) <= set(context):
        raise ValueError(f"{case_id}: expected citation is absent from context")
    human_checks = _string_list(
        raw_expected["human_checks"],
        f"{case_id}.expected.human_checks",
        identifiers=True,
        allow_empty=False,
    )
    if not set(human_checks) <= ALLOWED_HUMAN_CHECKS:
        raise ValueError(f"{case_id}: human-review check is unsupported")
    return Case(
        case_id=case_id,
        category=category,
        turns=turns,
        context=context,
        expected=ExpectedBehavior(
            action=action,
            must_include=must_include,
            must_exclude=must_exclude,
            citations=citations,
            human_checks=human_checks,
        ),
    )


def load_cases(path: Path) -> list[Case]:
    cases = [_parse_case(record) for record in _read_jsonl(path)]
    identifiers = [case.case_id for case in cases]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("case_id values must be unique")
    return cases


def _parse_output(
    record: dict[str, Any],
    cases: dict[str, Case],
    *,
    allow_sanitized_local: bool,
) -> tuple[str, str, Output]:
    expected_fields = {
        "schema_version",
        "run_id",
        "mode",
        "case_id",
        "response",
        "action",
        "citations",
        "human_review",
    }
    if set(record) != expected_fields or record["schema_version"] != "1":
        raise ValueError("run record fields or schema version differ")
    run_id = _identifier(record["run_id"], "run_id")
    mode = _identifier(record["mode"], "mode")
    allowed_modes = {"synthetic-mock"}
    if allow_sanitized_local:
        allowed_modes.add("sanitized-local")
    if mode not in allowed_modes:
        raise ValueError(
            "run mode requires synthetic-mock or an explicit sanitized-local acknowledgement"
        )
    case_id = _identifier(record["case_id"], "case_id")
    if case_id not in cases:
        raise ValueError(f"{case_id}: run output has no matching case")
    response = _text(record["response"], f"{case_id}.response")
    action = _identifier(record["action"], f"{case_id}.action")
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"{case_id}: observed action is unsupported")
    citations = _string_list(
        record["citations"], f"{case_id}.citations", identifiers=True
    )
    if not set(citations) <= set(cases[case_id].context):
        raise ValueError(f"{case_id}: run cites context absent from the case")
    raw_human = record["human_review"]
    expected_checks = set(cases[case_id].expected.human_checks)
    if type(raw_human) is not dict or set(raw_human) != expected_checks:
        raise ValueError(f"{case_id}: human review must cover exactly the declared checks")
    human_review: dict[str, str] = {}
    for check, result in raw_human.items():
        check_id = _identifier(check, f"{case_id}.human_review key")
        if type(result) is not str or result not in HUMAN_RESULTS:
            raise ValueError(f"{case_id}.{check_id}: invalid human-review result")
        human_review[check_id] = result
    return run_id, mode, Output(
        case_id=case_id,
        response=response,
        action=action,
        citations=citations,
        human_review=human_review,
    )


def load_run(path: Path, cases: list[Case], *, allow_sanitized_local: bool = False) -> Run:
    case_map = {case.case_id: case for case in cases}
    parsed = [
        _parse_output(
            record,
            case_map,
            allow_sanitized_local=allow_sanitized_local,
        )
        for record in _read_jsonl(path)
    ]
    run_ids = {run_id for run_id, _mode, _output in parsed}
    modes = {mode for _run_id, mode, _output in parsed}
    if len(run_ids) != 1 or len(modes) != 1:
        raise ValueError(f"{path.name}: every record must share one run_id and mode")
    outputs: dict[str, Output] = {}
    for _run_id, _mode, output in parsed:
        if output.case_id in outputs:
            raise ValueError(f"{path.name}: duplicate output for {output.case_id}")
        outputs[output.case_id] = output
    if set(outputs) != set(case_map):
        missing = sorted(set(case_map) - set(outputs))
        extra = sorted(set(outputs) - set(case_map))
        raise ValueError(f"{path.name}: run coverage differs; missing={missing}, extra={extra}")
    return Run(run_id=run_ids.pop(), mode=modes.pop(), outputs=outputs)
