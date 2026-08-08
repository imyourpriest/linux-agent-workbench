"""Fail when the intended public tree contains private paths or common secret signatures."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


MAX_FILE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 25_000_000
BANNED_PATH_PARTS = {".private", ".codex", ".agents", "private", "task-exports"}
SECRET_PATTERNS = {
    "private key block": re.compile(
        rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"
    ),
    "GitHub token": re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})"),
    "OpenAI-style API key": re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    "Stripe secret key": re.compile(rb"sk_(?:live|test)_[A-Za-z0-9]{16,}"),
    "AWS access key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "Stellar secret seed": re.compile(rb"S[A-Z2-7]{55}"),
}


def public_paths(root: Path) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=15,
    )
    return sorted(os.fsdecode(item) for item in result.stdout.split(b"\0") if item)


def scan(root: Path) -> tuple[int, int]:
    paths = public_paths(root)
    failures: list[str] = []
    total_bytes = 0

    for relative in paths:
        path_parts = {part.casefold() for part in Path(relative).parts}
        if path_parts & BANNED_PATH_PARTS:
            failures.append(f"private/tool-state path is included: {relative!r}")
            continue
        if any(ord(character) < 32 or ord(character) == 127 for character in relative):
            failures.append(f"control character in public path: {relative!r}")
            continue

        path = root / relative
        if not path.exists():
            failures.append(f"listed public path is absent from the working tree: {relative!r}")
            continue
        if path.is_symlink() or path.is_junction() or not path.is_file():
            failures.append(f"public scan accepts regular files only: {relative!r}")
            continue
        resolved = path.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError:
            failures.append(f"public path resolves outside the repository: {relative!r}")
            continue

        with path.open("rb") as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
        if len(payload) > MAX_FILE_BYTES:
            failures.append(f"file exceeds {MAX_FILE_BYTES}-byte scan limit: {relative!r}")
            continue
        total_bytes += len(payload)
        if total_bytes > MAX_TOTAL_BYTES:
            failures.append(f"tree exceeds {MAX_TOTAL_BYTES}-byte scan limit")
            break
        for label, expression in SECRET_PATTERNS.items():
            if expression.search(payload):
                failures.append(f"{label} signature detected in {relative!r}")

    if failures:
        raise SystemExit("Public-tree review failed:\n- " + "\n- ".join(failures))
    return len(paths), total_bytes


def main() -> int:
    root = Path(__file__).resolve(strict=True).parent.parent
    file_count, byte_count = scan(root)
    print(
        f"Public-tree heuristic review passed: {file_count} files, {byte_count} bytes, "
        f"{len(SECRET_PATTERNS)} secret-signature families."
    )
    print("This bounded signature scan supplements, but cannot guarantee, privacy review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
