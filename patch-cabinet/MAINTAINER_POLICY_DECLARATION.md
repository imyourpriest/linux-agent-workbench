# Maintainer policy declaration prototype

This standalone component renders trusted-local declaration JSON into reviewable cards. Accepted
project records are maintainer- or operator-supplied and unauthenticated/unverified. Structural
acceptance does not establish the supplier's identity or authority. The component does not fetch or
interpret policy prose, detect AI use, verify repository ownership or authorship, authenticate a
source, establish current policy or permission, score work, authorize contact, or act as a CI merge
gate.

It is deliberately separate from `AGENTS.md`. `AGENTS.md` gives instructions to coding agents
operating inside a repository. This prototype records unauthenticated/unverified, maintainer- or
operator-supplied declarations about contribution practices in a closed shape. Neither format is
treated as proof of identity, authority, or permission.

## Prototype boundary

- Component `maintainer-policy-declaration` version `0.2.0`, schema `1`.
- Local/public 30-day prototype, not a standard or proposed standard.
- Inputs must be explicitly supplied trusted-local JSON. No network, subprocess, policy-prose parser, AI detector, or candidate-engine integration exists.
- The checked-in example uses the reserved `example.invalid` synthetic namespace. It makes no
  existence or identity assertion. The starter contains invalid placeholders and is not validated
  until every placeholder is replaced.
- Output parents are trusted local filesystems. Atomic replacement limits partial output but does not defend against adversarial parent replacement between validation and writing.

## Commands

Installed one-record validation is available after package installation:

```sh
maintainer-policy-declaration validate path/to/mpd-v1-<digest>.json
```

This command safely opens the file once and uses that same payload for strict validation and the
raw-file SHA-256 in its deterministic JSON receipt. That digest is only a recomputable fingerprint,
not a signature. The receipt establishes no supplier identity, authority, authorization, source
truth, policy currentness, or permission to contact or submit.

From `patch-cabinet/`:

```sh
python -m patch_cabinet.maintainer_policy_declaration render \
  data/maintainer-policy-declarations/synthetic/v1 \
  --json-out samples/maintainer-policy-declaration-index.json \
  --markdown-out samples/maintainer-policy-declaration-index.md

python -m patch_cabinet.maintainer_policy_declaration starter \
  unverified_project_declaration
```

## Schema reference

Every record contains exactly these fields. JSON numbers, extra fields, omitted fields, duplicate
keys, invalid UTF-8, a BOM, unsafe controls, and noncanonical values are rejected.

| Field | Required shape or values |
|---|---|
| `schema_version` | Exact string `1` |
| `declaration_id` | `mpd-v1-` plus 64 lowercase SHA-256 hex characters; derivation below |
| `record_kind` | `synthetic_example` or `unverified_project_declaration` |
| `assertion_basis` | Exact value paired with `record_kind` below |
| `repository` | Canonical owner/name under the selected provenance grammar |
| `repository_url` | Exact kind-specific URL below |
| `commit_sha` | 40 lowercase hexadecimal characters |
| `policy_source_url` | Exact kind-specific URL binding repository, commit, and path |
| `policy_path` | Canonical ASCII repository-relative path, maximum 300 characters |
| `source_sha256` | 64 lowercase hexadecimal characters, excluding the all-zero digest |
| `observed_at` | Non-future canonical local date in `YYYY-MM-DD` form |
| `dimensions` | Exactly the 13 dimension keys and values below |
| `disclosure_location` | `pr_description`, `commit_trailer`, `either`, `project_defined`, or `not_declared` |
| `enforcement` | `close_or_reject`, `request_changes`, `label_or_flag`, `maintainer_discretion`, or `not_declared` |
| `supersedes` | `null` or an in-catalog canonical declaration ID |
| `notes` | Nonempty inert text, maximum 500 characters |

The exact record-kind mapping is:

| `record_kind` | Required `assertion_basis` |
|---|---|
| `synthetic_example` | `synthetic_example_not_a_maintainer_assertion` |
| `unverified_project_declaration` | `trusted_local_operator_supplied_unverified_declaration` |

The first nine dimensions—`ai_assisted_code`, `ai_assisted_documentation`,
`ai_authored_issue_text`, `ai_authored_pr_text`, `autonomous_issue_submission`,
`autonomous_pr_submission`, `automated_review_comments`, `good_first_issue_automation`, and
`security_report_automation`—each accept `allowed`, `conditional`, `disallowed`, or
`not_declared`. The remaining dimensions—`disclosure`, `human_review`, `human_accountability`, and
`license_ip_checks`—each accept `required`, `recommended`, or `not_declared`.

If `disclosure` is `required` or `recommended`, `disclosure_location` must be a location other than
`not_declared`. If `disclosure` is `not_declared`, the location must also be `not_declared`. No
other semantic cross-field inference is made.

For `synthetic_example`, repository URLs have the exact shapes
`https://example.invalid/<owner>/<repository>` and
`https://example.invalid/<owner>/<repository>/blob/<commit>/<policy_path>`. The renderer emits the
synthetic source as inert code, not a link. Synthetic records cannot use `github.com` or another
live provider namespace. For `unverified_project_declaration`, the exact shapes are
`https://github.com/<owner>/<repository>` and the same-repository commit-pinned
`https://github.com/<owner>/<repository>/blob/<commit>/<policy_path>`.

The canonical ID is `mpd-v1-` followed by SHA-256 of the UTF-8 bytes of these six strings joined
with a single NUL byte: literal `mpd-v1`, case-folded repository, `record_kind`, full lowercase
commit SHA, case-sensitive `policy_path`, and full lowercase source SHA-256. This uses every
canonical identity field and does not fold punctuation.

A successor must reference an existing different record, preserve the case-folded repository,
policy path, `record_kind`, and `assertion_basis`, and use a later observation date. One record may
have only one direct successor; missing predecessors, forks, and cycles are rejected. Synthetic and
project declarations cannot transition into one another.

The checked-in starter is specifically for `unverified_project_declaration`, has the exact matching
assertion basis, shows each controlled vocabulary in its placeholders, and points back to this
table. It remains invalid until every placeholder is replaced and the ID is derived from the final
fields. Use `starter synthetic_example` to request the separate synthetic shape.

Structural validation and faithful rendering do not verify assertions, source truth, supplier
identity, authorship, repository ownership, current policy, permission to contact or submit, or
eligibility. Cards are not authorization artifacts.

## Evaluation gate

Success during the 30-day prototype requires 3-5 maintainers, at least three unaided complete profiles in 15 minutes or less, every seeded structural and provenance error caught, faithful rendering, and at least two reports of reuse or time benefit without permission confusion.

Stop without building beyond the prototype if fewer than three maintainers participate, completion exceeds 20 minutes per profile, semantic disagreement would require automated prose inference, anyone confuses a card with authorization, or no reuse/time benefit is reported.

## Current public context

The prototype scope was informed by current public examples and discussions captured on 2026-08-10. These sources do not endorse this component and must be revalidated before later decisions:

- AGENTS.md project: https://github.com/agentsmd/agents.md
- AGENTS.md issue 135: https://github.com/agentsmd/agents.md/issues/135
- GitHub Community discussion 185387: https://github.com/orgs/community/discussions/185387
- LLVM policy on AI tools: https://llvm.org/docs/AIToolPolicy.html
- Home Assistant AI policy: https://developers.home-assistant.io/blog/2026/07/20/ai-policy/
- The Carpentries generative-AI policy: https://docs.carpentries.org/policies/genai-policy.html
- OpenSSF practical guide: https://openssf.org/resources/securing-open-source-in-the-age-of-ai-a-practical-guide/
