# Patch Cabinet verifier capsule 0.3.0

This capsule is the active schema-2 environment for Patch Cabinet engine 0.3.0 with policy
`season-1.3` and `packaging==26.3`.

Policy `season-1.3` makes workflow consent a hard eligibility condition. `ai_policy: allows`
means pinned upstream text permits this AI-operated contribution workflow; permission for
human-led AI assistance alone is insufficient when autonomous submissions are barred. Unknown
policy is ineligible rather than a scoring caution. Schema 2 binds the controlled status and basis
to a same-repository policy file URL pinned at the candidate commit and emits that binding in the
result evidence.

The vendored wheel is the unmodified PyPI file
`packaging-26.3-py3-none-any.whl`, SHA-256
`d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c`. Its upstream license
files remain inside the wheel. Evidence replay runs the wheel directly from an isolated Python
process; it performs no network installation.

Replay loads the hash-pinned frozen policy at `verifiers/policies/season-1.3/policy.py` directly
and must reproduce the registered synthetic JSON/Markdown vector before this engine is accepted.

Any source, policy, renderer, dependency, or serialization change requires a new engine identity.
