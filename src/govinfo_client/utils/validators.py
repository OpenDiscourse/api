"""Validation utilities."""

import re
from typing import List


# Known collection codes
VALID_COLLECTIONS = [
    "BILLS",
    "BILLSTATUS",
    "CHRG",
    "FR",
    "CREC",
    "CRECB",
    "CFR",
    "PLAW",
    "USCOURTS",
    "GAOREPORTS",
    "CRPT",
    "CPRT",
    "CDOC",
    "CCAL",
    "GOVPUB",
    "CPD",
    "CZIC",
    "GPO",
    "PAI",
    "USCODE",
    "ERIC",
    "BUDGET",
    "ECONI",
    "LSA",
    "PPP",
    "STATUTE",
    "HOB",
    "ERP",
    "GOVMAN",
    "CDIR",
    "HMAN",
    "SMAN",
    "HJOURNAL",
]


def validate_collection_code(code: str) -> bool:
    """
    Validate a collection code.

    Args:
        code: Collection code to validate

    Returns:
        True if valid, False otherwise
    """
    return code.upper() in VALID_COLLECTIONS


def validate_package_id(package_id: str) -> bool:
    """
    Validate a package ID format.

    Package IDs typically follow the pattern: COLLECTION-details
    For example: BILLS-115hr1625enr, FR-2024-01-03, CREC-2024-01-03

    Args:
        package_id: Package ID to validate

    Returns:
        True if format appears valid, False otherwise
    """
    # Basic pattern check
    pattern = r"^[A-Z]+-[A-Za-z0-9\-]+$"
    if not re.match(pattern, package_id):
        return False

    # Extract collection code
    parts = package_id.split("-", 1)
    if len(parts) != 2:
        return False

    collection_code = parts[0]
    return validate_collection_code(collection_code)


def get_collection_codes() -> List[str]:
    """
    Get list of all valid collection codes.

    Returns:
        List of collection codes
    """
    return VALID_COLLECTIONS.copy()


def normalize_collection_code(code: str) -> str:
    """
    Normalize a collection code to uppercase.

    Args:
        code: Collection code

    Returns:
        Normalized collection code

    Raises:
        ValueError: If collection code is invalid
    """
    normalized = code.upper()
    if not validate_collection_code(normalized):
        raise ValueError(f"Invalid collection code: {code}")
    return normalized
