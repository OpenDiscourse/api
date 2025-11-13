"""Models for Collection endpoints."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Collection(BaseModel):
    """Represents a GovInfo collection."""

    collection_code: str = Field(..., alias="collectionCode", description="Collection identifier")
    collection_name: str = Field(..., alias="collectionName", description="Human-readable name")
    package_count: int = Field(..., alias="packageCount", description="Number of packages")
    granule_count: Optional[int] = Field(
        None, alias="granuleCount", description="Number of granules"
    )

    class Config:
        populate_by_name = True


class CollectionList(BaseModel):
    """Response from /collections endpoint."""

    collections: List[Collection] = Field(..., description="List of available collections")


class PackageInfo(BaseModel):
    """Brief package information in collection listings."""

    package_id: str = Field(..., alias="packageId", description="Unique package identifier")
    last_modified: datetime = Field(..., alias="lastModified", description="Last modification time")
    package_link: str = Field(..., alias="packageLink", description="Link to package summary")

    class Config:
        populate_by_name = True


class CollectionPackages(BaseModel):
    """Response from /collections/{code}/{date} endpoint."""

    count: int = Field(..., description="Total number of packages")
    message: Optional[str] = Field(None, description="API message")
    next_page: Optional[str] = Field(None, alias="nextPage", description="URL to next page")
    previous_page: Optional[str] = Field(
        None, alias="previousPage", description="URL to previous page"
    )
    packages: List[PackageInfo] = Field(default_factory=list, description="List of packages")

    class Config:
        populate_by_name = True
