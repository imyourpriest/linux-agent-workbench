# Linux Release Readiness Lab

Linux Release Readiness Lab is a descriptive pre-brand name for an AI-directed, human-owned experiment in earning revenue by fixing Linux release friction for open-source maintainers. A public commercial brand will be selected only after trademark/confusion screening and demand evidence; the earlier `ReleaseMender` working name was retired before publication because it sat too close to the established Linux update brand Mender.

The thesis is deliberately narrower than “AI repository audit”:

> Free evidence surfaces possible release friction for review. Paid work delivers a reviewed plan or a small, maintainer-approved patch that makes a public Go or Python CLI easier to release on Linux.

No domain, merchant account, customer data, private repository access, or paid infrastructure is needed for validation.

## Initial offer

- **Current free synthetic demonstration** — provenance-labeled declared metadata, detected release signals, and potential gaps from project-owned fixture data.
- **Planned free real-repository report** — available only after the D-014 disposable acquisition and network-disabled analysis gate passes.
- **$79 Release Readiness Review** — AI-assisted, owner-accountable review of the generated evidence and a repository-specific implementation plan.
- **$249 Release Repair** — one fixed-scope patch branch by default, such as release automation, Linux amd64/arm64 artifacts, checksums, SBOM generation, or installation documentation. A pull request is opened only when invited and permitted by upstream policy.
- **$499 Linux Launch Bundle** — up to two agreed release/package targets, CI validation, documentation, and one revision.

These are validation prices, not claims of market acceptance. No order is accepted until the revenue gate in the root policy is complete.

## MVP

The MVP is a standard-library static evidence collector for synthetic or trusted project-owned local demonstrations. It reads bounded text files without invoking Git, hooks, build steps, or project commands. Repository URL, commit, and date are declared labels and are always marked unverified. Do not feed a customer or third-party checkout to this demo collector; real repository input waits for the D-014 acquisition gate.

The collector caps entries, files, path depth, per-file bytes, aggregate text, and retained evidence. Its internal deadline is cooperative because filesystem calls can block; a hard wall-clock limit belongs to the future disposable supervisor. The report therefore does not claim that the supplied storage is local or network-disabled.

Verified public reports are intentionally blocked until the project has a disposable, project-controlled acquisition environment that clones upstream without local-object reuse, proves the requested upstream commit, disables network access during analysis, and is independently tested. This boundary is a launch requirement, not a feature implied by the demo.

The [D-014 acquisition and sandbox contract](D014_ACQUISITION_AND_SANDBOX_CONTRACT.md)
now records the threat model, fail-closed platform requirements, and synthetic-only
contract-test scaffold. The scaffold performs no acquisition or isolation and always marks
real-repository use ineligible; passing its tests does not pass the D-014 gate.

```powershell
$env:PYTHONPATH = "src"
python -m release_readiness.cli audit samples/demo-cli --repository-url https://example.invalid/release-readiness/demo-cli --commit-sha 1111111111111111111111111111111111111111 --observed-at 2026-08-07 --unverified-demo --markdown-out out/demo-report.md --json-out out/demo-report.json
python -m unittest discover -s tests -v
```

The included demo is synthetic and intentionally incomplete. The report is maintenance evidence—not a security audit, certification, compliance opinion, or guarantee.

Read [the charter](CHARTER.md), [validation plan](VALIDATION_PLAN.md), [claims boundary](LEGAL_AND_CLAIMS.md), and [revenue ledger](REVENUE_LEDGER.md).
