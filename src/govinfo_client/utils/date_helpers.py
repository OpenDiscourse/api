"""Date and time helper functions."""

from datetime import datetime, timedelta
from typing import Tuple


def format_iso_date(dt: datetime) -> str:
    """
    Format datetime as ISO 8601 string for API requests.

    Args:
        dt: datetime object

    Returns:
        ISO 8601 formatted string (e.g., "2024-01-01T00:00:00Z")
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso_date(date_str: str) -> datetime:
    """
    Parse ISO 8601 date string.

    Args:
        date_str: ISO 8601 formatted string

    Returns:
        datetime object
    """
    # Try different formats
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date string: {date_str}")


def get_date_range(days: int = 30) -> Tuple[str, str]:
    """
    Get date range for the last N days.

    Args:
        days: Number of days to look back

    Returns:
        Tuple of (start_date, end_date) as ISO 8601 strings
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    return (
        format_iso_date(start_date),
        format_iso_date(end_date),
    )


def get_last_month_range() -> Tuple[str, str]:
    """
    Get date range for the previous month.

    Returns:
        Tuple of (start_date, end_date) as ISO 8601 strings
    """
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)

    return (
        format_iso_date(first_day_last_month),
        format_iso_date(last_day_last_month),
    )


def get_year_to_date_range() -> Tuple[str, str]:
    """
    Get date range from start of year to today.

    Returns:
        Tuple of (start_date, end_date) as ISO 8601 strings
    """
    today = datetime.now()
    start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0)

    return (
        format_iso_date(start_of_year),
        format_iso_date(today),
    )
