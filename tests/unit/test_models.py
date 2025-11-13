"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime
from govinfo_client.models import (
    Collection,
    CollectionList,
    CollectionPackages,
    PackageSummary,
    GranuleSummary,
    SearchQuery,
    SearchResults,
)


class TestCollectionModels:
    """Test collection models."""

    def test_collection_creation(self):
        """Test creating a Collection instance."""
        coll = Collection(
            collectionCode="BILLS",
            collectionName="Congressional Bills",
            packageCount=197925,
            granuleCount=None,
        )

        assert coll.collection_code == "BILLS"
        assert coll.collection_name == "Congressional Bills"
        assert coll.package_count == 197925
        assert coll.granule_count is None

    def test_collection_list_parsing(self):
        """Test parsing CollectionList from API response."""
        data = {
            "collections": [
                {
                    "collectionCode": "BILLS",
                    "collectionName": "Congressional Bills",
                    "packageCount": 197925,
                    "granuleCount": None,
                },
                {
                    "collectionCode": "FR",
                    "collectionName": "Federal Register",
                    "packageCount": 20702,
                    "granuleCount": 778537,
                },
            ]
        }

        coll_list = CollectionList(**data)
        assert len(coll_list.collections) == 2
        assert coll_list.collections[0].collection_code == "BILLS"
        assert coll_list.collections[1].granule_count == 778537


class TestPackageModels:
    """Test package models."""

    def test_package_summary_creation(self):
        """Test creating a PackageSummary instance."""
        summary = PackageSummary(
            title="Test Bill",
            collectionCode="BILLS",
            collectionName="Congressional Bills",
            packageId="BILLS-115hr1625enr",
            detailsLink="https://www.govinfo.gov/app/details/BILLS-115hr1625enr",
        )

        assert summary.title == "Test Bill"
        assert summary.package_id == "BILLS-115hr1625enr"
        assert summary.collection_code == "BILLS"

    def test_package_summary_with_download_links(self):
        """Test PackageSummary with download links."""
        data = {
            "title": "Test Package",
            "collectionCode": "BILLS",
            "collectionName": "Congressional Bills",
            "packageId": "TEST-123",
            "detailsLink": "https://example.com",
            "download": {
                "pdfLink": "https://example.com/pdf",
                "xmlLink": "https://example.com/xml",
            },
        }

        summary = PackageSummary(**data)
        assert summary.download is not None
        assert summary.download.pdf_link == "https://example.com/pdf"
        assert summary.download.xml_link == "https://example.com/xml"


class TestSearchModels:
    """Test search models."""

    def test_search_query_creation(self):
        """Test creating a SearchQuery instance."""
        query = SearchQuery(
            query="test query",
            pageSize="100",
            offsetMark="*",
            sorts=[{"field": "score", "sortOrder": "DESC"}],
        )

        assert query.query == "test query"
        assert query.page_size == "100"
        assert query.offset_mark == "*"
        assert len(query.sorts) == 1

    def test_search_query_serialization(self):
        """Test SearchQuery serialization."""
        query = SearchQuery(
            query="test",
            pageSize="50",
            offsetMark="*",
        )

        data = query.model_dump(by_alias=True)
        assert data["query"] == "test"
        assert data["pageSize"] == "50"
        assert data["offsetMark"] == "*"


class TestGranuleModels:
    """Test granule models."""

    def test_granule_summary_creation(self):
        """Test creating a GranuleSummary instance."""
        summary = GranuleSummary(
            title="Test Granule",
            granuleId="TEST-GRANULE-123",
            packageId="TEST-PACKAGE-456",
        )

        assert summary.title == "Test Granule"
        assert summary.granule_id == "TEST-GRANULE-123"
        assert summary.package_id == "TEST-PACKAGE-456"

    def test_granule_with_metadata(self):
        """Test GranuleSummary with metadata."""
        data = {
            "title": "Congressional Record Section",
            "granuleId": "CREC-2018-01-03-pt1-PgH1",
            "packageId": "CREC-2018-01-03",
            "congress": "115",
            "session": "2",
            "pages": "H1-H10",
        }

        summary = GranuleSummary(**data)
        assert summary.congress == "115"
        assert summary.session == "2"
        assert summary.pages == "H1-H10"
