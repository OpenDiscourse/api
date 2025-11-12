"""Models for Granule endpoints."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GranuleDownload(BaseModel):
    """Download links for granule content."""

    txt_link: Optional[str] = Field(None, alias="txtLink")
    xml_link: Optional[str] = Field(None, alias="xmlLink")
    pdf_link: Optional[str] = Field(None, alias="pdfLink")
    mods_link: Optional[str] = Field(None, alias="modsLink")
    premis_link: Optional[str] = Field(None, alias="premisLink")
    zip_link: Optional[str] = Field(None, alias="zipLink")

    class Config:
        populate_by_name = True


class GranuleSummary(BaseModel):
    """Complete granule summary from /packages/{id}/granules/{granuleId}/summary."""

    title: str = Field(..., description="Granule title")
    granule_id: str = Field(..., alias="granuleId", description="Unique granule identifier")
    granule_class: Optional[str] = Field(None, alias="granuleClass", description="Granule class")
    package_id: str = Field(..., alias="packageId", description="Parent package identifier")
    collection_code: Optional[str] = Field(None, alias="collectionCode")
    collection_name: Optional[str] = Field(None, alias="collectionName")
    category: Optional[str] = Field(None, description="Document category")
    date_issued: Optional[str] = Field(None, alias="dateIssued")
    details_link: Optional[str] = Field(None, alias="detailsLink")
    download: Optional[GranuleDownload] = Field(None, description="Download links")
    last_modified: Optional[datetime] = Field(None, alias="lastModified")

    # Collection-specific fields
    branch: Optional[str] = Field(None, description="Government branch")
    pages: Optional[str] = Field(None, description="Page count or range")
    congress: Optional[str] = Field(None)
    session: Optional[str] = Field(None)
    member_name: Optional[str] = Field(None, alias="memberName")
    authority_id: Optional[str] = Field(None, alias="authorityId")
    birth_year: Optional[str] = Field(None, alias="birthYear")
    state: Optional[str] = Field(None)
    district: Optional[str] = Field(None)
    party: Optional[str] = Field(None)
    biographical_note: Optional[str] = Field(None, alias="biographicalNote")
    official_url: Optional[str] = Field(None, alias="officialUrl")
    social_media: Optional[Dict[str, str]] = Field(None, alias="socialMedia")

    class Config:
        populate_by_name = True
        extra = "allow"


class GranuleInfo(BaseModel):
    """Brief granule information in listings."""

    granule_id: str = Field(..., alias="granuleId")
    title: str = Field(..., description="Granule title")
    granule_link: str = Field(..., alias="granuleLink", description="Link to granule summary")
    granule_class: Optional[str] = Field(None, alias="granuleClass")

    class Config:
        populate_by_name = True


class GranuleList(BaseModel):
    """Response from /packages/{id}/granules endpoint."""

    count: int = Field(..., description="Total number of granules")
    message: Optional[str] = Field(None)
    next_page: Optional[str] = Field(None, alias="nextPage")
    previous_page: Optional[str] = Field(None, alias="previousPage")
    offset_mark: Optional[str] = Field(None, alias="offsetMark")
    granules: List[GranuleInfo] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class Granule(BaseModel):
    """Simplified granule model."""

    granule_id: str = Field(..., alias="granuleId")
    title: Optional[str] = Field(None)
    package_id: Optional[str] = Field(None, alias="packageId")

    class Config:
        populate_by_name = True
