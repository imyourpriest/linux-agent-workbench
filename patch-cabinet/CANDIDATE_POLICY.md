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
- compatible with any explicit AI-contribution rule;
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

They lose points for a required human attestation, an unknown AI policy, or a large open-PR backlog. A lower score is not a value judgment about a project; it is a measure of Patch Cabinet fit.

The as-of date is required and cannot be in the future. A past as-of date is a historical/demo evaluation and can never produce a `ready` band, even when its numerical score is high.

## Manual review before code

Check and record:

- license file and SPDX identifier;
- `CONTRIBUTING`, code of conduct, `SECURITY`, CLA/DCO, and AI policy;
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
