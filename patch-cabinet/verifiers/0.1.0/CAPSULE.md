# Patch Cabinet verifier capsule 0.1.0

This capsule replays schema-1 evidence produced by Patch Cabinet engine 0.1.0 with policy
`season-1.2` and `packaging==26.2`.

The vendored wheel is the unmodified PyPI file
`packaging-26.2-py3-none-any.whl`, SHA-256
`5fc45236b9446107ff2415ce77c807cee2862cb6fac22b8a73826d0693b0980e`. Its upstream license
files remain inside the wheel. The verifier runs the wheel directly from an isolated Python
process; it performs no network installation.

Replay loads the hash-pinned frozen policy at `verifiers/policies/season-1.2/policy.py` directly;
it does not import the mutable active package initializer or engine descriptor.

This capsule is replay-only. It must not generate new evidence bundles.
