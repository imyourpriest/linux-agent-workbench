"""Prepare the closed, non-authorizing declaration compatibility v3 harness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Sequence


ROOT_PARTS = ("interop", "maintainer-policy-declaration", "compatibility-v3")
V2_ROOT_PARTS = ("interop", "maintainer-policy-declaration", "compatibility-v2")
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
V2_SOURCE_SHA256 = "6062c7c10d0259180fa3e32899926758909531c94dbabb704cc8db2177fb5ea9"
V2_FILE_SHA256 = {
    "README.md": "4201807b02e17c1fceaa553102265dd44c1bb13f78c87eec032626aa24ff0e04",
    "base-corpus-binding.json": "2fb480e9c62c5b08d02951d97ff2870287a19a226ff4382f3613796b2b24848b",
    "expected-results.json": "b0a34e4101026be4daf4683ad6f319f15e1ad6dc9d3f95783d2c77912308c0b5",
    "manifest.json": "013a9704723cf8cdbde62007df74e5717477006fa87a7ff2ba1cdffd1a8a1d66",
    "node_runner.mjs": "01c832780af8d589de72424a677456e94ec80435c580167ecdab70c96c8d5698",
    "node-dependency-evidence.json": "efb9fecbc5b7da2fe56ee45b58bdbf3ce78b5b54a14c1d0cdce4c85a6e1afdf9",
    "package-lock.json": "c96a9ea9d24d5e7106642b544f7288ffc87d792d135686eacc51ae5de60e44cd",
    "package.json": "83931144252b8146874b7378bc3fa5e35bc5ad149249c7b2d40a098098412161",
    "prepared-receipt.json": "4adf69d286af0bf7699ff8a3fe1aabd3279b18d3f84b54439da15c998a2fc0ba",
    "python_runner.py": "77fe7cba98f822b41b38b497eeeaa76148f3628f7254f45d6eb2bb557ee976f5",
    "requirements.lock": "05bae31857a05a9c7a8a2cd779caf2b54b2705e975a15d36dce8f1040dea12ae",
    "supplemental-corpus.json": "2d92b036bf285269260f4dc222f77ca087a41fcf28a93823a66d76c82ad23e2c",
}
UNCHANGED_STATIC_FILES = (
    "base-corpus-binding.json",
    "supplemental-corpus.json",
    "expected-results.json",
    "requirements.lock",
)
BOUNDARY = (
    "Prepared structural compatibility only. Hosted observations are not observed locally and "
    "would not establish attestation, authentication, semantic correctness, provenance, "
    "freshness, privacy, isolation, standard adoption, source truth, permission, or production "
    "enforcement. Dependency acquisition is network-enabled."
)
EXPECTED_NODE_DEPENDENCY_EVIDENCE = {
    "schema_version": "1",
    "dependency": "fast-uri",
    "registry_metadata_source": "https://registry.npmjs.org/fast-uri/3.1.7",
    "observed_at": "2026-09-07",
    "version": "3.1.7",
    "resolved": "https://registry.npmjs.org/fast-uri/-/fast-uri-3.1.7.tgz",
    "integrity": (
        "sha512-dOvZVzjdZdz7phd9v6jCbwxrBW3fK6n8Rc0CtdmM4bumzMnxywBYhuph6J819RRw/"
        "ku+rLbelwfMunktuzVVHg=="
    ),
    "registry_shasum": "743157d957f3cbb4c65310e033dc2ad4ad7dc60a",
    "license": "BSD-3-Clause",
    "install_script_observed": False,
    "engines_field_observed": False,
    "claim_boundary": (
        "Selected fields transcribed from official npm registry metadata; this is not a raw "
        "response archive and does not establish downloaded bytes, runtime behavior, "
        "exploitation resistance, isolation, future availability, or production security."
    ),
}
README = """# Declaration structural compatibility harness v3

This closed harness prepares two separate hosted adapters for the existing declaration Draft
2020-12 structural profile: Python `jsonschema==4.26.0` and Node `ajv==8.20.0`. It does not run
either third-party validator locally. Dependency acquisition in a hosted job uses the network;
the later validation phase merely has no configured remote loader.

Both runners reject duplicate JSON keys or non-standard numbers at the decoder boundary, preflight
every schema reference keyword, allow only the two exact local `$defs` fragments, and compare every
parse and schema result with `expected-results.json`. Duplicate-key and NaN vectors remain decoder
observations and are excluded from the structural-agreement denominator. Date `format` is
deliberately ignored by both exact configurations.

Compatibility `parse` means acceptance by the strict JSON decoder only; it does not mean
acceptance by the authoritative declaration parser. The frozen v1 schema's character/shape
pattern structurally accepts dot-only path segments, including the `..` segment in this corpus,
while the authoritative parser separately rejects `.` and `..` segments. Recording that gap is
not path-safety evidence or semantic acceptance of the declaration.

A hosted success could establish only the configured structural results for its named commit and
run. It would not establish attestation, authentication, semantic correctness, provenance,
freshness, privacy, isolation, standard adoption, source truth, permission, or production
enforcement.

This additive successor preserves the published v1 and v2 harnesses and keeps Ajv `8.20.0` while
pinning its `fast-uri` transitive dependency to `3.1.7`. The v3 generator binds every predecessor
file by SHA-256 and permits only the reviewed version, path, package-lock tuple, runner inventory,
and dependency-evidence changes. The schema profile, corpus, expected results, Python lock, and
validator configurations remain unchanged.

The selection is supported by the official fast-uri 3.1.7 release and GitHub Advisory Database
record reviewed on 2026-09-07:

- https://github.com/fastify/fast-uri/releases/tag/v3.1.7
- https://github.com/advisories/GHSA-qw65-cvwx-89v3

The advisory reports that versions `>=3.0.0 <3.1.7` are affected by port-component injection and
that 3.1.7 is patched. This record does not assert that Rivetloom's fixed corpus or hosted
configuration is exploitable. GHSA-58mr-gqgx-xq4g affects only 3.1.6 and therefore does not apply
to the preserved 3.1.5 predecessor.

`node-dependency-evidence.json` binds only selected fields transcribed from a successful
metadata-only HTTPS GET of the official npm registry record on 2026-09-07; it is not a raw response
archive. No tarball was downloaded locally. That record and a hosted passing vector run would not
prove downloaded bytes, runtime behavior, exploitation resistance, isolation, future availability,
or production security.
""".encode()


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


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _replace_exact(payload: bytes, old: bytes, new: bytes, count: int, label: str) -> bytes:
    if payload.count(old) != count:
        raise ValueError(f"exact v2 {label} transform source differs")
    return payload.replace(old, new)


def _v2_payloads(project: Path) -> dict[str, bytes]:
    root = project.joinpath(*V2_ROOT_PARTS)
    actual = {entry.name for entry in os.scandir(root)}
    if actual != set(V2_FILE_SHA256):
        raise ValueError("exact v2 closed inventory differs")
    payloads = {name: _read(root / name) for name in V2_FILE_SHA256}
    for name, expected in V2_FILE_SHA256.items():
        if _sha(payloads[name]) != expected:
            raise ValueError(f"exact v2 predecessor digest differs: {name}")
    return payloads


def _load_v2(project: Path) -> ModuleType:
    source = project / "src/patch_cabinet/declaration_compatibility_v2.py"
    payload = _read(source)
    if _sha(payload) != V2_SOURCE_SHA256:
        raise ValueError("exact v2 verifier source digest differs")
    module = ModuleType("_rivetloom_compatibility_v2")
    module.__file__ = str(source)
    exec(compile(payload, str(source), "exec"), module.__dict__)
    return module


def _expected_static(project: Path) -> tuple[dict[str, bytes], ModuleType, dict[str, bytes]]:
    predecessor = _v2_payloads(project)
    v2 = _load_v2(project)
    if v2.build(project) != {
        "manifest.json": predecessor["manifest.json"],
        "prepared-receipt.json": predecessor["prepared-receipt.json"],
    }:
        raise ValueError("exact v2 generated artifacts do not replay")
    result = {name: predecessor[name] for name in UNCHANGED_STATIC_FILES}
    result["README.md"] = README
    package = _replace_exact(
        predecessor["package.json"],
        b"maintainer-policy-declaration-compatibility-v2",
        b"maintainer-policy-declaration-compatibility-v3",
        1,
        "package name",
    )
    result["package.json"] = _replace_exact(
        package, b'"version": "2.0.0"', b'"version": "3.0.0"', 1, "package version"
    )
    lock = _replace_exact(
        predecessor["package-lock.json"],
        b"maintainer-policy-declaration-compatibility-v2",
        b"maintainer-policy-declaration-compatibility-v3",
        2,
        "lock name",
    )
    lock = _replace_exact(lock, b'"version": "2.0.0"', b'"version": "3.0.0"', 1, "lock header version")
    lock = _replace_exact(lock, b'"version":"2.0.0"', b'"version":"3.0.0"', 1, "lock root version")
    lock = _replace_exact(lock, b'"version":"3.1.5"', b'"version":"3.1.7"', 1, "fast-uri version")
    lock = _replace_exact(
        lock,
        b"https://registry.npmjs.org/fast-uri/-/fast-uri-3.1.5.tgz",
        EXPECTED_NODE_DEPENDENCY_EVIDENCE["resolved"].encode(),
        1,
        "fast-uri URL",
    )
    lock = _replace_exact(
        lock,
        b"sha512-gHwA1O9LDIcKunMKhObS/HimwtehO1nPUECKAu5TpKgaO19fcWEl4bliWe1jWxVFvIXztJjjQ4L8XQ1EU9f7Jw==",
        EXPECTED_NODE_DEPENDENCY_EVIDENCE["integrity"].encode(),
        1,
        "fast-uri integrity",
    )
    result["package-lock.json"] = lock
    result["python_runner.py"] = _replace_exact(
        predecessor["python_runner.py"], b'"compatibility-v2"', b'"compatibility-v3"', 1, "Python root"
    )
    node = _replace_exact(
        predecessor["node_runner.mjs"], b'"compatibility-v2"', b'"compatibility-v3"', 1, "Node root"
    )
    result["node_runner.mjs"] = _replace_exact(
        node, b'"fast-uri":"3.1.5"', b'"fast-uri":"3.1.7"', 1, "Node inventory"
    )
    result["node-dependency-evidence.json"] = (
        json.dumps(EXPECTED_NODE_DEPENDENCY_EVIDENCE, indent=2) + "\n"
    ).encode()
    return result, v2, predecessor


def build(project: Path) -> dict[str, bytes]:
    root = project.joinpath(*ROOT_PARTS)
    expected_static, v2, predecessor = _expected_static(project)
    actual = {entry.name for entry in os.scandir(root)}
    if not actual.issubset(EXPECTED_FILES) or not set(STATIC_FILES).issubset(actual):
        raise ValueError("compatibility inventory differs")
    payloads = {name: _read(root / name) for name in STATIC_FILES}
    for name in STATIC_FILES:
        if payloads[name] != expected_static[name]:
            raise ValueError(f"v3 file differs from exact v2-derived successor: {name}")
    predecessor_static = {name: predecessor[name] for name in STATIC_FILES}
    bindings = v2._validate_contracts(project.joinpath(*V2_ROOT_PARTS), project, predecessor_static)
    inventory = [
        {"path": name, "sha256": _sha(payload), "bytes": len(payload)}
        for name, payload in sorted(payloads.items())
    ]
    manifest = {
        "schema_version": "1",
        "component": {"name": "maintainer-policy-declaration-compatibility", "version": "3"},
        "status": "prepared_not_executed_locally",
        "claim_boundary": BOUNDARY,
        "predecessor": {
            "component_version": "2",
            "closed_inventory_sha256": V2_FILE_SHA256,
            "verifier_source_sha256": V2_SOURCE_SHA256,
        },
        "bindings": bindings,
        "inventory": inventory,
    }
    manifest_payload = (json.dumps(manifest, indent=2) + "\n").encode()
    receipt = {
        "schema_version": "1",
        "result": "closed_harness_prepared",
        "manifest_sha256": _sha(manifest_payload),
        "validator_configurations": v2.EXPECTED_VALIDATOR_CONFIGURATIONS,
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


def initialize(project: Path) -> dict[str, object]:
    project = project.absolute()
    root = project.joinpath(*ROOT_PARTS)
    if root.exists():
        raise ValueError("compatibility-v3 already exists")
    expected_static, _v2, _predecessor = _expected_static(project)
    root.mkdir()
    for name in STATIC_FILES:
        _write(root / name, expected_static[name])
    for name, payload in build(project).items():
        _write(root / name, payload)
    return run(project, True)


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
    parser.add_argument("--initialize", action="store_true")
    args = parser.parse_args(argv)
    if args.check and args.initialize:
        parser.error("--check and --initialize are mutually exclusive")
    receipt = initialize(Path(args.project)) if args.initialize else run(Path(args.project), args.check)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
