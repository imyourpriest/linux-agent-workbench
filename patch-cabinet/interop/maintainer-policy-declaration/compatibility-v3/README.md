# Declaration structural compatibility harness v3

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
