# Usage ledger

This is an allocation ledger, not a claim of exact token accounting.

Official product behavior makes exact consumption task-dependent: model, context, reasoning, tool use, retrieval, and caching all affect usage. A sponsor-reported product-dashboard reading is the only available global capacity signal; the agent cannot read it continuously or attribute concurrent use. A work unit records one bounded, substantive project outcome and maintains the sponsor's requested 2:1 ratio; it does not equal a fixed number of messages, tokens, or credits.

## Policy

- Patch Cabinet allocation: 50% of each sponsor-reported weekly allowance.
- Release Readiness Lab allocation: 25%.
- Sponsor reserve: 25%, never intentionally consumed by these projects.
- Scheduling ratio: two Patch Cabinet work units for each Release Readiness Lab work unit over a reset period.
- Shared governance work is allocated 2/3 to Patch Cabinet and 1/3 to Release Readiness Lab.
- Stop starting new turns when the sponsor reports 25% remaining, a usage warning appears, or the sponsor reports project capacity exhausted.
- The sponsor reports resets; the ledger records them without inventing a timestamp or percentage.

## Reset periods

### R-001 — reported 2026-08-07

- Starting capacity: sponsor reported 100% immediately before launch.
- Reserved capacity: 25%.
- Patch Cabinet ceiling: 50 percentage points of the starting allowance.
- Release Readiness Lab ceiling: 25 percentage points of the starting allowance.
- Ending UI reading: not reported; the agent cannot independently attribute concurrent global usage.

| Date | Workstream | Work units | Outcome | Actual dashboard delta |
|---|---:|---:|---|---:|
| 2026-08-07 | Patch Cabinet | 2 | Launch governance, candidate policy, MVP scaffold, and verification | unknown |
| 2026-08-07 | Release Readiness Lab | 1 | Market pivot, offer charter, MVP scaffold, and verification | unknown |
| 2026-08-08 | Patch Cabinet | 2 | Privacy, policy, provenance, and reproducibility hardening | unknown |
| 2026-08-08 | Release Readiness Lab | 1 | Provenance fail-closed redesign, terms correction, and adversarial probes | unknown |
| 2026-08-08 | Patch Cabinet | 2 | Explicit exclusion trust boundary, strict input handling, and final verification | unknown |
| 2026-08-08 | Release Readiness Lab | 1 | Trusted-demo isolation, bounded enumeration, and operative acquisition gate | unknown |

Do not backfill an “actual” delta from message count. When the sponsor supplies before/after UI readings, record them as sponsor-reported and preserve ambiguity caused by unrelated or concurrent ChatGPT use.
