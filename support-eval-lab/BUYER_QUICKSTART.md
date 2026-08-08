# Buyer quickstart for a sanitized local comparison

This path is for synthetic test prompts and public policy material only. The checker runs locally
and invokes no model, network client, subprocess, upload, or customer system.

## Prepare safely

1. Choose one public policy source you own or are authorized to use.
2. Write up to ten synthetic user prompts. Do not copy production conversations.
3. Remove names, emails, account/order IDs, URLs with private tokens, credentials, internal host
   names, confidential incidents, regulated-domain material, and third-party copyrighted text.
4. Create cases using `samples/cases.jsonl` as the shape. Keep exact assertions narrow and put
   meaning/tone/context decisions in `human_checks`.
5. Obtain baseline and candidate responses in your own approved test environment. Paste only the
   sanitized response, declared action, public-context citations, and rubric labels into JSONL.
6. Review every label under [RUBRIC.md](RUBRIC.md). Use `not-reviewed` when uncertain.

## Compare

```sh
support-eval compare-local cases.jsonl baseline.jsonl candidate.jsonl \
  --acknowledge-sanitized-local-input \
  --json-out comparison.json --markdown-out comparison.md
```

The separate local command never writes response text into its reports; it records only response
hashes and results. The acknowledgement means you confirmed the files contain no private
transcript, personal data, credential, regulated content, or confidential material. A small
obvious-pattern preflight can reject common mistakes, but it is not a data-loss-prevention system
and does not authenticate the reviewer. A response hash is an identifier, not a confidentiality
guarantee; short or predictable responses may be guessable. Do not send run JSONL files to this
project.

Interpret `fail` as a concrete assertion or human-review failure, `review` as unresolved human
judgment, and `pass` only as "this one case cleared its declared checks." Never infer that a passing
sample proves production readiness or the absence of other regressions.
