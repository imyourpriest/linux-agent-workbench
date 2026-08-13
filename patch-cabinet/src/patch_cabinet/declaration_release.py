"""Deterministic builder for the portable maintainer declaration release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Sequence

VERSION = "0.2.0"
ARCHIVE_NAME = f"maintainer-policy-declaration-v{VERSION}.zip"
FIXED_TIME = (2026, 8, 13, 0, 0, 0)
MAX_FILES = 8
MAX_FILE_BYTES = 262_144
MAX_TOTAL_BYTES = 1_048_576
MAX_ARCHIVE_BYTES = 2_097_152
MAX_DEPTH = 3
PAYLOAD = {
    "LICENSE": "../LICENSE",
    "README.md": "release-source/README.md",
    "SPECIFICATION.md": "MAINTAINER_POLICY_DECLARATION.md",
    "maintainer_policy_declaration.py": "src/patch_cabinet/maintainer_policy_declaration.py",
    "starter-unverified-project.json": "samples/maintainer-policy-declaration-starter.json",
    "synthetic-example.json": (
        "data/maintainer-policy-declarations/synthetic/v1/"
        "mpd-v1-99c6adc72099ab3f3ad6aaa070f50fb8916b77dc13fa0f70940f61805364572a.json"
    ),
}


def _unsafe(path: Path, inspected: os.stat_result) -> bool:
    junction = getattr(path, "is_junction", None)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return (
        path.is_symlink()
        or (callable(junction) and junction())
        or bool(reparse and getattr(inspected, "st_file_attributes", 0) & reparse)
    )


def _read_regular(path: Path) -> bytes:
    before = path.lstat()
    if _unsafe(path, before) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("release inputs must be non-link regular files without hard-link aliases")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise ValueError("release input changed or aliases another file")
        payload = os.read(descriptor, MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("release input exceeds the per-file limit")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("release inputs must be UTF-8") from error
    if text.startswith("\ufeff") or "\r" in text:
        raise ValueError("release inputs must use canonical UTF-8 without BOM and LF newlines")
    return payload


def _validate_name(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("archive paths must be canonical relative paths")
    if "\\" in name or len(path.parts) > MAX_DEPTH:
        raise ValueError("archive path is noncanonical or too deep")


def _trusted_directory(path: Path, *, create: bool) -> Path:
    # The output parent is trusted local scope. Rechecking the exact directory rejects links and
    # irregular objects, but does not claim protection from an adversarial parent replacement
    # after inspection.
    if create:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ValueError("output must be a non-link regular directory") from error
    try:
        inspected = path.lstat()
    except OSError as error:
        raise ValueError("trusted-local output directory cannot be inspected") from error
    if _unsafe(path, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("output must be a non-link regular directory")
    return path.resolve(strict=True)


def _build_archive(output: Path, payloads: dict[str, bytes]) -> bytes:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{ARCHIVE_NAME}.archive.", suffix=".tmp", dir=output
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w+b") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise ValueError("secure archive staging file is not an exclusive regular file")
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
                for name, data in sorted(payloads.items()):
                    info = zipfile.ZipInfo(name, FIXED_TIME)
                    info.compress_type = zipfile.ZIP_STORED
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
                raise ValueError("secure archive staging file changed or gained an alias")
            stream.seek(0)
            archive_bytes = stream.read(MAX_ARCHIVE_BYTES + 1)
        if len(archive_bytes) > MAX_ARCHIVE_BYTES:
            raise ValueError("release archive exceeds the archive-byte limit")
        return archive_bytes
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_bytes(path: Path, payload: bytes) -> None:
    _trusted_directory(path.parent, create=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def build(project: Path, output: Path) -> dict[str, object]:
    project = _trusted_directory(project, create=False)
    if len(PAYLOAD) > MAX_FILES:
        raise ValueError("release payload exceeds the file-count limit")
    payloads: dict[str, bytes] = {}
    identities: set[tuple[int, int]] = set()
    for archive_path, source_text in sorted(PAYLOAD.items()):
        _validate_name(archive_path)
        candidate = project / source_text
        allowed_root = project.parent if source_text == "../LICENSE" else project
        inspected_candidate = candidate.lstat()
        if _unsafe(candidate, inspected_candidate):
            raise ValueError("release input path cannot be a symlink, junction, or reparse point")
        source = candidate.resolve(strict=True)
        if not source.is_relative_to(allowed_root.resolve(strict=True)):
            raise ValueError("release input escapes its trusted project boundary")
        inspected = source.stat()
        identity = (inspected.st_dev, inspected.st_ino)
        if identity in identities:
            raise ValueError("release inputs cannot alias the same file")
        identities.add(identity)
        payloads[archive_path] = _read_regular(source)
    if sum(map(len, payloads.values())) > MAX_TOTAL_BYTES:
        raise ValueError("release payload exceeds the total-byte limit")
    inventory = [
        {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        for name, data in sorted(payloads.items())
    ]
    fingerprint_material = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
    manifest = {
        "schema_version": "1",
        "component": {"name": "maintainer-policy-declaration", "version": VERSION},
        "status": "release_candidate_not_published",
        "archive_format": "zip_stored_fixed_metadata",
        "sha256_boundary": "recomputable_fingerprint_not_signature_attestation_or_external_trust",
        "source_tree_fingerprint": hashlib.sha256(fingerprint_material).hexdigest(),
        "payload": inventory,
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    output = _trusted_directory(output, create=True)
    archive_bytes = _build_archive(output, payloads)
    archive_sha = hashlib.sha256(archive_bytes).hexdigest()
    receipt = {
        "schema_version": "1",
        "status": "prepared_release_candidate_not_published",
        "archive": ARCHIVE_NAME,
        "archive_bytes": len(archive_bytes),
        "archive_sha256": archive_sha,
        "sha256_boundary": "recomputable_fingerprint_not_signature_attestation_or_external_trust",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    _atomic_bytes(output / ARCHIVE_NAME, archive_bytes)
    _atomic_bytes(output / f"{ARCHIVE_NAME}.sha256", f"{archive_sha}  {ARCHIVE_NAME}\n".encode())
    _atomic_bytes(output / "manifest.json", manifest_bytes)
    _atomic_bytes(output / "build-receipt.json", (json.dumps(receipt, indent=2) + "\n").encode())
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m patch_cabinet.declaration_release")
    parser.add_argument("--project", default=".")
    parser.add_argument(
        "--output", default=f"release-candidate/maintainer-policy-declaration-v{VERSION}"
    )
    args = parser.parse_args(argv)
    print(json.dumps(build(Path(args.project), Path(args.output)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
