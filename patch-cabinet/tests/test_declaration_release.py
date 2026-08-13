from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from patch_cabinet import declaration_release


class DeclarationReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(__file__).resolve().parents[1]

    def test_checked_release_is_fresh_and_archive_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            receipt = declaration_release.build(self.project, output)
            checked = self.project / "release-candidate" / "maintainer-policy-declaration-v0.2.0"
            for name in (declaration_release.ARCHIVE_NAME, declaration_release.ARCHIVE_NAME + ".sha256", "manifest.json", "build-receipt.json"):
                self.assertEqual((output / name).read_bytes(), (checked / name).read_bytes())
            with zipfile.ZipFile(output / declaration_release.ARCHIVE_NAME) as archive:
                self.assertEqual(archive.namelist(), sorted(declaration_release.PAYLOAD))
                self.assertTrue(all(item.compress_type == zipfile.ZIP_STORED for item in archive.infolist()))
                self.assertTrue(all(item.date_time == declaration_release.FIXED_TIME for item in archive.infolist()))
            self.assertEqual(receipt["status"], "prepared_release_candidate_not_published")

    def test_build_is_identical_across_distinct_roots(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            a, b = Path(first) / "a", Path(second) / "b"
            declaration_release.build(self.project, a)
            declaration_release.build(self.project, b)
            self.assertEqual((a / declaration_release.ARCHIVE_NAME).read_bytes(), (b / declaration_release.ARCHIVE_NAME).read_bytes())

    def test_link_alias_and_noncanonical_text_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "patch-cabinet"
            shutil.copytree(self.project, copy)
            root_license = Path(temporary) / "LICENSE"
            shutil.copy2(self.project.parent / "LICENSE", root_license)
            readme = copy / "release-source" / "README.md"
            alias = readme.with_suffix(".alias")
            try:
                os.link(readme, alias)
                with self.assertRaisesRegex(ValueError, "hard-link"):
                    declaration_release.build(copy, Path(temporary) / "out")
            finally:
                alias.unlink(missing_ok=True)
            readme.write_bytes(readme.read_bytes().replace(b"\n", b"\r\n"))
            with self.assertRaisesRegex(ValueError, "LF"):
                declaration_release.build(copy, Path(temporary) / "out")

    def test_manifest_does_not_self_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            declaration_release.build(self.project, output)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertNotIn("manifest_sha256", manifest)
            self.assertNotIn("manifest.json", {item["path"] for item in manifest["payload"]})
            digest = hashlib.sha256((output / declaration_release.ARCHIVE_NAME).read_bytes()).hexdigest()
            self.assertEqual(digest, json.loads((output / "build-receipt.json").read_text())["archive_sha256"])

    def test_old_predictable_staging_path_is_never_touched(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            output.mkdir()
            old = output / f".{declaration_release.ARCHIVE_NAME}.build"
            old.write_bytes(b"regular sentinel")
            declaration_release.build(self.project, output)
            self.assertEqual(old.read_bytes(), b"regular sentinel")
            old.unlink()
            victim = Path(temporary) / "victim"
            victim.write_bytes(b"hardlink victim")
            os.link(victim, old)
            declaration_release.build(self.project, output)
            self.assertEqual(victim.read_bytes(), b"hardlink victim")
            self.assertEqual(old.read_bytes(), b"hardlink victim")

    def test_old_predictable_symlink_is_untouched_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            output.mkdir()
            victim = Path(temporary) / "victim"
            victim.write_bytes(b"symlink victim")
            old = output / f".{declaration_release.ARCHIVE_NAME}.build"
            try:
                old.symlink_to(victim)
            except OSError as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            declaration_release.build(self.project, output)
            self.assertTrue(old.is_symlink())
            self.assertEqual(victim.read_bytes(), b"symlink victim")

    def test_secure_archive_staging_is_unique_and_cleaned(self) -> None:
        created: list[Path] = []
        real_mkstemp = tempfile.mkstemp

        def capture(*args: object, **kwargs: object) -> tuple[int, str]:
            result = real_mkstemp(*args, **kwargs)
            if ".archive." in str(kwargs.get("prefix", "")):
                created.append(Path(result[1]))
            return result

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            with mock.patch.object(declaration_release.tempfile, "mkstemp", side_effect=capture):
                declaration_release.build(self.project, output)
                declaration_release.build(self.project, output)
            self.assertEqual(len(created), 2)
            self.assertEqual(len(set(created)), 2)
            self.assertTrue(all(not path.exists() for path in created))

    def test_output_directory_link_is_rejected_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            actual = Path(temporary) / "actual"
            actual.mkdir()
            linked = Path(temporary) / "linked"
            try:
                linked.symlink_to(actual, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlink creation unavailable: {error}")
            with self.assertRaisesRegex(ValueError, "non-link"):
                declaration_release.build(self.project, linked)

    def test_output_directory_must_be_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "output"
            output.write_bytes(b"not a directory")
            with self.assertRaisesRegex(ValueError, "directory"):
                declaration_release.build(self.project, output)


if __name__ == "__main__":
    unittest.main()
