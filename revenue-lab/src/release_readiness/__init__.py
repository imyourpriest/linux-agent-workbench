"""Linux Release Readiness Lab trusted-local evidence collector."""

from .version import __version__
from .audit import audit_repository

__all__ = ["audit_repository", "__version__"]
