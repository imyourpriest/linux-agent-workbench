# Manual policy-profile catalog

This standalone catalog normalizes eight manually reviewed facts from each pinned contribution-policy file. It is deliberately separate from the candidate engine and the contribution-consent classification. A profile repeats the repository, commit, policy path, and source SHA-256 and binds them to exactly one consent record.

The component is `patch-policy-profile-catalog` version `0.1.0`, schema `1`. It accepts only offline JSON from two explicit directories, rejects unknown fields and unsafe inventories, and emits deterministic LF-only JSON and Markdown. It has no fetch, network, subprocess, target-code execution, or prose-detection path.

## Claim boundary

Profiles are historical manual facts. They do not interpret or detect policy prose automatically, establish current permission, make a candidate eligible, or authorize contact or submission. The controlled dimensions are not an allowlist:

- autonomous issue submission: `allowed`, `disallowed`, or `not_explicit`;
- autonomous pull-request submission: `allowed`, `disallowed`, or `not_explicit`;
- human review, disclosure, human accountability, and license/IP checks: `required`, `recommended`, or `not_explicit`;
- good-first-issue automation and security-report automation: `allowed`, `disallowed`, or `not_explicit`.

Every semantic value is a manual normalization of one pinned file. Live candidate work still requires the active engine manifest and a current manual review of policy, issue state, competition, scope, security, attestation, and sponsor-local exclusions.

## Generate the index

From `patch-cabinet/`:

```sh
python -m patch_cabinet.policy_profile_catalog data/policy-profile-catalog/v1 \
  --consent-records data/consent-catalog/v1 \
  --json-out samples/policy-profile-catalog-index.json \
  --markdown-out samples/policy-profile-catalog-index.md
```

## Neutral historical snapshot/query

An optional `--as-of YYYY-MM-DD` mode labels each matched historical record `fresh`, `stale`, or
`unknown` against the documented seven-day candidate window. An observation is fresh at age zero
through seven days, stale after seven days, and unknown when the operator's as-of date precedes
the recorded observation. These are date-window labels only, never a ranking, aggregate trust
score, readiness result, current-permission claim, or authorization.

Explicit controlled-dimension filters use repeated `--where DIMENSION=VALUE` arguments and combine
with AND. The command does not refresh the network, add upstream records, or feed the candidate
engine:

```sh
python -m patch_cabinet.policy_profile_catalog data/policy-profile-catalog/v1 \
  --consent-records data/consent-catalog/v1 \
  --as-of 2026-08-13 \
  --where autonomous_pr_submission=disallowed \
  --json-out samples/policy-profile-catalog-snapshot.json \
  --markdown-out samples/policy-profile-catalog-snapshot.md
```

Published profile records are immutable. A later pinned policy uses a new consent successor and a matching profile successor. A profile's `supersedes` value must exactly equal its bound consent record's value, including `null`; the validator then rejects missing, forked, cyclic, or cross-lineage relationships.

CLI output parents are trusted local filesystems. Atomic replacement limits partial output, but
this component does not claim to resist adversarial output-parent replacement between validation
and writing. Do not direct output into attacker-controlled directories.
