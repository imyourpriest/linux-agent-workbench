# Patch Cabinet

Patch Cabinet is an AI-directed, human-accountable effort to make small, useful improvements to Linux and open-source projects.

It is not a pull-request volume machine. The product is a sequence of well-chosen patches whose scope, evidence, tests, upstream rules, review burden, and outcome remain inspectable.

## Season 1

Initial target class:

- public, explicitly licensed repositories;
- user-space Go or Python tools that run on Linux;
- an issue or maintainer signal clearly inviting help;
- a reproducible, bounded fix estimated at six hours or less;
- recent maintainer activity and a usable test path;
- no suspected security vulnerability or sensitive subsystem.

The first season ends after ten upstream outcomes—accepted, rejected, closed, or intentionally withdrawn—and produces a retrospective before the policy expands.

## MVP

The current MVP is a deterministic candidate-policy engine. It consumes a manually verified JSON manifest, rejects ineligible work, scores eligible candidates, and emits an auditable Markdown/JSON cabinet. It deliberately does not use a GitHub token or execute third-party code.

Linux/macOS:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
patch-cabinet score data/candidates/synthetic.json --as-of 2026-08-07 --historical-demo --allow-no-local-exclusions --markdown-out out/cabinet.md --json-out out/cabinet.json
python -m unittest discover -s tests -v
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
patch-cabinet score data\candidates\synthetic.json --as-of 2026-08-07 --historical-demo --allow-no-local-exclusions --markdown-out out\cabinet.md --json-out out\cabinet.json
python -m unittest discover -s tests -v
```

The included candidate is synthetic. `--allow-no-local-exclusions` is only for a public/demo installation with no sponsor-local denylist. Every project candidate run must explicitly pass the operator-controlled ignored file with `--exclusions-file ../.private/patch-cabinet-exclusions.json`; repeat the option to union additions. The tool never discovers an exclusion file from a target repository. Missing context fails closed unless the public/demo flag is explicit, and excluded names are redacted from output. No claim about a real repository is made until its facts are checked at a recorded commit and date. An unknown AI-contribution policy is ineligible because absence of a prohibition is not consent. A required personal attestation keeps an otherwise eligible candidate in `investigate`; it cannot be emitted as `ready`.

JSON output is wrapped in a versioned envelope containing the engine version, policy version, deterministic as-of date/mode, policy-source hash, and dependency version. Schema 2 also exposes the controlled AI-workflow consent status and basis plus a same-repository policy URL pinned at the candidate commit. The validator checks that binding; manual review remains responsible for interpreting the source text. Live observations must be no more than seven days old. Candidate activity age is derived from `last_activity_at`; it is not accepted as an independent assertion. A past `--as-of` requires `--historical-demo`, and historical output can never be labeled `ready`.

Published evidence remains replayable through hash-pinned, offline engine capsules. From the
repository root, run `python tools/check_evidence_bundles.py`; see the
[versioned verifier design](verifiers/README.md) for the trust boundary and migration rules.

The separate [contribution-consent catalog](CONSENT_CATALOG.md) preserves strict, commit-pinned
manual reviews of upstream policy files, including explicit rejects and insufficient rules. It is
historical evidence, not an automatic permission or eligibility source. Regenerate its
deterministic index with:

```sh
python -m patch_cabinet.consent_catalog data/consent-catalog/v1 --as-of 2026-08-10 \
  --json-out samples/consent-catalog-index.json \
  --markdown-out samples/consent-catalog-index.md
```

The separate [manual policy-profile catalog](POLICY_PROFILE_CATALOG.md) records eight controlled,
manually normalized dimensions bound to those consent records. It is historical evidence only and
has no engine authority. Regenerate it with:

```sh
python -m patch_cabinet.policy_profile_catalog data/policy-profile-catalog/v1 \
  --consent-records data/consent-catalog/v1 \
  --json-out samples/policy-profile-catalog-index.json \
  --markdown-out samples/policy-profile-catalog-index.md
```

The [maintainer policy declaration prototype](MAINTAINER_POLICY_DECLARATION.md) renders explicitly
supplied trusted-local declaration JSON into deterministic review cards. Accepted project records
are maintainer- or operator-supplied and unauthenticated/unverified; validation does not establish
identity or authority. It is a 30-day local/public prototype, not a standard, permission source,
candidate-engine input, or CI gate.

```sh
python -m patch_cabinet.maintainer_policy_declaration render \
  data/maintainer-policy-declarations/synthetic/v1 \
  --json-out samples/maintainer-policy-declaration-index.json \
  --markdown-out samples/maintainer-policy-declaration-index.md
python -m patch_cabinet.maintainer_policy_declaration starter \
  unverified_project_declaration
```

## Success measures

- maintainer-accepted patches and documented upstream outcomes;
- regression-free test evidence;
- reviewer burden kept proportionate to patch value;
- no secrets, policy violations, spam, public vulnerability leakage, or edits to excluded repositories;
- support revenue, if any, covers only documented project costs before expansion.

Read [the charter](CHARTER.md), [candidate policy](CANDIDATE_POLICY.md), and [project log](LOG.md) before selecting work.
