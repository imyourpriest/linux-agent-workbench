# Candidate policy

The policy engine ranks evidence; it does not replace manual verification or maintainer judgment.

## Hard eligibility

A candidate must be:

- a public, non-archived repository;
- covered by an explicit valid SPDX expression whose identifiers are in the reviewed Season 1 allowlist;
- directly or materially relevant to Linux;
- active within the previous 365 days;
- observed no more than seven days before the explicit policy as-of date;
- tied to an explicit issue or `help wanted` maintainer signal;
- a non-security task estimated at no more than six focused hours;
- independent of secrets, production access, or network probing;
- explicitly permitted by the upstream policy for this AI-operated contribution workflow;
- outside the frozen-repository and Season 1 sensitive-subsystem exclusions.

No license means no contribution. A public repository is not automatically open source. SPDX syntax alone is insufficient: custom `LicenseRef-*`, source-available, and other identifiers outside the deliberately narrow allowlist remain ineligible until a reviewed policy change. This is a project safety gate, not legal advice or a universal judgment about a license.

## Ranking

Eligible candidates gain points for:

- explicit maintainer request;
- direct Linux usefulness;
- reproducible evidence;
- existing automated tests;
- recent activity;
- small scope;
- a clear contribution guide.

They lose points for a required human attestation or a large open-PR backlog. Unknown AI policy is
not a ranking caution: it is ineligible because absence of a prohibition is not consent. A lower
score is not a value judgment about a project; it is a measure of Patch Cabinet fit.

The as-of date is required and cannot be in the future. A past as-of date is a historical/demo evaluation and can never produce a `ready` band, even when its numerical score is high.

## Manual review before code

Check and record:

- license file and SPDX identifier;
- `CONTRIBUTING`, code of conduct, `SECURITY`, CLA/DCO, and AI policy;
- whether the policy permits the actual workflow: an AI system chooses and prepares the change,
  discloses that assistance, and a human performs only required identity or attestation steps;
- issue ownership, recent comments, duplicate work, and open pull requests;
- exact commit, observation date, last-activity date, reproduction, test command, and estimated review surface;
- whether the change could expose or silently fix a vulnerability.

If a security concern emerges, stop public work and follow the private security process.

## Exclusions

- repositories listed in the ignored sponsor-local exclusion file
- repositories without an explicit license
- archived or clearly abandoned repositories
- speculative rewrites, style churn, dependency-update floods, and benchmark claims without reproducible evidence
- work whose primary purpose is marketing Patch Cabinet
- tasks requiring secrets, production access, customer data, or unauthorized network probing

Project runs pass the operator-owned ignored exclusion file explicitly. The CLI never trusts a candidate or target repository to provide this policy input. A missing file is an error unless the caller explicitly declares a public/synthetic run with no sponsor context.

## Meaning of `ai_policy`

`allows` means pinned upstream text explicitly permits the AI-operated workflow described above.
Permission for human-led AI assistance does not qualify when the same policy bars autonomous agents
from opening issues or pull requests. `disallows` means the pinned policy conflicts with this
workflow. `unknown` means no sufficiently explicit upstream rule was found; under policy
`season-1.3`, that candidate is ineligible until upstream publishes or directly supplies a clear
rule. Patch Cabinet does not solicit a policy statement merely to create work for itself.

Every status is reviewable evidence, not an unbound label. `ai_policy_source_url` must point to a
file in the candidate's GitHub repository at the exact recorded `commit_sha`.
`ai_policy_basis` must match the status: `explicitly_allows_agent_submission`,
`no_explicit_workflow_rule`, or `disallows_agent_submission`. The source URL, status, and basis are
included in generated evidence. The engine validates their binding and controlled vocabulary; a
human reviewer still owns the semantic judgment about what the pinned text actually says.

## Consent catalog boundary

The separate contribution-consent catalog may reduce repeated policy discovery, but it never
supplies candidate permission automatically. Each catalog record is one manual historical review
of one public file at one commit and becomes stale for live-candidate use after seven days. A
candidate manifest must still carry its own current policy status, controlled basis, and pinned
same-repository URL, and every manual gate above still applies. Catalog records are added by
successor rather than rewritten; disallowed and insufficient policies remain visible.
