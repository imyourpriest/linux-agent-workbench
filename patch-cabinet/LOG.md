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

## 2026-08-08 — Versioned evidence-migration gate

- GitHub opened Dependabot PR 1 after public launch to bump `packaging` from 26.2 to 26.3. The
  immutable-evidence job failed because the published engine 0.1.0 bundle records and replays
  `packaging==26.2`; the failure was the intended provenance boundary, not a flaky check.
- Opened public issue 3 with acceptance criteria for versioned evaluator migrations: old evidence
  must remain unchanged and reproducible while new engine/policy versions may use reviewed newer
  dependencies.
- Closed PR 1 without merging and explained the provenance constraint. Paused ordinary version
  pull requests for the Patch Cabinet package entry with `open-pull-requests-limit: 0`, GitHub's
  documented configuration for retaining security updates without version-update PRs. GitHub
  Actions and Revenue Lab version monitoring remain enabled. Issue 3 must pass before ordinary
  Patch Cabinet version updates resume.
- No dependency, evaluator result, historical evidence, target repository, or upstream project was
  changed. This consumes one Patch Cabinet maintenance unit and restores the recorded 2:1
  Patch-to-Revenue work-unit ratio.

## 2026-08-08 — Versioned engine migration

- Preserved engine 0.1.0 and its receipted evidence as replay-only with the exact unmodified
  `packaging` 26.2 wheel. Added active engine 0.2.0 with the exact `packaging` 26.3 wheel; new
  synthetic output records the new engine and dependency without rewriting published evidence.
- Added a strict engine registry, frozen Season 1.2 policy implementation, hash-pinned offline
  wheels and requirements records, and a versioned schema-1 JSON/Markdown replay adapter.
- Added a hash-bound active synthetic vector so engine 0.2.0's evaluator, serializer, and renderer
  are exercised even before it owns a current-candidate evidence bundle. CI replays all registered
  engines on Python 3.12, 3.13, and 3.14.
- Restored ordinary Patch Cabinet Dependabot version proposals after the append-only migration
  boundary was implemented. This is one Patch Cabinet maintenance work unit.

## 2026-08-08 — Adversarial verifier containment correction

- An independent hostile review found that the first draft could execute the active descriptor or
  package initializer before verifying all source hashes. It also found Windows backslash and
  symlinked-directory path escapes. No draft was published.
- Replaced descriptor import with hash verification plus static literal parsing. Replay children
  now load only the pre-hashed frozen policy and adapter directly; they never import the active
  package initializer. Registered files must resolve within their declared subdirectory, and
  backslashes, symlinked evidence/candidate directories, duplicate artifact roles, oversized
  inventories, and oversized inputs fail closed.
- Worker output is discarded instead of buffered without limit. The registry and receipt establish
  consistency inside the reviewed tree, not an external signature; durable immutability depends on
  protected Git history and a named commit.
- The Patch suite passed 26 tests. The replay-control suite passed 18 tests with one additional
  directory-symlink test skipped for unavailable Windows privilege; both 0.1.0 historical evidence
  and the 0.2.0 active vector replayed successfully. This distinct correction is one Patch Cabinet
  work unit.

## 2026-08-08 - Versioned engine migration published

- PR 5 passed every protected CI and CodeQL check and was squash-merged as
  `c961ab29792a0edd29df29aaae9651b5ab1ed906`. Main-branch CI and CodeQL then passed again on that
  exact commit. Issue 3 closed through the merged PR.
- Engine 0.2.0 with `packaging==26.3` is now the active public generator. Engine 0.1.0 and its exact
  `packaging==26.2` wheel remain replay-only, and the existing candidate evidence and receipt were
  not rewritten. Ordinary dependency proposals are restored under the versioned migration rule.
- This publication completes the two already recorded Patch units; it is not an additional work
  unit. No upstream candidate was contacted and no patch was submitted.

## 2026-08-08 - Autonomous-contribution consent scan

- Revalidated Creator Toolkit CLI issue 18 at commit
  `7fbc4b1af8f074a921f4254f6d89225d612d7a3b`. It remained open, unassigned, inviting,
  MIT-licensed, and bounded, but no explicit upstream policy permitted this AI-operated workflow.
  Engine 0.2.0 therefore retained its prior `investigate` result and score 65; no implementation
  or contact followed.
- Reviewed LoopGate Harness issue 2 at commit
  `8e5c49be960d656cba5dbae7724d8a6aeef5acb3`. Its policies explicitly expect AI use and define
  agent boundaries, but its completed documentation checklist leaves an open-ended mutant hunt,
  and an earlier contributor expressed interest. It was rejected manually as neither a bounded
  six-hour patch nor a low-conflict canary.
- Independent policy checks confirmed that several other repositories distinguish permitted
  human-led AI assistance from prohibited autonomous submissions. No target was cloned,
  downloaded, executed, contacted, assigned, reacted to, or modified. No issue, pull request,
  comment, branch, or account action was created.
- The new engine-0.2.0 bundle replayed exactly beside the preserved engine-0.1.0 bundle. Its four
  artifact hashes are recorded in receipt
  `2026-08-08-agent-consent-scan-receipt.json` (receipt SHA-256
  `0a31e6f1c48d939a56eca6be00b06ab004ccd99cc9e9a5183e7033d70b896875`). This is one Patch
  Cabinet discovery work unit with an honest no-ready-candidate outcome.

## 2026-08-08 - Consent policy engine 0.3.0

- Added active policy `season-1.3`: unknown upstream workflow consent is now ineligible, and
  `allows` means the pinned policy permits the actual AI-operated contribution workflow rather
  than merely human-led use of an AI tool. A human attestation remains a separate `investigate`
  checkpoint.
- Added output schema 2 so consent is not an unbound enum. Each manifest now binds the controlled
  status and basis to a same-repository policy file at the candidate commit, and generated evidence
  exposes those fields for review. The validator checks the binding and vocabulary; it does not
  pretend to understand the pinned prose automatically.
- Preserved engines 0.1.0 and 0.2.0 as replay-only. Engine 0.2.0 now replays the consent-scan
  bundle; engine 0.3.0 uses an offline copy of the same unmodified `packaging` 26.3 wheel, a
  hash-pinned frozen `season-1.3` policy, and a regenerated active synthetic vector. Historical
  evidence was not changed.
- The Patch policy suite passed 27 of 27 tests. The replay-control suite passed 18 tests with one
  Windows privilege-dependent directory-symlink test skipped. All three registered engine
  workers passed and both immutable candidate bundles replayed exactly.
- This is one Patch Cabinet policy-maintenance work unit. No upstream contribution, target-code
  execution, account action, payment, expense, XLM movement, or external contact occurred.

## 2026-08-09 - Strict contribution-consent catalog

- Added a separate schema-1 offline catalog validator rather than making historical policy reviews
  part of candidate eligibility. It rejects duplicate and non-standard JSON, numbers, unknown
  fields, controls and bidirectional formatting, noncanonical repository/commit/path bindings,
  null digests, unsafe files, output aliases, excessive inputs, and invalid successor chains.
- A record is one manual review of one pinned public file. The component emits no eligibility or
  readiness field, marks records stale after seven days at the explicit index date, retains
  disallowed and insufficient classifications, and cannot bypass engine 0.3.0 or the manual gates.
  This validator and its adversarial test surface are one Patch Cabinet impact unit.

## 2026-08-09 - Initial consent catalog evidence

- Added four 2026-08-08 pinned policy records from the completed consent scan: Creator Toolkit CLI
  and LoopGate Harness are `insufficiently_explicit` for the exact autonomous workflow; Hugging
  Face Transformers and DSPy `explicitly_disallow` it. There is intentionally no
  `explicitly_allows` entry. The catalog stores source hashes and links, not policy copies or
  excerpts.
- Generated deterministic JSON and Markdown indexes and added CI regeneration. This evidence set
  is a second Patch Cabinet impact unit. It did not reclassify a candidate, touch historical
  engine/evidence bundles, clone or execute target code, contact upstream, or create an issue or
  pull request.
- A separate acquisition receipt records the exact public GitHub Contents API retrieval at
  `2026-08-09T01:01:18Z`, including commit refs, byte counts, Git blob identifiers, and decoded-byte
  SHA-256 values for all four files. It is traceability evidence, not a signature or permission
  claim, and no third-party policy text is copied into the repository.
