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
