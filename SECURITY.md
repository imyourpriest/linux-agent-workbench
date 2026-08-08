# Security policy

Do not report a suspected vulnerability in a public issue, pull request, candidate manifest, sample report, or project log.

## Supported versions

This is pre-release research software. Only the current `main` branch is considered for security
corrections; no released version is currently supported.

## Report privately

Use the repository's **Security** tab, open **Advisories**, and select **Report a
vulnerability**. GitHub private vulnerability reporting must remain enabled before any project
source is public. If that button is absent, do not disclose details in an issue, pull request,
discussion, chat, or project log; stop the affected work until the private route is restored.

Include the affected path/version, impact, minimal reproduction, and any suggested mitigation.
Do not include unrelated personal data, credentials, tokens, wallet material, or third-party
private source.

This project does not authorize scanning or probing deployed third-party services. Patch Cabinet
uses read-only public metadata and evidence. The current Release Readiness demo accepts only
synthetic or trusted project-owned input; customer and third-party checkouts remain prohibited
until the D-014 acquisition and isolated-analysis gate passes.
