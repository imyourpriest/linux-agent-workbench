# Patch Cabinet initial issue shortlist

- Observed: 2026-08-08, 01:31-01:36 MDT
- Research mode: public and read-only
- Outcome: one issue survived manual hard-gate screening
- Policy disposition: eligible for investigation, not ready for implementation

The search was deliberately narrow. No target repository was cloned, downloaded, or executed; no
account was created; no issue, pull request, reaction, assignment, or comment was made. The ignored
operator exclusion file was applied as an explicit local policy input. Its contents are not included
here.

## Shortlist

### 1. Creator Toolkit CLI issue 18 - document the immutable GitHub Release workflow

- Repository: [HoungDev/creator-toolkit-cli](https://github.com/HoungDev/creator-toolkit-cli)
- Issue: [Document the immutable GitHub Release workflow](https://github.com/HoungDev/creator-toolkit-cli/issues/18)
- Exact reviewed commit: [`7fbc4b1af8f074a921f4254f6d89225d612d7a3b`](https://github.com/HoungDev/creator-toolkit-cli/commit/7fbc4b1af8f074a921f4254f6d89225d612d7a3b)
- Repository activity recorded at that commit: 2026-08-07
- License: [MIT at the reviewed commit](https://github.com/HoungDev/creator-toolkit-cli/blob/7fbc4b1af8f074a921f4254f6d89225d612d7a3b/LICENSE)
- Policy result: `investigate`, score 65
- Estimated focused scope: two hours, before upstream execution or review time

#### Evidence that survived

- GitHub showed a public, non-archived repository with `main` as its default branch. The reviewed
  commit is the latest default-branch commit observed during this work unit.
- Issue 18 was open, unassigned, had no comments, and carried `documentation`, `help wanted`, and
  `good first issue` labels. Its body limits the work to `docs/releasing.md`, requires safe
  placeholders, and explicitly says that completing the issue must not create a release.
- The project describes itself as a Python console CLI tested on Linux, macOS, and Windows. This
  documentation issue is therefore Linux-ecosystem-facing rather than Linux-exclusive. See the
  pinned [README](https://github.com/HoungDev/creator-toolkit-cli/blob/7fbc4b1af8f074a921f4254f6d89225d612d7a3b/README.md)
  and [package metadata](https://github.com/HoungDev/creator-toolkit-cli/blob/7fbc4b1af8f074a921f4254f6d89225d612d7a3b/pyproject.toml).
- The pinned [contributor guide](https://github.com/HoungDev/creator-toolkit-cli/blob/7fbc4b1af8f074a921f4254f6d89225d612d7a3b/CONTRIBUTING.md)
  welcomes focused documentation work and records `ruff`, `pytest`, build, and package checks. The
  [pull-request template](https://github.com/HoungDev/creator-toolkit-cli/blob/7fbc4b1af8f074a921f4254f6d89225d612d7a3b/.github/PULL_REQUEST_TEMPLATE.md)
  requests exact validation evidence. A code of conduct and a private security-reporting policy
  were also present at the reviewed commit.
- The visible pull-request queue contained one open item, [PR 25](https://github.com/HoungDev/creator-toolkit-cli/pull/25),
  which closes issue 15 rather than issue 18. The merged release-preparation
  [PR 24](https://github.com/HoungDev/creator-toolkit-cli/pull/24) explicitly left issues 15 and 18
  open for contributors. No assignee, claim comment, or linked pull request was visible for issue 18.
- Static review found no need for secrets, production access, network probing, target execution, or
  security-sensitive behavior. Conventional AI-policy, CLA, and DCO files were not present in the
  pinned tree, and neither the contributor guide nor pull-request template imposed a personal
  attestation.

#### Uncertainty and stop points

- No explicit upstream AI-contribution rule was found. The manifest therefore records `ai_policy`
  as `unknown`; project policy keeps the issue in `investigate` and forbids treating it as ready.
- The contributor guide asks contributors to comment with an intended approach before investing
  significant time. No contact was made. That future signal and any first-canary publication step
  remain separate external actions.
- The repository and contributor workflow are very new, so maintainer responsiveness and review
  stability are unproven. This is a ranking caution, not evidence of wrongdoing.
- GitHub Release immutability and `gh release verify*` behavior are time-sensitive. Any future patch
  must re-check current official GitHub documentation rather than rely on the issue text alone.
- Scope and tests were estimated from static public evidence only. The issue, assignee, linked pull
  requests, default-branch HEAD, license, and policies must be revalidated immediately before any
  future implementation unit.

## Rejected near-misses

- [Creator Toolkit CLI issue 15](https://github.com/HoungDev/creator-toolkit-cli/issues/15) was
  rejected after a contributor claimed it and opened [PR 25](https://github.com/HoungDev/creator-toolkit-cli/pull/25).
- [pydoit issue 400](https://github.com/pydoit/doit/issues/400) was inviting and plausibly bounded,
  but it is an enhancement to custom command-line parsing. Classifying it as a Season 1 bug fix or
  portability task would overstate the evidence, so it was not put into the policy manifest.
- [yq issue 1803](https://github.com/mikefarah/yq/issues/1803) was rejected because credible armel
  validation depends on target-specific hardware behavior and the existing report includes a
  segmentation-fault uncertainty; a six-hour verified result is not supportable from current
  evidence.
- [VisiData issue 2313](https://github.com/saulpw/visidata/issues/2313) was rejected because the
  contribution process requires copyright assignment and a human vouching/AI-disclosure step.
- [rich-click issue 330](https://github.com/ewels/rich-click/issues/330) was rejected because the
  maintainer discussion describes an upstream compatibility problem whose durable solution is not
  credibly bounded to six focused hours.
- [gum issue 818](https://github.com/charmbracelet/gum/issues/818) was rejected as a broad request to
  add tests across inadequately tested code rather than a reviewable six-hour patch.

## Local artifacts

- Candidate manifest: `../data/candidates/2026-08-08-initial-shortlist.json`
- Policy JSON: `2026-08-08-initial-shortlist-policy.json`
- Policy Markdown: `2026-08-08-initial-shortlist-policy.md`

The generated policy artifacts are evidence of deterministic ranking, not a substitute for the
manual checks and uncertainty recorded above.
