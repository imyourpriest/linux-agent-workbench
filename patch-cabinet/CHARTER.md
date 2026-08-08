# Patch Cabinet charter

- Status: accepted
- Season: 1
- Started: 2026-08-07

## Mission

Find neglected but welcome, bounded work in Linux-facing open source and deliver the smallest correct patch with enough evidence that a maintainer can make an easy decision.

## Decision rights

The AI chooses candidate discovery, ranking, issue selection, technical approach, implementation, tests, documentation, and whether to abandon a weak candidate. The human appears only when a platform, account, CLA/DCO, private security process, or consequential external action requires a person.

## Season constraints

- Work on user-space Go and Python command-line tools for Linux first.
- Prefer bug fixes, tests, documentation tied to behavior, release engineering, portability, and small dependency-maintenance changes.
- Require a public license and an upstream signal inviting the work.
- Maximum expected implementation scope: six focused hours before re-evaluation.
- One active upstream candidate at a time.
- Maximum two open Patch Cabinet pull requests at a time.
- No automated bulk PRs, promotional issues, or unrequested style-only changes.
- No kernel, bootloader, authentication, cryptography, wallet, payment, package-manager core, offensive tooling, medical, industrial-control, or other high-consequence work in Season 1.

## Patch workflow

1. Record repository URL, exact commit, observation date, license, policies, issue, and maintainer signal.
2. Reject exclusions and score the candidate using the policy engine.
3. Reproduce the problem without secrets or production access.
4. Work in a disposable, unprivileged environment.
5. Make the smallest coherent change and add or update tests.
6. Run upstream checks and inspect the complete diff for scope, generated artifacts, private data, and licensing.
7. Draft a plain PR explaining problem, change, evidence, limits, and AI assistance.
8. Publish only after launch and first-canary gates are satisfied.
9. Record maintainer response and outcome without editorially rewriting history.

## Funding path

Season 1 uses no cash and no XLM. After at least three accepted upstream patches and a public cost/outcome ledger, the project may propose a user-owned GitHub Sponsors, Open Collective, or conventional card-support route. No support link is added merely to make the project look self-sustaining.

Cleared support may pay, in order, for unavoidable hosting/domain costs, project-specific AI capacity, reproducible test infrastructure, and small upstream donations. Any purchase remains subject to the root external-action policy.

## Season exit

After ten upstream outcomes, publish:

- accepted/rejected/withdrawn counts;
- median time to first maintainer response;
- regressions or corrections;
- reviewer feedback on usefulness and AI disclosure;
- usage and cash cost, with uncertainty;
- whether to continue, narrow, expand, or stop.
