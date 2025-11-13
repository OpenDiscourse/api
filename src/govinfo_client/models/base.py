"""Base models and common types."""

from typing import Optional
from pydantic import BaseModel, Field


class PageInfo(BaseModel):
    """Pagination information for API responses."""

    count: Optional[int] = Field(None, description="Total count of items")
    offset_mark: Optional[str] = Field(None, alias="offsetMark", description="Current offset mark")
    next_page: Optional[str] = Field(None, alias="nextPage", description="URL to next page")
    previous_page: Optional[str] = Field(
        None, alias="previousPage", description="URL to previous page"
    )
    message: Optional[str] = Field(None, description="Message from API")

    class Config:
        populate_by_name = True
