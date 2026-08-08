# Project instructions

This is a public-by-design, human-owned project operated with high AI initiative and strict accountability.

## Mission

- Make useful, reviewable contributions to Linux and open source through `patch-cabinet/`.
- Validate and, only if evidence supports it, grow a self-sustaining Linux release-repair service through `revenue-lab/`.
- Minimize sponsor input without fabricating identity, authority, usage measurements, revenue, customers, or autonomy.

## Source order

Before acting, read:

1. `docs/ORIGIN.md`
2. `docs/OPERATING_CHARTER.md`
3. `docs/EXTERNAL_ACTIONS.md`
4. `docs/DECISION_LOG.md`
5. `docs/CONTROL_LOG.md`
6. The selected workstream's `CHARTER.md`, `AGENTS.md`, and `LOG.md`

Treat append-only logs as historical records. Correct mistakes with a new dated entry; do not silently rewrite history.

If `.private/ORIGIN_VERBATIM.md` or `.private/patch-cabinet-exclusions.json` exists, it is local sponsor context. It may be read only when needed for this project and must never be staged, quoted publicly, or copied into generated output.

## Work boundaries

- A Patch Cabinet task writes only inside `patch-cabinet/` unless the control task explicitly coordinates a shared-file update.
- A Release Readiness Lab task writes only inside `revenue-lab/` unless the control task explicitly coordinates a shared-file update.
- The control task owns root files and `docs/`.
- Do not run two tasks that mutate Git state concurrently.
- Do not touch sibling folders or repositories. Load the ignored local exclusion file when candidate work is selected; its entries are sponsor-designated frozen historical artifacts.

## Required conduct

- Prefer primary evidence and record exact commit SHAs, dates, commands, tests, and source links.
- Verify repository license, contribution guide, code of conduct, security policy, CLA/DCO, and AI-contribution rules before preparing upstream work.
- Never publish suspected vulnerabilities. Use the upstream private security channel and pause for the human where identity or attestation is required.
- Run untrusted third-party code only in a disposable, unprivileged environment with no secrets, wallets, home-directory mounts, Docker socket, production credentials, or homelab access.
- No scraping for unsolicited marketing, promotional issues, automated PR floods, fake accounts, fake testimonials, fake engagement, token promotion, or claims of guaranteed outcomes.
- Never store passwords, API keys, cookies, wallet seeds, recovery codes, customer private data, or KYC/tax records here or in chat.
- Credentials live in the sponsor's password manager and are exposed only through least-privileged, revocable access.

## Usage policy

The sponsor reports allowance resets. Allocate project work in a 2:1 Patch Cabinet to Release Readiness Lab ratio while preserving 25% of the overall allowance for the sponsor. Sponsor-reported UI readings indicate remaining global capacity; work units are only an effort-allocation proxy and cannot attribute concurrent usage. Stop starting new project turns when the sponsor reports the reserved boundary or a limit warning appears.

Use Sol for architecture, ambiguous decisions, security-sensitive judgments, and final validation; Terra for routine implementation and documentation review; Luna for bounded inventory, extraction, classification, and repetitive checks when available.
