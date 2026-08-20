"""Prepare the closed, non-authorizing declaration compatibility v2 harness."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Sequence


ROOT_PARTS = ("interop", "maintainer-policy-declaration", "compatibility-v2")
STATIC_FILES = (
    "README.md",
    "base-corpus-binding.json",
    "supplemental-corpus.json",
    "expected-results.json",
    "python_runner.py",
    "node_runner.mjs",
    "requirements.lock",
    "package.json",
    "package-lock.json",
    "node-dependency-evidence.json",
)
GENERATED_FILES = ("manifest.json", "prepared-receipt.json")
EXPECTED_FILES = set(STATIC_FILES) | set(GENERATED_FILES)
MAX_FILE_BYTES = 262_144
BOUNDARY = (
    "Prepared structural compatibility only. Hosted observations are not observed locally and "
    "would not establish attestation, authentication, semantic correctness, provenance, "
    "freshness, privacy, isolation, standard adoption, source truth, permission, or production "
    "enforcement. Dependency acquisition is network-enabled."
)
EXPECTED_BASE_BINDING = {
    "schema_version": "1",
    "schema": {
        "path": "interop/maintainer-policy-declaration/v1/schema.json",
        "sha256": "1582238b1ac144c9df0dc58e1252da67bf41c4851f39aa2386ae2dc06a6f28a2",
    },
    "base_corpus": {
        "path": "interop/maintainer-policy-declaration/v1/corpus.json",
        "sha256": "280d9d2aca66844e5fc03d6ae907e74e0dd54a8ab5f82e1daa29b8ad31a3ed2a",
    },
    "reference_policy": {
        "allowed_ref_values": ["#/$defs/policy", "#/$defs/expectation"],
        "dynamic_or_external_refs": "reject",
    },
}
EXPECTED_VALIDATOR_CONFIGURATIONS = {
    "python_jsonschema_4_26_0": {
        "dialect": "Draft202012Validator",
        "check_schema": True,
        "format_checker": None,
        "registry_or_remote_loader": False,
        "raw_decoder": "strict_json_loads",
        "duplicate_key_preflight": "object_pairs_hook_reject",
    },
    "node_ajv_8_20_0": {
        "entrypoint": "ajv/dist/2020.js",
        "strict": True,
        "strictTypes": True,
        "allowUnionTypes": True,
        "allErrors": True,
        "validateFormats": False,
        "async_loader": False,
        "raw_decoder": "JSON.parse",
        "duplicate_key_preflight": "object_scoped_recursive_descent_reject",
    },
}
EXPECTED_NODE_DEPENDENCY_EVIDENCE = {
    "schema_version": "1",
    "dependency": "fast-uri",
    "registry_metadata_source": "https://registry.npmjs.org/fast-uri/3.1.5",
    "observed_at": "2026-08-20",
    "version": "3.1.5",
    "resolved": "https://registry.npmjs.org/fast-uri/-/fast-uri-3.1.5.tgz",
    "integrity": (
        "sha512-gHwA1O9LDIcKunMKhObS/HimwtehO1nPUECKAu5TpKgaO19fcWEl4bliWe1jWxVFv"
        "IXztJjjQ4L8XQ1EU9f7Jw=="
    ),
    "registry_shasum": "610f37419a030270430cecd68d74e3d4d96725d0",
    "license": "BSD-3-Clause",
    "install_script_observed": False,
    "engines_field_observed": False,
    "claim_boundary": (
        "Selected fields transcribed from official npm registry metadata; this is not a raw "
        "response archive and does not establish downloaded bytes, runtime behavior, "
        "exploitation resistance, isolation, future availability, or production security."
    ),
}
V1_LOCK_SHA256 = "58fffd062e7152bd07a1dfefb91082a1715126094e9d2321fd034a3a266cf543"
V1_PYTHON_RUNNER_SHA256 = "182c674dc7fb0f583a316e9cef95136ebe9d354a6bc3efbd843b58b85576d777"
V1_NODE_RUNNER_SHA256 = "8d4f7233905b6b640a65d536f6c52a19a7c79c78c45fedafa55246a2df808e04"


def _duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _constant(_value: str) -> object:
    raise ValueError("non-standard JSON constant")


def _read(path: Path) -> bytes:
    before = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("compatibility files must be single-link regular files")
    if before.st_size > MAX_FILE_BYTES:
        raise ValueError("compatibility file exceeds limit")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("compatibility file changed during open")
        payload = os.read(descriptor, MAX_FILE_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("compatibility file exceeds limit")
    return payload


def _json(payload: bytes, label: str) -> object:
    try:
        text = payload.decode("utf-8")
        if text.startswith("\ufeff"):
            raise ValueError
        return json.loads(text, object_pairs_hook=_duplicates, parse_constant=_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"{label} is not strict UTF-8 JSON") from error


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _replace_once(payload: bytes, old: bytes, new: bytes, label: str) -> bytes:
    if payload.count(old) != 1:
        raise ValueError(f"published v1 {label} transform source differs")
    return payload.replace(old, new, 1)


def _v1_payload(project: Path, name: str, expected_sha256: str) -> bytes:
    path = project / "interop/maintainer-policy-declaration/compatibility-v1" / name
    payload = _read(path)
    if _sha(payload) != expected_sha256:
        raise ValueError(f"published v1 {name} digest differs")
    return payload


def _preflight_schema(schema: object) -> None:
    allowed = {"#/$defs/policy", "#/$defs/expectation"}
    pending = [schema]
    while pending:
        value = pending.pop()
        if type(value) is dict:
            for key, child in value.items():
                if key in {"$dynamicRef", "$recursiveRef"}:
                    raise ValueError("dynamic or recursive references are prohibited")
                if key == "$ref" and child not in allowed:
                    raise ValueError("schema reference is not an exact reviewed local fragment")
                pending.append(child)
        elif type(value) is list:
            pending.extend(value)


def _set_pointer(value: dict[str, object], pointer: str, replacement: object, *, delete: bool = False) -> None:
    if not pointer.startswith("/") or "~" in pointer:
        raise ValueError("supplemental pointer is not canonical")
    parts = pointer[1:].split("/")
    parent: object = value
    for part in parts[:-1]:
        if type(parent) is not dict or part not in parent:
            raise ValueError("supplemental pointer does not resolve")
        parent = parent[part]
    if type(parent) is not dict:
        raise ValueError("supplemental pointer parent differs")
    if delete:
        if parts[-1] not in parent:
            raise ValueError("supplemental delete target differs")
        del parent[parts[-1]]
    else:
        parent[parts[-1]] = replacement


def _raw_vectors(base: dict[str, object], supplemental: dict[str, object]) -> list[tuple[str, str]]:
    result = [(item["id"], item["payload"]) for item in base["vectors"]]
    for vector in supplemental["vectors"]:
        if type(vector) is not dict or set(vector) != {"id", "operations"} or type(vector["operations"]) is not list:
            raise ValueError("supplemental vector fields differ")
        value = copy.deepcopy(supplemental["base_payload"])
        for operation in vector["operations"]:
            if type(operation) is not dict or operation.get("op") not in {"delete", "set", "repeat"}:
                raise ValueError("supplemental operation differs")
            if operation["op"] == "delete" and set(operation) == {"op", "pointer"}:
                _set_pointer(value, operation["pointer"], None, delete=True)
            elif operation["op"] == "set" and set(operation) == {"op", "pointer", "value"}:
                _set_pointer(value, operation["pointer"], operation["value"])
            elif operation["op"] == "repeat" and set(operation) == {"op", "pointer", "value", "count"} and type(operation["value"]) is str and type(operation["count"]) is int and 1 <= operation["count"] <= 1_000:
                _set_pointer(value, operation["pointer"], operation["value"] * operation["count"])
            else:
                raise ValueError("supplemental operation fields differ")
        result.append((vector["id"], json.dumps(value, sort_keys=True, separators=(",", ":"))))
    return result


def _expected_v2_lock(project: Path) -> dict[str, object]:
    v1_payload = _v1_payload(project, "package-lock.json", V1_LOCK_SHA256)
    v1_lock = _json(v1_payload, "published v1 Node package lock")
    if type(v1_lock) is not dict:
        raise ValueError("published v1 Node package lock differs")
    expected = copy.deepcopy(v1_lock)
    if (expected.get("name"), expected.get("version")) != (
        "maintainer-policy-declaration-compatibility-v1", "1.0.0"
    ):
        raise ValueError("published v1 Node package lock header differs")
    expected["name"] = "maintainer-policy-declaration-compatibility-v2"
    expected["version"] = "2.0.0"
    packages = expected.get("packages")
    if type(packages) is not dict or packages.get("") != {
        "name": "maintainer-policy-declaration-compatibility-v1",
        "version": "1.0.0",
        "dependencies": {"ajv": "8.20.0"},
    }:
        raise ValueError("published v1 Node package lock root differs")
    packages[""]["name"] = "maintainer-policy-declaration-compatibility-v2"
    packages[""]["version"] = "2.0.0"
    old_fast_uri = {
        "version": "3.1.0",
        "resolved": "https://registry.npmjs.org/fast-uri/-/fast-uri-3.1.0.tgz",
        "integrity": (
            "sha512-iPeeDKJSWf4IEOasVVrknXpaBV0IApz/gp7S2bb7Z4Lljbl2MGJRqInZiUrQwV16"
            "cpzw/D3S5j5Julj/gT52AA=="
        ),
    }
    if packages.get("node_modules/fast-uri") != old_fast_uri:
        raise ValueError("published v1 fast-uri lock tuple differs")
    packages["node_modules/fast-uri"] = {
        "version": EXPECTED_NODE_DEPENDENCY_EVIDENCE["version"],
        "resolved": EXPECTED_NODE_DEPENDENCY_EVIDENCE["resolved"],
        "integrity": EXPECTED_NODE_DEPENDENCY_EVIDENCE["integrity"],
    }
    return expected


def _expected_v2_python_runner(project: Path) -> bytes:
    payload = _v1_payload(project, "python_runner.py", V1_PYTHON_RUNNER_SHA256)
    return _replace_once(
        payload,
        b'"compatibility-v1"',
        b'"compatibility-v2"',
        "Python runner root",
    )


def _expected_v2_node_runner(project: Path) -> bytes:
    payload = _v1_payload(project, "node_runner.mjs", V1_NODE_RUNNER_SHA256)
    payload = _replace_once(
        payload,
        b'import Ajv2020 from "ajv/dist/2020.js";\n',
        b"",
        "Node static Ajv import",
    )
    payload = _replace_once(
        payload,
        b'"compatibility-v1"',
        b'"compatibility-v2"',
        "Node runner root",
    )
    old_inventory = (
        b"const inventory = {};\n"
        b'for (const name of ["ajv", "fast-deep-equal", "fast-uri", '
        b'"json-schema-traverse", "require-from-string"]) inventory[name] = '
        b'strictParse(read(path.join(root, "node_modules", name, "package.json"))).version;\n'
        b'const required = { ajv:"8.20.0", "fast-deep-equal":"3.1.3", '
        b'"fast-uri":"3.1.0", "json-schema-traverse":"1.0.0", '
        b'"require-from-string":"2.0.2" };\n'
        b'if (JSON.stringify(inventory) !== JSON.stringify(required)) throw new Error('
        b'"installed dependency inventory differs");\n'
    )
    payload = _replace_once(payload, old_inventory, b"", "Node late inventory guard")
    schema_start = (
        b'const schema = strictParse(read(path.join(project, "interop/'
        b'maintainer-policy-declaration/v1/schema.json")));\n'
    )
    early_inventory = (
        b'const required = {"ajv":"8.20.0","fast-deep-equal":"3.1.3",'
        b'"fast-uri":"3.1.5","json-schema-traverse":"1.0.0",'
        b'"require-from-string":"2.0.2"};\n'
        b"const inventory = {};\n"
        b"for (const name of Object.keys(required)) inventory[name] = "
        b'strictParse(read(path.join(root, "node_modules", name, "package.json"))).version;\n'
        b'if (JSON.stringify(inventory) !== JSON.stringify(required)) throw new Error('
        b'"installed dependency inventory differs");\n'
        b'const { default: Ajv2020 } = await import("ajv/dist/2020.js");\n'
    )
    return _replace_once(
        payload,
        schema_start,
        early_inventory + schema_start,
        "Node pre-import inventory insertion",
    )


def _validate_node_dependencies(project: Path, payloads: dict[str, bytes]) -> None:
    package = _json(payloads["package.json"], "Node package")
    lock = _json(payloads["package-lock.json"], "Node package lock")
    evidence = _json(payloads["node-dependency-evidence.json"], "node dependency evidence")
    if evidence != EXPECTED_NODE_DEPENDENCY_EVIDENCE:
        raise ValueError("node dependency evidence differs from verifier-owned policy")
    expected_package = {
        "name": "maintainer-policy-declaration-compatibility-v2",
        "version": "2.0.0",
        "private": True,
        "type": "module",
        "dependencies": {"ajv": "8.20.0"},
    }
    if package != expected_package:
        raise ValueError("Node package configuration differs")
    if lock != _expected_v2_lock(project):
        raise ValueError("Node package lock differs from exact v1-derived successor")
    packages = lock["packages"]
    for name, item in packages.items():
        if name and (
            not item.get("resolved", "").startswith("https://registry.npmjs.org/")
            or not item.get("integrity", "").startswith("sha512-")
        ):
            raise ValueError("Node package lock source or integrity differs")


def _validate_runners(project: Path, payloads: dict[str, bytes]) -> None:
    if payloads["python_runner.py"] != _expected_v2_python_runner(project):
        raise ValueError("Python runner differs from exact v1-derived successor")
    if payloads["node_runner.mjs"] != _expected_v2_node_runner(project):
        raise ValueError("Node runner differs from exact v1-derived successor")


def _validate_contracts(root: Path, project: Path, payloads: dict[str, bytes]) -> dict[str, object]:
    binding = _json(payloads["base-corpus-binding.json"], "base binding")
    supplemental = _json(payloads["supplemental-corpus.json"], "supplemental corpus")
    expected = _json(payloads["expected-results.json"], "expected results")
    _validate_node_dependencies(project, payloads)
    _validate_runners(project, payloads)
    if type(binding) is not dict or set(binding) != {
        "schema_version", "schema", "base_corpus", "reference_policy"
    }:
        raise ValueError("base binding fields differ")
    if binding != EXPECTED_BASE_BINDING:
        raise ValueError("base binding paths, digests, or reference policy differ")
    schema_path = project / binding["schema"]["path"]
    corpus_path = project / binding["base_corpus"]["path"]
    schema_payload = _read(schema_path)
    corpus_payload = _read(corpus_path)
    if _sha(schema_payload) != binding["schema"]["sha256"]:
        raise ValueError("bound schema digest differs")
    if _sha(corpus_payload) != binding["base_corpus"]["sha256"]:
        raise ValueError("bound base corpus digest differs")
    _preflight_schema(_json(schema_payload, "bound schema"))
    if type(supplemental) is not dict or set(supplemental) != {
        "schema_version", "canonicalization", "base_payload", "vectors"
    }:
        raise ValueError("supplemental corpus fields differ")
    if supplemental["schema_version"] != "1" or supplemental["canonicalization"] != (
        "recursively_sorted_keys_compact_utf8_json"
    ):
        raise ValueError("supplemental corpus fixed configuration differs")
    vectors = supplemental["vectors"]
    if type(vectors) is not list or not 10 <= len(vectors) <= 40:
        raise ValueError("supplemental vector count differs")
    ids = [item.get("id") for item in vectors if type(item) is dict]
    if len(ids) != len(vectors) or len(ids) != len(set(ids)):
        raise ValueError("supplemental vector identifiers differ")
    if type(expected) is not dict or set(expected) != {
        "schema_version", "validator_configurations", "vectors"
    }:
        raise ValueError("expected-results fields differ")
    if expected["schema_version"] != "1" or expected["validator_configurations"] != (
        EXPECTED_VALIDATOR_CONFIGURATIONS
    ):
        raise ValueError("validator configurations differ from verifier-owned policy")
    expected_ids = [item.get("id") for item in expected["vectors"] if type(item) is dict]
    base = _json(corpus_payload, "base corpus")
    all_ids = [item["id"] for item in base["vectors"]] + ids
    if expected_ids != all_ids or len(expected_ids) != len(set(expected_ids)):
        raise ValueError("expected results do not cover each vector exactly once")
    excluded = {"invalid-duplicate-key", "invalid-nonstandard-number"}
    for item in expected["vectors"]:
        required = {"id", "parse", "schema", "structural_agreement_denominator"}
        if type(item) is not dict or set(item) != required:
            raise ValueError("expected vector fields differ")
        if item["structural_agreement_denominator"] != (item["id"] not in excluded):
            raise ValueError("decoder-boundary denominator differs")
    expected_by_id = {item["id"]: item for item in expected["vectors"]}
    vector_contracts = []
    for identifier, raw_payload in _raw_vectors(base, supplemental):
        item = expected_by_id[identifier]
        vector_contracts.append({
            "id": identifier,
            "raw_payload_sha256": _sha(raw_payload.encode("utf-8")),
            "parse_expected": item["parse"],
            "schema_expected": item["schema"],
            "structural_agreement_denominator": item["structural_agreement_denominator"],
        })
    return {
        "schema_sha256": _sha(schema_payload),
        "base_corpus_sha256": _sha(corpus_payload),
        "supplemental_corpus_sha256": _sha(payloads["supplemental-corpus.json"]),
        "vector_ids": all_ids,
        "vector_contracts": vector_contracts,
    }


def build(project: Path) -> dict[str, bytes]:
    root = project.joinpath(*ROOT_PARTS)
    actual = {entry.name for entry in os.scandir(root)}
    if not actual.issubset(EXPECTED_FILES) or not set(STATIC_FILES).issubset(actual):
        raise ValueError("compatibility inventory differs")
    payloads = {name: _read(root / name) for name in STATIC_FILES}
    bindings = _validate_contracts(root, project, payloads)
    inventory = [
        {"path": name, "sha256": _sha(payload), "bytes": len(payload)}
        for name, payload in sorted(payloads.items())
    ]
    manifest = {
        "schema_version": "1",
        "component": {"name": "maintainer-policy-declaration-compatibility", "version": "2"},
        "status": "prepared_not_executed_locally",
        "claim_boundary": BOUNDARY,
        "bindings": bindings,
        "inventory": inventory,
    }
    manifest_payload = (json.dumps(manifest, indent=2) + "\n").encode()
    expected = _json(payloads["expected-results.json"], "expected results")
    receipt = {
        "schema_version": "1",
        "result": "closed_harness_prepared",
        "manifest_sha256": _sha(manifest_payload),
        "validator_configurations": EXPECTED_VALIDATOR_CONFIGURATIONS,
        "hosted_observations": {
            "python_jsonschema_4_26_0": "not_observed",
            "node_ajv_8_20_0": "not_observed",
        },
        "claim_boundary": BOUNDARY,
    }
    return {
        "manifest.json": manifest_payload,
        "prepared-receipt.json": (json.dumps(receipt, indent=2) + "\n").encode(),
    }


def _write(path: Path, payload: bytes) -> None:
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


def run(project: Path, check: bool) -> dict[str, object]:
    project = project.absolute()
    root = project.joinpath(*ROOT_PARTS)
    artifacts = build(project)
    if check:
        if {entry.name for entry in os.scandir(root)} != EXPECTED_FILES:
            raise ValueError("compatibility inventory is not closed")
        for name, payload in artifacts.items():
            if _read(root / name) != payload:
                raise ValueError(f"stale compatibility artifact: {name}")
    else:
        for name, payload in artifacts.items():
            _write(root / name, payload)
    return json.loads(artifacts["prepared-receipt.json"])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run(Path(args.project), args.check), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
