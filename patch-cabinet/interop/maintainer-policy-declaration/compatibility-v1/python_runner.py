"""Hosted-only adapter for jsonschema 4.26.0; do not import locally."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry


EXPECTED_DISTRIBUTIONS = {
    "attrs": "26.1.0",
    "jsonschema": "4.26.0",
    "jsonschema-specifications": "2025.9.1",
    "referencing": "0.37.0",
    "rpds-py": "2026.6.3",
}


def duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def constant(_value):
    raise ValueError("non-standard number")


def strict_load(raw):
    return json.loads(raw, object_pairs_hook=duplicates, parse_constant=constant)


def preflight(value):
    allowed = {"#/$defs/policy", "#/$defs/expectation"}
    pending = [value]
    while pending:
        current = pending.pop()
        if type(current) is dict:
            for key, child in current.items():
                if key in {"$dynamicRef", "$recursiveRef"}:
                    raise ValueError("dynamic reference rejected")
                if key == "$ref" and child not in allowed:
                    raise ValueError("nonlocal reference rejected")
                pending.append(child)
        elif type(current) is list:
            pending.extend(current)


def no_remote(uri):
    raise ValueError(f"remote retrieval prohibited: {uri}")


def set_pointer(value, pointer, replacement, delete=False):
    parts = pointer.lstrip("/").split("/")
    parent = value
    for part in parts[:-1]:
        parent = parent[part]
    if delete:
        del parent[parts[-1]]
    else:
        parent[parts[-1]] = replacement


def raw_vectors(base_corpus, supplemental):
    result = [(item["id"], item["payload"]) for item in base_corpus["vectors"]]
    for vector in supplemental["vectors"]:
        value = copy.deepcopy(supplemental["base_payload"])
        for operation in vector["operations"]:
            if operation["op"] == "delete":
                set_pointer(value, operation["pointer"], None, delete=True)
            elif operation["op"] == "set":
                set_pointer(value, operation["pointer"], operation["value"])
            elif operation["op"] == "repeat":
                set_pointer(value, operation["pointer"], operation["value"] * operation["count"])
            else:
                raise ValueError("unknown mutation")
        result.append((vector["id"], json.dumps(value, sort_keys=True, separators=(",", ":"))))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    args = parser.parse_args()
    project = Path(args.project)
    root = project / "interop" / "maintainer-policy-declaration" / "compatibility-v1"
    schema = strict_load((project / "interop/maintainer-policy-declaration/v1/schema.json").read_text())
    base = strict_load((project / "interop/maintainer-policy-declaration/v1/corpus.json").read_text())
    supplemental = strict_load((root / "supplemental-corpus.json").read_text())
    expected = strict_load((root / "expected-results.json").read_text())
    manifest_payload = (root / "manifest.json").read_bytes()
    manifest = strict_load(manifest_payload.decode("utf-8"))
    prepared_receipt = strict_load((root / "prepared-receipt.json").read_text())
    manifest_digest = hashlib.sha256(manifest_payload).hexdigest()
    if prepared_receipt["manifest_sha256"] != manifest_digest:
        raise SystemExit("prepared receipt manifest binding differs")
    preflight(schema)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, registry=Registry(retrieve=no_remote))
    expected_by_id = {item["id"]: item for item in expected["vectors"]}
    bound_by_id = {item["id"]: item for item in manifest["bindings"]["vector_contracts"]}
    observations = []
    for identifier, raw in raw_vectors(base, supplemental):
        try:
            instance = strict_load(raw)
            parse_result = "accept"
        except (json.JSONDecodeError, ValueError):
            instance = None
            parse_result = "reject"
        schema_result = (
            "not_run" if instance is None else ("accept" if validator.is_valid(instance) else "reject")
        )
        contract = expected_by_id[identifier]
        raw_digest = hashlib.sha256(raw.encode()).hexdigest()
        bound = bound_by_id[identifier]
        if raw_digest != bound["raw_payload_sha256"]:
            raise SystemExit(f"raw payload binding mismatch: {identifier}")
        if (
            bound["parse_expected"],
            bound["schema_expected"],
            bound["structural_agreement_denominator"],
        ) != (
            contract["parse"],
            contract["schema"],
            contract["structural_agreement_denominator"],
        ):
            raise SystemExit(f"expected outcome binding mismatch: {identifier}")
        if (parse_result, schema_result) != (contract["parse"], contract["schema"]):
            raise SystemExit(f"outcome mismatch: {identifier}")
        observations.append({
            "id": identifier,
            "raw_payload_sha256": raw_digest,
            "observed_parse": parse_result,
            "observed_schema": schema_result,
            "expected_parse": contract["parse"],
            "expected_schema": contract["schema"],
            "structural_agreement_denominator": contract[
                "structural_agreement_denominator"
            ],
        })
    installed = {name: importlib.metadata.version(name) for name in EXPECTED_DISTRIBUTIONS}
    if installed != EXPECTED_DISTRIBUTIONS:
        raise SystemExit("installed distribution inventory differs")
    print(json.dumps({"adapter":"python_jsonschema_4_26_0","manifest_sha256":manifest_digest,"configuration":expected["validator_configurations"]["python_jsonschema_4_26_0"],"installed_distributions":installed,"vectors":observations}, indent=2))


if __name__ == "__main__":
    main()
