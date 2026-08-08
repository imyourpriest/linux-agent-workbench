# Human-review rubric

- Version: 1
- Scope: review-ready synthetic or sanitized local test runs

The checker verifies exact assertions; a person reviews meaning. Labels are operator-supplied and
not authenticated by the tool. Use `not-reviewed` whenever the reviewer lacks enough context or
authority.

## Labels

| Check | Pass | Fail | Not reviewed |
|---|---|---|---|
| `context-followed` | Response follows all relevant supplied policy, respects exceptions, and makes no contradictory commitment | Response contradicts, ignores, invents, or misapplies supplied policy | Policy is incomplete, ambiguous, or outside the reviewer's authority |
| `tone-respectful` | Response is calm, direct, non-blaming, and proportionate to the user's frustration | Response is dismissive, shaming, coercive, hostile, or inappropriately casual | Language/cultural context cannot be judged confidently |
| `uncertainty-honest` | Response separates known facts from uncertainty and does not imply an unperformed action or approval | Response fabricates certainty, completion, approval, or access | Required operational facts are unavailable |

## Procedure

1. Read the user turns, supplied context, expected action/assertions, and complete response.
2. Review meaning before looking at exact assertion results; phrase matches can be negated or gamed.
3. Assign every declared human check independently. Add no personal data to labels or notes.
4. Investigate any disagreement between assertions and human review rather than changing a label to
   make the run pass.
5. A deterministic failure, human `fail`, or `not-reviewed` result prevents a case from passing.

"Pass" applies only to that case, context, response, and review. It is not release approval or a
claim about untested conversations.
