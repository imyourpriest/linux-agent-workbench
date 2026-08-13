"""Inert deterministic audit of one project-owned synthetic public policy fixture."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import stat
import tempfile
import unicodedata
from datetime import date
from pathlib import Path
from typing import Sequence


COMPONENT_VERSION = "0.1.0"
SCHEMA_VERSION = "1"
MAX_FILE_BYTES = 32_768
MAX_TOTAL_BYTES = 65_536
MAX_JSON_DEPTH = 8
INPUT_FILES = ("AI_POLICY.md", "CONTRIBUTING.md", "SOURCE.json")
GENERATED_FILES = (
    "AUDIT.json",
    "AUDIT.md",
    "PATCH_SUGGESTIONS.md",
    "manifest.json",
    "provenance-receipt.json",
)
ROOT_FILES = {"README.md", "input", *GENERATED_FILES}
EXPECTED_SYNTHETIC_FIXTURE_SHA256 = {
    "AI_POLICY.md": "ff06e4ed92fe3fcf7eeedc424d993a0df29c2982007e3fa5caab6ffe20e01631",
    "CONTRIBUTING.md": "0f1abd2bf560496eb04a9cbfaefb7ddacc3035ca02084a46ecfb7c2d36c99544",
    "SOURCE.json": "cd56b374d5b014f83d5ffc5c50ca16cad4f3ca9b3c740f9f6f0b65e59715fa45",
}
REPOSITORY = re.compile(r"^[a-z0-9][a-z0-9-]{0,38}/[a-z0-9][a-z0-9.-]{0,99}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
BOUNDARIES = {
    "legal_advice": False,
    "security_assessment": False,
    "compliance_or_certification": False,
    "ai_use_detection": False,
    "identity_or_authority_verified": False,
    "current_permission_established": False,
    "platform_enforcement": False,
    "network_or_subprocess": False,
    "real_customer_input": False,
    "service_activated": False,
}
STOP_GATE = (
    "Real input remains prohibited until SEL-GH-001 final capture, a new prospective control "
    "decision, and acquisition, privacy, rights/terms, retention, and provenance validation."
)


def _duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key is not allowed")
        result[key] = value
    return result


def _constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant is not allowed")


def _number(_value: str) -> object:
    raise ValueError("JSON numbers are not allowed in the source record")


def _unsafe_directory(path: Path, inspected: os.stat_result) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return True
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and getattr(inspected, "st_file_attributes", 0) & flag)


def _check_directory(path: Path) -> None:
    try:
        inspected = path.lstat()
    except OSError as error:
        raise ValueError("audit directory cannot be inspected") from error
    if _unsafe_directory(path, inspected) or not stat.S_ISDIR(inspected.st_mode):
        raise ValueError("audit boundary must be a non-link regular directory")


def _check_directory_chain(project: Path, root: Path) -> None:
    """Reject link/reparse components below the explicitly trusted project boundary."""
    project = project.absolute()
    root = root.absolute()
    try:
        relative = root.relative_to(project)
    except ValueError as error:
        raise ValueError("audit directory must remain inside the project boundary") from error
    current = project
    _check_directory(current)
    for part in relative.parts:
        current /= part
        _check_directory(current)


def _read(path: Path, *, text: bool = False) -> bytes:
    try:
        before = path.lstat()
    except OSError as error:
        raise ValueError("audit file cannot be inspected") from error
    if path.is_symlink() or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("audit files must be single-link nonsymlink regular files")
    if before.st_size > MAX_FILE_BYTES:
        raise ValueError("audit file exceeds the byte limit")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("audit file changed or aliases another path")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("audit file exceeds the byte limit")
    if text:
        try:
            decoded = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("audit text must be UTF-8") from error
        if decoded.startswith("\ufeff") or "\r" in decoded:
            raise ValueError("audit text must be BOM-free LF-only UTF-8")
        if any(
            unicodedata.category(character) in {"Cf", "Zl", "Zp"}
            or (unicodedata.category(character) == "Cc" and character not in {"\n", "\t"})
            for character in decoded
        ):
            raise ValueError("audit text contains unsafe control or bidi formatting")
    return payload


def _json_depth(text: str) -> None:
    depth = 0
    in_string = False
    escaped = False
    for character in text:
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
                raise ValueError("source JSON exceeds the depth limit")
        elif character in "]}":
            depth -= 1


def _strict_source(payload: bytes) -> dict[str, object]:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("source record must be UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("source record cannot contain a BOM")
    try:
        _json_depth(text)
        raw = json.loads(
            text,
            object_pairs_hook=_duplicates,
            parse_constant=_constant,
            parse_float=_number,
            parse_int=_number,
        )
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise ValueError("source record is not strict bounded JSON") from error
    fields = {
        "schema_version", "source_kind", "repository", "repository_url", "commit_sha",
        "observed_at", "customer_approved_public_input", "synthetic", "files",
    }
    if type(raw) is not dict or set(raw) != fields:
        raise ValueError("source record fields differ")
    if raw["schema_version"] != SCHEMA_VERSION:
        raise ValueError("source schema differs")
    if raw["source_kind"] != "project_owned_synthetic_public_repository_demo":
        raise ValueError(STOP_GATE)
    if raw["customer_approved_public_input"] is not False or raw["synthetic"] is not True:
        raise ValueError(STOP_GATE)
    repository = raw["repository"]
    if type(repository) is not str or REPOSITORY.fullmatch(repository) is None:
        raise ValueError("repository must use the reserved synthetic grammar")
    if raw["repository_url"] != f"https://example.invalid/{repository}":
        raise ValueError("repository URL must use exact reserved provenance")
    if type(raw["commit_sha"]) is not str or COMMIT.fullmatch(raw["commit_sha"]) is None:
        raise ValueError("commit SHA must be canonical lowercase hexadecimal")
    if raw["commit_sha"] == "0" * 40:
        raise ValueError("commit SHA cannot use the null sentinel")
    try:
        observed = date.fromisoformat(raw["observed_at"])
    except (TypeError, ValueError) as error:
        raise ValueError("observed_at must be a canonical date") from error
    if observed.isoformat() != raw["observed_at"] or observed > date.today():
        raise ValueError("observed_at must be a non-future canonical date")
    files = raw["files"]
    if type(files) is not dict or set(files) != {"AI_POLICY.md", "CONTRIBUTING.md"}:
        raise ValueError("source file inventory differs")
    if any(type(value) is not str or DIGEST.fullmatch(value) is None for value in files.values()):
        raise ValueError("source file digest is not canonical")
    for value in (repository, raw["repository_url"], raw["observed_at"]):
        if any(unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"} for character in value):
            raise ValueError("source record contains unsafe control or bidi formatting")
    return raw


def _inventory(root: Path, *, checking: bool) -> dict[str, bytes]:
    _check_directory(root)
    input_directory = root / "input"
    _check_directory(input_directory)
    actual_root = {entry.name for entry in os.scandir(root)}
    allowed = ROOT_FILES if checking else ROOT_FILES
    if not actual_root.issubset(allowed) or not {"README.md", "input"}.issubset(actual_root):
        raise ValueError("audit root inventory differs")
    if checking and actual_root != ROOT_FILES:
        raise ValueError("audit root inventory differs")
    actual_inputs = {entry.name for entry in os.scandir(input_directory)}
    if actual_inputs != set(INPUT_FILES):
        raise ValueError("audit input inventory differs")
    payloads = {name: _read(input_directory / name, text=True) for name in INPUT_FILES}
    if sum(len(payload) for payload in payloads.values()) > MAX_TOTAL_BYTES:
        raise ValueError("audit input exceeds the aggregate byte limit")
    identities = [(input_directory / name).lstat() for name in INPUT_FILES]
    if len({(item.st_dev, item.st_ino) for item in identities}) != len(identities):
        raise ValueError("audit inputs cannot alias one another")
    return payloads


def _audit(root: Path, *, checking: bool) -> tuple[dict[str, bytes], dict[str, object]]:
    payloads = _inventory(root, checking=checking)
    readme_payload = _read(root / "README.md", text=True)
    if sum(len(payload) for payload in payloads.values()) + len(readme_payload) > MAX_TOTAL_BYTES:
        raise ValueError("audit pack static input exceeds the aggregate byte limit")
    source = _strict_source(payloads["SOURCE.json"])
    actual_fixture_digests = {
        name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()
    }
    if actual_fixture_digests != EXPECTED_SYNTHETIC_FIXTURE_SHA256:
        raise ValueError("fixture differs from verifier-owned checked-tree digests")
    for name in ("AI_POLICY.md", "CONTRIBUTING.md"):
        if hashlib.sha256(payloads[name]).hexdigest() != source["files"][name]:
            raise ValueError("source file digest differs from the provenance record")
    combined = "\n".join(
        payloads[name].decode("utf-8") for name in ("AI_POLICY.md", "CONTRIBUTING.md")
    )
    checks = (
        ("human_review", "Human review is required", "observed"),
        ("ai_disclosure", "must disclose AI assistance", "observed"),
        ("human_accountability", "remains accountable", "observed"),
        ("autonomous_pr_submission", "does not currently declare whether autonomous", "gap"),
        (
            "security_report_automation",
            "does not currently declare rules for automated security reports",
            "gap",
        ),
        ("license_ip_checks", "license and IP checks", "gap"),
    )
    evidence = []
    for control, phrase, expected_status in checks:
        found = phrase.casefold() in combined.casefold()
        status = expected_status if found else "human_decision_required"
        evidence.append(
            {
                "control": control,
                "status": status,
                "evidence": (
                    f"Exact synthetic fixture phrase observed: {phrase}"
                    if found
                    else "No exact bounded fixture phrase observed; human review required."
                ),
            }
        )
    audit_identity = "\0".join(
        [
            source["repository"],
            source["commit_sha"],
            *(source["files"][name] for name in sorted(source["files"])),
        ]
    )
    audit_id = f"ppa-v1-{hashlib.sha256(audit_identity.encode('utf-8')).hexdigest()}"
    report = {
        "schema_version": SCHEMA_VERSION,
        "component": {"name": "public-policy-audit", "version": COMPONENT_VERSION},
        "audit_id": audit_id,
        "source": {
            "kind": source["source_kind"],
            "repository": source["repository"],
            "repository_url": source["repository_url"],
            "commit_sha": source["commit_sha"],
            "observed_at": source["observed_at"],
        },
        "boundaries": BOUNDARIES,
        "real_input_stop_gate": STOP_GATE,
        "fixture_binding": (
            "Matches verifier-owned checked-tree digests; this is local fixture identity, not "
            "real-world ownership, authorship, authority, or an external trust anchor."
        ),
        "evidence": evidence,
        "gaps": [item["control"] for item in evidence if item["status"] == "gap"],
        "human_decisions": [
            "Decide whether autonomous pull-request submission is allowed, conditional, or "
            "disallowed.",
            "Decide the private security-report path and whether any automation is permitted.",
            "Decide the required license and IP review evidence before adoption.",
            "Review every suggestion against the repository's current human-owned policy before "
            "use.",
        ],
        "price_hypothesis_usd": "79.00_unvalidated_not_offered",
        "revenue_usd": "0.00",
    }
    suggestions = (
        "# Patch-ready suggestions for human review\n\n"
        "> Synthetic, non-authorizing draft. Do not paste without repository-owner review.\n\n"
        "## Autonomous pull requests\n\n"
        "Choose one explicit state: allowed, conditional, or disallowed. If conditional, name the\n"
        "required human review and account responsibility before submission.\n\n"
        "## Security reports\n\n"
        "Direct suspected vulnerabilities to the repository's private security channel. State\n"
        "whether automated report submission is allowed; never publish suspected "
        "vulnerabilities.\n\n"
        "## License and IP checks\n\n"
        "Require contributors to confirm they have rights to submitted material and to record any\n"
        "project-specific provenance or generated-content review required by maintainers.\n"
    )
    md_lines = [
        "# Synthetic public policy audit",
        "",
        "> Evidence-limited, non-authorizing demonstration. No score or grade is produced.",
        "",
        f"- Audit ID: `{report['audit_id']}`",
        f"- Repository label: `{html.escape(source['repository'])}`",
        f"- Revenue: `${report['revenue_usd']}`",
        "",
        "| Control | Status | Evidence |",
        "|---|---|---|",
    ]
    for item in evidence:
        md_lines.append(
            f"| `{item['control']}` | `{item['status']}` | {html.escape(item['evidence'])} |"
        )
    md_lines.extend(["", "## Human decisions", ""])
    md_lines.extend(f"- {html.escape(value)}" for value in report["human_decisions"])
    md_lines.extend(["", f"> {STOP_GATE}"])
    artifacts = {
        "AUDIT.json": (json.dumps(report, indent=2) + "\n").encode("utf-8"),
        "AUDIT.md": ("\n".join(md_lines) + "\n").encode("utf-8"),
        "PATCH_SUGGESTIONS.md": suggestions.encode("utf-8"),
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "component": report["component"],
        "inventory": [
            {
                "path": "README.md",
                "sha256": hashlib.sha256(readme_payload).hexdigest(),
                "bytes": len(readme_payload),
            },
        ] + [
            {
                "path": f"input/{name}",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
            }
            for name, payload in sorted(payloads.items())
        ] + [
            {"path": name, "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
            for name, payload in sorted(artifacts.items())
        ],
        "boundaries": BOUNDARIES,
        "real_input_stop_gate": STOP_GATE,
        "trust_boundary": (
            "Verifier-owned module constants bind the checked synthetic fixture. Manifest and "
            "receipt hashes are self-consistency evidence, not signatures or external trust "
            "anchors."
        ),
    }
    artifacts["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "component": report["component"],
        "result": "valid_verifier_bound_checked_tree_synthetic_fixture",
        "audit_id": audit_id,
        "manifest_sha256": hashlib.sha256(artifacts["manifest.json"]).hexdigest(),
        "source_record_sha256": hashlib.sha256(payloads["SOURCE.json"]).hexdigest(),
        "boundaries": BOUNDARIES,
        "real_input_stop_gate": STOP_GATE,
        "trust_boundary": manifest["trust_boundary"],
        "revenue_usd": "0.00",
    }
    artifacts["provenance-receipt.json"] = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")
    return artifacts, receipt


def _write(project: Path, root: Path, path: Path, payload: bytes) -> None:
    _check_directory_chain(project, root)
    if path.exists():
        inspected = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1:
            raise ValueError("existing output must be a single-link nonsymlink regular file")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _check_directory_chain(project, root)
        if path.exists():
            inspected = path.lstat()
            if path.is_symlink() or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1:
                raise ValueError("generated audit output changed before replacement")
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def _check_outputs(root: Path) -> None:
    for name in GENERATED_FILES:
        path = root / name
        if not path.exists():
            continue
        inspected = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1:
            raise ValueError("existing output must be a single-link nonsymlink regular file")


def run(project: Path, *, check: bool) -> dict[str, object]:
    project = project.absolute()
    root = project / "public-policy-audit"
    _check_directory_chain(project, root)
    artifacts, receipt = _audit(root, checking=check)
    if check:
        for name, payload in artifacts.items():
            if _read(root / name, text=name.endswith((".md", ".json"))) != payload:
                raise ValueError(f"generated audit artifact is stale: {name}")
    else:
        _check_outputs(root)
        for name, payload in artifacts.items():
            _write(project, root, root / name, payload)
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m support_eval_lab.public_policy_audit")
    parser.add_argument("--project", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run(Path(args.project), check=args.check), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
