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
