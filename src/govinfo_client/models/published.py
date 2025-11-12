"""Models for Published endpoint."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PublishedPackageInfo(BaseModel):
    """Package information from published endpoint."""

    package_id: str = Field(..., alias="packageId")
    last_modified: datetime = Field(..., alias="lastModified")
    package_link: str = Field(..., alias="packageLink")
    doc_class: Optional[str] = Field(None, alias="docClass")
    date_issued: Optional[str] = Field(None, alias="dateIssued")
    title: Optional[str] = Field(None)

    class Config:
        populate_by_name = True


class PublishedPackages(BaseModel):
    """Response from /published endpoint."""

    count: int = Field(..., description="Total number of packages")
    message: Optional[str] = Field(None)
    next_page: Optional[str] = Field(None, alias="nextPage")
    previous_page: Optional[str] = Field(None, alias="previousPage")
    offset_mark: Optional[str] = Field(None, alias="offsetMark")
    packages: List[PublishedPackageInfo] = Field(default_factory=list)

    class Config:
        populate_by_name = True
