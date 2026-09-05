"""External infrastructure adapters for LAT-CES application workflows."""

from .thermal_adapters import DeepLinkAdapter, EmailWorkflowAdapter

__all__ = ["DeepLinkAdapter", "EmailWorkflowAdapter"]
