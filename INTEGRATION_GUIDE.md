# GovInfo API Integration Guide

This guide provides comprehensive instructions for integrating the GovInfo API client into your Python projects.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [API Endpoints](#api-endpoints)
5. [Database Integration](#database-integration)
6. [Data Analysis](#data-analysis)
7. [Advanced Usage](#advanced-usage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Installation

### Option 1: Install from Source

```bash
git clone https://github.com/OpenDiscourse/api.git
cd api
pip install -e .
```

### Option 2: Install with Dependencies

```bash
pip install -e ".[dev]"  # Includes development tools
```

### Requirements

- Python 3.9 or higher
- API key from [api.govinfo.gov](https://www.govinfo.gov/api-signup)

## Quick Start

### 1. Set Up Your Environment

Create a `.env` file in your project root:

```env
GOVINFO_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///govinfo.db
```

### 2. Basic API Usage

```python
import os
from govinfo_client import GovInfoClient

# Load API key from environment
api_key = os.getenv("GOVINFO_API_KEY")
client = GovInfoClient(api_key)

# List collections
collections = client.list_collections()
for coll in collections.collections[:5]:
    print(f"{coll.collection_code}: {coll.collection_name}")

# Get recent bills
packages = client.get_collection_packages(
    collection_code="BILLS",
    last_modified_start_date="2024-01-01T00:00:00Z",
    page_size=10
)

print(f"Found {packages.count} bills")
```

### 3. Database Integration

```python
from govinfo_client.db import init_db, get_engine
from govinfo_client.db.session import sessionmaker
from govinfo_client.services import DataIngestion

# Initialize database
init_db("sqlite:///govinfo.db")

# Create session
engine = get_engine("sqlite:///govinfo.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Ingest data
ingestion = DataIngestion(client, session)
ingestion.ingest_collections()

# Ingest recent packages
ingestion.ingest_collection_packages(
    collection_code="BILLS",
    start_date="2024-01-01T00:00:00Z",
    max_pages=5
)

session.close()
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOVINFO_API_KEY` | Your API key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///govinfo.db` |

### Client Configuration

```python
from govinfo_client import GovInfoClient

# Configure timeout
client = GovInfoClient(api_key="KEY", timeout=60.0)

# Use context manager for automatic cleanup
with GovInfoClient(api_key="KEY") as client:
    collections = client.list_collections()
```

## API Endpoints

### Collections

```python
# List all collections
collections = client.list_collections()

# Get packages from a collection
packages = client.get_collection_packages(
    collection_code="BILLS",
    last_modified_start_date="2024-01-01T00:00:00Z",
    last_modified_end_date="2024-12-31T23:59:59Z",
    page_size=100
)

# Iterate through all pages
for page in client.iter_collection_packages(
    collection_code="FR",
    last_modified_start_date="2024-01-01T00:00:00Z"
):
    for pkg in page.packages:
        print(pkg.package_id)
```

### Published

```python
# Get packages by publication date
packages = client.get_published_packages(
    date_issued_start="2024-01-01",
    date_issued_end="2024-01-31",
    collection="BILLS,FR",
    congress="118"
)
```

### Packages

```python
# Get package summary
summary = client.get_package_summary("BILLS-115hr1625enr")

# Download package content
response = client.get_package_content(
    "BILLS-115hr1625enr",
    content_type="pdf"
)

# Save to file
with open("bill.pdf", "wb") as f:
    f.write(response.content)
```

### Granules

```python
# Get granules for a package
granules = client.get_package_granules("CREC-2024-01-03")

# Get specific granule
granule = client.get_granule_summary(
    "CREC-2024-01-03",
    "CREC-2024-01-03-pt1-PgH1"
)
```

### Search

```python
# Basic search
results = client.search(
    query="collection:(BILLS) AND congress:118",
    page_size=100
)

# Advanced search
results = client.search(
    query='tax reform',
    sorts=[{"field": "publishdate", "sortOrder": "DESC"}]
)
```

### Related

```python
# Get related documents
related = client.get_related("BILLS-116hr748enr")

# Get specific relationship type
bills = client.get_related_by_type("BILLS-116hr748enr", "BILLS")
```

## Database Integration

### Schema Overview

The database schema includes:

- **collections**: Collection metadata
- **packages**: Package information
- **granules**: Granule information
- **search_cache**: Cached search results

### Working with the Database

```python
from sqlalchemy import select
from govinfo_client.db import get_engine, models
from govinfo_client.db.session import sessionmaker

engine = get_engine("sqlite:///govinfo.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Query collections
stmt = select(models.Collection).order_by(models.Collection.package_count.desc())
collections = session.scalars(stmt).all()

# Query packages
stmt = select(models.Package).where(
    models.Package.collection_code == "BILLS",
    models.Package.congress == "118"
).limit(10)
packages = session.scalars(stmt).all()

session.close()
```

### Using SQL Views

```python
import pandas as pd

engine = get_engine("sqlite:///govinfo.db")

# Query collection statistics
df = pd.read_sql("SELECT * FROM v_collection_stats", engine)
print(df)

# Query recent packages
df = pd.read_sql("SELECT * FROM v_recent_packages LIMIT 100", engine)
print(df)
```

## Data Analysis

### DataFrame Conversion

```python
# Convert collections to DataFrame
df = client.collections_to_dataframe()

# Convert packages to DataFrame
df = client.packages_to_dataframe(
    collection_code="BILLS",
    last_modified_start_date="2024-01-01T00:00:00Z",
    max_pages=10
)

# Convert search results to DataFrame
df = client.search_to_dataframe(
    query="climate change",
    max_results=100
)
```

### Analysis Examples

```python
import pandas as pd
import matplotlib.pyplot as plt

# Analyze package counts by collection
df = client.collections_to_dataframe()
top_10 = df.nlargest(10, 'package_count')

top_10.plot(
    x='collection_code',
    y='package_count',
    kind='bar',
    title='Top 10 Collections by Package Count'
)
plt.tight_layout()
plt.savefig('collections.png')

# Time series analysis
packages_df = client.packages_to_dataframe(
    collection_code="BILLS",
    last_modified_start_date="2024-01-01T00:00:00Z",
    max_pages=20
)

packages_df['date'] = pd.to_datetime(packages_df['last_modified'])
daily_counts = packages_df.groupby(packages_df['date'].dt.date).size()

daily_counts.plot(
    kind='line',
    title='Daily Package Updates'
)
plt.tight_layout()
plt.savefig('daily_updates.png')
```

## Advanced Usage

### Custom Pagination

```python
offset_mark = "*"
all_packages = []

while True:
    result = client.get_collection_packages(
        collection_code="BILLS",
        last_modified_start_date="2024-01-01T00:00:00Z",
        offset_mark=offset_mark,
        page_size=100
    )
    
    all_packages.extend(result.packages)
    
    if not result.next_page:
        break
    
    # Extract next offset mark
    offset_mark = result.next_page.split("offsetMark=")[1].split("&")[0]
```

### Bulk Data Ingestion

```python
from govinfo_client.utils import get_date_range

# Get date range for last 30 days
start_date, end_date = get_date_range(days=30)

# Ingest multiple collections
collections = ["BILLS", "FR", "CREC"]

for coll in collections:
    print(f"Ingesting {coll}...")
    count = ingestion.ingest_collection_packages(
        collection_code=coll,
        start_date=start_date,
        end_date=end_date,
        fetch_summaries=True
    )
    print(f"Ingested {count} packages from {coll}")
```

### Error Handling

```python
import httpx

try:
    summary = client.get_package_summary("INVALID-ID")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        print("Package not found")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"HTTP error: {e}")
except httpx.TimeoutException:
    print("Request timed out")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Use Context Managers

```python
# Good
with GovInfoClient(api_key="KEY") as client:
    data = client.list_collections()

# Also good for database sessions
with SessionLocal() as session:
    # Do database operations
    pass
```

### 2. Respect Rate Limits

The DEMO_KEY has a limit of 40 requests per hour. Personal keys have higher limits.

```python
import time

for package_id in package_ids:
    try:
        summary = client.get_package_summary(package_id)
        # Process summary
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            # Wait before retrying
            time.sleep(60)
            continue
```

### 3. Cache Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_summary(package_id: str):
    return client.get_package_summary(package_id)
```

### 4. Use Batch Operations

```python
# Ingest in batches
for i in range(0, len(package_ids), 100):
    batch = package_ids[i:i+100]
    for pkg_id in batch:
        # Process package
        pass
    session.commit()  # Commit batch
```

## Troubleshooting

### Connection Errors

```python
# Increase timeout
client = GovInfoClient(api_key="KEY", timeout=120.0)
```

### Database Errors

```python
# Reset database
from govinfo_client.db import init_db

init_db("sqlite:///govinfo.db")  # Creates new schema
```

### Import Errors

```bash
# Reinstall package
pip install -e . --force-reinstall
```

### API Key Issues

```bash
# Test API key
curl "https://api.govinfo.gov/collections?api_key=YOUR_KEY"
```

## Support

For issues and questions:

1. Check the [API documentation](https://api.govinfo.gov/docs)
2. Review the [examples](examples/)
3. Open an [issue](https://github.com/OpenDiscourse/api/issues)

## Additional Resources

- [GovInfo API Documentation](https://api.govinfo.gov/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
