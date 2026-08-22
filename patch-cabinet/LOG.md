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

## 2026-08-10 - Current autonomous-workflow scan

- Reviewed LoopGate Harness issue 2 and Ruff issue 27602 from public read-only evidence captured
  between `2026-08-11T00:12:49Z` and `2026-08-11T00:13:11Z` UTC, with local policy as-of date
  `2026-08-10`. The explicit operator-controlled exclusion file was applied without publishing its
  entries.
- LoopGate was ineligible because its eight-hour estimate exceeded the Season 1 scope and its
  pinned contributor guide did not explicitly authorize this autonomous workflow. Ruff was
  ineligible because its pinned contributor guide requires substantive human review and editorial
  judgment that conflict with the project's human-only identity and attestation checkpoint.
- The active engine 0.3.0 bundle records no ready candidate and no investigate claim. No target
  code or policy was acquired for execution, and no upstream contact, issue, comment, reaction,
  assignment, branch, pull request, or submission occurred. This is one Patch Cabinet impact unit.

## 2026-08-10 - Manual policy-profile experiment

- Added a separate strict offline profile catalog that binds eight manually normalized policy
  dimensions to exact immutable consent records. It rejects unsafe JSON and files, provenance
  mismatches, aliases, duplicate bindings, and invalid or cross-lineage successor chains.
- Added profiles for all five consent records and deterministic JSON/Markdown generation. The
  profiles are historical manual facts only: they do not interpret prose automatically, alter the
  active engine, establish current permission or candidate eligibility, or authorize contact or
  submission. This is one Patch Cabinet impact unit.

## 2026-08-10 - Post-review provenance and catalog correction

- Corrected the Ruff review to the evidence actually pinned in this repository. The exact
  `CONTRIBUTING.md` delegates substantive AI-use rules to a different repository at a mutable
  branch URL; that external policy has no commit pin or source receipt here. Ruff is therefore
  `unknown` and `insufficiently_explicit`, all eight Ruff profile dimensions are `not_explicit`,
  and the active engine still rejects it. No cross-repository policy claim or permission was
  imported.
- Required profile successor values to exactly match their consent records, including `null`;
  rejected catalog junction/reparse directory boundaries; and added strict bounded validation for
  both acquisition-receipt shapes and their exact record/API provenance.
- Catalog output parents are explicitly trusted-local scope. Atomic replacement avoids partial
  output but is not claimed to enforce against adversarial parent replacement. This correction is
  review remediation for the two recorded impact units, not an additional work unit.

## 2026-08-10 - Maintainer policy declaration prototype

- Added standalone schema-1/component-0.1.0 trusted-local declaration cards with strict JSON,
  canonical same-repository commit-pinned fields, controlled dimensions, disclosure consistency,
  immutable successor chains, link/junction/reparse rejection, deterministic LF output, inert
  notes, and an explicitly invalid starter template.
- The component is isolated from the candidate engine and policy CLI. It never fetches or parses
  policy prose, detects AI use, proves repository ownership/authorship/source truth/current
  permission, scores work, authorizes contact, or serves as a CI merge gate. The checked-in record
  is unmistakably synthetic and non-real. This implementation is one Patch Cabinet impact unit.

## 2026-08-10 - Maintainer declaration public-context research

- Recorded a 30-day local/public prototype gate informed by current public AGENTS.md, GitHub
  Community, LLVM, Home Assistant, The Carpentries, and OpenSSF materials linked in
  `MAINTAINER_POLICY_DECLARATION.md`. This is a research prototype, not a standard or endorsement.
- Distinguished declaration cards from `AGENTS.md`: one records explicitly supplied contribution
  practices; the other gives repository-local operating instructions to agents. Success and stop
  thresholds require maintainer usability, structural/provenance error capture, faithful rendering,
  reuse/time benefit, and no permission confusion. This research is one Patch Cabinet impact unit.
- No maintainer was contacted, no repository declaration was solicited, and no issue, pull request,
  release, account, listing, payment, or other external action occurred in these two units.

## 2026-08-10 - Declaration prototype P3 remediation

- Independent review reported no P0-P2 issue in scope and held publication for five P3
  corrections. D-034 corrects the earlier ambiguous wording: accepted project records are
  maintainer- or operator-supplied and unauthenticated/unverified. Structural validation does not
  establish supplier identity, maintainer authority, source truth, current permission, or
  authorization.
- Reserved synthetic provenance to `example.invalid`, rendered it without a live link, replaced
  punctuation-folded identifiers with full canonical-identity SHA-256 identifiers, preserved
  record kind and assertion basis across successor chains, and added an explicit kind-specific
  starter plus a complete schema/vocabulary reference. Synthetic records make no existence or
  identity assertion.
- Remediation and tests were local only. No contact, publication, account, issue, pull request,
  payment, or other external action occurred. This correction is not an additional work unit.

## 2026-08-12 - Fail-closed policy-gated scan and portable declaration receipt

- Recorded a fresh no-ready scan in `evidence/2026-08-12-no-ready-policy-gate.md`. The strongest
  new public near-miss, `jazzband/pip-tools` at exact commit
  `e7f9099f5a87e5c08fbdd9b6e6d7b8f2132cb8d4`, explicitly does not permit autonomous pull-request
  submission without human review. The operator exclusion baseline was applied without exposing
  its entries. The scan stopped at policy, before issue/competition checks or candidate scoring.
- Advanced only the isolated maintainer-declaration component to 0.2.0 and added an installed
  one-record `validate` command. Its deterministic receipt reuses the safe-open payload for strict
  validation and raw-file SHA-256, labels that digest only as a recomputable fingerprint, and
  establishes no identity, authority, authorization, currentness, source truth, or permission.
- These are two Patch Cabinet impact units. No candidate-engine/package version, active policy,
  versioned verifier, existing evidence bundle, target code, upstream contact, or external state
  changed.

## 2026-08-12 - R-006 declaration and evidence-control correction

- Corrected the declaration reference's normative component version from 0.1.0 to 0.2.0 and added
  a test that ties the documented value to the runtime constant.
- Corrected evidence-directory preflight capacity to reserve exactly one slot for the exact
  name-and-digest narrative allowlist. Tests now cover the allowed narrative, same-name content
  tampering, a near-name orphan, a candidate
  bundle attempting to share its stem, and deterministic maximum-cap arithmetic. The three
  immutable bundle inventories and replay requirements remain exact and unchanged.
- This is review remediation of the two already counted Patch units, not another work unit. No
  candidate, upstream contact, publication, or external action occurred.

## 2026-08-13 - R-004 portable declaration candidate and neutral catalog expansion

- Built one deterministic, self-contained, unpublished release candidate for component
  0.2.0/schema 1. The fixed-metadata stored ZIP contains only the standalone validator, README,
  specification, MIT license, unverified-project starter, and reserved synthetic example. Its
  manifest does not self-hash; the external receipt/checksum bind exact archive bytes. SHA-256 is
  a recomputable fingerprint, not a signature, attestation, or external trust.
- Added exactly five paired consent/profile records from exact commit-pinned files observed
  2026-08-13. Bitcoin and OpenTTD explicitly disallow the exact autonomous workflow; NewPipe,
  llama.cpp (CONTRIBUTING.md only), and n8n remain insufficiently explicit. Missing dimensions
  are `not_explicit`. One receipt binds returned bytes, decoded-byte SHA-256s, and Contents blob
  SHA-1s; no third-party source text is stored or executed.
- These are exactly two impact units. No candidate manifest, ranking, eligibility, contact, or
  submission authority changed. No GitHub release, adoption, contact, issue, pull request, or
  external action occurred.

## 2026-08-13 - R-004 declaration archive-staging correction

- Final assurance review found that the portable release builder used a predictable `.build` path
  that ZIP creation could truncate or follow. It now creates an exclusive random staging file in
  the checked trusted-local output directory, builds and reads through the opened descriptor,
  verifies regular-file identity and single-link state, removes only that exact temporary name,
  and atomically replaces final outputs. A pre-existing old predictable regular file or hard link
  remains untouched; symlink variants are covered where platform privilege permits.
- Output directories are explicitly checked as non-link, non-junction, non-reparse regular
  directories. This rejects the observed staging issue but does not claim protection if an
  adversary can replace a trusted-local parent after inspection.
- The focused suite passed 9 tests with two Windows symlink-privilege skips. The regenerated ZIP
  remained byte-identical. This is remediation of the existing impact unit, not a new unit,
  publication, adoption, external action, Usage reading, or production-enforcement claim.

## 2026-08-13 - Declaration interoperability and neutral catalog snapshot

- Added one versioned JSON Schema Draft 2020-12 structural profile, fixed valid/invalid/ambiguous
  corpus, deterministic manifest/receipt, and lossy non-authorizing AI-policy/PR-template draft
  projections for declaration schema 1. The existing strict Python parser remains authoritative.
  No independent JSON Schema validator was installed or tested, and no standard, detector,
  authority, permission, currentness, authorization, ruleset, or enforcement claim is made.
- Added one deterministic historical snapshot/query over the existing ten profile records. It
  filters exact controlled dimensions and labels each match fresh, stale, or unknown at an
  operator-provided canonical date using the documented seven-day window. It does not rank,
  aggregate trust, refresh the network, establish readiness/current permission, add records, or
  connect to the candidate engine.
- These are exactly two Patch impact units. No target code, candidate manifest, immutable evidence,
  frozen engine/verifier, upstream contact, issue, pull request, submission, publication, or other
  external state changed.

## 2026-08-13 - R-004 interoperability security-review remediation

- The reviewed pre-remediation state was 36 content paths at canonical NUL-safe digest
  `3277f724dfe684a4cbd7bed961f46967cb3acaec9f2ec3eddbf83c08b21823f5`, on
  `agent/r008-policy-interop-audit` with HEAD and `origin/main` both
  `6b9c0a506f325210482f3942cdc7f2be3331ce4d`. Diff check was clean.
- Security review found one P2 in the corpus projection boundary: an accepted declaration could be
  relabeled invalid or ambiguous and still supply generated text. The corpus now admits only four
  explicit classification/structural/strict/observed tuples, and only the exact all-accept `valid`
  tuple may become the sole projection source. Regression tests cover both relabelings and a
  mismatched tuple.
- Hardening replaced recursive node counting with an iterative early-fail node/depth walker and a
  byte-bounded deep probe. `not_declared` disclosure, review, and accountability values no longer
  become invented PR checkboxes; possible requirements are labeled independent maintainer
  proposals. Directory chains below the explicitly trusted project boundary and output leaves are
  rechecked around replacement. This reduces alias/reparse risk but is not race-proof against an
  adversary that can concurrently replace the trusted project parent or its components.
- This is remediation only: no work-unit, Usage, authorization, adoption, publication, or external
  action changed. Cumulative totals remain 24 impact / 12 Support and revenue remains `$0.00`.
- Focused interoperability tests passed 12/12. The stable full Patch suite passed 109 tests with
  five Windows privilege-dependent symlink skips. Complete generation/freshness, compilation,
  dependency, public-tree, frozen-inventory, and diff checks are recorded in the control log.

## 2026-08-19 - R-005 structural compatibility and exact projection contract

- Prepared two genuinely separate hosted-only structural adapters for the frozen declaration
  schema: Python `jsonschema==4.26.0` and Node Ajv `8.20.0`. The new workflow uses separate jobs,
  pinned actions, read-only contents permissions, exact validator configurations, hash-locked
  Python 3.13/Linux-x64 distributions, a private exact Node package lock, no lifecycle scripts,
  and no remote validator loader. Dependency acquisition is honestly network-enabled.
- Bound the frozen schema/base corpus, a supplemental corpus covering required/additional fields,
  enum/type/pattern/null-string/ignored-format/boundary cases, both runner sources, dependency
  locks, validator configurations, every vector ID, raw-payload digest, parse/schema expectation,
  and denominator status. Duplicate-key and NaN vectors remain decoder-boundary observations and
  are excluded from the structural-agreement denominator.
- Added a machine-readable projection contract covering every authoritative top-level declaration
  field and all thirteen nested dimensions exactly once by JSON Pointer. It derives values only
  from the one accepted synthetic declaration and verifier-owned mapping, binds source/mapping/
  output digests, fails on missing/duplicate/unknown mappings or stale output, and never converts
  `not_declared` into a contributor obligation or checklist.
- These are exactly two Patch impact units. The third-party validators were not installed,
  imported, or executed locally; hosted observations remain `not_observed`. Any later hosted
  success would establish only the named configured structural outcome on its named commit/run,
  not attestation, authentication, semantics, provenance, freshness, privacy, isolation,
  standard adoption, source truth, permission, or production enforcement.

## 2026-08-20 - R-005 hosted compatibility remediation cycle 1

- The reviewed branch `agent/r009-policy-compatibility` was published at
  `0ac9cd67dd8e9a91126ff1e407b054465659f4e1`, and draft PR 17 was created. The GitHub connector
  first returned 403 `Resource not accessible by integration`; an authenticated read-only CLI
  check verified zero existing head pull requests before the single authorized CLI fallback
  created the draft.
- On exact head `0ac9cd67dd8e9a91126ff1e407b054465659f4e1`, workflow run `32336332382` failed in Python job
  `96326529034` and Node job `96326528729`. Both failures occurred in the closed-harness preflight,
  after checkout and setup-python but before the exact locked validator-dependency installation
  steps (`pip install --require-hashes` and `npm ci`) and before either structural-adapter step ran.
  No hosted structural validator result or success is claimed; no claim is made that the runner
  platform itself performed no network acquisition.
- The package-style `python -B -m patch_cabinet.declaration_compatibility` invocation imported
  `patch_cabinet.__init__` and `policy.py`, which required the not-yet-acquired `packaging`
  dependency. The minimal remediation invokes the same project-owned standard-library checker by
  its root-relative script path in both jobs, removes workflow `PYTHONPATH`, and adds regression
  assertions for the exact two commands, pinned Python setup, and pre-acquisition ordering.
- This is the first of at most two authorized hosted-failure remediation cycles. It adds no work
  unit, hosted success, activation, adoption, customer, revenue, or production-enforcement claim;
  revenue remains `$0.00`, and the third-party validator observations remain `not_observed` until
  an exact hosted head/run succeeds.

## 2026-08-20 - R-005 hosted compatibility remediation cycle 2

- On exact head `be9e882d46e79dbaa44fadfc7a2c501fa650fa7f`, hosted compatibility run
  `32337297322` completed the preflight and exact locked installs. Python job `96329209177` and
  Node job `96329208990` both executed their structural adapters, and both reported the same
  mismatch: vector `policy-path-pattern-reject` structurally accepted where the prepared contract
  incorrectly expected rejection. This was an expected-outcome defect, not validator divergence,
  and no hosted structural success is claimed.
- The frozen v1 pattern accepts dot-only path segments. The authoritative declaration parser has
  a separate semantic guard that rejects `.` and `..`. Draft 2020-12 pattern behavior and review
  of pinned python-jsonschema 4.26.0 `_keywords.py` and Ajv 8.20.0 JSON Schema documentation support
  recording schema acceptance: https://json-schema.org/draft/2020-12/json-schema-validation#section-6.3.3.
- The one vector is renamed `policy-path-dot-segment-structural-accept` and made cross-field
  consistent with its source URL and NUL-derived declaration ID. Its contract is now strict JSON
  parse `accept`, schema `accept`, and included in the agreement denominator. This records a
  structural-profile gap only; it is not authoritative-parser, path-safety, or semantic acceptance.
- Ordinary CI run `32337297321` and CodeQL run `32337294075` passed all their checks on exact head
  `be9e882d46e79dbaa44fadfc7a2c501fa650fa7f`. This is the second and final authorized remediation
  cycle. Any next failure stops this path pending a new prospective decision. No unit, activation,
  adoption, customer, or revenue claim is added; revenue remains `$0.00`.
- Final review found that the cross-field regression assertions compared only fixed literals. They
  now independently derive the source URL and NUL-joined declaration ID and invoke the
  authoritative parser to require its canonical `..` path rejection. Artifact semantics,
  expected structural results, work units, activation, and revenue are unchanged.

## 2026-08-20 - R-010 additive fast-uri security migration prepared locally

- Added a separate compatibility-v2 closed harness rather than changing the published v1 record.
  All 11 compatibility-v1 files retain their exact recorded byte lengths and SHA-256 values.
- V2 keeps Ajv `8.20.0` and the unchanged Python adapter lock, schema, corpus, expected outcomes,
  and structural semantics. Its Node lock and runner require `fast-uri@3.1.5`. Official GitHub
  Advisory Database records reviewed on 2026-08-20 support the selection:
  https://github.com/advisories/GHSA-q3j6-qgpj-74h6,
  https://github.com/advisories/GHSA-v39h-62p7-jpjc,
  https://github.com/advisories/GHSA-4c8g-83qw-93j6,
  https://github.com/advisories/GHSA-v2hh-gcrm-f6hx, and
  https://github.com/advisories/GHSA-7p8r-x3mc-p8w7. A separate verifier-owned record binds only
  selected fields transcribed from official npm registry metadata: its source/date, exact tarball
  URL, SHA-512 integrity, registry shasum, BSD-3-Clause license, and absence of an observed install
  script/engines field. It is not a raw response archive or runtime proof. The generator validates
  that evidence, the exact whole v1-derived package lock, and exact v1-derived runner
  transformations before producing a manifest. The Node runner verifies the complete five-package
  installed inventory before dynamically importing Ajv.
- The protected workflow retains its exact job IDs/names, broad pull-request and main-push
  triggers, read-only permissions, pinned actions, timeouts, pre-install freshness/integrity
  ordering, and no-lifecycle-script acquisition flags while routing both adapters to v2. Ordinary
  generated-evidence CI retains the direct v1 freshness check and adds an independent v2 check.
- Double generation was byte-identical, and the prepared v2 receipt remains `not_observed` with
  manifest SHA-256 `013a9704723cf8cdbde62007df74e5717477006fa87a7ff2ba1cdffd1a8a1d66`.
  Focused tests passed 14/14; the full Patch suite passed 127 tests with five Windows privilege
  skips; evidence-control passed 22 tests with one Windows privilege skip. Engine/bundle replay,
  public-tree review, in-memory compilation, dependency consistency, freshness, closed-inventory,
  and diff checks passed. The historical frozen selector reproduced its exact 99 rows and
  `756910a774d9988a4f4e7bd0444b2ff84f83e7cdf2a92e605e5b4fd4b9df055f` fingerprint with zero
  worktree difference.
- No third-party validator or tarball was downloaded, installed, imported, or executed locally;
  npm was not run and no `node_modules` exists. These local static and synthetic checks do not
  establish exploitation resistance, isolation, hosted behavior, future availability, or
  production security/enforcement. This correction adds no work unit, activation, customer,
  payment, or revenue; totals remain 26 impact / 13 revenue and `$0.00`.

## 2026-08-22 - R-011 fail-closed scan and historical policy records

- A fresh bounded public-read-only scan considered four public candidates and found no ready
  candidate. Zero matched the private operator-exclusion list; its entries remain undisclosed.
  Rclone had policy evidence but no qualifying small issue; GSD-2 explicitly allowed an AI
  pull-request workflow but had no qualifying small issue; creator-toolkit-cli retained issue 18
  without explicit policy for the planned workflow; and OpenEverest had policy evidence without a
  qualifying small issue. Rclone near-misses were assigned, had competing work, or were sensitive.
  No acquisition, clone, third-party execution, contact, selection, or upstream mutation occurred.
- Added two immutable historical consent/profile pairs from exact public `CONTRIBUTING.md` bytes:
  rclone/rclone at `64ab1ac32260238eefca3c61327f5faf1c6e106f` is
  `insufficiently_explicit`; gsd-build/gsd-2 at
  `33c00aaffa56e5d394bccce1c8df59fb842e84c5` is `explicitly_allows`. A separate two-source
  receipt binds the API URLs, Git blob SHA-1 values, byte counts, SHA-256 values, and retrieval
  time. The records are historical policy evidence only, never candidate eligibility, contact
  authority, or submission authority.
- The current consent index is regenerated as of `2026-08-22`: 12 records, 2 current, 10 stale,
  1 explicitly allows, 4 explicitly disallow, and 7 are insufficiently explicit. The manual
  profile index contains 12 records. The intentionally historical `2026-08-13` snapshot remains
  on that date and reports 10 fresh, 0 stale, and 2 unknown later records.
- The catalog now evaluates future-date rejection against UTC rather than the operator host's
  local date, preventing a valid next-UTC-day observation from being rejected while preserving
  all other date and freshness semantics. Deterministic tests bind the UTC clock use and boundary.
- Local Patch tests passed 129 tests with five Windows privilege-dependent link skips. Evidence-
  control tests passed 22 tests with one such skip; all three registered engines replayed, the
  evidence inventory and public-tree heuristic passed, generated catalog outputs were byte-stable
  on regeneration, two modified Python modules compiled in memory, and `git diff --check` passed.
  One earlier mixed test command inherited `PYTHONPATH=patch-cabinet/src`, causing one evidence-
  engine isolation assertion to fail because a dependency loaded outside its wheel; rerunning the
  evidence tests without that contaminating environment passed 22/22 except the privilege skip.
- These are exactly two Patch impact units. Static/local tests establish bounded structural and
  deterministic behavior only, not source authenticity, semantic permission, production
  enforcement, or future candidate readiness.

## 2026-08-22 - R-011 independent-review correction

- D-046 was the first project edit and was expanded before the UTC production-code change, but its
  initial exact text/fingerprint was not retained; static review cannot audit that chronology.
  D-047 prospectively binds the independently reviewed 24-path baseline and is the publication
  basis.
- The prior broad `no acquisition` wording is superseded only as follows: public policy-source
  bytes for the historical consent catalog were acquired through the GitHub Contents API and bound
  by the separate receipt. No candidate repository was cloned or acquired for candidate work, no
  candidate or third-party code was executed, and no upstream contact or mutation occurred.
- The no-ready narrative now links the exact examined rclone issues and competing pull requests
  and bounded GSD-2/OpenEverest issue-list near-misses. It establishes only that this bounded scan
  advanced no examined issue to scoring and identified no ready candidate, not that no qualifying
  issue exists or that the search was exhaustive. Its exact SHA-256 is
  `3aeac82004020a707b6dae1e09a9002fd8e3de3d8232dba8bf819eee5b600cea`.
- Standalone evidence checking now fails if either allowlisted narrative is absent, not only when
  a present narrative has the wrong digest. Direct UTC index tests cover today acceptance and
  tomorrow rejection. Focused consent tests passed 19 with one privilege skip; evidence-control
  passed 23 with one skip and all three engines/bundles replayed; the full Patch suite passed 130
  with five skips. Deterministic catalog regeneration, public-tree review, compilation, diff,
  no-tag, and frozen-tree checks passed. These are local structural results only.
- This is remediation of the already counted two Patch units, not another unit, candidate,
  permission, activation, contact, submission, or external action. Totals remain 28 Patch impact /
  14 Support revenue units and `$0.00`.
