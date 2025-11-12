#!/usr/bin/env python3
"""
Script to ingest data from GovInfo API into local database.

Usage:
    python scripts/ingest_data.py --api-key YOUR_KEY --collections
    python scripts/ingest_data.py --api-key YOUR_KEY --collection BILLS --start-date 2024-01-01
"""

import argparse
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from govinfo_client import GovInfoClient
from govinfo_client.db import init_db, get_engine
from govinfo_client.db.session import sessionmaker
from govinfo_client.services import DataIngestion

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Ingest GovInfo data into local database")
    parser.add_argument("--api-key", required=True, help="GovInfo API key")
    parser.add_argument(
        "--database-url", default="sqlite:///govinfo.db", help="Database URL"
    )
    parser.add_argument(
        "--collections", action="store_true", help="Ingest all collections"
    )
    parser.add_argument("--collection", help="Specific collection code to ingest")
    parser.add_argument("--start-date", help="Start date (ISO 8601)")
    parser.add_argument("--end-date", help="End date (ISO 8601)")
    parser.add_argument(
        "--max-pages", type=int, help="Maximum pages to fetch (for testing)"
    )
    parser.add_argument(
        "--fetch-summaries",
        action="store_true",
        help="Fetch full package summaries (slower)",
    )
    parser.add_argument(
        "--fetch-granules", action="store_true", help="Fetch granules for packages"
    )

    args = parser.parse_args()

    # Initialize database
    console.print("[bold blue]Initializing database...[/bold blue]")
    init_db(args.database_url)

    # Create client and session
    client = GovInfoClient(args.api_key)
    engine = get_engine(args.database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        ingestion = DataIngestion(client, session)

        # Ingest collections
        if args.collections:
            console.print("[bold green]Ingesting collections...[/bold green]")
            count = ingestion.ingest_collections()
            console.print(f"[green]✓[/green] Ingested {count} collections")

        # Ingest specific collection
        if args.collection:
            if not args.start_date:
                args.start_date = (datetime.now() - timedelta(days=30)).strftime(
                    "%Y-%m-%dT00:00:00Z"
                )

            console.print(
                f"[bold green]Ingesting packages from {args.collection}...[/bold green]"
            )
            console.print(f"  Start date: {args.start_date}")
            console.print(f"  End date: {args.end_date or 'Not specified'}")
            console.print(f"  Fetch summaries: {args.fetch_summaries}")

            count = ingestion.ingest_collection_packages(
                args.collection,
                args.start_date,
                args.end_date,
                max_pages=args.max_pages,
                fetch_summaries=args.fetch_summaries,
            )
            console.print(f"[green]✓[/green] Ingested {count} packages")

        console.print("[bold green]✓ Data ingestion complete![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise
    finally:
        session.close()
        client.close()


if __name__ == "__main__":
    main()
