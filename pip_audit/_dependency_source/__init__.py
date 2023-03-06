"""
Dependency source interfaces and implementations for `pip-audit`.
"""

from .interface import (
    DependencyFixError,
    DependencyResolver,
    DependencyResolverError,
    DependencySource,
    DependencySourceError,
    HashMismatchError,
    HashMissingError,
    InvalidRequirementSpecifier,
    RequirementHashes,
    UnsupportedHashAlgorithm,
)
from .pip import PipSource, PipSourceError
from .poetry import PoetrySource
from .pyproject import PyProjectSource
from .requirement import RequirementSource
from .resolvelib import PYPI_URL, ResolveLibResolver

__all__ = [
    "PYPI_URL",
    "DependencyFixError",
    "DependencyResolver",
    "DependencyResolverError",
    "DependencySource",
    "DependencySourceError",
    "HashMismatchError",
    "HashMissingError",
    "InvalidRequirementSpecifier",
    "PipSource",
    "PipSourceError",
    "PoetrySource",
    "PyProjectSource",
    "RequirementHashes",
    "RequirementSource",
    "ResolveLibResolver",
    "UnsupportedHashAlgorithm",
]
