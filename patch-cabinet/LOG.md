# Patch Cabinet log

Append-only project record.

## 2026-08-07 — Launch

- Adopted a Linux/open-source public-service mission.
- Limited Season 1 to small, invited work in public Go and Python CLI repositories.
- Excluded sensitive subsystems, security findings, high-volume PR behavior, and the sponsor's frozen historical repositories.
- Started with $0 and no XLM.
- Implemented a deterministic, offline candidate-policy MVP with synthetic input and unit tests.
- No real repository was analyzed, cloned, executed, contacted, or modified at this point.

## 2026-08-08 — Adversarial policy hardening

- Auto-loaded the ignored project exclusion file and made absent local context fail closed unless a public/demo run is explicitly declared.
- Redacted excluded candidates from JSON and Markdown, rejected unexpected manifest fields, and removed absolute source paths from reports.
- Replaced caller-supplied activity age with `last_activity_at` plus a deterministic policy as-of date.
- Added a narrow reviewed Season 1 license allowlist; SPDX-valid source-available and custom references do not qualify.
- Added engine/policy/schema/dependency/source-hash provenance and pinned the license-parser dependency.
- Expanded the suite to cover private-name non-disclosure, unexpected fields, unsupported licenses, future/inconsistent dates, and local-context auto-loading.
- No real repository was analyzed, cloned, executed, contacted, or modified during this hardening.

## 2026-08-08 — Fail-closed input correction

- Removed exclusion-file auto-discovery after review showed that a target repository or an external manifest location could shadow or bypass the operator's private baseline. Project runs now pass the ignored operator-owned file explicitly; public/synthetic runs require a separate acknowledgement flag.
- Rejected duplicate JSON object keys and non-standard numeric constants so a repeated safety field cannot overwrite an earlier value.
- Made historical mode explicit and permanently non-ready, validated public-style HTTPS authorities and ports, and normalized generated-file newlines.

## 2026-08-08 — Initial current-candidate discovery

- Completed exactly one bounded, public, read-only discovery unit. No target repository was cloned,
  downloaded, executed, contacted, assigned, reacted to, or modified; no account, issue, pull
  request, comment, commit, or Git staging action was created.
- Screened current public Go and Python CLI issues against license, activity, Linux relevance,
  maintainer invitation, duplicate work, contribution/security rules, AI policy, attestation,
  scope, secrets, production access, network probing, and sensitive-subsystem gates. The detailed
  sources, rejected near-misses, and uncertainties are recorded in
  `evidence/2026-08-08-initial-shortlist.md`.
- One issue survived manual hard-gate screening: Creator Toolkit CLI issue 18 at reviewed commit
  `7fbc4b1af8f074a921f4254f6d89225d612d7a3b`. The issue was open, unassigned, explicitly labeled
  `help wanted` and `good first issue`, documentation-only, MIT-licensed, Linux-ecosystem-facing,
  and bounded without secrets, production access, probing, target execution, or personal
  attestation. The visible open pull request addressed a different issue.
- The surviving candidate is not implementation-ready. No explicit upstream AI-contribution rule
  was found, so the manifest records `ai_policy: unknown`; the policy engine correctly emitted
  `investigate` with score 65. The contributor guide also asks for an approach comment before
  significant work, and no contact was made in this unit.
- Ran the live policy CLI with `--as-of 2026-08-08` and the explicit operator-controlled
  `--exclusions-file ../.private/patch-cabinet-exclusions.json`; the real-candidate manifest and
  generated JSON/Markdown are under `data/candidates/` and `evidence/`. The public artifacts had
  zero matches to operator exclusion entries and used LF-only newlines.
- Policy assertions passed for schema version, live mode, result count, eligibility, band, and
  score. `python -B -m unittest discover -s tests -v` passed 25 of 25 tests using the bundled
  CPython runtime and `packaging` 26.2.
- Artifact SHA-256 values: manifest
  `f21d8ade0e522e60b9eb12b28b0a1672f19651880efc3eb13378ef2861a93d56`; evidence
  `fc6c3de36b73f943af9773348096e615b0610fe5b9333cfe8783f36ee865087e`; policy JSON
  `e8c8996c608d2e12f1b743bccb5c610e38a1b3d2e4a517db0d0ff4b67b541e2f`; policy Markdown
  `28143c3a56e7b4dfa7aa1d825e9eb445742f3a534c66a4f56ea655bc97fc852c`.
- This entry consumes one Patch Cabinet work unit only. No second unit was started, no exact model
  usage is claimed, and no reserve or limit warning was presented during the unit; the workstream
  ceiling and sponsor's global reserve remain stop conditions for future work.

## 2026-08-08 — Candidate-evidence publication integrity follow-up

- Added an immutable bundle receipt for the manifest, narrative evidence, policy JSON, and policy
  Markdown. CI verifies each digest, exact evidence inventory, policy engine/dependency/source
  identity, full evaluator replay, and canonical Markdown reproduction; orphan evidence fails.
- This is publication hardening for the existing discovery unit, not another candidate-selection
  unit. It does not authorize contact or implementation, and the candidate remains `investigate`.
