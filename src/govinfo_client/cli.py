"""Command-line interface for GovInfo client."""

import sys
import argparse
from typing import Optional
from rich.console import Console
from rich.table import Table

console = Console()


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GovInfo API Client - Access government information programmatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Collections command
    collections_parser = subparsers.add_parser("collections", help="List all collections")
    collections_parser.add_argument("--api-key", required=True, help="GovInfo API key")
    collections_parser.add_argument("--format", choices=["table", "json"], default="table")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for documents")
    search_parser.add_argument("--api-key", required=True, help="GovInfo API key")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Number of results")

    # Package command
    package_parser = subparsers.add_parser("package", help="Get package details")
    package_parser.add_argument("--api-key", required=True, help="GovInfo API key")
    package_parser.add_argument("package_id", help="Package ID")

    # Init database command
    init_parser = subparsers.add_parser("init-db", help="Initialize database")
    init_parser.add_argument(
        "--database-url", default="sqlite:///govinfo.db", help="Database URL"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "collections":
            return cmd_collections(args)
        elif args.command == "search":
            return cmd_search(args)
        elif args.command == "package":
            return cmd_package(args)
        elif args.command == "init-db":
            return cmd_init_db(args)
        else:
            console.print(f"[red]Unknown command: {args.command}[/red]")
            return 1
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


def cmd_collections(args) -> int:
    """List all collections."""
    from govinfo_client import GovInfoClient

    with GovInfoClient(args.api_key) as client:
        collections = client.list_collections()

        if args.format == "table":
            table = Table(title="GovInfo Collections")
            table.add_column("Code", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Packages", justify="right", style="yellow")
            table.add_column("Granules", justify="right", style="magenta")

            for coll in collections.collections:
                table.add_row(
                    coll.collection_code,
                    coll.collection_name,
                    str(coll.package_count),
                    str(coll.granule_count or "N/A"),
                )

            console.print(table)
        else:
            import json

            data = [c.model_dump() for c in collections.collections]
            console.print_json(json.dumps(data, indent=2))

    return 0


def cmd_search(args) -> int:
    """Search for documents."""
    from govinfo_client import GovInfoClient

    with GovInfoClient(args.api_key) as client:
        results = client.search(args.query, page_size=args.limit)

        console.print(f"\n[bold]Found {results.count} total results[/bold]\n")

        table = Table(title=f"Search Results (showing {len(results.results)})")
        table.add_column("Package ID", style="cyan")
        table.add_column("Title", style="green", max_width=50)
        table.add_column("Collection", style="yellow")

        for item in results.results:
            title = item.title or "N/A"
            if len(title) > 50:
                title = title[:47] + "..."
            table.add_row(
                item.package_id or "N/A",
                title,
                item.collection_code or "N/A",
            )

        console.print(table)

    return 0


def cmd_package(args) -> int:
    """Get package details."""
    from govinfo_client import GovInfoClient

    with GovInfoClient(args.api_key) as client:
        summary = client.get_package_summary(args.package_id)

        console.print(f"\n[bold cyan]Package: {summary.package_id}[/bold cyan]\n")
        console.print(f"[bold]Title:[/bold] {summary.title}")
        console.print(f"[bold]Collection:[/bold] {summary.collection_name}")
        console.print(f"[bold]Date Issued:[/bold] {summary.date_issued or 'N/A'}")

        if summary.congress:
            console.print(f"[bold]Congress:[/bold] {summary.congress}")

        if summary.download:
            console.print("\n[bold]Download Links:[/bold]")
            if summary.download.pdf_link:
                console.print(f"  PDF: {summary.download.pdf_link}")
            if summary.download.xml_link:
                console.print(f"  XML: {summary.download.xml_link}")
            if summary.download.txt_link:
                console.print(f"  HTML: {summary.download.txt_link}")

    return 0


def cmd_init_db(args) -> int:
    """Initialize database."""
    from govinfo_client.db import init_db

    console.print(f"[bold blue]Initializing database at {args.database_url}...[/bold blue]")
    init_db(args.database_url)
    console.print("[green]✓ Database initialized successfully![/green]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
