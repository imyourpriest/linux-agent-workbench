from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from patch_cabinet import maintainer_policy_declaration as declaration


class DeclarationCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]
        self.script = self.project / "src" / "patch_cabinet" / "maintainer_policy_declaration.py"
        self.synthetic = (
            self.project
            / "data"
            / "maintainer-policy-declarations"
            / "synthetic"
            / "v1"
            / "mpd-v1-99c6adc72099ab3f3ad6aaa070f50fb8916b77dc13fa0f70940f61805364572a.json"
        )

    def _run(self, script: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, "-B", str(script), *arguments],
            cwd=self.project,
            check=False,
            capture_output=True,
        )

    def _assert_expected_error(
        self, result: subprocess.CompletedProcess[bytes], fragment: bytes
    ) -> None:
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(
            result.stderr.startswith(b"maintainer-policy-declaration: error: "),
            result.stderr,
        )
        self.assertIn(fragment, result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def test_process_boundary_handles_expected_input_and_filesystem_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wrong = root / "wrong.json"
            cases = (
                (b"[", b"declaration is not valid strict JSON"),
                (b"[]", b"declaration must be a JSON object"),
                (b"null", b"declaration must be a JSON object"),
            )
            for payload, diagnostic in cases:
                with self.subTest(payload=payload):
                    wrong.write_bytes(payload)
                    self._assert_expected_error(
                        self._run(self.script, "validate", str(wrong)), diagnostic
                    )

            self._assert_expected_error(
                self._run(self.script, "validate", str(root / "missing.json")),
                b"declaration cannot be inspected",
            )

            regular_parent = root / "regular-parent"
            regular_parent.write_bytes(b"not a directory")
            self._assert_expected_error(
                self._run(
                    self.script,
                    "render",
                    str(self.synthetic.parent),
                    "--json-out",
                    str(regular_parent / "index.json"),
                ),
                b"regular-parent",
            )

    def test_valid_source_and_portable_commands_are_byte_identical(self) -> None:
        archive_path = (
            self.project
            / "release-candidate"
            / "maintainer-policy-declaration-v0.2.0"
            / "maintainer-policy-declaration-v0.2.0.zip"
        )
        with tempfile.TemporaryDirectory() as temporary, zipfile.ZipFile(archive_path) as archive:
            portable = Path(temporary) / "maintainer_policy_declaration.py"
            portable_bytes = archive.read("maintainer_policy_declaration.py")
            self.assertEqual(portable_bytes, self.script.read_bytes())
            portable.write_bytes(portable_bytes)

            source_validation = self._run(self.script, "validate", str(self.synthetic))
            portable_validation = self._run(portable, "validate", str(self.synthetic))
            self.assertEqual(source_validation.returncode, 0)
            self.assertEqual(portable_validation.returncode, 0)
            self.assertEqual(source_validation.stderr, b"")
            self.assertEqual(portable_validation.stderr, b"")
            self.assertEqual(source_validation.stdout, portable_validation.stdout)

            source_starter = self._run(
                self.script, "starter", "unverified_project_declaration"
            )
            portable_starter = self._run(
                portable, "starter", "unverified_project_declaration"
            )
            self.assertEqual(source_starter.returncode, 0)
            self.assertEqual(portable_starter.returncode, 0)
            self.assertEqual(source_starter.stderr, b"")
            self.assertEqual(portable_starter.stderr, b"")
            self.assertEqual(source_starter.stdout, portable_starter.stdout)

            with contextlib.redirect_stdout(io.StringIO()) as captured:
                self.assertEqual(declaration.main(["validate", str(self.synthetic)]), 0)
            self.assertEqual(json.loads(source_validation.stdout), json.loads(captured.getvalue()))
            self.assertEqual(
                json.loads(source_starter.stdout),
                declaration.starter_template("unverified_project_declaration"),
            )

    def test_portable_process_boundary_handles_malformed_input(self) -> None:
        archive_path = (
            self.project
            / "release-candidate"
            / "maintainer-policy-declaration-v0.2.0"
            / "maintainer-policy-declaration-v0.2.0.zip"
        )
        with tempfile.TemporaryDirectory() as temporary, zipfile.ZipFile(archive_path) as archive:
            root = Path(temporary)
            portable = root / "maintainer_policy_declaration.py"
            portable.write_bytes(archive.read("maintainer_policy_declaration.py"))
            wrong = root / "wrong.json"
            wrong.write_bytes(b"[")
            self._assert_expected_error(
                self._run(portable, "validate", str(wrong)),
                b"declaration is not valid strict JSON",
            )

    def test_library_and_unexpected_exceptions_still_propagate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            wrong = Path(temporary) / "wrong.json"
            wrong.write_bytes(b"[]")
            with self.assertRaisesRegex(ValueError, "JSON object"):
                declaration.main(["validate", str(wrong)])

        for error in (RuntimeError("unexpected"), TypeError("unexpected")):
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(declaration, "main", side_effect=error):
                    with self.assertRaises(type(error)):
                        declaration.cli([])

        with contextlib.redirect_stderr(io.StringIO()) as captured:
            with self.assertRaises(SystemExit) as raised:
                declaration.cli([])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("usage:", captured.getvalue())

    def test_console_entrypoint_uses_the_tested_process_boundary(self) -> None:
        configuration = tomllib.loads((self.project / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(
            configuration["project"]["scripts"]["maintainer-policy-declaration"],
            "patch_cabinet.maintainer_policy_declaration:cli",
        )


if __name__ == "__main__":
    unittest.main()
