# Project instructions

This is a public-by-design, human-owned project operated with high AI initiative and strict accountability.

## Mission

- Pursue useful, reviewable impact through `patch-cabinet/`; Linux and open source are current
  preferences, not permanent scope constraints.
- Find a lawful, evidence-backed path to self-sustaining revenue through `support-eval-lab/`.
  `revenue-lab/` is a parked portfolio artifact, not an active offer.
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
- A Support Agent Regression Lab task writes only inside `support-eval-lab/` unless the control
  task explicitly coordinates a shared-file update.
- `revenue-lab/` is read-only while parked unless a control-task decision explicitly reactivates it.
- The control task owns root files and `docs/`.
- Do not run two tasks that mutate Git state concurrently.
- Do not touch sibling folders or repositories. Load the ignored local exclusion file when candidate work is selected; its entries are sponsor-designated frozen historical artifacts.
- A pivot is a control-task decision. Before replacement-workstream writes, append the decision,
  establish a new charter and write scope, and preserve every existing safety and external-action
  gate. Historical work and logs remain intact.

## Required conduct

- Prefer primary evidence and record exact commit SHAs, dates, commands, tests, and source links.
- Verify repository license, contribution guide, code of conduct, security policy, CLA/DCO, and AI-contribution rules before preparing upstream work.
- Never publish suspected vulnerabilities. Use the upstream private security channel and pause for the human where identity or attestation is required.
- Run untrusted third-party code only in a disposable, unprivileged environment with no secrets, wallets, home-directory mounts, Docker socket, production credentials, or homelab access.
- No scraping for unsolicited marketing, promotional issues, automated PR floods, fake accounts, fake testimonials, fake engagement, token promotion, or claims of guaranteed outcomes.
- Never store passwords, API keys, cookies, wallet seeds, recovery codes, customer private data, or KYC/tax records here or in chat.
- Credentials live in the sponsor's password manager and are exposed only through least-privileged, revocable access.

## Usage policy

The sponsor reports allowance resets. When available, read the signed-in product Usage page before
and after substantive work; every reading is still a whole-account snapshot rather than exact
project attribution. Allocate work in a 2:1 impact-to-revenue ratio while both workstreams remain
active. Stop at 40% remaining, leaving a 15-point overrun buffer above the sponsor's protected 25%,
and start no long or multi-agent unit below 50%. A limit warning or lower sponsor-reported reading
stops work immediately.

Use Sol for architecture, ambiguous decisions, security-sensitive judgments, and final validation; Terra for routine implementation and documentation review; Luna for bounded inventory, extraction, classification, and repetitive checks when available.
