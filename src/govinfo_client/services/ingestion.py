"""Data ingestion service for populating local database from API."""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
import hashlib

from govinfo_client.client import GovInfoClient
from govinfo_client.db import models


class DataIngestion:
    """Service for ingesting data from GovInfo API into local database."""

    def __init__(self, client: GovInfoClient, session: Session):
        """
        Initialize data ingestion service.

        Args:
            client: GovInfo API client
            session: Database session
        """
        self.client = client
        self.session = session

    def ingest_collections(self) -> int:
        """
        Ingest all collections into database.

        Returns:
            Number of collections ingested/updated
        """
        collections_data = self.client.list_collections()
        count = 0

        for coll in collections_data.collections:
            # Check if collection exists
            stmt = select(models.Collection).where(
                models.Collection.collection_code == coll.collection_code
            )
            db_collection = self.session.scalar(stmt)

            if db_collection:
                # Update existing
                db_collection.collection_name = coll.collection_name
                db_collection.package_count = coll.package_count
                db_collection.granule_count = coll.granule_count
                db_collection.updated_at = datetime.utcnow()
            else:
                # Create new
                db_collection = models.Collection(
                    collection_code=coll.collection_code,
                    collection_name=coll.collection_name,
                    package_count=coll.package_count,
                    granule_count=coll.granule_count,
                )
                self.session.add(db_collection)

            count += 1

        self.session.commit()
        return count

    def ingest_collection_packages(
        self,
        collection_code: str,
        start_date: str,
        end_date: Optional[str] = None,
        max_pages: Optional[int] = None,
        fetch_summaries: bool = False,
    ) -> int:
        """
        Ingest packages from a collection.

        Args:
            collection_code: Collection code
            start_date: Start date (ISO 8601)
            end_date: Optional end date (ISO 8601)
            max_pages: Maximum pages to fetch
            fetch_summaries: Whether to fetch full package summaries

        Returns:
            Number of packages ingested/updated
        """
        # Get collection from database
        stmt = select(models.Collection).where(
            models.Collection.collection_code == collection_code
        )
        db_collection = self.session.scalar(stmt)

        if not db_collection:
            raise ValueError(f"Collection {collection_code} not found in database")

        count = 0
        page_num = 0

        for page in self.client.iter_collection_packages(
            collection_code, start_date, end_date
        ):
            for pkg in page.packages:
                # Fetch full summary if requested
                if fetch_summaries:
                    try:
                        pkg_summary = self.client.get_package_summary(pkg.package_id)
                        self._save_package_summary(pkg_summary, db_collection.id)
                    except Exception as e:
                        print(f"Error fetching summary for {pkg.package_id}: {e}")
                        self._save_package_basic(pkg, db_collection.id, collection_code)
                else:
                    self._save_package_basic(pkg, db_collection.id, collection_code)

                count += 1

            page_num += 1
            if max_pages and page_num >= max_pages:
                break

            self.session.commit()

        self.session.commit()
        return count

    def _save_package_basic(
        self, pkg_info, collection_id: int, collection_code: str
    ) -> models.Package:
        """Save basic package information."""
        stmt = select(models.Package).where(models.Package.package_id == pkg_info.package_id)
        db_package = self.session.scalar(stmt)

        if db_package:
            db_package.last_modified = pkg_info.last_modified
            db_package.updated_at = datetime.utcnow()
        else:
            db_package = models.Package(
                package_id=pkg_info.package_id,
                collection_id=collection_id,
                collection_code=collection_code,
                last_modified=pkg_info.last_modified,
            )
            self.session.add(db_package)

        return db_package

    def _save_package_summary(
        self, pkg_summary, collection_id: int
    ) -> models.Package:
        """Save full package summary."""
        stmt = select(models.Package).where(models.Package.package_id == pkg_summary.package_id)
        db_package = self.session.scalar(stmt)

        package_data = {
            "package_id": pkg_summary.package_id,
            "title": pkg_summary.title,
            "collection_id": collection_id,
            "collection_code": pkg_summary.collection_code,
            "collection_name": pkg_summary.collection_name,
            "category": pkg_summary.category,
            "date_issued": pkg_summary.date_issued,
            "last_modified": pkg_summary.last_modified,
            "branch": pkg_summary.branch,
            "congress": pkg_summary.congress,
            "session": pkg_summary.session,
            "download_links": (
                pkg_summary.download.model_dump() if pkg_summary.download else None
            ),
            "related_links": pkg_summary.related.model_dump() if pkg_summary.related else None,
            "references": (
                [r.model_dump() for r in pkg_summary.references]
                if pkg_summary.references
                else None
            ),
            "metadata": {
                "bill_type": pkg_summary.bill_type,
                "bill_number": pkg_summary.bill_number,
                "bill_version": pkg_summary.bill_version,
                "publisher": pkg_summary.publisher,
                "pages": pkg_summary.pages,
            },
        }

        if db_package:
            for key, value in package_data.items():
                if key != "package_id":  # Don't update primary key
                    setattr(db_package, key, value)
            db_package.updated_at = datetime.utcnow()
        else:
            db_package = models.Package(**package_data)
            self.session.add(db_package)

        return db_package

    def ingest_package_granules(self, package_id: str, max_pages: Optional[int] = None) -> int:
        """
        Ingest granules for a package.

        Args:
            package_id: Package identifier
            max_pages: Maximum pages to fetch

        Returns:
            Number of granules ingested
        """
        # Get package from database
        stmt = select(models.Package).where(models.Package.package_id == package_id)
        db_package = self.session.scalar(stmt)

        if not db_package:
            raise ValueError(f"Package {package_id} not found in database")

        count = 0
        offset_mark = "*"
        page_num = 0

        while True:
            granules_data = self.client.get_package_granules(package_id, offset_mark)

            for granule_info in granules_data.granules:
                # Optionally fetch full granule summary
                try:
                    granule_summary = self.client.get_granule_summary(
                        package_id, granule_info.granule_id
                    )
                    self._save_granule_summary(granule_summary, db_package.id, package_id)
                except Exception as e:
                    print(f"Error fetching granule {granule_info.granule_id}: {e}")
                    self._save_granule_basic(granule_info, db_package.id, package_id)

                count += 1

            page_num += 1
            if max_pages and page_num >= max_pages:
                break

            if not granules_data.next_page:
                break

            # Extract offset mark
            if "offsetMark=" in granules_data.next_page:
                offset_mark = granules_data.next_page.split("offsetMark=")[1].split("&")[0]
            else:
                break

            self.session.commit()

        self.session.commit()
        return count

    def _save_granule_basic(self, granule_info, package_id: int, package_identifier: str):
        """Save basic granule information."""
        stmt = select(models.Granule).where(models.Granule.granule_id == granule_info.granule_id)
        db_granule = self.session.scalar(stmt)

        if db_granule:
            db_granule.title = granule_info.title
            db_granule.updated_at = datetime.utcnow()
        else:
            db_granule = models.Granule(
                granule_id=granule_info.granule_id,
                title=granule_info.title,
                package_id=package_id,
                package_identifier=package_identifier,
                granule_class=granule_info.granule_class,
            )
            self.session.add(db_granule)

        return db_granule

    def _save_granule_summary(
        self, granule_summary, package_id: int, package_identifier: str
    ):
        """Save full granule summary."""
        stmt = select(models.Granule).where(
            models.Granule.granule_id == granule_summary.granule_id
        )
        db_granule = self.session.scalar(stmt)

        granule_data = {
            "granule_id": granule_summary.granule_id,
            "title": granule_summary.title,
            "package_id": package_id,
            "package_identifier": package_identifier,
            "granule_class": granule_summary.granule_class,
            "collection_code": granule_summary.collection_code,
            "date_issued": granule_summary.date_issued,
            "last_modified": granule_summary.last_modified,
            "download_links": (
                granule_summary.download.model_dump() if granule_summary.download else None
            ),
            "metadata": {
                "branch": granule_summary.branch,
                "pages": granule_summary.pages,
                "congress": granule_summary.congress,
                "session": granule_summary.session,
            },
        }

        if db_granule:
            for key, value in granule_data.items():
                if key != "granule_id":
                    setattr(db_granule, key, value)
            db_granule.updated_at = datetime.utcnow()
        else:
            db_granule = models.Granule(**granule_data)
            self.session.add(db_granule)

        return db_granule

    def cache_search_results(self, query: str, results: dict, ttl_hours: int = 24) -> None:
        """
        Cache search results.

        Args:
            query: Search query string
            results: Search results dictionary
            ttl_hours: Time to live in hours
        """
        query_hash = hashlib.sha256(query.encode()).hexdigest()

        stmt = select(models.SearchCache).where(models.SearchCache.query_hash == query_hash)
        cache_entry = self.session.scalar(stmt)

        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        if cache_entry:
            cache_entry.results = results
            cache_entry.result_count = results.get("count", 0)
            cache_entry.created_at = datetime.utcnow()
            cache_entry.expires_at = expires_at
        else:
            cache_entry = models.SearchCache(
                query_hash=query_hash,
                query=query,
                results=results,
                result_count=results.get("count", 0),
                expires_at=expires_at,
            )
            self.session.add(cache_entry)

        self.session.commit()
