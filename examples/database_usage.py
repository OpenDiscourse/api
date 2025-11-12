#!/usr/bin/env python3
"""
Database usage examples - ingesting and querying local data.
"""

import os
from datetime import datetime, timedelta
from govinfo_client import GovInfoClient
from govinfo_client.db import init_db, get_engine, models
from govinfo_client.db.session import sessionmaker
from govinfo_client.services import DataIngestion
from sqlalchemy import select
import pandas as pd

API_KEY = os.getenv("GOVINFO_API_KEY", "DEMO_KEY")
DATABASE_URL = "sqlite:///govinfo_example.db"


def example_setup_database():
    """Example: Initialize the database."""
    print("=== Setting up database ===\n")

    # Initialize database schema
    init_db(DATABASE_URL)
    print("✓ Database initialized")


def example_ingest_collections():
    """Example: Ingest collection metadata."""
    print("\n=== Ingesting Collections ===\n")

    client = GovInfoClient(API_KEY)
    engine = get_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        ingestion = DataIngestion(client, session)
        count = ingestion.ingest_collections()
        print(f"✓ Ingested {count} collections")
    finally:
        session.close()
        client.close()


def example_ingest_packages():
    """Example: Ingest recent packages from a collection."""
    print("\n=== Ingesting Packages ===\n")

    client = GovInfoClient(API_KEY)
    engine = get_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        ingestion = DataIngestion(client, session)

        # Ingest Federal Register documents from the last 7 days
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z")

        print(f"Ingesting FR documents from {start_date}...")
        count = ingestion.ingest_collection_packages(
            collection_code="FR",
            start_date=start_date,
            max_pages=1,  # Limit to 1 page for demo
            fetch_summaries=False,
        )
        print(f"✓ Ingested {count} packages")
    finally:
        session.close()
        client.close()


def example_query_collections():
    """Example: Query collections from database."""
    print("\n=== Querying Collections ===\n")

    engine = get_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Query all collections
        stmt = select(models.Collection).order_by(models.Collection.package_count.desc())
        collections = session.scalars(stmt).all()

        print(f"Total collections in database: {len(collections)}\n")

        print("Top 5 collections by package count:")
        for coll in collections[:5]:
            print(f"  {coll.collection_code}: {coll.collection_name}")
            print(f"    Packages: {coll.package_count}, Granules: {coll.granule_count or 'N/A'}")
    finally:
        session.close()


def example_query_packages():
    """Example: Query packages from database."""
    print("\n=== Querying Packages ===\n")

    engine = get_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Query packages
        stmt = (
            select(models.Package)
            .order_by(models.Package.last_modified.desc())
            .limit(10)
        )
        packages = session.scalars(stmt).all()

        print(f"Most recent packages:\n")
        for pkg in packages:
            print(f"  {pkg.package_id}")
            print(f"    Collection: {pkg.collection_code}")
            print(f"    Last Modified: {pkg.last_modified}")
            if pkg.title:
                title = pkg.title[:60] + "..." if len(pkg.title) > 60 else pkg.title
                print(f"    Title: {title}")
            print()
    finally:
        session.close()


def example_export_to_dataframe():
    """Example: Export database data to pandas DataFrame."""
    print("\n=== Export to DataFrame ===\n")

    engine = get_engine(DATABASE_URL)

    # Load packages into DataFrame
    query = "SELECT * FROM packages ORDER BY last_modified DESC LIMIT 100"
    df = pd.read_sql(query, engine)

    print(f"Packages DataFrame shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")

    if not df.empty:
        print("\nFirst few rows:")
        print(df[["package_id", "collection_code", "date_issued"]].head())

        # Group by collection
        print("\nPackages by collection:")
        print(df["collection_code"].value_counts())


def example_sql_views():
    """Example: Query using SQL views."""
    print("\n=== Using SQL Views ===\n")

    engine = get_engine(DATABASE_URL)

    # Query collection statistics view
    query = "SELECT * FROM v_collection_stats"
    df = pd.read_sql(query, engine)

    if not df.empty:
        print("Collection Statistics:")
        print(df[["collection_code", "actual_package_count", "latest_package_modified"]])


def main():
    """Run all database examples."""
    examples = [
        example_setup_database,
        example_ingest_collections,
        example_ingest_packages,
        example_query_collections,
        example_query_packages,
        example_export_to_dataframe,
        example_sql_views,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}\n")

    print("\n✓ Database examples complete!")
    print(f"Database file: {DATABASE_URL}")


if __name__ == "__main__":
    main()
