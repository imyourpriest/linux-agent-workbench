"""Build and verify the one inert policy-starter lineage successor."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from typing import Sequence

from .policy_starter import EXPECTED_CONTENT_SHA256


ROOT_NAME = "policy-clarity-candidate-v1"
ARCHIVE = "maintainer-ai-policy-clarity-v0.1.0.zip"
STATIC_FILES = ("ISSUE_FORM_DRAFT.yml", "LANDING_DRAFT.md", "MEASUREMENT_CONTRACT.json", "README.md", "SCOPE_LIMITS.md", "SUCCESSOR_CONTRACT.json")
GENERATED_FILES = (ARCHIVE, f"{ARCHIVE}.sha256", "manifest.json", "validation-receipt.json")
EXPECTED_FILES = set(STATIC_FILES) | set(GENERATED_FILES)
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,119}$")
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
BOUNDARY = "Inert public draft and unpromoted direct successor only; no activation, private input, contact, analytics, listing, checkout, payment, customer, demand, or production-enforcement claim."
EXPECTED_SOURCE_SHA256 = {
    "ISSUE_FORM_DRAFT.yml":"dabec597d50448a9cac98b84717abb694175de8e2a7a141e894e9490d15f0f1e",
    "LANDING_DRAFT.md":"674b7def0e52895003a567ff821e91eaeb22c4fba63c823b8450776517191d84",
    "MEASUREMENT_CONTRACT.json":"3ecdb5bb1cbe87f236db30c2b71e77191c01163352d402a0657ededa007c1ebd",
    "README.md":"61c9559ed3bace65c34b44c980cea6a0a6cb3065faa5908b2722e93500bf45a6",
    "SCOPE_LIMITS.md":"fac8528211b2aa3e92811e11c1e787ea227b9296e61df34ec73d91f98628692c",
    "SUCCESSOR_CONTRACT.json":"fa686a87da311560f16b80c3b208620633b8fe974f2dbb26988f78aa7cd9ff2b",
}
OUTPUT_MAPPING = {
    "README.md":"README.md", "SCOPE.md":"SCOPE_LIMITS.md", "ASYNC_HANDOFF.md":"ISSUE_FORM_DRAFT.yml",
    "AUDIT.md":"MEASUREMENT_CONTRACT.json", "DECISION_MATRIX.md":"LANDING_DRAFT.md", "CONTRIBUTING.md":"LANDING_DRAFT.md",
    "ISSUE_PR_CHECKLIST.md":"ISSUE_FORM_DRAFT.yml", "mpd-v1-cb8c158f561d0387ddb6059fa1fe43038a988c27ec2982cc07bdc79f2b301d37.json":"SUCCESSOR_CONTRACT.json",
}
FUTURE_GATES = [
    "complete_independently_verified_SEL_final_capture", "SEL_frozen_and_no_incident",
    "exact_final_diff_privacy_and_digest_review", "new_prospective_control_decision_selects_exactly_one_candidate_and_marks_other_inert_or_retired",
    "separate_legal_terms_privacy_merchant_and_payment_review", "new_external_action_decision",
]
PREDECESSOR_RELEASE_ROOT = "policy-release-experiment"
PREDECESSOR_RELEASE_INVENTORY = {
    "ACTIVATION_CONTRACT.json", "ISSUE_FORM_DRAFT.yml", "MEASUREMENT_TEMPLATE.json",
    "README.md", "RELEASE.json", "RELEASE_BODY.md", "ai-policy-starter-v0.1.0.zip",
    "ai-policy-starter-v0.1.0.zip.sha256", "manifest.json", "validation-receipt.json",
}
PREDECESSOR_RELEASE_BINDING = {
    "location": "support-eval-lab/policy-release-experiment",
    "experiment_id": "policy-release-r004",
    "status": "prepared_not_activated",
    "tag": "ai-policy-starter-v0.1.0",
    "asset": {
        "path": "ai-policy-starter-v0.1.0.zip", "bytes": 9433,
        "sha256": "e76a5999e618002d69481428a1b08952a2b77ab8f516c3de9e6b51971d8ccd4a",
    },
    "checksum": {
        "path": "ai-policy-starter-v0.1.0.zip.sha256",
        "line": "e76a5999e618002d69481428a1b08952a2b77ab8f516c3de9e6b51971d8ccd4a  ai-policy-starter-v0.1.0.zip\n",
        "sha256": "3c65fff0ccc9184d0b91f08b9e0f798d26c2128e063bab81c55c08846d79f7d1",
    },
    "files": {
        "ACTIVATION_CONTRACT.json":"0fdb0d7829364f79d28aab1755a2b9aa1025b5f20161addd0377c7ad4ddfead5",
        "ISSUE_FORM_DRAFT.yml":"abf004a183e4779bc53af6a384549ea09a3e58a8f1db1302a2b0b86127a10b5b",
        "MEASUREMENT_TEMPLATE.json":"ebe7bbdb8a5c54239cbabe49cba18bef3eb1f9a82c9179692c6401ade0d0046d",
        "README.md":"a65fa245bf04dc0b6f2636ca7befc475986d3ab09b90fdb2cb6dfa0d1e4a9e3d",
        "RELEASE.json":"86cde277eb197924cb0a29e8f1f2af0da9f8d467e6db2113ae65db2b0d513717",
        "RELEASE_BODY.md":"ff2925f70876c3881ca515084b5cc86e08bf2be0a8f4ff63479f6e9dfa4b60c3",
        "manifest.json":"f644c46dd90de3dcda6ef82e7b0eef49990bef65946ed37c75a5e9ae4d26ea5c",
        "validation-receipt.json":"8db6456407a45ea2019e945c32f18f7d6c96349ff093797143710b99365e141f",
    },
    "hash_boundary": "recomputable_consistency_fingerprints_not_signatures_or_external_trust",
}


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _json(payload: bytes, label: str) -> object:
    try: return json.loads(payload.decode("utf-8"), object_pairs_hook=_duplicates, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error: raise ValueError(f"{label} is not strict JSON") from error


def _unsafe_path(path: Path, inspected: os.stat_result) -> bool:
    is_junction=getattr(path,"is_junction",None); reparse=getattr(stat,"FILE_ATTRIBUTE_REPARSE_POINT",0)
    return path.is_symlink() or (callable(is_junction) and is_junction()) or bool(reparse and getattr(inspected,"st_file_attributes",0) & reparse)


def _check_root(root: Path) -> None:
    inspected=root.lstat()
    if _unsafe_path(root,inspected) or not stat.S_ISDIR(inspected.st_mode): raise ValueError("candidate root must be a non-link regular directory")


def _read_payload(path: Path, *, text: bool) -> bytes:
    before = path.lstat()
    if _unsafe_path(path,before) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1: raise ValueError("candidate files must be single-link regular files")
    flags=os.O_RDONLY|getattr(os,"O_BINARY",0)|getattr(os,"O_NOFOLLOW",0); descriptor=os.open(path,flags)
    try:
        opened=os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or (before.st_dev,before.st_ino)!=(opened.st_dev,opened.st_ino): raise ValueError("candidate file changed or aliases another path")
        chunks=[]; remaining=131_073
        while remaining:
            chunk=os.read(descriptor,remaining)
            if not chunk: break
            chunks.append(chunk); remaining-=len(chunk)
        payload=b"".join(chunks)
    finally: os.close(descriptor)
    if len(payload)>131_072: raise ValueError("candidate file exceeds limit")
    if text:
        if b"\r" in payload or b"\x00" in payload: raise ValueError("candidate file has unsafe newlines or NUL")
        try: decoded=payload.decode("utf-8")
        except UnicodeDecodeError as error: raise ValueError("candidate text must be UTF-8") from error
        if any(unicodedata.category(character) in {"Cc","Cf","Zl","Zp"} and character not in {"\n","\t"} for character in decoded): raise ValueError("candidate text contains unsafe control or formatting characters")
    return payload


def _read(path: Path) -> bytes:
    return _read_payload(path,text=True)


def _validate_registry(raw: object) -> None:
    if type(raw) is not dict or set(raw) != {"schema_version","lineage_id","selected_for_activation","predecessor_release","candidates"}: raise ValueError("registry fields differ")
    if raw["schema_version"] != "1" or raw["lineage_id"] != "ai-contribution-policy-starter-audit" or raw["selected_for_activation"] is not None: raise ValueError("registry fixed values differ")
    if raw["predecessor_release"] != PREDECESSOR_RELEASE_BINDING: raise ValueError("registry predecessor release binding differs")
    candidates = raw["candidates"]
    if type(candidates) is not list or len(candidates) != 2: raise ValueError("registry must contain predecessor and one successor")
    by_id = {item.get("candidate_id"): item for item in candidates if type(item) is dict}
    if len(by_id) != 2 or set(by_id) != {"policy-starter-synthetic-v1","maintainer-ai-policy-clarity-synthetic-v1"}: raise ValueError("candidate identifiers differ")
    predecessor = by_id["policy-starter-synthetic-v1"]; successor = by_id["maintainer-ai-policy-clarity-synthetic-v1"]
    common = {"candidate_id","lineage_id","path","archive","component_version","experiment_id","price","predecessor_id","successor_id","activated","status"}
    if set(predecessor) != common or set(successor) != common: raise ValueError("candidate fields differ")
    if any(item["lineage_id"] != raw["lineage_id"] or item["activated"] is not False or item["price"] != "$79_unvalidated_hypothesis" for item in candidates): raise ValueError("lineage, activation, or price differs")
    if predecessor != {"candidate_id":"policy-starter-synthetic-v1","lineage_id":raw["lineage_id"],"path":"policy-starter","archive":None,"component_version":"0.1.0","experiment_id":"policy-release-r004","price":"$79_unvalidated_hypothesis","predecessor_id":None,"successor_id":"maintainer-ai-policy-clarity-synthetic-v1","activated":False,"status":"inert_predecessor_pending_future_exclusive_selection"}: raise ValueError("predecessor record differs")
    if successor != {"candidate_id":"maintainer-ai-policy-clarity-synthetic-v1","lineage_id":raw["lineage_id"],"path":ROOT_NAME,"archive":ARCHIVE,"component_version":"0.1.0","experiment_id":"policy-clarity-r005","price":"$79_unvalidated_hypothesis","predecessor_id":"policy-starter-synthetic-v1","successor_id":None,"activated":False,"status":"inert_successor_pending_future_exclusive_selection"}: raise ValueError("successor record differs")


def _zip_payload(payloads: dict[str, bytes]) -> bytes:
    with tempfile.SpooledTemporaryFile(max_size=1_000_000) as stream:
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
            for name in sorted(payloads):
                if not SAFE_NAME.fullmatch(name): raise ValueError("unsafe archive name")
                info=zipfile.ZipInfo(name, FIXED_TIME); info.compress_type=zipfile.ZIP_STORED; info.create_system=3; info.external_attr=(0o100644 << 16)
                archive.writestr(info, payloads[name])
        stream.seek(0); return stream.read()


def _validate_archive(payload: bytes, sources: dict[str, bytes]) -> None:
    with tempfile.SpooledTemporaryFile(max_size=1_000_000) as stream:
        stream.write(payload); stream.seek(0)
        with zipfile.ZipFile(stream) as archive:
            infos=archive.infolist(); names=[item.filename for item in infos]
            if names != sorted(STATIC_FILES) or len(names) != len(set(names)): raise ValueError("archive inventory/order differs")
            for info in infos:
                pure=PurePosixPath(info.filename); mode=(info.external_attr >> 16) & 0o177777
                if not SAFE_NAME.fullmatch(info.filename) or pure.is_absolute() or ".." in pure.parts or "\\" in info.filename or info.is_dir(): raise ValueError("unsafe archive entry")
                if stat.S_ISLNK(mode) or mode & 0o111 or info.compress_type != zipfile.ZIP_STORED or info.date_time != FIXED_TIME: raise ValueError("archive metadata differs")
                if archive.read(info) != sources[info.filename]: raise ValueError("archive/source mismatch")


def _verify_predecessor_release(project: Path, binding: object) -> None:
    if binding != PREDECESSOR_RELEASE_BINDING: raise ValueError("predecessor release binding differs")
    root=project/PREDECESSOR_RELEASE_ROOT; _check_root(root)
    if {entry.name for entry in os.scandir(root)} != PREDECESSOR_RELEASE_INVENTORY: raise ValueError("predecessor release inventory differs")
    asset=_read_payload(root/PREDECESSOR_RELEASE_BINDING["asset"]["path"],text=False)
    if len(asset) != PREDECESSOR_RELEASE_BINDING["asset"]["bytes"] or _sha(asset) != PREDECESSOR_RELEASE_BINDING["asset"]["sha256"]: raise ValueError("predecessor release asset differs")
    checksum=_read(root/PREDECESSOR_RELEASE_BINDING["checksum"]["path"])
    if checksum.decode("utf-8") != PREDECESSOR_RELEASE_BINDING["checksum"]["line"] or _sha(checksum) != PREDECESSOR_RELEASE_BINDING["checksum"]["sha256"]: raise ValueError("predecessor release checksum differs")
    payloads={name:_read(root/name) for name in PREDECESSOR_RELEASE_BINDING["files"]}
    if {name:_sha(payload) for name,payload in payloads.items()} != PREDECESSOR_RELEASE_BINDING["files"]: raise ValueError("predecessor release file binding differs")
    release=_json(payloads["RELEASE.json"],"predecessor release metadata")
    manifest=_json(payloads["manifest.json"],"predecessor manifest")
    activation=_json(payloads["ACTIVATION_CONTRACT.json"],"predecessor activation contract")
    receipt=_json(payloads["validation-receipt.json"],"predecessor validation receipt")
    if release.get("tag_name") != PREDECESSOR_RELEASE_BINDING["tag"] or release.get("status") != PREDECESSOR_RELEASE_BINDING["status"] or release.get("asset_path") != PREDECESSOR_RELEASE_BINDING["asset"]["path"] or release.get("checksum_path") != PREDECESSOR_RELEASE_BINDING["checksum"]["path"]: raise ValueError("predecessor release tag/status/path differs")
    if manifest.get("experiment_id") != PREDECESSOR_RELEASE_BINDING["experiment_id"] or manifest.get("status") != PREDECESSOR_RELEASE_BINDING["status"] or manifest.get("inert_location") != PREDECESSOR_RELEASE_BINDING["location"] or manifest.get("asset") != PREDECESSOR_RELEASE_BINDING["asset"]: raise ValueError("predecessor experiment binding differs")
    if activation.get("status") != PREDECESSOR_RELEASE_BINDING["status"] or activation.get("asset_sha256") != PREDECESSOR_RELEASE_BINDING["asset"]["sha256"] or activation.get("time_alone_authorizes_activation") is not False: raise ValueError("predecessor activation semantics differ")
    if receipt.get("status") != PREDECESSOR_RELEASE_BINDING["status"] or receipt.get("asset_sha256") != PREDECESSOR_RELEASE_BINDING["asset"]["sha256"] or receipt.get("manifest_sha256") != PREDECESSOR_RELEASE_BINDING["files"]["manifest.json"] or receipt.get("activation_authorized") is not False: raise ValueError("predecessor receipt semantics differ")


def build(project: Path) -> dict[str, bytes]:
    root=project/ROOT_NAME; _check_root(root); actual={entry.name for entry in os.scandir(root)}
    if not actual.issubset(EXPECTED_FILES) or not set(STATIC_FILES).issubset(actual): raise ValueError("candidate inventory differs")
    registry_payload=_read(project/"candidate-registry.json"); registry=_json(registry_payload,"registry"); _validate_registry(registry); _verify_predecessor_release(project,registry["predecessor_release"])
    sources={name:_read(root/name) for name in STATIC_FILES}
    if {name:_sha(payload) for name,payload in sources.items()} != EXPECTED_SOURCE_SHA256: raise ValueError("candidate source differs from verifier-owned digests")
    successor_contract=_json(sources["SUCCESSOR_CONTRACT.json"],"successor contract")
    if type(successor_contract) is not dict or set(successor_contract) != {"schema_version","lineage_id","predecessor_id","successor_id","direct_successor","fork_or_competing_candidate","activated","predecessor_release_binding","predecessor_fixture_sha256","predecessor_to_successor_output_mapping"}: raise ValueError("successor contract fields differ")
    if successor_contract != {"schema_version":"1","lineage_id":"ai-contribution-policy-starter-audit","predecessor_id":"policy-starter-synthetic-v1","successor_id":"maintainer-ai-policy-clarity-synthetic-v1","direct_successor":True,"fork_or_competing_candidate":False,"activated":False,"predecessor_release_binding":PREDECESSOR_RELEASE_BINDING,"predecessor_fixture_sha256":EXPECTED_CONTENT_SHA256,"predecessor_to_successor_output_mapping":OUTPUT_MAPPING}: raise ValueError("predecessor release, fixture, or output mapping differs")
    measurement=_json(sources["MEASUREMENT_CONTRACT.json"],"measurement contract")
    if measurement != {"schema_version":"1","experiment_id":"policy-clarity-r005","status":"pending_future_exclusive_selection","activation":False,"selected_for_activation":None,"future_gates":FUTURE_GATES,"time_alone_authorizes_activation":False,"collection":"none","payment":"disabled"}: raise ValueError("measurement/activation contract differs")
    archive=_zip_payload(sources); _validate_archive(archive,sources)
    checksum=f"{_sha(archive)}  {ARCHIVE}\n".encode()
    generator_path=Path(__file__); generator_payload=generator_path.read_bytes()
    predecessor_binding_payload=(json.dumps(PREDECESSOR_RELEASE_BINDING,sort_keys=True,separators=(",",":") )+"\n").encode()
    manifest={"schema_version":"1","candidate_id":"maintainer-ai-policy-clarity-synthetic-v1","status":"inert_successor_pending_future_exclusive_selection","claim_boundary":BOUNDARY,"registry_sha256":_sha(registry_payload),"predecessor_release_binding":PREDECESSOR_RELEASE_BINDING,"predecessor_release_binding_sha256":_sha(predecessor_binding_payload),"generator":{"path":"src/support_eval_lab/policy_successor.py","sha256":_sha(generator_payload)},"sources":[{"path":name,"sha256":_sha(payload),"bytes":len(payload)} for name,payload in sorted(sources.items())],"archive":{"path":ARCHIVE,"sha256":_sha(archive),"bytes":len(archive),"compression":"ZIP_STORED","fixed_timestamp":"1980-01-01T00:00:00"}}
    manifest_payload=(json.dumps(manifest,indent=2)+"\n").encode()
    receipt={"schema_version":"1","result":"valid_inert_direct_successor_bundle","candidate_id":manifest["candidate_id"],"manifest_sha256":_sha(manifest_payload),"archive_sha256":_sha(archive),"registry_sha256":_sha(registry_payload),"predecessor_release_binding_sha256":_sha(predecessor_binding_payload),"claim_boundary":BOUNDARY,"revenue_usd":"0.00"}
    return {ARCHIVE:archive,f"{ARCHIVE}.sha256":checksum,"manifest.json":manifest_payload,"validation-receipt.json":(json.dumps(receipt,indent=2)+"\n").encode()}


def _write(path: Path, payload: bytes) -> None:
    if path.exists():
        inspected=path.lstat()
        if _unsafe_path(path,inspected) or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1: raise ValueError("generated output must be a single-link regular file")
    descriptor, temporary=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(descriptor,"wb") as stream: stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        if path.exists():
            inspected=path.lstat()
            if _unsafe_path(path,inspected) or not stat.S_ISREG(inspected.st_mode) or inspected.st_nlink != 1: raise ValueError("generated output changed before replacement")
        os.replace(temporary,path)
    except BaseException: Path(temporary).unlink(missing_ok=True); raise


def run(project: Path, check: bool) -> dict[str, object]:
    project=project.absolute(); root=project/ROOT_NAME; artifacts=build(project)
    if check:
        if {entry.name for entry in os.scandir(root)} != EXPECTED_FILES: raise ValueError("candidate inventory is not closed")
        for name,payload in artifacts.items():
            current=_read_payload(root/name,text=name!=ARCHIVE)
            if name==ARCHIVE: _validate_archive(current,{item:_read(root/item) for item in STATIC_FILES})
            if current != payload: raise ValueError(f"stale candidate artifact: {name}")
    else:
        for name,payload in artifacts.items(): _write(root/name,payload)
    return json.loads(artifacts["validation-receipt.json"])


def main(argv: Sequence[str] | None=None) -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--project",default="."); parser.add_argument("--check",action="store_true"); args=parser.parse_args(argv)
    print(json.dumps(run(Path(args.project),args.check),indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
