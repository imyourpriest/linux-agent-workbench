"""Bounded Linux release-readiness evidence collection for local demos."""

from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable
from urllib.parse import urlsplit

from .version import __version__


REPORT_SCHEMA_VERSION = "2"
RULES_VERSION = "1.2"
MAX_FILES = 5_000
MAX_ENTRIES = 10_000
MAX_TEXT_BYTES = 1_000_000
MAX_TOTAL_TEXT_BYTES = 20_000_000
MAX_PATH_BYTES = 1_024
MAX_PATH_DEPTH = 20
MAX_SCAN_SECONDS = 30
MAX_EVIDENCE_ITEMS = 50
IGNORED_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "vendor",
    "venv",
}
TEXT_SUFFIXES = {
    "",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
FULL_COMMIT = re.compile(r"^[0-9a-fA-F]{40}$")
USES_LINE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)


@dataclass(frozen=True)
class Finding:
    identifier: str
    title: str
    status: str
    review_priority: str
    evidence: tuple[str, ...]
    recommendation: str

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["evidence"] = list(self.evidence)
        return result


@dataclass(frozen=True)
class Audit:
    repository_url: str
    commit_sha: str
    observed_at: str
    observation_source: str
    provenance_status: str
    provenance_details: tuple[str, ...]
    rules_sha256: str
    files_considered: int
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": REPORT_SCHEMA_VERSION,
            "collector": {
                "name": "linux-release-readiness",
                "version": __version__,
                "rules_version": RULES_VERSION,
                "rules_sha256": self.rules_sha256,
            },
            "declared_repository_url": self.repository_url,
            "declared_commit_sha": self.commit_sha,
            "declared_observed_at": self.observed_at,
            "observation_source": self.observation_source,
            "provenance_status": self.provenance_status,
            "provenance_details": list(self.provenance_details),
            "files_considered": self.files_considered,
            "findings": [finding.to_dict() for finding in self.findings],
        }


class Inventory:
    """A bounded text-only view of a trusted local demo directory."""

    def __init__(self, root: Path):
        self.root = root
        self.paths: list[str] = []
        self.text: dict[str, str] = {}

    @classmethod
    def collect(cls, root: Path) -> "Inventory":
        """Collect a local demo without following known links or junctions."""

        resolved = root.resolve(strict=True)
        if not resolved.is_dir():
            raise ValueError("audit path must be a directory")

        inventory = cls(resolved)
        candidates: list[Path] = []
        pending_directories = [resolved]
        entries_seen = 0
        deadline = time.monotonic() + MAX_SCAN_SECONDS
        while pending_directories:
            _check_deadline(deadline)
            current_path = pending_directories.pop()
            depth = len(current_path.relative_to(resolved).parts)
            try:
                entries = os.scandir(current_path)
            except OSError as error:
                raise ValueError("unable to enumerate the trusted-local demo directory") from error
            with entries:
                for entry in entries:
                    _check_deadline(deadline)
                    entries_seen += 1
                    if entries_seen > MAX_ENTRIES:
                        raise ValueError(
                            f"repository exceeds the {MAX_ENTRIES}-entry audit limit"
                        )
                    path = Path(entry.path)
                    if entry.name.casefold() in IGNORED_PARTS:
                        continue
                    if entry.is_symlink() or path.is_junction():
                        continue
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            if depth >= MAX_PATH_DEPTH:
                                raise ValueError(
                                    f"repository exceeds the {MAX_PATH_DEPTH}-level depth limit"
                                )
                            pending_directories.append(path)
                        elif entry.is_file(follow_symlinks=False):
                            candidates.append(path)
                            if len(candidates) > MAX_FILES:
                                raise ValueError(
                                    f"repository exceeds the {MAX_FILES}-file audit limit"
                                )
                    except OSError as error:
                        raise ValueError(
                            "unable to inspect an entry in the trusted-local demo directory"
                        ) from error

        total_text_bytes = 0
        for path in sorted(candidates, key=lambda item: item.relative_to(resolved).as_posix()):
            _check_deadline(deadline)
            relative = path.relative_to(resolved).as_posix()
            if len(relative.encode("utf-8", errors="surrogatepass")) > MAX_PATH_BYTES:
                raise ValueError(f"repository path exceeds the {MAX_PATH_BYTES}-byte limit")
            if path.is_symlink() or path.is_junction():
                continue
            try:
                if not path.resolve(strict=True).is_relative_to(resolved):
                    continue
            except OSError:
                continue
            inventory.paths.append(relative)
            if path.suffix.casefold() not in TEXT_SUFFIXES:
                continue
            flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            try:
                descriptor = os.open(path, flags)
            except OSError:
                continue
            try:
                chunks: list[bytes] = []
                remaining = MAX_TEXT_BYTES + 1
                while remaining:
                    _check_deadline(deadline)
                    chunk = os.read(descriptor, min(65_536, remaining))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    remaining -= len(chunk)
                raw = b"".join(chunks)
            finally:
                os.close(descriptor)
            if len(raw) > MAX_TEXT_BYTES:
                continue
            total_text_bytes += len(raw)
            if total_text_bytes > MAX_TOTAL_TEXT_BYTES:
                raise ValueError(
                    f"repository exceeds the {MAX_TOTAL_TEXT_BYTES}-byte text audit limit"
                )
            inventory.text[relative] = raw.decode("utf-8", errors="replace")
        return inventory

    def matching_paths(self, predicate: Callable[[str], bool]) -> tuple[str, ...]:
        return tuple(path for path in self.paths if predicate(path))


def _check_deadline(deadline: float) -> None:
    if time.monotonic() > deadline:
        raise ValueError("repository exceeded the static inventory time limit")


def _bounded_unique(evidence: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    recorded: list[str] = []
    omitted = 0
    for item in evidence:
        if item in seen:
            continue
        seen.add(item)
        if len(recorded) < MAX_EVIDENCE_ITEMS:
            recorded.append(item)
        else:
            omitted += 1
    recorded.sort()
    if omitted:
        recorded.append(f"... {omitted} additional unique items omitted")
    return tuple(recorded)


def _finding(
    identifier: str,
    title: str,
    evidence: Iterable[str],
    review_priority: str,
    recommendation: str,
) -> Finding:
    recorded = _bounded_unique(evidence)
    detected = bool(recorded)
    return Finding(
        identifier=identifier,
        title=title,
        status="signal_detected" if detected else "not_detected",
        review_priority="manual_review" if detected else review_priority,
        evidence=recorded,
        recommendation=(
            "Confirm the signal's applicability and correctness manually at the declared commit."
            if detected
            else "First confirm applicability with the maintainer. If applicable: " + recommendation
        ),
    )


def _pinned_actions(inventory: Inventory) -> Finding:
    workflow_paths = inventory.matching_paths(
        lambda path: path.startswith(".github/workflows/")
        and path.casefold().endswith((".yml", ".yaml"))
    )
    composite_paths = inventory.matching_paths(
        lambda path: PurePosixPath(path).name.casefold() in {"action.yml", "action.yaml"}
        and re.search(
            r"^\s*using:\s*['\"]?composite['\"]?\s*$",
            inventory.text.get(path, ""),
            re.IGNORECASE | re.MULTILINE,
        )
        is not None
    )
    action_paths = tuple(sorted(set(workflow_paths) | set(composite_paths)))
    if not action_paths:
        return Finding(
            identifier="pinned-actions",
            title="GitHub Actions immutable-pin signal",
            status="manual_review",
            review_priority="low",
            evidence=(),
            recommendation=(
                "No GitHub Actions workflow was found; "
                "review the applicable CI system manually."
            ),
        )

    unpinned: list[str] = []
    observed_paths: list[str] = []
    unpinned_omitted = 0
    for path in action_paths:
        for match in USES_LINE.finditer(inventory.text.get(path, "")):
            if len(observed_paths) < MAX_EVIDENCE_ITEMS:
                observed_paths.append(path)
            reference = match.group(1).strip("'\"")
            immutable = False
            if reference.startswith("./"):
                immutable = True
            elif reference.startswith("docker://"):
                image = reference.removeprefix("docker://")
                immutable = bool(re.fullmatch(r".+@sha256:[0-9a-fA-F]{64}", image))
            else:
                _, separator, revision = reference.rpartition("@")
                immutable = bool(separator and FULL_COMMIT.fullmatch(revision))
            if not immutable:
                if len(unpinned) < MAX_EVIDENCE_ITEMS:
                    unpinned.append(f"{path}: {reference}")
                else:
                    unpinned_omitted += 1

    if unpinned:
        evidence = sorted(set(unpinned))
        if unpinned_omitted:
            evidence.append(f"... at least {unpinned_omitted} additional references omitted")
        return Finding(
            identifier="pinned-actions",
            title="GitHub Actions immutable-pin signal",
            status="potential_gap",
            review_priority="medium",
            evidence=tuple(evidence),
            recommendation="Manually confirm and pin third-party Actions to full commit SHAs.",
        )
    if not observed_paths:
        return Finding(
            identifier="pinned-actions",
            title="GitHub Actions immutable-pin signal",
            status="manual_review",
            review_priority="low",
            evidence=action_paths[:MAX_EVIDENCE_ITEMS],
            recommendation=(
                "Workflows contain no detected Actions references; "
                "review reusable/local steps manually."
            ),
        )
    return Finding(
        identifier="pinned-actions",
        title="GitHub Actions immutable-pin signal",
        status="signal_detected",
        review_priority="manual_review",
        evidence=tuple(sorted(set(observed_paths))),
        recommendation="Confirm parsed references and immutable pins manually.",
    )


def _line_evidence(
    inventory: Inventory, paths: Iterable[str], pattern: str
) -> tuple[str, ...]:
    expression = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    evidence: list[str] = []
    for path in paths:
        match = expression.search(inventory.text.get(path, ""))
        if match:
            line = inventory.text[path].count("\n", 0, match.start()) + 1
            evidence.append(f"{path}:{line}")
    return tuple(evidence)


def _matching_path_set(
    inventory: Inventory, paths: Iterable[str], pattern: str
) -> set[str]:
    expression = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    return {path for path in paths if expression.search(inventory.text.get(path, ""))}


def _validate_declared_metadata(
    repository_url: str, commit_sha: str, observed_at: str | None
) -> date:
    parsed_url = urlsplit(repository_url)
    try:
        parsed_port = parsed_url.port
    except ValueError as error:
        raise ValueError("repository_url must contain a valid port") from error
    if (
        parsed_url.scheme != "https"
        or not parsed_url.hostname
        or parsed_url.username is not None
        or parsed_url.password is not None
        or parsed_url.query
        or parsed_url.fragment
        or parsed_url.path in {"", "/"}
        or any(character.isspace() or ord(character) < 32 for character in repository_url)
    ):
        raise ValueError("repository_url must be an absolute HTTPS repository URL")
    _ = parsed_port
    if not FULL_COMMIT.fullmatch(commit_sha) or commit_sha == "0" * 40:
        raise ValueError("commit_sha must be a full 40-character hexadecimal commit")
    if observed_at is None:
        raise ValueError("observed_at is required for deterministic unverified demos")
    try:
        observed_date = date.fromisoformat(observed_at)
    except ValueError as error:
        raise ValueError("observed_at must be a valid YYYY-MM-DD date") from error
    if observed_date.isoformat() != observed_at:
        raise ValueError("observed_at must use YYYY-MM-DD")
    if observed_date > date.today():
        raise ValueError("observed_at cannot be in the future")
    return observed_date


def audit_repository(
    root: Path,
    *,
    repository_url: str,
    commit_sha: str,
    observed_at: str | None = None,
    unverified_demo: bool = False,
) -> Audit:
    """Collect bounded evidence from an explicitly unverified trusted-local demo."""

    if not unverified_demo:
        raise ValueError(
            "verified acquisition is not implemented; pass unverified_demo=True only for "
            "synthetic or trusted-local demonstrations"
        )
    observed_date = _validate_declared_metadata(repository_url, commit_sha, observed_at)
    inventory = Inventory.collect(root)

    workflows = inventory.matching_paths(
        lambda path: path.startswith(".github/workflows/")
        and path.casefold().endswith((".yml", ".yaml"))
    )
    ci_paths = tuple(
        sorted(
            set(workflows)
            | set(
                inventory.matching_paths(
                    lambda path: path
                    in {
                        ".circleci/config.yml",
                        ".circleci/config.yaml",
                        ".gitlab-ci.yml",
                        "Jenkinsfile",
                        "azure-pipelines.yml",
                        "azure-pipelines.yaml",
                    }
                )
            )
        )
    )
    readmes = inventory.matching_paths(
        lambda path: PurePosixPath(path).name.casefold().startswith("readme")
    )
    release_scope = inventory.matching_paths(
        lambda path: (
            path in {"Makefile", "Taskfile.yml", "Taskfile.yaml", "pyproject.toml"}
            or path.startswith(".github/workflows/")
            or PurePosixPath(path).name.casefold().startswith((".goreleaser", "release"))
            or "/release" in path.casefold()
        )
    )

    release_workflows: list[str] = []
    release_pattern = re.compile(
        r"goreleaser|release-please|tags:\s*[-\[]|\brelease\b", re.IGNORECASE
    )
    for path in workflows:
        if "release" in PurePosixPath(path).stem.casefold():
            release_workflows.append(path)
            continue
        content = inventory.text.get(path, "")
        match = release_pattern.search(content)
        if match:
            release_workflows.append(f"{path}:{content.count(chr(10), 0, match.start()) + 1}")

    architecture_paths = (
        _matching_path_set(inventory, release_scope, r"linux")
        & _matching_path_set(inventory, release_scope, r"amd64|x86_64")
        & _matching_path_set(inventory, release_scope, r"arm64|aarch64")
    )
    architecture_evidence = tuple(
        f"{path}: Linux, amd64/x86_64, and arm64/aarch64 signals"
        for path in sorted(architecture_paths)
    )

    findings = (
        _finding(
            "license",
            "License-file signal",
            inventory.matching_paths(
                lambda path: PurePosixPath(path).name.casefold().startswith(
                    ("license", "copying")
                )
            ),
            "high",
            "select an appropriate license with owner approval and add its full text.",
        ),
        _finding(
            "package-metadata",
            "Go or Python package-metadata signal",
            inventory.matching_paths(lambda path: path in {"go.mod", "pyproject.toml"}),
            "high",
            "add or repair Go module or Python project metadata for the supported release path.",
        ),
        _finding(
            "changelog",
            "Changelog or release-note-history signal",
            inventory.matching_paths(
                lambda path: PurePosixPath(path).name.casefold().startswith(
                    ("changelog", "changes")
                )
            ),
            "medium",
            "add a maintained changelog or documented generated-release-note workflow.",
        ),
        _finding(
            "ci",
            "Continuous-integration configuration signal",
            ci_paths,
            "high",
            "add a least-privileged CI workflow for the project's supported test matrix.",
        ),
        _finding(
            "release-workflow",
            "Automated release-workflow signal",
            release_workflows,
            "high",
            "add a reviewed tag/manual release workflow with minimal permissions "
            "and rollback notes.",
        ),
        _finding(
            "linux-architectures",
            "Linux amd64 and arm64 artifact signals",
            architecture_evidence,
            "high",
            "configure and test Linux amd64 and arm64 release artifacts where supported.",
        ),
        _finding(
            "checksums",
            "Release-checksum signal",
            _line_evidence(inventory, release_scope, r"checksums?|sha256|sha512"),
            "medium",
            "generate and publish checksums for downloadable release artifacts.",
        ),
        _finding(
            "sbom",
            "SBOM-generation signal",
            _line_evidence(
                inventory, release_scope, r"\bsboms?\b|\bsyft\b|cyclonedx|spdx-json"
            ),
            "medium",
            "generate an SBOM in a documented format as part of the release workflow.",
        ),
        _finding(
            "provenance",
            "Provenance or attestation signal",
            _line_evidence(
                inventory, release_scope, r"\bslsa\b|attest(?:ation)?|provenance|cosign"
            ),
            "low",
            "evaluate an appropriate provenance or artifact-attestation step.",
        ),
        _finding(
            "install",
            "Installation-instruction signal",
            _line_evidence(inventory, readmes, r"^#{1,6}\s+install(?:ation|ing)?\b"),
            "high",
            "document and test at least one supported Linux installation path.",
        ),
        _finding(
            "uninstall",
            "Uninstall or removal-instruction signal",
            _line_evidence(
                inventory,
                readmes,
                r"^#{1,6}\s+(?:uninstall(?:ation|ing)?|removal|removing)\b",
            ),
            "low",
            "document how users can remove installed files and reverse setup changes.",
        ),
        _finding(
            "tests",
            "Automated-test-file signal",
            inventory.matching_paths(
                lambda path: (
                    path.startswith("tests/")
                    or PurePosixPath(path).name.startswith("test_")
                    or PurePosixPath(path).name.endswith("_test.go")
                )
            ),
            "high",
            "add automated validation for release-critical behavior before changing automation.",
        ),
        _pinned_actions(inventory),
    )
    rules_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return Audit(
        repository_url=repository_url,
        commit_sha=commit_sha.lower(),
        observed_at=observed_date.isoformat(),
        observation_source="caller_supplied_for_unverified_demo",
        provenance_status="unverified_local_demo",
        provenance_details=(
            "Repository URL, commit, and observation date are caller-supplied labels; "
            "no upstream identity was verified.",
            "The collector read the supplied local directory without invoking Git or target code.",
            "Use only synthetic or trusted staging directories; safe third-party acquisition "
            "is intentionally outside this MVP.",
        ),
        rules_sha256=rules_sha256,
        files_considered=len(inventory.paths),
        findings=findings,
    )
