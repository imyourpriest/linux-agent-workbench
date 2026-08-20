# Declaration structural compatibility harness v2

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

This additive successor preserves the published v1 harness and keeps Ajv `8.20.0` while pinning
its `fast-uri` transitive dependency to `3.1.5`. The migration selection is supported by these
official GitHub Advisory Database records reviewed on 2026-08-20:

- https://github.com/advisories/GHSA-q3j6-qgpj-74h6
- https://github.com/advisories/GHSA-v39h-62p7-jpjc
- https://github.com/advisories/GHSA-4c8g-83qw-93j6
- https://github.com/advisories/GHSA-v2hh-gcrm-f6hx
- https://github.com/advisories/GHSA-7p8r-x3mc-p8w7

Those records show first patched 3.x versions 3.1.1 through 3.1.5 respectively, so 3.1.5 is the
first reviewed 3.x version patched for all five. `node-dependency-evidence.json` separately binds
only selected fields transcribed from official npm registry metadata; it is not a raw response
archive. That record and a hosted passing vector run would not prove downloaded bytes, runtime
behavior, exploitation resistance, isolation, future availability, or production security.
