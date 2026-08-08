# Support Agent Regression Lab charter

- Status: accepted
- Phase: prototype validation
- Started: 2026-08-08

## Mission

Earn the first lawful project dollar by helping a small team detect support-agent behavior
regressions before users do. Grow only when buyer evidence and cleared revenue justify the next
product, channel, or expense.

## Buyer and problem

Initial buyers are small B2B SaaS teams maintaining a text support assistant and changing prompts,
policies, knowledge sources, or model versions. The first outcome is catching policy-grounding,
unauthorized-commitment, escalation, ambiguity, and multi-turn regressions before publishing a
change. It does not pretend that subjective quality is fully automatable.

## Product boundary

- Public prototype: ten original synthetic support cases, strict JSONL inputs, deterministic
  assertions, explicit human-review fields, two mocked runs, and reproducible JSON/Markdown output.
- A separately acknowledged `sanitized-local` mode can compare test outputs prepared outside this
  tool from synthetic prompts and sanitized, customer-approved public policy material. The tool
  still performs no upload, model call, integration, or provenance/reviewer authentication.
- Proposed paid hypotheses: $49 reusable template; $149 fixed ten-case custom pilot from one
  approved public policy source. The pilot handoff is a versioned archive containing ten JSONL
  cases, the rubric, one response-free comparison template, and one revision. The proposed window
  is five business days after written scope approval and receipt of the approved source; one
  consolidated revision is due within three business days of feedback received within seven
  calendar days. A 30-case pack or recurring refresh waits for measured delivery time and repeat
  demand.
- No model calls, production bot access, credentials, private transcripts, personal data, customer
  databases, tracking scripts, or paid API are required for the prototype.
- No medical, legal, financial, employment, insurance, or other regulated-domain evaluation at
  launch. No penetration testing, vulnerability research, compliance/certification claim,
  accuracy guarantee, deployment gate, or automated production decision.
- Synthetic mocked runs are always labeled. Deterministic failures and human judgments are
  reported separately.

## Decision rights and economics

The AI chooses cases, taxonomy, evaluator design, reports, price/channel experiments, copy, and
pivots. The human participates only for identity, terms, KYC/tax, merchant, credential, contract,
payment, or account-recovery actions.

Launch spend is $0. Existing XLM is not funding. No paid tool, domain, model/API credit, or plan
upgrade is eligible before D-019's cleared-revenue, repeat-coverage, reserve, and reversion test.

## Validation and pivot rule

Publish a useful free starter before requesting payment. Prices are hypotheses until a real buyer
acts. Track qualified page views as views rather than unique people unless the platform proves
uniqueness; record nonbinding interest separately from orders and cleared receipts.

A qualified view is a view of a unique, unlisted channel-entry Markdown path recorded in GitHub
Traffic's Popular content table during that path's declared activation window. Each external
channel gets a separate entry path before its link is used. Record the UTC window, path, channel,
raw views, and manually logged owner previews at least once every 14 days; qualified views are raw
views minus those previews. Direct README/repository traffic, aggregate repository views, referrer
totals, CI, and paths with no retained GitHub record do not count. GitHub's aggregate data cannot
prove a viewer's identity, intent, or uniqueness or exclude every bot, so these remain views - not
people - and the separate human-interest gate is mandatory.

At 45 calendar days or 100 qualified views, whichever comes first, require at least three genuine
inbound interest signals and one explicit request to buy or commission the ten-case pilot. The
nonbinding interest form records buyer role, desired outcome, and discovery channel without
accepting private data or payment. If the gate fails, change buyer, problem, product, channel, or
price before adding infrastructure. After three paid deliveries, compare actual time, rework,
support burden, refunds, satisfaction, and net margin before automating or expanding.
