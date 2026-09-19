"""Neutral boundary for external backend packages.

Third-party backends remain outside the canonical model and Engineering Core.
"""

from .package import ExternalBackendPackage, ExternalBackendPackageError

__all__ = ["ExternalBackendPackage", "ExternalBackendPackageError"]
