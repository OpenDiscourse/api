"""
GovInfo API Client Library

A strongly-typed Python client for the GovInfo API with database integration,
DataFrame support, and comprehensive coverage of all API endpoints.
"""

__version__ = "0.1.0"

from govinfo_client.client import GovInfoClient
from govinfo_client.models import (
    Collection,
    Package,
    Granule,
    SearchResult,
)

__all__ = [
    "GovInfoClient",
    "Collection",
    "Package",
    "Granule",
    "SearchResult",
]
