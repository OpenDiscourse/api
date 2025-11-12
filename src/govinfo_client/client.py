"""Main GovInfo API client with strongly-typed methods."""

import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd

from govinfo_client.models import (
    CollectionList,
    CollectionPackages,
    PackageSummary,
    GranuleList,
    GranuleSummary,
    SearchQuery,
    SearchResults,
    PublishedPackages,
)


class GovInfoClient:
    """
    Strongly-typed client for the GovInfo API.

    Provides methods for all API endpoints with proper type hints and validation.
    """

    BASE_URL = "https://api.govinfo.gov"

    def __init__(self, api_key: str, timeout: float = 30.0):
        """
        Initialize the GovInfo API client.

        Args:
            api_key: Your api.data.gov API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def __enter__(self) -> "GovInfoClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        if params is None:
            params = {}
        params["api_key"] = self.api_key

        response = self.client.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def _post(
        self, endpoint: str, json_data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request to the API."""
        if params is None:
            params = {}
        params["api_key"] = self.api_key

        response = self.client.post(f"{self.BASE_URL}{endpoint}", json=json_data, params=params)
        response.raise_for_status()
        return response.json()

    # Collections Service

    def list_collections(self) -> CollectionList:
        """
        Get a list of all available collections.

        Returns:
            CollectionList with all available collections
        """
        data = self._get("/collections")
        return CollectionList(**data)

    def get_collection_packages(
        self,
        collection_code: str,
        last_modified_start_date: str,
        last_modified_end_date: Optional[str] = None,
        offset_mark: str = "*",
        page_size: int = 100,
    ) -> CollectionPackages:
        """
        Get packages from a collection modified within a date range.

        Args:
            collection_code: Collection code (e.g., 'BILLS', 'FR', 'CREC')
            last_modified_start_date: Start date in ISO 8601 format
            last_modified_end_date: Optional end date in ISO 8601 format
            offset_mark: Pagination offset mark (start with '*')
            page_size: Number of results per page (max 1000)

        Returns:
            CollectionPackages with list of packages
        """
        endpoint = f"/collections/{collection_code}/{last_modified_start_date}"
        if last_modified_end_date:
            endpoint += f"/{last_modified_end_date}"

        params = {"offsetMark": offset_mark, "pageSize": page_size}
        data = self._get(endpoint, params)
        return CollectionPackages(**data)

    def iter_collection_packages(
        self,
        collection_code: str,
        last_modified_start_date: str,
        last_modified_end_date: Optional[str] = None,
        page_size: int = 100,
    ):
        """
        Iterator for all packages in a collection (handles pagination automatically).

        Args:
            collection_code: Collection code
            last_modified_start_date: Start date in ISO 8601 format
            last_modified_end_date: Optional end date in ISO 8601 format
            page_size: Number of results per page

        Yields:
            CollectionPackages objects for each page
        """
        offset_mark = "*"
        while True:
            result = self.get_collection_packages(
                collection_code,
                last_modified_start_date,
                last_modified_end_date,
                offset_mark,
                page_size,
            )
            yield result

            if not result.next_page:
                break

            # Extract offsetMark from nextPage URL
            if "offsetMark=" in result.next_page:
                offset_mark = result.next_page.split("offsetMark=")[1].split("&")[0]
            else:
                break

    # Published Service

    def get_published_packages(
        self,
        date_issued_start: str,
        date_issued_end: Optional[str] = None,
        offset_mark: str = "*",
        page_size: int = 100,
        collection: Optional[str] = None,
        doc_class: Optional[str] = None,
        congress: Optional[str] = None,
        modified_since: Optional[str] = None,
    ) -> PublishedPackages:
        """
        Get packages by publication date.

        Args:
            date_issued_start: Start date (YYYY-MM-DD)
            date_issued_end: Optional end date (YYYY-MM-DD)
            offset_mark: Pagination offset mark
            page_size: Number of results per page
            collection: Comma-separated collection codes
            doc_class: Filter by document class
            congress: Filter by congress number
            modified_since: ISO 8601 timestamp for lastModified filter

        Returns:
            PublishedPackages with list of packages
        """
        endpoint = f"/published/{date_issued_start}"
        if date_issued_end:
            endpoint += f"/{date_issued_end}"

        params = {"offsetMark": offset_mark, "pageSize": page_size}
        if collection:
            params["collection"] = collection
        if doc_class:
            params["docClass"] = doc_class
        if congress:
            params["congress"] = congress
        if modified_since:
            params["modifiedSince"] = modified_since

        data = self._get(endpoint, params)
        return PublishedPackages(**data)

    # Package Service

    def get_package_summary(self, package_id: str) -> PackageSummary:
        """
        Get complete summary information for a package.

        Args:
            package_id: Unique package identifier

        Returns:
            PackageSummary with full package metadata
        """
        data = self._get(f"/packages/{package_id}/summary")
        return PackageSummary(**data)

    def get_package_content(
        self, package_id: str, content_type: str = "pdf"
    ) -> httpx.Response:
        """
        Get package content in specified format.

        Args:
            package_id: Unique package identifier
            content_type: Content type (pdf, xml, htm, mods, premis, zip)

        Returns:
            httpx.Response with content
        """
        params = {"api_key": self.api_key}
        return self.client.get(
            f"{self.BASE_URL}/packages/{package_id}/{content_type}", params=params
        )

    # Granules Service

    def get_package_granules(
        self, package_id: str, offset_mark: str = "*", page_size: int = 100
    ) -> GranuleList:
        """
        Get list of granules for a package.

        Args:
            package_id: Package identifier
            offset_mark: Pagination offset mark
            page_size: Number of results per page

        Returns:
            GranuleList with granule information
        """
        params = {"offsetMark": offset_mark, "pageSize": page_size}
        data = self._get(f"/packages/{package_id}/granules", params)
        return GranuleList(**data)

    def get_granule_summary(self, package_id: str, granule_id: str) -> GranuleSummary:
        """
        Get complete summary for a specific granule.

        Args:
            package_id: Package identifier
            granule_id: Granule identifier

        Returns:
            GranuleSummary with full granule metadata
        """
        data = self._get(f"/packages/{package_id}/granules/{granule_id}/summary")
        return GranuleSummary(**data)

    # Search Service

    def search(
        self,
        query: str,
        page_size: int = 100,
        offset_mark: str = "*",
        sorts: Optional[List[Dict[str, str]]] = None,
    ) -> SearchResults:
        """
        Search for packages and granules.

        Args:
            query: Search query string
            page_size: Number of results per page
            offset_mark: Pagination offset mark
            sorts: List of sort specifications

        Returns:
            SearchResults with matching items
        """
        if sorts is None:
            sorts = [{"field": "score", "sortOrder": "DESC"}]

        search_query = SearchQuery(
            query=query, page_size=str(page_size), offset_mark=offset_mark, sorts=sorts
        )

        data = self._post("/search", json_data=search_query.model_dump(by_alias=True))
        return SearchResults(**data)

    # Related Service

    def get_related(self, package_id: str) -> Dict[str, Any]:
        """
        Get related documents for a package.

        Args:
            package_id: Package identifier

        Returns:
            Dictionary of related document information
        """
        return self._get(f"/related/{package_id}")

    def get_related_by_type(self, package_id: str, relationship_type: str) -> Dict[str, Any]:
        """
        Get related documents of a specific type.

        Args:
            package_id: Package identifier
            relationship_type: Type of relationship (e.g., 'BILLS', 'HOB', 'CPD')

        Returns:
            Dictionary of related documents
        """
        return self._get(f"/related/{package_id}/{relationship_type}")

    # DataFrame Conversion Methods

    def collections_to_dataframe(self) -> pd.DataFrame:
        """
        Get all collections as a pandas DataFrame.

        Returns:
            DataFrame with collection information
        """
        collections = self.list_collections()
        return pd.DataFrame([c.model_dump() for c in collections.collections])

    def packages_to_dataframe(
        self,
        collection_code: str,
        last_modified_start_date: str,
        last_modified_end_date: Optional[str] = None,
        max_pages: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get collection packages as a pandas DataFrame.

        Args:
            collection_code: Collection code
            last_modified_start_date: Start date
            last_modified_end_date: Optional end date
            max_pages: Maximum number of pages to fetch (None for all)

        Returns:
            DataFrame with package information
        """
        all_packages = []
        page_count = 0

        for page in self.iter_collection_packages(
            collection_code, last_modified_start_date, last_modified_end_date
        ):
            all_packages.extend([p.model_dump() for p in page.packages])
            page_count += 1
            if max_pages and page_count >= max_pages:
                break

        return pd.DataFrame(all_packages)

    def search_to_dataframe(
        self, query: str, max_results: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get search results as a pandas DataFrame.

        Args:
            query: Search query string
            max_results: Maximum number of results (None for all)

        Returns:
            DataFrame with search results
        """
        results = self.search(query)
        result_items = [r.model_dump() for r in results.results]

        if max_results:
            result_items = result_items[:max_results]

        return pd.DataFrame(result_items)
