"""SQLAlchemy database models for storing GovInfo data."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Collection(Base):
    """Collection information."""

    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    collection_name: Mapped[str] = mapped_column(String(255))
    package_count: Mapped[int] = mapped_column(Integer)
    granule_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    packages: Mapped[list["Package"]] = relationship(
        "Package", back_populates="collection", cascade="all, delete-orphan"
    )


class Package(Base):
    """Package information."""

    __tablename__ = "packages"
    __table_args__ = (
        Index("ix_packages_collection_date", "collection_id", "date_issued"),
        Index("ix_packages_last_modified", "last_modified"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"))
    collection_code: Mapped[str] = mapped_column(String(50), index=True)
    collection_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_issued: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    congress: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    session: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Store complex data as JSON
    download_links: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    related_links: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    references: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )  # For additional fields

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    collection: Mapped["Collection"] = relationship("Collection", back_populates="packages")
    granules: Mapped[list["Granule"]] = relationship(
        "Granule", back_populates="package", cascade="all, delete-orphan"
    )


class Granule(Base):
    """Granule information."""

    __tablename__ = "granules"
    __table_args__ = (Index("ix_granules_package_date", "package_id", "date_issued"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    granule_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.id"))
    package_identifier: Mapped[str] = mapped_column(String(255), index=True)
    granule_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    collection_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_issued: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Store complex data as JSON
    download_links: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    package: Mapped["Package"] = relationship("Package", back_populates="granules")


class SearchCache(Base):
    """Cache for search results."""

    __tablename__ = "search_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    query_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    query: Mapped[str] = mapped_column(Text)
    results: Mapped[dict] = mapped_column(JSON)
    result_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Auto-expire after 24 hours
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
