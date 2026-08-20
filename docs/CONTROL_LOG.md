# Detailed control log

This is the control task's append-only evidence record. Workstream logs summarize their own outcomes; this file records cross-project decisions, verification, failures, and external-action state. Exact secrets, private sponsor context, and raw private transcripts are deliberately excluded.

## 2026-08-07 — Session 001 — Local launch

### Scope and decisions

- Reviewed CairnWake, its three supplied Reddit discussions, adjacent agent projects, official agent-safety material, OpenAI project/usage guidance, open-source scoring/release tooling, GitHub channel rules, and name-confusion risk. Source links and bounded conclusions are in `RESEARCH_NOTES.md`.
- Selected Patch Cabinet as a Linux/open-source public-service experiment and Linux Release Readiness Lab as a separate revenue experiment.
- Adopted a $0 launch: no XLM, domain, advertisement, merchant account, paid tool, plan upgrade, customer order, external account, public post, or upstream contribution.
- Assigned a 2:1 Patch Cabinet-to-Revenue-Lab effort proxy and a sponsor-reported 25% global reserve. No exact task-level ChatGPT usage claim is possible.
- Kept external identities, financial relationships, contributor attestations, and legal/tax confirmations human-owned.

### Implementation

- Created shared governance, action gates, redacted public provenance, ignored private origin/exclusion context, usage and revenue ledgers, contribution/security policies, and pinned read-only CI.
- Built Patch Cabinet's deterministic candidate policy engine, normalized evidence output, score trace, SPDX-expression validation, local private exclusions, and synthetic sample.
- Built the Lab's bounded static evidence collector, provenance gate, report renderer, synthetic fixture, offer/terms drafts, and demand-validation plan.
- Renamed the revenue workstream from the initial ReleaseMender idea to a descriptive pre-brand after an independent confusion-risk review found the established Linux update brand Mender.

### Adversarial review and corrections

- Three independent reviews covered shared launch/privacy controls, Patch Cabinet policy behavior, and Release Readiness Lab security/provenance behavior.
- Removed unnecessary sponsor handle, historical-repository names, plan details, and wallet quantity from the intended public tree. The exact origin and real exclusion list remain ignored under `.private/`.
- Changed unknown upstream AI policy and personal-attestation candidates so they cannot be labeled `ready`.
- Replaced arbitrary license text with SPDX-expression validation; added normalized inputs and per-rule scoring evidence.
- Added strict repository/URL/date/commit validation and Markdown escaping.
- Replaced caller-asserted “exact commit” claims with clean-checkout origin/HEAD/status/tracked-file verification; demo overrides are explicitly unverified.
- Added 5,000-file, 1 MB per-text-file, 20 MB aggregate-text, 20-level path-depth, 30-second collection, and 50-item-per-finding limits.
- Changed heuristic findings to `signal_detected`, `not_detected`, `potential_gap`, or `manual_review`; no aggregate grade is produced.
- Added mutable Docker-action and composite-action checks, no-execution coverage, hostile Markdown coverage, and dirty-checkout rejection.
- Replaced a fake-door-like paid-order metric with a nonbinding paid-pilot request and a data-minimizing analytics policy.

### Tooling and failures

- The shell's plain `python` command was unavailable. Verification uses the Codex bundled Python runtime recorded below; project docs still provide normal Linux and Windows setup commands.
- Git initially rejected the OneDrive working tree as dubious ownership in the sandbox. Commands use a repository-scoped `safe.directory` argument; no global Git trust setting was changed.
- GitHub CLI authentication was checked and the stored account token was invalid. Publication stopped; no browser workaround, credential extraction, remote creation, commit, or push occurred.
- A local Git repository exists on `main`, but there is no commit or remote yet. This log must gain the reviewed initial commit SHA after owner authentication and commit-identity confirmation.
- Local YAML-library parsing was not assumed. CI syntax and pinned action identities were reviewed statically; hosted CI remains part of the publication gate.

### Verification record

Final runtime versions, commands, test counts, generated-file checks, public-tree scan totals, and Git diff checks are appended in the next entry after the corrected tree is rerun.

### External-action record

No external state was changed. Research was read-only. No money or cryptocurrency moved, no terms were accepted, and no third party was contacted.

## 2026-08-08 — Session 002 — Second adversarial hardening

### Surviving findings from the second review

- Patch Cabinet did not auto-load its sponsor-local exclusion context, still serialized excluded names, accepted extra manifest fields into public JSON, treated SPDX syntax as an open-source license gate, accepted caller-computed activity age, and omitted policy/schema provenance.
- The Lab's verified path used `git status`. An adversarial repository-local `core.fsmonitor` command executed during the check, and `skip-worktree` hid a modified workflow while the report still claimed a verified clean checkout.
- Git metadata capture was not bounded before the collector limits, origin identity discarded port/path case, heuristic wording exceeded the evidence, initial sample-publication policy lacked an opt-in/anonymization condition, and terms overstated deletion/revocation of public artifacts.

### Corrections

- Patch Cabinet now auto-loads local exclusions, fails closed when local context is absent unless an explicit public/demo flag is used, redacts excluded results, rejects unknown fields, derives activity age, enforces a narrow documented license allowlist, and emits a versioned envelope with engine, policy, dependency, as-of, and source-hash provenance.
- The Lab now reads capped Git commit/tree/blob output instead of worktree files in verified mode. It sanitizes inherited Git variables, disables filesystem monitoring, replacement objects, optional locks, prompts, and lazy fetching, caps every Git response, rejects special tree entries, and SHA-1-checks commit and returned text-blob content.
- Added executable regression probes for the filesystem-monitor command and skip-worktree contamination, plus Git-output, junction, total-text, file-count, no-execution, date, identity, composite-action, mutable-container, and Markdown-injection coverage.
- Changed report language to signals, review priority, and possible friction; added matched-line evidence for text rules and report/rules version provenance.
- Real published samples must be maintainer opt-in or non-identifying. Paid delivery defaults to a patch branch; a pull request requires an invitation and compatible upstream policy.
- Terms now disclose persistence of public Git history, forks, caches, archives, and third-party copies. Dashboard language is limited to sponsor-reported UI readings.

### Verification pending in this entry

The final consolidated command results, sample hashes, staged-tree scan, and initial commit SHA are appended after the final independent re-review. Publication and revenue acceptance remain blocked by their separate gates.

## 2026-08-08 — Session 003 — Reviewed local launch candidate

### Final architecture corrections

- A third revenue probe showed that configured Git origin data could be spoofed, target-controlled Git metadata remained outside a complete no-execution boundary, and a partial-clone helper could outlive a top-level timeout. D-014 therefore removed the verified Git mode entirely. The MVP now fails closed unless explicitly invoked on a synthetic or trusted project-owned local demo, labels URL/commit/date as declared and unverified, and invokes no Git, subprocess, network client, or target code.
- The revenue collector now uses incremental entry enumeration with entry, file, path, depth, per-file, aggregate-text, and retained-evidence caps. Evidence is sorted before truncation; Unicode format/direction and line-separator controls are escaped. Its internal time checks are documented as cooperative, and storage locality is not claimed.
- Real repository reports and every sale are blocked until the disposable acquisition and network-disabled analysis gate in D-014 passes, in addition to the legal, merchant, tax, privacy, refund, support, and private-security-reporting gates.
- D-015 removed Patch Cabinet exclusion auto-discovery. Every project run passes the ignored operator-owned file explicitly; a missing file fails closed unless a public/synthetic no-context flag is explicit. Target repositories cannot supply this policy input.
- Patch Cabinet now rejects duplicate JSON keys, non-standard constants, oversized manifests/candidate sets, malformed/non-public-style URL authorities, overlong hostnames, the null Git object ID, future/stale evidence, and ambiguous historical mode. Historical output is explicitly selected and never `ready`.

### Independent adversarial verdicts

- Three independent final reviews covered Patch Cabinet, the revenue collector, and shared documentation/privacy/CI. After corrections, none reported a surviving P0, P1, or P2 finding.
- The shared-tree reviewer passed the launch candidate for local reviewed history only. External publication, real-repository revenue analysis, payment, and upstream work remain separately gated.

### Reproducible verification

- Runtime: Codex bundled CPython 3.12.13; Git 2.53.0.windows.3; `packaging` 26.2. The isolated verification environment installed both local packages with no cache, no build isolation, and no dependency resolution; `pip check` reported no broken requirements and both installed entry points returned help successfully.
- Installed-package tests with `ResourceWarning` treated as an error: Patch Cabinet 25/25 passed. Linux Release Readiness Lab ran 19 tests: 18 passed and the Windows symlink test skipped because this session lacks symlink privilege; the Windows junction test passed.
- Source modules compiled successfully. Intended Python source and test lines were checked at 100 characters or fewer.
- Installed `policy.py`, Patch CLI, revenue `audit.py`, and revenue CLI hashes matched their working-source counterparts exactly before sample generation.
- All four installed-entry-point regenerations matched the committed-target samples byte-for-byte and used LF-only newlines:
  - Patch Markdown: `e02dba527e4daf9e47c6f64b3b6d92fe820b7a264e7e40816261d5f21fe369f5`
  - Patch JSON: `2929b1d236ec6034731dd2da7989f6bfa0b72630da1a3fb82eabd68021c57d58`
  - Revenue Markdown: `419cecd948f6dfc5676e68c30e2767c2eaf64f3331450c1eb9a9441caebe1e4a`
  - Revenue JSON: `2125b89eca85c500bda02887f03e89c290f7611cc8fc63c58bb4dd673d3763da`
- A project-mode Patch run explicitly loaded the real ignored exclusion file. Its synthetic output remained byte-identical to the public sample, demonstrating that private policy context did not enter the artifact.
- The final shared-tree review's bounded public scan passed 52 intended files, 194,834 bytes, and six secret-signature families. It also resolved all 19 relative Markdown links and found no sponsor handle, local path, exact plan/wallet quantity, credential signature, or inclusion of either ignored private record. A fresh staged-tree scan follows before commit.

### External-action state

- XLM remains untouched. No cash was spent; no domain, merchant account, customer record, sale, advertisement, social post, third-party contact, target-repository clone, upstream contribution, or remote repository was created.
- GitHub CLI 2.96.0 was present, but its stored account authentication was invalid when checked. The owner must reauthenticate before remote creation. Publication also requires enabled private vulnerability reporting and a passing hosted CI run.
- Local commits use the project-only neutral identity `Cairn-Inspo automation <cairn-inspo@localhost.invalid>` via per-command environment variables. No global Git identity or trust configuration is changed.

## 2026-08-08 — Session 004 — Local history created

- Immediately before the launch commit, the staged scope contained exactly 52 intended public files. `git diff --cached --check` passed, the bounded public-tree scanner passed 52 files / 199,931 bytes / six signature families, and no ignored/private/build path was staged.
- Created root commit `fea128776194193fd133c468ba2d8b3d3c7e01e1` (`Launch Patch Cabinet and Linux release lab`) on local `main` using the neutral project-only author and committer identity recorded above.
- After the commit, the working tree contained no tracked or untracked public changes. Only ignored `.private`, `.tmp`, build, package-metadata, and bytecode/cache directories remained.
- No remote exists and nothing was pushed. GitHub reauthentication, private vulnerability reporting, and hosted CI remain publication gates.

## 2026-08-08 — Session 005 — Private hosted-CI staging

### Reviewed work units

- Patch Cabinet completed one public, read-only discovery unit. Creator Toolkit CLI issue 18 was
  independently revalidated as open, unassigned, uncommented, documentation-only, and unrelated
  to the sole open pull request. The evidence remains `investigate`, not implementation-ready,
  because no explicit upstream AI-contribution policy was found. No contact or target checkout
  occurred.
- Release Readiness Lab completed one synthetic contract-only D-014 unit. Repeated adversarial
  review corrected bounded JSON parsing, resource/isolation shape coverage, sentinel digests,
  integration-boundary parsing, and acquisition/analysis signature sequencing. The public
  entrypoint has no acquisition, network, Git, subprocess, target-execution, or real-repository
  eligibility path.
- Three independent final reviews reported no surviving P1 or P2 finding after the corrections.

### Local verification

- Installed both packages from the reviewed tree without dependency resolution or build
  isolation; `pip check` and both installed entrypoint help commands passed.
- Patch Cabinet passed 25/25 tests. Release Readiness Lab ran 41 tests: 40 passed and the Windows
  symlink test skipped because the local session lacks symlink privilege; its junction test passed.
- Compilation, whitespace, generated sample reproduction, the bounded public-tree scan, and the
  immutable candidate-evidence replay passed. The intended public scan covered 61 files / 295,870
  bytes / six secret-signature families before commit.

### Private staging action

- The owner reauthenticated GitHub CLI 2.96.0 as the expected account; token contents were not
  displayed or stored in the project.
- Created neutral branch `agent/launch-linux-agent-workbench` and commit
  `bd9f7b5ed312171a0a9b8d820c4c118a34dfacce` (`Add first work units and publication gates`).
- Created the private `linux-agent-workbench-ci` staging repository, pushed local `main` and the
  candidate branch, and opened draft staging PR 1. This was project publication infrastructure,
  not third-party contact.
- Hosted Actions run `31249833586` passed all five jobs on the exact candidate commit: Python 3.12,
  3.13, and 3.14; Release Readiness on Windows; and generated-evidence/privacy integrity.
- The final repository does not yet exist and no source is public. GitHub private vulnerability
  reporting is available only on public repositories, so D-016 requires a public-but-empty final
  repository, verified private reporting, and only then the source push.

### External-action state

- No issue, upstream pull request, comment, social post, advertisement, domain, merchant account,
  customer record, payment, sale, purchase, wallet action, or XLM movement occurred.
- The private staging repository is retained as audit evidence. It is not a customer-facing or
  revenue channel.

## 2026-08-08 — Session 006 — Public source launch

### Gate sequence

- Pushed the audit-log update to the private staging PR. Hosted Actions run `31249908795` passed
  the same five jobs on candidate commit `594bf0f9928e90533d1c6cb8d647852df56ad6ee`.
- Marked staging PR 1 ready and merged it as
  `703a4efb05b41e4632f2ec7911d6cda846729166`; the reviewed candidate commit remains separately
  identifiable in that history.
- Created `imyourpriest/linux-agent-workbench` as a public but empty repository. Before pushing any
  source, enabled private vulnerability reporting, confirmed the API returned `enabled: true`, and
  confirmed that an unauthenticated visitor could see **Report a vulnerability** on the repository
  security page. The empty repository reported size zero at that checkpoint.
- Added the final repository as local `origin` and pushed the privately verified candidate commit
  to `main`. Public CI run `31249964779` passed all five jobs on the same exact commit.

### Public security baseline

- Enabled Dependabot vulnerability alerts and security updates. GitHub secret scanning and push
  protection were enabled. Default CodeQL setup was configured for Actions and Python; run
  `31249984455` passed both analyses.
- At the post-run snapshot, the repository reported zero Dependabot alerts, zero secret-scanning
  alerts, and zero CodeQL alerts. These are time-stamped launch observations, not guarantees.
- Protected `main` with strict required checks for the five CI jobs and both CodeQL analyses,
  administrator enforcement, pull-request use, conversation resolution, and linear history.
  Force pushes and branch deletion are disabled; no approving review is required because the
  accountable owner is currently the sole maintainer.
- Enabled public Issues, disabled the unused wiki, and added descriptive Linux, open-source,
  AI-agent, reproducible-research, and GitHub Actions topics.

### Publication outcome

- Public source: `https://github.com/imyourpriest/linux-agent-workbench` at launch commit
  `594bf0f9928e90533d1c6cb8d647852df56ad6ee`.
- The source crossed the public boundary only after the private reporting route was enabled and
  tested. The same source state passed private staging CI and public CI.
- No upstream project or candidate was contacted. No social promotion, customer outreach, domain,
  merchant relationship, payment, purchase, sale, wallet action, or XLM movement occurred.
- Patch Cabinet issue 18 remains evidence-only and `investigate`. D-014 and every real-repository
  Revenue Lab report or sale remain blocked by the real isolation, legal, merchant, privacy,
  support, refund, and tax gates.

## 2026-08-08 — Session 007 — First post-launch maintenance boundary

- GitHub's first Dependabot pull request proposed `packaging` 26.3 for Patch Cabinet. All ordinary
  tests passed, but the immutable-evidence job rejected the unversioned evaluator dependency
  change because the published engine 0.1.0 bundle records 26.2.
- Opened issue 3 to design a versioned migration that keeps historical bundles unchanged and
  reproducible. Closed Dependabot PR 1 without merging and linked the explanation to issue 3.
- D-017 pauses ordinary Patch Cabinet version-update PRs with `open-pull-requests-limit: 0`, the
  GitHub-documented configuration that retains security updates. Vulnerability alerts,
  security-update proposals, Revenue Lab and Actions version monitoring, and CodeQL remain
  enabled; ordinary Patch dependency updates resume only after the versioned migration.
- This is one Patch Cabinet maintenance work unit, bringing recorded dedicated units to eight
  Patch Cabinet and four Revenue Lab. No dependency or historical artifact changed, and no
  third-party project was contacted.

## 2026-08-08 — Session 008 — Reset and mandate correction

- The sponsor reported that the first period ended with approximately 13% remaining, below the
  intended 25% personal reserve. Project work paused until the sponsor reported a reset to 100%.
- At the start of the resumed turn, the signed-in product Usage page directly displayed 98%
  remaining after reset verification and setup. It is a whole-account snapshot, not exact
  project attribution.
- Adopted a 40% operational stop and a rule against beginning long or multi-agent work below 50%.
  This creates a 15-point buffer above the sponsor's protected final 25%.
- Clarified that the named projects, Linux, and open source are preferences and current hypotheses,
  not permanent constraints. The AI operating task may pivot, replace, combine, or end weak concepts.
- Clarified that the sponsor contribution is hard-capped at $20 per month. Every plan
  upgrade, model/API credit, host, domain, or tool must be funded by cleared project receipts,
  demonstrate repeat coverage, retain three future monthly increments after each charge, and
  revert or pause before it could increase the sponsor's bill. Existing XLM and sponsor transfers
  are not project funding.
- No money, XLM, account, subscription, credit, domain, customer, marketing message, or third-party
  repository changed during this governance correction.

## 2026-08-08 — Session 009 — Versioned Patch evidence migration

- Implemented D-021 locally on `agent/governance-and-evidence-v2`. The published 0.1.0 candidate
  bundle and four-file receipt remain unchanged; a replay-only capsule retains the exact
  `packaging==26.2` wheel. New output identifies engine 0.2.0 and `packaging==26.3`.
- Added a strict registry, frozen Season 1.2 policy source, hash-pinned offline wheels and locks,
  a versioned replay adapter, an active 0.2.0 synthetic vector, and CI replay across Python
  3.12–3.14. Restored the Patch Cabinet Dependabot version-update limit from zero to five.
- Independent adversarial review found and blocked pre-hash source execution, Windows backslash
  scope escape, and symlinked-directory escape. The corrected verifier statically parses the
  hash-bound descriptor, directly loads only hash-verified frozen code, resolves every registered
  path inside its declared subdirectory, caps inputs/inventory, discards worker output, and rejects
  artifact-role collisions.
- Local verification passed 26 Patch policy tests. The replay-control suite ran 19 tests: 18
  passed and one expected Windows test skipped because this session cannot create directory
  symlinks. Both registered
  engines passed isolated replay, including the historical receipted bundle and active synthetic
  vector. Revenue Lab's 41-test suite remained 40 passed with its existing privilege-dependent
  symlink skip. Compilation, package dependency checks, and the public-tree heuristic scan passed.
- This records two Patch Cabinet work units: one versioned migration and one distinct adversarial
  containment correction. A direct whole-account Usage-page reading after these units showed 83%
  remaining; no per-action consumption is inferred. The branch remains local and uncommitted at this checkpoint; no GitHub
  issue, pull request, dependency, customer, payment, wallet, XLM, domain, account, or subscription
  changed yet.

## 2026-08-08 - Session 010 - Revenue pivot prototype and combined local checkpoint

- Implemented D-022 and D-023 locally as Support Agent Regression Lab: a free ten-case synthetic
  support-agent regression starter, an offline deterministic checker, an explicit human-review
  rubric, mocked before/after runs, and reproducible response-free reports. Linux Release
  Readiness Lab remains intact but parked; D-014 still blocks every hostile third-party checkout.
- The first paid hypothesis is deliberately narrow: $149 for ten original cases derived from one
  approved public policy source, a rubric and response-free comparison template, one revision,
  and a proposed five-business-day initial handoff. It is not an active offer or market-value
  claim. The $49 reusable template is secondary; larger or recurring work remains deferred.
- Independent security review found and reproduced sensitive-content acceptance, deep-nesting
  failure, pathname time-of-check/time-of-use exposure, existing-output hard-link overwrite, and
  a review-to-fail classification error. The corrected local-only path uses an explicit separate
  command, common-sensitive-pattern preflight, one verified input descriptor, bounded nesting,
  atomic same-directory output replacement, severity ordering, and response-free reports. The
  review then returned no surviving P0-P2 findings.
- Independent product review narrowed scope and required a public/permanent issue-form warning,
  AI-assistance disclosure, fixed delivery/revision window, hash-confidentiality caveat, and a
  measurable validation record. Qualified views now require a unique unlisted channel-entry path
  in GitHub Traffic's Popular content table, a declared UTC window, manual owner-preview
  subtraction, and a retained record at least every 14 days; unattributed repository totals do not
  count. The final product review returned clean.
- Local tests passed: Patch Cabinet 26/26; Release Readiness Lab 41 tests with one expected
  Windows privilege-dependent symlink skip; Support Agent Regression Lab 17/17; replay controls
  19 tests with one expected Windows symlink skip. Both registered Patch engines and the immutable
  evidence checker passed. All three generated sample pairs were regenerated from the installed
  packages. Compilation and dependency checks passed. The final bounded public-tree scan covered
  96 files / 716308 bytes / six secret-signature families.
- This is one revenue work unit, bringing R-002 to two Patch units and one revenue unit. A direct
  whole-account Usage-page observation after the unit showed 73% remaining; no per-action usage is
  inferred. Created the project-owned `support-eval-interest` label so the public issue form does
  not reference a missing label; no issue was submitted. The branch remains local and uncommitted
  at this checkpoint. No customer, marketing post, checkout, payment, merchant account, purchase,
  domain, wallet, XLM, subscription, or customer/private input changed.

## 2026-08-08 - Session 011 - Versioned migration and Support Eval publication

- Committed the 57-file reviewed scope as `72d3bcd341dbe4a9492f21b48fbd541211e09778` on
  `agent/governance-and-evidence-v2` and pushed that branch. Ignored `.private`, `.tmp`, build,
  egg-info, and cache paths were not staged. The existing four-file Patch candidate bundle and
  its receipt were unchanged relative to the previous public `main`.
- The GitHub connector returned HTTP 403 when asked to create the pull request, so the documented
  publication fallback used the already authenticated GitHub CLI. Draft PR 5 accurately disclosed
  the AI assistance, safety boundary, local checks, and absence of customers, payments, wallet
  actions, or marketing. No repository source changed during that fallback.
- PR 5's protected checks passed on the exact branch commit: CI run `31284206557` passed Python
  3.12, 3.13, 3.14, the preserved `Release Readiness on Windows` check, and generated-evidence
  replay; CodeQL run `31284205553` passed Actions and Python analysis. Only then was the PR marked
  ready and squash-merged.
- Public `main` now points to `c961ab29792a0edd29df29aaae9651b5ab1ed906`. PR 5 is merged and its
  `Closes #3` link closed the versioned-evidence-migration issue. Post-merge CI run `31284253009`
  and CodeQL run `31284252933` both passed on that exact merge commit.
- The project-owned `support-eval-interest` label exists for the public nonbinding form. At the
  post-merge checkpoint, private vulnerability reporting returned `enabled: true`; Dependabot,
  secret-scanning, and code-scanning APIs each returned zero open alerts. These are time-stamped
  observations, not guarantees. No open issue or pull request remained.
- A direct whole-account Usage-page reading after merge and hosted verification showed 69%
  remaining; the final publication-audit snapshot showed 67%. Neither is attributed to a
  particular action. R-002 remains two Patch units to one revenue unit; publication is shared
  completion work, not another dedicated unit. Revenue remains $0.00. No customer, interest
  submission, marketing post, checkout, payment, merchant account, purchase, domain, wallet, XLM,
  subscription, upstream contact, or customer/private input changed.

## 2026-08-08 - Session 012 - Consent gate and first channel local checkpoint

- D-024 records the sponsor's one-time request to continue R-002 toward, but not below, the 25%
  protected floor. Direct whole-account readings during this continuation were 64%, 60%, 59%,
  54%, and 49% remaining. No delta is attributed to an individual action.
- Completed one bounded, public, read-only Patch candidate scan. Creator Toolkit CLI issue 18
  remained `investigate` because no explicit policy permits this AI-operated workflow. LoopGate
  issue 2 had explicit AI rules but no bounded remaining patch and possible contributor overlap.
  Several near-matches expressly barred autonomous submissions. No upstream repository was
  cloned, downloaded, executed, contacted, assigned, reacted to, or modified.
- Added a second immutable candidate bundle under engine 0.2.0, then migrated new output to engine
  0.3.0, policy `season-1.3`, and schema 2. The consent status and controlled basis must now bind
  to a same-repository GitHub policy file at the exact candidate commit and are emitted in result
  evidence. Canonical-path validation rejects wrong repositories, wrong commits, raw or encoded
  traversal, backslashes, dot components, and doubled leading separators. Historical engines
  0.1.0 and 0.2.0 and both prior bundles remain replay-only and byte-preserved.
- Independent security review first reproduced the unbound-enum weakness, then raw/encoded path
  traversal and doubled-leading-separator cases. Independent final review found no surviving
  P0-P2 issue after schema binding, frozen replay-v2, canonical URL validation, regression tests,
  and registry/hash updates.
- Prepared D-026's first revenue channel: one SHA-pinned project-owned GitHub pre-release, six
  accurate added topics, one corrected repository description, and one unique public entry path.
  It offers only the free synthetic starter, has no uploaded assets or checkout, and uses no other
  project's issues, comments, discussions, direct messages, scraped contacts, or bulk outreach.
  Measurement treats missing top-path rows as unobservable, subtracts owner previews, freezes the
  issue form, and counts only unverified, in-window, boundary-compliant, non-owner/non-bot form
  issues once per account. The public-submission incident path fails closed. Independent final
  channel review found no surviving P0-P2 issue.
- Final local checks passed: Patch Cabinet 27/27; Release Readiness Lab 41 tests with one expected
  Windows privilege-dependent symlink skip; Support Agent Regression Lab 17/17; replay controls
  19 tests with one expected Windows symlink skip. All three registered Patch engines and both
  immutable evidence bundles replayed. Generated samples, compilation, package checks, diff
  checks, and the original bundle byte-comparison passed. The pre-log bounded public-tree scan
  covered 109 files / 914263 bytes / six signature families.
- This records two Patch units and one Support Agent Regression Lab unit, bringing R-002 to a 4:2
  ratio and the cumulative dedicated totals to 12 impact and 6 revenue units. The branch is still
  local and uncommitted at this checkpoint; the release and topics are not active. Revenue,
  interest, orders, payments, expenses, subscriptions, domains, wallet movements, and XLM use
  remain $0 or absent.

## 2026-08-09 - Session 013 - Consent migration publication and channel activation

- Committed the reviewed 37-file scope as `b25c0684ed1d7452281a64e80a8cf334a42233a9` on
  `agent/r003-impact-revenue-cycle`. Explicit staging checks excluded `.private`, `.tmp`, caches,
  build output, distributions, and egg-info. The connector returned HTTP 403 for pull-request
  creation, ready-for-review, and merge mutations, so the documented authenticated GitHub CLI
  fallback opened draft PR 7, marked it ready only after hosted checks, and squash-merged its exact
  head.
- PR 7 CI run `31286258695` passed Python 3.12, 3.13, 3.14, Windows, and generated-evidence
  checks; CodeQL run `31286257927` passed Actions and Python analysis. Public `main` became
  `2b162ce572379a10a61007a722a7ba7e23d43f75`. Main CI run `31286316986`, CodeQL run
  `31286316861`, and dependency-graph run `31286318876` then passed on that exact merge commit.
- A just-in-time checkpoint confirmed the authenticated owner account, public repository,
  owner-admin permission, enabled private vulnerability reporting, enabled Dependabot security
  updates, secret scanning and push protection, no prior release, the expected five topics and old
  description, and no new identity, terms, recovery, or credential prompt.
- Corrected the description to name both workstreams and added only the six reviewed topics.
  Published source-only pre-release `support-eval-starter-v0.1.0` at
  `2026-08-09T00:33:48Z`, pinned by lightweight tag to the exact merge commit. It is not a draft,
  is not the latest stable release, and has no uploaded assets. The release body matched the
  versioned template exactly after its one SHA substitution.
- The release-body SHA-256 is
  `9c2db782538e604c05188525fbb7c39424d16e33287ff867118cf285a5a03acd`; the frozen issue-form
  SHA-256 is `e6a3a9fc9a610b109dfd74dabb3c78538ab12554dbaf2945c4679454ac70ac0e`.
  The complete activation receipt and frozen metadata are in `support-eval-lab/CHANNEL_EXPERIMENTS.md`.
- Direct whole-account Usage-page readings showed 47% remaining after the first post-merge
  checkpoint and 46% after activation. Neither change is attributed to a particular action.
  Release activation completes the previously counted revenue unit and preserves R-002's 4:2
  dedicated-work ratio.
- Post-receipt local verification passed 27 Patch tests, 41 Release Readiness tests with one
  expected Windows privilege-dependent symlink skip, 17 Support Eval tests, and 19 replay-control
  tests with one expected Windows directory-symlink skip. All three registered Patch engines and
  both immutable bundles passed, as did compilation and dependency checks. Immediately before
  this log line was added, the bounded public-tree scan covered 109 files / 924814 bytes / six
  signature families; it is a heuristic supplement, not a privacy guarantee.
- No customer, qualifying interest, order, payment, expense, subscription, domain, wallet
  movement, XLM use, private input, external marketing post, direct message, or third-party
  project interaction occurred. Revenue remains $0.00.

## 2026-08-09 - Session 014 - Consent catalog and channel-observation closeout

- Began the final bounded R-002 cycle from public `main`
  `d8bde52d96bd2247a1cc62d5de80a8f2d84b585e` on local branch
  `agent/r003-catalog-observation`. This cycle contains two Patch Cabinet impact units and one
  Support Agent Regression Lab revenue unit. No additional unit began after the direct Usage-page
  reading reached 27% remaining.
- Added the separate strict contribution-consent catalog. Its schema binds repository, exact
  commit, canonical pinned policy path, source SHA-256, manual review dates, exact workflow,
  controlled classification, immutable successor history, and a non-authorizing claim boundary.
  Future dates, invalid chronology, unsafe Markdown, malformed JSON, unsafe files, and output/input
  aliases fail closed. The generated index makes no eligibility or permission claim.
- Added four conservative records from the completed public scan: Creator Toolkit CLI and
  LoopGate Harness remain `insufficiently_explicit`; Hugging Face Transformers and DSPy are
  `explicitly_disallows`. There is intentionally no `explicitly_allows` record. A separate
  acquisition receipt binds all four exact GitHub Contents API refs, Git blob identifiers, byte
  counts, and decoded-byte SHA-256 values while explicitly disclaiming signatures and semantic
  interpretation. Historical engine bundles and replay capsules were byte-preserved.
- Added the offline SEL-GH-001 channel-observation normalizer and minimal activation record. The
  registered configuration is file-hash and owner-namespace bound; configuration agreement is
  derived from repeated observed fields. Checked traffic binds one exact retained 14-day window,
  owner previews are subtracted only inside that window, duplicate issues and late final captures
  are rejected, absent rows remain null/unobservable, and every output keeps checkout false.
  The record contains no issue text, screenshot, customer/private input, or payment data.
- Independent review reproduced four catalog P2s and three Support P1/two P2 findings. Corrections
  added real-date bounds, inert CommonMark/GFM note encoding, chronological successors, a source
  receipt, registered configuration/owner binding, duplicate-issue rejection, final deadlines,
  retained-window arithmetic, and input/output identity checks. A final Support P2 showed that
  portable two-file replacement is not transactional; the tool now claims only staged per-file
  replacement, embeds the canonical JSON SHA-256 in Markdown, and requires full regeneration on
  failure. Both independent final re-reviews reported no surviving P0-P2.
- Final local verification passed 40 Patch tests with one expected Windows symlink-privilege skip,
  41 Release Readiness tests with one expected skip, 35 Support tests with one expected skip, and
  19 replay-control tests with one expected directory-symlink skip. All three Patch engines and
  both immutable candidate bundles replayed; regenerated artifacts, compilation, dependency,
  whitespace, and historical-evidence comparisons passed. Immediately before this log entry, the
  bounded public-tree heuristic covered 126 files / 1062509 bytes / six signature families; it is
  not a privacy guarantee.
- Direct whole-account Usage readings during this cycle were 45%, 40%, and 27% remaining. No
  change is attributed to an individual action. At 27%, D-024 permits only review resolution,
  publication, and closeout and protects the 25% floor. R-002 now contains six impact and three
  revenue units; cumulative dedicated totals are fourteen and seven, preserving 2:1.
- At this pre-publication checkpoint the branch remains local and uncommitted. Revenue and cleared
  receipts remain $0.00. No customer, qualifying interest, order, checkout, payment, merchant
  account, purchase, subscription, domain, wallet movement, XLM use, private input, upstream
  contact, pull request, social post, advertisement, or direct message occurred in this cycle.

## 2026-08-10 - Session 015 - Source-limited traffic checkpoint prepared

- D-029 records the sponsor's one-time authorization to continue from a reported 14% toward
  approximately 4% remaining for this bounded checkpoint, review, publication, and closeout. A
  direct Usage-page reading soon afterward showed 12% remaining, an August 15, 2026 4:22 PM reset,
  no reset available, and zero credits. Both are whole-account snapshots; no change is attributed
  to this project or any action, and no new work unit is counted.
- At `2026-08-10T22:33:36Z`, the authenticated GitHub Popular content request returned three
  top-path rows and no exact match for the frozen SEL-GH-001 entry path. The endpoint supplies no
  exact retained-window cutoff, so D-030 keeps this source-limited receipt outside the current
  normalizer. The absent top-ten row is unobservable, not zero; the current normalized report
  remains unchanged with null raw and qualified views and a not-observed state. The new receipt
  does not validate those values.
- The `2026-08-10T22:34:53Z` through `2026-08-10T22:35:05Z` configuration recheck found the public
  repository, frozen description and topics, default `main`, source-only research pre-release,
  lightweight tag target, and issue-form hash unchanged. The bounded GitHub Search query from
  `2026-08-10T22:44:57Z` through `2026-08-10T22:44:58Z` returned `total_count: 0`,
  `incomplete_results: false`, and zero returned items for issues with the frozen interest label.
  This is not proof of no private or off-platform interest. These checks establish observed
  configuration and source response only, not traffic, attribution, or buyer intent.
- Completed local evidence checks: the receipt invariants and `git diff --check` passed; the
  Support Eval suite ran 35 tests with 34 passing and one expected Windows link-privilege skip.
  The bounded public-tree heuristic passed over 127 files / 1077209 bytes / six signature
  families; it is not a privacy guarantee. An independent security reviewer initially found two
  P2 claim and provenance issues. After correction, its focused re-review reported no surviving
  P0-P2 issue in this seven-file scope. Remote facts remain time-bound API/operator evidence, and
  the ad hoc receipt has no schema or consumer. These local checks are not production proof.
- This documentation-and-evidence branch is local and uncommitted at this checkpoint. Separately
  from the source check, the AI operating task's session ledger records that it neither initiated
  nor received a sale, customer inquiry, qualifying-interest event, order, checkout, payment,
  expense, private input, upstream contact, social post, advertisement, or direct message, and did
  not create or change a merchant account, purchase, subscription, or domain and did not perform a
  wallet movement or use XLM.
  This is a project/session ledger assertion, not an inference from the source receipt. Cleared
  revenue remains $0.00.

## 2026-08-10 - Session 016 - PR 10 publication and R-003 reset

- PR [10](https://github.com/imyourpriest/linux-agent-workbench/pull/10) merged its exact head
  `35b443a887af4c6cc6a9fe945079b65a8dda8df7` at `2026-08-10T22:50:51Z` as public `main`
  `508404db5e0757f51b9ac677c432b2dfac995ffe`.
- PR CI run `31439874809` and CodeQL run `31439872974` passed on the exact PR head. Post-merge
  `main` CI run `31439983239` and CodeQL run `31439983110` passed on the exact merge commit. These
  hosted checks establish the reported workflows' results on those commits; they are not a claim
  of production enforcement.
- The final direct R-002 Usage-page reading after merge and `main` validation showed 2% remaining.
  The source is a whole-account snapshot and cannot attribute the change to this project or any
  individual action.
- The sponsor then reported the R-003 reset at 100%. The first direct Usage-page reading after
  reset verification and setup showed 99% remaining, the next reset at August 17, 2026 6:01 PM,
  no reset available, and zero credits. This is also a whole-account snapshot with no project or
  action attribution. No substantive R-003 work unit began before this record.
- D-024 and D-029 were one-reset R-002 exceptions and are now expired. Ordinary controls resume:
  maintain the 2:1 impact-to-revenue ratio while both workstreams remain active, start no long or
  multi-agent unit below 50%, stop at 40%, and protect the final 25%.
- Revenue and cleared receipts remain $0.00. No customer, qualifying interest, order, checkout,
  payment, merchant account, purchase, expense, subscription, domain, wallet movement, XLM use,
  private input, upstream contact, social post, advertisement, or direct message was recorded in
  this publication/reset closeout.

## 2026-08-10 - Session 017 - R-003 three-unit batch and review correction

- Completed two Patch Cabinet impact units: the current autonomous-workflow candidate scan and the
  standalone manual policy-profile experiment. Completed one Support Agent Regression Lab revenue
  unit: the current primary-source payment/distribution channel comparison. This batch establishes
  the required 2:1 period ratio; it does not assign usage to any unit or reactivate the parked
  Revenue Lab.
- Post-review correction made Ruff fail closed because its pinned contributor file delegates
  substantive AI rules to an unbound cross-repository mutable policy. The receipt, successor, and
  junction/reparse boundaries were corrected and tested. The output-parent claim was narrowed and
  documented as trusted-local scope rather than adversarially tested. No prior frozen evidence,
  engine, verifier, parked Revenue Lab input, SEL-GH-001 release, form, configuration, or
  observation window changed.
- The direct Usage-page reading after the complete three-unit batch showed 86% remaining. This is
  one whole-account snapshot; no delta or amount is attributed to a project, workstream, unit,
  agent, tool call, or action.
- The active Support Agent Regression Lab payment-channel research remains provisional and does
  not pivot or reactivate the parked Revenue Lab. No merchant or payment account, checkout,
  listing, release, issue, customer, qualifying interest, order, payment, purchase, expense,
  subscription, domain, wallet movement, XLM use, private input, upstream contact, social post,
  advertisement, or direct message occurred. Revenue and cleared receipts remain $0.00.

## 2026-08-10 - Session 018 - Clean re-review and pre-publication checkpoint

- After remediation, an independent clean re-review reported no P0-P3 finding in its reviewed
  scope. This is a bounded review verdict, not proof that the repository or production environment
  is free of defects.
- Primary local reruns passed: Patch Cabinet discovered 59 tests, with 57 passing and two
  privilege-dependent symlink skips; both Windows junction tests ran and passed. Tools discovered
  19 tests, with 18 passing and one privilege-dependent symlink skip. Revenue Lab discovered 41
  tests, with 40 passing and one privilege-dependent symlink skip. Support Agent Regression Lab
  discovered 35 tests, with 34 passing and one privilege-dependent symlink skip. All three
  immutable candidate bundles replayed successfully.
- The bounded public-tree heuristic passed across 144 files / 1,182,984 bytes / six
  secret-signature families, and `git diff --check` passed. The public-tree result is a heuristic,
  not a privacy guarantee. Hosted CI has not yet run on these uncommitted changes, and external
  platform facts remain provisional and require revalidation before action.
- A direct whole-account Usage-page snapshot after remediation and clean re-review showed 73%
  remaining, the next reset at August 17, 2026 6:00 PM, no reset available, and zero credits. No
  delta or amount is attributed to this project, workstream, unit, agent, tool call, or action.

## 2026-08-10 - Session 019 - PR 11 publication and declaration-policy batch

- PR 11 published exact head `240f639b3fe6b643da059f12128a5bfb3cc87bb9`. PR CI run
  `31448798931` and CodeQL run `31448797163` passed on that head. The pull request was
  squash-merged at `2026-08-11T01:18:19Z` as public `main`
  `d7330d84df969b60e31132bf6039eb2403e25376`; post-main CI run `31448891667` and CodeQL run
  `31448891498` passed on that exact commit. These hosted results establish only the named
  workflows' observed outcomes on those commits, not production enforcement.
- A direct whole-account Usage-page snapshot after publication showed 70% remaining, the next
  reset at August 17, 2026 6:00 PM, no reset available, and zero credits. A later direct snapshot
  after the declaration-policy research phase showed 68% remaining with the same reset, reset
  availability, and credit state. No delta or amount is attributed to this project, workstream,
  unit, agent, tool call, or action.
- Completed two Patch Cabinet impact units: the isolated maintainer policy declaration prototype
  and its bounded public-context research. Completed one Support Agent Regression Lab revenue
  research unit for the future public-source-only AI Contribution Policy Starter + Audit. This
  preserves the R-003 and cumulative 2:1 ratios. Governance, review, and publication are not extra
  work units.
- Revenue and cleared receipts remain `$0.00`. Beyond the recorded project PR publication, no
  maintainer/customer contact, account, listing, checkout, payment, purchase, subscription,
  release, issue, form, external post, wallet movement, XLM use, private input, or other external
  action occurred in this batch. SEL-GH-001 and the parked Revenue Lab remain unchanged.

## 2026-08-10 - Session 020 - Declaration prototype independent-review remediation

- Independent review found no P0-P2 issue in the reviewed scope and held publication for five P3
  corrections: ambiguous identity wording, synthetic use of a live-provider namespace,
  punctuation-folded identifiers, successor kind transitions, and insufficient unaided starter
  guidance. D-034 and the Patch Cabinet log explicitly correct rather than silently rewrite the
  earlier append-only description.
- Accepted project records are now described as maintainer- or operator-supplied and
  unauthenticated/unverified. Reserved `example.invalid` synthetic provenance is inert, canonical
  IDs hash the complete identity, lineage preserves record kind and basis, and the starter and
  schema reference expose exact controlled values. These are local structural controls, not
  authentication, authority, source-truth, current-permission, or production-enforcement proof.
- Local validation retains honest platform boundaries: link tests may skip when Windows denies
  symlink creation, hosted CI has not yet run on the remediation, and local passing tests do not
  establish production enforcement. No external action or additional work unit occurred.
- A direct whole-account Usage-page snapshot after validation showed 62% remaining, the next reset
  at August 17, 2026 6:00 PM, no reset available, and zero credits. No delta or amount is attributed
  to this repository, workstream, unit, agent, tool call, test, or action.

## 2026-08-12 - Session 021 - PR 12 publication receipt and R-006 batch start

- PR 12 published exact head `830f3d39575518517264f0853126bec308527a6a`. PR CI run
  `31451569534` and CodeQL run `31451568339` passed on that head. The pull request was
  squash-merged at `2026-08-11T02:12:24Z` as public `main`
  `6d2acca70dbeed4f6df658c0055acb97cd84068e`; post-main CI run `31451666188` and CodeQL run
  `31451666248` passed on that exact commit. These hosted results establish only the observed
  named workflow outcomes on those commits, not production enforcement.
- The new R-006/R-003 batch began from an observed whole-account Usage snapshot of 55% remaining,
  next reset August 17, 2026 at 6:01 PM, no additional reset available, and zero credits. No delta
  or amount is attributed to this project, batch, workstream, unit, agent, tool call, test, or
  action. D-035 records the sponsor's one-reset 15% floor and start/closeout thresholds.
- D-036 selects two Patch impact units and one Support revenue unit with local-only non-activation
  boundaries. No final post-work Usage reading is recorded here; that reading remains pending.

## 2026-08-12 - Session 022 - R-006 independent-review remediation

- Independent review identified two P2 publication blockers: mutable-manifest content was not
  independently bound before the policy-starter receipt emitted fixed boundaries, and the
  declaration reference still named component 0.1.0. It also identified an evidence-directory
  preflight capacity edge after the exact narrative exception.
- Remediation binds every canonical pack content file to verifier-owned checked-tree digests,
  derives declaration identity from canonical semantics, ties the documented declaration version
  to runtime, and accounts for only the exact name-and-digest narrative allowlist in evidence
  capacity. The
  verifier constants are local checked-tree policy, not signatures or an external trust anchor.
- This correction changes no work-unit count and records no final post-work Usage reading. No
  commit, publication, customer/contact/payment action, private input, or external state change is
  claimed by this local remediation entry.

## 2026-08-12 - Session 023 - PR 13 Windows test-fixture correction

- Exact PR head `42d300254b64bfb8bf3d7b40f2aed2d99f4389f3` failed CI run `31650000604`,
  protected Windows job `94292016466`. Linux, CodeQL, and generated-freshness checks passed.
- The failure was in test setup, not an observed verifier acceptance: `os.link` crossed from the
  `D:` checkout to the `C:` temporary volume and raised WinError 17 before validation. The local
  test now creates both hard-link names on the same temporary volume, confirms shared identity and
  link count, and exercises the unchanged verifier rejection.
- No hosted rerun success is claimed by this entry. No production code, work-unit total, Usage
  reading, commit, publication, customer/contact/payment action, private input, or external state
  changed during this local correction.

## 2026-08-13 - Session 024 - PR 13 publication receipt and R-004 reset baseline

- PR 13 was published at https://github.com/imyourpriest/linux-agent-workbench/pull/13 with reviewed
  head `397dbe6d8fe4216e559c1c41c22e942c5aa5cc6e`, then merged at `2026-08-12T23:20:46Z` as public
  `main` `bca18d21aa3a3df18b8a7ae32d966321681f418f`. PR CI `31650442543` and CodeQL
  `31650438270` succeeded; post-main CI `31650541809`, CodeQL `31650540794`, and dependency graph
  `31650543744` succeeded at that exact public SHA. These are hosted results for named commits and
  workflows, not local tests or production enforcement.
- The sponsor separately reported 93% whole-account Usage remaining after the reset. A later direct
  signed-in Usage page displayed 91% remaining, reset August 19, 2026 at 9:33 PM, no reset
  available, and zero credits. No exact capture time is claimed, the two-point difference is not
  attributed, and no amount is attributed to this repository, batch, unit, agent, or action.
- Before work, branch, HEAD, and `origin/main` were `agent/r007-policy-release-prep`,
  `bca18d21aa3a3df18b8a7ae32d966321681f418f`, and the same public SHA, with a clean worktree. The
  frozen pre-change inventory covered 107 files with fingerprint
  `9b63fa8294e34d29bc6c8df97c19848f0b37ba27e747f5eb0a085a4cba8ac2dc`.

## 2026-08-13 - Session 025 - R-004 three-unit batch prepared locally

- Completed exactly two Patch impact units and one Support revenue-validation unit. R-004 totals
  are 2/1; cumulative totals are 22 impact and 11 revenue, preserving 2:1.
- Prepared candidates, records, form draft, and measurement contract are not publication, policy
  adoption, demand, willingness to pay, customers, sales, listing, or production enforcement.
  Revenue and cleared receipts remain `$0.00`.
- No commit, push, issue, pull request, release, tag, topic, setting, account, form activation,
  message, payment rail, purchase, wallet movement, XLM use, private-input access, or external
  action occurred. Hosted CI has not evaluated these local changes.

## 2026-08-13 - Session 026 - R-004 measurement semantics correction

- Claims review identified a P3 ambiguity in how the prepared Support experiment combined its
  metric thresholds. The corrected local validator applies explicit final-checkpoint logic:
  success iff every success gate passes; failure iff either failure gate passes; otherwise the
  result is inconclusive. Tests cover boundary combinations, exact source/window bindings,
  contradictory declared results, privacy fields, paid-signal separation, and payment/channel
  invariants.
- This correction changes no work-unit or revenue total and does not activate any release, form,
  channel, payment, customer contact, or external state. Hosted CI and production enforcement are
  not claimed.

## 2026-08-13 - Session 027 - R-004 usage-ledger omission corrected

- The R-004 reset snapshots and work-unit totals were recorded in this control log but omitted
  from `docs/USAGE_LEDGER.md`. The append-only R-004 ledger section now records the separate 93%
  sponsor report and later 91% direct display, zero-unit PR 13 publication receipt, exact 2/1 batch,
  cumulative 22/11 totals, `$0.00` revenue, and the absence of a final post-work reading or per-unit
  attribution. Prior entries are unchanged.

## 2026-08-13 - Session 028 - R-004 final assurance review remediation

- Final assurance review identified predictable archive staging in both new builders (P2),
  incomplete exact Support field/artifact binding (P2), and ignored extra `__pycache__` inventory
  (P3). Both builders now use exclusive random descriptor-backed staging in checked trusted-local
  directories and leave the old predictable regular/hard-link sentinel paths unchanged. Support
  validation closes and cross-binds admitted static and generated fields and rejects all extras.
- Focused declaration tests passed 9 with two Windows privilege skips; focused Support tests passed
  17 with two such skips; the full Support suite passed 66 with four skips. Exact regeneration,
  Support freshness, modified-module compilation, and diff checks passed locally. These results are
  local structural evidence, not hosted CI or production enforcement.
- No work-unit, Usage, or revenue total changes. No network, private input, commit, push,
  publication, activation, payment, customer contact, or external state changed.

## 2026-08-13 - Session 029 - R-004 final local verification and Usage checkpoint

- The stable final working tree passed 91 Patch tests with five Windows privilege-dependent skips,
  66 Support tests with four skips, 41 parked Revenue tests with one skip, and 22 evidence-control
  tests with one skip. All three registered engine workers and three immutable bundles passed.
- Twenty-five generated artifacts regenerated exactly in OS temporary copies. The bounded public-
  tree heuristic passed across 195 files / 1,506,691 bytes / six signature families. The frozen
  inventory remained exactly 107 files with fingerprint
  `9b63fa8294e34d29bc6c8df97c19848f0b37ba27e747f5eb0a085a4cba8ac2dc`.
  These are local and synthetic validation results, not hosted CI or production enforcement.
- A later direct signed-in Usage page displayed 67% whole-account capacity remaining, with the
  next reset shown as August 19, 2026 at 9:33 PM, no reset available, and zero credits. No delta or
  amount is attributed to this repository, workstream, unit, agent, tool call, test, or action.
- No work-unit or revenue total changed. No network, private input, commit, push, publication,
  activation, payment, customer contact, or other external action occurred.

## 2026-08-13 - Session 030 - PR 14 receipt and R-004 extension start

- PR 14 was reviewed at head `64e91a6f69e9c935478e6cf4e48d0d4923b475bd` and squash-merged at
  `2026-08-13T16:02:32Z` as public `main` `6b9c0a506f325210482f3942cdc7f2be3331ce4d`.
  The feature and merge trees match at `70ea964d8179cb4f4a5a606f3780723f20a8957d`.
  PR CI `31718464458`, PR CodeQL `31718462348`, post-main CI `31718633677`, and
  post-main CodeQL `31718632949` succeeded. No post-main Dependency Graph run was observed during
  bounded checks; absence of an observed run is not a failure claim. These hosted results establish
  only the named workflow outcomes on the named commits, not production enforcement.
- The branch started clean on `agent/r007-policy-release-prep` at the reviewed PR head, with local
  `origin/main` at the exact public-main SHA. The authorized local branch
  `agent/r008-policy-interop-audit` was created from that public-main commit. Git commands used a
  per-command safe-directory override; no global Git trust setting changed.
- A direct signed-in Usage page at batch start showed 60% weekly remaining, reset August 19, 2026
  at 9:33 PM, no reset available, and zero credits. The sponsor authorized this one cycle down to
  a hard 30% floor; ordinary 40% reserve resumes next reset. This is a whole-account snapshot and
  no amount or delta is attributed to this repository, batch, unit, agent, tool call, or action.

## 2026-08-13 - Session 031 - R-004 interoperability and inert audit batch prepared locally

- Completed exactly two Patch impact units and one Support revenue unit under D-038. Cumulative
  totals are 24 impact and 12 revenue, preserving 2:1. Revenue and cleared receipts remain `$0.00`.
- Added a versioned declaration structural profile/corpus with authoritative-parser evidence and
  lossy non-authorizing projections; a neutral date-window catalog snapshot/query over existing
  records; and an isolated project-owned synthetic public-policy-audit artifact pack. No
  independent JSON Schema validator was tested. Local structural checks are not production
  enforcement or proof of identity, authority, current permission, adoption, or source truth.
- No network, subprocess, target execution, third-party checkout, real/customer/private input,
  commit, push, pull request, release, issue, ruleset, listing, checkout, payment, outreach,
  account, credential, subscription, purchase, domain, wallet movement, XLM use, or other external
  action occurred. SEL-GH-001, the parked Revenue Lab, and prior frozen artifacts remain unchanged.

## 2026-08-13 - Session 032 - R-004 extension security-review remediation

- The independently reviewed pre-remediation baseline was branch
  `agent/r008-policy-interop-audit`, HEAD and `origin/main`
  `6b9c0a506f325210482f3942cdc7f2be3331ce4d`, 36 expanded content paths (13 modified,
  23 untracked), canonical path/newline/little-endian-length/content SHA-256
  `3277f724dfe684a4cbd7bed961f46967cb3acaec9f2ec3eddbf83c08b21823f5`, and clean diff check.
- Security review reported two P2s: the Support verifier lacked an independent checked-fixture
  anchor, and the Patch corpus allowed accepted records with non-valid labels to supply a
  projection. It also requested iterative structure bounds, stronger trusted-project descendant
  path checks and honest TOCTOU scope, subprocess wording correction, and removal of invented PR
  obligations for `not_declared` fields.
- Remediation adds verifier-owned Support fixture digests and precise checked-tree result wording;
  closed Patch classification/expectation/observation tuples and a valid-only projection source;
  iterative bounded walking; output-chain/leaf rechecks; independent-maintainer-proposal wording;
  and explicit disclosure that a Windows test invokes `cmd.exe` solely for junction setup. Local
  constants are not external trust anchors, and descendant checks are not race-proof against a
  concurrently hostile trusted project parent.
- This correction adds no work unit and changes no Usage or revenue claim. Totals remain 24 Patch
  impact / 12 Support revenue units and `$0.00`. No network, external input, commit, push,
  publication, activation, listing, issue, payment, customer contact, or other external action
  occurred. The production modules remain network/subprocess free; the Windows junction test
  subprocess is test-fixture setup only.
- Stable local validation passed: focused Patch 12/12; focused Support 12 with 11 passing and one
  symlink-privilege skip; full Patch 109 with five skips; full Support 78 with five skips; parked
  Revenue 41 with one skip; tools/evidence 22 with one skip. All three registered replay workers
  and three immutable bundles passed. Complete artifact regeneration/freshness, compileall,
  `pip check`, and `git diff --check` passed. The bounded public-tree heuristic passed 218 files /
  1,636,596 bytes / six signature families; it is not a privacy guarantee. The 104-file frozen
  inventory remained zero-difference at listing fingerprint
  `10ed570e0e049d50abc242e838d8195d4ad7d532ff41d5d6cfac3d10b4eb3902`.

## 2026-08-13 - Session 033 - PR 15 publication receipt and R-004 extension closeout

- PR [#15](https://github.com/imyourpriest/linux-agent-workbench/pull/15) was reviewed and pushed
  at head `591aea1cf38875d5ae699e33e9c95a8cfa600f88`. PR CI run `31738504542` succeeded for
  Python 3.12, 3.13, 3.14, Release Readiness on Windows, and Generated evidence is current. PR
  CodeQL run `31738502560` succeeded for actions and python; the repository CodeQL check also
  passed, with no separate run ID recorded here.
- The PR was marked ready and squash-merged at `2026-08-13T19:59:38Z` using the exact expected-head
  guard. Public main and the merge commit are
  `d45af0624cfbda0ad7b9de87a3aa2f0901534578`; the feature and public-main trees both resolve to
  `dd1366456bdff92096087dadbdbe91a0986a582a`. Post-main CI run `31738623378` succeeded, and
  post-main CodeQL/Push run `31738623352` succeeded for actions and python. These hosted results
  describe only the named checks on the named commits, not production enforcement.
- Local `main` was clean after the merge and matched `origin/main` at the public-main commit.
- A direct signed-in Usage observation after merge showed 38% weekly remaining, reset August 19,
  2026 at 9:33 PM, and zero credits. This is global whole-account UI state; no amount or delta is
  attributed to this task, repository, workstream, unit, agent, tool call, or action. The
  sponsor-authorized one-cycle 30% floor was honored. The normal 40% reserve resumes next reset
  and cycle.
- This publication receipt adds zero Patch or Support work units. Cumulative totals remain exactly
  24 Patch impact / 12 Support revenue units, and revenue remains `$0.00`. No release, active
  form, payment, outreach, customer or private input, XLM movement, or other activation occurred.

## 2026-08-19 - Session 034 - Corrected R-005 local batch start

- Public `main` and the clean local baseline were verified at
  `0ecc40ee1935abd88a309ac3a61134b9357db624`; the local work branch is
  `agent/r009-policy-compatibility`. Git commands use a per-command safe-directory override; no
  global Git trust setting changed.
- Before the first write, the frozen baseline contained 99 tracked files. Its sorted Git
  `ls-tree` inventory fingerprint was
  `756910a774d9988a4f4e7bd0444b2ff84f83e7cdf2a92e605e5b4fd4b9df055f`. The inventory covers the
  frozen declaration `v1`, candidate/evidence/verifier/catalog surfaces, SEL-GH-001 records and
  channels, the complete policy-release experiment, and all parked Revenue Lab files.
- A whole-account start snapshot reported 88% weekly remaining, reset August 26, 2026 at 9:34 PM,
  no resets available, and zero credits. This is a whole-account snapshot only; no amount or delta
  is attributed to this repository, batch, workstream, unit, agent, tool call, test, or action.
- D-039 authorizes only the local two-Patch/one-Support R-005 preparation. No external mutation,
  package execution, activation, revenue, or customer input is authorized.

## 2026-08-19 - Session 035 - Corrected R-005 batch prepared locally

- Completed exactly two Patch impact units and one Support revenue unit under D-039, bringing
  cumulative dedicated totals to 26 impact / 13 revenue and preserving 2:1. Revenue remains
  `$0.00`.
- Prepared two separate hosted structural-compatibility jobs, one exact field-by-field projection
  contract, and one uniquely identified inert direct successor in the existing `$79` hypothesis
  lineage. The third-party validators were not installed, imported, or executed locally. Their
  prepared receipt states both hosted observations are `not_observed`.
- Public package metadata/artifacts used only to prepare reviewed locks were downloaded in a
  disposable temporary area with user configuration disabled and scripts disabled. No downloaded
  validator package was installed or executed. Node/npm was unavailable locally; exact Ajv and
  transitive lock resolution/integrity metadata was obtained directly from the HTTPS npm registry
  and inspected statically.
- No commit, push, pull request, release, form activation, account, checkout, payment, customer
  input, private input, contact, analytics, package execution, or other external mutation occurred.
  Local structural and synthetic validation is not hosted CI or production enforcement.
- Stable local validation passed: 119 Patch tests with five Windows privilege-dependent skips, 84
  Support tests with five skips, 41 parked Revenue tests with one skip, and 22 evidence-control
  tests with one skip. All three registered engine replay workers and all three immutable candidate
  bundles passed. The three new deterministic freshness checks, compileall, `pip check`,
  `git diff --check`, and the bounded six-family public-tree heuristic passed.
- The frozen surfaces remained zero-difference at 99 tracked files with the original sorted
  `ls-tree` fingerprint
  `756910a774d9988a4f4e7bd0444b2ff84f83e7cdf2a92e605e5b4fd4b9df055f`. These local checks do not
  prove hosted behavior, privacy, isolation, or production enforcement.
- The final signed-in Usage snapshot showed 79% weekly remaining, reset August 26, 2026 at
  9:34 PM, no usage-limit resets available, and zero credits. This is whole-account state only.
  The observed nine-point delta is not attributable to this repository, task, workstream, unit,
  agent, tool call, test, or action; no per-unit usage is inferred.
- The first static review found two hosted-harness issues: each hosted job lacked its own
  pre-acquisition closed-harness check, and the Node duplicate-key preflight incorrectly treated
  equal keys in distinct objects as duplicates while runner results omitted complete expected/
  observed bindings. Primary trace review also found an unsupported predecessor experiment label.
  All three findings were remediated locally: both jobs now self-check,
  runner outputs and verifier-owned configurations are fully bound, the Node parser is
  object-scoped with a closed counterexample, and the predecessor now binds the exact frozen
  `policy-release-r004` release. Independent re-review remains required. No Usage snapshot, work
  unit, revenue, activation, or external-action claim changed.
- The first re-review found the frozen predecessor `README.md` and `ISSUE_FORM_DRAFT.yml` were
  closed-inventory and manifest-covered but not directly rehashed by the successor verifier. Both
  files now have exact verifier-owned SHA-256 bindings and byte-mutation regression cases. Final
  independent re-review remains required; Usage, work-unit, revenue, activation, and external-
  action claims remain unchanged.

## 2026-08-19 - Session 036 - D-040 pre-action publication control

- The sponsor reports 67% whole-account Usage remaining and authorizes the already-started R-005
  publication and closeout down to a hard 35% floor. Start no new three-unit batch at or below
  45%; stop immediately at 35%, any Usage warning, or any lower sponsor report. Ordinary Usage
  policy resumes at reset or R-005 closeout, whichever comes first. The reading and any delta are
  whole-account state only and are not attributed to this repository, task, workstream, unit,
  agent, tool, test, or action; no per-unit usage is inferred.
- D-040 prospectively permits only the exact R-005 source-review path: one initial local commit on
  `agent/r009-policy-compatibility` descended from public-main base
  `0ecc40ee1935abd88a309ac3a61134b9357db624`, one initial branch push to the existing project-owned
  public repository, and at most one draft pull request. At most two additional in-scope commits
  and pushes may address concrete hosted failures on that same branch and same pull request; each
  requires affected local validation/freshness reruns, a new exact whole-tree fingerprint and
  independent review before push, and all hosted checks rerun on the new exact head. All required
  checks must pass before ready/squash-merge, and publication/hosted/merge/post-main receipts remain
  required. A third cycle, scope expansion, branch or pull-request change, or inability to retain
  controls stops the path pending a new prospective decision.
- Only after both new compatibility contexts pass on the exact pull-request head, D-040 permits
  adding exactly `Python jsonschema 4.26.0 structural compatibility` and
  `Node Ajv 8.20.0 structural compatibility` to `main`'s required contexts. The change must retain
  every existing required context and protection without bypass or weakening, and the additive
  result must be verified before merge. If an additive-only change cannot be made and verified,
  stop rather than merge.
- Read-only live observations on 2026-08-19/20 UTC found authenticated owner `imyourpriest` and
  public origin `imyourpriest/linux-agent-workbench` with default branch `main`. Remote `main` was
  exactly `0ecc40ee1935abd88a309ac3a61134b9357db624`, and no pull requests were open. Private
  vulnerability reporting, secret scanning, and push protection were enabled. `main` protection
  was strict and admin-enforced, with force pushes and deletion disabled and seven existing
  required check contexts. CodeQL is evidenced here only by the required contexts
  `Analyze (actions)` and `Analyze (python)`; no Advanced Security status is claimed because the
  corresponding API value was null.
- The earlier `f768009f501282ab97630f2660aba2cf50e3db63e120d2c7ca6cb2434aa341f0`
  whole-diff fingerprint used culture-aware PowerShell ordering. Independent reconstruction found
  no byte drift and established the pre-D-040 ordinal baseline as
  `bb0e1f62df912fabc7157ad83fb537427413520287743f89691ff2f0615931db`. A final
  post-edit fingerprint and independent review are still required before publication.
- This pre-action entry records no commit, push, pull request, hosted run, merge, release, form
  activation, listing, offer, contact, customer/private input, payment, account action, or other
  external mutation. D-040 leaves every August 25 SEL, exclusive-selection, legal, privacy,
  merchant/payment, and exact external-action gate intact. Time alone is never sufficient.
- Any future hosted success establishes only the named configured structural checks on its named
  run and commit. It does not establish attestation, authentication, semantic correctness,
  provenance, freshness, privacy, isolation, standard adoption, source truth, permission, or
  production enforcement.
- Independent coherence review found that the draft's earlier one-commit/one-push wording
  conflicted with its authorization for in-scope hosted remediation. The still-uncommitted D-040
  draft now permits exactly one initial commit and push plus at most two additional remediation
  commits and pushes to the same branch and single draft pull request. Each additional cycle must
  respond to a concrete hosted failure, remain within R-005, rerun affected local validation and
  freshness, receive a new exact whole-tree fingerprint and independent review before push, and
  rerun every hosted check on the new exact head. A third cycle, scope expansion, branch or pull-
  request change, or inability to retain controls stops the path pending a new decision.
- Before that wording fix, the exact 43-file tree had canonical ordinal fingerprint
  `8c570266dadbea3731e08b227159492cc5d82c2dc5c26bb67542aca971a7ed6f`. Stable local validation
  passed: Patch 119 tests with five skips; Support 84 with five skips; parked Revenue 41 with one
  skip; and evidence-control 22 with one skip. All three freshness checks, all three registered
  engine workers and three immutable bundles, in-memory compilation, `pip check`, the bounded
  six-family public-tree heuristic, `git diff --check`, and the frozen 99-file zero-difference
  replay passed.
- These are local structural and synthetic results, not hosted behavior, privacy, isolation, or
  production enforcement. Python `jsonschema` 4.26.0 and Node Ajv 8.20.0 remain unexecuted locally.

## 2026-08-20 - Session 037 - R-005 hosted compatibility remediation cycle 1

- The reviewed branch `agent/r009-policy-compatibility` was pushed at exact commit
  `0ac9cd67dd8e9a91126ff1e407b054465659f4e1`. The GitHub connector returned 403
  `Resource not accessible by integration`; authenticated read-only CLI verification then found
  zero pull requests for the head, and the single authorized fallback created draft PR 17 with
  maintainer edits disabled. This entry does not authorize another PR, branch, or activation.
- Workflow run `32336332382` failed on that exact head. Python job `96326529034` and Node job
  `96326528729` both stopped in their closed-harness step after checkout and setup-python but before
  the exact locked validator-dependency installation steps (`pip install --require-hashes` and
  `npm ci`) and before either structural-adapter step ran. No hosted structural validator result
  or success is claimed; no claim is made that the runner platform itself performed no network
  acquisition.
- Root cause was package-style preflight execution: `python -B -m
  patch_cabinet.declaration_compatibility` imported `patch_cabinet.__init__` and `policy.py`, which
  required absent `packaging` before the workflow acquired its locked dependencies. The minimal
  in-scope fix directly runs the project-owned standard-library checker at
  `patch-cabinet/src/patch_cabinet/declaration_compatibility.py` from the repository root in both
  jobs, with no workflow `PYTHONPATH`. Tests bind both exact commands, both setup-python pins, and
  their ordering before `pip install` and `npm ci`.
- This is remediation cycle 1 of at most two authorized cycles. It adds no Patch or Support unit,
  hosted success, activation, release, candidate selection, customer/private input, payment, or
  revenue; cumulative totals remain 26 impact / 13 revenue units and revenue remains `$0.00`.
  All D-039/D-040 claim limits and future gates remain unchanged.
