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
