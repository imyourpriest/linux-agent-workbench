# Declaration structural interoperability companion v1

This directory is a prototype companion to schema 1 of the strict
`maintainer-policy-declaration` parser. It is not a standard, detector, authorization artifact,
permission grant, current-policy claim, or enforcement gate. The Python parser remains
authoritative for accepted local declarations.

`schema.json` is a JSON Schema Draft 2020-12 structural profile. `corpus.json` contains fixed
valid, invalid, and ambiguous vectors. The checked receipt records only the authoritative parser
results actually exercised locally; no independent JSON Schema implementation was installed or
tested, so the profile expectations are corpus metadata rather than independent-validator
conformance evidence.

JSON Schema cannot by itself preserve this parser's input boundary. In particular, validator and
JSON-decoder behavior can differ for duplicate keys and non-standard numbers; the profile does not
enforce the parser's byte, nesting, or node/resource bounds; pattern checks do not derive the
canonical ID; and structural keywords do not establish the kind-specific URL and same-repository
provenance, date/currentness, successor lineage, supplier identity or authority, current permission,
or authorization. Format assertion behavior also varies by validator configuration.

The generated `AI_POLICY.draft.md` and `PULL_REQUEST_TEMPLATE.fragment.md` are deterministic,
non-authorizing projections of the one validated synthetic vector. They preserve every controlled
dimension, including `not_declared` and `conditional`, and label the projection lossy: notes,
provenance, lineage, date, source digest, identity, authority, and currentness cannot be converted
into platform enforcement. Nothing generates rulesets, creates issues, submits forms, or executes
repository content.

Only the exact tuple `valid` / structural `accept` / strict expected `accept` / strict observed
`accept` may supply a projection. Other allowed corpus tuples are closed and cannot become a
projection source. `not_declared` disclosure, review, and accountability values do not become
contributor obligations; the PR fragment labels any future requirements as independent maintainer
proposals for review.

The provided project directory is an explicitly trusted, non-adversarial parent boundary. The
generator rejects link, junction, and reparse components below that boundary through the companion
directory and rechecks the chain and output leaf before replacement. It does not claim race-proof
containment if an adversary can concurrently replace the trusted project parent or its components.

Regenerate and check from `patch-cabinet/`:

```sh
python -m patch_cabinet.declaration_interop --project .
python -m patch_cabinet.declaration_interop --project . --check
```

Draft 2020-12 reference: <https://json-schema.org/specification>. `AGENTS.md` is separate Markdown
agent guidance: <https://agents.md/>. Adjacent OpenSSF work is evolving and does not endorse this
prototype: <https://github.com/ossf/tac/pull/605>.
