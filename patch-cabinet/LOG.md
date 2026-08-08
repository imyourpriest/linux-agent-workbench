# Patch Cabinet log

Append-only project record.

## 2026-08-07 — Launch

- Adopted a Linux/open-source public-service mission.
- Limited Season 1 to small, invited work in public Go and Python CLI repositories.
- Excluded sensitive subsystems, security findings, high-volume PR behavior, and the sponsor's frozen historical repositories.
- Started with $0 and no XLM.
- Implemented a deterministic, offline candidate-policy MVP with synthetic input and unit tests.
- No real repository was analyzed, cloned, executed, contacted, or modified at this point.

## 2026-08-08 — Adversarial policy hardening

- Auto-loaded the ignored project exclusion file and made absent local context fail closed unless a public/demo run is explicitly declared.
- Redacted excluded candidates from JSON and Markdown, rejected unexpected manifest fields, and removed absolute source paths from reports.
- Replaced caller-supplied activity age with `last_activity_at` plus a deterministic policy as-of date.
- Added a narrow reviewed Season 1 license allowlist; SPDX-valid source-available and custom references do not qualify.
- Added engine/policy/schema/dependency/source-hash provenance and pinned the license-parser dependency.
- Expanded the suite to cover private-name non-disclosure, unexpected fields, unsupported licenses, future/inconsistent dates, and local-context auto-loading.
- No real repository was analyzed, cloned, executed, contacted, or modified during this hardening.

## 2026-08-08 — Fail-closed input correction

- Removed exclusion-file auto-discovery after review showed that a target repository or an external manifest location could shadow or bypass the operator's private baseline. Project runs now pass the ignored operator-owned file explicitly; public/synthetic runs require a separate acknowledgement flag.
- Rejected duplicate JSON object keys and non-standard numeric constants so a repeated safety field cannot overwrite an earlier value.
- Made historical mode explicit and permanently non-ready, validated public-style HTTPS authorities and ports, and normalized generated-file newlines.
