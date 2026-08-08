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

## 2026-08-08 — D-014 contract-only acquisition gate work unit

- Kept this turn to one bounded Revenue Lab work unit. No exact task-level allowance claim is possible; no additional Revenue Lab unit was started, preserving the workstream ceiling and sponsor-reported global reserve policy.
- Added a concrete hostile-source threat model and two-environment contract. The future acquisition environment must use a fresh store with no host objects or target-controlled Git metadata, bind the requested commit to an approved source-host identity, independently verify the commit/tree/blob graph, and emit a normalized capsule. A separate unprivileged analysis VM must have no virtual NIC, host/home mounts, secrets, Docker socket, target/Git/helper/hook execution path, or unbounded CPU, memory, process, input, writable-disk, wall-time, or output use.
- Added a standard-library contract scaffold that accepts only two pinned, non-routable project-owned synthetic fixture identities. It rejects unknown/missing/duplicate fields, noncanonical URLs and object IDs, mismatched request/receipt records, relaxed safety assertions, network-enabled or privileged analysis declarations, and absent or excessive hard limits.
- The scaffold performs no acquisition, filesystem scan, network call, subprocess launch, Git command, isolation, or analysis. Its assertion and digest fields are explicitly synthetic/untrusted, its platform-evidence status is `absent`, and every plan is `real_repository_eligible: false`.
- Corrected the CLI path help so it requests a synthetic or trusted project-owned demo directory rather than implying a third-party checkout is permitted.
- An adversarial implementation review identified self-asserted proof wording, arbitrary synthetic URL labeling, missing writable-disk policy, incomplete schema/type cases, replay ambiguity, and deterministic-hash overclaim risk. Corrections pinned fixture identities and URL/object tuples, renamed fields as fixture assertions or declared values, described hashes as recomputable fingerprints rather than signatures, added a writable-work cap, aligned the process cap with the no-child-process rule, added strict receipt/sandbox/type cases, and recorded that freshness and replay require trusted controller state.
- Verification used bundled CPython 3.12.13 with `PYTHONPATH=src`: 33 tests ran in 0.155 seconds, 32 passed, and the existing Windows symlink test skipped because this session lacks symlink privilege. The Windows junction test passed. Source/test compilation, the 100-character Python line check, and `git diff --check -- revenue-lab` passed.
- This evidence validates only deterministic synthetic policy behavior. It does not prove upstream identity or acquisition, a controller signature, fresh-store uniqueness, capsule contents, VM disposal, network denial, unprivileged identity, mount/syscall policy, hard resource enforcement, zero target/helper/hook execution, or independently observed telemetry.
- Stopped before the first real-platform step. Selecting and operating a disposable VM supervisor, pinned images, source-host adapter, independent Git-object verifier, controller signing key, and adversarial egress/resource/process telemetry requires a separately reviewed isolation platform. D-014 and every real-repository report or sale remain blocked.
- No customer or third-party checkout was read by the demo or scaffold. No network access, Docker, WSL, account, domain, merchant route, payment, marketing, contact, deployment, purchase, Git staging/commit, or XLM movement occurred. The revenue ledger remains unchanged at $0.00 because there was no financial event.
- Final post-review correction: capsule manifest and capsule digests are now bound from the synthetic receipt into the sandbox record; the sandbox input quota must cover the declared sealed input; and acquisition storage plus sealed input cannot exceed 512 MiB combined. The final suite supersedes the earlier count: 36 tests ran in 0.150 seconds, 35 passed, and the same privilege-dependent Windows symlink test skipped. Compilation, Python line-length, whitespace, bounded secret-signature, and stale/unsafe-status scans passed. Independent final security and test-design reviews reported no surviving P1 or P2 in the synthetic scaffold or contract; this does not change the blocked real-platform status.

## 2026-08-08 — Superseding D-014 verification correction

- A later independent review invalidated the preceding entry's premature “final” count and clean
  verdict. The historical line remains above for auditability; this entry supersedes it.
- Bounded strict JSON loading now rejects excessive characters, UTF-8 bytes, nesting, node counts,
  integer digits, duplicate keys, non-standard constants, floats, and all-zero digest sentinels.
  The public plan entrypoint accepts serialized JSON only, so integration cannot bypass duplicate
  detection by supplying a last-key-wins dictionary.
- The synthetic records now model every written Phase A resource limit and Phase B isolation
  assertion. They still attest to nothing: every plan remains ineligible and platform evidence
  remains absent.
- D-014 now separates a signed acquisition receipt, pre-analysis authorization, and final analysis
  attestation. Unique job nonces and cross-hashes prevent an acquisition receipt from being
  ambiguously overwritten with facts that exist only after analysis.
- Final local verification ran 41 tests: 40 passed and the existing Windows symlink test skipped
  because this session lacks symlink privilege. Compilation and whitespace checks passed. The
  independent final security review reported no surviving P1 or P2 in the code or contract.
- Real acquisition, real repository analysis, and every sale remain blocked. No network, Git,
  subprocess, filesystem acquisition, target execution, customer input, payment, or XLM movement
  occurred in this correction.
