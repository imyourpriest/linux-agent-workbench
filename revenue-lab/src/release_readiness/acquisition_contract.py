"""Synthetic-only contract scaffold for the D-014 acquisition gate.

This module validates policy records. It does not acquire source, create a sandbox,
or attest that a platform enforced the records.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import uuid
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlsplit


REQUEST_SCHEMA = "d014-acquisition-request-v1"
RECEIPT_SCHEMA = "d014-acquisition-receipt-v2"
SANDBOX_SCHEMA = "d014-analysis-sandbox-v2"
SYNTHETIC_FIXTURE = "project_owned_synthetic"
PLAN_STATUS = "synthetic_policy_shape_checked_no_platform_evidence"
PLATFORM_EVIDENCE_STATUS = "absent"

_PROJECT_FIXTURES = {
    "d014-contract-sha1-v1": (
        "https://example.invalid/cairn/d014-contract-sha1",
        "sha1",
        "a" * 40,
        "project-owned-synthetic/d014-contract-sha1-v1",
    ),
    "d014-contract-sha256-v1": (
        "https://example.invalid/cairn/d014-contract-sha256",
        "sha256",
        "b" * 64,
        "project-owned-synthetic/d014-contract-sha256-v1",
    ),
}

MAX_CPU_COUNT = 1
MAX_CPU_SECONDS = 60
MAX_WALL_SECONDS = 90
MAX_MEMORY_BYTES = 1_073_741_824
MAX_PROCESSES = 1
MAX_ACQUISITION_PROCESSES = 64
MAX_INPUT_BYTES = 536_870_912
MAX_WRITABLE_WORK_BYTES = 67_108_864
MAX_STDOUT_STDERR_BYTES = 1_048_576
MAX_REPORT_BYTES = 2_097_152
MAX_CONTRACT_JSON_BYTES = 65_536
MAX_CONTRACT_JSON_DEPTH = 16
MAX_CONTRACT_JSON_NODES = 1_024
MAX_JSON_INTEGER_DIGITS = 19

_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_ID = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,127}$")
_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_PATH = re.compile(r"^/[A-Za-z0-9._~-]+(?:/[A-Za-z0-9._~-]+)+$")


class GateBlocked(ValueError):
    """Raised when a D-014 contract record fails closed."""


@dataclass(frozen=True)
class CommitIdentity:
    object_format: str
    oid: str

    def to_dict(self) -> dict[str, str]:
        return {"object_format": self.object_format, "oid": self.oid}


@dataclass(frozen=True)
class AcquisitionRequest:
    fixture_id: str
    canonical_https_url: str
    requested_commit: CommitIdentity
    sha256: str


@dataclass(frozen=True)
class SyntheticReceiptAssertions:
    declared_capsule_manifest_sha256: str
    declared_capsule_sha256: str
    declared_analysis_input_bytes: int
    sha256: str


@dataclass(frozen=True)
class SandboxContract:
    sha256: str


@dataclass(frozen=True)
class AnalysisPlan:
    """A contract-test result that is deliberately ineligible for real source."""

    status: str
    platform_evidence_status: str
    real_repository_eligible: bool
    fixture_id: str
    canonical_https_url: str
    requested_commit: CommitIdentity
    declared_capsule_manifest_sha256: str
    declared_capsule_sha256: str
    request_sha256: str
    receipt_sha256: str
    sandbox_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "platform_evidence_status": self.platform_evidence_status,
            "real_repository_eligible": self.real_repository_eligible,
            "fixture_id": self.fixture_id,
            "canonical_https_url": self.canonical_https_url,
            "requested_commit": self.requested_commit.to_dict(),
            "declared_capsule_manifest_sha256": self.declared_capsule_manifest_sha256,
            "declared_capsule_sha256": self.declared_capsule_sha256,
            "request_sha256": self.request_sha256,
            "receipt_sha256": self.receipt_sha256,
            "sandbox_sha256": self.sandbox_sha256,
        }


def load_strict_json(serialized: str) -> dict[str, object]:
    """Load one bounded JSON object while rejecting ambiguous JSON extensions."""

    if type(serialized) is not str:
        raise GateBlocked("json: invalid contract document")
    if len(serialized) > MAX_CONTRACT_JSON_BYTES:
        raise GateBlocked("json: document exceeds character limit")
    try:
        encoded_size = len(serialized.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise GateBlocked("json: invalid Unicode") from error
    if encoded_size > MAX_CONTRACT_JSON_BYTES:
        raise GateBlocked("json: document exceeds byte limit")

    depth = 0
    in_string = False
    escaped = False
    for character in serialized:
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
            if depth > MAX_CONTRACT_JSON_DEPTH:
                raise GateBlocked("json: document exceeds depth limit")
        elif character in "]}":
            depth -= 1
            if depth < 0:
                raise GateBlocked("json: invalid contract document")

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise GateBlocked("json: duplicate field")
            result[key] = value
        return result

    def parse_integer(value: str) -> int:
        digits = value[1:] if value.startswith("-") else value
        if len(digits) > MAX_JSON_INTEGER_DIGITS:
            raise GateBlocked("json: integer exceeds digit limit")
        return int(value)

    def reject_non_integer_number(_value: str) -> object:
        raise GateBlocked("json: unsupported numeric value")

    try:
        result = json.loads(
            serialized,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_non_integer_number,
            parse_float=reject_non_integer_number,
            parse_int=parse_integer,
        )
    except GateBlocked:
        raise
    except (json.JSONDecodeError, RecursionError, TypeError, ValueError) as error:
        raise GateBlocked("json: invalid contract document") from error
    if type(result) is not dict:
        raise GateBlocked("json: top level must be an object")

    nodes = 0
    stack: list[object] = [result]
    while stack:
        value = stack.pop()
        nodes += 1
        if nodes > MAX_CONTRACT_JSON_NODES:
            raise GateBlocked("json: document exceeds node limit")
        if type(value) is dict:
            stack.extend(value.values())
        elif type(value) is list:
            stack.extend(value)
    return result


def _canonical_sha256(record: Mapping[str, object]) -> str:
    try:
        encoded = json.dumps(
            record,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (TypeError, ValueError) as error:
        raise GateBlocked("contract: values must be canonical JSON") from error
    return hashlib.sha256(encoded).hexdigest()


def _exact_record(
    value: object, expected_fields: frozenset[str], record_name: str
) -> dict[str, object]:
    if type(value) is not dict:
        raise GateBlocked(f"{record_name}: must be an object")
    record = value
    if set(record) != expected_fields:
        raise GateBlocked(f"{record_name}: unknown or missing field")
    return record


def _literal(record: Mapping[str, object], field: str, expected: object) -> None:
    value = record[field]
    if type(value) is not type(expected) or value != expected:
        raise GateBlocked(f"{field}: required safety value is absent")


def _digest(record: Mapping[str, object], field: str) -> str:
    value = record[field]
    if (
        type(value) is not str
        or _HEX_DIGEST.fullmatch(value) is None
        or value == "0" * 64
    ):
        raise GateBlocked(f"{field}: must be a lowercase SHA-256 digest")
    return value


def _commit(value: object, field: str) -> CommitIdentity:
    record = _exact_record(value, frozenset({"object_format", "oid"}), field)
    object_format = record["object_format"]
    oid = record["oid"]
    if type(object_format) is not str or object_format not in {"sha1", "sha256"}:
        raise GateBlocked(f"{field}: unsupported object format")
    expected_length = 40 if object_format == "sha1" else 64
    if (
        type(oid) is not str
        or re.fullmatch(f"[0-9a-f]{{{expected_length}}}", oid) is None
        or oid == "0" * expected_length
    ):
        raise GateBlocked(f"{field}: object identifier is not canonical")
    return CommitIdentity(object_format=object_format, oid=oid)


def _canonical_repository_url(value: object) -> str:
    if type(value) is not str or len(value) > 2_048:
        raise GateBlocked("canonical_https_url: invalid value")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as error:
        raise GateBlocked("canonical_https_url: invalid structure") from error
    hostname = parsed.hostname
    path_parts = parsed.path.split("/")[1:]
    if (
        parsed.scheme != "https"
        or hostname is None
        or hostname != hostname.casefold()
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or port == 443
        or _PATH.fullmatch(parsed.path) is None
        or "%" in parsed.path
        or any(part in {".", ".."} for part in path_parts)
        or any(ord(character) < 33 or ord(character) == 127 for character in value)
    ):
        raise GateBlocked("canonical_https_url: must be a canonical HTTPS repository URL")
    labels = hostname.split(".")
    if len(hostname) > 253 or any(_HOST_LABEL.fullmatch(label) is None for label in labels):
        raise GateBlocked("canonical_https_url: unsupported hostname")
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        raise GateBlocked("canonical_https_url: IP literals are forbidden")
    authority = hostname if port is None else f"{hostname}:{port}"
    if parsed.netloc != authority or value != f"https://{authority}{parsed.path}":
        raise GateBlocked("canonical_https_url: value is not canonical")
    return value


def _validate_request_record(raw: object) -> AcquisitionRequest:
    """Validate a project-owned synthetic acquisition request."""

    record = _exact_record(
        raw,
        frozenset(
            {
                "schema_version",
                "fixture_class",
                "fixture_id",
                "canonical_https_url",
                "requested_commit",
            }
        ),
        "request",
    )
    _literal(record, "schema_version", REQUEST_SCHEMA)
    _literal(record, "fixture_class", SYNTHETIC_FIXTURE)
    fixture_id = record["fixture_id"]
    if type(fixture_id) is not str or fixture_id not in _PROJECT_FIXTURES:
        raise GateBlocked("fixture_id: fixture is not project-owned and pinned")
    canonical_url = _canonical_repository_url(record["canonical_https_url"])
    requested_commit = _commit(record["requested_commit"], "requested_commit")
    expected_url, expected_format, expected_oid, _ = _PROJECT_FIXTURES[fixture_id]
    if (
        canonical_url != expected_url
        or requested_commit.object_format != expected_format
        or requested_commit.oid != expected_oid
    ):
        raise GateBlocked("fixture_id: request does not match the pinned fixture")
    return AcquisitionRequest(
        fixture_id=fixture_id,
        canonical_https_url=canonical_url,
        requested_commit=requested_commit,
        sha256=_canonical_sha256(record),
    )


_RECEIPT_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_class",
        "fixture_id",
        "request_sha256",
        "canonical_https_url",
        "requested_commit",
        "resolved_commit",
        "synthetic_source_id",
        "synthetic_store_id",
        "fixture_asserts_source_identity_binding",
        "fixture_asserts_requested_commit_binding",
        "fixture_asserts_fresh_store",
        "fixture_asserts_no_local_object_reuse",
        "fixture_asserts_no_target_git_metadata_trust",
        "fixture_asserts_no_target_code_execution",
        "fixture_asserts_no_target_controlled_git_execution",
        "fixture_asserts_no_target_git_helper_execution",
        "fixture_asserts_no_target_hook_execution",
        "fixture_asserts_commit_tree_walk",
        "fixture_asserts_analyzed_blob_oids",
        "declared_acquisition_store_bytes",
        "declared_analysis_input_bytes",
        "declared_acquisition_cpu_count",
        "declared_acquisition_cpu_seconds",
        "declared_acquisition_wall_seconds",
        "declared_acquisition_memory_bytes",
        "declared_acquisition_processes",
        "declared_acquisition_diagnostics_bytes",
        "declared_acquisition_image_sha256",
        "declared_verifier_sha256",
        "declared_source_identity_policy_sha256",
        "declared_capsule_manifest_sha256",
        "declared_capsule_sha256",
    }
)


def _validate_receipt_record(
    request: AcquisitionRequest, raw: object
) -> SyntheticReceiptAssertions:
    """Validate synthetic receipt shape and safety invariants, not platform truth."""

    record = _exact_record(raw, _RECEIPT_FIELDS, "receipt")
    _literal(record, "schema_version", RECEIPT_SCHEMA)
    _literal(record, "fixture_class", SYNTHETIC_FIXTURE)
    _literal(record, "fixture_id", request.fixture_id)
    _literal(record, "request_sha256", request.sha256)
    _literal(record, "canonical_https_url", request.canonical_https_url)
    requested = _commit(record["requested_commit"], "requested_commit")
    resolved = _commit(record["resolved_commit"], "resolved_commit")
    if requested != request.requested_commit or resolved != request.requested_commit:
        raise GateBlocked("resolved_commit: does not match the pinned synthetic request")
    _, _, _, expected_source_id = _PROJECT_FIXTURES[request.fixture_id]
    _literal(record, "synthetic_source_id", expected_source_id)
    source_id = record["synthetic_source_id"]
    if type(source_id) is not str or _SOURCE_ID.fullmatch(source_id) is None:
        raise GateBlocked("synthetic_source_id: invalid value")
    store_id_value = record["synthetic_store_id"]
    if type(store_id_value) is not str:
        raise GateBlocked("synthetic_store_id: invalid identifier")
    try:
        store_id = uuid.UUID(store_id_value)
    except (ValueError, AttributeError) as error:
        raise GateBlocked("synthetic_store_id: invalid identifier") from error
    if str(store_id) != store_id_value or store_id.int == 0:
        raise GateBlocked("synthetic_store_id: identifier is not canonical")

    for field in (
        "fixture_asserts_source_identity_binding",
        "fixture_asserts_requested_commit_binding",
        "fixture_asserts_fresh_store",
        "fixture_asserts_no_local_object_reuse",
        "fixture_asserts_no_target_git_metadata_trust",
        "fixture_asserts_no_target_code_execution",
        "fixture_asserts_no_target_controlled_git_execution",
        "fixture_asserts_no_target_git_helper_execution",
        "fixture_asserts_no_target_hook_execution",
        "fixture_asserts_commit_tree_walk",
        "fixture_asserts_analyzed_blob_oids",
    ):
        _literal(record, field, True)
    _bounded_positive_integer(
        record, "declared_acquisition_store_bytes", MAX_INPUT_BYTES
    )
    _bounded_positive_integer(record, "declared_analysis_input_bytes", MAX_INPUT_BYTES)
    for field, maximum in (
        ("declared_acquisition_cpu_count", MAX_CPU_COUNT),
        ("declared_acquisition_cpu_seconds", MAX_CPU_SECONDS),
        ("declared_acquisition_wall_seconds", MAX_WALL_SECONDS),
        ("declared_acquisition_memory_bytes", MAX_MEMORY_BYTES),
        ("declared_acquisition_processes", MAX_ACQUISITION_PROCESSES),
        ("declared_acquisition_diagnostics_bytes", MAX_STDOUT_STDERR_BYTES),
    ):
        _bounded_positive_integer(record, field, maximum)
    if (
        int(record["declared_acquisition_store_bytes"])
        + int(record["declared_analysis_input_bytes"])
        > MAX_INPUT_BYTES
    ):
        raise GateBlocked(
            "declared_analysis_input_bytes: combined acquisition and input limit exceeded"
        )
    for field in (
        "request_sha256",
        "declared_acquisition_image_sha256",
        "declared_verifier_sha256",
        "declared_source_identity_policy_sha256",
        "declared_capsule_manifest_sha256",
        "declared_capsule_sha256",
    ):
        _digest(record, field)
    return SyntheticReceiptAssertions(
        declared_capsule_manifest_sha256=str(
            record["declared_capsule_manifest_sha256"]
        ),
        declared_capsule_sha256=str(record["declared_capsule_sha256"]),
        declared_analysis_input_bytes=int(record["declared_analysis_input_bytes"]),
        sha256=_canonical_sha256(record),
    )


_SANDBOX_FIELDS = frozenset(
    {
        "schema_version",
        "fixture_class",
        "fixture_id",
        "separate_disposable_vm",
        "fresh_workdir",
        "fixed_environment",
        "empty_home",
        "dedicated_unprivileged_user",
        "network",
        "unprivileged",
        "capabilities",
        "privilege_escalation",
        "input_read_only",
        "no_host_mounts",
        "no_home_mount",
        "no_secrets",
        "docker_socket",
        "fixed_analyzer_entrypoint",
        "target_code_execution",
        "git_execution",
        "git_helpers",
        "hooks",
        "child_processes",
        "target_derived_imports",
        "target_derived_configuration",
        "target_derived_plugins",
        "target_derived_exec_paths",
        "process_creation_syscalls_after_start",
        "network_syscalls_after_start",
        "failure_disposition",
        "partial_report",
        "cpu_count",
        "cpu_seconds",
        "wall_seconds",
        "memory_bytes",
        "processes",
        "input_bytes",
        "declared_input_capsule_manifest_sha256",
        "declared_input_capsule_sha256",
        "writable_work_bytes",
        "stdout_stderr_bytes",
        "report_bytes",
        "declared_analysis_image_sha256",
        "declared_syscall_policy_sha256",
    }
)


def _bounded_positive_integer(
    record: Mapping[str, object], field: str, maximum: int
) -> None:
    value = record[field]
    if type(value) is not int or value <= 0 or value > maximum:
        raise GateBlocked(f"{field}: hard limit is absent or exceeds policy")


def _validate_sandbox_record(
    request: AcquisitionRequest,
    receipt: SyntheticReceiptAssertions,
    raw: object,
) -> SandboxContract:
    """Validate the required analysis sandbox declaration, not its enforcement."""

    record = _exact_record(raw, _SANDBOX_FIELDS, "sandbox")
    for field, expected in (
        ("schema_version", SANDBOX_SCHEMA),
        ("fixture_class", SYNTHETIC_FIXTURE),
        ("fixture_id", request.fixture_id),
        ("separate_disposable_vm", True),
        ("fresh_workdir", True),
        ("fixed_environment", True),
        ("empty_home", True),
        ("dedicated_unprivileged_user", True),
        ("network", "disabled_no_virtual_nic"),
        ("unprivileged", True),
        ("capabilities", "none"),
        ("privilege_escalation", "forbidden"),
        ("input_read_only", True),
        ("no_host_mounts", True),
        ("no_home_mount", True),
        ("no_secrets", True),
        ("docker_socket", False),
        ("fixed_analyzer_entrypoint", True),
        ("target_code_execution", "forbidden"),
        ("git_execution", "forbidden"),
        ("git_helpers", "forbidden"),
        ("hooks", "forbidden"),
        ("child_processes", "forbidden"),
        ("target_derived_imports", "forbidden"),
        ("target_derived_configuration", "forbidden"),
        ("target_derived_plugins", "forbidden"),
        ("target_derived_exec_paths", "forbidden"),
        ("process_creation_syscalls_after_start", "denied"),
        ("network_syscalls_after_start", "denied"),
        ("failure_disposition", "kill_and_discard"),
        ("partial_report", "forbidden"),
        (
            "declared_input_capsule_manifest_sha256",
            receipt.declared_capsule_manifest_sha256,
        ),
        ("declared_input_capsule_sha256", receipt.declared_capsule_sha256),
    ):
        _literal(record, field, expected)
    for field, maximum in (
        ("cpu_count", MAX_CPU_COUNT),
        ("cpu_seconds", MAX_CPU_SECONDS),
        ("wall_seconds", MAX_WALL_SECONDS),
        ("memory_bytes", MAX_MEMORY_BYTES),
        ("processes", MAX_PROCESSES),
        ("input_bytes", MAX_INPUT_BYTES),
        ("writable_work_bytes", MAX_WRITABLE_WORK_BYTES),
        ("stdout_stderr_bytes", MAX_STDOUT_STDERR_BYTES),
        ("report_bytes", MAX_REPORT_BYTES),
    ):
        _bounded_positive_integer(record, field, maximum)
    if receipt.declared_analysis_input_bytes > int(record["input_bytes"]):
        raise GateBlocked("input_bytes: smaller than the declared sealed analysis input")
    _digest(record, "declared_analysis_image_sha256")
    _digest(record, "declared_syscall_policy_sha256")
    _digest(record, "declared_input_capsule_manifest_sha256")
    _digest(record, "declared_input_capsule_sha256")
    return SandboxContract(sha256=_canonical_sha256(record))


def build_synthetic_analysis_plan(
    request_serialized: str,
    receipt_serialized: str,
    sandbox_serialized: str,
) -> AnalysisPlan:
    """Validate three strict serialized records for the synthetic D-014 contract."""

    request_raw = load_strict_json(request_serialized)
    receipt_raw = load_strict_json(receipt_serialized)
    sandbox_raw = load_strict_json(sandbox_serialized)
    request = _validate_request_record(request_raw)
    receipt = _validate_receipt_record(request, receipt_raw)
    sandbox = _validate_sandbox_record(request, receipt, sandbox_raw)
    return AnalysisPlan(
        status=PLAN_STATUS,
        platform_evidence_status=PLATFORM_EVIDENCE_STATUS,
        real_repository_eligible=False,
        fixture_id=request.fixture_id,
        canonical_https_url=request.canonical_https_url,
        requested_commit=request.requested_commit,
        declared_capsule_manifest_sha256=receipt.declared_capsule_manifest_sha256,
        declared_capsule_sha256=receipt.declared_capsule_sha256,
        request_sha256=request.sha256,
        receipt_sha256=receipt.sha256,
        sandbox_sha256=sandbox.sha256,
    )
