"""Offline builder and validator for the inert post-SEL policy release experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

ASSET = "ai-policy-starter-v0.1.0.zip"
STATIC = ("ACTIVATION_CONTRACT.json", "ISSUE_FORM_DRAFT.yml", "MEASUREMENT_TEMPLATE.json", "README.md", "RELEASE.json", "RELEASE_BODY.md")
GENERATED = (ASSET, ASSET + ".sha256", "manifest.json", "validation-receipt.json")
MAX_FILE_BYTES = 262_144
MAX_TOTAL_BYTES = 1_048_576
MAX_ARCHIVE_BYTES = 2_097_152
MAX_FILES = 16
MAX_JSON_DEPTH = 12
FIXED_TIME = (2026, 8, 13, 0, 0, 0)
DIGEST = re.compile(r"^[0-9a-f]{64}$")
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
FEEDBACK_ROUTE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,119}$")
RELEASE_TAG = "ai-policy-starter-v0.1.0"
RELEASE_NAME = "AI Contribution Policy Starter v0.1.0 research prerelease"
STOP_CONDITIONS = [
    "asset_digest_mismatch",
    "secret_or_personal_data_leak",
    "policy_or_legal_complaint",
    "sel_gh_001_contamination",
]
CLAIM_BOUNDARY = (
    "Local structural and fingerprint validation only; not publication, activation, adoption, "
    "demand, sale, listing, payment, or production enforcement."
)
MEASUREMENT_FIELDS = {
    "schema_version", "status", "checkpoint_kind", "window_days", "window_start_utc",
    "window_end_utc", "release_id", "release_tag", "release_asset_id", "asset_name",
    "asset_sha256", "download_source",
    "github_reported_download_count", "downloads_are_unique_people", "feedback_source",
    "feedback_form_route", "substantive_feedback_issues", "distinct_public_accounts",
    "intended_adoption_or_use_reports", "unsolicited_customization_requests",
    "explicit_budget_signals", "paid_signal", "paid_signal_basis", "evaluation_result",
    "result_action", "payment_enabled", "second_channel_allowed",
    "aggregate_only_no_raw_usernames_or_links", "attribution_boundary",
}


def _duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _unsafe(path: Path, inspected: os.stat_result) -> bool:
    junction = getattr(path, "is_junction", None)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return (
        path.is_symlink()
        or (callable(junction) and junction())
        or bool(reparse and getattr(inspected, "st_file_attributes", 0) & reparse)
    )


def _trusted_directory(path: Path, *, create: bool) -> Path:
    # Parents are trusted local scope. Exact-directory rechecks reject links and irregular
    # objects, but do not claim protection from an adversarial parent replacement after inspection.
    if create:
        path.mkdir(parents=True, exist_ok=True)
    try:
        inspected = path.lstat()
    except OSError as error:
        raise ValueError("trusted-local directory cannot be inspected") from error
    if _unsafe(path, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("trusted-local boundary must be a non-link regular directory")
    return path.resolve(strict=True)


def _read(path: Path, *, text_required: bool = True) -> bytes:
    before = path.lstat()
    if _unsafe(path, before) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("experiment inputs must be non-link regular files without hard-link aliases")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino) or opened.st_nlink != 1:
            raise ValueError("experiment input changed or aliases another file")
        payload = os.read(descriptor, MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("experiment file exceeds size limit")
    if text_required:
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("experiment text must be UTF-8") from error
        if text.startswith("\ufeff") or "\r" in text:
            raise ValueError("experiment text must be canonical UTF-8 and LF")
    return payload


def _json(payload: bytes) -> object:
    depth = 0
    in_string = False
    escaped = False
    for character in payload.decode("utf-8"):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise ValueError("JSON nesting exceeds the bounded depth")
        elif character in "]}":
            depth -= 1
    try:
        return json.loads(
            payload,
            object_pairs_hook=_duplicate,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonstandard JSON")),
            parse_float=lambda _: (_ for _ in ()).throw(ValueError("JSON floats are not allowed")),
        )
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise ValueError("invalid strict JSON") from error


def _atomic(path: Path, payload: bytes) -> None:
    _trusted_directory(path.parent, create=False)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True); raise


def _build_archive(experiment: Path, payloads: dict[str, bytes]) -> bytes:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{ASSET}.archive.", suffix=".tmp", dir=experiment
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w+b") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise ValueError("secure asset staging file is not an exclusive regular file")
            with zipfile.ZipFile(stream, "w", zipfile.ZIP_STORED) as archive:
                for name, data in sorted(payloads.items()):
                    info = zipfile.ZipInfo(name, FIXED_TIME)
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, data)
            stream.flush()
            os.fsync(stream.fileno())
            after = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(after.st_mode)
                or after.st_nlink != 1
                or (after.st_dev, after.st_ino) != (before.st_dev, before.st_ino)
            ):
                raise ValueError("secure asset staging file changed or gained an alias")
            stream.seek(0)
            asset = stream.read(MAX_ARCHIVE_BYTES + 1)
        if len(asset) > MAX_ARCHIVE_BYTES:
            raise ValueError("release asset exceeds the archive-byte limit")
        return asset
    finally:
        temporary.unlink(missing_ok=True)


def _bounded_count(value: object, field: str) -> int:
    if type(value) is not int or not 0 <= value <= 1_000_000_000:
        raise ValueError(f"{field} must be a bounded nonnegative integer")
    return value


def _utc(value: object, field: str) -> datetime:
    if type(value) is not str or UTC_TIMESTAMP.fullmatch(value) is None:
        raise ValueError(f"{field} must be canonical UTC")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise ValueError(f"{field} must be canonical UTC") from error
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ValueError(f"{field} must be canonical UTC")
    return parsed


def evaluate_measurement(raw: object) -> dict[str, object]:
    if type(raw) is not dict or set(raw) != MEASUREMENT_FIELDS or raw.get("schema_version") != "1":
        raise ValueError("measurement fields or schema version differ")
    exact = {
        "window_days": 14,
        "release_tag": RELEASE_TAG,
        "asset_name": ASSET,
        "asset_sha256": "e76a5999e618002d69481428a1b08952a2b77ab8f516c3de9e6b51971d8ccd4a",
        "download_source": "github_rest_release_asset_download_count",
        "downloads_are_unique_people": False,
        "feedback_source": "exact_activated_feedback_form_route_and_window_only",
        "paid_signal_basis": (
            "unsolicited_customization_request_or_explicit_budget_only_checkbox_excluded"
        ),
        "payment_enabled": False,
        "second_channel_allowed": False,
        "aggregate_only_no_raw_usernames_or_links": True,
        "attribution_boundary": (
            "The exact release asset download_count measures downloads, not unique people or "
            "exact attribution."
        ),
    }
    if any(raw.get(name) != value for name, value in exact.items()):
        raise ValueError("measurement source, identity, privacy, or payment boundary differs")
    if raw["status"] == "not_started":
        if raw["checkpoint_kind"] != "not_started":
            raise ValueError("unstarted checkpoint kind differs")
        null_fields = {
            "window_start_utc", "window_end_utc", "release_id", "release_asset_id",
            "feedback_form_route",
            "github_reported_download_count", "substantive_feedback_issues",
            "distinct_public_accounts", "intended_adoption_or_use_reports",
            "unsolicited_customization_requests", "explicit_budget_signals", "paid_signal",
        }
        if any(raw[name] is not None for name in null_fields):
            raise ValueError("unstarted measurement fields must remain null")
        if raw["evaluation_result"] != "not_started" or raw["result_action"] != "not_started":
            raise ValueError("unstarted evaluation result differs")
        return dict(raw)
    if raw["status"] != "final" or raw["checkpoint_kind"] != "final_exact_14_day_checkpoint":
        raise ValueError("measurement status is not a supported checkpoint")
    started = _utc(raw["window_start_utc"], "window_start_utc")
    ended = _utc(raw["window_end_utc"], "window_end_utc")
    if ended - started != timedelta(days=14):
        raise ValueError("final measurement window must be exactly 14 days")
    release_id = raw["release_id"]
    if type(release_id) is not int or not 1 <= release_id <= 9_007_199_254_740_991:
        raise ValueError("release_id must bind one positive GitHub release integer")
    asset_id = raw["release_asset_id"]
    if type(asset_id) is not int or not 1 <= asset_id <= 9_007_199_254_740_991:
        raise ValueError("release_asset_id must bind one positive GitHub release asset integer")
    route = raw["feedback_form_route"]
    if type(route) is not str or FEEDBACK_ROUTE.fullmatch(route) is None:
        raise ValueError("feedback_form_route must bind one canonical activated route")
    downloads = _bounded_count(raw["github_reported_download_count"], "download count")
    feedback = _bounded_count(raw["substantive_feedback_issues"], "feedback count")
    accounts = _bounded_count(raw["distinct_public_accounts"], "distinct account count")
    adoption = _bounded_count(raw["intended_adoption_or_use_reports"], "adoption count")
    customization = _bounded_count(
        raw["unsolicited_customization_requests"], "customization count"
    )
    budgets = _bounded_count(raw["explicit_budget_signals"], "budget count")
    if accounts != feedback:
        raise ValueError("substantive feedback must count at most one issue per distinct account")
    if adoption > feedback:
        raise ValueError("adoption/use reports cannot exceed qualifying feedback issues")
    paid_signal = customization >= 1 or budgets >= 1
    if raw["paid_signal"] is not paid_signal:
        raise ValueError("paid_signal must derive only from unsolicited requests or explicit budget")
    success = downloads >= 10 and feedback >= 3 and adoption >= 2
    failure = downloads < 5 or feedback == 0
    if success and failure:
        raise ValueError("success and failure sets must not overlap")
    result = "success" if success else "failure" if failure else "inconclusive"
    if raw["evaluation_result"] != result:
        raise ValueError("evaluation_result does not match the closed operator logic")
    expected_action = (
        "future_decision_required_payment_disabled"
        if result == "success"
        else "no_payment_and_revise_or_retire"
    )
    if raw["result_action"] != expected_action:
        raise ValueError("result_action does not match the evaluation result")
    return dict(raw)


def _semantic(contract: object, release: object, measurement: object) -> None:
    if type(contract) is not dict or set(contract) != {"schema_version", "status", "earliest_activation_utc", "asset_sha256", "time_alone_authorizes_activation", "evaluation_checkpoint", "required_gates", "success", "paid_signal", "failure", "otherwise_result", "stop_conditions", "payment_enabled", "activate_command_present", "network_code_present"}:
        raise ValueError("activation contract shape differs")
    if contract["schema_version"] != "1":
        raise ValueError("activation contract schema version differs")
    if contract["status"] != "prepared_not_activated" or contract["earliest_activation_utc"] != "2026-08-25T01:00:00Z" or any(contract[name] is not False for name in ("time_alone_authorizes_activation", "payment_enabled", "activate_command_present", "network_code_present")):
        raise ValueError("activation boundary relaxed")
    if contract["required_gates"] != ["sel_gh_001_final_retained_row_capture_exists", "sel_gh_001_final_capture_independently_verifies_complete", "sel_gh_001_frozen_and_no_incident", "final_release_diff_metadata_and_privacy_review", "exact_asset_digest_matches_contract", "new_future_control_task_decision"]:
        raise ValueError("activation gates differ")
    if contract["evaluation_checkpoint"] != "final_exact_14_day_checkpoint_only":
        raise ValueError("evaluation checkpoint differs")
    if contract["success"] != {"operator": "all", "minimum_downloads": 10, "minimum_substantive_feedback_issues": 3, "feedback_accounts_must_be_distinct_and_public": True, "minimum_intended_adoption_or_use": 2}:
        raise ValueError("success gate differs")
    if contract["paid_signal"] != {"minimum_unsolicited_customization_requests_or_explicit_budget": 1, "checkbox_alone_is_sufficient": False}:
        raise ValueError("paid-signal gate differs")
    if contract["failure"] != {"operator": "any", "downloads_below": 5, "zero_substantive_maintainer_feedback": True, "action": "no_payment_and_revise_or_retire", "second_channel_allowed": False}:
        raise ValueError("failure gate differs")
    if contract["otherwise_result"] != "inconclusive_no_payment_and_revise_or_retire":
        raise ValueError("inconclusive result differs")
    if contract["stop_conditions"] != STOP_CONDITIONS:
        raise ValueError("stop conditions differ or are not in canonical order")
    release_exact = {
        "schema_version": "1",
        "tag_name": RELEASE_TAG,
        "name": RELEASE_NAME,
        "prerelease": True,
        "draft_only": True,
        "status": "prepared_not_activated",
        "payment_enabled": False,
        "body_path": "RELEASE_BODY.md",
        "asset_path": ASSET,
        "checksum_path": ASSET + ".sha256",
    }
    if type(release) is not dict or set(release) != set(release_exact) or release != release_exact:
        raise ValueError("release draft boundary differs")
    evaluate_measurement(measurement)


def _expected_manifest(static_payloads: dict[str, bytes], asset: bytes) -> dict[str, object]:
    asset_sha = hashlib.sha256(asset).hexdigest()
    return {
        "schema_version": "1",
        "experiment_id": "policy-release-r004",
        "status": "prepared_not_activated",
        "inert_location": "support-eval-lab/policy-release-experiment",
        "asset": {"path": ASSET, "bytes": len(asset), "sha256": asset_sha},
        "sha256_boundary": (
            "recomputable_fingerprint_not_signature_attestation_or_external_trust"
        ),
        "static_inventory": [
            {
                "path": name,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            for name, data in sorted(static_payloads.items())
        ],
    }


def _expected_receipt(asset: bytes, manifest_bytes: bytes) -> dict[str, object]:
    return {
        "schema_version": "1",
        "result": "valid_inert_draft",
        "status": "prepared_not_activated",
        "activation_authorized": False,
        "payment_enabled": False,
        "demand_validated": False,
        "revenue_usd": "0.00",
        "asset_sha256": hashlib.sha256(asset).hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _validate_generated_payloads(
    static_payloads: dict[str, bytes], generated: dict[str, bytes]
) -> dict[str, object]:
    if set(static_payloads) != set(STATIC) or set(generated) != set(GENERATED):
        raise ValueError("generated validation inventory differs")
    asset = generated[ASSET]
    asset_sha = hashlib.sha256(asset).hexdigest()
    expected_checksum = f"{asset_sha}  {ASSET}\n".encode()
    if generated[ASSET + ".sha256"] != expected_checksum:
        raise ValueError("release asset checksum line differs from exact asset bytes")
    expected_manifest = _expected_manifest(static_payloads, asset)
    manifest = _json(generated["manifest.json"])
    if manifest != expected_manifest:
        raise ValueError("generated manifest does not bind exact static and asset bytes")
    manifest_bytes = (json.dumps(expected_manifest, indent=2) + "\n").encode()
    if generated["manifest.json"] != manifest_bytes:
        raise ValueError("generated manifest is not canonical")
    expected_receipt = _expected_receipt(asset, manifest_bytes)
    receipt = _json(generated["validation-receipt.json"])
    if receipt != expected_receipt:
        raise ValueError("validation receipt does not bind exact asset and manifest bytes")
    receipt_bytes = (json.dumps(expected_receipt, indent=2) + "\n").encode()
    if generated["validation-receipt.json"] != receipt_bytes:
        raise ValueError("validation receipt is not canonical")
    contract = _json(static_payloads["ACTIVATION_CONTRACT.json"])
    release = _json(static_payloads["RELEASE.json"])
    if (
        contract["asset_sha256"] != asset_sha
        or release["asset_path"] != expected_manifest["asset"]["path"]
        or release["checksum_path"] != ASSET + ".sha256"
        or release["body_path"] not in static_payloads
    ):
        raise ValueError("release, contract, manifest, checksum, or body binding differs")
    return expected_receipt


def build(project: Path) -> dict[str, object]:
    project = _trusted_directory(project, create=False)
    experiment = _trusted_directory(project / "policy-release-experiment", create=False)
    if experiment.parent != project:
        raise ValueError("experiment must stay in its inert project location")
    payloads = {name: _read(experiment / name) for name in STATIC}
    _semantic(_json(payloads["ACTIVATION_CONTRACT.json"]), _json(payloads["RELEASE.json"]), _json(payloads["MEASUREMENT_TEMPLATE.json"]))
    starter = _trusted_directory(project / "policy-starter", create=False)
    entries = sorted(path for path in starter.iterdir())
    if len(entries) > MAX_FILES or any(not path.is_file() for path in entries):
        raise ValueError("bound starter inventory exceeds the flat file boundary")
    starter_payloads = {path.name: _read(path) for path in entries}
    if sum(map(len, payloads.values())) + sum(map(len, starter_payloads.values())) > MAX_TOTAL_BYTES:
        raise ValueError("experiment inputs exceed the total-byte limit")
    asset = _build_archive(experiment, starter_payloads)
    asset_sha = hashlib.sha256(asset).hexdigest()
    contract = _json(payloads["ACTIVATION_CONTRACT.json"])
    if contract["asset_sha256"] != asset_sha or DIGEST.fullmatch(contract["asset_sha256"]) is None:
        raise ValueError("activation contract asset digest differs from exact asset bytes")
    manifest = _expected_manifest(payloads, asset)
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    receipt = _expected_receipt(asset, manifest_bytes)
    generated = {
        ASSET: asset,
        ASSET + ".sha256": f"{asset_sha}  {ASSET}\n".encode(),
        "manifest.json": manifest_bytes,
        "validation-receipt.json": (json.dumps(receipt, indent=2) + "\n").encode(),
    }
    _validate_generated_payloads(payloads, generated)
    for name in GENERATED:
        _atomic(experiment / name, generated[name])
    return receipt


def validate(project: Path) -> dict[str, object]:
    project = _trusted_directory(project, create=False)
    experiment = _trusted_directory(project / "policy-release-experiment", create=False)
    expected = set(STATIC + GENERATED)
    entries: list[Path] = []
    with os.scandir(experiment) as scanned:
        for entry in scanned:
            if len(entries) >= MAX_FILES:
                raise ValueError("experiment inventory exceeds the file-count limit")
            path = Path(entry.path)
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise ValueError("experiment inventory must be flat regular files only")
            entries.append(path)
    actual = {path.name for path in entries}
    if actual != expected:
        raise ValueError("experiment inventory differs")
    static_before = {name: _read(experiment / name) for name in STATIC}
    generated_before = {
        name: _read(experiment / name, text_required=name != ASSET) for name in GENERATED
    }
    checked_receipt = _validate_generated_payloads(static_before, generated_before)
    with tempfile.TemporaryDirectory() as temporary:
        copy = Path(temporary) / "support-eval-lab"
        # Build against copies so validation never authorizes or mutates the checked experiment.
        import shutil
        shutil.copytree(project / "policy-starter", copy / "policy-starter")
        shutil.copytree(experiment, copy / "policy-release-experiment")
        receipt = build(copy)
        for name in GENERATED:
            if (copy / "policy-release-experiment" / name).read_bytes() != generated_before[name]:
                raise ValueError("generated experiment artifact is stale")
    if receipt != checked_receipt:
        raise ValueError("fresh build receipt differs from checked artifact receipt")
    return checked_receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m support_eval_lab.policy_release")
    parser.add_argument("--project", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.project)) if args.check else build(Path(args.project))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
