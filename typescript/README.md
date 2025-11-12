# TypeScript/JavaScript Client (Planned)

A TypeScript/JavaScript client library for the GovInfo API is planned for future development. This will provide similar functionality to the Python client with strong TypeScript typing.

## Planned Features

- ✅ Full TypeScript support with type definitions
- ✅ Promise-based async/await API
- ✅ Support for Node.js and browser environments
- ✅ Automatic pagination handling
- ✅ Built-in retry logic
- ✅ Request caching

## Example Usage (Planned)

```typescript
import { GovInfoClient } from '@govinfo/api-client';

// Initialize client
const client = new GovInfoClient({
  apiKey: process.env.GOVINFO_API_KEY
});

// List collections
const collections = await client.listCollections();

// Get packages
const packages = await client.getCollectionPackages({
  collectionCode: 'BILLS',
  lastModifiedStartDate: '2024-01-01T00:00:00Z',
  pageSize: 100
});

// Search
const results = await client.search({
  query: 'collection:(BILLS) AND congress:118',
  pageSize: 100
});

// Get package summary
const summary = await client.getPackageSummary('BILLS-115hr1625enr');
```

## Installation (When Available)

```bash
npm install @govinfo/api-client
# or
yarn add @govinfo/api-client
```

## Type Definitions

```typescript
interface Collection {
  collectionCode: string;
  collectionName: string;
  packageCount: number;
  granuleCount?: number;
}

interface PackageSummary {
  packageId: string;
  title: string;
  collectionCode: string;
  collectionName: string;
  dateIssued?: string;
  download?: DownloadLinks;
  lastModified?: Date;
}

interface DownloadLinks {
  pdfLink?: string;
  xmlLink?: string;
  txtLink?: string;
  modsLink?: string;
  premisLink?: string;
  zipLink?: string;
}
```

## Contributing

If you're interested in contributing to the TypeScript client development:

1. Check the [issues](https://github.com/OpenDiscourse/api/issues)
2. See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines
3. Focus on maintaining parity with the Python client

## Current Alternative

While the TypeScript client is in development, you can use the GovInfo API directly:

```typescript
import axios from 'axios';

const API_KEY = process.env.GOVINFO_API_KEY;
const BASE_URL = 'https://api.govinfo.gov';

async function listCollections() {
  const response = await axios.get(`${BASE_URL}/collections`, {
    params: { api_key: API_KEY }
  });
  return response.data;
}

async function getPackageSummary(packageId: string) {
  const response = await axios.get(
    `${BASE_URL}/packages/${packageId}/summary`,
    { params: { api_key: API_KEY } }
  );
  return response.data;
}
```

## Related

- [Python Client](../CLIENT_README.md) - Full-featured Python implementation
- [API Documentation](https://api.govinfo.gov/docs) - Official API docs
