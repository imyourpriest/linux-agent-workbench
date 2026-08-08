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

The included candidate is synthetic. `--allow-no-local-exclusions` is only for a public/demo installation with no sponsor-local denylist. Every project candidate run must explicitly pass the operator-controlled ignored file with `--exclusions-file ../.private/patch-cabinet-exclusions.json`; repeat the option to union additions. The tool never discovers an exclusion file from a target repository. Missing context fails closed unless the public/demo flag is explicit, and excluded names are redacted from output. No claim about a real repository is made until its facts are checked at a recorded commit and date. An unknown AI-contribution policy or required personal attestation keeps a candidate in `investigate`; it cannot be emitted as `ready`.

JSON output is wrapped in a versioned envelope containing the engine version, policy version, deterministic as-of date/mode, policy-source hash, and dependency version. Live observations must be no more than seven days old. Candidate activity age is derived from `last_activity_at`; it is not accepted as an independent assertion. A past `--as-of` requires `--historical-demo`, and historical output can never be labeled `ready`.

## Success measures

- maintainer-accepted patches and documented upstream outcomes;
- regression-free test evidence;
- reviewer burden kept proportionate to patch value;
- no secrets, policy violations, spam, public vulnerability leakage, or edits to excluded repositories;
- support revenue, if any, covers only documented project costs before expansion.

Read [the charter](CHARTER.md), [candidate policy](CANDIDATE_POLICY.md), and [project log](LOG.md) before selecting work.
