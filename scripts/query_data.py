#!/usr/bin/env python3
"""
Script to query data from the local database and export to various formats.

Usage:
    python scripts/query_data.py --collections
    python scripts/query_data.py --packages --collection BILLS --output bills.csv
    python scripts/query_data.py --search "tax reform" --output results.json
"""

import argparse
import os
import json
from sqlalchemy import select, func, and_, or_
from rich.console import Console
from rich.table import Table
import pandas as pd

from govinfo_client.db import get_engine, models
from govinfo_client.db.session import sessionmaker

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Query GovInfo database")
    parser.add_argument(
        "--database-url", default="sqlite:///govinfo.db", help="Database URL"
    )
    parser.add_argument("--collections", action="store_true", help="List all collections")
    parser.add_argument("--packages", action="store_true", help="List packages")
    parser.add_argument("--collection", help="Filter by collection code")
    parser.add_argument("--congress", help="Filter by congress number")
    parser.add_argument("--limit", type=int, default=100, help="Limit results")
    parser.add_argument("--output", help="Output file (CSV, JSON, or Excel)")
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format for console",
    )

    args = parser.parse_args()

    # Create session
    engine = get_engine(args.database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Query collections
        if args.collections:
            stmt = select(models.Collection).order_by(models.Collection.collection_code)
            collections = session.scalars(stmt).all()

            if args.format == "table":
                table = Table(title="GovInfo Collections")
                table.add_column("Code", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Packages", style="yellow")
                table.add_column("Granules", style="magenta")

                for coll in collections:
                    table.add_row(
                        coll.collection_code,
                        coll.collection_name,
                        str(coll.package_count),
                        str(coll.granule_count or "N/A"),
                    )

                console.print(table)
            elif args.format == "json":
                data = [
                    {
                        "collection_code": c.collection_code,
                        "collection_name": c.collection_name,
                        "package_count": c.package_count,
                        "granule_count": c.granule_count,
                    }
                    for c in collections
                ]
                console.print_json(json.dumps(data, indent=2))

            # Save to file if requested
            if args.output:
                df = pd.DataFrame(
                    [
                        {
                            "collection_code": c.collection_code,
                            "collection_name": c.collection_name,
                            "package_count": c.package_count,
                            "granule_count": c.granule_count,
                        }
                        for c in collections
                    ]
                )
                save_dataframe(df, args.output)

        # Query packages
        if args.packages:
            stmt = select(models.Package).order_by(models.Package.last_modified.desc())

            # Apply filters
            if args.collection:
                stmt = stmt.where(models.Package.collection_code == args.collection)
            if args.congress:
                stmt = stmt.where(models.Package.congress == args.congress)

            stmt = stmt.limit(args.limit)
            packages = session.scalars(stmt).all()

            if args.format == "table":
                table = Table(title=f"Packages (showing {len(packages)})")
                table.add_column("Package ID", style="cyan")
                table.add_column("Title", style="green", max_width=50)
                table.add_column("Collection", style="yellow")
                table.add_column("Date Issued", style="magenta")

                for pkg in packages:
                    title = pkg.title[:47] + "..." if pkg.title and len(pkg.title) > 50 else pkg.title or ""
                    table.add_row(
                        pkg.package_id, title, pkg.collection_code, pkg.date_issued or "N/A"
                    )

                console.print(table)
            elif args.format == "json":
                data = [
                    {
                        "package_id": p.package_id,
                        "title": p.title,
                        "collection_code": p.collection_code,
                        "date_issued": p.date_issued,
                        "congress": p.congress,
                        "last_modified": p.last_modified.isoformat() if p.last_modified else None,
                    }
                    for p in packages
                ]
                console.print_json(json.dumps(data, indent=2))

            # Save to file if requested
            if args.output:
                df = pd.DataFrame(
                    [
                        {
                            "package_id": p.package_id,
                            "title": p.title,
                            "collection_code": p.collection_code,
                            "collection_name": p.collection_name,
                            "date_issued": p.date_issued,
                            "congress": p.congress,
                            "session": p.session,
                            "branch": p.branch,
                            "last_modified": p.last_modified.isoformat() if p.last_modified else None,
                        }
                        for p in packages
                    ]
                )
                save_dataframe(df, args.output)

    finally:
        session.close()


def save_dataframe(df: pd.DataFrame, output_file: str):
    """Save DataFrame to file based on extension."""
    ext = os.path.splitext(output_file)[1].lower()

    if ext == ".csv":
        df.to_csv(output_file, index=False)
        console.print(f"[green]✓[/green] Saved to {output_file}")
    elif ext == ".json":
        df.to_json(output_file, orient="records", indent=2)
        console.print(f"[green]✓[/green] Saved to {output_file}")
    elif ext in [".xlsx", ".xls"]:
        df.to_excel(output_file, index=False)
        console.print(f"[green]✓[/green] Saved to {output_file}")
    else:
        console.print(f"[red]Unsupported file format: {ext}[/red]")


if __name__ == "__main__":
    main()
