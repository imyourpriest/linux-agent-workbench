# Support Agent Regression Lab

This prototype turns expected support-agent behavior into a small, repeatable regression suite. It
compares two structured runs with explicit example or operator-supplied human-review labels and
reports assertion failures, unresolved review, regressions, and improvements without calling a
model or customer system.

The included ten-case starter and both runs are original synthetic fixtures. They demonstrate the
workflow; they are not evidence about a real model, company, policy, or production bot.

## Run the synthetic comparison

Linux/macOS:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
support-eval compare samples/cases.jsonl samples/baseline.jsonl samples/candidate.jsonl \
  --json-out samples/comparison.json --markdown-out samples/comparison.md
python -m unittest discover -s tests -v
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
support-eval compare samples\cases.jsonl samples\baseline.jsonl samples\candidate.jsonl `
  --json-out samples\comparison.json --markdown-out samples\comparison.md
python -m unittest discover -s tests -v
```

## What the checker establishes

- strict, bounded JSONL inputs with duplicate-key and unknown-field rejection;
- exact action, required/forbidden phrase, and citation checks;
- visibly separate human-review fields;
- complete case coverage and deterministic before/after classification;
- escaped, reproducible JSON and Markdown reports.

It does not establish factual correctness, policy completeness, safety, compliance, production
readiness, customer satisfaction, or revenue potential. Read the [charter](CHARTER.md),
[review rubric](RUBRIC.md), [buyer quickstart](BUYER_QUICKSTART.md),
[offer hypothesis](OFFER.md), [claims boundary](LEGAL_AND_CLAIMS.md), and [log](LOG.md).

The separate [channel-observation normalizer](OBSERVATION_RECORDS.md) validates only a strict,
minimal operator-recorded experiment file. It pins the registered configuration hash, derives
configuration agreement from explicit observed fields, rejects duplicate issues and late final
captures, and subtracts previews only within each exact retained window. It performs no network
access, never accepts issue text or screenshots, does not add rolling traffic snapshots, and emits
`null` rather than zero when an exact retained path row is absent. Its current activation report
is reproducible with:

```sh
python -m support_eval_lab.observation \
  experiments/sel-gh-001.json observations/sel-gh-001-window.json \
  --as-of 2026-08-09T00:50:13Z \
  --json-out samples/channel-observation.json \
  --markdown-out samples/channel-observation.md
```

## Non-activated policy-starter pack

The [`policy-starter/`](policy-starter/) subtree is a fully synthetic, reserved
`example.invalid` **AI Contribution Policy Starter + Audit** hypothesis. Its strict manifest and
verifier-owned checked-tree SHA-256 constants jointly bind an exact flat inventory: scope/readme,
one declaration record, a decision matrix, cautious
`CONTRIBUTING` snippet, issue/PR checklist, ten-point evidence-linked audit, and asynchronous
handoff. Validate it offline and regenerate the deterministic receipt with:

```sh
python -m support_eval_lab.policy_starter policy-starter \
  --json-out samples/policy-starter-validation-receipt.json
maintainer-policy-declaration validate \
  policy-starter/mpd-v1-cb8c158f561d0387ddb6059fa1fe43038a988c27ec2982cc07bdc79f2b301d37.json
```

The pack is not activated. `$79` is one unvalidated hypothesis, not a listing or price promise.
No checkout, payment, customer input, identity/authority verification, legal advice, AI-use
detection, compliance result, or enforcement guarantee exists. The receipt hashes are only
recomputable consistency fingerprints, not signatures or authentication.
The verifier-owned constants are local checked-tree policy, not signatures or an external trust
anchor, and changing the example requires an intentional verifier release and review.
# Inert policy release experiment

The isolated `policy-release-experiment/` is an inert post-SEL draft only. Regenerate it with
`python -m support_eval_lab.policy_release --project .` and check freshness with `--check`.
Neither command contains activation or network behavior. The earliest date is not authorization;
all final SEL capture, independent completeness, frozen/no-incident, final review, exact digest,
and future control-decision gates remain mandatory. It is not a listing, sale, demand result,
adoption claim, or GitHub release, and revenue remains `$0.00`.
The experiment directory is trusted-local scope. Generation and validation reject links and
irregular directories and use exclusive random staging, but do not claim protection if an
adversary can replace the trusted parent after inspection.
