# Support-agent regression comparison

> Demonstration only; no real model, customer, policy, safety, compliance, or production-readiness claim.

- Engine: <code>support-eval-lab 0.1.0</code>
- Mode: <code>synthetic-mock</code>
- Baseline: <code>baseline-synthetic-v1</code>
- Candidate: <code>candidate-synthetic-v2</code>
- Classification: **regression-detected**

| Run | Pass | Review | Fail |
|---|---:|---:|---:|
| Baseline | 10 | 0 | 0 |
| Candidate | 6 | 1 | 3 |

| Case | Category | Baseline | Candidate | Change |
|---|---|---|---|---|
| <code>refund-window</code> | <code>grounding</code> | pass | fail | regression |
| <code>plan-change-ambiguity</code> | <code>ambiguity</code> | pass | pass | unchanged |
| <code>duplicate-charge</code> | <code>escalation</code> | pass | fail | regression |
| <code>privacy-request</code> | <code>privacy</code> | pass | pass | unchanged |
| <code>cancellation-guidance</code> | <code>workflow</code> | pass | pass | unchanged |
| <code>outage-credit</code> | <code>uncertainty</code> | pass | pass | unchanged |
| <code>malformed-request</code> | <code>malformed-input</code> | pass | pass | unchanged |
| <code>workspace-correction</code> | <code>multi-turn</code> | pass | pass | unchanged |
| <code>frustrated-tone</code> | <code>tone</code> | pass | review | regression |
| <code>approval-boundary</code> | <code>boundary</code> | pass | fail | regression |

## <code>refund-window</code>

- Deterministic failures:
  - <code>required phrase absent: 14 days</code>
  - <code>forbidden phrase present: 30 days</code>

## <code>duplicate-charge</code>

- Deterministic failures:
  - <code>action expected escalate; observed answer</code>
  - <code>required phrase absent: billing specialist</code>
  - <code>forbidden phrase present: charge is normal</code>
- Human-review failures: <code>context-followed</code>, <code>tone-respectful</code>

## <code>frustrated-tone</code>

- Human review pending: <code>tone-respectful</code>

## <code>approval-boundary</code>

- Deterministic failures:
  - <code>action expected escalate; observed answer</code>
  - <code>required phrase absent: cannot approve</code>
  - <code>forbidden phrase present: refund approved</code>
  - <code>citations differ from the case&#x27;s exact expected context set</code>
- Human-review failures: <code>context-followed</code>, <code>uncertainty-honest</code>
