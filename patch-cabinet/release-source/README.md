# Maintainer policy declaration 0.2.0 portable candidate

This archive is a self-contained, unpublished release candidate for the schema-1 declaration
component. Read `SPECIFICATION.md`, replace every placeholder in
`starter-unverified-project.json`, and validate one record with Python 3.12 or later:

```text
python maintainer_policy_declaration.py validate path/to/record.json
```

The included synthetic example uses the reserved `example.invalid` namespace. Structural
validation does not authenticate identity or authority, verify source truth or current policy,
or authorize contact or submission. SHA-256 values are recomputable fingerprints, not signatures,
attestations, or external trust. This candidate is not a GitHub release and has no adoption claim.
