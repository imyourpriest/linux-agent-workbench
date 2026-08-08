# External-action policy

- Status: accepted
- Effective: 2026-08-07

This file distinguishes broad project delegation from confirmations that must happen at the moment of action.

| Action | Default | Required evidence or confirmation |
|---|---|---|
| Public web/repository research | Proceed | Record sources; honor access limits and terms |
| Local implementation and tests | Proceed | Stay within workspace and isolation policy |
| Draft public copy or contribution | Proceed | Claims linked to evidence; no private data |
| Execute third-party code | Proceed only in isolation | Disposable, unprivileged environment; no secrets, wallets, Docker socket, homelab, or production access |
| Publish project-owned source repository | Allowed after launch gate | Passing tests, clean secret scan, license, public-log review, authenticated owner, and enabled private vulnerability reporting |
| First upstream pull request | Canary gate | Eligible repository, contribution-policy review, tested patch, clear AI-assistance disclosure; human handles any CLA/DCO attestation |
| Later routine upstream pull requests | Proceed under Patch Cabinet policy | Same evidence; no vulnerability, controversy, mass automation, or identity attestation |
| Create external account or organization | Human checkpoint | Human owns it, accepts terms, supplies truthful identity/recovery data, and enables MFA |
| Save or use credentials | Human checkpoint | Password manager only; least privilege; never copied into repository/chat/logs |
| Create social post or marketing campaign | First-channel checkpoint | Accurate identity/disclosure; platform rules; no spam, scraping, fake engagement, or unsolicited bulk contact |
| Buy domain, service, credits, or subscription | Per-purchase checkpoint | Exact total/renewal/owner/refund terms shown; cleared project revenue available |
| Accept first customer payment | Human/legal checkpoint | Merchant/KYC/tax owner established; offer terms, privacy, refund, scope, and records ready |
| Access private customer repository | Not allowed at launch | Separate reviewed contract, least privilege, retention/deletion, incident response, and isolated environment |
| Publish security finding | Never publicly by default | Use upstream private security process and coordinated disclosure |
| Send XLM or other crypto | Per-transfer checkpoint | Dedicated project wallet, tax record, exact destination/purpose, human co-sign; existing wallet seed never exposed |
| Hold, pool, exchange, forward, or escrow customer funds | Prohibited | None |
| Legal, compliance, penetration-test, or security certification claim | Prohibited | None; only bounded maintenance/release-readiness evidence |

## Launch gate for public source

Before first publication:

1. Tests pass from a clean checkout.
2. Secret and private-data review passes.
3. License, contribution policy, security policy, and AI disclosure exist.
4. Generated examples contain synthetic or intentionally public data only.
5. Decision and project logs accurately describe what happened.
6. The target account and owner are confirmed without sharing credentials.
7. A usable private vulnerability-reporting route is enabled and tested without sensitive content.
8. Dependabot alerts, secret scanning and push protection, and code scanning are enabled where
   GitHub makes them available; any unavailable control is documented rather than implied.
9. The default branch requires the hosted CI checks and blocks force pushes and deletion before
   outside contributions are accepted.

## Revenue gate

Before first sale:

1. For any real repository report or review, pass the D-014 disposable acquisition and network-disabled analysis gate; the trusted-local demo is not eligible for customer source.
2. Verify the owner's jurisdiction and any trade-name/entity/license obligations.
3. Establish user-owned merchant, tax, and bookkeeping records.
4. Publish scope, limitations, price, delivery conditions, refund policy, privacy/retention terms, and contact route.
5. Test checkout, cancellation/refund, delivery, deletion, and support flows.
6. Never describe a purchase as a charitable donation unless a qualified organization is actually involved.
