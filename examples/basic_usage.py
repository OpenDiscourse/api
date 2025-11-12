#!/usr/bin/env python3
"""
Basic usage examples for the GovInfo API client.
"""

import os
from govinfo_client import GovInfoClient

# Get API key from environment variable
API_KEY = os.getenv("GOVINFO_API_KEY", "DEMO_KEY")


def example_list_collections():
    """Example: List all available collections."""
    print("=== Example: List Collections ===\n")

    with GovInfoClient(API_KEY) as client:
        collections = client.list_collections()

        print(f"Total collections: {len(collections.collections)}\n")

        for coll in collections.collections[:5]:  # Show first 5
            print(f"Code: {coll.collection_code}")
            print(f"Name: {coll.collection_name}")
            print(f"Packages: {coll.package_count}")
            print(f"Granules: {coll.granule_count or 'N/A'}")
            print()


def example_get_recent_bills():
    """Example: Get recent congressional bills."""
    print("=== Example: Recent Congressional Bills ===\n")

    with GovInfoClient(API_KEY) as client:
        # Get bills from the last 30 days
        packages = client.get_collection_packages(
            collection_code="BILLS",
            last_modified_start_date="2024-01-01T00:00:00Z",
            page_size=10,
        )

        print(f"Found {packages.count} total bills")
        print(f"Showing {len(packages.packages)} bills:\n")

        for pkg in packages.packages:
            print(f"Package ID: {pkg.package_id}")
            print(f"Last Modified: {pkg.last_modified}")
            print(f"Link: {pkg.package_link}")
            print()


def example_get_package_details():
    """Example: Get detailed information for a specific package."""
    print("=== Example: Package Details ===\n")

    with GovInfoClient(API_KEY) as client:
        # Get details for a specific bill
        package_id = "BILLS-115hr1625enr"
        summary = client.get_package_summary(package_id)

        print(f"Title: {summary.title}")
        print(f"Collection: {summary.collection_name}")
        print(f"Date Issued: {summary.date_issued}")
        print(f"Congress: {summary.congress}")
        print(f"Bill Type: {summary.bill_type}")
        print(f"Bill Number: {summary.bill_number}")
        print(f"Pages: {summary.pages}")
        print("\nDownload Links:")
        if summary.download:
            print(f"  PDF: {summary.download.pdf_link}")
            print(f"  XML: {summary.download.xml_link}")
            print(f"  HTML: {summary.download.txt_link}")


def example_search():
    """Example: Search for documents."""
    print("=== Example: Search ===\n")

    with GovInfoClient(API_KEY) as client:
        # Search for documents about climate change
        results = client.search(
            query='collection:(BILLS) AND "climate change"', page_size=5
        )

        print(f"Total results: {results.count}")
        print(f"Showing {len(results.results)} results:\n")

        for item in results.results:
            print(f"Package ID: {item.package_id}")
            print(f"Title: {item.title}")
            print(f"Collection: {item.collection_name}")
            print(f"Date Issued: {item.date_issued}")
            print()


def example_dataframe_usage():
    """Example: Convert data to pandas DataFrame."""
    print("=== Example: DataFrame Usage ===\n")

    with GovInfoClient(API_KEY) as client:
        # Get collections as DataFrame
        df = client.collections_to_dataframe()

        print("Collections DataFrame:")
        print(df.head())
        print(f"\nShape: {df.shape}")
        print(f"\nColumns: {df.columns.tolist()}")

        # Basic statistics
        print("\nPackage counts by collection (top 5):")
        print(df.nlargest(5, "package_count")[["collection_code", "package_count"]])


def main():
    """Run all examples."""
    examples = [
        example_list_collections,
        example_get_recent_bills,
        example_get_package_details,
        example_search,
        example_dataframe_usage,
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
            if i < len(examples):
                print("\n" + "=" * 60 + "\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}\n")


if __name__ == "__main__":
    main()
