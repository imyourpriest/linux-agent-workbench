"""Active Patch Cabinet engine identity and runtime provenance."""

from __future__ import annotations

from importlib.metadata import version


ENGINE_NAME = "patch-cabinet"
ENGINE_VERSION = "0.2.0"
OUTPUT_SCHEMA_VERSION = "1"
EXPECTED_DEPENDENCIES = {"packaging": "26.3"}


def validate_runtime_dependencies() -> dict[str, str]:
    """Return the active dependency identity, failing on an unversioned runtime."""

    observed = {name: version(name) for name in EXPECTED_DEPENDENCIES}
    if observed != EXPECTED_DEPENDENCIES:
        expected = ", ".join(
            f"{name}=={dependency_version}"
            for name, dependency_version in sorted(EXPECTED_DEPENDENCIES.items())
        )
        actual = ", ".join(
            f"{name}=={dependency_version}"
            for name, dependency_version in sorted(observed.items())
        )
        raise RuntimeError(
            f"Patch Cabinet engine {ENGINE_VERSION} requires {expected}; observed {actual}"
        )
    return observed
