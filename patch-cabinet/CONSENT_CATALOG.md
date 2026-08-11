# Contribution-consent catalog

This catalog preserves bounded manual reviews of exact public upstream policy files. It exists to
avoid repeatedly rediscovering the same policy distinction and to make rejected as well as
permitted classifications inspectable.

It is not a permission directory. A record is historical evidence about one file at one commit.
The validator checks strict provenance shape, dates, successor chains, and deterministic output;
it does not fetch the source, understand prose, authenticate a maintainer, or make a candidate
eligible. A current candidate review must still re-check the repository, policy, issue, competing
work, attestation, security, task scope, and sponsor-local exclusions. Records older than seven
days at the explicit index date are marked stale rather than removed.

## Review and update protocol

1. Read the public policy at an exact repository commit without executing target code.
2. Hash the exact source bytes and record a short non-quoting manual rationale.
3. Classify only the exact Patch Cabinet workflow:
   `agent_selects_prepares_and_submits_with_disclosure`.
4. Add a new immutable JSON record; do not edit a published record to reflect later policy.
5. When policy changes, add one successor with a new commit and source hash. The validator rejects
   missing, cross-repository, forked, or cyclic successor chains.
6. Regenerate both index files and run the Patch and repository verification suites.

`explicitly_allows` requires pinned text that permits this actual workflow. Permission for
human-led AI assistance alone remains `insufficiently_explicit`. An explicit conflict is
`explicitly_disallows`. Neither status authorizes contact or submission by itself.

From `patch-cabinet/`:

```sh
python -m patch_cabinet.consent_catalog data/consent-catalog/v1 \
  --as-of 2026-08-10 \
  --json-out samples/consent-catalog-index.json \
  --markdown-out samples/consent-catalog-index.md
```

The initial records were manually checked through GitHub's public content API. The separate
`data/consent-catalog/ACQUISITION_RECEIPT.json` records the exact retrieval timestamp, commit refs,
API paths, decoded byte lengths, Git blob identifiers, and SHA-256 values. The catalog stores
hashes and pinned links, not copies or excerpts of third-party policy text.

The later Ruff source capture has its own
`data/consent-catalog/RUFF_SOURCE_ACQUISITION_RECEIPT.json`; the initial receipt and its four-source
inventory remain unchanged. Both receipts are retrieval traceability, not signatures or permission.
The validator strictly loads both receipt shapes, bounds their bytes, depth, source count, and
integer byte counts, and binds every source to an exact catalog record and canonical GitHub API
URL. This validates the recorded shape and internal provenance only; it does not authenticate the
remote response or grant permission.

The [manual policy-profile catalog](POLICY_PROFILE_CATALOG.md) is a separate experiment that binds
eight controlled, manually normalized dimensions to exact consent records. It cannot change a
consent classification, candidate result, or authorization boundary.

CLI output parents are trusted local filesystems. Atomic replacement limits partial output, but
the catalog does not claim to resist an adversary replacing an output parent between validation
and writing. Do not direct output into attacker-controlled directories.
