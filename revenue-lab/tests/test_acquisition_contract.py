from __future__ import annotations

import json
import subprocess
import unittest
from copy import deepcopy
from unittest.mock import patch

from release_readiness.acquisition_contract import (
    MAX_CPU_COUNT,
    MAX_CPU_SECONDS,
    MAX_ACQUISITION_PROCESSES,
    MAX_CONTRACT_JSON_BYTES,
    MAX_CONTRACT_JSON_DEPTH,
    MAX_CONTRACT_JSON_NODES,
    MAX_INPUT_BYTES,
    MAX_MEMORY_BYTES,
    MAX_PROCESSES,
    MAX_REPORT_BYTES,
    MAX_STDOUT_STDERR_BYTES,
    MAX_WALL_SECONDS,
    MAX_WRITABLE_WORK_BYTES,
    GateBlocked,
    _validate_receipt_record as validate_receipt,
    _validate_request_record as validate_request,
    build_synthetic_analysis_plan,
    load_strict_json,
)


SHA1 = "a" * 40
SHA256 = "b" * 64


class AcquisitionContractTests(unittest.TestCase):
    def request(self) -> dict[str, object]:
        return {
            "schema_version": "d014-acquisition-request-v1",
            "fixture_class": "project_owned_synthetic",
            "fixture_id": "d014-contract-sha1-v1",
            "canonical_https_url": "https://example.invalid/cairn/d014-contract-sha1",
            "requested_commit": {"object_format": "sha1", "oid": SHA1},
        }

    def receipt(self, request: dict[str, object]) -> dict[str, object]:
        validated = validate_request(request)
        return {
            "schema_version": "d014-acquisition-receipt-v2",
            "fixture_class": "project_owned_synthetic",
            "fixture_id": validated.fixture_id,
            "request_sha256": validated.sha256,
            "canonical_https_url": validated.canonical_https_url,
            "requested_commit": validated.requested_commit.to_dict(),
            "resolved_commit": validated.requested_commit.to_dict(),
            "synthetic_source_id": f"project-owned-synthetic/{validated.fixture_id}",
            "synthetic_store_id": "12345678-1234-5678-9234-567812345678",
            "fixture_asserts_source_identity_binding": True,
            "fixture_asserts_requested_commit_binding": True,
            "fixture_asserts_fresh_store": True,
            "fixture_asserts_no_local_object_reuse": True,
            "fixture_asserts_no_target_git_metadata_trust": True,
            "fixture_asserts_no_target_code_execution": True,
            "fixture_asserts_no_target_controlled_git_execution": True,
            "fixture_asserts_no_target_git_helper_execution": True,
            "fixture_asserts_no_target_hook_execution": True,
            "fixture_asserts_commit_tree_walk": True,
            "fixture_asserts_analyzed_blob_oids": True,
            "declared_acquisition_store_bytes": 1_024,
            "declared_analysis_input_bytes": 512,
            "declared_acquisition_cpu_count": MAX_CPU_COUNT,
            "declared_acquisition_cpu_seconds": MAX_CPU_SECONDS,
            "declared_acquisition_wall_seconds": MAX_WALL_SECONDS,
            "declared_acquisition_memory_bytes": MAX_MEMORY_BYTES,
            "declared_acquisition_processes": MAX_ACQUISITION_PROCESSES,
            "declared_acquisition_diagnostics_bytes": MAX_STDOUT_STDERR_BYTES,
            "declared_acquisition_image_sha256": "1" * 64,
            "declared_verifier_sha256": "2" * 64,
            "declared_source_identity_policy_sha256": "3" * 64,
            "declared_capsule_manifest_sha256": "4" * 64,
            "declared_capsule_sha256": "5" * 64,
        }

    def sandbox(
        self, fixture_id: str = "d014-contract-sha1-v1"
    ) -> dict[str, object]:
        return {
            "schema_version": "d014-analysis-sandbox-v2",
            "fixture_class": "project_owned_synthetic",
            "fixture_id": fixture_id,
            "separate_disposable_vm": True,
            "fresh_workdir": True,
            "fixed_environment": True,
            "empty_home": True,
            "dedicated_unprivileged_user": True,
            "network": "disabled_no_virtual_nic",
            "unprivileged": True,
            "capabilities": "none",
            "privilege_escalation": "forbidden",
            "input_read_only": True,
            "no_host_mounts": True,
            "no_home_mount": True,
            "no_secrets": True,
            "docker_socket": False,
            "fixed_analyzer_entrypoint": True,
            "target_code_execution": "forbidden",
            "git_execution": "forbidden",
            "git_helpers": "forbidden",
            "hooks": "forbidden",
            "child_processes": "forbidden",
            "target_derived_imports": "forbidden",
            "target_derived_configuration": "forbidden",
            "target_derived_plugins": "forbidden",
            "target_derived_exec_paths": "forbidden",
            "process_creation_syscalls_after_start": "denied",
            "network_syscalls_after_start": "denied",
            "failure_disposition": "kill_and_discard",
            "partial_report": "forbidden",
            "cpu_count": MAX_CPU_COUNT,
            "cpu_seconds": MAX_CPU_SECONDS,
            "wall_seconds": MAX_WALL_SECONDS,
            "memory_bytes": MAX_MEMORY_BYTES,
            "processes": MAX_PROCESSES,
            "input_bytes": MAX_INPUT_BYTES,
            "declared_input_capsule_manifest_sha256": "4" * 64,
            "declared_input_capsule_sha256": "5" * 64,
            "writable_work_bytes": MAX_WRITABLE_WORK_BYTES,
            "stdout_stderr_bytes": MAX_STDOUT_STDERR_BYTES,
            "report_bytes": MAX_REPORT_BYTES,
            "declared_analysis_image_sha256": "6" * 64,
            "declared_syscall_policy_sha256": "7" * 64,
        }

    def build(self):
        request = self.request()
        return self.build_records(
            request,
            self.receipt(request),
            self.sandbox(),
        )

    def build_records(self, request: object, receipt: object, sandbox: object):
        return build_synthetic_analysis_plan(
            json.dumps(request, separators=(",", ":")),
            json.dumps(receipt, separators=(",", ":")),
            json.dumps(sandbox, separators=(",", ":")),
        )

    def test_synthetic_contract_builds_non_authorizing_plan(self):
        plan = self.build()

        self.assertEqual(
            plan.status,
            "synthetic_policy_shape_checked_no_platform_evidence",
        )
        self.assertEqual(plan.platform_evidence_status, "absent")
        self.assertFalse(plan.real_repository_eligible)
        self.assertEqual(plan.requested_commit.oid, SHA1)
        for digest in (
            plan.request_sha256,
            plan.receipt_sha256,
            plan.sandbox_sha256,
            plan.declared_capsule_manifest_sha256,
            plan.declared_capsule_sha256,
        ):
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_pure_validator_regression_invokes_no_network_or_process(self):
        with patch("socket.socket") as socket_call, patch.object(
            subprocess, "Popen"
        ) as process_call:
            plan = self.build()

        socket_call.assert_not_called()
        process_call.assert_not_called()
        self.assertFalse(plan.real_repository_eligible)

    def test_receipt_rejects_relaxed_safety_invariants(self):
        request = self.request()
        unsafe_values = {
            "fixture_asserts_source_identity_binding": False,
            "fixture_asserts_requested_commit_binding": False,
            "fixture_asserts_fresh_store": False,
            "fixture_asserts_no_local_object_reuse": False,
            "fixture_asserts_no_target_git_metadata_trust": False,
            "fixture_asserts_no_target_code_execution": False,
            "fixture_asserts_no_target_controlled_git_execution": False,
            "fixture_asserts_no_target_git_helper_execution": False,
            "fixture_asserts_no_target_hook_execution": False,
            "fixture_asserts_commit_tree_walk": False,
            "fixture_asserts_analyzed_blob_oids": False,
        }
        for field, unsafe in unsafe_values.items():
            with self.subTest(field=field):
                receipt = self.receipt(request)
                receipt[field] = unsafe
                with self.assertRaisesRegex(GateBlocked, field):
                    validate_receipt(validate_request(request), receipt)

    def test_receipt_must_bind_exact_request_and_resolved_commit(self):
        request = self.request()
        mutations = {
            "request_sha256": "0" * 64,
            "canonical_https_url": "https://example.invalid/cairn/other",
            "requested_commit": {"object_format": "sha1", "oid": "b" * 40},
            "resolved_commit": {"object_format": "sha1", "oid": "b" * 40},
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                receipt = self.receipt(request)
                receipt[field] = value
                with self.assertRaises(GateBlocked):
                    validate_receipt(validate_request(request), receipt)

    def test_acquisition_and_sealed_input_share_one_storage_cap(self):
        request = self.request()
        receipt = self.receipt(request)
        receipt["declared_acquisition_store_bytes"] = MAX_INPUT_BYTES
        receipt["declared_analysis_input_bytes"] = 1
        with self.assertRaisesRegex(GateBlocked, "combined"):
            validate_receipt(validate_request(request), receipt)

    def test_acquisition_limits_are_positive_integers_with_hard_maxima(self):
        maxima = {
            "declared_acquisition_cpu_count": MAX_CPU_COUNT,
            "declared_acquisition_cpu_seconds": MAX_CPU_SECONDS,
            "declared_acquisition_wall_seconds": MAX_WALL_SECONDS,
            "declared_acquisition_memory_bytes": MAX_MEMORY_BYTES,
            "declared_acquisition_processes": MAX_ACQUISITION_PROCESSES,
            "declared_acquisition_diagnostics_bytes": MAX_STDOUT_STDERR_BYTES,
        }
        request = self.request()
        for field, maximum in maxima.items():
            for unsafe in (0, -1, True, maximum + 1):
                with self.subTest(field=field, unsafe=unsafe):
                    receipt = self.receipt(request)
                    receipt[field] = unsafe
                    with self.assertRaisesRegex(GateBlocked, field):
                        validate_receipt(validate_request(request), receipt)

    def test_sandbox_input_quota_covers_declared_sealed_input(self):
        request = self.request()
        receipt = self.receipt(request)
        sandbox = self.sandbox()
        sandbox["input_bytes"] = 511
        with self.assertRaisesRegex(GateBlocked, "input_bytes"):
            self.build_records(request, receipt, sandbox)

    def test_sandbox_input_must_match_receipt_capsule_declarations(self):
        request = self.request()
        receipt = self.receipt(request)
        for field in (
            "declared_input_capsule_manifest_sha256",
            "declared_input_capsule_sha256",
        ):
            with self.subTest(field=field):
                sandbox = self.sandbox()
                sandbox[field] = "8" * 64
                with self.assertRaisesRegex(GateBlocked, field):
                    self.build_records(request, receipt, sandbox)

    def test_sandbox_rejects_relaxed_isolation(self):
        unsafe_values = {
            "separate_disposable_vm": False,
            "fresh_workdir": False,
            "fixed_environment": False,
            "empty_home": False,
            "dedicated_unprivileged_user": False,
            "network": "enabled",
            "unprivileged": False,
            "capabilities": "inherited",
            "privilege_escalation": "allowed",
            "input_read_only": False,
            "no_host_mounts": False,
            "no_home_mount": False,
            "no_secrets": False,
            "docker_socket": True,
            "fixed_analyzer_entrypoint": False,
            "target_code_execution": "allowed",
            "git_execution": "allowed",
            "git_helpers": "allowed",
            "hooks": "allowed",
            "child_processes": "allowed",
            "target_derived_imports": "allowed",
            "target_derived_configuration": "allowed",
            "target_derived_plugins": "allowed",
            "target_derived_exec_paths": "allowed",
            "process_creation_syscalls_after_start": "allowed",
            "network_syscalls_after_start": "allowed",
            "failure_disposition": "retain",
            "partial_report": "allowed",
        }
        request = self.request()
        receipt = self.receipt(request)
        for field, unsafe in unsafe_values.items():
            with self.subTest(field=field):
                sandbox = self.sandbox()
                sandbox[field] = unsafe
                with self.assertRaisesRegex(GateBlocked, field):
                    self.build_records(request, receipt, sandbox)

    def test_sandbox_limits_are_positive_integers_with_hard_maxima(self):
        maxima = {
            "cpu_count": MAX_CPU_COUNT,
            "cpu_seconds": MAX_CPU_SECONDS,
            "wall_seconds": MAX_WALL_SECONDS,
            "memory_bytes": MAX_MEMORY_BYTES,
            "processes": MAX_PROCESSES,
            "input_bytes": MAX_INPUT_BYTES,
            "writable_work_bytes": MAX_WRITABLE_WORK_BYTES,
            "stdout_stderr_bytes": MAX_STDOUT_STDERR_BYTES,
            "report_bytes": MAX_REPORT_BYTES,
        }
        request = self.request()
        receipt = self.receipt(request)
        for field, maximum in maxima.items():
            for unsafe in (0, -1, True, maximum + 1):
                with self.subTest(field=field, unsafe=unsafe):
                    sandbox = self.sandbox()
                    sandbox[field] = unsafe
                    with self.assertRaisesRegex(GateBlocked, field):
                        self.build_records(request, receipt, sandbox)

    def test_contract_records_reject_unknown_and_missing_fields(self):
        request = self.request()
        request["target_path"] = "ignored"
        with self.assertRaisesRegex(GateBlocked, "unknown or missing"):
            validate_request(request)

        request = self.request()
        request.pop("fixture_class")
        with self.assertRaisesRegex(GateBlocked, "unknown or missing"):
            validate_request(request)

        request = self.request()
        receipt = self.receipt(request)
        receipt["controller_signature"] = "not-supported"
        with self.assertRaisesRegex(GateBlocked, "unknown or missing"):
            validate_receipt(validate_request(request), receipt)

        receipt = self.receipt(request)
        receipt.pop("fixture_asserts_no_local_object_reuse")
        with self.assertRaisesRegex(GateBlocked, "unknown or missing"):
            validate_receipt(validate_request(request), receipt)

        sandbox = self.sandbox()
        sandbox["network_note"] = "disabled"
        with self.assertRaisesRegex(GateBlocked, "unknown or missing"):
            self.build_records(request, self.receipt(request), sandbox)

        sandbox = self.sandbox()
        sandbox.pop("memory_bytes")
        with self.assertRaisesRegex(GateBlocked, "unknown or missing"):
            self.build_records(request, self.receipt(request), sandbox)

    def test_json_loader_rejects_duplicate_keys_at_any_depth(self):
        with self.assertRaisesRegex(GateBlocked, "duplicate"):
            load_strict_json('{"schema_version":"a","schema_version":"b"}')
        with self.assertRaisesRegex(GateBlocked, "duplicate"):
            load_strict_json('{"requested_commit":{"oid":"a","oid":"b"}}')

    def test_json_loader_enforces_bytes_depth_nodes_and_integer_bounds(self):
        oversized = '{"x":"' + ("a" * MAX_CONTRACT_JSON_BYTES) + '"}'
        too_deep = '{"x":' + ("[" * MAX_CONTRACT_JSON_DEPTH) + "0"
        too_deep += ("]" * MAX_CONTRACT_JSON_DEPTH) + "}"
        too_many_nodes = '{"x":[' + ",".join(
            "0" for _ in range(MAX_CONTRACT_JSON_NODES)
        ) + "]}"
        huge_integer = '{"x":' + ("9" * 5_000) + "}"

        for label, serialized in (
            ("byte", oversized),
            ("depth", too_deep),
            ("node", too_many_nodes),
            ("integer", huge_integer),
        ):
            with self.subTest(label=label):
                with self.assertRaises(GateBlocked):
                    load_strict_json(serialized)

    def test_json_loader_rejects_nonstandard_and_noninteger_numbers(self):
        for value in ("NaN", "Infinity", "-Infinity", "1.5", "1e3"):
            with self.subTest(value=value):
                with self.assertRaises(GateBlocked):
                    load_strict_json('{"x":' + value + "}")

    def test_contract_safety_fields_reject_lookalike_types(self):
        request = self.request()
        receipt_mutations = {
            "fixture_asserts_no_local_object_reuse": 1,
            "synthetic_store_id": 1,
            "declared_analysis_input_bytes": True,
            "declared_verifier_sha256": "A" * 64,
        }
        for field, value in receipt_mutations.items():
            with self.subTest(record="receipt", field=field):
                receipt = self.receipt(request)
                receipt[field] = value
                with self.assertRaisesRegex(GateBlocked, field):
                    validate_receipt(validate_request(request), receipt)

        sandbox_mutations = {
            "unprivileged": 1,
            "memory_bytes": 1.0,
            "cpu_seconds": "60",
            "declared_analysis_image_sha256": "6" * 63,
        }
        for field, value in sandbox_mutations.items():
            with self.subTest(record="sandbox", field=field):
                sandbox = self.sandbox()
                sandbox[field] = value
                with self.assertRaises(GateBlocked):
                    self.build_records(
                        request,
                        self.receipt(request),
                        sandbox,
                    )

    def test_contract_rejects_all_zero_digest_sentinels(self):
        request = self.request()
        for field in (
            "declared_acquisition_image_sha256",
            "declared_verifier_sha256",
            "declared_source_identity_policy_sha256",
            "declared_capsule_manifest_sha256",
            "declared_capsule_sha256",
        ):
            with self.subTest(record="receipt", field=field):
                receipt = self.receipt(request)
                receipt[field] = "0" * 64
                with self.assertRaisesRegex(GateBlocked, field):
                    validate_receipt(validate_request(request), receipt)

        for field in (
            "declared_analysis_image_sha256",
            "declared_syscall_policy_sha256",
            "declared_input_capsule_manifest_sha256",
            "declared_input_capsule_sha256",
        ):
            with self.subTest(record="sandbox", field=field):
                sandbox = self.sandbox()
                sandbox[field] = "0" * 64
                with self.assertRaisesRegex(GateBlocked, field):
                    self.build_records(
                        request,
                        self.receipt(request),
                        sandbox,
                    )

    def test_request_rejects_noncanonical_url_oid_and_real_input(self):
        invalid_urls = (
            "http://example.invalid/cairn/demo-cli",
            "https://user@example.invalid/cairn/demo-cli",
            "https://example.invalid/cairn/demo-cli?ref=main",
            "https://EXAMPLE.invalid/cairn/demo-cli",
            "https://example.invalid/cairn/demo-cli/",
            "https://127.0.0.1/cairn/demo-cli",
            "https://example.invalid/cairn/../demo-cli",
            "https://github.com/third-party/repo",
        )
        for url in invalid_urls:
            with self.subTest(url=url):
                request = self.request()
                request["canonical_https_url"] = url
                with self.assertRaises(GateBlocked):
                    validate_request(request)

        for oid in ("A" * 40, "0" * 40, "a" * 39):
            with self.subTest(oid=oid):
                request = self.request()
                request["requested_commit"] = {"object_format": "sha1", "oid": oid}
                with self.assertRaises(GateBlocked):
                    validate_request(request)

        request = self.request()
        request["fixture_class"] = "third_party_public"
        with self.assertRaisesRegex(GateBlocked, "fixture_class"):
            validate_request(request)

    def test_sha256_git_object_format_is_supported_by_contract(self):
        request = self.request()
        request["fixture_id"] = "d014-contract-sha256-v1"
        request["canonical_https_url"] = (
            "https://example.invalid/cairn/d014-contract-sha256"
        )
        request["requested_commit"] = {"object_format": "sha256", "oid": SHA256}
        plan = self.build_records(
            request,
            self.receipt(request),
            self.sandbox("d014-contract-sha256-v1"),
        )
        self.assertEqual(plan.requested_commit.object_format, "sha256")
        self.assertEqual(plan.requested_commit.oid, SHA256)

    def test_record_hashes_are_order_independent_and_change_with_content(self):
        request = self.request()
        receipt = self.receipt(request)
        sandbox = self.sandbox()
        first = self.build_records(request, receipt, sandbox)
        second = self.build_records(
            dict(reversed(list(request.items()))),
            dict(reversed(list(receipt.items()))),
            dict(reversed(list(sandbox.items()))),
        )
        self.assertEqual(first.to_dict(), second.to_dict())

        changed_receipt = deepcopy(receipt)
        changed_receipt["declared_analysis_input_bytes"] = 513
        changed = self.build_records(request, changed_receipt, sandbox)
        self.assertNotEqual(first.receipt_sha256, changed.receipt_sha256)

    def test_missing_platform_records_fail_closed(self):
        request = self.request()
        receipt = self.receipt(request)
        sandbox = self.sandbox()
        missing_records = (
            (None, receipt, sandbox),
            (request, None, sandbox),
            (request, receipt, None),
        )
        for records in missing_records:
            with self.subTest(records=records):
                with self.assertRaises(GateBlocked):
                    self.build_records(*records)

    def test_serialized_valid_fixture_round_trips_strictly(self):
        request = self.request()
        serialized = json.dumps(request, separators=(",", ":"))
        loaded = load_strict_json(serialized)
        self.assertEqual(validate_request(request), validate_request(loaded))

    def test_public_plan_entrypoint_always_uses_strict_json_loader(self):
        request = self.request()
        duplicate_request = '{"schema_version":"wrong",' + json.dumps(request)[1:]
        receipt = json.dumps(self.receipt(request), separators=(",", ":"))
        sandbox = json.dumps(self.sandbox(), separators=(",", ":"))

        with self.assertRaisesRegex(GateBlocked, "duplicate"):
            build_synthetic_analysis_plan(duplicate_request, receipt, sandbox)
        with self.assertRaisesRegex(GateBlocked, "invalid contract document"):
            build_synthetic_analysis_plan(request, receipt, sandbox)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
