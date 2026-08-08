# Linux Release Readiness Lab log

Append-only project record.

## 2026-08-07 — Launch and market pivot

- Rejected the initial idea of charging for a generic repository-health score because strong free and low-cost analyzers already occupy that category.
- Retired the initial `ReleaseMender` working name before publication because of likely confusion with the established Linux update brand Mender. Adopted the descriptive pre-brand name Linux Release Readiness Lab until demand and a proper clearance check justify branding.
- Defined the paid outcome as a reviewed Linux release plan or a bounded maintainer-approved repair patch.
- Limited launch to public Go and Python CLI repositories and static offline analysis.
- Set validation prices at $79 / $249 / $499; these are hypotheses, not proven willingness to pay.
- Set a no-spend demand gate: ten samples, 100 qualified visitors, five maintainer opt-ins, and one paid-order attempt.
- Started with $0, no XLM, no domain, no merchant account, no customers, and no external marketing.
- Implemented the first offline evidence collector and synthetic demo fixture.

## 2026-08-07 — Adversarial launch correction

- Replaced the earlier “paid-order attempt” metric with a clearly labeled, nonbinding paid-pilot request that takes no payment information.
- Redefined the traffic gate as qualified page views rather than unverified unique visitors and adopted aggregate, short-retention analytics.
- Replaced presence/gap claims with static signals requiring manual confirmation and added input/report bounds and hostile-input tests.
- Added incomplete terms, privacy, retention, delivery, cancellation, and refund drafts; no payment became eligible.

## 2026-08-08 — Commit-object provenance redesign

- An executable adversarial probe proved that the first verified mode could run a repository-configured Git filesystem-monitor command; another probe showed skip-worktree could hide modified evidence.
- Removed verified worktree/status scanning. Verified reports now read bounded commit objects, disable relevant Git configuration behaviors and lazy fetching, reject special entries, and verify commit/text-blob object hashes.
- Added bounded Git-output handling, port/path-case-preserving origin identity, collector-derived dates, report/rules provenance, matched-line signal evidence, and a Windows junction CI job.
- Changed initial real samples to opt-in named examples or non-identifying pattern briefs and made patch-branch delivery the default.
- Clarified that public Git history, forks, caches, archives, and third-party copies may persist after first-party case-study permission ends.
- No target repository, customer, payment, marketing channel, wallet, or external service was touched.

## 2026-08-08 — Provenance mode removed after adversarial re-review

- A third review demonstrated that repository-local origin metadata can be spoofed and that Git may consult target-controlled configuration or partial-clone helpers even when known hooks, replacement objects, and lazy fetching are constrained.
- Removed every Git invocation and verified-provenance path from the MVP. The collector now fails closed unless the caller explicitly acknowledges a synthetic or trusted-local, unverified demonstration.
- Made the declared repository URL, commit, and date visibly unverified; required an explicit date for deterministic output; retained file, byte, path, depth, time, link/junction, no-execution, and Markdown-injection controls.
- Deferred real repository reports to a separately designed disposable acquisition environment. No claim of upstream identity or safe hostile-checkout acquisition is made by the demo.
- No target repository, customer, payment, marketing channel, wallet, or external service was touched.

## 2026-08-08 — Final bounded-demo hardening

- Replaced full-directory `os.walk` materialization with incremental enumeration and an aggregate entry cap; documented that the in-process deadline is cooperative rather than a hard filesystem timeout.
- Sorted evidence before truncation, escaped Unicode direction/format and line-separator controls, and forced LF newlines in generated artifacts.
- Narrowed “offline” claims to the behavior actually established: the collector invokes no network client, subprocess, Git command, or target code, but does not prove storage locality.
- Added the disposable acquisition and network-disabled analysis environment to the operative revenue gate. Before it passes, the demo accepts only synthetic or trusted project-owned staging data, never a third-party checkout.
