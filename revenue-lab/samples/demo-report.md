# Linux release-readiness evidence report

- Report schema: <code>2</code>
- Collector: <code>linux-release-readiness 0.1.0</code>
- Rules: <code>1.2</code>
- Rules source SHA-256: <code>e4700e171ffc30b3f92b27651572bb8bd1e0800cf99fded52c84e1fce3ea00ae</code>
- Declared repository URL: <code>https://example.invalid/release-readiness/demo-cli</code>
- Declared commit: <code>1111111111111111111111111111111111111111</code>
- Declared observation date: <code>2026-08-07</code>
- Observation source: <code>caller_supplied_for_unverified_demo</code>
- Provenance: <code>unverified_local_demo</code>
- Provenance details:
  - <code>Repository URL, commit, and observation date are caller-supplied labels; no upstream identity was verified.</code>
  - <code>The collector read the supplied local directory without invoking Git or target code.</code>
  - <code>Use only synthetic or trusted staging directories; safe third-party acquisition is intentionally outside this MVP.</code>
- Files considered: 4
- Target code executed: no
- Repository acquisition performed by the collector: no
- Git or target-project commands invoked by the collector: no
- Storage location verified as local rather than network-backed: no

> This report is a static maintenance-readiness observation with the provenance status shown above. Caller-supplied metadata does not establish repository or commit identity. The collector reads only the supplied trusted-local directory and invokes no network client, subprocess, Git command, or target code. It does not test deployed services or constitute a security audit, penetration test, certification, legal opinion, or guarantee. Findings may be incomplete or become stale.

## Summary

- Signals detected: 3
- Signals not detected: 9
- Potential gaps: 0
- Manual-review-only results: 1

No aggregate grade is assigned. Applicability and repair value require maintainer judgment.

## License-file signal

- ID: <code>license</code>
- Status: <code>signal_detected</code>
- Review priority: <code>manual_review</code>
- Evidence:
  - <code>LICENSE</code>
- Next step: Confirm the signal&#x27;s applicability and correctness manually at the declared commit.

## Go or Python package-metadata signal

- ID: <code>package-metadata</code>
- Status: <code>signal_detected</code>
- Review priority: <code>manual_review</code>
- Evidence:
  - <code>pyproject.toml</code>
- Next step: Confirm the signal&#x27;s applicability and correctness manually at the declared commit.

## Changelog or release-note-history signal

- ID: <code>changelog</code>
- Status: <code>not_detected</code>
- Review priority: <code>medium</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: add a maintained changelog or documented generated-release-note workflow.

## Continuous-integration configuration signal

- ID: <code>ci</code>
- Status: <code>not_detected</code>
- Review priority: <code>high</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: add a least-privileged CI workflow for the project&#x27;s supported test matrix.

## Automated release-workflow signal

- ID: <code>release-workflow</code>
- Status: <code>not_detected</code>
- Review priority: <code>high</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: add a reviewed tag/manual release workflow with minimal permissions and rollback notes.

## Linux amd64 and arm64 artifact signals

- ID: <code>linux-architectures</code>
- Status: <code>not_detected</code>
- Review priority: <code>high</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: configure and test Linux amd64 and arm64 release artifacts where supported.

## Release-checksum signal

- ID: <code>checksums</code>
- Status: <code>not_detected</code>
- Review priority: <code>medium</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: generate and publish checksums for downloadable release artifacts.

## SBOM-generation signal

- ID: <code>sbom</code>
- Status: <code>not_detected</code>
- Review priority: <code>medium</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: generate an SBOM in a documented format as part of the release workflow.

## Provenance or attestation signal

- ID: <code>provenance</code>
- Status: <code>not_detected</code>
- Review priority: <code>low</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: evaluate an appropriate provenance or artifact-attestation step.

## Installation-instruction signal

- ID: <code>install</code>
- Status: <code>signal_detected</code>
- Review priority: <code>manual_review</code>
- Evidence:
  - <code>README.md:5</code>
- Next step: Confirm the signal&#x27;s applicability and correctness manually at the declared commit.

## Uninstall or removal-instruction signal

- ID: <code>uninstall</code>
- Status: <code>not_detected</code>
- Review priority: <code>low</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: document how users can remove installed files and reverse setup changes.

## Automated-test-file signal

- ID: <code>tests</code>
- Status: <code>not_detected</code>
- Review priority: <code>high</code>
- Evidence:
  - none detected by the static collector
- Next step: First confirm applicability with the maintainer. If applicable: add automated validation for release-critical behavior before changing automation.

## GitHub Actions immutable-pin signal

- ID: <code>pinned-actions</code>
- Status: <code>manual_review</code>
- Review priority: <code>low</code>
- Evidence:
  - none detected by the static collector
- Next step: No GitHub Actions workflow was found; review the applicable CI system manually.
