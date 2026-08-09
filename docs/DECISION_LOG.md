# Decision log

Append-only. A superseding entry may change a decision; old entries remain.

## 2026-08-07 — D-001 — One monorepo, two workstreams

**Decision:** Start in one local repository with shared governance and separate `patch-cabinet/` and `revenue-lab/` write scopes. Keep this originating task as the control record and create a dedicated task for each workstream when available.

**Why:** Shared provenance, policy, and usage accounting remain atomic while day-to-day context stays focused. Separate external repositories may be considered later if customer/private commercial data creates a real boundary.

## 2026-08-07 — D-002 — Patch Cabinet is Linux/open-source public service

**Decision:** Prioritize small fixes for public, explicitly licensed Linux-facing tools and infrastructure. Optimize for maintainer usefulness, test evidence, and accepted patches—not patch count or theatrical autonomy.

**Why:** This matches the sponsor's interests and produces durable public value. High-volume unsolicited pull requests are explicitly rejected.

## 2026-08-07 — D-003 — Revenue project becomes a Linux release-readiness service

**Decision:** Build a productized service around reproducible Linux release-readiness evidence, with paid value tied to an owner-accountable repair plan or maintainer-approved repair patch. Use **Linux Release Readiness Lab** as a descriptive pre-brand name. Retire the initial `ReleaseMender` working name before publication because of confusion risk with the established Linux update brand Mender. Initial scope is public Go and Python CLI repositories targeting Linux.

**Why:** Generic repository scores are heavily commoditized by free and inexpensive tools. Correct integration and a passing patch are clearer buyer outcomes. The name remains subject to final trademark and registrar checks before public commercial use.

## 2026-08-07 — D-004 — No XLM or cash seed

**Decision:** Start both projects at $0. Leave the sponsor's preexisting cryptocurrency in its existing wallet and outside all agent environments.

**Why:** The wallet is not needed to validate either thesis. Using it adds key, accounting, tax, and possibly custody risk without improving the first deliverable.

## 2026-08-07 — D-005 — Usage policy is 2:1 plus reserve

**Decision:** Allocate project work in a 2:1 Patch Cabinet-to-Release-Readiness-Lab ratio and preserve 25% of the sponsor's overall weekly allowance. Use sponsor-reported UI readings for the global stop boundary; use work units only to keep effort proportional.

**Why:** Model, context, reasoning, retrieval, and tool use make messages an unreliable usage measure. False precision would undermine the audit trail.

## 2026-08-07 — D-006 — Human-owned external identity

**Decision:** Accounts, domains, wallets, contracts, merchant relationships, and revenue are owned by the sponsor or a sponsor-owned entity. The AI may prepare and operate within granted access but will not invent an identity or claim ownership.

**Why:** External services and law require an accountable person or entity. Minimal input cannot waive service confirmations, identity checks, contributor attestations, or financial approvals.

## 2026-08-07 — D-007 — MIT license for project-owned code

**Decision:** License original project-owned code and documentation under MIT at launch. Upstream contributions inherit and comply with the target project's terms.

**Why:** A short, recognized permissive license lowers reuse friction. This can be superseded for a separable component if a stronger copyleft rationale emerges.

## 2026-08-07 — D-008 — Evidence before domain or paid infrastructure

**Decision:** Do not buy a domain or paid service until the Release Readiness Lab reaches its validation gate: ten sample audits, at least 100 qualified page views from relevant channels (not claimed to be unique people), at least five maintainer opt-ins, and at least one explicit nonbinding request for a paid pilot. A registrar and trademark-confusion check happens immediately before any purchase.

**Why:** A domain does not validate demand. Free infrastructure is sufficient for initial evidence.

## 2026-08-07 — D-009 — Verification is a report property, not marketing copy

**Decision:** Public reports default to a clean-Git-checkout provenance gate that verifies origin, HEAD, tracked files, and clean state before and after collection. Caller-supplied repository metadata is permitted only behind an explicit demo flag and must be labeled unverified in the report.

**Why:** A commit-shaped string is not evidence that the analyzed files came from that commit. Provenance must be machine-checked or honestly qualified.

## 2026-08-07 — D-010 — No fake checkout or hidden visitor tracking

**Decision:** The demand gate uses a clearly labeled, nonbinding paid-pilot request that accepts no payment details. Initial analytics are aggregate and data-minimizing; page views are not represented as unique people without evidence.

**Why:** A disabled or ambiguous checkout creates deceptive intent data, while invasive tracking would be disproportionate to early validation.

## 2026-08-08 — D-011 — Verified revenue reports scan commit objects

**Decision:** Verified Linux Release Readiness reports read bounded immutable Git commit objects. They do not use worktree cleanliness as provenance. Inherited Git configuration is sanitized, filesystem monitoring, replacement objects, and lazy fetching are disabled, output is capped, and returned commit/text-blob content is checked against its SHA-1 object identifier.

**Why:** A repository-local filesystem-monitor command can execute during `git status`, and skip-worktree flags can hide modified files. Neither mutable worktree state nor target-controlled Git helpers may enter a verified report.

## 2026-08-08 — D-012 — Patch Cabinet fails closed on local context

**Decision:** Project runs auto-load the ignored sponsor-local exclusion file when present and redact excluded candidates from every output. A public/demo installation without that context requires an explicit flag. Candidate manifests reject unknown fields, derive activity age from dates, and accept only a narrow reviewed Season 1 open-source license allowlist.

**Why:** Optional denylist loading and permissive serialization could leak sponsor context. Valid SPDX syntax does not by itself establish that a source-available or custom license fits an open-source contribution project.

## 2026-08-08 — D-013 — Source publication remains gated

**Decision:** Create reviewed local history, but do not create or publish the external repository until the owner reauthenticates GitHub and a private vulnerability-reporting route can be enabled and tested. Hosted CI must pass before the repository becomes public.

**Why:** Local green tests cannot substitute for owner authentication, safe vulnerability intake, or clean-checkout hosted evidence.

## 2026-08-08 — D-014 — Revenue provenance modes are removed from the MVP

**Decision:** Supersede D-009 and D-011. The current Linux Release Readiness collector supports only an explicit, unverified synthetic or trusted-local demo. It does not invoke Git and cannot emit verified provenance. Public repository reports remain blocked until acquisition occurs through a disposable, project-controlled environment that obtains and proves the upstream commit without trusting target-controlled Git metadata, then analyzes it with network access disabled.

**Why:** Local Git origin and object data can prove internal consistency but not upstream identity. More importantly, invoking Git against attacker-controlled metadata is not a complete no-execution boundary, and partial-clone helpers can outlive a top-level timeout. Removing the mode is safer and more truthful than overstating incremental hardening.

## 2026-08-08 — D-015 — Patch exclusions are explicit operator inputs

**Decision:** Supersede the auto-discovery portion of D-012. Project candidate runs must pass the ignored operator-owned exclusion file explicitly; the CLI never discovers exclusions from a manifest or target repository. Missing exclusion context fails closed unless a public/synthetic no-context flag is explicit. Repeatable explicit files are unioned and excluded candidates remain redacted.

**Why:** A target-controlled Git tree can contain a plausible `.private` file, while a manifest may live outside the project root. An explicit operator path is a smaller, auditable trust boundary and forgetting it stops the run rather than exposing a sponsor-excluded name.

## 2026-08-08 — D-016 — Publish through an isolated CI staging repository

**Decision:** Use `linux-agent-workbench` as the neutral descriptive public repository name. First
run the exact candidate commit and hosted checks in a separate private staging repository. Then
create the final repository public but empty, enable and verify GitHub private vulnerability
reporting before any source push, and publish only the already-verified commit. Keep the staging
repository private as audit evidence; do not delete it as part of launch.

**Why:** GitHub private vulnerability reporting is available only for public repositories. The
two-repository sequence satisfies both gates without exposing project source during a disclosure
gap, and the neutral name avoids implying affiliation with CairnWake or either workstream's future
commercial brand.

## 2026-08-08 — D-017 — Historical evidence dependencies move only through versioned migration

**Decision:** Do not merge automated version updates to a dependency recorded in a published
evaluator bundle. Temporarily set the Patch Cabinet package entry's version-update pull-request
limit to zero while a public issue defines a new engine/policy version, historical-verifier
selection, reproducibility tests, and a fail-closed migration. Keep vulnerability alerts and
security-update proposals enabled; continue Revenue Lab and Actions version monitoring.

**Why:** Replacing a recorded evaluator dependency in place would make historical evidence either
unreproducible or silently evaluated under different semantics. A versioned migration preserves
the append-only record while allowing future maintenance.

## 2026-08-08 — D-018 — Success outranks attachment to the initial concepts

**Decision:** Treat Patch Cabinet and Linux Release Readiness Lab as replaceable experiments. The
AI operating task may narrow, combine, rename, replace, or end either after a bounded evidence
review recorded by the control task, which first establishes the replacement charter and write scope.
Linux and open source are sponsor preferences and useful inspiration, not permanent constraints.

**Why:** The objective is lawful, useful impact and sustainable revenue. Preserving a weak initial
idea because effort has already been invested would substitute sunk cost for evidence.

## 2026-08-08 — D-019 — Every expansion must fund its own renewal and reversion

**Decision:** The sponsor contribution is hard-capped at $20 per month. A higher plan, API or model
credits, hosting, and any other project expense must be paid entirely from cleared project funds;
sponsor transfers and existing XLM are not permitted as project funding. Before activation and
before every renewal, cleared unrestricted funds must cover the next incremental charge plus three
further monthly increments, and recurring net revenue must have covered the monthly increment for
two consecutive months. After any charge, three future monthly increments remain reserved.
Downgrade, cancel, or pause before an uncovered renewal. If the base price rises above $20, project
funds cover the increment or project operation pauses.

**Why:** One receipt can buy capacity but does not prove the project can sustain it. A reserve,
repeat revenue, and automatic fallback keep project risk from becoming a personal bill.

## 2026-08-08 — D-020 — Usage stops at 40%, not at the sponsor reserve

**Decision:** Supersede D-005's 25% start-stop boundary. Preserve the final 25% for the sponsor by
stopping project work at 40% remaining and beginning no long or multi-agent unit below 50%.
Read the signed-in Usage page before and after substantive units when available; sponsor reports
remain authoritative snapshots when browser access is unavailable.

**Why:** The first period's observed end reading fell below the intended reserve. No cause is
attributed from a whole-account snapshot; a 15-point operational buffer reduces recurrence risk.

## 2026-08-08 — D-021 — Evidence engines migrate by addition, never replacement

**Decision:** Preserve engine 0.1.0 and its `packaging==26.2` environment as replay-only. Make
engine 0.2.0 with `packaging==26.3` the active generator, backed by a strict registry, frozen
policy source, hash-pinned offline wheels, a versioned replay adapter, and an active synthetic
replay vector. Existing candidate artifacts and their receipt remain byte-for-byte unchanged.
Ordinary Patch Cabinet dependency proposals resume only after both engines pass isolated replay.

The checker validates working-tree consistency tied to a reviewed commit; it is not an external
signature. It statically reads the hash-bound active descriptor, executes only pre-hashed frozen
policy/adapter code in isolated child interpreters, rejects path escapes and symlinked evidence
directories, and caps replay inputs and inventory. A policy, dependency, renderer, source, or
serialization change requires a new engine identity.

**Why:** Replacing a published evaluator dependency would destroy reproducibility. Append-only
engines allow maintenance without rewriting evidence, while frozen code and active replay vectors
prevent an apparently complete registry entry from bypassing its actual evaluator and renderer.

## 2026-08-08 — D-022 — Revenue pivots to support-agent regression packs

**Decision:** Park Linux Release Readiness Lab as an honest portfolio artifact and replace its
active revenue role with **Support Agent Regression Lab**, a descriptive pre-brand under
`support-eval-lab/`. The first bounded product is a free ten-case synthetic regression starter with
an offline deterministic checker, human-review rubric, mocked before/after runs, and reproducible
Markdown/JSON report. Proposed next offers are a $49 reusable expanded pack and a $149 custom
starter based only on sanitized, customer-approved public policy material; these are price
hypotheses, not established value, and no sale is eligible until the revenue gate passes.

The launch prototype accepts no credentials, production access, private transcripts, personal
data, model-provider keys, regulated-domain work, penetration testing, security/compliance claims,
or guarantees. It does not call a model or score subjective quality as objective fact. Human-review
fields remain visibly separate from deterministic checks. The earlier Lab, D-014, and its blocked
real-repository acquisition design remain intact and inactive.

**Why:** Upwork's completed-job data reports 109% year-over-year growth for AI-referencing skills
and 71% growth for AI chatbot development, while experimentation/testing remains an in-demand data
skill. Paid agent-evaluation products provide a second demand signal. This does not prove demand
for this offer, but it gives a faster, safer test than building the D-014 hostile-repository
platform before a buyer exists. The pivot creates a product that can demonstrate value using only
original synthetic data and project-owned code.

## 2026-08-08 — D-023 — The first paid hypothesis is a ten-case local pilot

**Decision:** Narrow D-022 after adversarial product review. The free artifact remains an
educational synthetic starter. Add an explicit `sanitized-local` mode for test outputs prepared
outside the tool from synthetic prompts and one customer-approved public policy source; it requires
an acknowledgement and still performs no upload, model call, customer-system access, or reviewer
authentication. Publish a review rubric and redaction-focused buyer quickstart.

Test a fixed $149 ten-case custom pilot with one comparison template and one revision, not a
30-case custom pack. Treat the $49 reusable template as a secondary hypothesis and defer larger or
recurring work until delivery time and repeat demand are measured. Focus initially on small B2B
SaaS teams with text support assistants. Evaluate at 45 days or 100 qualified views, whichever
comes first, under the operational view definition in the charter.

**Why:** The first draft was a credible technical demo but could not accept even sanitized local
test output and overstated example labels as completed human review. A smaller, explicit,
review-ready pilot is both more useful and more honest, while preserving the no-private-data and
no-production-access boundary.

## 2026-08-08 - D-024 - One-time R-002 work may approach the protected floor

**Decision:** For the remainder of reset period R-002 only, supersede D-020's 40% operational stop
after the sponsor explicitly requested continued work until only 25% remains. Preserve 25% as the
hard floor: read the signed-in Usage page before and after bounded units, begin no long or
multi-agent unit below 40%, begin no new work unit at or below 30%, and stop immediately at 25%, a
limit warning, or a lower sponsor report. The ordinary 40% stop and 50% long-unit threshold return
automatically at the next reset.

**Why:** The earlier buffer protected the sponsor after an unexplained overshoot. The sponsor now
knowingly authorizes use of that buffer for this reset while retaining the original 25% personal
reserve. Shorter endgame work and direct UI checks reduce, but cannot eliminate, delayed-meter
risk; no exact per-action usage is inferred.

## 2026-08-08 - D-025 - Autonomous contribution consent is a hard eligibility gate

**Decision:** Preserve Patch Cabinet engines 0.1.0 and 0.2.0 as replay-only. Make engine 0.3.0 with
policy `season-1.3` the active generator, retaining `packaging==26.3`. Under the new policy,
`ai_policy: allows` means pinned upstream text permits this actual AI-operated workflow: the AI
chooses and prepares the change, discloses its assistance, and a human performs only required
identity or attestation steps. Permission for human-led AI assistance is insufficient when the
same policy bars autonomous agents from opening issues or pull requests. `unknown` is ineligible,
not a scoring caution; `disallows` records an explicit conflict. Schema 2 requires a
same-repository policy-file URL pinned to the candidate commit and a controlled basis matching the
status, and emits all three as evidence. The engine verifies that binding and vocabulary; manual
review remains responsible for interpreting the pinned text.

Engine 0.2.0 retains the immutable autonomous-consent scan bundle created before this migration,
so its prior `investigate` treatment of unknown policy remains exactly replayable. Engine 0.3.0
owns a new hash-bound synthetic vector. No prior evidence or frozen policy is rewritten.

**Why:** Independent candidate scans found projects that welcome disclosed AI assistance while
explicitly prohibiting autonomous-agent submissions. A single generic AI-policy label could hide
that distinction. Treating silence as consent would create avoidable maintainer burden and weaken
the project's claim to be upstream-compatible.

## 2026-08-08 - D-026 - First revenue channel is a project-owned GitHub pre-release

**Decision:** Run one 14-day GitHub-native discovery experiment for Support Agent Regression Lab.
Create one unique channel-entry path not intentionally linked from standard navigation, accurately
classify the project with six added repository topics, and publish one pre-release targeting the
exact merge commit. The release is the only intentional direct link to the entry page; topics are
classification and discovery metadata, and views are not attributed exclusively to the release.
Correct the repository description once so it names both the open-source-impact and
support-agent-evaluation workstreams. The release offers the free synthetic starter, not a
purchase, and contains no uploaded asset, price, checkout, mention, discussion post, or request for
private input. Do not promote through another repository's issues, pull requests, comments,
discussions, direct messages, scraped contacts, or bulk outreach.

Record path-level GitHub Traffic observations on days 1, 7, 13, and 14 when available; subtract
logged owner previews and retain GitHub's measurement limitations. A missing top-path row is
unobservable, not zero. Freeze copy, issue form, and topics for the window except for platform,
privacy, security, or misleading-claim corrections. A retained row below ten qualified views or
zero qualifying self-reported interest signals at the day-14 observation ends this channel as
insufficient signal. Qualifying signals follow the charter's non-owner, non-bot, one-per-account,
boundary-compliant definition and remain unverified. No outcome activates checkout or bypasses the
existing validation and first-sale gates.

**Why:** The repository has no established audience. A project-owned release and accurate topics
are the narrowest platform-native discovery test that does not impose on another community or
pretend to have demand. Its likely low reach is a measured baseline, not evidence for spamming a
larger channel.

## 2026-08-09 - D-027 - Consent catalog is historical evidence, never automatic permission

**Decision:** Maintain a separate strict, offline catalog of manually reviewed public upstream
contribution-policy files. Each record binds one repository, exact commit, canonical file URL,
source-byte SHA-256, date, exact autonomous-workflow scope, controlled classification, and short
non-quoting rationale. Published records are not edited; a later policy becomes a validated
successor. The generated index marks records stale after seven days at its explicit as-of date.

The catalog never makes a candidate eligible or authorizes contact, implementation, or submission.
It does not fetch source or interpret prose. Every live candidate retains the current engine's own
policy fields plus the complete manual issue, competition, scope, security, attestation, and local
exclusion review.

**Why:** The bounded scan repeatedly encountered the same important distinction between human-led
AI assistance and autonomous-agent submission. Preserving pinned manual rejects and uncertainties
reduces rediscovery without turning an aging spreadsheet into a misleading permission directory.

## 2026-08-09 - D-028 - Channel observations are offline unverified evidence

**Decision:** Normalize SEL-GH-001 observations with a strict offline configuration and cumulative
event record. The schema accepts no issue title, body, comment, excerpt, screenshot, customer
input, or payment data. It never calls GitHub. It derives controlled state, subtracts logged owner
previews from one retained exact-path row without adding rolling snapshots, and represents an
absent row as `null` and `unobservable`, never zero. A sensitive or uncertain issue accepts only
its public URL, timestamps, and disposition and halts the channel.

The active experiment file is SHA-256 pinned in the validator, its repository owner must equal the
declared owner, and the cumulative record repeats the observed configuration fields rather than
asserting an opaque unchanged flag. Every checked traffic row binds an exact 14-day retained
window; the final row has a two-day post-window deadline. Duplicate issue identities are rejected,
and only owner previews inside the selected retained window are subtracted.

Qualifying interest remains operator-recorded and unverified. Author logins are used only to apply
the one-per-account rule and are omitted from generated reports. No channel result authorizes
checkout or supersedes the charter gate.

**Why:** Manual platform observations are easy to overcount or narrate into buyer evidence. A
closed schema and deterministic state machine preserve the measurement boundary while avoiding a
network integration or collection of submitted content.
