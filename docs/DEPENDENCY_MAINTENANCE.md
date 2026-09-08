# Dependency maintenance

Rivetloom preserves reproducible compatibility evidence without treating an old dependency lock
as a supported execution target. The active declaration-schema compatibility jobs on `main` use
[`compatibility-v3`](../patch-cabinet/interop/maintainer-policy-declaration/compatibility-v3/):
the Python job installs its hash-locked requirements, and the Node job runs `npm ci` from its exact
lock with lifecycle scripts disabled. Both jobs verify the closed v3 harness before acquisition.
The Node runner also checks the expected five-package installed inventory before importing Ajv.

Compatibility v1 and v2 are preserved historical evidence. Project-owned standard-library checks
read their contracts, locks, runners, manifests, and receipts as data and bind their exact bytes;
the active hosted jobs do not install or execute those dependency trees. This is the project's
current policy and workflow design, not a claim that those files are harmless or technically
impossible to execute.
The v3 first-party generator also SHA-verifies and executes the v2 verifier source in memory to
validate the predecessor contracts before deriving v3; it does not install or run v2's third-party
dependency tree or adapters.

## Preparing an update

1. Start from a named `main` commit and record the advisory, release, and registry evidence used
   to select the version. Prefer the package publisher and the
   [GitHub Advisory Database](https://github.com/advisories).
2. Add a complete successor: preserve the predecessor bytes; add the new generator, closed
   harness tree, contract tests, both hosted-job routes, first-party freshness checks, and concise
   documentation. Bind the predecessor source, contracts, and locks rather than changing their
   expected hashes to make a check pass.
3. Keep acquisition in the existing hosted compatibility workflow. Preserve its read-only
   permissions, pinned actions, timeouts, pre-acquisition verification, exact Python hashes, npm
   lock, and disabled npm lifecycle scripts unless a separately reviewed change justifies altering
   one of those controls.
4. Run the project-owned generators in check mode, focused compatibility tests, the broader Patch
   suite, evidence checks, the public-tree heuristic, and diff/scope checks. Local and synthetic
   results establish only those bounded outcomes.
5. Review the complete successor and test it through a pull request at a named commit. Attribute
   hosted results only to the exact commit and checks observed; passing CI is not proof of future
   availability, production enforcement, isolation, or absence of exploitable behavior.

Do not auto-merge a lock-only dependency pull request, modify a frozen binding hash merely to make
CI green, or treat an alert state as permission to dismiss it. GitHub documents
[Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates)
separately from scheduled
[Dependabot version-update configuration](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file).
As observed on 2026-09-08 UTC (2026-09-07 America/Denver), vulnerability alerts and security pull
requests were enabled even though this repository had no scheduled npm version-update entry.

## Current preserved-path records

The following open alerts were observed on 2026-09-08 UTC. They describe vulnerable dependencies
still present in preserved v1/v2 bytes; moving active hosted execution to v3 does not fix those
historical artifacts or establish that they are unexploitable.

| Alert | Preserved path | Advisory |
|---:|---|---|
| 6 | compatibility-v2 | `GHSA-5jgf-p345-68v8` |
| 7 | compatibility-v2 | `GHSA-fph4-wmhf-6fwf` |
| 8 | compatibility-v1 | `GHSA-f65p-4m7j-42xc` |
| 9 | compatibility-v1 | `GHSA-jqff-g426-hqxp` |
| 10 | compatibility-v2 | `GHSA-f65p-4m7j-42xc` |
| 11 | compatibility-v2 | `GHSA-jqff-g426-hqxp` |

Two Dependabot pull requests were also open and untouched at that observation:

- PR 27, compatibility-v2, head `6f9ea2b2265ec6d46f40a7caad1dac2e2e688325`;
- PR 28, compatibility-v1, head `951e4bbc92618026eabf5804aba1b88b010913d8`.

Neither these records nor this guide authorizes merging, closing, editing, or dismissing anything.
Before merging any future change that installs, imports, or executes a preserved v1/v2 dependency
tree or adapter, obtain a fresh security review and reopen every affected previously dismissed
alert. D-044 and D-045 record that mandatory pre-merge control for v1; D-067 applies the same rule
to preserved v2.
