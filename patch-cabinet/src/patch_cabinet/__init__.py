"""Patch Cabinet candidate policy engine."""

from .engine import ENGINE_VERSION
from .policy import evaluate_candidates

__all__ = ["evaluate_candidates"]
__version__ = ENGINE_VERSION
