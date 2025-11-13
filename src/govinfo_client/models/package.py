"""Models for Package endpoints."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PackageDownload(BaseModel):
    """Download links for package content."""

    txt_link: Optional[str] = Field(None, alias="txtLink", description="HTML/text format link")
    xml_link: Optional[str] = Field(None, alias="xmlLink", description="XML format link")
    pdf_link: Optional[str] = Field(None, alias="pdfLink", description="PDF format link")
    mods_link: Optional[str] = Field(None, alias="modsLink", description="MODS metadata link")
    premis_link: Optional[str] = Field(None, alias="premisLink", description="PREMIS metadata link")
    zip_link: Optional[str] = Field(None, alias="zipLink", description="ZIP archive link")

    class Config:
        populate_by_name = True


class PackageRelated(BaseModel):
    """Related documents and links."""

    bill_status_link: Optional[str] = Field(
        None, alias="billStatusLink", description="Bill status XML link"
    )

    class Config:
        populate_by_name = True
        extra = "allow"  # Allow additional related links


class OtherIdentifier(BaseModel):
    """Other identifiers for the package."""

    migrated_doc_id: Optional[str] = Field(None, alias="migrated-doc-id")
    parent_ils_system_id: Optional[str] = Field(None, alias="parent-ils-system-id")
    parent_ils_title: Optional[str] = Field(None, alias="parent-ils-title")
    child_ils_system_id: Optional[str] = Field(None, alias="child-ils-system-id")
    child_ils_title: Optional[str] = Field(None, alias="child-ils-title")
    stock_number: Optional[str] = Field(None, alias="stock-number")

    class Config:
        populate_by_name = True
        extra = "allow"


class ReferenceContent(BaseModel):
    """Reference content (USC, Statute, etc.)."""

    title: Optional[str] = Field(None, description="Title number")
    label: Optional[str] = Field(None, description="Label (e.g., 'U.S.C')")
    sections: Optional[List[str]] = Field(None, description="Section numbers")
    pages: Optional[List[str]] = Field(None, description="Page numbers")
    congress: Optional[str] = Field(None, description="Congress number")
    number: Optional[str] = Field(None, description="Law/document number")

    class Config:
        populate_by_name = True
        extra = "allow"


class PackageReference(BaseModel):
    """References to other collections (USC, Statutes, etc.)."""

    collection_code: str = Field(..., alias="collectionCode", description="Referenced collection")
    collection_name: str = Field(..., alias="collectionName", description="Collection name")
    contents: List[ReferenceContent] = Field(default_factory=list, description="Reference contents")

    class Config:
        populate_by_name = True


class PackageSummary(BaseModel):
    """Complete package summary from /packages/{id}/summary."""

    title: str = Field(..., description="Package title")
    collection_code: str = Field(..., alias="collectionCode", description="Collection identifier")
    collection_name: str = Field(..., alias="collectionName", description="Collection name")
    category: Optional[str] = Field(None, description="Document category")
    date_issued: Optional[str] = Field(None, alias="dateIssued", description="Date issued")
    details_link: str = Field(..., alias="detailsLink", description="Link to details page")
    package_id: str = Field(..., alias="packageId", description="Unique package identifier")
    download: Optional[PackageDownload] = Field(None, description="Download links")
    related: Optional[PackageRelated] = Field(None, description="Related documents")
    last_modified: Optional[datetime] = Field(
        None, alias="lastModified", description="Last modification time"
    )

    # Optional fields that may appear in various collections
    branch: Optional[str] = Field(None, description="Government branch")
    pages: Optional[str] = Field(None, description="Page count")
    government_author1: Optional[str] = Field(None, alias="governmentAuthor1")
    su_doc_class_number: Optional[str] = Field(None, alias="suDocClassNumber")
    bill_type: Optional[str] = Field(None, alias="billType")
    congress: Optional[str] = Field(None, description="Congress number")
    origin_chamber: Optional[str] = Field(None, alias="originChamber")
    current_chamber: Optional[str] = Field(None, alias="currentChamber")
    session: Optional[str] = Field(None, description="Session number")
    bill_number: Optional[str] = Field(None, alias="billNumber")
    bill_version: Optional[str] = Field(None, alias="billVersion")
    is_appropriation: Optional[str] = Field(None, alias="isAppropriation")
    is_private: Optional[str] = Field(None, alias="isPrivate")
    publisher: Optional[str] = Field(None, description="Publisher")
    other_identifier: Optional[OtherIdentifier] = Field(None, alias="otherIdentifier")
    references: Optional[List[PackageReference]] = Field(None, description="References")

    class Config:
        populate_by_name = True
        extra = "allow"


class Package(BaseModel):
    """Simplified package model for listings."""

    package_id: str = Field(..., alias="packageId")
    title: Optional[str] = Field(None)
    date_issued: Optional[str] = Field(None, alias="dateIssued")
    last_modified: Optional[datetime] = Field(None, alias="lastModified")

    class Config:
        populate_by_name = True
