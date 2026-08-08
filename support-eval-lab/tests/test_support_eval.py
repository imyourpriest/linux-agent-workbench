from __future__ import annotations

import io
import json
import os
import socket
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from support_eval_lab.cli import _render_markdown, main
from support_eval_lab.evaluator import compare_runs
from support_eval_lab.schema import MAX_FILE_BYTES, load_cases, load_run


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"


class SupportEvalTests(unittest.TestCase):
    def sample_cases(self):
        return load_cases(SAMPLES / "cases.jsonl")

    def sample_runs(self):
        cases = self.sample_cases()
        baseline = load_run(SAMPLES / "baseline.jsonl", cases)
        candidate = load_run(SAMPLES / "candidate.jsonl", cases)
        return cases, baseline, candidate

    def first_record(self, name: str) -> dict:
        line = (SAMPLES / name).read_text(encoding="utf-8").splitlines()[0]
        return json.loads(line)

    def write_jsonl(self, path: Path, records: list[object]) -> None:
        path.write_text(
            "".join(json.dumps(record, separators=(",", ":")) + "\n" for record in records),
            encoding="utf-8",
            newline="\n",
        )

    def test_sample_comparison_catches_three_failures_and_one_review(self):
        cases, baseline, candidate = self.sample_runs()
        report = compare_runs(cases, baseline, candidate)
        self.assertEqual(report["baseline"]["summary"], {"pass": 10, "review": 0, "fail": 0})
        self.assertEqual(report["candidate"]["summary"], {"pass": 6, "review": 1, "fail": 3})
        self.assertEqual(
            report["comparison"]["regressions"],
            ["refund-window", "duplicate-charge", "frustrated-tone", "approval-boundary"],
        )
        self.assertEqual(report["comparison"]["classification"], "regression-detected")

    def test_comparison_is_deterministic_and_does_not_copy_responses(self):
        cases, baseline, candidate = self.sample_runs()
        first = compare_runs(cases, baseline, candidate)
        second = compare_runs(cases, baseline, candidate)
        self.assertEqual(first, second)
        serialized = json.dumps(first, sort_keys=True)
        self.assertNotIn(candidate.outputs["refund-window"].response, serialized)
        self.assertRegex(
            first["cases"][0]["candidate"]["response_sha256"], r"^[0-9a-f]{64}$"
        )

    def test_duplicate_keys_nonstandard_constants_and_numbers_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.jsonl"
            path.write_text('{"schema_version":"1","schema_version":"1"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                load_cases(path)
            path.write_text('{"schema_version":NaN}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-standard JSON"):
                load_cases(path)
            path.write_text('{"schema_version":1}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "numbers are not part"):
                load_cases(path)

    def test_unknown_case_fields_and_control_characters_fail(self):
        record = self.first_record("cases.jsonl")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "cases.jsonl"
            unknown = deepcopy(record)
            unknown["secret"] = "unexpected"
            self.write_jsonl(path, [unknown])
            with self.assertRaisesRegex(ValueError, "fields or schema"):
                load_cases(path)
            hostile = deepcopy(record)
            hostile["turns"] = ["safe\u202eevil"]
            self.write_jsonl(path, [hostile])
            with self.assertRaisesRegex(ValueError, "control or formatting"):
                load_cases(path)

    def test_case_citations_and_phrase_rules_fail_closed(self):
        record = self.first_record("cases.jsonl")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "cases.jsonl"
            bad_citation = deepcopy(record)
            bad_citation["expected"]["citations"] = ["missing-context"]
            self.write_jsonl(path, [bad_citation])
            with self.assertRaisesRegex(ValueError, "citation is absent"):
                load_cases(path)
            overlap = deepcopy(record)
            overlap["expected"]["must_exclude"] = overlap["expected"]["must_include"]
            self.write_jsonl(path, [overlap])
            with self.assertRaisesRegex(ValueError, "overlap"):
                load_cases(path)

    def test_run_requires_exact_coverage_and_unique_outputs(self):
        cases = self.sample_cases()
        records = [
            json.loads(line) for line in (SAMPLES / "baseline.jsonl").read_text().splitlines()
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "run.jsonl"
            self.write_jsonl(path, records[:-1])
            with self.assertRaisesRegex(ValueError, "coverage differs"):
                load_run(path, cases)
            self.write_jsonl(path, records + [records[0]])
            with self.assertRaisesRegex(ValueError, "duplicate output"):
                load_run(path, cases)

    def test_run_rejects_real_mode_unknown_context_and_incomplete_human_review(self):
        cases = self.sample_cases()
        record = self.first_record("baseline.jsonl")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "run.jsonl"
            real = deepcopy(record)
            real["mode"] = "real-customer"
            self.write_jsonl(path, [real])
            with self.assertRaisesRegex(ValueError, "synthetic-mock"):
                load_run(path, cases[:1])
            unknown = deepcopy(record)
            unknown["citations"] = ["invented"]
            self.write_jsonl(path, [unknown])
            with self.assertRaisesRegex(ValueError, "absent from the case"):
                load_run(path, cases[:1])
            incomplete = deepcopy(record)
            incomplete["human_review"].pop("tone-respectful")
            self.write_jsonl(path, [incomplete])
            with self.assertRaisesRegex(ValueError, "cover exactly"):
                load_run(path, cases[:1])

    def test_same_run_identity_cannot_be_compared(self):
        cases, baseline, _candidate = self.sample_runs()
        with self.assertRaisesRegex(ValueError, "run_id values must differ"):
            compare_runs(cases, baseline, baseline)

    def test_sanitized_local_mode_requires_explicit_acknowledgement(self):
        cases = self.sample_cases()
        baseline_records = [
            json.loads(line) for line in (SAMPLES / "baseline.jsonl").read_text().splitlines()
        ]
        candidate_records = [
            json.loads(line) for line in (SAMPLES / "candidate.jsonl").read_text().splitlines()
        ]
        for record in baseline_records + candidate_records:
            record["mode"] = "sanitized-local"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline_path = root / "baseline.jsonl"
            candidate_path = root / "candidate.jsonl"
            self.write_jsonl(baseline_path, baseline_records)
            self.write_jsonl(candidate_path, candidate_records)
            with self.assertRaisesRegex(ValueError, "explicit sanitized-local acknowledgement"):
                load_run(baseline_path, cases)
            baseline = load_run(baseline_path, cases, allow_sanitized_local=True)
            candidate = load_run(candidate_path, cases, allow_sanitized_local=True)
            report = compare_runs(cases, baseline, candidate)
            self.assertEqual(report["evaluation_mode"], "sanitized-local")
            self.assertIn("provenance", report["claim_boundary"])
            with redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    main(
                        [
                            "compare-local",
                            str(SAMPLES / "cases.jsonl"),
                            str(baseline_path),
                            str(candidate_path),
                        ]
                    )
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "compare-local",
                            str(SAMPLES / "cases.jsonl"),
                            str(baseline_path),
                            str(candidate_path),
                            "--acknowledge-sanitized-local-input",
                        ]
                    ),
                    0,
                )

    def test_markdown_escapes_case_controlled_failure_text(self):
        case_record = self.first_record("cases.jsonl")
        case_record["expected"]["must_include"] = ["<script>alert(1)</script>"]
        baseline_record = self.first_record("baseline.jsonl")
        candidate_record = deepcopy(baseline_record)
        candidate_record["run_id"] = "candidate-hostile"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases_path = root / "cases.jsonl"
            baseline_path = root / "baseline.jsonl"
            candidate_path = root / "candidate.jsonl"
            self.write_jsonl(cases_path, [case_record])
            self.write_jsonl(baseline_path, [baseline_record])
            self.write_jsonl(candidate_path, [candidate_record])
            cases = load_cases(cases_path)
            report = compare_runs(
                cases,
                load_run(baseline_path, cases),
                load_run(candidate_path, cases),
            )
            markdown = _render_markdown(report)
            self.assertNotIn("<script>alert(1)</script>", markdown)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", markdown)

    def test_file_byte_limit_is_enforced_before_json_parse(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "large.jsonl"
            path.write_bytes(b"x" * (MAX_FILE_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "input exceeds"):
                load_cases(path)

    def test_deep_json_nesting_fails_with_controlled_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "deep.jsonl"
            path.write_text("[" * 5_000 + "]" * 5_000 + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nesting exceeds"):
                load_cases(path)

    def test_obvious_sensitive_data_is_rejected(self):
        cases = self.sample_cases()
        record = self.first_record("baseline.jsonl")
        record["response"] = "My SSN is 123-45-6789."
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "run.jsonl"
            self.write_jsonl(path, [record])
            with self.assertRaisesRegex(ValueError, "resembles prohibited sensitive data"):
                load_run(path, cases[:1])

    def test_cli_writes_lf_only_reproducible_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_out = root / "report.json"
            markdown_out = root / "report.md"
            arguments = [
                "compare",
                str(SAMPLES / "cases.jsonl"),
                str(SAMPLES / "baseline.jsonl"),
                str(SAMPLES / "candidate.jsonl"),
                "--json-out",
                str(json_out),
                "--markdown-out",
                str(markdown_out),
            ]
            self.assertEqual(main(arguments), 0)
            first = (json_out.read_bytes(), markdown_out.read_bytes())
            self.assertEqual(main(arguments), 0)
            self.assertEqual(first, (json_out.read_bytes(), markdown_out.read_bytes()))
            self.assertNotIn(b"\r\n", json_out.read_bytes() + markdown_out.read_bytes())

    def test_atomic_output_replacement_does_not_modify_hardlink_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            victim = root / "victim.txt"
            output = root / "report.json"
            victim.write_text("sentinel", encoding="utf-8")
            os.link(victim, output)
            self.assertEqual(
                main(
                    [
                        "compare",
                        str(SAMPLES / "cases.jsonl"),
                        str(SAMPLES / "baseline.jsonl"),
                        str(SAMPLES / "candidate.jsonl"),
                        "--json-out",
                        str(output),
                    ]
                ),
                0,
            )
            self.assertEqual(victim.read_text(encoding="utf-8"), "sentinel")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["schema_version"], "1")

    def test_review_to_fail_is_a_regression(self):
        cases = self.sample_cases()
        baseline_records = [
            json.loads(line) for line in (SAMPLES / "baseline.jsonl").read_text().splitlines()
        ]
        candidate_records = deepcopy(baseline_records)
        for record in baseline_records:
            if record["case_id"] == "frustrated-tone":
                record["human_review"]["tone-respectful"] = "not-reviewed"
        for record in candidate_records:
            record["run_id"] = "candidate-fail"
            if record["case_id"] == "frustrated-tone":
                record["human_review"]["tone-respectful"] = "fail"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline_path = root / "baseline.jsonl"
            candidate_path = root / "candidate.jsonl"
            self.write_jsonl(baseline_path, baseline_records)
            self.write_jsonl(candidate_path, candidate_records)
            report = compare_runs(
                cases,
                load_run(baseline_path, cases),
                load_run(candidate_path, cases),
            )
            self.assertIn("frustrated-tone", report["comparison"]["regressions"])
            self.assertEqual(report["comparison"]["classification"], "regression-detected")

    def test_comparison_path_invokes_no_network_or_subprocess(self):
        arguments = [
            "compare",
            str(SAMPLES / "cases.jsonl"),
            str(SAMPLES / "baseline.jsonl"),
            str(SAMPLES / "candidate.jsonl"),
        ]
        with patch.object(socket, "socket", side_effect=AssertionError("network invoked")):
            with patch.object(subprocess, "run", side_effect=AssertionError("process invoked")):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(main(arguments), 0)


if __name__ == "__main__":
    unittest.main()
