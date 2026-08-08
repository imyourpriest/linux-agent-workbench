# Versioned evidence verifiers

`index.json` is the strict, reviewed registry for Patch Cabinet evidence engines. A bundle chooses
nothing executable: its already-receipted policy artifact supplies an engine identity, and the
checker requires that complete provenance tuple to match exactly one registry entry.

Each engine entry binds:

- engine and output-schema identity;
- a frozen policy implementation and its SHA-256;
- exact dependency name/version and an unmodified, hash-pinned offline wheel;
- a versioned replay adapter and its SHA-256;
- a hash-pinned requirements record and capsule note.

The checker validates receipt and artifact bytes first, then starts an isolated child interpreter
for every registered engine. The child loads only the hash-verified frozen policy and replay
adapter, puts the registered wheel at the front of its import path, verifies the dependency origin
and version, freezes the policy date to the recorded observation date, and reproduces canonical
JSON and Markdown byte-for-byte. The active engine must also replay a hash-bound synthetic vector,
so a new engine cannot enter the registry without exercising its serializer and renderer.

Historical capsules are immutable and replay-only. New output uses only the registry's active
engine. Missing, unknown, mismatched, corrupt, unreferenced, or path-escaping entries fail closed.

Run the complete offline replay from the repository root:

```sh
python tools/check_evidence_bundles.py
```

The receipt and registry prove consistency inside the checked tree; they are not an external
signature. Immutability comes from preserving these bytes in reviewed commits on protected Git
history. A verifier result must therefore be tied to the commit that produced it.
