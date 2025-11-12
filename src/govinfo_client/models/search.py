"""Models for Search endpoint."""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class SortField(BaseModel):
    """Sort field specification for search queries."""

    field: Literal["score", "publishdate", "lastModified", "title"] = Field(
        ..., description="Field to sort by"
    )
    sort_order: Literal["ASC", "DESC"] = Field(
        ..., alias="sortOrder", description="Sort order"
    )

    class Config:
        populate_by_name = True


class SearchQuery(BaseModel):
    """Search query parameters for POST /search."""

    query: str = Field(..., description="Search query string")
    page_size: str = Field("100", alias="pageSize", description="Number of results per page")
    offset_mark: str = Field("*", alias="offsetMark", description="Offset mark for pagination")
    sorts: List[SortField] = Field(
        default_factory=lambda: [SortField(field="score", sort_order="DESC")],
        description="Sort fields",
    )

    class Config:
        populate_by_name = True


class SearchResultItem(BaseModel):
    """Individual search result item."""

    package_id: Optional[str] = Field(None, alias="packageId")
    granule_id: Optional[str] = Field(None, alias="granuleId")
    title: Optional[str] = Field(None)
    congress: Optional[str] = Field(None)
    session: Optional[str] = Field(None)
    collection_code: Optional[str] = Field(None, alias="collectionCode")
    collection_name: Optional[str] = Field(None, alias="collectionName")
    category: Optional[str] = Field(None)
    date_issued: Optional[str] = Field(None, alias="dateIssued")
    last_modified: Optional[str] = Field(None, alias="lastModified")
    government_author1: Optional[str] = Field(None, alias="governmentAuthor1")
    government_author2: Optional[str] = Field(None, alias="governmentAuthor2")
    publisher: Optional[str] = Field(None)
    download: Optional[Dict[str, str]] = Field(None, description="Download links")
    details_link: Optional[str] = Field(None, alias="detailsLink")

    class Config:
        populate_by_name = True
        extra = "allow"


class SearchResults(BaseModel):
    """Response from POST /search endpoint."""

    count: int = Field(..., description="Total number of results")
    offset_mark: Optional[str] = Field(None, alias="offsetMark")
    next_page: Optional[str] = Field(None, alias="nextPage")
    previous_page: Optional[str] = Field(None, alias="previousPage")
    results: List[SearchResultItem] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class SearchResult(BaseModel):
    """Alias for SearchResultItem."""

    package_id: Optional[str] = Field(None, alias="packageId")
    title: Optional[str] = Field(None)
    collection_code: Optional[str] = Field(None, alias="collectionCode")

    class Config:
        populate_by_name = True
