"""Generate the exact field-by-field declaration projection contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Sequence

from .maintainer_policy_declaration import DIMENSION_VOCABULARIES, EXPECTED_FIELDS, _parse_declaration_payload


ROOT_PARTS = ("interop", "maintainer-policy-declaration", "projection-contract-v1")
SOURCE = Path("data/maintainer-policy-declarations/synthetic/v1/mpd-v1-99c6adc72099ab3f3ad6aaa070f50fb8916b77dc13fa0f70940f61805364572a.json")
STATIC_FILES = {"README.md", "mapping.json"}
GENERATED_FILES = {"AI_POLICY.projected.md", "projection-contract.json", "manifest.json", "validation-receipt.json"}
EXPECTED_FILES = STATIC_FILES | GENERATED_FILES
NON_ESTABLISHED = ["identity", "authority", "currentness", "permission", "enforcement_or_adoption"]
TOP_DISPOSITIONS = {
    "schema_version":"omitted_by_target_profile", "declaration_id":"preserved_exactly",
    "record_kind":"not_established_by_source", "assertion_basis":"not_established_by_source",
    "repository":"preserved_exactly", "repository_url":"omitted_by_target_profile",
    "commit_sha":"human_review_required", "policy_source_url":"human_review_required",
    "policy_path":"human_review_required", "source_sha256":"human_review_required",
    "observed_at":"not_established_by_source", "dimensions":"human_review_required",
    "disclosure_location":"preserved_exactly", "enforcement":"not_representable_in_target",
    "supersedes":"omitted_by_target_profile", "notes":"human_review_required",
}
DIMENSION_DISPOSITIONS = {
    name: ("not_established_by_source" if name in {"disclosure", "human_review", "human_accountability", "license_ip_checks"} else "preserved_exactly")
    for name in DIMENSION_VOCABULARIES
}
ALLOWED_DISPOSITIONS = {"preserved_exactly", "omitted_by_target_profile", "not_representable_in_target", "not_established_by_source", "human_review_required"}


def _duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _strict(path: Path) -> tuple[bytes, object]:
    payload = path.read_bytes()
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_duplicates, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("projection input is not strict JSON") from error
    return payload, value


def _pointer_value(raw: dict[str, object], pointer: str) -> object:
    value: object = raw
    for part in pointer.lstrip("/").split("/"):
        if type(value) is not dict or part not in value:
            raise ValueError("mapping pointer does not resolve")
        value = value[part]
    return value


def _validate_mapping(raw: object) -> list[dict[str, object]]:
    if type(raw) is not dict or set(raw) != {"schema_version", "source", "mappings", "non_established_claims"}:
        raise ValueError("mapping contract fields differ")
    if raw["schema_version"] != "1" or raw["source"] != SOURCE.as_posix() or raw["non_established_claims"] != NON_ESTABLISHED:
        raise ValueError("mapping fixed fields differ")
    expected = {f"/{name}": disposition for name, disposition in TOP_DISPOSITIONS.items()}
    expected.update({f"/dimensions/{name}": disposition for name, disposition in DIMENSION_DISPOSITIONS.items()})
    observed = {}
    for item in raw["mappings"]:
        if type(item) is not dict or set(item) != {"pointer", "disposition", "target"}:
            raise ValueError("mapping entry fields differ")
        pointer = item["pointer"]
        if pointer in observed:
            raise ValueError("duplicate mapping pointer")
        if item["disposition"] not in ALLOWED_DISPOSITIONS:
            raise ValueError("unknown mapping disposition")
        if type(item["target"]) not in {str, type(None)}:
            raise ValueError("mapping target differs")
        observed[pointer] = item["disposition"]
    if observed != expected:
        raise ValueError("mapping is missing, unknown, or disposition-shifted")
    return raw["mappings"]


def build(project: Path) -> dict[str, bytes]:
    root = project.joinpath(*ROOT_PARTS)
    if {entry.name for entry in os.scandir(root)} - GENERATED_FILES != STATIC_FILES:
        raise ValueError("projection static inventory differs")
    source_payload, source_raw = _strict(project / SOURCE)
    if type(source_raw) is not dict:
        raise ValueError("projection source differs")
    declaration = _parse_declaration_payload(source_payload, project / SOURCE)
    mapping_payload, mapping_raw = _strict(root / "mapping.json")
    mappings = _validate_mapping(mapping_raw)
    lines = [
        "# AI contribution policy projection", "",
        "> Inert, non-authorizing generated output for human review. Source values do not establish identity, authority, currentness, permission, enforcement, or adoption.", "",
        "## Trace", "", f"- Declaration: `{declaration.declaration_id}`", f"- Repository label: `{declaration.repository}`", f"- Source record SHA-256: `{hashlib.sha256(source_payload).hexdigest()}`", "",
        "## Field projection", "", "| JSON Pointer | Source value | Disposition |", "|---|---|---|",
    ]
    entries = []
    for item in mappings:
        value = _pointer_value(source_raw, item["pointer"])
        rendered = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        target = item["target"]
        evidence = None
        if target is not None:
            evidence = f"`{item['pointer']}` = `{rendered}`"
            lines.append(f"| `{item['pointer']}` | `{rendered}` | `{item['disposition']}` |")
        entries.append({**item, "source_value": value, "target_evidence": evidence})
    lines.extend(["", "## Non-established claims", ""] + [f"- `{claim}`: not established by this source or projection" for claim in NON_ESTABLISHED])
    lines.extend(["", "> `not_declared` is an absence of a declaration. It is never converted into a contributor obligation or checklist item.", ""])
    markdown = "\n".join(lines).encode("utf-8")
    contract = {
        "schema_version":"1", "source_path":SOURCE.as_posix(), "source_sha256":hashlib.sha256(source_payload).hexdigest(),
        "mapping_sha256":hashlib.sha256(mapping_payload).hexdigest(), "mappings":entries,
        "non_established_claims":NON_ESTABLISHED, "output_path":"AI_POLICY.projected.md", "output_sha256":hashlib.sha256(markdown).hexdigest(),
    }
    contract_payload = (json.dumps(contract, indent=2) + "\n").encode()
    manifest = {"schema_version":"1", "files":[
        {"path":"README.md","sha256":hashlib.sha256((root/"README.md").read_bytes()).hexdigest()},
        {"path":"mapping.json","sha256":hashlib.sha256(mapping_payload).hexdigest()},
        {"path":"AI_POLICY.projected.md","sha256":hashlib.sha256(markdown).hexdigest()},
        {"path":"projection-contract.json","sha256":hashlib.sha256(contract_payload).hexdigest()},
    ]}
    manifest_payload = (json.dumps(manifest, indent=2) + "\n").encode()
    receipt = {"schema_version":"1", "result":"field_complete_projection_prepared", "source_sha256":contract["source_sha256"], "output_sha256":contract["output_sha256"], "manifest_sha256":hashlib.sha256(manifest_payload).hexdigest(), "non_established_claims":NON_ESTABLISHED}
    return {"AI_POLICY.projected.md":markdown, "projection-contract.json":contract_payload, "manifest.json":manifest_payload, "validation-receipt.json":(json.dumps(receipt, indent=2)+"\n").encode()}


def _write(path: Path, payload: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True); raise


def run(project: Path, check: bool) -> dict[str, object]:
    project = project.absolute(); root = project.joinpath(*ROOT_PARTS); artifacts = build(project)
    if check:
        if {entry.name for entry in os.scandir(root)} != EXPECTED_FILES:
            raise ValueError("projection inventory is not closed")
        for name, payload in artifacts.items():
            if (root/name).read_bytes() != payload: raise ValueError(f"stale projection artifact: {name}")
    else:
        for name, payload in artifacts.items(): _write(root/name, payload)
    return json.loads(artifacts["validation-receipt.json"])


def main(argv: Sequence[str] | None = None) -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--project", default="."); parser.add_argument("--check", action="store_true"); args=parser.parse_args(argv)
    print(json.dumps(run(Path(args.project), args.check), indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
