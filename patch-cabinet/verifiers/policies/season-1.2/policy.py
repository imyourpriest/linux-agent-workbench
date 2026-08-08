"""Deterministic Patch Cabinet eligibility and ranking policy."""

from __future__ import annotations

import ipaddress
import math
import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Iterable
from urllib.parse import urlsplit

from packaging.licenses import InvalidLicenseExpression, canonicalize_license_expression


DEFAULT_EXCLUDED_REPOSITORIES = {"historical/frozen-demo".casefold()}
SEASON_POLICY_VERSION = "season-1.2"
MAX_OBSERVATION_AGE_DAYS = 7
VALID_LINUX_RELEVANCE = {"direct", "ecosystem", "none"}
VALID_SIGNALS = {"explicit_issue", "help_wanted", "none"}
VALID_AI_POLICIES = {"allows", "unknown", "disallows"}
ALLOWED_TASK_TYPES = {
    "bugfix",
    "dependency_maintenance",
    "documentation",
    "portability",
    "release_engineering",
    "tests",
}
FULL_COMMIT = re.compile(r"^[0-9a-fA-F]{40}$")
LICENSE_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*")
REPOSITORY_NAME = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}/[A-Za-z0-9][A-Za-z0-9._-]{0,99}$"
)
SEASON_1_LICENSE_IDS = {
    "0BSD",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
    "Apache-2.0",
    "Artistic-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "BSL-1.0",
    "CC0-1.0",
    "EPL-2.0",
    "EUPL-1.2",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "ISC",
    "LGPL-2.1-only",
    "LGPL-2.1-or-later",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
    "MIT",
    "MPL-2.0",
    "Python-2.0",
    "Unlicense",
    "Zlib",
}
SEASON_1_EXCEPTION_IDS = {
    "Classpath-exception-2.0",
    "GCC-exception-3.1",
    "LLVM-exception",
}
REQUIRED_FIELDS = {
    "repository",
    "url",
    "observed_at",
    "commit_sha",
    "public",
    "archived",
    "license_spdx",
    "linux_relevance",
    "maintainer_signal",
    "issue_url",
    "task_type",
    "last_activity_at",
    "estimated_hours",
    "has_reproduction",
    "has_tests",
    "has_contributing",
    "ai_policy",
    "requires_human_attestation",
    "sensitive_subsystem",
    "requires_secrets",
    "requires_production_access",
    "requires_network_probe",
    "open_pull_requests",
}


@dataclass(frozen=True)
class Evaluation:
    repository: str
    eligible: bool
    score: int
    band: str
    reasons: tuple[str, ...]
    cautions: tuple[str, ...]
    evidence: dict[str, Any]
    normalized_inputs: dict[str, Any]
    score_trace: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["reasons"] = list(self.reasons)
        result["cautions"] = list(self.cautions)
        result["score_trace"] = list(self.score_trace)
        return result


def _validate(candidate: dict[str, Any], *, as_of: date) -> tuple[date, date]:
    missing = sorted(REQUIRED_FIELDS - candidate.keys())
    if missing:
        raise ValueError(f"candidate is missing required fields: {', '.join(missing)}")
    unexpected = sorted(candidate.keys() - REQUIRED_FIELDS)
    if unexpected:
        raise ValueError(f"candidate contains unexpected fields: {', '.join(unexpected)}")

    repository = candidate["repository"]
    if not isinstance(repository, str) or not REPOSITORY_NAME.fullmatch(repository):
        raise ValueError("repository must be a non-empty 'owner/name' string")

    for field in (
        "url",
        "observed_at",
        "last_activity_at",
        "commit_sha",
        "license_spdx",
        "issue_url",
        "task_type",
    ):
        if not isinstance(candidate[field], str):
            raise ValueError(f"{field} must be a string")

    for field in ("url", "issue_url"):
        value = candidate[field]
        parsed = urlsplit(value)
        try:
            port = parsed.port
        except ValueError as error:
            raise ValueError(f"{field} must contain a valid HTTPS port") from error
        hostname = parsed.hostname or ""
        labels = hostname.split(".")
        valid_labels = all(
            re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
            for label in labels
        )
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            is_ip_address = False
        else:
            is_ip_address = True
        if (
            parsed.scheme != "https"
            or not hostname
            or parsed.username is not None
            or parsed.password is not None
            or port not in {None, 443}
            or parsed.path in {"", "/"}
            or len(hostname) > 253
            or len(labels) < 2
            or not valid_labels
            or is_ip_address
            or any(
                character.isspace()
                or unicodedata.category(character) in {"Cc", "Cf"}
                for character in value
            )
        ):
            raise ValueError(f"{field} must be a public-style absolute HTTPS URL")

    if (
        not FULL_COMMIT.fullmatch(candidate["commit_sha"])
        or candidate["commit_sha"] == "0" * 40
    ):
        raise ValueError("commit_sha must be a full 40-character hexadecimal commit")
    parsed_dates: dict[str, date] = {}
    for field in ("observed_at", "last_activity_at"):
        try:
            parsed_dates[field] = date.fromisoformat(candidate[field])
        except ValueError as error:
            raise ValueError(f"{field} must be a valid YYYY-MM-DD date") from error
        if parsed_dates[field].isoformat() != candidate[field]:
            raise ValueError(f"{field} must use YYYY-MM-DD")
    observed = parsed_dates["observed_at"]
    last_activity = parsed_dates["last_activity_at"]
    if observed > as_of:
        raise ValueError("observed_at cannot be later than the policy as-of date")
    if last_activity > observed:
        raise ValueError("last_activity_at cannot be later than observed_at")

    for field in (
        "public",
        "archived",
        "has_reproduction",
        "has_tests",
        "has_contributing",
        "requires_human_attestation",
        "sensitive_subsystem",
        "requires_secrets",
        "requires_production_access",
        "requires_network_probe",
    ):
        if not isinstance(candidate[field], bool):
            raise ValueError(f"{field} must be a boolean")

    for field in ("open_pull_requests",):
        value = candidate[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field} must be a non-negative integer")

    hours = candidate["estimated_hours"]
    if (
        isinstance(hours, bool)
        or not isinstance(hours, (int, float))
        or not math.isfinite(hours)
        or hours <= 0
    ):
        raise ValueError("estimated_hours must be a positive number")

    if candidate["linux_relevance"] not in VALID_LINUX_RELEVANCE:
        raise ValueError("linux_relevance must be direct, ecosystem, or none")
    if candidate["maintainer_signal"] not in VALID_SIGNALS:
        raise ValueError("maintainer_signal must be explicit_issue, help_wanted, or none")
    if candidate["ai_policy"] not in VALID_AI_POLICIES:
        raise ValueError("ai_policy must be allows, unknown, or disallows")
    if candidate["task_type"].strip().casefold() not in ALLOWED_TASK_TYPES:
        allowed = ", ".join(sorted(ALLOWED_TASK_TYPES))
        raise ValueError(f"task_type must be one of: {allowed}")
    raw_license = candidate["license_spdx"].strip()
    if raw_license.upper() not in {"", "NONE", "NOASSERTION", "UNLICENSED"}:
        try:
            canonicalize_license_expression(raw_license)
        except InvalidLicenseExpression as error:
            raise ValueError("license_spdx must be a valid SPDX license expression") from error
    return observed, last_activity


def evaluate_candidate(
    candidate: dict[str, Any],
    *,
    as_of: date,
    evaluation_mode: str,
    excluded_repositories: Iterable[str] = (),
) -> Evaluation:
    """Evaluate one manually verified candidate against Season 1 policy."""

    if not isinstance(as_of, date):
        raise ValueError("as_of must be a date")
    if evaluation_mode not in {"live", "historical"}:
        raise ValueError("evaluation_mode must be live or historical")
    today = date.today()
    if as_of > today:
        raise ValueError("as_of cannot be in the future")
    if evaluation_mode == "live" and as_of != today:
        raise ValueError("live evaluation requires as_of to equal the current date")
    policy_as_of = as_of
    observed, last_activity = _validate(candidate, as_of=policy_as_of)
    observation_age = (policy_as_of - observed).days
    if observation_age > MAX_OBSERVATION_AGE_DAYS:
        raise ValueError(
            f"observed_at is more than {MAX_OBSERVATION_AGE_DAYS} days before as_of"
        )
    failures: list[str] = []
    cautions: list[str] = []

    repository = candidate["repository"]
    raw_license = candidate["license_spdx"].strip()
    license_spdx = (
        raw_license.upper()
        if raw_license.upper() in {"", "NONE", "NOASSERTION", "UNLICENSED"}
        else canonicalize_license_expression(raw_license)
    )
    task_type = candidate["task_type"].strip().casefold()
    normalized_inputs = dict(candidate)
    normalized_inputs["license_spdx"] = license_spdx
    normalized_inputs["task_type"] = task_type
    normalized_inputs["policy_as_of"] = policy_as_of.isoformat()
    normalized_inputs["evaluation_mode"] = evaluation_mode
    normalized_inputs["last_activity_days"] = (observed - last_activity).days

    exclusions = DEFAULT_EXCLUDED_REPOSITORIES | {
        item.casefold() for item in excluded_repositories
    }
    if repository.casefold() in exclusions:
        return Evaluation(
            repository="[locally excluded]",
            eligible=False,
            score=0,
            band="ineligible",
            reasons=("repository is a sponsor-designated frozen historical artifact",),
            cautions=(),
            evidence={
                "url": "[redacted]",
                "observed_at": "[redacted]",
                "commit_sha": "[redacted]",
                "issue_url": "[redacted]",
                "license_spdx": "[redacted]",
                "task_type": "[redacted]",
            },
            normalized_inputs={"repository": "[locally excluded]", "redacted": True},
            score_trace=(),
        )
    if not candidate["public"]:
        failures.append("repository is not public")
    if candidate["archived"]:
        failures.append("repository is archived")
    if license_spdx in {"", "NONE", "NOASSERTION", "UNLICENSED"}:
        failures.append("repository lacks an explicit SPDX license")
    else:
        identifiers = {
            token
            for token in LICENSE_TOKEN.findall(license_spdx)
            if token.upper() not in {"AND", "OR", "WITH"}
        }
        approved = SEASON_1_LICENSE_IDS | SEASON_1_EXCEPTION_IDS
        if not identifiers or not identifiers <= approved:
            failures.append(
                "license expression is outside the reviewed Season 1 open-source allowlist"
            )
    if candidate["linux_relevance"] == "none":
        failures.append("task has no material Linux relevance")
    activity_days = (observed - last_activity).days
    if activity_days > 365:
        failures.append("repository has no recorded activity within 365 days")
    if candidate["maintainer_signal"] == "none":
        failures.append("no explicit issue or help-wanted signal invites the work")
    if not candidate["issue_url"].strip():
        failures.append("no issue URL records the maintainer signal")
    if candidate["sensitive_subsystem"]:
        failures.append("candidate affects a Season 1 sensitive subsystem")
    if candidate["requires_secrets"]:
        failures.append("candidate requires secrets")
    if candidate["requires_production_access"]:
        failures.append("candidate requires production access")
    if candidate["requires_network_probe"]:
        failures.append("candidate requires a network probe")
    if candidate["estimated_hours"] > 6:
        failures.append("estimated scope exceeds the six-hour Season 1 limit")
    if candidate["ai_policy"] == "disallows":
        failures.append("upstream policy disallows AI-assisted contributions")

    evidence = {
        "url": candidate["url"],
        "observed_at": candidate["observed_at"],
        "commit_sha": candidate["commit_sha"],
        "issue_url": candidate["issue_url"],
        "license_spdx": candidate["license_spdx"],
        "task_type": candidate["task_type"],
    }

    if failures:
        return Evaluation(
            repository=repository,
            eligible=False,
            score=0,
            band="ineligible",
            reasons=tuple(failures),
            cautions=tuple(cautions),
            evidence=evidence,
            normalized_inputs=normalized_inputs,
            score_trace=(),
        )

    score = 0
    score_trace: list[dict[str, Any]] = []

    def apply_score(rule: str, delta: int) -> None:
        nonlocal score
        score += delta
        score_trace.append({"rule": rule, "delta": delta})

    signal = candidate["maintainer_signal"]
    apply_score("maintainer signal", 30 if signal == "explicit_issue" else 25)
    apply_score(
        "Linux relevance", 20 if candidate["linux_relevance"] == "direct" else 10
    )
    apply_score("reproduction recorded", 15 if candidate["has_reproduction"] else 0)
    apply_score("automated tests recorded", 10 if candidate["has_tests"] else 0)

    if activity_days <= 30:
        apply_score("activity recency", 10)
    elif activity_days <= 90:
        apply_score("activity recency", 8)
    elif activity_days <= 180:
        apply_score("activity recency", 5)
    else:
        apply_score("activity recency", 2)

    hours = candidate["estimated_hours"]
    if hours <= 2:
        apply_score("bounded scope", 10)
    elif hours <= 4:
        apply_score("bounded scope", 7)
    else:
        apply_score("bounded scope", 4)

    apply_score("contribution guide recorded", 5 if candidate["has_contributing"] else 0)

    if candidate["requires_human_attestation"]:
        apply_score("human attestation required", -10)
        cautions.append("CLA or DCO requires a human attestation checkpoint")
    if candidate["ai_policy"] == "unknown":
        apply_score("AI policy unknown", -5)
        cautions.append("upstream AI-contribution policy is unknown")
    if candidate["open_pull_requests"] >= 50:
        apply_score("large open-PR backlog", -5)
        cautions.append("large open-PR backlog may delay or burden review")
    if not candidate["has_tests"]:
        cautions.append("no existing automated test path was recorded")
    if not candidate["has_contributing"]:
        cautions.append("no contribution guide was recorded")
    if evaluation_mode == "historical":
        cautions.append("historical evaluation cannot be labeled ready")

    score = max(0, min(100, score))
    unresolved_gate = (
        candidate["ai_policy"] == "unknown" or candidate["requires_human_attestation"]
        or evaluation_mode == "historical"
    )
    band = "ready" if score >= 70 and not unresolved_gate else "investigate"
    reasons = (
        f"{signal.replace('_', ' ')} invites the work",
        f"Linux relevance is {candidate['linux_relevance']}",
        f"estimated scope is {hours:g} hours",
        f"last recorded activity was {activity_days} days before observation",
    )
    return Evaluation(
        repository=repository,
        eligible=True,
        score=score,
        band=band,
        reasons=reasons,
        cautions=tuple(cautions),
        evidence=evidence,
        normalized_inputs=normalized_inputs,
        score_trace=tuple(score_trace),
    )


def evaluate_candidates(
    candidates: Iterable[dict[str, Any]],
    *,
    as_of: date,
    evaluation_mode: str,
    excluded_repositories: Iterable[str] = (),
) -> list[Evaluation]:
    """Evaluate and deterministically rank candidates."""

    evaluations = [
        evaluate_candidate(
            candidate,
            excluded_repositories=excluded_repositories,
            as_of=as_of,
            evaluation_mode=evaluation_mode,
        )
        for candidate in candidates
    ]
    return sorted(
        evaluations,
        key=lambda item: (not item.eligible, -item.score, item.repository.casefold()),
    )
