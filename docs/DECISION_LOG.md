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

## 2026-08-20 - D-041 - Required compatibility-check liveness coverage

**Decision:** Post-merge verification confirmed a required-check liveness defect: the two globally
required compatibility job contexts are absent or remain pending on documentation-only and other
unrelated pull requests when the compatibility workflow's event-level path filters prevent the
jobs from being created. Bypassing required checks, removing either context, or introducing a
separate sentinel context is rejected. The correction removes only the event-level `paths`
filters so the existing required jobs are created for every pull request and every push to
`main`.

This is a zero-unit control/reliability correction based on public-main commit
`f9e483056d1fd8539c2a3a6c08c5eb7817d3224b`. Its exact local branch is
`agent/r009-required-check-coverage`, and its write ownership is limited to these four files:
`.github/workflows/schema-compatibility.yml`,
`patch-cabinet/tests/test_declaration_compatibility.py`, `docs/CONTROL_LOG.md`, and
`docs/DECISION_LOG.md`.

The workflow must retain unfiltered `pull_request` coverage and `push` limited to branches
`[main]`; both exact compatibility job identifiers and names; root/job read-only permissions;
pinned checkout, setup-python, and setup-node actions; closed-harness preflight; exact locks and
dependency-acquisition commands; and both existing structural adapters. Registry and runner
network availability remain external hosted dependencies and are not guaranteed. Dependency
acquisition remains network-enabled. A named hosted success establishes only the configured
structural result on its exact commit/run, not attestation, authentication, semantic correctness,
provenance, path safety, privacy, isolation, permission, adoption, or production enforcement.

This correction adds no Patch or Support unit. Cumulative totals remain 26 impact / 13 revenue
units, and revenue remains `$0.00`. Every August 25, SEL final-capture, frozen/no-incident,
exclusive-selection, legal, terms, privacy, merchant, payment, and activation gate remains
unchanged; time alone is insufficient.

D-041 authorizes exactly one local commit, one push of
`agent/r009-required-check-coverage`, and at most one draft pull request for this correction. The
exact reviewed head must pass normal project checks and both compatibility jobs; required-context
read-back must remain the exact protected nine-context set. The pull request may be marked ready
and squash-merged only while those checks, protection controls, exact-head review, and scope remain
clean, followed by public-main and post-main verification. At most one same-branch/same-PR hosted-
failure remediation is allowed, limited to the same four files and requiring affected local
validation, a new exact fingerprint, and independent review before push. Any further failure,
scope expansion, branch/PR change, or control weakening stops this path pending a new prospective
decision. No receipt-only pull request or other external action is authorized.

**Why:** Required contexts must be created reliably on every event they protect. Removing only the
filters preserves the already reviewed jobs and evidence boundaries while restoring liveness
without weakening branch protection or inventing a bypass signal.

## 2026-08-20 - D-042 - Final R-005 publication receipt and direct liveness probe

**Decision:** Authorize one zero-unit, control-only final receipt for R-005 and D-041, plus a
direct documentation-only required-check liveness probe. The exact base is public-main commit
`6c7ea98c76cc99b28b2adadfdea5ac53ec06aaa6`, the exact branch is
`agent/r009-publication-receipt`, and write ownership is limited to
`docs/DECISION_LOG.md`, `docs/CONTROL_LOG.md`, and `docs/USAGE_LEDGER.md`.

The committed receipt must cover PR 17 and public-main commit
`f9e483056d1fd8539c2a3a6c08c5eb7817d3224b`, and PR 19 and public-main commit
`6c7ea98c76cc99b28b2adadfdea5ac53ec06aaa6`, including their exact reviewed heads, named hosted
runs and jobs, protection read-backs, squash merges, tree/fingerprint bindings, and post-main
checks. The receipt pull request changes only the three named documents and changes no workflow,
compatibility, code, generated, or any other path. Both exact required contexts, `Python
jsonschema 4.26.0 structural
compatibility` and `Node Ajv 8.20.0 structural compatibility`, must nevertheless be created and
pass on its exact documentation-only head. That is the direct observation required for
unrelated-path liveness. All normal checks must also pass, and main protection must remain the
same exact nine GitHub-Actions-app-bound contexts with strict status checks, admin enforcement,
linear history, conversation resolution, and force-push/deletion protections unchanged. Bypass,
context removal, app-binding substitution, or any protection weakening is rejected.

D-042 authorizes exactly one initial local commit, one initial push of
`agent/r009-publication-receipt`, and at most one draft pull request for these three documents.
The exact reviewed head must receive fresh local validation, an exact three-path raw-byte
fingerprint, independent review, every normal hosted check, both compatibility contexts, and an
unchanged protection read-back. The pull request may be marked ready and protected-squash-merged
only while those conditions remain clean, followed by public-main verification. If a concrete
hosted failure occurs, at most one additional remediation commit and one additional push may
update the same branch and same pull request, limited to the same three documents and only after
fresh validation, fingerprint, and independent review; all hosted checks must rerun on the new
exact head. Any further failure, scope expansion, branch or pull-request change, or weakened
control stops this path pending a new prospective decision.

The receipt pull request's hosted checks are its merge gate and the direct liveness evidence. Its
eventual merge is intentionally non-recursive: it will be recorded in the next ordinary control
cycle rather than creating another receipt pull request. No receipt-only continuation or other
external action is authorized here.

This control receipt adds no Patch or Support unit and no revenue. R-005 remains exactly two Patch
impact units and one Support revenue unit; cumulative totals remain 26 impact / 13 revenue units,
and revenue remains `$0.00`. The last sponsor report remains 67% whole-account Usage with the
hard 35% floor and no attribution or per-unit inference; ordinary Usage policy resumes at R-005
closeout. Every claim boundary, August 25 gate, SEL final-capture and frozen/no-incident gate,
exclusive-selection requirement, legal/terms/privacy/merchant/payment review, and future exact
activation authorization remains unchanged. Time alone is insufficient, and no candidate,
release, tag, form, offer, contact route, analytics, customer/private input, checkout, payment,
account, merchant, tax, or other activation is authorized.

Hosted successes establish only the named configured structural results on their exact commits,
runs, and jobs. They do not establish semantic correctness, provenance, path safety, privacy,
isolation, permission, adoption, availability on future runs, or production enforcement;
dependency acquisition remains network-enabled and registry/runner availability remains
external.

**Why:** A three-document pull request can directly test whether both globally required contexts
are created without a workflow or compatibility-path change, while the final receipt closes the
already authorized publication record without inventing another unit, activation, or recursive
receipt chain.

## 2026-08-20 - D-043 - Additive fast-uri security migration

**Decision:** Treat five High-severity GitHub Advisory Database records reviewed on 2026-08-20
against the hosted Node compatibility adapter's locked `fast-uri@3.1.0` transitive dependency as
urgent zero-unit security/control maintenance. The official records show first patched 3.x
versions 3.1.1 through 3.1.5 respectively, making 3.1.5 the first reviewed 3.x version that
addresses all five:
https://github.com/advisories/GHSA-q3j6-qgpj-74h6,
https://github.com/advisories/GHSA-v39h-62p7-jpjc,
https://github.com/advisories/GHSA-4c8g-83qw-93j6,
https://github.com/advisories/GHSA-v2hh-gcrm-f6hx, and
https://github.com/advisories/GHSA-7p8r-x3mc-p8w7. Preserve the published
`patch-cabinet/interop/maintainer-policy-declaration/compatibility-v1/` evidence tree byte-for-byte
and add an independent `compatibility-v2` successor. The successor retains Ajv `8.20.0`, pins
`fast-uri==3.1.5` at the exact reviewed registry URL, integrity, and shasum, and keeps the schema,
corpus, result semantics, protected job identifiers/names, least-privilege workflow controls, and
pre-install closed-harness checks unchanged except for the mechanically required v2 roots and
version identifiers. The v1 generator remains unchanged; v2 receives a separate generator and
independent CI freshness check.

The exact base is public-main commit `7ae123429837067f135b0173226537cebf6a49da`, the exact branch
is `agent/r010-fast-uri-security-migration`, and write ownership is limited to
`docs/DECISION_LOG.md`, `docs/CONTROL_LOG.md`, `docs/USAGE_LEDGER.md`, `patch-cabinet/LOG.md`,
`.github/workflows/schema-compatibility.yml`, `.github/workflows/ci.yml`,
`patch-cabinet/src/patch_cabinet/declaration_compatibility_v2.py`,
`patch-cabinet/tests/test_declaration_compatibility.py`, and the new complete
`patch-cabinet/interop/maintainer-policy-declaration/compatibility-v2/` tree. No path in
`compatibility-v1` may change. The third-party tarball and validators must not be downloaded,
installed, imported, or executed locally, and no local `node_modules` may be created.

D-043 authorizes local implementation and validation, one initial local commit and push of the
exact reviewed branch, at most one draft replacement pull request, a ready-for-review transition
after independent review, and an exact-head protected squash merge while unchanged branch
protection and all required checks pass. If a concrete hosted failure occurs, at most one
additional same-branch/same-PR remediation commit and push may address only that failure after
affected local validation, a new exact fingerprint, and independent review; every hosted check
must rerun on the new exact head. Dependabot pull request 18 may be closed as superseded, with a
link to the replacement, only after the replacement pull request exists and every check on its
exact head passes. The feature branch is retained. No force push, check bypass, protection
weakening, branch deletion, tag, release, activation, payment, contact, or unrelated external
mutation is authorized. Any material scope change, protection change, unexpected dependency
behavior, or further hosted failure stops this path pending a new prospective decision.

This correction adds no Patch or Support unit. Cumulative totals remain 26 impact / 13 revenue
units and revenue remains `$0.00`. Every August 25, SEL final-capture, frozen/no-incident,
exclusive-selection, legal, terms, privacy, merchant, payment, and activation gate remains
unchanged; time alone is insufficient. Local static and synthetic checks can establish only
deterministic artifact consistency and the configured fixed vectors. A later exact hosted success
can establish only that the locked bytes installed and the named configured structural checks
passed on its named commit/run. Neither boundary proves exploitation resistance, isolation,
semantic correctness, provenance, permission, adoption, future availability, or production
security/enforcement. Dependency acquisition remains network-enabled.

**Why:** D-017 and D-021 require published evaluator dependencies and evidence engines to migrate
by addition rather than in-place replacement. The versioned successor moves the active hosted
adapter to the first reviewed 3.x version patched for all five cited advisories while preserving
the immutable v1 record and its auditability.

## 2026-08-20 - D-044 - Dependabot alert scope for immutable compatibility-v1 evidence

**Decision:** Treat the five remaining `fast-uri@3.1.0` Dependabot alerts as exact-path execution-
scope records, not as evidence that their immutable v1 bytes were fixed. PR 21 was protected-
squash-merged at public-main commit `7dafa1b4fcaceca59912265ccf03c9ac6de785a4`; active
compatibility Python/Node acquisition and structural-adapter execution route exclusively to
`compatibility-v2`, whose locked Node inventory retains Ajv `8.20.0` and requires
`fast-uri@3.1.5`. The preserved
`patch-cabinet/interop/maintainer-policy-declaration/compatibility-v1/package-lock.json` still
records `fast-uri@3.1.0` as immutable historical evidence. Active compatibility Python/Node
acquisition and structural adapters route only to compatibility-v2. No active workflow, Python
package, or release path npm-installs, imports, or executes the compatibility-v1 Node dependency
tree or v1 structural adapters. Ordinary CI does execute the first-party standard-library v1
freshness/binding checker; that checker reads and strict-validates v1 contracts, locks, manifests,
receipts, and runner bytes as inert data without installing, importing, or executing the v1
adapters or `fast-uri`. The v2 generator separately reads exact SHA-bound v1 lock and runner bytes
as data for its exact-transform checks. This is an active project-path observation, not a claim
that a manual user or future change can never run v1. Exact-head PR and post-main compatibility,
CI, and CodeQL jobs passed, but those hosted observations establish only their named configured
outcomes on their named commits and runs. They do not prove broad production security,
exploitation resistance, isolation, semantic correctness, future availability, or production
enforcement.

After this D-044 documentation-only change is independently reviewed at an exact head, every
required check passes, it is protected-squash-merged, and every post-main check passes on the
merge commit, authorize dismissal of exactly these five alerts and no others, each only at the
exact v1 lock path above and only with GitHub's `not_used` reason:

- alert 1 / `GHSA-4c8g-83qw-93j6`;
- alert 2 / `GHSA-v2hh-gcrm-f6hx`;
- alert 3 / `GHSA-7p8r-x3mc-p8w7`;
- alert 4 / `GHSA-v39h-62p7-jpjc`; and
- alert 5 / `GHSA-q3j6-qgpj-74h6`.

Each dismissal must use this exact substantive comment, optionally prefixed only by its matching
alert/GHSA identifier:

> fast-uri@3.1.0 exists only in immutable compatibility-v1 historical evidence. Active Node
> compatibility jobs install and execute compatibility-v2 with fast-uri@3.1.5 (PR #21; code
> merge 7dafa1b4fcaceca59912265ccf03c9ac6de785a4). No active workflow, Python package, or release
> path npm-installs, imports, or executes the compatibility-v1 Node dependency tree or structural
> adapters; first-party standard-library freshness and exact-transform checks only read v1 files
> as inert bytes or data. Reopen before merging any change that causes an active project workflow,
> package, release, or automated execution path to install, import, or execute the v1 Node
> dependency tree or adapters. This not_used dismissal does not claim the v1 bytes were fixed.

The dismissals must never use `fixed` or `inaccurate`. They are auditable and reopenable, and hide
the records only from GitHub's default open-alert view; they do not remove a vulnerability from
the immutable bytes. PATCH exactly the five individually—never by bulk selection—then read back
each alert's number, state, actor, dismissal time, reason, comment, dependency path, package, and
GHSA identifier. Leave every other alert, Dependabot setting/configuration, repository setting,
and branch-protection control untouched. Before merging any future change that causes an active
project workflow, package, release, or automated execution path to install, import, or execute the
v1 Node dependency tree or adapters, reopen every affected alert and obtain a fresh security
review. This mandatory control applies before, not after, such an active path is merged.

The exact base is public-main commit `7dafa1b4fcaceca59912265ccf03c9ac6de785a4`, the exact branch
is `agent/r010-dependabot-alert-scope`, and write ownership is limited to append-only changes in
`docs/DECISION_LOG.md`, `docs/CONTROL_LOG.md`, and `docs/USAGE_LEDGER.md`. D-044 authorizes local
documentation validation; one initial local commit and push; at most one draft pull request; a
ready-for-review transition after independent exact-head review; an exact-head protected squash
merge under unchanged protection after all required checks pass; post-main check observation;
and only then the five exact dismissals and read-backs above. No remediation commit is anticipated.
Any hosted failure, source or alert mismatch, scope change, protection change, or comment/reason
constraint prevents further action and requires a new prospective decision. The feature branch
must be retained. No force push, bypass, branch deletion, tag, release, receipt pull request,
activation, payment, contact, account action, or unrelated mutation is authorized.

This is zero-unit security/control maintenance. Cumulative totals remain 26 Patch impact / 13
Support revenue units and revenue remains `$0.00`. No new Usage snapshot is taken; the last
sponsor report remains 67% whole-account Usage, the current hard floor remains 35%, and no amount
or delta is attributed to this repository, cycle, workstream, unit, agent, tool, test, or action.
Every August 25, SEL final-capture, frozen/no-incident, exclusive-selection,
legal/terms/privacy/merchant/payment, and activation gate remains unchanged. The D-044 merge and
five dismissal read-backs are intentionally non-recursive and will be recorded in the next
ordinary control cycle, not in a receipt pull request.

**Why:** The active reviewed Node compatibility dependency and adapter-execution path no longer
uses the vulnerable transitive version, but the immutable v1 evidence must remain byte-for-byte
auditable. Exact `not_used` dismissals preserve that distinction without presenting historical
bytes as remediated or weakening the mandatory reopen-before-reactivation control.

## 2026-08-20 - D-045 - Dependabot dismissal-comment API limit correction

**Decision:** Correct only D-044's impossible 745-character dismissal-comment constraint. The
authorized first alert precheck matched alert 1's exact number, `GHSA-4c8g-83qw-93j6`, `fast-uri`
package, immutable v1 lock path, `open` state, and null dismissal/fix fields. GitHub rejected its
PATCH with HTTP 422 and this exact error:
`Invalid request. Invalid property /dismissed_comment: Only 280 characters are allowed; 745 were supplied.`
Alert 1 remained open with null dismissal reason, comment, actor, time, and fix time;
alerts 2 through 5 were never attempted. Immediate read-back found all five exact alerts open and
zero dismissed alerts. Public main remained
`9a809d9ca68ae70225799dcbe871d189c12b2b34`, the local worktree remained clean, and no alert,
file, branch, pull request, protection, Dependabot configuration, setting, or other state changed
as a result of the rejected request.

D-045 supersedes only the impossible D-044 comment text and length. Every other D-044 control
remains binding: the exact five alert/GHSA/package/v1-lock mappings; individual ordered PATCHes;
the `not_used` reason and prohibition on `fixed`/`inaccurate`; exact prechecks and immediate
read-backs; active-v2/inactive-v1-Node execution boundary; ordinary standard-library freshness
checker and manual-run distinction; mandatory reopen-before-active-path merge rule; sequencing;
feature-branch retention; zero-unit accounting; and prohibition on broader mutation.

Each dismissal must instead use this exact comment, with no prefix or suffix:

> fast-uri@3.1.0 remains only in immutable compatibility-v1 evidence. Active automation
> installs/runs v2 with 3.1.5; no active path installs/imports/executes v1 Node
> dependencies/adapters. Reopen before merging any active path to v1. not_used does not mean v1
> bytes are fixed.

The normalized comment is exactly 274 characters and 274 UTF-8 bytes, within the observed
280-character API limit. It continues to state the immutable historical scope, active v2 route,
inactive v1 Node dependency/adapter path, reopen-before-active-path condition, and the boundary
that `not_used` does not mean the v1 bytes are fixed. This decision does not claim that a retry or
dismissal has occurred.

The exact base is public-main commit `9a809d9ca68ae70225799dcbe871d189c12b2b34`, the exact branch
is `agent/r010-alert-comment-limit`, and write ownership is limited to append-only changes in
`docs/DECISION_LOG.md`, `docs/CONTROL_LOG.md`, and `docs/USAGE_LEDGER.md`. Authorize local
documentation validation; one initial commit and push; at most one draft pull request; a ready
transition after independent exact-head review; an exact-head protected squash merge under
unchanged protection after every required check passes; and post-main check observation. Only
after those steps pass and the complete prestate still matches may alert 1 be retried and alerts
2 through 5 continue individually, in order, using only the exact 274-character comment above,
`state=dismissed`, and `dismissed_reason=not_used`. Before each PATCH, re-read and require the exact
number/GHSA/package/path/open/null state. Immediately after each PATCH, require the exact dismissed
state, reason, comment, non-null actor/time, null fix time, and unchanged identity. Any API
rejection, precheck mismatch, or partial read-back mismatch stops the sequence without retry,
rollback, reopen, or continuation pending a new prospective decision.

Retain the feature branch. No force push, bypass, branch deletion, tag, release, receipt pull
request, Dependabot configuration or setting change, mutation of another alert, activation,
payment, contact, account action, or unrelated mutation is authorized. This is zero-unit
security/control maintenance: totals remain 26 Patch impact / 13 Support revenue units and
revenue remains `$0.00`. No new Usage snapshot is taken; the last sponsor report remains 67%
whole-account Usage, the hard floor remains 35%, and no amount or delta is attributed to this
repository, cycle, workstream, unit, agent, tool, test, or action. Every August 25, SEL,
frozen/no-incident, exclusive-selection, legal/terms/privacy/merchant/payment, and activation gate
remains unchanged. The D-045 merge and eventual five dismissal read-backs are non-recursive and
will be recorded in the next ordinary control cycle, with no receipt pull request.

**Why:** GitHub's observed API limit makes D-044's original exact comment impossible to submit.
The shorter exact comment preserves the material scope and safety boundaries while fitting the
enforced limit; no other D-044 authority or control changes.

## 2026-08-22 - D-046 - R-011 policy-gate scan and alternatives review

**Decision:** Select exactly two Patch Cabinet impact units and one Support Agent Regression Lab
revenue-validation unit. Patch unit one is a fresh, bounded, public-read-only, fail-closed
candidate scan observed on 2026-08-22. Four public candidates were considered and zero matched the
private operator-exclusion list; the entries remain undisclosed. No candidate is ready. At exact
commits, `rclone/rclone` `64ab1ac32260238eefca3c61327f5faf1c6e106f` has current policy evidence
but no qualifying small issue; `gsd-build/gsd-2`
`33c00aaffa56e5d394bccce1c8df59fb842e84c5` explicitly allows an AI pull-request workflow but has
no qualifying small issue; `HoungDev/creator-toolkit-cli`
`7fbc4b1af8f074a921f4254f6d89225d612d7a3b` retains issue 18 but has no explicit policy; and
`openeverest/openeverest` `cc647bb5a693a50be6718973dacfbe28ba35ff25` has policy evidence but no
qualifying small issue. The reviewed rclone near-misses were assigned, had competing work, or were
sensitive. No acquisition, clone, execution, contact, candidate selection, or upstream mutation
occurred, and no readiness may be inferred.

Patch unit two adds immutable historical consent and policy-profile records for the pinned rclone
policy (`insufficiently_explicit`) and GSD-2 policy (`explicitly_allows`), a separate two-source
acquisition receipt, and regenerated catalog outputs. These records are historical policy evidence
only. They do not establish current candidate eligibility, source truth beyond the pinned bytes,
identity, authority, permission for a specific issue, contact authority, or submission authority.
The current consent index moves to an as-of date of 2026-08-22; the intentionally historical
policy-profile snapshot remains as of 2026-08-13 and labels later records `unknown`.

The Support unit is a dated, pinned, public-source alternatives review within the existing inert
AI Contribution Policy Starter + Audit hypothesis. Public examples already supply generic policy
text, so defensible differentiation would require repository-specific implementation and audit:
workflow tailoring, policy/template/CI alignment, evidence-backed gap identification, and review
and security-path validation. Revise rather than retire the hypothesis pending the final
SEL-GH-001 capture. The `$79` price and all demand remain unvalidated. No activation, contact,
release, form, listing, checkout, payment, customer, private input, account, merchant, tax,
subscription, wallet, or XLM action is authorized or claimed.

This prospective control coordinates append-only root and workstream records, the bounded Patch
evidence/catalog changes, the current-index CI date, generated catalog outputs, and focused tests.
Because a UTC source observation can fall on the next canonical date while the operator host is
still on the prior local date, it also authorizes the narrow correctness change in
`patch-cabinet/src/patch_cabinet/consent_catalog.py` and its existing consent-catalog test file to
evaluate only future-date rejection against the current UTC date. No other date, freshness, or
catalog semantics may change.
It authorizes local implementation and project-owned testing on branch
`agent/r011-policy-scan-alternatives`, based on verified public main
`7c7336ddba9d16dfc57f75481fd39ecb85d685e9`. After the exact diff and results receive independent
review, it authorizes one future draft-first guarded publication cycle: one local commit and push,
at most one draft pull request, ready transition only after exact-head review and all required
checks, and protected squash merge under unchanged protection, followed by post-main verification.
At most one same-branch, same-pull-request remediation may address a concrete hosted failure after
fresh local validation and independent review. Retain the feature branch. No force push, bypass,
branch deletion, tag, release, activation, or unrelated write is authorized. Any material scope,
source, protection, or review mismatch stops that future publication path pending a new decision.

This ordinary cycle also records the non-recursive D-045 closeout. PR 23 reviewed head
`a998e03742383d6bf694a24cbd84d0affd5df91f` and tree
`e56be17cfe5bd3f6fb5a541f144b5ff679d10e44` were protected-squash-merged as
`7c7336ddba9d16dfc57f75481fd39ecb85d685e9`, with sole parent
`9a809d9ca68ae70225799dcbe871d189c12b2b34` and the same tree. Exact-head compatibility run
`32550834192`, CI run `32550834257`, and CodeQL run `32550832464` passed their named jobs;
post-main compatibility run `32550916474`, CI run `32550916485`, and CodeQL run `32550916360`
passed their named jobs. The exact nine required contexts and protection controls remained
unchanged, and branch `agent/r010-alert-comment-limit` was retained. Alerts 1 through 5 were then
individually dismissed with reason `not_used` and D-045's exact 274-character comment at
`2026-08-22T04:10:48Z`, `2026-08-22T04:10:50Z`, `2026-08-22T04:10:51Z`,
`2026-08-22T04:10:53Z`, and `2026-08-22T04:10:54Z`, respectively, by `imyourpriest`. The final
inventory was total/open/dismissed/fixed `5/0/5/0`, and every `fixed_at` remained null. Dismissal
is not a fix; every affected alert must be reopened before merging any future active v1 Node path.

Named hosted successes prove only their configured outcomes on the exact commits, runs, and jobs.
They do not prove semantic correctness, provenance, isolation, exploitation resistance, future
availability, permission, or production enforcement. R-011 adds exactly two Patch impact units
and one Support revenue-validation unit, bringing cumulative totals to 28 Patch impact / 14
Support revenue units while preserving 2:1. Revenue and cleared receipts remain `$0.00`.

The sponsor reports that the allowance reset occurred and requests continuation without going
below 35% remaining. The exact signed-in Usage value is not independently observed, and no amount
or delta is attributed to this repository, cycle, workstream, unit, agent, tool, test, or action.
The ordinary, stricter policy still stops at 40% remaining, any warning, or any lower sponsor
report, and starts no long or multi-agent unit below 50%.

**Why:** The batch preserves fail-closed candidate selection while adding current, pinned,
non-authorizing policy evidence and testing whether a repository-specific service can offer value
beyond freely available generic policy wording. It also closes the prior alert-control cycle
without a recursive receipt pull request and preserves every SEL, privacy, legal, payment, and
activation gate.

## 2026-08-22 - D-047 - R-011 review remediation and prospective publication basis

**Decision:** Independent review found that D-046 was the first project edit and was expanded in
place before the UTC production-code correction, but the initial exact D-046 text and fingerprint
were not preserved. Static review therefore cannot audit that chronology from immutable evidence.
Do not rely on D-046's edit order as publication authority; any R-011 publication relies
prospectively on this D-047 decision instead.

D-047 binds and re-authorizes the complete current 24-path baseline at public-main base
`7c7336ddba9d16dfc57f75481fd39ecb85d685e9`, with canonical baseline fingerprint
`5b1a9539cb7339b018b1e56ea51e00847e7d51571cb0d86d393039ad6e8057a3`. The exact paths are:

- `.github/workflows/ci.yml`;
- `docs/CONTROL_LOG.md`;
- `docs/DECISION_LOG.md`;
- `docs/USAGE_LEDGER.md`;
- `patch-cabinet/LOG.md`;
- `patch-cabinet/data/consent-catalog/R011_SOURCE_ACQUISITION_RECEIPT.json`;
- `patch-cabinet/data/consent-catalog/v1/github-gsd-build-gsd-2-33c00aaffa56-66c32b399e41.json`;
- `patch-cabinet/data/consent-catalog/v1/github-rclone-rclone-64ab1ac32260-f85dafb73da4.json`;
- `patch-cabinet/data/policy-profile-catalog/v1/github-gsd-build-gsd-2-33c00aaffa56-66c32b399e41.json`;
- `patch-cabinet/data/policy-profile-catalog/v1/github-rclone-rclone-64ab1ac32260-f85dafb73da4.json`;
- `patch-cabinet/evidence/2026-08-22-no-ready-policy-gate.md`;
- `patch-cabinet/samples/consent-catalog-index.json`;
- `patch-cabinet/samples/consent-catalog-index.md`;
- `patch-cabinet/samples/policy-profile-catalog-index.json`;
- `patch-cabinet/samples/policy-profile-catalog-index.md`;
- `patch-cabinet/samples/policy-profile-catalog-snapshot.json`;
- `patch-cabinet/samples/policy-profile-catalog-snapshot.md`;
- `patch-cabinet/src/patch_cabinet/consent_catalog.py`;
- `patch-cabinet/tests/test_consent_catalog.py`;
- `patch-cabinet/tests/test_policy_profile_catalog.py`;
- `patch-cabinet/tests/test_policy_profile_snapshot.py`;
- `support-eval-lab/LOG.md`;
- `tools/check_evidence_bundles.py`; and
- `tools/tests/test_check_evidence_bundles.py`.

Within only that same 24-path set, authorize these exact review remediations: add deterministic
`build_index` tests proving UTC-today acceptance and UTC-tomorrow rejection without changing
production behavior; require every hash-allowlisted standalone evidence narrative to be present
and test deletion of each; revise only the new no-ready narrative to cite the exact reviewed
rclone issue and competing-pull-request links while narrowing negative-search claims, then update
its exact allowlist digest; and append clarifications to the control and Patch logs.

The precise acquisition boundary supersedes only D-046 and the R-011 Patch-log entry's broad
`no acquisition` wording. Public policy-source bytes for the historical catalog were acquired
through the GitHub Contents API and bound in the separate receipt. No candidate repository was
cloned or acquired for candidate work, no candidate or third-party code was executed, and no
upstream contact or mutation occurred. The scan was bounded and no examined issue advanced to
scoring; this is not proof that no qualifying issue exists.

All unit totals, claim limits, Usage controls, SEL and activation gates, and the draft-first,
exact-head guarded publication authority remain unchanged. No additional path, unit, external
write, activation, or permission is authorized.

**Why:** The remediation makes the standalone-evidence inventory fail closed, tests the UTC index
boundary directly, and replaces broad negative claims with auditable bounded evidence while using
a prospective decision whose exact pre-remediation baseline is independently fingerprinted.

## 2026-08-23 - D-048 - R-012 source-limited SEL-GH-001 final-capture closeout

**Decision:** Authorize one zero-unit, source-limited final capture and closeout for the completed
SEL-GH-001 observation window. The capture may make fresh read-only GitHub REST and GraphQL
requests using REST API version `2022-11-28`; record only the complete Popular paths response,
frozen public configuration facts, and metadata-only presence or absence of issues carrying the
`support-eval-interest` label. Do not open an entry page or issue content. Manually logged owner
entry-page previews remain zero only because no such event is logged; this is not proof of every
owner activity. D-030's frozen observation normalizer, cumulative record, generated report, and
exact-window contract remain unchanged: a source response without disclosed retained-window
bounds stays outside that normalizer, and target-path absence is `unobservable`, never zero.

Write scope is exactly these seven paths on branch `agent/r012-sel-final-capture`, based on clean
public main `cccf398804108e80bc1c15621df72ceea946c05d`:

- `docs/DECISION_LOG.md`;
- `docs/CONTROL_LOG.md`;
- `docs/USAGE_LEDGER.md`;
- `support-eval-lab/observations/sel-gh-001-final-source-check-2026-08-23.json`;
- `support-eval-lab/CHANNEL_EXPERIMENTS.md`;
- `support-eval-lab/OBSERVATION_RECORDS.md`; and
- `support-eval-lab/LOG.md`.

Authorize local validation, independent exact-diff review, and at most one later draft-first
guarded publication cycle after that review: one local commit and push, at most one draft pull
request, ready transition only after exact-head review and all required checks, protected squash
merge under unchanged protection, and post-main verification. Retain the feature branch. Any API
failure, frozen-configuration difference, uploaded release asset, missing interest label, more
than one exact target-path match, or returned interest issue fails closed before closeout. An
interest issue requires separate privacy review without copying title, body, comments, or content.

No frozen-normalizer source, test, generated sample, cumulative observation, release, tag, issue
form, topic, label, repository setting, or other GitHub object may change. No activation,
exclusive selection, listing, promotion, contact, customer or private input, identity, terms,
merchant, tax, checkout, order, payment, subscription, wallet, XLM, account, force push, bypass,
branch deletion, tag, release, or unrelated write is authorized. The August 25 timing and every
frozen/no-incident, exclusive-selection, privacy, rights/terms, provenance, legal, merchant,
payment, and external-action gate remain unchanged; time and this closeout authorize nothing.

For this R-012 closeout and at most its later guarded publication cycle only, the sponsor-reported
reset-period reading of 58% remaining and explicit request to continue toward a 15% floor
supersede the ordinary numeric Usage thresholds. The first local Codex session snapshot showed
57% remaining; that is operational telemetry, not a product-dashboard reading or per-project
measurement. Stop active work at 20% remaining, begin no long or multi-agent unit at or below 25%,
and stop immediately on a warning or lower sponsor report. The hard floor is 15%. The ordinary
40% stop and 50% long/multi-agent threshold resume automatically at the next reset. No Usage
amount or delta is attributed to this repository, closeout, workstream, unit, agent, tool, test,
or action.

This closeout is zero Patch and zero Support units. Cumulative totals remain 28 Patch impact / 14
Support revenue units, preserving 2:1, and revenue and cleared receipts remain `$0.00`.

**Why:** The declared window has ended and the final retained-source check is due, while GitHub's
available traffic response remains weaker than the frozen exact-window schema. A separate receipt
can close the channel truthfully without fabricating bounds, weakening privacy, changing the
normalizer, or implying demand or activation.

## 2026-08-23 - D-049 - R-012 independently bound review remediation

**Decision:** D-048's first-edit chronology is an operator-recorded assertion. Static review cannot
independently establish that chronology, and publication must not rely on it. Prospectively bind
the independently reviewed pre-remediation state at public-main base
`cccf398804108e80bc1c15621df72ceea946c05d`, base tree
`a15aa3ba7d919bec882320fcd9e20b7930f47636`, exact seven-path canonical fingerprint
`f84f1348416c094da65e5e5df48cd181794614bb7bf551ea4fcc449831a06111`, and final source-receipt
SHA-256 `8f0e5e474014be8d811158d21a5665ff70c353626e175dab82522fed5a1e73e5`.

The bound paths remain exactly `docs/DECISION_LOG.md`, `docs/CONTROL_LOG.md`,
`docs/USAGE_LEDGER.md`, `support-eval-lab/CHANNEL_EXPERIMENTS.md`,
`support-eval-lab/OBSERVATION_RECORDS.md`, `support-eval-lab/LOG.md`, and
`support-eval-lab/observations/sel-gh-001-final-source-check-2026-08-23.json`. Within only those
paths, authorize the minimal claim corrections required by independent review: characterize the
result as zero observed qualifying public signals and zero returned current public labeled
records, not an independent zero-interest condition; state that the metadata-only current-label
query cannot exclude a deleted issue or an issue whose label was previously removed; and retain
D-026's channel disposition only as an observed-signal insufficient result, not proof that no
qualifying issue ever existed. Do not add the reviewer's separately run extant-issue query to the
capture record because exact query timestamps were not preserved.

Authorize revalidation, independent exact-diff re-review, and the same at-most-one later
draft-first guarded publication cycle recorded by D-048. Publication relies prospectively on
D-049 and the independently bound state above, not D-048 chronology. Every zero-unit total, Usage
threshold and no-attribution rule, SEL and frozen-normalizer boundary, no-activation/no-selection
condition, privacy/payment/legal/merchant control, external-action gate, branch-retention rule,
and prohibition on unrelated or GitHub-object mutation remains unchanged. No new work unit,
source capture, API request, permission, or external action is authorized.

**Why:** The original capture supports a current observed-signal closeout, but its chronology and
current-label query do not support stronger historical absence claims. A prospectively bound
baseline and narrow corrections preserve the useful source evidence without overstating what
static review or current public metadata can prove.

## 2026-08-23 - D-050 - R-013 parks Support and pauses repeated unit selection

**Decision:** Select one zero-unit R-013 control-only park/pause update from exact public main
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`. Local edit order is operator process evidence only,
not publication evidence; do not claim that this decision's edit chronology is independently
proved. Any future publication relies only on independent exact-diff review of the complete
current nine-path scope.

Close R-012 publication non-recursively. PR 25 reviewed head
`e892f1604610cbba135880180c10341ff71fcb14` and tree
`b50997115d95a2ed061d3c48a28569a77edee395` were protected-squash-merged at public-main commit
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`, whose sole parent was
`cccf398804108e80bc1c15621df72ceea946c05d` and whose tree matched the reviewed tree. The feature
branch remains retained at the reviewed head. Post-main compatibility run `32627551168` passed
jobs `97165130122` and `97165130237`; CI run `32627551063` passed jobs `97165129837`,
`97165129902`, `97165129918`, `97165129929`, and `97165129944`; and CodeQL run `32627550787`
passed jobs `97165131213`, `97165131047`, and `97165131207`. Main protection remained unchanged:
strict app-bound required checks, admin enforcement, linear history and conversation resolution
enabled, with force pushes and deletion disabled. These named hosted observations establish only
their configured outcomes on the named commits, runs, and jobs, not broad semantic correctness,
privacy, production enforcement, future availability, or demand.

Park Support Agent Regression Lab and every `$49`, `$149`, and `$79` hypothesis. There is no active
promotion, measurement window, commercial contact route, checkout/payment route, customer work,
or activation. The preserved historical prerelease, entry, and public feedback issue form remain
technically accessible and may receive public submissions, but are not an active measured demand
channel. Existing public-data warnings and unsafe-submission/privacy response controls remain
controlling; no real or private customer input is solicited or accepted for project work. Preserve
the public prototype, reports, policy artifacts, historical prerelease, and all append-only
evidence untouched. Both policy candidates remain inert and unselected; do not delete, rewrite,
activate, select, or promote either. Parking records only that bounded evidence did not validate
demand, not that the underlying need is absent or that no buyer could exist.

Bounded official-source research retrieved on `2026-08-23` confirms that vendors provide support
model, evaluation, experiment, tracing, and self-hosting capabilities and publish substitute
products or pricing. Vendor capabilities and prices are alternatives evidence, not buyer-demand
evidence for this project. None of three possible pivots clears a buyer-evidence threshold:
privacy-local evaluation kit, cross-platform migration adapter, or support trace-governance pack.
Cross-platform migration remains `investigate` only because OpenAI's dated Evals transition/sunset
notice may create migration work; its time-sensitive details require revalidation, and qualifying
public demand is required before any design or implementation.

Pause immediate repeated Patch Cabinet scans and all new work units. Patch Cabinet remains valued,
but a future control must identify either a specific independently observed eligible issue or a
materially different revenue hypothesis with a falsifiable zero-spend validation threshold before
selecting more units. No new 2:1 batch is selected. Historical totals remain exactly 28 Patch
impact / 14 Support revenue units and revenue and cleared receipts remain `$0.00`.

The exact R-013 write scope is limited to these nine paths:

- `README.md`;
- `docs/DECISION_LOG.md`;
- `docs/CONTROL_LOG.md`;
- `docs/USAGE_LEDGER.md`;
- `docs/RESEARCH_NOTES.md`;
- `support-eval-lab/CHARTER.md`;
- `support-eval-lab/OFFER.md`;
- `support-eval-lab/README.md`; and
- `support-eval-lab/LOG.md`.

Authorize only stale-status correction, append-only control/research/Usage/Support records, and
local static validation within those paths. After independent exact-diff review, authorize at
most one later draft-first guarded publication: one commit and normal push, at most one draft pull
request, ready transition only after exact-head review and all nine required checks succeed,
protected squash merge under unchanged protection, retained feature branch, and post-main
verification. At most one same-branch, same-pull-request remediation may address a concrete
review or hosted-check failure after fresh validation and independent review. No force push,
bypass, branch deletion, release/tag/form/label/topic/settings change, activation, selection,
contact, payment, external action, or unrelated write is authorized.

For the remainder of this same reset only, the sponsor-reported 58% starting value and explicit
authorization toward a hard 15% floor remain controlling. Local session telemetry showed 45%
remaining before R-013 implementation; this is operational whole-account telemetry, not a product
dashboard or per-project measurement. Stop active work at 20%, begin no long or multi-agent unit
at or below 25%, and stop immediately on any warning or lower sponsor report. The ordinary 40%
stop and 50% long/multi-agent threshold resume at the next reset. No Usage amount or delta is
attributed to this repository, control, workstream, unit, agent, tool, test, or action.

**Why:** SEL-GH-001 closed on zero observed qualifying public signals, while the official-source
review found mature substitute capabilities but no independently observed buyer demand for the
existing or adjacent hypotheses. Parking preserves useful public evidence and prevents sunk-cost
continuation until a specific issue or materially different falsifiable hypothesis exists.

**Independent-review remediation:** Independent review bound the pre-remediation exact nine-path
fingerprint `3e93b784213afa5f414e4fcd2bd184d9612180b01c5e5dc92369795b63a44a1f` and found that the
P2 availability/privacy defect was that the preserved historical prerelease entry still links to
the technically accessible public feedback issue form. The P3 stale-status clarification is that
the frozen `CHANNEL_EXPERIMENTS.md` line `Current status: active` belongs to its dated `2026-08-09`
activation record; it is superseded by that file's appended `2026-08-23` closeout and by D-050 and
is not a current-status claim. Correct the current R-013 status surfaces to distinguish technical
accessibility from an active measured demand channel. Do not rewrite the frozen channel record or
mutate the release, entry, form, label, issues, settings, or any other external object. Existing
public-data warnings,
unsafe-submission/privacy response controls, zero-unit totals, and every privacy, payment,
activation, selection, Usage, and external-action boundary remain controlling. D-050 remains the
sole publication authority for this same-branch remediation; no additional API request or
publication action is authorized by this note.

## 2026-08-23 - D-051 - R-014 migration qualification fails buyer-demand gate

**Decision:** Select one zero-unit R-014 control-only qualification, not a workstream or artifact.
The bounded `2026-06-03` through `2026-08-23` review found three concrete current pain reports in
OpenSSF Scorecard issues [#5188](https://github.com/ossf/scorecard/issues/5188),
[#5145](https://github.com/ossf/scorecard/issues/5145), and
[#5170](https://github.com/ossf/scorecard/issues/5170). Their reconciler and adjacent mechanics
overlap the parked Linux Release Readiness Lab and establish pain, not buyer demand for a new
Cairn deliverable.

Official OpenAI sources were revalidated during the bounded review. The dated update in
[Introducing AgentKit](https://openai.com/index/introducing-agentkit/) records that Agent Builder
and Evals are scheduled to be unavailable after `2026-11-30`; the
[Agent Builder guide](https://developers.openai.com/api/docs/guides/agent-builder) and
[Evals-to-Promptfoo guide](https://developers.openai.com/cookbook/examples/evaluation/moving-from-openai-evals-to-promptfoo)
provide official product and migration guidance. These official sources establish a migration
event, not commercial demand, and require revalidation before any later action.

The researcher-reported source families included the OpenAI Developer Community, GitHub, the
public LangSmith, Braintrust, and Langfuse trackers, and buyer-intent searches across Upwork,
Freelancer, GitHub, and the OpenAI Developer Community. Research Notes records the reported query
families and their completeness and observability limits. Two distinct public user-reported
help/pain records were
observed: [cboisen's community thread](https://community.openai.com/t/deprecation-notice-evals-will-be-shut-down-on-november-30th-2026/1385537)
described an Evals-to-Promptfoo export gap, and
[che.kulhan's community thread](https://community.openai.com/t/deprecation-notice-agent-builder/1382650)
described the economics and hosting concerns of moving Agent Builder/ChatKit work to a FastAPI or
self-hosted backend. These are not official notices, endorsements, identity verification, or
buyer evidence. Neither record requested a paid pilot, quote, budgeted engagement, contract, or
bounded fixed-scope delivery. No qualifying paid, contract, or fixed-scope delivery request was
observed in the accessible results returned by this bounded review. That result does not prove
that no buyer, demand, inaccessible result, or off-platform signal exists.

The researcher's pain-level `PASS` is rejected at the independently reviewed buyer-demand level.
R-014 therefore ends `FAIL` / no-go. Evals migration remains materially distinct and
`investigate` only. Create no charter, code, fixture, prototype, offer, form, release, channel,
contact route, or Scorecard workstream. Public third-party pages were read only as untrusted
research evidence. D-014 remains controlling: no third-party repository or source artifact was
ingested into or executed by a project analyzer or product workflow, and no source repository or
file was downloaded or cloned. No outreach, contact, private input, or external mutation occurred.

D-051 authorizes no rescan. A future control decision may consider a rescan no earlier than
`2026-11-21`, unless an independently observed qualifying buyer signal or material official
timeline change warrants earlier reconsideration. The future gate requires two distinct public
accounts self-reporting separate team contexts and explicitly requesting an independent bounded
migration deliverable; those accounts and team contexts remain unverified, and at least one must
include an explicit paid-pilot, quote, or budget signal. A later pass itself authorizes only
another prospective control decision, not implementation, publication, contact, payment, or any
other external action.

R-014 uses a local content baseline at retained head
`5647bf7ad3cb36fb54b0e252e516bfe712490c74`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`. That tree matched last independently verified
public-main commit `d1ea152fc725f303ea31c30cbfb456299db47b6b` at `2026-08-23T08:55Z`.
The current shell cannot refresh GitHub because Git/GitHub socket access is blocked, the public
web cache misses, and no browser surface is available. Therefore current public main is not
claimed refreshed and no publication is attempted or authorized. The exact R-014 write scope is
`docs/DECISION_LOG.md`, `docs/CONTROL_LOG.md`, `docs/RESEARCH_NOTES.md`, and
`docs/USAGE_LEDGER.md`; only local static validation and independent exact-diff review are
authorized.

The sponsor reports a new `100%` whole-account reset start. Local session telemetry showed `97%`
after investigation and `96%` before record implementation; neither value is a signed-in Usage
page reading or project attribution. The ordinary stop remains `40%`, with no long or multi-agent
unit begun below `50%`, and immediate stop on any warning or lower sponsor report. No amount or
delta is attributed to this repository, control, workstream, unit, agent, tool, research request,
validation, or action. Historical totals remain 28 Patch impact / 14 Support revenue units;
revenue and cleared receipts remain `$0.00`.

**Why:** The official shutdown timeline and two independent migration pain records make the area
materially distinct enough to preserve for later investigation, but pain and migration help are
not evidence that two teams want an independent bounded deliverable or that any team will pay.
Stopping at the buyer-demand gate prevents another speculative artifact while preserving a
falsifiable future threshold.

## 2026-08-24 - D-052 - R-015 prospective draft-publication gate

**Decision:** Select one zero-unit R-015 control-only prospective draft-publication gate for the
already reviewed R-014 no-go. At `2026-08-24T01:27:32Z`, an authenticated GitHub connector
read-back identified account `imyourpriest` (id `49080423`), public repository
`imyourpriest/linux-agent-workbench`, default branch `main`, and public-main commit
`d1ea152fc725f303ea31c30cbfb456299db47b6b`. That commit had tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`, and a verified signature. The connector returned
zero open pull requests and no branch matching `agent/r014`. The public-main tree exactly matched
the local retained base. This supersedes only R-014's stale-hosted-state observation; it does not
change D-051's no-go, research limitations, `investigate`-only status, zero-unit result, or future
demand gate.

The branch endpoint reported `protected=true`, enforcement `everyone`, and exactly these nine
required contexts, each bound to GitHub Actions app id `15368`:

- `Python 3.12`;
- `Python 3.13`;
- `Python 3.14`;
- `Release Readiness on Windows`;
- `Generated evidence is current`;
- `Analyze (actions)`;
- `Analyze (python)`;
- `Python jsonschema 4.26.0 structural compatibility`; and
- `Node Ajv 8.20.0 structural compatibility`.

This is not a full protection read-back. The direct protection endpoint was unavailable to the
connector, shell sockets remain blocked, and the Browser skill found no browser surface. Current
admin enforcement, pull-request-review requirement, linear-history, conversation-resolution,
force-push, and deletion fields are unobserved; their previously recorded values are historical
only. The connector observation establishes only the named hosted objects and branch-endpoint
fields at the named time. Local static evidence establishes only local bytes and Git structure.
Neither proves complete protection, semantic correctness, privacy, or production enforcement.

Only after a replacement independent review of the cumulative exact four-file diff, D-052
authorizes API construction of the exact reviewed repository tree from base tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, changing only `docs/DECISION_LOG.md`,
`docs/CONTROL_LOG.md`, `docs/RESEARCH_NOTES.md`, and `docs/USAGE_LEDGER.md`; one single-parent
commit whose parent is `d1ea152fc725f303ea31c30cbfb456299db47b6b` and whose message is exactly
`Record R-014 migration buyer-demand no-go`; one previously absent remote branch named exactly
`agent/r014-migration-qualification`; and at most one draft pull request targeting `main` with
`maintainer_can_modify=false`. Any base, parent, path, byte, branch-presence, target, or draft-state
difference fails closed.

After creation, the root operator must recompute and verify the remote four-file bytes, resulting
tree, sole parent, exact diff scope, pull-request base and head, and hosted checks. D-052 does not
authorize a ready transition or merge. It also forbids protection or settings changes,
admin/bypass/force use, force push, branch deletion, release, tag, form, issue, label, contact,
payment, activation, and every other external mutation. Even if every hosted check passes, ready
or merge remains unauthorized while the full protection fields are unobserved. A later
prospective control decision, after a full fresh protection read-back, is required.

At most one same-branch remediation is permitted solely for a concrete independent-review or
hosted-check failure, after local revalidation and a new independent exact-diff review; otherwise
no remediation is authorized. It must use a normal non-force update to the same branch and draft
pull request, retain the exact four-path scope and all prohibitions, and cannot authorize ready or
merge.

The sponsor now reports `88%` whole-account Usage remaining and authorizes continuation to the
ordinary `40%` stop. Begin no long or multi-agent unit below `50%`; stop at `40%`, any warning, or
any lower sponsor report. No amount or delta is attributed to this repository, control,
workstream, unit, agent, connector, tool, validation, or action. R-015 adds zero Patch and zero
Support units. Historical totals remain 28 Patch impact / 14 Support revenue units, and revenue
and cleared receipts remain `$0.00`.

**Why:** The refreshed connector evidence re-establishes exact base-tree and remote-branch
preconditions for a draft-only record without overstating the incomplete protection observation.
Separating draft construction from ready/merge keeps the unobserved hosted controls fail-closed.

**Independent-review remediation:** This remediation supersedes any less-specific D-052
transaction wording. A final replacement independent review of the complete cumulative four-file
diff is mandatory. Let `F` be the 64-character lowercase SHA-256 returned by that final review
using this exact algorithm: case-sensitive ordinal sort of the four exact repository-relative
paths; for each path, append its UTF-8 path bytes, one NUL byte, the raw file bytes, and one NUL
byte; SHA-256 the resulting byte stream. Only the exact four file bytes matching `F` may be
published.

The GitHub API commit must use connector/authenticated author and committer defaults only. Do not
provide or override author, committer, name, email, signature, date, or any other identity or
attribution field. The commit message remains exactly `Record R-014 migration buyer-demand
no-go`. The pull-request title is exactly `Record R-014 migration buyer-demand no-go`. Its body is
the following canonical text. Encode it as UTF-8 with LF-only line endings and no terminal
newline; replace `<F>` at transaction time with exactly the final 64-character lowercase review
fingerprint and make no other substitution or change.

```text
## Summary

- Record the bounded R-014 OpenAI Evals / Agent Builder migration qualification.
- Keep the hypothesis `investigate`-only after no qualifying paid, contract, or fixed-scope delivery request was observed in accessible returned results.
- Add D-052's draft-only publication gate.

## Evidence boundaries

- Search completeness is not independently replayable; inaccessible and off-platform demand remain unknown.
- This is an append-only, documentation-only, zero-unit record. Revenue and cleared receipts remain `$0.00`.
- Full branch-protection fields remain unobserved. This pull request must remain draft; ready transition and merge are unauthorized.

## Validation

- Base: `d1ea152fc725f303ea31c30cbfb456299db47b6b`.
- Changed paths: exactly `docs/CONTROL_LOG.md`, `docs/DECISION_LOG.md`, `docs/RESEARCH_NOTES.md`, and `docs/USAGE_LEDGER.md`.
- Canonical fingerprint: `<F>`.
- Append-only prefix and `git diff --check` passed locally.

No project or third-party code was executed for this documentation-only publication.
```

After final replacement review and immediately before any write, require an authenticated
connector reread of login and id, repository identity and visibility, default branch, main SHA,
main tree, sole parent, the partial branch-protection observation (`protected=true`, enforcement
`everyone`, and the exact nine contexts listed above, each bound to app id `15368`), zero open
pull requests, and exact absence of `agent/r014-migration-qualification`. Any mismatch,
unavailable field, ambiguity, or changed main invalidates D-052's authority and stops the
transaction.

If and only if that reread passes, perform these external operations in order:

1. Create the exact four reviewed blobs and verify each returned SHA equals the corresponding
   local Git blob SHA.
2. Create one tree from exact base tree `e22fd1f125be2b8afe7b8296ddac6c2e1d505e02` with only
   those four blob replacements, and verify the returned tree.
3. Create one commit with that exact tree, sole parent
   `d1ea152fc725f303ea31c30cbfb456299db47b6b`, exact message, and default authenticated identity,
   with no additional parent; fetch/read it back and verify every bound field.
4. Only after commit verification, create the exact previously absent branch
   `agent/r014-migration-qualification` at the verified commit, then read it back and verify it.
5. Create one exact-title, exact-body draft pull request targeting `main` with
   `maintainer_can_modify=false`, then read back and verify title, canonical body bytes, draft
   state, base, head, and maintainer-modification field.

At any partial, unavailable, failed, or ambiguous outcome, stop all writes immediately and permit
read-only reconciliation only. No retry, resume, update, deletion, cleanup, pull-request creation
after an earlier ambiguous stage, or other mutation is authorized. A new prospective control
decision after exact state capture and review is required. Dangling blobs, tree, or commit may
remain; do not imply or attempt cleanup.

For clarity, except for the exact initial construction above and the separately conditioned
at-most-one same-branch remediation already described by D-052, every other external mutation is
forbidden. That conditioned remediation does not cover an initial or partial transaction retry,
resume, cleanup, or any ambiguous outcome. It still requires its new exact-diff review and all
previous limits; it cannot force push, change identity metadata, alter the canonical title/body,
or authorize ready or merge.

**Second independent-review remediation:** This remediation supersedes the earlier canonical body
and all standing D-052 remediation authority, including the at-most-one same-branch remediation
described at lines 1395-1399 and 1480-1485 and the corresponding Session 050 wording. The earlier
canonical body must not be used. The replacement pull-request body is the following full
canonical text. Encode it as UTF-8 with LF-only line endings and no terminal newline; replace
`<F>` only with the final 64-character lowercase fingerprint from the mandatory final replacement
independent review, and make no other substitution or change.

```text
## Summary

- Record the bounded R-014 OpenAI Evals / Agent Builder migration qualification.
- Keep the hypothesis `investigate`-only after no qualifying paid, contract, or fixed-scope delivery request was observed in accessible returned results.
- Add D-052's draft-only publication gate.

## Evidence boundaries

- Search completeness is not independently replayable; inaccessible and off-platform demand remain unknown.
- This is an append-only, documentation-only, zero-unit record. Revenue and cleared receipts remain `$0.00`.
- Full branch-protection fields remain unobserved. This pull request must remain draft; ready transition and merge are unauthorized.

## Validation

- Base: `d1ea152fc725f303ea31c30cbfb456299db47b6b`.
- Changed paths: exactly `docs/CONTROL_LOG.md`, `docs/DECISION_LOG.md`, `docs/RESEARCH_NOTES.md`, and `docs/USAGE_LEDGER.md`.
- Canonical fingerprint: `<F>`.
- Append-only prefix and `git diff --check` passed locally.

No project or third-party code was executed during local record preparation or static validation. Draft publication is expected to trigger hosted workflows that may execute project and pinned third-party code; their results establish only the named configured outcomes on the published commit, not production enforcement.
```

D-052's entire at-most-one same-branch remediation authorization is withdrawn and superseded. No
remediation commit, branch update, pull-request title or body update, retry, resume, cleanup, or
other post-initial-construction write is authorized. Any independent-review finding,
hosted-check failure, stale fingerprint or body, changed byte, base, or head, partial or ambiguous
result, or desired correction requires an immediate stop, read-only reconciliation, and a new
prospective control decision after exact state capture and independent review.

Only the exact initial five-stage construction remains authorized, subject to every pre-write,
identity, byte, tree, parent, branch, draft, and read-back condition above. The initial body value
of `F` remains bound to the exact commit created during that construction; no later tree/body or
fingerprint/body mismatch is permitted. Every mutation other than that exact initial five-stage
construction is forbidden. Ready transition and merge remain unauthorized.

## 2026-08-24 - D-053 - R-016 terminates unexecuted draft transaction

**Decision:** Select one zero-unit R-016 local no-mutation closeout. Final independent review
approved only exact cumulative fingerprint
`18e52539e52a5d5a8be52a5ddf040664162bd700a324af8a8d72369c3133f8e6` for D-052's initial
five-stage transaction. The canonical pull-request body after substituting that fingerprint had
SHA-256 `a636f7a4df66bafcad5768817233abc392a714e8fa51c2553fca06ca3841b177`.

At `2026-08-24T01:55:50Z`, D-052's mandatory immediate pre-write authenticated connector reread
passed. It returned owner `imyourpriest` (id `49080423`), public repository
`imyourpriest/linux-agent-workbench`, default branch `main`, exact main
`d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`, `protected=true`, enforcement `everyone`, zero open
pull requests, exact absence of target branch `agent/r014-migration-qualification`, and the exact
nine contexts previously enumerated by D-052, each bound to GitHub Actions app id `15368`.

The very first external operation, the first `github_create_blob`, was rejected before dispatch by
the runtime/tool approval boundary with exact error `MCP tool call requires approval, but approval
policy is never`. It returned no blob SHA, and the transaction write ledger remained empty. This
is a reported pre-dispatch approval rejection, not a GitHub API rejection and not evidence that
GitHub received or rejected a request.

D-052 therefore required immediate stop. No second blob call, tree, commit, branch, pull request,
retry, cleanup, or other write was attempted. D-052's initial authority is exhausted and
terminated. Its canonical pull-request body is an unexecuted historical transaction contract,
not public metadata.

At `2026-08-24T01:56:14Z`, permitted read-only reconciliation found main, tree, and sole parent
unchanged; zero open pull requests; no matching `agent/r014-migration-qualification` branch with
no cursor remainder; and no commit matching exact planned message
`Record R-014 migration buyer-demand no-go`. This establishes unchanged reachable state only.
Dangling-object absence is not independently enumerable. The narrower evidence is that the tool
reported a pre-dispatch rejection and returned no object id; do not infer total object absence
beyond that evidence.

D-053 authorizes no retry, resume, local commit, branch, pull request, cleanup, publication,
ready transition, merge, or other external mutation. A wholly new prospective control decision
after changed execution capability, fresh exact state capture, and independent review would be
required. The current approval policy prevented the attempted `github_create_blob` from
dispatching in this environment; no broader connector-write capability claim is made. Shell and
browser routes remain unavailable. Preserve the uncommitted local staging diff.

No new project research or work unit is selected. D-050 and D-051's cooldown and no-go remain
controlling. The sponsor's last report remains `88%` whole-account Usage with the ordinary `40%`
stop. Local operational telemetry at `2026-08-24T01:56:14Z` showed `77%` remaining. These values
are whole-account observations only; no amount or delta is attributed to this repository,
control, workstream, unit, agent, connector, tool, validation, or action. Begin no long or
multi-agent unit below `50%`.

R-016 adds zero Patch and zero Support units. Historical totals remain 28 Patch impact / 14
Support revenue units, and revenue and cleared receipts remain `$0.00`.

**Why:** The first write never crossed the runtime approval boundary, and D-052 deliberately
provided no retry or partial-transaction continuation authority. Recording the exact stop and
reachable-state reconciliation preserves the reviewed local evidence without fabricating a
GitHub write, cleanup, publication, or broader absence claim.

## 2026-08-31 - D-054 - R-017 guarded publication recovery

**Decision:** Select one zero-unit R-017 prospective control for one exact guarded publication
cycle of the retained R-014 four-file no-go record. This is a wholly new decision after changed
execution capability, fresh state capture, and required independent review; it is not a retry or
resumption of D-052. D-053 remains the accurate closeout of D-052. The original MCP
`github_create_blob` was historically rejected before dispatch because the approval policy was
`never`; the approval policy remains `never`, and that route was not retried. The newly observed
route is authenticated shell GitHub/Git access over the network.

Fresh authenticated capture from `2026-09-01T00:42:45.0712440Z` through
`2026-09-01T00:42:49.4924053Z` identified user `imyourpriest` id `49080423`, public repository
`imyourpriest/linux-agent-workbench`, and default branch `main`. Main was
`d1ea152fc725f303ea31c30cbfb456299db47b6b`, with tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`, and a verified signature. The repository returned
zero open pull requests, exact target branch `agent/r014-migration-qualification` was absent,
squash merge was allowed, and automatic branch deletion was false.

Classic protection returned `protected=true`, strict status checks, required pull requests with
zero required approvals, dismissal of stale approvals false, code-owner review false, last-push
approval false, admin enforcement true, linear history true, conversation resolution true, force
push false, deletion false, and no restrictions. The exact required contexts, each bound to
GitHub Actions app id `15368`, were `Python 3.12`, `Python 3.13`, `Python 3.14`,
`Release Readiness on Windows`, `Generated evidence is current`, `Analyze (actions)`,
`Analyze (python)`, `Python jsonschema 4.26.0 structural compatibility`, and
`Node Ajv 8.20.0 structural compatibility`. The effective branch-rules endpoint and both the
repository and parent ruleset listings returned empty. This establishes only that no active or
applicable ruleset rules were returned under the authenticated view; it neither negates classic
protection nor proves policy outside the returned visibility.

A normal authenticated `git push --dry-run` proposed creation of the exact target branch and
exited zero. A subsequent read-only check still found that branch absent. This demonstrates route
negotiation only: it was not a dispatched write and does not prove the real transaction will
succeed.

Before this D-054 append, local static inspection found HEAD
`5647bf7ad3cb36fb54b0e252e516bfe712490c74`, whose tree matched the public-main tree, exactly the
four modified paths named below, no untracked files, canonical fingerprint
`33170c1630e79987adf030165ee3f72ae7df81517edba7740a5d1a942422d485`, 647 additions and zero
deletions, exact HEAD prefixes, LF-only files, and a passing `git diff --check`. These are local
static observations only, not remote state, hosted-test results, or production enforcement.

D-050 and D-051's cooldown and no-go remain controlling. Select no new research or work unit and
do not activate an offer, contact anyone, accept input or payment, or create any channel or form.
The sponsor reported a reset. Local operational telemetry at `2026-09-01T00:38:54.291Z` showed
`94%` remaining and at `2026-09-01T00:44:00.059Z` showed `83%` remaining. These are whole-account
observations only, with no amount or delta attributed to this repository, control, workstream,
unit, agent, tool, or action. Stop at the ordinary `40%`, begin no long or multi-agent unit below
`50%`, and stop immediately on a warning or lower sponsor report. R-017 adds zero Patch and zero
Support units; historical totals remain 28/14 and revenue and cleared receipts remain `$0.00`.

Before any publication write, a final independent security review must approve the complete
cumulative exact four-file bytes. Define `F` as lowercase SHA-256 over the four repo-relative paths
sorted by case-sensitive ordinal order, feeding for each path its UTF-8 path, one NUL byte, the raw
file bytes, and one NUL byte. Only bytes matching that final `F` may be published. The exact changed
paths are `docs/CONTROL_LOG.md`, `docs/DECISION_LOG.md`, `docs/RESEARCH_NOTES.md`, and
`docs/USAGE_LEDGER.md`. The base must remain main
`d1ea152fc725f303ea31c30cbfb456299db47b6b` and tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`. The branch is exactly
`agent/r014-migration-qualification`; the commit message and pull-request title are exactly
`Record R-014 migration buyer-demand no-go`; the pull-request base is `main`, `draft=true`, and
`maintainer_can_modify=false`. Git Database API commit creation must use authenticated defaults
only, without any author, committer, name, email, date, identity, signature, or attribution
override.

The pull-request body is the following canonical text. Encode it as UTF-8 with LF-only line
endings and no terminal newline. Replace `<F>` only with the final 64-character lowercase
fingerprint; make no other substitution or byte change. Before creating the pull request, compute
and retain its exact SHA-256 digest for read-back comparison.

```text
## Summary

- Record the bounded R-014 OpenAI Evals / Agent Builder migration qualification.
- Keep the hypothesis `investigate`-only after no qualifying paid, contract, or fixed-scope delivery request was observed in accessible returned results.
- Record D-053's pre-dispatch stop and D-054's newly reviewed guarded publication recovery.

## Evidence boundaries

- Search completeness is not independently replayable; inaccessible and off-platform demand remain unknown.
- This is an append-only, documentation-only, zero-unit record. Revenue and cleared receipts remain `$0.00`.
- Full classic branch protection was freshly observed before publication; empty rules/rulesets responses establish only that no active/applicable ruleset rules were returned under the authenticated view.
- Hosted results establish only named configured outcomes on exact commits, not broad semantic correctness, privacy, or production enforcement.

## Validation

- Base: `d1ea152fc725f303ea31c30cbfb456299db47b6b`.
- Changed paths: exactly `docs/CONTROL_LOG.md`, `docs/DECISION_LOG.md`, `docs/RESEARCH_NOTES.md`, and `docs/USAGE_LEDGER.md`.
- Canonical fingerprint: `<F>`.
- Append-only prefix and `git diff --check` passed locally.

No project or third-party code was executed during local record preparation or static validation. Draft publication is expected to trigger hosted workflows that may execute project and pinned third-party code; their results establish only the named configured outcomes on the published commit, not production enforcement.
```

After the final review and a last read-only equality check of every bound local and remote field,
D-054 authorizes exactly one five-stage shell `gh api` Git Database transaction, in this order:

1. Create exactly four blobs from the reviewed local file bytes and verify each returned SHA
   against the corresponding locally computed Git blob SHA before continuing.
2. Create and read back one tree from exact base tree
   `e22fd1f125be2b8afe7b8296ddac6c2e1d505e02` with only those four blob replacements; verify its
   entries and full tree against the reviewed local tree before continuing.
3. Create one commit with that exact tree, sole parent
   `d1ea152fc725f303ea31c30cbfb456299db47b6b`, exact message, and authenticated identity defaults;
   read it back and verify tree, sole parent, message, and identity before continuing.
4. Create previously absent ref `refs/heads/agent/r014-migration-qualification` at that exact
   verified commit, then read it back and verify exact target before continuing.
5. Create one pull request with the exact canonical title and body, base `main`, exact head branch,
   `draft=true`, and `maintainer_can_modify=false`; read it back and verify every field and the
   canonical body digest.

Every construction call must use shell `gh api`; each stage must be completely verified before
the next. Any failure, ambiguity, partial result, unavailable field, or mismatch stops all mutation
and permits read-only reconciliation only. No retry, resume, cleanup, remediation, update, or
deletion is authorized.

After draft creation, verify the remote bytes and recomputed `F`, tree, sole parent, exact diff
paths, pull-request metadata and body digest, target branch, and exact head. Obtain a second
independent security review of that exact remote head before ready. Require all nine exact
app-`15368` checks to reach success on that head, with no failure or pending result. Query both
check runs and commit statuses, preserving duplicates so a successful duplicate name cannot hide
a failing or pending result. These hosted outcomes establish only the named configured results.

Immediately before ready and again immediately before merge, reread and match the exact head,
base, title, canonical body digest, `maintainer_can_modify=false`, unchanged main/base, full classic
protection, the narrowly described empty effective-rules and ruleset surfaces, zero unresolved
conversations, and all check-run and commit-status results. Mark ready only with `gh pr ready`, then
read back `isDraft=false` and every other metadata field without drift. Repeat every gate and run
exactly one `gh pr merge --squash --match-head-commit <exact-head>` with no `--admin`, `--auto`,
`--delete-branch`, force, or bypass option. Bind the merge subject exactly to
`Record R-014 migration buyer-demand no-go` and the merge body exactly to
`Protected squash merge of the exact reviewed R-014 documentation record.`

Afterward, verify the pull request is merged by authenticated actor `imyourpriest` id `49080423`;
verify the resulting main commit has sole parent the old main and tree equal to the reviewed pull-
request tree; verify the target branch remains at the exact reviewed head; verify all nine checks
on resulting main; and verify full classic protection and the narrowly described rules surfaces
remain unchanged. Omitting `--admin` together with the protection and read-backs is strong
operational evidence, not cryptographic proof that no bypass occurred.

There is no remediation authority. Any stale state, mismatch, failure, unavailable field, or
ambiguous result stops all mutation and requires a new prospective control after fresh capture
and review. Settings or protection changes, admin or bypass use, force, branch deletion, release,
tag, form, issue, label, contact, payment, activation, and unrelated mutations are forbidden.
D-054 authorizes the complete exact draft-to-ready-to-protected-squash-merge cycle so that no
recursive receipt pull request is needed. Final receipts are appended locally in the next ordinary
zero-unit control cycle and are not themselves authorized for publication by D-054.

**Why:** Changed execution capability makes a newly reviewed guarded route possible while the
previous transaction remains correctly terminated. Exact byte, state, review, protection, check,
and read-back gates permit one narrow publication cycle without reviving old authority or creating
standing remediation power.

## 2026-08-31 - D-055 - R-018 security-review correction and replacement authority

**Decision:** Select one zero-unit R-018 local correction and new prospective guarded-publication
control. The independent security review placed D-054 fingerprint
`4d29edb31c666bdcaebbf7c235f37a1860b3af304fe4f69ef26a17b9219f175c` on HOLD for one P3
audit-provenance error and reported no P0-P2 finding. It independently confirmed the prior exact
scope, HEAD-prefix, LF-only, and `git diff --check` results, canonical body digest
`33a1844bbb5a49022608ba65dcfca0c277844e1ab9e454d9df4e65bbace23420`, the four recorded Git blob
SHAs, and the captured public state, but it did not approve publication.

The P3 finding is narrow but controlling: D-054 and Session 052 implied separate repository and
parent ruleset listings. The actual evidence was exactly one effective branch-rules request that
returned `[]`, and one combined repository rulesets request with `includes_parents=true` that
returned `[]`. There was no separately observed parent listing. The supported claim is only that
no active or applicable effective rules and no repository or inherited rulesets were returned
under those two authenticated views. D-055 supersedes the misleading split-listing wording in
D-054 and Session 052 everywhere that wording could control a publication gate or later claim;
the historical bytes remain unchanged.

D-054's mandatory review therefore failed before its authority activated, and it caused no GitHub
write. D-055 is the new prospective control required after that finding. It supersedes and
replaces all D-054 publication authority; in any conflict D-055 controls. It does not supersede
D-053's transaction history or D-050/D-051's no-go and cooldown.

Fresh replacement capture from `2026-09-01T00:57:17.7861054Z` through
`2026-09-01T00:57:20.9320160Z` found unchanged main
`d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, and sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`; classic protection remained enabled with strict
status checks, admin enforcement, linear history, and conversation resolution true, and force
push and deletion false. The same exact nine required contexts were returned, each bound to app
id `15368`: `Python 3.12`, `Python 3.13`, `Python 3.14`,
`Release Readiness on Windows`, `Generated evidence is current`, `Analyze (actions)`,
`Analyze (python)`, `Python jsonschema 4.26.0 structural compatibility`, and
`Node Ajv 8.20.0 structural compatibility`. Exactly one effective-rules request returned one
response with zero results (`[]`), and exactly one combined repository rulesets request with
`includes_parents=true` returned one response with zero results (`[]`). Zero open pull requests
were present and exact target ref `refs/heads/agent/r014-migration-qualification` remained absent.

After a new final independent security review approves the new cumulative exact four-file
fingerprint `F`, D-055 reissues exactly one guarded full-cycle transaction. It incorporates
D-054's exact changed paths, base main and tree, branch, commit message, pull-request title,
canonical body template, authenticated-default commit identity, five-stage shell `gh api` order
and stage-by-stage verification, second independent review of the exact remote head, nine exact
app-`15368` success gates across check runs and commit statuses, ready transition, exact-head
non-admin protected squash merge with exact subject and body, retained-branch and post-main
read-backs, no-remediation rule, forbidden actions, and nonrecursive local final-receipt semantics.
Those incorporated requirements have the same exact values and constraints stated in D-054 except
for the corrected rules/ruleset evidence and gates below. D-054's canonical pull-request body text
itself is accurate and is reused byte-for-byte, with only `<F>` replaced by the new final
64-character lowercase fingerprint. Its substituted UTF-8/LF/no-terminal-newline SHA-256 must be
computed and bound before the first write and verified on read-back.

Every pre-write, pre-ready, pre-merge, and post-merge rules/ruleset gate is corrected and replaced
as follows: perform exactly one authenticated effective branch-rules request and require its full
result to equal empty array `[]`; perform exactly one authenticated combined repository rulesets
request with `includes_parents=true` and require its full result to equal empty array `[]`. Do not
describe, require, or infer a separate parent ruleset listing. These empty results establish only
that no active or applicable effective rules and no repository or inherited rulesets were returned
under those two authenticated views; they do not negate classic protection or prove policy beyond
returned visibility. All classic-protection, main, head, pull-request, conversation, check, actor,
tree, parent, branch-retention, and exact-byte gates incorporated from D-054 remain mandatory.

No publication mutation may begin until the replacement review approves exact `F`, its canonical
body digest, and every cumulative byte. Any review finding, stale state, mismatch, failure,
ambiguity, unavailable field, or partial result stops all mutation and requires another new
prospective control after fresh capture and review. No retry, resume, cleanup, remediation, update,
or deletion is authorized. Every settings/protection change, admin or bypass use, force, branch
deletion, release, tag, form, issue, label, contact, payment, activation, and unrelated mutation
forbidden by D-054 remains forbidden.

No new research or work unit is selected; D-050/D-051 remain controlling. No offer, channel,
activation, contact, private input, payment, or other external action occurred. Local operational
telemetry at `2026-09-01T00:56:47.449Z` showed `60%` whole-account Usage remaining. No amount or
delta is attributed to this repository, control, workstream, unit, agent, review, tool, or action.
Stop at the ordinary `40%`, begin no long or multi-agent unit below `50%`, and stop on any warning
or lower sponsor report. R-018 adds zero Patch and zero Support units; historical totals remain
28/14 and revenue and cleared receipts remain `$0.00`.

**Why:** Append-only correction preserves the failed review and its provenance while replacing
the inaccurate ruleset topology with the exact observed request surfaces. A newly fingerprinted
and independently reviewed control is required before the narrowly bounded publication cycle can
activate.

## 2026-08-31 - D-056 - R-019 partial-transaction stop and replacement authority

**Decision:** Record the fail-closed stop of D-055 and select one zero-unit R-019 prospective
replacement control. Independent security review approved D-055's exact fingerprint
`737cd12334028d7ed61c6c841b6d2577d50b57ef715fa378922fb493f257e252` and canonical body digest
`238e78f76ab8965debce3de1a8edda26c2ad7481502e38187b6347c11ef89345`, with no P0-P3 finding.
The mandatory pre-write capture from `2026-09-01T01:03:09.3718190Z` through
`2026-09-01T01:03:14.6644126Z` passed every bound local and remote field, including fingerprint,
body, main, tree, pull-request and ref absence, protection, the corrected rules surfaces, and the
dry-run. That capture caused no mutation.

The first actual write created the `docs/CONTROL_LOG.md` blob and returned its exact expected Git
SHA `c75aa75b72168285393f44015b0200fcccf58834`. Its GET read-back returned before the local byte
comparison. The validator then stopped on exact PowerShell error `Cannot convert to the ByRef-like
type "System.ReadOnlySpan`1[System.Byte]". ByRef-like types are not supported in PowerShell.` while
attempting `[MemoryExtensions]::SequenceEqual`. This occurred before the loop could issue the
second blob call. Stop was immediate: no later blob, tree, commit, ref, or pull-request call was
issued, and no retry or cleanup was attempted.

Read-only reconciliation at `2026-09-01T01:04:03.7144793Z` confirmed blob
`c75aa75b72168285393f44015b0200fcccf58834` had identical local and remote size `141949` bytes,
byte equality true using supported `[System.Linq.Enumerable]::SequenceEqual[byte]`, and identical
raw SHA-256 `8ed87a161d4c915ad820e9137fec46cefd620b93f2675f45c34eec161929bf39`.
Main remained `d1ea152fc725f303ea31c30cbfb456299db47b6b`, with zero open pull requests and the target ref
absent. This establishes one known dangling blob and the observed execution path only; it does not
establish absence of every unreachable object. The dangling blob must never be cleaned up.

D-055 authority is exhausted. D-056 is a wholly new prospective control, not a retry or resume.
It supersedes and replaces all D-055 publication authority, and in conflict D-056 controls, while
preserving D-055, D-054, and D-053 history and D-050/D-051's no-go and cooldown.

Fresh capture from `2026-09-01T01:04:51.2539896Z` through
`2026-09-01T01:04:54.1037613Z` found unchanged main
`d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, and sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`; classic protection remained protected and strict,
with admin enforcement, linear history, and conversation resolution true and force push and
deletion false. The same nine required contexts remained bound to app id `15368`. Exactly one
effective-rules request returned `[]`, and exactly one combined repository rulesets request with
`includes_parents=true` returned `[]`. Zero open pull requests and exact target-ref absence were
reconfirmed; the known dangling blob remained.

Only after a brand-new final independent review approves the new cumulative exact four-file
fingerprint `F` and its substituted canonical body digest, D-056 reissues by reference the exact
D-055/D-054 guarded full-cycle constraints: exact paths, base and tree, branch, title and message,
canonical body with only new `F` substitution, authenticated-default identity, corrected two
rules surfaces, five-stage shell `gh api` transaction, second exact-remote-head review, nine exact
app-`15368` checks across check runs and statuses, ready transition, exact-head non-admin protected
squash merge with exact subject and body, retained-branch and post-main read-backs, local-only final
receipt, all forbidden actions, and no remediation. Every incorporated exact value and evidence
boundary remains unchanged except the new reviewed bytes, `F`, body digest, and per-file bindings
required below.

This must be a wholly new four-blob transaction using the newly appended exact file bytes. The
stale `c75aa75b72168285393f44015b0200fcccf58834` object must not be reused as the CONTROL blob and
must not be deleted or cleaned. Before the first write, prove the corrected read-back validator on
non-mutating current local data. For each exact new file, bind its precomputed Git blob SHA, raw
byte length, and raw SHA-256. After each blob POST, verify the returned SHA, decode the GET content,
and compare raw length and SHA-256 only, or additionally use supported
`[System.Linq.Enumerable]::SequenceEqual[byte]`. Never construct `ReadOnlySpan` or call
`MemoryExtensions.SequenceEqual`. Fully verify each blob before issuing the next stage.

Any review finding, stale state, mismatch, failure, ambiguity, unavailable field, or partial
result again stops all mutation and requires a new prospective control after fresh capture and
review. No retry, resume, cleanup, remediation, update, or deletion is authorized.

No new research or work unit is selected and no activation, contact, private input, payment, or
other unrelated action occurred. This long cycle began above `50%`; local telemetry at
`2026-09-01T01:04:17.768Z` showed `47%` remaining. This is whole-account telemetry with no amount
or delta attributed to this repository, control, workstream, unit, agent, tool, or action. Start no
new long or multi-agent unit below `50%`, stop at `40%`, and stop on any warning or lower sponsor
report. R-019 adds zero Patch and zero Support units; totals remain 28/14 and revenue and cleared
receipts remain `$0.00`.

**Why:** The first blob was created, but its mandated local verification path failed before the
second write. Immediate stop and a new fingerprinted control preserve fail-closed semantics while
correcting the validator without retrying or concealing the known dangling object.

## 2026-08-31 - D-057 - R-020 Usage-window correction and replacement authority

**Decision:** Correct the Usage-window audit trail and select one zero-unit R-020 prospective
replacement publication control. The sponsor explicitly clarified that the protected `40%` floor
applies to the weekly limit and reported `64%` weekly remaining at correction time. Prior control
reasoning had mistaken the five-hour window for the weekly window.

Exact local telemetry at `2026-09-01T01:14:35.867Z` reported
`primary.window_minutes=300`, primary `used=72` / `remaining=28`, and
`secondary.window_minutes=10080`, secondary `used=37` / `remaining=63`. Reset fields were also
present. This is operational telemetry, not signed dashboard evidence or project attribution. The
one-point difference between the sponsor's `64%` weekly report and secondary telemetry's `63%` is
a timing difference, not evidence of attribution.

Official OpenAI documentation fetched `2026-08-31` from
https://developers.openai.com/codex/pricing states that local-message estimates are per five-hour
window and that additional weekly limits may apply. This supports the window distinction; it does
not establish exact account usage.

D-057 supersedes every prior statement that treated locally parsed `primary` percentages as
weekly or whole-account floor values. In particular, R-014's `97%` and `96%`, R-016's `77%`,
R-017's `94%` and `83%`, R-018's `60%`, R-019's `47%`, and the later unrecorded `39%` stop reading
were primary 300-minute observations. Preserve them as historical raw five-hour observations
only; none controls the protected weekly floor. Sponsor-reported percentages remain sponsor
evidence, not independently measured values.

From this decision forward, calculate five-hour remaining only from `primary` and weekly remaining
only from `secondary`. The weekly secondary value controls the project start and stop gates: begin
no new long or multi-agent unit below `50%` weekly, and stop at `40%` weekly or on a warning or
lower sponsor weekly report. A five-hour limit can affect platform availability but does not by
itself consume or trigger the protected weekly floor.

D-056's mandatory independent security review was interrupted solely because the primary
five-hour `39%` reading was mistakenly treated as the weekly stop. It neither completed nor
approved fingerprint `3d2ae4135217eba962ec6f618a4a18c56bbf6ea31e9455aed0cc0db5667b9200`, and no write
occurred after D-056. D-056 authority never activated. D-057 is a wholly new prospective control,
not a retry or resume; it supersedes and replaces all D-056 publication authority, and in conflict
D-057 controls. It preserves all prior history, the one known dangling
`c75aa75b72168285393f44015b0200fcccf58834` blob, and D-050/D-051's no-go and cooldown.

Fresh GitHub capture from `2026-09-01T01:14:31.9754202Z` through
`2026-09-01T01:14:35.6999479Z` matched authenticated user `imyourpriest` id `49080423`; unchanged
main `d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, and sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`; protected and strict classic controls; the same nine
required app-`15368` contexts; admin enforcement, linear history, and conversation resolution
true; and force push and deletion false. Exactly one effective-rules request returned `[]`, and
exactly one combined repository rulesets request with `includes_parents=true` returned `[]`.
Zero open pull requests and exact target-ref absence remained; the known dangling blob remained
at size `141949` bytes.

Only after a new independent security review approves the new cumulative exact four-file
fingerprint `F` and its substituted canonical body digest, D-057 reissues by reference the full
exact D-056/D-055/D-054 guarded cycle: every exact path, base, tree, branch, title, message,
canonical body, authenticated-default identity, corrected two rules surfaces, corrected blob
validator, second exact-remote-head review, nine exact checks across both check surfaces, ready
transition, exact-head non-admin protected squash merge with exact subject and body, post-main and
retained-branch read-backs, local-only receipt, no-remediation rule, and forbidden action. Every
incorporated exact value and evidence boundary remains controlling except the newly reviewed
bytes, fingerprint, body digest, per-file bindings, and Usage-window correction in D-057.

The appended bytes require a wholly new four-blob transaction. Never reuse or clean the stale
`c75aa75b72168285393f44015b0200fcccf58834` object. Before writing, bind each new file's Git blob
SHA, raw byte length, and raw SHA-256. Blob read-back must compare length and SHA-256, or may also
use supported `[System.Linq.Enumerable]::SequenceEqual[byte]`; never construct `ReadOnlySpan` or
call `MemoryExtensions.SequenceEqual`.

Any review finding, stale state, mismatch, failure, ambiguity, unavailable field, or partial
result stops all mutation and requires a new prospective control after fresh capture and review.
No retry, resume, cleanup, remediation, update, or deletion is authorized.

No new research or work unit is selected; no activation, contact, private input, payment, or
unrelated action occurred. R-020 adds zero Patch and zero Support units; totals remain 28/14 and
revenue and cleared receipts remain `$0.00`.

**Why:** Correct window attribution is required for an honest protected-floor decision. The prior
security review stopped before approval, so only a newly fingerprinted and independently reviewed
control may authorize another guarded transaction.

## 2026-08-31 - D-058 - R-021 window-mapping correction and replacement authority

**Decision:** Correct the Usage-window mapping rule, preserve the failed D-057 review, and select
one zero-unit R-021 prospective replacement control. D-057's mandatory independent review found
one controlling P3 in exact fingerprint
`be7230e48cbedbb6db87dba906b7dce171bd7927cc8871b5e4c75e33968fe257`; it did not approve that
fingerprint. D-057 never activated and caused no GitHub write.

Window meaning must be derived from `window_minutes`, never from a fixed `primary` or `secondary`
field name. A returned `10080`-minute window is weekly and a returned `300`-minute window is the
five-hour window. Historical telemetry sometimes placed the `10080`-minute weekly window in
`primary` with `secondary=null`; later dual-window telemetry placed `300` minutes in `primary` and
`10080` minutes in `secondary`. Field labels remain raw evidence, but they do not define meaning.

Independent reread of the exact local session telemetry establishes:

- R-014 at `2026-08-24T00:54:12.658Z`: `primary.used=3`,
  `primary.window_minutes=10080`, `secondary=null`; `97%` remaining was weekly.
- R-014 at `2026-08-24T00:55:25.008Z`: `primary.used=4`,
  `primary.window_minutes=10080`, `secondary=null`; `96%` remaining was weekly.
- R-016 at `2026-08-24T01:56:14.434Z`: `primary.used=23`,
  `primary.window_minutes=10080`, `secondary=null`; `77%` remaining was weekly.
- R-017 at `2026-09-01T00:38:54.291Z`: primary `used=6`, `window_minutes=300`, so `94%`
  was five-hour; secondary `used=27`, `window_minutes=10080`, so weekly remaining was `73%`.
- R-017 at `2026-09-01T00:44:00.059Z`: primary `used=17`, `window_minutes=300`, so `83%`
  was five-hour; secondary `used=28`, `window_minutes=10080`, so weekly remaining was `72%`.
- R-018 at `2026-09-01T00:56:47.449Z`: primary `used=40`, `window_minutes=300`, so `60%`
  was five-hour; secondary `used=32`, `window_minutes=10080`, so weekly remaining was `68%`.
- R-019 at `2026-09-01T01:04:17.768Z`: primary `used=53`, `window_minutes=300`, so `47%`
  was five-hour; secondary `used=34`, `window_minutes=10080`, so weekly remaining was `66%`.
- The later unrecorded sample at `2026-09-01T01:08:54.559Z`: primary `used=61`,
  `window_minutes=300`, so `39%` was five-hour; secondary `used=35`,
  `window_minutes=10080`, so weekly remaining was `65%`.
- D-057's sample at `2026-09-01T01:14:35.867Z`: primary `used=72`, remaining `28%`,
  `window_minutes=300`; secondary `used=37`, remaining `63%`, `window_minutes=10080`; the
  sponsor reported `64%` weekly.
- Current sample at `2026-09-01T01:25:39.434Z`: primary `used=98`, remaining `2%`,
  `window_minutes=300`; secondary `used=41`, remaining `59%`, `window_minutes=10080`.

All of these local values are operational telemetry, not signed dashboard proof or project
attribution. Official OpenAI documentation remains source-limited: it says local-message
estimates are per five-hour window and additional weekly limits may apply, but it does not prove
exact account usage.

At every future Usage gate, select whichever returned window has `window_minutes=10080` as weekly,
regardless of its field label, and select `window_minutes=300` as five-hour. Begin no new long or
multi-agent unit below `50%` weekly; stop at `40%` weekly, a warning, or a lower sponsor weekly
report. Five-hour exhaustion can affect platform availability only and does not itself trigger
the protected weekly floor. If the `10080`-minute window is absent or ambiguous at a consequential
gate, do not infer weekly state from a field name; rely on a fresh sponsor dashboard report when
available or stop safely pending reliable weekly evidence.

Fresh read-only GitHub capture from `2026-09-01T01:25:34.2706379Z` through
`2026-09-01T01:25:39.2589607Z` matched viewer `imyourpriest` id `49080423`; unchanged main
`d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, and sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`. Historical baseline
`0ecc40ee1935abd88a309ac3a61134b9357db624` was the merge base; current main was ahead 9 and
behind 0. Classic protection remained protected and strict, with required pull-request reviews
count 0 and no stale-approval dismissal, code-owner review, or last-push approval requirement;
admin enforcement, linear history, and conversation resolution true; force push and deletion
false; and the same exact nine required contexts bound to app id `15368`. Exactly one effective-
rules request and one combined `rulesets?includes_parents=true` request each returned exact raw
`[]`. Zero open pull requests and exact target-ref absence remained. Known dangling blob
`c75aa75b72168285393f44015b0200fcccf58834` remained size `141949`; never reuse, delete, or clean
it.

D-058 is wholly new prospective authority, not a retry or resume. It supersedes and replaces all
D-057 publication authority; in conflict D-058 controls. It preserves D-057 and all earlier
history, D-050/D-051's no-go and cooldown, and the known dangling blob.

Only after a brand-new independent security review passes the new cumulative exact four-file
fingerprint `F`, the new canonical body digest, and all exact bytes, D-058 reissues by reference
the entire corrected D-056/D-055/D-054 guarded cycle: exact paths, base, tree, branch, title,
message, canonical body template with only new `F` substitution, authenticated-default identity,
five-stage shell `gh api` sequence, corrected length-plus-raw-SHA-256 blob read-back validator,
exact new four blobs, no stale-blob reuse, full tree/commit/ref/pull-request read-backs, second
independent exact-remote-head review, all nine exact app-`15368` checks and conditional legacy
commit statuses without duplicate masking, ready transition, exact-head non-admin protected
squash merge, retained branch and post-main read-backs, local-only nonrecursive receipt,
no-remediation rule, and every forbidden action. Never construct `ReadOnlySpan` or call
`MemoryExtensions.SequenceEqual`; supported Enumerable equality may supplement, but not replace,
length and raw-SHA-256 comparison.

Any finding, mismatch, stale state, failure, ambiguity, unavailable field, or partial result stops
all mutation and requires another prospective control after fresh capture and review. No retry,
resume, cleanup, remediation, update, or deletion is authorized. Until the new review passes,
D-058 grants no publication authority.

No new research or work unit is selected; no activation, contact, private input, payment, or
unrelated action occurred. R-021 adds zero Patch and zero Support units; historical totals remain
28 impact / 14 revenue and revenue and cleared receipts remain `$0.00`.

**Why:** The weekly window has changed field position across telemetry formats. Binding semantics
to duration rather than label corrects the audit trail and prevents another false Usage-floor
decision. The failed review requires a new fingerprint and independent approval before any write.

## 2026-09-01 - D-059 - R-022 run-specific weekly floor and replacement authority

**Decision:** Record the sponsor's explicit instruction for this run to continue toward a
protected `20%` **weekly** remaining floor, and select one zero-unit R-022 prospective replacement
control. This run-specific instruction supersedes D-058's `40%` weekly stop and `50%` no-new-long
threshold only for this run. The autonomous safety buffer begins no new long or multi-agent unit
below `30%` weekly and stops at `20%` weekly, any warning, or any lower sponsor weekly report. It
does not change the ordinary thresholds for a future reset or future run.

Usage meaning remains duration-based exactly as corrected by D-058: a returned
`window_minutes=10080` window is weekly and `window_minutes=300` is five-hour, regardless whether
either appears as `primary` or `secondary`. If the weekly window is missing or ambiguous at a
consequential gate, never infer it from a field label; use a fresh sponsor dashboard report if
available or stop pending reliable weekly evidence. Five-hour exhaustion affects availability,
not the weekly floor.

Exact local operational telemetry at `2026-09-01T21:25:05.953Z` returned the 300-minute window at
`used=0` / `remaining=100` and the 10080-minute window at `used=42` / `remaining=58`; reset fields
were present. This is operational telemetry only, not signed dashboard proof or project
attribution. The sponsor's `20%` instruction is authorization and a protected floor, not a claim
that current weekly remaining is `20%`.

D-058 was appended locally and remained pending mandatory independent review. No independent
review completed, D-058 never activated, and it caused no GitHub write. Because the sponsor
materially changed the Usage constraint after D-058's bytes were prepared, D-059 is wholly new
prospective authority, not retry or resume. It supersedes and replaces every conflicting D-058
publication authorization while preserving D-058, D-057, and all prior history, D-050/D-051's
no-go and cooldown, and the known dangling blob.

Fresh read-only GitHub capture from `2026-09-01T21:25:55.3924537Z` through
`2026-09-01T21:26:00.7331050Z` matched authenticated viewer `imyourpriest` id `49080423`; unchanged
main `d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, and sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`. Historical baseline
`0ecc40ee1935abd88a309ac3a61134b9357db624` remained the merge base, with current main ahead `9`
and behind `0`. Classic protection remained strict with the exact nine required contexts each
bound to app id `15368`; required pull-request review count `0`, stale-review dismissal false,
code-owner review false, and last-push approval false; admin enforcement, linear history, and
conversation resolution true; force push and deletion false. Exactly one effective branch-rules
request returned raw `[]`, and exactly one combined repository rulesets request with
`includes_parents=true` returned raw `[]`. There were zero open pull requests and the exact target
ref was absent. Known dangling blob `c75aa75b72168285393f44015b0200fcccf58834` persisted at size
`141949`; never reuse, delete, or clean it. These are reachable-state observations under the
authenticated view, not proof of every unreachable object or policy outside returned surfaces.

Only after a brand-new independent security-review PASS of D-059's cumulative exact four-file
fingerprint `F`, substituted canonical pull-request body digest, and every exact byte, D-059
reissues by reference the full corrected D-058/D-056/D-055/D-054 guarded publication cycle. This
incorporates the exact paths, base/tree, branch, title/message, canonical body template,
authenticated-default identity, five-stage shell `gh api` Git Database and pull-request sequence,
new four blobs, corrected length-plus-raw-SHA-256 read-back validator that never uses
`ReadOnlySpan` or `MemoryExtensions`, complete read-backs, second independent review of the exact
remote head, required check and status gates, ready transition, exact-head non-admin protected
squash merge, retained-branch and post-main reads, local-only nonrecursive receipt, every
no-remediation rule, and every forbidden action. New bytes require new blobs; the stale blob must
never be reused.

Any finding, stale state, mismatch, failure, ambiguity, unavailable field, or partial result stops
all mutation. No retry, resume, cleanup, remediation, update, or deletion is authorized. Until
that new review passes, D-059 grants no publication authority.

No new research or work unit is selected; no activation, contact, private input, payment, or
unrelated mutation occurred. R-022 adds zero Patch and zero Support units; historical totals
remain 28 impact / 14 revenue, preserving 2:1, and revenue and cleared receipts remain `$0.00`.

**Why:** The sponsor changed the weekly floor after D-058's exact bytes were prepared. A new
append-only, fingerprinted, independently reviewed control is required before any guarded write.

## 2026-09-01 - D-060 - R-023 prewrite-validator stop and replacement authority

**Decision:** Record D-059's fail-closed prewrite-validator stop and select one zero-unit R-023
prospective replacement control. Independent security review had PASSed D-059's exact cumulative
fingerprint `a9460282c1801702ce4e113d0d66f56fd7f7c96d9290a5848b502ee835a6d2b6`, canonical body
digest `5532cd961cf13ea3d1ac24bbce657fe355463347bbbdb5d1514eccedd5fdb48d`, and all exact bytes
with no P0-P3 finding. Review-time remote state was unchanged, and exact operational telemetry at
`2026-09-01T21:38:18.318Z` showed `53%` weekly remaining.

The mandatory final read-only equality script, whose failed tool output was timestamped
`2026-09-01T21:41:29.740Z`, stopped **before every write**. It passed the local HEAD, tree, path,
diff, hash, fingerprint, and canonical-body gates and the viewer, repository, main, ancestry, and
classic-protection fields through the required-review flags. PowerShell StrictMode then raised
exactly `The property 'restrictions' cannot be found on this object. Verify that the property
exists.` because the script directly accessed an omitted property. That invocation stopped before
rules/rulesets, pull-request, target-ref, dangling-blob, and Usage checks. It issued no
`POST`/`PATCH`/`PUT`/`DELETE`, blob/tree/commit/ref/pull-request call, or mutation.

Read-only reconciliation from `2026-09-01T21:41:50.8804685Z` through
`2026-09-01T21:41:53.0266182Z` proved that the parent protection object omitted `restrictions`.
Its property list was exactly `allow_deletions`, `allow_force_pushes`, `allow_fork_syncing`,
`block_creations`, `enforce_admins`, `lock_branch`, `required_conversation_resolution`,
`required_linear_history`, `required_pull_request_reviews`, `required_signatures`,
`required_status_checks`, and `url`. The dedicated restrictions GET returned exit `1` / HTTP
`404`; its final body parsed as valid JSON with status `404` and message exactly
`Push restrictions not enabled`. Main was unchanged, there were zero open pull requests, and the
exact target ref returned HTTP 404. A first post-stop full-capture helper made read-only GETs only
but failed locally before output because `Select-Object -Last1` was mistyped and null parsing
cascaded. This is diagnostic provenance, not a GitHub failure or write. The corrected permitted
reconciliation capture succeeded.

The fresh successful capture from `2026-09-01T21:43:03.9683315Z` through
`2026-09-01T21:43:14.5704723Z` matched viewer `imyourpriest` id `49080423`; public repository with
default branch `main`; main `d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, and sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`; and historical
`0ecc40ee1935abd88a309ac3a61134b9357db624` as merge base with main ahead `9` / behind `0`.
Protection was strict with the same exact nine app-`15368` checks/contexts, review count `0` and
all three review flags false, admins true, signatures false, linear history and conversation
resolution true, and force push, deletion, fork sync, block creation, and lock false. The parent
object omitted `restrictions`, and the dedicated endpoint returned the exact not-enabled tuple
above. The effective-rules response was raw `[]`; the combined
`rulesets?includes_parents=true` response was raw `[]`; there were zero open pull requests; the
target ref returned exact HTTP 404; and known dangling blob
`c75aa75b72168285393f44015b0200fcccf58834` remained size `141949`. Latest telemetry at
`2026-09-01T21:42:39.041Z` was five-hour `63%` remaining and weekly `52%` remaining, with weekly
selected only by `window_minutes=10080`. These are authenticated reachable-state and local
operational observations, not proof beyond the returned surfaces or signed Usage attribution.

Official GitHub documentation shows `restrictions` in a full-protection example but does not say
the property is mandatory. Its dedicated restrictions-endpoint documentation lists 200 and 404
responses but not this exact runtime message. The omitted property and exact observed 404 tuple
are therefore runtime evidence, not a guaranteed universal API contract.

The replacement parent-protection predicate requires HTTP 200, valid JSON, and every exact bound
field. Inspect `PSObject.Properties['restrictions']` without directly accessing a missing
property, and require the property to be absent for this baseline. Call the dedicated restrictions
endpoint exactly once and accept not-enabled only when the non-success exit corresponds to HTTP
404, the final body parses as JSON with status 404, and its message is exactly
`Push restrictions not enabled`. A present property, generic 404, authorization or transport
error, malformed body, missing or changed message, or any other result is drift or unknown and
stops. Use `Select-Object -Last 1`, never `-Last1`.

D-059's prewrite failure exhausts all its prospective publication authority even though no
mutation occurred. D-060 is wholly new authority, not retry or resume, and supersedes all D-059
publication authority while preserving history; D-058's duration-based Usage mapping; this run's
no-new-long/multi-agent threshold below `30%` weekly and stop at `20%` weekly, any warning, or
lower sponsor weekly report; D-050/D-051's no-go and cooldown; and the known dangling blob.

Only after a brand-new independent security-review PASS of D-060's cumulative exact four-file
fingerprint `F`, substituted canonical body digest, and every exact byte, D-060 reissues by
reference the entire corrected D-059/D-058/D-056/D-055/D-054 guarded cycle with this sole
validator correction: exact new four blobs and exact base, tree, paths, branch, title, message,
body, and authenticated-default identity; the five-stage sequence and all read-backs; second
independent exact-remote-head review; hosted gates; ready transition; protected exact-head
non-admin squash merge; retained branch and post-main verification; local-only receipt; and all
forbidden, no-remediation, no-cleanup rules. Never reuse, delete, or clean the stale blob.

Before the first write, run a wholly new final equality gate using this corrected restrictions
predicate and every remaining incorporated gate. Any finding, staleness, mismatch, failure,
ambiguity, unavailable field, or partial result stops with no retry, resume, cleanup, remediation,
update, or deletion. D-060 grants no publication authority until the new review PASSes.

No new research or work unit is selected; no activation, contact, private input, payment, or
unrelated mutation occurred. R-023 adds zero Patch and zero Support units; totals remain 28 impact
/ 14 revenue, preserving 2:1, and revenue and cleared receipts remain `$0.00`.

**Why:** A strict-mode assumption about an optional runtime field stopped the mandatory equality
gate before every write. A new exact-byte review must bind the corrected fail-closed predicate.

## 2026-09-01 - D-061 - R-024 canonical-body-digest stop and replacement authority

**Decision:** Record D-060's fail-closed canonical-body-digest stop and select one zero-unit R-024
prospective replacement control. Independent security review had labeled D-060 a PASS with no
P0-P3 finding and approved its exact cumulative fingerprint
`0e076768647e077ff2628615f691ca2986cf3840899e6ae425ef7a408d0958ee`, file blobs, lengths, and
raw hashes. However, both the implementation report and review transcribed D-060's canonical-body
SHA-256 as `b332d554a55e0894608a3afec6c0ac5bd508f0d7c03e4e9bd605da498d508c3`, which is only 63
lowercase hexadecimal characters because the final `b` is missing. The mandatory gate's discovery
of that binding/provenance defect is a controlling P3 finding regardless of the earlier PASS label;
the prior review failed to count or report the missing character.

At `2026-09-01T21:59:00.876Z`, D-060's brand-new final equality script recomputed the actual
canonical body and stopped exactly at `D060_PREWRITE_FAIL: canonical body hash`. It stopped during
local checks before invoking the viewer or any other GitHub helper. That gate therefore issued zero
GitHub requests and absolutely no `POST`, `PATCH`, `PUT`, or `DELETE`; it created no blob, tree,
commit, ref, pull request, or other mutation.

Read-only local reconciliation proved that the expected digest string had length `63`, the actual
canonical body had byte length `1598`, the cumulative fingerprint had length `64`, and the D-054
template contained exactly one `<F>` placeholder. With that placeholder replaced once by the exact
D-060 fingerprint, encoded as UTF-8 with LF endings and no terminal newline, the actual canonical
SHA-256 had length `64` and value
`b332d554a55e0894608a3afec6c0ac5bd508f0d7c03e4e9bd605da498d508c3b`. The four local files
had no byte drift. The earlier 63-character transcription was the defect, not a change to the
canonical body.

D-060's prospective publication authority is exhausted. D-061 is wholly new authority, not a
retry or resume, and supersedes all D-060 publication authority while preserving every historical
record; D-058's duration-based Usage mapping; this run's prohibition on beginning a new long or
multi-agent unit below `30%` weekly and stop at `20%` weekly, any warning, or any lower sponsor
weekly report; D-050/D-051's no-go and cooldown; and known dangling blob
`c75aa75b72168285393f44015b0200fcccf58834`, which must never be reused, deleted, or cleaned.

Fresh read-only reconciliation from `2026-09-01T22:00:01.6621829Z` through
`2026-09-01T22:00:11.7039317Z` matched authenticated viewer `imyourpriest` id `49080423`; the
public repository with default branch `main`; main
`d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, and sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`; and historical baseline
`0ecc40ee1935abd88a309ac3a61134b9357db624` as merge base with main ahead `9` and behind `0`.
Every full classic-protection property and value remained unchanged, including the same nine
required contexts each bound to app id `15368`; the parent `restrictions` property was absent and
the dedicated endpoint returned exact HTTP/status `404` with message
`Push restrictions not enabled`. Effective branch rules were raw `[]`, combined repository
rulesets with `includes_parents=true` were raw `[]`, there were zero open pull requests, the exact
target ref returned `404`, and the known dangling blob remained size `141949`. Exact operational
telemetry at `2026-09-01T21:59:40.336Z` showed `48%` weekly remaining, selected only by
`window_minutes=10080`. These are authenticated reachable-state and local operational
observations, not proof beyond the returned surfaces, signed Usage evidence, or project
attribution.

Only after a brand-new independent security-review PASS of D-061's cumulative exact four-file
fingerprint `F`, substituted canonical body digest, and every exact byte, D-061 reissues by
reference the complete corrected D-060/D-059/D-058/D-056/D-055/D-054 guarded publication cycle.
It preserves the exact base, tree, four paths, branch, title, commit message, canonical D-054 body
template, authenticated-default identity, new-four-blob sequence and read-backs, tree/commit/ref/
draft-pull-request sequence, second independent exact-remote-head review, hosted gates, ready
transition, protected non-admin exact-head squash merge, retained branch, post-main verification,
local-only receipt, forbidden actions, and every stop/no-remediation/no-cleanup requirement.

The sole new correction is that every SHA-256 or fingerprint binding must match lowercase
`[0-9a-f]{64}` and have `.Length -eq 64` before it can be used in an equality comparison or
transaction. The canonical body must be recomputed from the D-054 template by replacing exactly
one `<F>` with the reviewed final fingerprint, using UTF-8, LF only, no terminal newline, its exact
byte length, and its 64-character SHA-256. The reviewer must independently count and validate the
length and lowercase-hex form of every binding rather than accept a transcription.

Before any first write, run a wholly new final equality gate with the corrected missing-
`restrictions` predicate, `Select-Object -Last 1`, manual length/hash verification, and explicit
64-lowercase-hex validation for `F`, the canonical-body digest, and every raw file hash. Any
failure, drift, mismatch, ambiguity, unavailable field, or partial result stops. No retry, resume,
cleanup, remediation, update, or deletion is authorized. D-061 grants no publication authority
until the new review PASSes.

No new research or work unit is selected; no activation, contact, private input, payment, or
unrelated mutation occurred. R-024 adds zero Patch and zero Support units; totals remain 28 impact
/ 14 revenue, preserving 2:1, and revenue and cleared receipts remain `$0.00`.

**Why:** A 63-character digest transcription escaped the prior review but was caught by the
mandatory local equality gate before any GitHub request. New exact-byte authority and independent
length validation are required before publication can be considered.

## 2026-09-01 - D-062 - R-025 parser stop and reviewed-helper publication authority

**Decision:** Record D-061's fail-closed PowerShell parser stop and select one zero-unit R-025
prospective replacement control. Independent security review PASSed D-061's exact cumulative
fingerprint `fb77d7677d21d2e7b0fdb675d5514b27fc43ce61fd824684a10c5c7ea15fbb47`, its canonical
body and file bindings, and all 64-character lowercase-hex validation with no P0-P3 finding.

At `2026-09-01T22:15:32.800Z`, D-061's final equality command failed at PowerShell parse time with
exactly `Missing 'in' after variable in foreach loop. The correct form is: foreach ($a in $b)
{...}`. Inline text contained `foreach($path in$paths)` rather than `foreach ($path in $paths)` in
two places. Parsing failed before any statement executed. The invocation performed zero local
checks, called no GitHub helper or request, and issued no write or mutation of any kind.

D-061 authority is exhausted. D-062 is wholly new prospective authority, not a retry or resume,
and supersedes D-061 authority while preserving all history; D-058's duration-based Usage mapping;
this run's prohibition on beginning a new long or multi-agent unit below `30%` weekly and stop at
`20%` weekly, any warning, or any lower sponsor weekly report; D-050/D-051's no-go and cooldown;
and known dangling blob `c75aa75b72168285393f44015b0200fcccf58834`, which must never be
reused, deleted, or cleaned.

Fresh independent review state from `2026-09-01T22:10:41.898Z` through
`2026-09-01T22:10:54.638Z` was unchanged: authenticated viewer `imyourpriest` id `49080423` and
public repository `imyourpriest/linux-agent-workbench` with default branch `main`; main
`d1ea152fc725f303ea31c30cbfb456299db47b6b`, tree
`e22fd1f125be2b8afe7b8296ddac6c2e1d505e02`, sole parent
`7cee864eea5bc4821ecfb6ea17091f45dba5a656`, and historical baseline
`0ecc40ee1935abd88a309ac3a61134b9357db624` as merge base with main ahead `9` and behind `0`.
Full classic protection and the exact nine app-`15368` checks were unchanged. The parent
`restrictions` property was absent and the dedicated endpoint returned the exact observed
exit/HTTP/status `1`/`404`/`404` tuple with message `Push restrictions not enabled`. Effective
rules were raw `[]`, combined parent-inclusive rulesets were raw `[]`, there were zero open pull
requests, the exact target ref was absent, and the known dangling blob remained size `141949`.
Operational telemetry at `2026-09-01T22:13:06.401Z` was weekly `43%` and five-hour `5%`
remaining. These are authenticated reachable-state and local operational observations, not proof
beyond returned surfaces, signed Usage evidence, project attribution, or production enforcement.

D-062 retires inline mega-command execution. It prospectively permits only the exact separately
SHA-256-bound helper bytes at `C:\Users\IYP\.codex\cairn-r014-d062-guarded-publish.ps1`, outside
the repository. The helper contains no secrets, is not part of the published tree, and may not be
changed after review. A helper or static-review change requires a new review. D-062 grants no
publication authority until one brand-new independent security review PASSes both the cumulative
exact four-file bytes, fingerprint, body and file bindings and the helper's exact bytes, SHA-256,
and fail-closed security behavior.

After that PASS only, exact helper mode `-Mode PublishDraft` is the sole permitted mechanism for a
new final equality gate and the exact five-stage draft transaction. It must first rerun all local
static checks and a complete read-only remote/Usage preflight. Then it may create and fully verify
exactly four new blobs in sorted path order, the exact replacement tree, one authenticated-default
commit, the exact new ref, and one draft pull request. Any parse, static, preflight, stage, or
read-back failure stops immediately with no rerun, retry, resume, remediation, cleanup, update, or
deletion. The helper may publish draft only; it may not run checks, mark ready, or merge.

D-062 reissues by reference the complete corrected D-061/D-060/D-059/D-058/D-056/D-055/D-054
guarded cycle: exact base/tree/four paths/branch/title/message/canonical body/default identity; new
blobs and all read-backs; exact remote-fingerprint verification; later second independent review
of the exact remote head; hosted check/status gates; ready transition; protected non-admin
exact-head squash merge; branch retention; post-main verification; local-only receipt; and every
forbidden, stop, no-remediation, and no-cleanup rule. The stale blob is never a new object and must
not be reused or deleted. The exact branch remains `agent/r014-migration-qualification`; title and
commit message remain `Record R-014 migration buyer-demand no-go`; pull-request base remains
`main`, `draft=true`, and `maintainer_can_modify=false`.

No new research or work unit is selected; no activation, contact, private input, payment,
publication, or unrelated mutation occurred. R-025 adds zero Patch and zero Support units; totals
remain 28 impact / 14 revenue, preserving 2:1, and revenue and cleared receipts remain `$0.00`.

**Why:** Parse failure prevented the entire reviewed inline command from executing. A readable,
separately bound helper and a new joint exact-byte security review reduce transcription risk while
preserving fail-closed publication boundaries.

## 2026-09-01 - D-063 - R-026 query-interpolation stop and replacement authority

**Decision:** Record D-062's independently reviewed partial Git Database transaction and select one
zero-unit R-026 prospective replacement control. The first formal D-062 helper review reported a
P2 because Stage 1 reread file bytes were passed to a blob POST before that same byte array was
rechecked against its bound length, raw SHA-256, and Git blob SHA; three immediate pre-POST
assertions corrected it. A second fresh review reported a P2 because unconditional
`Write-Output -NoEnumerate` wrapped a top-level `PSCustomObject` in this PowerShell runtime, plus a
P3 because warning literals were not inspected on every returned Usage window. It also
prohibitedly and inadvertently invoked pre-PASS `PublishDraft` once. That invocation failed during
read-only classic-protection preflight before its first POST. Root GET reconciliation at
`2026-09-02T03:12:30.6524274Z` showed unchanged main, zero open pull requests, absent target ref,
and the exact four local modified paths. The reviewer also created and deleted one empty temporary
file outside the repository. These were process violations. The bounded reconciliation found no
reachable GitHub or repository mutation from that invocation; it cannot prove universal
non-mutation or absence of unreachable objects.

The corrected helper preserved top-level objects versus arrays, scanned warning variants across
the event payload, rate-limits object, and all non-null Usage windows, and retained every earlier
fail-closed check. A third independent review PASSed its exact 36,055 bytes, helper SHA-256
`ab09540ab5a84783867ded4d59782f11db8c952de4fbfa7285e801ed620b4a1e`, exact cumulative
four-file fingerprint/body/file bindings, and security behavior with no P0-P3. Review-time
operational telemetry was weekly `32%` and five-hour `30%` remaining.

One authorized D-062 helper invocation produced output timestamp `2026-09-02T03:25:13.928Z`.
Immediately beforehand its length and SHA-256 matched the reviewed binding. Static checks and the
complete remote/Usage preflight passed. It issued four exact create-blob calls in case-sensitive
sorted path order, verified every returned SHA and decoded-byte length/raw hash/Git hash readback,
and then POSTed the exact candidate tree. It stopped while evaluating the first recursive
base-tree GET, before any tree readback or commit POST, with exact error `The variable
'$BaseTree?recursive' cannot be retrieved because it has not been set.` In the double-quoted
endpoint `"$RepoApi/git/trees/$BaseTree?recursive=1"`, StrictMode parsed `$BaseTree?recursive` as
the variable name. No retry occurred.

Root read-only reconciliation at `2026-09-02T03:26:45.0979063Z` deterministically computed and
GET-confirmed these public-repository content-addressed, unreferenced objects:

- prior stale blob `c75aa75b72168285393f44015b0200fcccf58834`, size `141949`;
- D-062 blobs `c351e5e407c60f8575f9dbdbac56acf520f9ba7b` / `166243`,
  `6e589b3a73121d7700e9e98f5935f6ee0ad23755` / `174943`,
  `53797dd28bce35553efe4142a5d3b0f829679752` / `21862`, and
  `f6ba39002f89a060246b2de1d88abe89cc3326d7` / `52854`, respectively for Control,
  Decision, Research, and Usage; and
- D-062 docs subtree `b45d4bf4cc93025f7e3a412b2e94b60ba3ab1ed8` and root tree
  `778391d1a5416e201248ac6c023282e0d71eca90`. The root-tree GET was exact and untruncated and
  contained the four exact documentation path/mode/blob bindings.

Main remained `d1ea152fc725f303ea31c30cbfb456299db47b6b`, there were zero open pull requests, and exact
target `agent/r014-migration-qualification` returned 404. Source order establishes that no commit
POST occurred. Absence of every other unreachable object cannot be enumerated. Operational
telemetry at `2026-09-02T03:26:45.273Z` was weekly `31%` for the 10080-minute window and five-hour
`26%` for the 300-minute window, with no reached or spend control. This remediation/review unit
began above the 30% no-new-long threshold; the 20% weekly stop remains controlling.

D-062 authority is exhausted and may never be retried, resumed, deleted, remediated, or cleaned.
No stale blob or tree may be reused or deleted. D-063 is wholly new prospective authority, not a
retry or resume, and remains inactive until one new independent security-review PASS covers the
final exact cumulative four-file bytes and the helper's wholly new exact bytes and SHA-256.

After that PASS only, the exact helper path may be invoked once with `-Mode PublishDraft`. It must
use explicit query interpolation, bind and revalidate all known stale objects, and require every
new expected file blob and created tree to differ from all bound stale object SHAs. Any failure
again stops without retry, resume, remediation, cleanup, update, or deletion. Appending D-063
changes every documentation file hash, so all four expected blobs and the new candidate tree must
be distinct from every known D-055/D-062 stale object.

D-063 otherwise reissues by reference the same exact target/base/title/message, canonical D-054
body, authenticated-default identity, draft-only transaction, second exact-remote-head review,
hosted checks, ready transition, non-admin exact-head protected squash merge, branch retention,
post-main checks, and local-only receipt cycle. No new research or work unit, contact, private
input, payment, pull request, branch, main change, or commit occurred. Four blobs and two trees do
exist and are retrievable by SHA in the public repository object database; therefore this record
does not claim that no GitHub write or public object publication occurred. R-026 adds zero Patch
and zero Support units; totals remain 28/14, preserving 2:1, and revenue and cleared receipts
remain `$0.00`.

**Why:** The reviewed transaction stopped after creating content-addressed objects because one
unbraced query interpolation failed under StrictMode. New bytes, stale-object binding, and a new
joint exact-byte review are required before another prospective draft transaction exists.

## 2026-09-05 - D-064 - R-027 Rivetloom identity and guarded draft recovery

**Decision:** Adopt **Rivetloom** as the project's current public name. CairnWake remains only as
historical origin provenance; immutable records, fixtures, package identifiers, the remote
repository name, and local folder names remain unchanged. Update the README identity, license
contributor label, parked Revenue Lab author metadata, these four append-only control records, and
the four deterministic files in the current unpublished Patch Cabinet v0.2.0 release candidate.
The release candidate is regenerated only to keep its checked LICENSE-derived evidence current;
this is not a release, tag, publication, or historical-artifact rewrite. Public demand/workstream
research, workstream activation, units, offers, contact, payments, and revenue remain parked.

D-063's one authorized transaction created and verified its exact four blobs, docs tree
`cac75900e57a82c29446ed66589f4d94bf2b60a8`, and root tree
`b6eba97578df55bd53bb179cc4f730fd07a462ac`. It then POSTed a commit but stopped at the obsolete
local-clock proximity assertion before any branch or pull-request creation. The returned commit
SHA was not durably retained and is unknown. No brute-force or object enumeration is justified;
the unknown commit and every known D-055/D-062/D-063 object remain stale, excluded from reuse,
deletion, cleanup, or revival. D-063 is exhausted.

The sponsor's current instructions permit this run to continue to `0%` remaining in both the
300-minute five-hour window and the 10080-minute weekly window. After using a reset, they expressly
authorized using the full new five-hour allowance; the earlier weekly-zero-floor instruction also
remains in force. A primary product observation at that reset showed `98%` five-hour and `100%`
weekly remaining with one reset credit still reported. The earlier `11%` weekly observation was a
preparation-time sample, not the latest reading. All readings are whole-account observations
without project attribution. Any real warning, reached limit, spend-control signal, malformed or
ambiguous telemetry, or unavailable tool still stops. The active project model is GPT-6 Astra at
ultra reasoning; this is operating context, not evidence that the model owns accounts or authority.

D-064 is wholly new prospective authority for one complete gated publication cycle, only after a
fresh independent exact-byte security PASS. Its first stage is exactly one draft recovery on branch
`agent/rivetloom-d064`, with commit message and pull-request title `Name project Rivetloom and
record migration no-go`; the D-064 helper implements only that draft stage. Before the PASS, only
Static and read-only Preflight modes may run. The exact eleven paths are `README.md`, `LICENSE`,
`revenue-lab/pyproject.toml`, `docs/CONTROL_LOG.md`, `docs/DECISION_LOG.md`,
`docs/RESEARCH_NOTES.md`, `docs/USAGE_LEDGER.md`, and the current unpublished v0.2.0 candidate's
`build-receipt.json`, `maintainer-policy-declaration-v0.2.0.zip`,
`maintainer-policy-declaration-v0.2.0.zip.sha256`, and `manifest.json` under
`patch-cabinet/release-candidate/maintainer-policy-declaration-v0.2.0/`. The helper must bind all
eleven candidate files in memory before the first POST, preserve exact HEAD prefixes for the four
logs, require exact minimal replacements for the three text identity files, require exact frozen
raw bytes for the four regenerated candidate files, compare the complete candidate tree, and
allowlist the two unrelated Dependabot pull requests #27 and #28 exactly while preserving them.

Each POST is a one-shot stage. A repository-external local journal records and flushes intent before the
call and raw stdout plus exit status immediately afterward, before JSON parsing; the commit SHA is
therefore durable before any assertion can fail. Commit validation uses the create response, Git
Database GET, and REST commit GET with strict zero-offset ISO-8601 dates, matching default
author/committer metadata, and authenticated-owner association. It omits author and committer
fields from the POST and makes no local-clock proximity claim. Any write failure, persistence
failure, mismatch, drift, ambiguity, unavailable field, or partial result consumes D-064 and stops
without retry, resume, remediation, cleanup, update, or deletion.

D-064 preserves by reference the later D-054 independent exact-remote-head review, exact hosted
checks, ready transition, protected non-admin exact-head squash merge, retained branch,
post-main verification, and local-only receipt gates as corrected by D-055 through D-063, without
reviving any spent transaction authority, but substitutes throughout D-064's final
reviewed eleven-file manifest and fingerprint, branch `agent/rivetloom-d064`, title and commit
message `Name project Rivetloom and record migration no-go`, and canonical helper-bound body for
D-054's obsolete four-file metadata. The protected squash merge must use exact subject `Name
project Rivetloom and record migration no-go` and exact body `Protected squash merge of the exact
reviewed Rivetloom identity and migration no-go record.` The complete gated cycle is authorized
only after review; this helper implements only its draft stage. R-027 adds zero Patch and zero
Support units. Totals remain 28/14, preserving 2:1; revenue and cleared receipts remain `$0.00`.

**Why:** The user asked for an original project identity rather than continued Cairn branding, and
D-063 exposed that remote mutation receipts must survive assertions and local clock skew. A new
name, exact eleven-file scope, one-shot journal, and fresh independent review provide a coherent
prospective recovery without rewriting provenance or reviving exhausted attempts.

## 2026-09-07 - D-066 - Additive fast-uri 3.1.7 security maintenance

**Decision:** Select one zero-unit, project-owned security-maintenance milestone for the active
hosted declaration compatibility harness observed in open Dependabot pull requests 27 and 28.
From exact public main `503c1394583251a69aed591d853c3d77100f476e`, preserve compatibility-v1
and compatibility-v2 byte-for-byte and add compatibility-v3 with Ajv `8.20.0`, Python
`jsonschema==4.26.0`, the existing schema and corpus contract, and `fast-uri@3.1.7`. Route only the
active hosted compatibility jobs to v3 while keeping independent standard-library freshness and
preservation checks for v1, v2, and v3.

Official fast-uri release and GitHub Advisory Database records observed on 2026-09-07 identify
3.1.7 as fixing GHSA-qw65-cvwx-89v3, which affects versions `>=3.0.0 <3.1.7`; this selection does
not assert that Rivetloom's fixed corpus or hosted configuration is exploitable. GHSA-58mr-gqgx-xq4g
affects 3.1.6 and does not apply to the preserved 3.1.5 predecessor. A metadata-only HTTPS GET of
`https://registry.npmjs.org/fast-uri/3.1.7` confirmed the exact registry URL, SHA-512 integrity,
SHA-1 shasum, and BSD-3-Clause license recorded by the new verifier-owned evidence. No tarball or
third-party validator may be downloaded, installed, imported, or executed locally.

Write scope is the new v3 generator and closed 12-file v3 tree, compatibility tests, the two active
workflow files, current maintainer documentation where needed, and append-only control, usage,
research, and Patch records. Historical v1/v2 artifacts and old release-candidate/schema/fixture
files remain immutable. D-050/D-051 remain controlling: this is not a new business hypothesis,
research scan, counted workstream unit, offer, contact, payment, activation, release, or revenue
event. D-064 and all earlier publication authorities remain separate historical records and grant
no authority for this branch. Local implementation and project-owned standard-library validation
are authorized. Publication remains pending root authorization of the exact reviewed candidate.
If authorized without material drift, D-066 may proceed through one normal branch push and draft
pull request, exact-head hosted checks and review, a protected non-admin squash merge, and retained
feature branch. Focused same-branch fixes require new exact review. Never force-push, bypass an
admin or protection control, close or alter pull requests 27 or 28 without a separately reviewed
disposition, change settings, delete a branch, create a tag or release, or make an unrelated
external mutation.

**Why:** The active hosted compatibility dependency has a security-maintenance update available.
An additive successor preserves both historical evidence generations while allowing exact,
reviewable migration of the active hosted path.

## 2026-09-07 - D-067 - Dependency-maintenance operating guide

**Decision:** Record D-066's completed publication non-recursively, then select one separate
zero-unit documentation follow-up under the sponsor's current continuation. PR 30 was merged at
`2026-09-07T21:05:14Z` as commit `19a613ff047ddbfda323dfec6a092dba5867d4b1`, from candidate
`10ccd1ee2ef74a4c80d31ab53757b2db06b9b884`; both have exact tree
`3e3972bc28ef33107d4b7681da58ed51286df9c4`. All ten post-main checks observed for that commit,
each from GitHub app 15368, completed successfully. This records named-commit hosted outcomes only,
not broad production security or future enforcement. D-066 is spent and grants no authority to
this follow-up.

Add a concise dependency-maintenance guide, a maintained-support clarification in `SECURITY.md`,
a Patch Cabinet link, and append-only entries in the Decision, Control, Usage, and Patch logs.
The guide documents the active compatibility-v3 hosted install/runner path, first-party generators
that execute and read the preserved v1/v2 source, contracts, and adapters as data, complete
additive-successor scope, named-commit validation, and the current alert/Dependabot boundaries.
It retains D-044/D-045's v1 fresh-review and reopen-before-reactivation control and applies the
same rule to preserved v2. Exactly six open alerts (6-11) and open Dependabot PRs 27 and
28 were observed on 2026-09-08 UTC (2026-09-07 America/Denver); their state may change after that
observation. Security alerts and security updates were enabled independently of any scheduled npm
version-update entry. The guide does not claim missing security coverage, fixed historical bytes,
unexploitable behavior, dismissal authority, or authority to alter the two pull requests.

Write scope is exactly `docs/DEPENDENCY_MAINTENANCE.md`, `SECURITY.md`,
`patch-cabinet/README.md`, `docs/DECISION_LOG.md`, `docs/CONTROL_LOG.md`,
`docs/USAGE_LEDGER.md`, and `patch-cabinet/LOG.md`. Local documentation preparation and
project-owned checks are authorized. Publication has not occurred and any future external action
must bind the exact reviewed candidate and then-current remote state. No recursive receipt pull
request is required. D-067 adds zero Patch and zero Support units; totals remain 28/14 and revenue
remains `$0.00`.

**Why:** The additive compatibility design is now active on public `main`, but maintainers need a
short operational procedure that preserves reproducibility, keeps dependency acquisition in the
reviewed hosted path, and states how historical alerts must be handled without implying repair or
dismissal authority.
