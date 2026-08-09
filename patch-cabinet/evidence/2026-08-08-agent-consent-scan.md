# Patch Cabinet autonomous-contribution consent scan

- Observed: 2026-08-08
- Research mode: public, read-only, and no target-code execution
- Outcome: no candidate was ready for an autonomous canary pull request
- Policy disposition: one previously recorded issue remains `investigate`; all new near-matches
  failed a manual gate

This scan treated upstream consent as a compatibility requirement, not a hurdle to route around.
No target repository was cloned, downloaded, executed, contacted, assigned, reacted to, or
modified. No issue, pull request, comment, branch, or account action was created. The ignored
operator exclusion file was applied as a local policy input and its contents are not included.

## Revalidated candidate

### Creator Toolkit CLI issue 18 - documentation remains inviting, AI policy remains unknown

- Repository: [HoungDev/creator-toolkit-cli](https://github.com/HoungDev/creator-toolkit-cli)
- Issue: [Document the immutable GitHub Release workflow](https://github.com/HoungDev/creator-toolkit-cli/issues/18)
- Exact reviewed commit: [`7fbc4b1af8f074a921f4254f6d89225d612d7a3b`](https://github.com/HoungDev/creator-toolkit-cli/commit/7fbc4b1af8f074a921f4254f6d89225d612d7a3b)
- License: [MIT at the reviewed commit](https://github.com/HoungDev/creator-toolkit-cli/blob/7fbc4b1af8f074a921f4254f6d89225d612d7a3b/LICENSE)
- Policy result under engine 0.2.0: `investigate`, score 65

The repository remained public and non-archived. Issue 18 remained open, unassigned, uncommented,
and labeled `documentation`, `help wanted`, and `good first issue`. Its bounded scope still forbids
creating a release. The only visible open pull request, PR 25, addressed issue 15 instead. The
[contributor guide](https://github.com/HoungDev/creator-toolkit-cli/blob/7fbc4b1af8f074a921f4254f6d89225d612d7a3b/CONTRIBUTING.md)
still contained no explicit rule that permits this AI-operated contribution workflow, so the
manifest truthfully retains `ai_policy: unknown`. Unknown consent is not implementation consent.

## New near-match reviewed and rejected

### LoopGate Harness issue 2 - explicit AI rules, but no bounded remaining patch

- Repository: [rxdt/loopgate_harness](https://github.com/rxdt/loopgate_harness)
- Issue: [Use Mutmut-generated JSON to go mutant-hunting](https://github.com/rxdt/loopgate_harness/issues/2)
- Exact reviewed commit: [`8e5c49be960d656cba5dbae7724d8a6aeef5acb3`](https://github.com/rxdt/loopgate_harness/commit/8e5c49be960d656cba5dbae7724d8a6aeef5acb3)
- License: [MIT at the reviewed commit](https://github.com/rxdt/loopgate_harness/blob/8e5c49be960d656cba5dbae7724d8a6aeef5acb3/LICENSE)

The pinned [contributor guide](https://github.com/rxdt/loopgate_harness/blob/8e5c49be960d656cba5dbae7724d8a6aeef5acb3/CONTRIBUTING.md)
explicitly expects AI use, makes the contributor responsible, and requires review and relevant
checks. The pinned [agent rules](https://github.com/rxdt/loopgate_harness/blob/8e5c49be960d656cba5dbae7724d8a6aeef5acb3/AGENTS.md)
also define repository, path, test, gate, and handoff boundaries for agents.

The issue was not selected because its original documentation checklist is already marked
complete. The remaining requests are open-ended mutant hunting and deterministic test
strengthening, with no named mutant or bounded acceptance case. A prior contributor also asked to
work on the issue, while the maintainer later invited further work. That combination is a useful
lead, but not a defensible six-hour patch or low-conflict canary without first contacting the
maintainer. Patch Cabinet does not create a promotional or speculative issue comment merely to
manufacture a signal.

## Policy rejects confirmed independently

- [Hugging Face Transformers contribution rules](https://github.com/huggingface/transformers/blob/main/CONTRIBUTING.md)
  currently tell autonomous agents not to create issues or pull requests. A later section permits
  coordinated AI-assisted work, but that does not authorize this autonomous submission workflow.
- [DSPy contribution rules](https://github.com/stanfordnlp/dspy/blob/main/CONTRIBUTING.md)
  welcome disclosed, human-understood AI assistance while separately directing autonomous agents
  not to open pull requests.
- [UltraPlot contribution rules](https://ultraplot.readthedocs.io/en/latest/contributing.html)
  prohibit using AI to resolve an entire good-first issue. That is incompatible with Patch
  Cabinet's intended canary workflow even if the issue itself appears inviting.

These projects were not put into the scoring manifest because they fail scope, Linux-CLI fit, or
workflow-consent gates before ranking. Their treatment also exposed an ambiguity in the current
`ai_policy` label: permission for human-led AI assistance is not necessarily permission for an
AI-operated contribution. A separate append-only policy migration follows this scan; it does not
rewrite this engine 0.2.0 result.

## Local artifacts

- Candidate manifest: `../data/candidates/2026-08-08-agent-consent-scan.json`
- Policy JSON: `2026-08-08-agent-consent-scan-policy.json`
- Policy Markdown: `2026-08-08-agent-consent-scan-policy.md`

Generated ranking is reproducible evidence, not authorization to implement or contact upstream.
