# GovInfo API Client Library

A comprehensive, strongly-typed Python client library for the [GovInfo API](https://api.govinfo.gov) with database integration, pandas DataFrame support, and full API coverage.

## Features

- ✅ **Strongly Typed**: Full Pydantic models for all API responses
- ✅ **Complete API Coverage**: All endpoints including Collections, Packages, Granules, Search, Published, and Related
- ✅ **Database Integration**: SQLAlchemy models with SQLite support (easily extensible to PostgreSQL, MySQL, etc.)
- ✅ **DataFrame Support**: Built-in pandas DataFrame conversion for data analysis
- ✅ **SQL Migrations**: Ready-to-use SQL scripts for database setup
- ✅ **Data Ingestion**: Scripts to populate local database from API
- ✅ **Type Safety**: Full type hints for IDE autocomplete and type checking
- ✅ **Pagination Handling**: Automatic pagination support for large datasets
- ✅ **Comprehensive Tests**: Unit and integration tests with high coverage

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/OpenDiscourse/api.git
cd api

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Requirements

- Python 3.9+
- Dependencies: pydantic, httpx, pandas, sqlalchemy, rich

## Quick Start

### 1. Get an API Key

Sign up for a free API key at [api.govinfo.gov/api-signup](https://www.govinfo.gov/api-signup).

### 2. Basic Usage

```python
from govinfo_client import GovInfoClient

# Initialize the client
client = GovInfoClient(api_key="YOUR_API_KEY")

# List all collections
collections = client.list_collections()
for coll in collections.collections:
    print(f"{coll.collection_code}: {coll.collection_name}")

# Get recent bills
packages = client.get_collection_packages(
    collection_code="BILLS",
    last_modified_start_date="2024-01-01T00:00:00Z",
    page_size=10
)

# Get package details
summary = client.get_package_summary("BILLS-115hr1625enr")
print(f"Title: {summary.title}")
print(f"PDF: {summary.download.pdf_link}")

# Search for documents
results = client.search(
    query='collection:(BILLS) AND "climate change"',
    page_size=10
)

# Convert to DataFrame
df = client.collections_to_dataframe()
print(df.head())
```

### 3. Database Integration

```python
from govinfo_client import GovInfoClient
from govinfo_client.db import init_db, get_engine
from govinfo_client.db.session import sessionmaker
from govinfo_client.services import DataIngestion

# Initialize database
init_db("sqlite:///govinfo.db")

# Setup ingestion
client = GovInfoClient(api_key="YOUR_API_KEY")
engine = get_engine("sqlite:///govinfo.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

ingestion = DataIngestion(client, session)

# Ingest collections
ingestion.ingest_collections()

# Ingest recent packages
ingestion.ingest_collection_packages(
    collection_code="BILLS",
    start_date="2024-01-01T00:00:00Z",
    max_pages=5,
    fetch_summaries=True
)
```

### 4. Query Local Data

```python
import pandas as pd
from govinfo_client.db import get_engine

# Connect to database
engine = get_engine("sqlite:///govinfo.db")

# Load data into DataFrame
query = """
SELECT package_id, title, collection_code, date_issued 
FROM packages 
ORDER BY last_modified DESC 
LIMIT 100
"""
df = pd.read_sql(query, engine)

# Analyze data
print(df.groupby("collection_code").size())
```

## API Endpoints Coverage

### Collections Service

```python
# List all collections
collections = client.list_collections()

# Get packages from a collection
packages = client.get_collection_packages(
    collection_code="BILLS",
    last_modified_start_date="2024-01-01T00:00:00Z",
    last_modified_end_date="2024-12-31T23:59:59Z",
    offset_mark="*",
    page_size=100
)

# Iterate through all pages
for page in client.iter_collection_packages(
    collection_code="FR",
    last_modified_start_date="2024-01-01T00:00:00Z"
):
    for package in page.packages:
        print(package.package_id)
```

### Published Service

```python
# Get packages by publication date
packages = client.get_published_packages(
    date_issued_start="2024-01-01",
    date_issued_end="2024-01-31",
    collection="BILLS,FR",
    page_size=100
)
```

### Packages Service

```python
# Get package summary
summary = client.get_package_summary("BILLS-115hr1625enr")

# Download package content
response = client.get_package_content("BILLS-115hr1625enr", content_type="pdf")
with open("bill.pdf", "wb") as f:
    f.write(response.content)
```

### Granules Service

```python
# Get granules for a package
granules = client.get_package_granules("CREC-2024-01-03", page_size=100)

# Get specific granule details
granule = client.get_granule_summary(
    "CREC-2024-01-03",
    "CREC-2024-01-03-pt1-PgH1"
)
```

### Search Service

```python
# Basic search
results = client.search(
    query="collection:(BILLS) AND congress:118",
    page_size=100
)

# Advanced search with custom sorting
results = client.search(
    query='tax reform',
    sorts=[
        {"field": "publishdate", "sortOrder": "DESC"}
    ]
)
```

### Related Service

```python
# Get all related documents
related = client.get_related("BILLS-116hr748enr")

# Get specific relationship type
bills = client.get_related_by_type("BILLS-116hr748enr", "BILLS")
```

## Database Schema

The library includes a complete SQLite database schema with the following tables:

- **collections**: Collection metadata
- **packages**: Package information with full metadata
- **granules**: Granule information
- **search_cache**: Cached search results

### Views

- **v_recent_packages**: Recent packages by collection
- **v_collection_stats**: Collection statistics
- **v_packages_with_granules**: Packages that have granules

### Migrations

Run the SQL migration script to create the database schema:

```bash
sqlite3 govinfo.db < migrations/001_initial_schema.sql
```

Or use the Python API:

```python
from govinfo_client.db import init_db
init_db("sqlite:///govinfo.db")
```

## Command Line Tools

### Ingest Data

```bash
# Ingest all collections
python scripts/ingest_data.py --api-key YOUR_KEY --collections

# Ingest specific collection
python scripts/ingest_data.py \
    --api-key YOUR_KEY \
    --collection BILLS \
    --start-date 2024-01-01T00:00:00Z \
    --fetch-summaries

# Limit pages for testing
python scripts/ingest_data.py \
    --api-key YOUR_KEY \
    --collection FR \
    --start-date 2024-01-01T00:00:00Z \
    --max-pages 5
```

### Query Data

```bash
# List collections
python scripts/query_data.py --collections

# List packages
python scripts/query_data.py --packages --collection BILLS --limit 50

# Export to CSV
python scripts/query_data.py --packages --collection FR --output fr_packages.csv

# Export to JSON
python scripts/query_data.py --collections --output collections.json

# Filter by congress
python scripts/query_data.py --packages --congress 118 --output congress_118.csv
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py`: Basic API client usage
- `database_usage.py`: Database integration examples

Run examples:

```bash
export GOVINFO_API_KEY=your_key_here
python examples/basic_usage.py
python examples/database_usage.py
```

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=govinfo_client --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v
```

### Run Integration Tests

Integration tests require a valid API key:

```bash
export GOVINFO_API_KEY=your_key_here
pytest tests/integration/
```

## Data Analysis with Pandas

The library provides seamless integration with pandas for data analysis:

```python
import matplotlib.pyplot as plt
from govinfo_client import GovInfoClient

client = GovInfoClient(api_key="YOUR_KEY")

# Get collections as DataFrame
df = client.collections_to_dataframe()

# Analyze package counts
df.nlargest(10, 'package_count').plot(
    x='collection_code', 
    y='package_count', 
    kind='bar'
)
plt.show()

# Get packages and analyze by date
packages_df = client.packages_to_dataframe(
    collection_code="BILLS",
    last_modified_start_date="2024-01-01T00:00:00Z",
    max_pages=10
)

# Time series analysis
packages_df['date'] = pd.to_datetime(packages_df['last_modified'])
daily_counts = packages_df.groupby(packages_df['date'].dt.date).size()
daily_counts.plot()
plt.show()
```

## Advanced Usage

### Custom Database Connection

```python
from govinfo_client.db import get_engine, init_db

# PostgreSQL
init_db("postgresql://user:password@localhost/govinfo")

# MySQL
init_db("mysql://user:password@localhost/govinfo")
```

### Async Support (Coming Soon)

The library is designed to support async operations in future releases.

### Custom Retry Logic

```python
import httpx
from govinfo_client import GovInfoClient

# Configure custom timeout and retries
transport = httpx.HTTPTransport(retries=3)
client = GovInfoClient(api_key="YOUR_KEY", timeout=60.0)
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is in the public domain. See [LICENSE.md](LICENSE.md) for details.

## Resources

- [GovInfo API Documentation](https://api.govinfo.gov/docs)
- [GovInfo Website](https://www.govinfo.gov)
- [API Signup](https://www.govinfo.gov/api-signup)
- [GitHub Issues](https://github.com/OpenDiscourse/api/issues)

## Support

For issues and questions:

1. Check the [API documentation](https://api.govinfo.gov/docs)
2. Review the [examples](examples/)
3. Open an [issue](https://github.com/OpenDiscourse/api/issues)
