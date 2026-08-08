# Patch Cabinet candidate ranking

Input label: <code>synthetic.json</code>
Engine: <code>patch-cabinet 0.1.0</code>
Policy: <code>season-1.2</code>
Policy as-of: <code>2026-08-07</code>
Evaluation mode: <code>historical</code>
Policy source SHA-256: <code>f65055c2c771296958b4bc6fc464ba79f48af756b6d2a47404ca78042bc7582a</code>

> A score measures Season 1 fit, not project quality. Facts require manual verification.

| Rank | Repository | Status | Score | Observed | Commit |
|---:|---|---|---:|---|---|
| 1 | <code>example-linux/quiet-cli</code> | investigate | 95 | <code>2026-08-07</code> | <code>0123456789ab</code> |

## <code>example-linux/quiet-cli</code>

- Eligibility: **yes**
- Band: <code>investigate</code>
- Score: <code>95</code>
- License: <code>MIT</code>
- Issue: <code>https://example.invalid/example-linux/quiet-cli/issues/12</code>
- Reasons:
  - explicit issue invites the work
  - Linux relevance is direct
  - estimated scope is 2 hours
  - last recorded activity was 14 days before observation
- Cautions:
  - upstream AI-contribution policy is unknown
  - historical evaluation cannot be labeled ready
- Score trace:
  - maintainer signal: +30
  - Linux relevance: +20
  - reproduction recorded: +15
  - automated tests recorded: +10
  - activity recency: +10
  - bounded scope: +10
  - contribution guide recorded: +5
  - AI policy unknown: -5
