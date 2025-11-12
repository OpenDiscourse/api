"""Integration tests for the API client (requires API key)."""

import pytest
import os
from govinfo_client import GovInfoClient
from govinfo_client.models import CollectionList, PackageSummary


# Skip these tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.getenv("GOVINFO_API_KEY"),
    reason="GOVINFO_API_KEY environment variable not set",
)


@pytest.fixture
def client():
    """Create a client with API key from environment."""
    api_key = os.getenv("GOVINFO_API_KEY", "DEMO_KEY")
    return GovInfoClient(api_key)


class TestCollectionsEndpoint:
    """Test collections endpoint."""

    def test_list_collections(self, client):
        """Test listing all collections."""
        collections = client.list_collections()

        assert isinstance(collections, CollectionList)
        assert len(collections.collections) > 0

        # Check that BILLS collection exists
        bills_coll = next(
            (c for c in collections.collections if c.collection_code == "BILLS"), None
        )
        assert bills_coll is not None
        assert bills_coll.collection_name == "Congressional Bills"
        assert bills_coll.package_count > 0

    def test_get_collection_packages(self, client):
        """Test getting packages from a collection."""
        packages = client.get_collection_packages(
            collection_code="BILLS",
            last_modified_start_date="2024-01-01T00:00:00Z",
            page_size=10,
        )

        assert packages.count > 0
        assert len(packages.packages) > 0

        # Check package structure
        pkg = packages.packages[0]
        assert pkg.package_id is not None
        assert pkg.last_modified is not None


class TestPackagesEndpoint:
    """Test packages endpoint."""

    def test_get_package_summary(self, client):
        """Test getting package summary."""
        # Use a known package ID
        package_id = "BILLS-115hr1625enr"
        summary = client.get_package_summary(package_id)

        assert isinstance(summary, PackageSummary)
        assert summary.package_id == package_id
        assert summary.title is not None
        assert summary.collection_code == "BILLS"
        assert summary.download is not None


class TestPublishedEndpoint:
    """Test published endpoint."""

    def test_get_published_packages(self, client):
        """Test getting published packages."""
        packages = client.get_published_packages(
            date_issued_start="2024-01-01",
            date_issued_end="2024-01-31",
            collection="BILLS",
            page_size=10,
        )

        assert packages.count >= 0
        # Note: May be 0 if no packages published in this range


class TestSearchEndpoint:
    """Test search endpoint."""

    def test_search_basic(self, client):
        """Test basic search."""
        results = client.search(query="collection:(BILLS)", page_size=10)

        assert results.count > 0
        assert len(results.results) > 0

    def test_search_with_filters(self, client):
        """Test search with complex query."""
        results = client.search(
            query='collection:(BILLS) AND congress:115',
            page_size=5,
        )

        assert results.count >= 0


class TestDataFrameConversion:
    """Test DataFrame conversion methods."""

    def test_collections_to_dataframe(self, client):
        """Test converting collections to DataFrame."""
        df = client.collections_to_dataframe()

        assert not df.empty
        assert "collection_code" in df.columns
        assert "collection_name" in df.columns
        assert "package_count" in df.columns

        # Check that BILLS is in the DataFrame
        bills_row = df[df["collection_code"] == "BILLS"]
        assert not bills_row.empty

    def test_search_to_dataframe(self, client):
        """Test converting search results to DataFrame."""
        df = client.search_to_dataframe(query="collection:(BILLS)", max_results=10)

        assert not df.empty
        assert len(df) <= 10
