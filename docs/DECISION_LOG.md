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

## 2026-08-10 - D-029 - One-time R-002 usage extension for source-limited closeout

**Decision:** For this bounded SEL-GH-001 source check, its review, publication, and closeout only,
the sponsor's explicit request to use the remaining ten percentage points supersedes D-024's 25%
floor. Target approximately 4% remaining from the sponsor-reported 14% snapshot, use direct Usage
page checks when available, and stop on any limit warning or lower sponsor report. This is not a
new work unit and creates no automatic exception for a future reset or continuation.

**Why:** The sponsor knowingly authorized a small final evidence pass before the imminent reset.
The dashboard remains a delayed, whole-account measure, so neither the reported 14% nor the later
direct 12% snapshot can be attributed to this project or any individual action.

## 2026-08-10 - D-030 - GitHub traffic source limits override inferred window bounds

**Decision:** Do not fabricate exact retained-window start or end timestamps for GitHub's Popular
content endpoint. GitHub describes that endpoint as the top ten popular contents over the last 14
days, but its response exposes only path, title, count, and uniques. A source capture that lacks an
exact cutoff stays outside the current observation normalizer, whose checked-row contract requires
an exact 14-day window ending at capture time. An absent exact target is `unobservable`, not zero;
the existing normalized report remains unchanged with `null` raw and qualified views and a
`not-observed` state. The ad hoc source receipt does not validate those values. Any schema redesign
applies only prospectively and must preserve historical records.

**Why:** The current normalizer contract is stronger than the available source. Treating capture
time as GitHub's undisclosed cutoff would turn an implementation assumption into evidence and
could misclassify an absent top-ten row as measured traffic.

## 2026-08-10 - D-031 - Manual policy profiles are non-authorizing historical facts

**Decision:** Add a standalone schema-1 manual policy-profile catalog that binds exactly one
profile to one immutable consent record through the repeated repository, commit, policy path, and
source SHA-256. Normalize only eight controlled dimensions with manual semantic review and strict
offline validation. The catalog is not part of the candidate engine or versioned verifier and
does not automatically interpret or detect prose, establish current permission, make a candidate
eligible or ready, or authorize contact, implementation, issue creation, pull-request creation,
security reporting, or submission. Every live candidate retains the active engine and all current
manual policy, issue, competition, scope, security, attestation, and local-exclusion gates.

**Why:** Repeated policy review yields useful distinctions beyond one consent classification, but
turning those historical notes into engine authority would overstate aging evidence. Strict
provenance binding and a non-authorizing output boundary preserve the observations without
creating a permission directory.

**Post-review boundary:** A profile successor must exactly match the bound consent record's
successor, including `null`. The two checked-in acquisition-receipt shapes receive strict bounded
JSON and provenance validation, but a receipt remains a local record rather than a remote
signature. Catalog input directories reject links, Windows junctions, and detected reparse-point
directories. CLI output parents are trusted local filesystems; atomic replacement is not claimed
as protection against adversarial parent replacement between validation and writing.

## 2026-08-10 - D-032 - Payment channel remains provisional and human-owned

**Decision:** Record the active Support Agent Regression Lab's current primary-source comparison
as a provisional sequence only. If a payment test later passes the existing legal, validation,
reserve, and human-action gates, a public project-owned GitHub release or issue funnel leading to a
human-owned Ko-fi route currently appears to have the lowest upfront cost. GitHub Sponsors,
Gumroad, and GitHub Marketplace currently add greater identity, fee, setup, or adoption burdens for
this experiment. The dated official-source inventory is in `support-eval-lab/LOG.md`. Revalidate
every platform's current terms, fees, eligibility, and product fit immediately before any action.

This decision creates no merchant or payment account, checkout, listing, release, issue, or
external action. It does not activate a payment test, spend money, change the frozen SEL-GH-001
release/form/window, or establish buyer demand.
It does not pivot or reactivate the parked Revenue Lab.

**Why:** Preserving a bounded next-channel hypothesis reduces future rediscovery without turning a
source comparison into authorization or traction. Financial ownership and every platform
confirmation remain human checkpoints.

## 2026-08-10 - D-033 - Maintainer declarations are a 30-day prototype, not a standard

**Decision:** Run a 30-day local/public prototype for explicit trusted-local maintainer policy
declarations. The standalone schema validates structure and repeated commit-pinned fields and
renders deterministic cards. It does not fetch or parse policy prose, detect AI use, verify
repository ownership, authorship, source truth, current policy, or permission, score work,
authorize contact, feed Patch Cabinet candidate eligibility, or act as a CI merge gate.

This is distinct from `AGENTS.md`: that convention supplies repository-local instructions to
agents, while this prototype records a maintainer/operator declaration about contribution
practices. It is not a standard or proposed standard. Current public context captured on
2026-08-10 is listed in `patch-cabinet/MAINTAINER_POLICY_DECLARATION.md`, including AGENTS.md and
its issue 135, GitHub Community discussion 185387, LLVM, Home Assistant, The Carpentries, and
OpenSSF sources. Those projects do not endorse this prototype.

Success requires 3-5 maintainers, at least three unaided complete profiles in 15 minutes or less,
all seeded structural/provenance errors caught, faithful rendering, at least two reports of reuse
or time benefit, and no permission confusion. Stop without building beyond the prototype if fewer
than three maintainers participate, completion exceeds 20 minutes per profile, semantic
disagreement would force automated prose inference, authorization confusion occurs, or no
reuse/time benefit is reported.

**Why:** Public contribution policies expose repeated distinctions, but normalizing them without
an explicit declarant risks inventing semantics. A small, reversible, measured prototype can test
whether maintainers benefit from declaring the facts themselves without changing the candidate
engine or claiming a new ecosystem convention.

## 2026-08-10 - D-034 - Project declarations remain unauthenticated and unverified

**Decision:** Correct D-033's ambiguous identity wording. Accepted project records are
maintainer- or operator-supplied, unauthenticated/unverified declarations. Structural acceptance
does not authenticate the supplier, establish maintainer status or authority, verify the assertion
or source, show current permission, or authorize contact or submission. This correction supersedes
D-033 wherever that entry could be read as reserving verified maintainer authority.

Synthetic examples use only the reserved `example.invalid` namespace and render their source as
inert text. They make no existence or identity assertion and cannot transition into project
records. Project records retain exact same-repository, commit-pinned GitHub provenance but remain
unverified. Canonical IDs now hash the complete canonical identity, and successors preserve record
kind and assertion basis.

Independent review found no P0-P2 issue in the reviewed scope but held publication for five P3
corrections: identity wording, synthetic namespace isolation, collision-resistant identity,
kind-preserving lineage, and an unaided schema/starter reference. The corrections and validation
are local only; hosted CI has not yet evaluated them. Local symlink tests may skip when Windows
does not grant link-creation privilege, and local structural tests are not production enforcement.

**Why:** A declaration format must not manufacture identity or authority through labels, URLs, or
rendering. Explicit unauthenticated/unverified language and namespace separation keep the
prototype's claim boundary aligned with what local structural validation can actually establish.

## 2026-08-12 - D-035 - One-time R-003 usage exception with a 15% floor

**Decision:** For reset period R-003 only, the sponsor explicitly authorized spending up to 40
percentage points from the directly verified 55% whole-account reading while preserving a 15%
floor and the 2:1 impact-to-revenue ratio. Start no new three-unit batch at or below 30%. Below
30%, continue only already-started review, remediation, publication, and closeout. Stop immediately
at 15%, any product limit warning, or a lower sponsor reading. This exception expires at reset and
does not alter any other safety, authorization, financial, privacy, or external-action gate.

The signed-in Usage UI contradicted the earlier "likely tomorrow" estimate: the observed reset is
August 17, 2026 at 6:01 PM. The 55% reading is a whole-account snapshot and no portion is attributed
to this repository, batch, workstream, agent, tool call, test, or action.

**Why:** The sponsor knowingly authorized one bounded continuation with a larger reserve than the
prior period's final exception. Explicit start and stop thresholds prevent that authorization from
becoming an open-ended permission.

## 2026-08-12 - D-036 - Select one non-activated policy-starter batch

**Decision:** Select exactly two Patch Cabinet impact units and one Support Agent Regression Lab
revenue unit: a fail-closed no-ready scan, portable one-record declaration validation, and a fully
synthetic AI Contribution Policy Starter + Audit pack. The batch may change local source, tests,
samples, CI regeneration, and append-only documentation only.

The batch does not activate an offer, channel, listing, checkout, payment, contact route, customer
input, maintainer outreach, issue, pull request, release, account, domain, subscription, wallet, or
other external action. It does not verify identity or authority, give legal advice, detect AI use,
certify compliance, guarantee enforcement, change the candidate engine, or reactivate the parked
Revenue Lab. `$79` is a single unvalidated hypothesis.

**Why:** The three units preserve the period's 2:1 allocation while producing reusable local
evidence and a bounded revenue hypothesis without crossing identity, policy, private-input,
payment, or publication gates.

## 2026-08-13 - D-037 - R-004 prepares a portable declaration and post-SEL experiment

**Decision:** Select exactly two Patch Cabinet impact units and one Support revenue-validation
unit: a deterministic portable declaration 0.2.0 release candidate, five conservative
commit-pinned catalog pairs, and one inert post-SEL release/feedback experiment. These units may
change local source, tests, generated artifacts, CI freshness, and append-only governance only.
They do not change the candidate engine/version, historical evidence, SEL-GH-001, any active form,
release/tag/topics, payment state, or external surface.

Activation is prohibited before `2026-08-25T01:00:00Z`, and time alone is insufficient. The final
retained-row capture must exist and independently verify complete; SEL-GH-001 must remain frozen
without incident; final release diff, metadata, privacy, and exact asset digest require review;
and a new future control-task decision is mandatory. August 24 is unsafe.

Repeated candidate scans are deprioritized because recent bounded scans repeatedly stop at the
autonomous-submission policy gate. A broad new linter is rejected as duplicative of the existing
strict validators, immutable-evidence replay, generated freshness, compile, dependency, and
public-tree controls.

**Why:** This smallest local-only batch preserves cumulative 2:1 while improving reuse and
preparing a privacy-minimal measurement. Prepared artifacts are not adoption, demand,
willingness-to-pay, revenue, or production enforcement.

**Dated primary context (reviewed 2026-08-13):** GitHub repository limits and pull-request diff
limits: https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits;
AAIF-hosted AGENTS.md convention: https://agents.md/; GitHub rulesets:
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets;
OpenSSF Scorecard and badge: https://scorecard.dev/ and
https://github.com/ossf/scorecard#scorecard-badge; GitHub releases and traffic:
https://docs.github.com/en/rest/releases/releases and https://docs.github.com/en/rest/metrics/traffic.
These are context, not need, adoption, or willingness-to-pay evidence; free policy references are
alternatives rather than market validation.

## 2026-08-13 - D-038 - R-004 interoperability and inert audit extension

**Decision:** Select exactly two Patch Cabinet impact units and one Support revenue unit: a
versioned JSON Schema Draft 2020-12 structural companion and conformance corpus for declaration
schema 1; a neutral local historical policy-profile snapshot/query; and an isolated project-owned
synthetic public-policy-audit demonstration. This decision permits local source, tests, generated
artifacts, focused CI freshness, and append-only governance only.

The declaration's strict Python parser remains authoritative. No independent JSON Schema validator
is claimed, and no standard, detector, permission grant, authorization, current-policy claim, or
enforcement gate is created. The catalog query does not rank, score trust, refresh the network,
establish readiness/current permission, or feed the candidate engine. The Support demonstration
accepts only its project-owned synthetic fixture, has no network/subprocess/activation path, score,
or grade, and is not legal, security, compliance, certification, or detection work.

Real public input remains stopped until SEL-GH-001 final capture, a new prospective control
decision, and reviewed acquisition, privacy, rights/terms, retention, and provenance validation.
No checkout, payment, listing, release, issue, outreach, platform write, customer, or private input
is authorized. The existing `$79` hypothesis remains unvalidated and not offered; revenue remains
`$0.00`.

For this reset/cycle only, the sponsor authorized this cycle from the directly observed 60%
whole-account snapshot down to a hard 30% floor. Stop at 30%, any warning, or a lower sponsor
report; ordinary 40% reserve policy resumes at the next reset. The page showed August 19, 2026 at
9:33 PM, no reset available, and zero credits. No global usage is attributed to this repository,
batch, unit, agent, tool call, or action.

**Why:** The batch adds non-authorizing interoperability and evidence-limited historical utility
without changing the existing authority or execution boundaries, while preserving the cumulative
2:1 work-unit allocation.

## 2026-08-19 - D-039 - R-005 structural compatibility and one inert policy successor

**Decision:** Select exactly two Patch Cabinet impact units and one Support Agent Regression Lab
revenue unit. The Patch units are (1) two genuinely separate hosted structural-compatibility jobs
for the declaration schema using Python `jsonschema` 4.26.0 and Node Ajv 8.20.0 with exact reviewed
configurations, and (2) a machine-readable, field-by-field projection contract derived only from
the one accepted declaration and verifier-owned mappings. The Support unit is one uniquely
identified, inert direct successor in the existing `$79` AI Contribution Policy Starter + Audit
hypothesis lineage. It is a non-activated successor, not a pivot, replacement workstream, competing
offer, or second simultaneous candidate.

This local-only batch may add isolated source, tests, deterministic generated artifacts, narrowly
scoped CI preparation/freshness checks, two separate hosted compatibility adapters, and append-only
governance records. It may not activate a form, release, listing, contact route, analytics,
checkout, payment, customer-input path, account, package locally, or other external state. The
existing candidate engine, evidence, consent/profile catalogs, declaration interoperability `v1`,
SEL-GH-001 experiment/observations/channel records, the complete policy-release experiment, and
all parked Revenue Lab files are frozen. Revenue and cleared receipts remain `$0.00`; `$79` remains
one unvalidated, not-offered hypothesis.

Any future activation remains stopped until the complete SEL final capture is independently
verified, SEL stays frozen without incident, the exact final diff/privacy/digests receive review,
a new prospective control decision selects exactly one candidate and marks the other inert or
retired, separate legal/terms/privacy/merchant/payment review completes, and a new external-action
decision authorizes the exact action. Time alone never authorizes activation.

Hosted successes, if later observed, could establish only the named configured structural outcomes
on a named commit and run. They would not establish attestation, authentication, semantic
correctness, provenance, freshness, privacy, isolation, standard adoption, source truth,
permission, or production enforcement. Dependency acquisition is network-enabled; neither local
preparation nor a hosted validator result changes these claim boundaries.

**Why:** Independent validators can expose accidental schema-dialect or implementation divergence,
and an exact projection contract can make lossy transformations reviewable. Keeping the one
Support successor inside the existing hypothesis tests a clearer inert artifact without inventing
a new offer, demand, revenue, authority, or permission. The three units preserve the cumulative
2:1 impact-to-revenue allocation.

## 2026-08-19 - D-040 - Prospective R-005 source-review publication and closeout

**Decision:** The sponsor now reports 67% whole-account Usage remaining and renews the standing
mandate for this already-started R-005 publication and closeout down to a hard 35% floor. This
exception starts no new three-unit batch at or below 45% and stops immediately at 35%, any Usage
warning, or any lower sponsor report. The ordinary Usage policy resumes at reset or R-005
closeout, whichever comes first. This whole-account reading and any later delta are not attributed
to this repository, task, workstream, unit, agent, tool, test, or action; no per-unit usage is
inferred.

D-040 supersedes only D-039's local-only and no-external-mutation restriction for the exact R-005
source-review publication path. It authorizes exactly one initial local commit on
`agent/r009-policy-compatibility`, descended from the verified public-main base
`0ecc40ee1935abd88a309ac3a61134b9357db624`, and one initial push of that branch to the already
project-owned public repository; creating at most one draft pull request; and permitting only the
prepared, exact, locked hosted compatibility jobs and the repository's normal project checks.
If a concrete hosted failure occurs, at most two additional in-scope remediation commits and
pushes may update that same branch and same single draft pull request. Each remediation must be
caused by the observed failure, must not expand R-005 scope, must rerun the affected local
validation and freshness checks, and must receive a new exact whole-tree fingerprint and
independent review before push. All hosted checks must rerun on each new exact head. A third
hosted-failure cycle, any scope expansion, branch or pull-request change, or inability to retain
the controls stops this path pending a new prospective decision. The pull request may be marked
ready and squash-merged only if all required checks pass on the exact reviewed head. Afterward,
public `main` must be verified and exact publication, hosted-check, merge, and post-main receipts
appended. Any hosted failure blocks merge until an authorized remediation succeeds on a newly
reviewed exact head.

Only after both new compatibility job contexts succeed on the exact pull-request head, D-040 also
authorizes adding exactly `Python jsonschema 4.26.0 structural compatibility` and
`Node Ajv 8.20.0 structural compatibility` to `main`'s required status-check contexts. That
protection change must be additive: no existing required context or other branch protection may
be removed, bypassed, or weakened. The additive result must be verified before merge. If it cannot
be made and verified without weakening an existing control, stop rather than merge.

This authorization is inert source publication and structural validation only. It does not
authorize candidate selection, a release or tag, an active issue form, a listing, an offer, a
topic/description/analytics change, contact or outreach, customer or private input, checkout or
payment, account/merchant/tax action, or any other activation. All August 25 SEL final-capture,
frozen/no-incident, exact final diff/privacy/digest review, future exclusive-selection,
legal/terms/privacy/merchant/payment, and exact external-action gates remain. Time alone never
authorizes activation.

Hosted outcomes can establish only the named configured structural checks on the named run and
commit. They do not establish attestation, authentication, semantic correctness, provenance,
freshness, privacy, isolation, standard adoption, source truth, permission, production
enforcement, or any other boundary excluded by D-039.

**Why:** The bounded source-review path can obtain the hosted evidence that cannot be observed
locally while retaining an exact-head merge gate, a hard Usage floor, and every candidate,
commercial, privacy, and activation restriction.
