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
