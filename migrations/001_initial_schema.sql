-- Initial schema for GovInfo database
-- This script creates the core tables for storing GovInfo data

-- Collections table
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_code VARCHAR(50) UNIQUE NOT NULL,
    collection_name VARCHAR(255) NOT NULL,
    package_count INTEGER NOT NULL,
    granule_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_collections_code ON collections(collection_code);

-- Packages table
CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT,
    collection_id INTEGER NOT NULL,
    collection_code VARCHAR(50) NOT NULL,
    collection_name VARCHAR(255),
    category VARCHAR(100),
    date_issued VARCHAR(50),
    last_modified TIMESTAMP,
    branch VARCHAR(50),
    congress VARCHAR(10),
    session VARCHAR(10),
    download_links JSON,
    related_links JSON,
    references JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
);

CREATE INDEX IF NOT EXISTS ix_packages_package_id ON packages(package_id);
CREATE INDEX IF NOT EXISTS ix_packages_collection_code ON packages(collection_code);
CREATE INDEX IF NOT EXISTS ix_packages_collection_date ON packages(collection_id, date_issued);
CREATE INDEX IF NOT EXISTS ix_packages_last_modified ON packages(last_modified);

-- Granules table
CREATE TABLE IF NOT EXISTS granules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    granule_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT,
    package_id INTEGER NOT NULL,
    package_identifier VARCHAR(255) NOT NULL,
    granule_class VARCHAR(100),
    collection_code VARCHAR(50),
    date_issued VARCHAR(50),
    last_modified TIMESTAMP,
    download_links JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (package_id) REFERENCES packages(id)
);

CREATE INDEX IF NOT EXISTS ix_granules_granule_id ON granules(granule_id);
CREATE INDEX IF NOT EXISTS ix_granules_package_identifier ON granules(package_identifier);
CREATE INDEX IF NOT EXISTS ix_granules_package_date ON granules(package_id, date_issued);

-- Search cache table
CREATE TABLE IF NOT EXISTS search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    query TEXT NOT NULL,
    results JSON NOT NULL,
    result_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_search_cache_query_hash ON search_cache(query_hash);
CREATE INDEX IF NOT EXISTS ix_search_cache_created_at ON search_cache(created_at);
CREATE INDEX IF NOT EXISTS ix_search_cache_expires_at ON search_cache(expires_at);

-- Create views for common queries

-- View: Recent packages by collection
CREATE VIEW IF NOT EXISTS v_recent_packages AS
SELECT 
    p.package_id,
    p.title,
    p.collection_code,
    c.collection_name,
    p.date_issued,
    p.last_modified,
    p.congress,
    p.session
FROM packages p
JOIN collections c ON p.collection_id = c.id
ORDER BY p.last_modified DESC;

-- View: Collection statistics
CREATE VIEW IF NOT EXISTS v_collection_stats AS
SELECT 
    c.collection_code,
    c.collection_name,
    c.package_count AS reported_package_count,
    COUNT(DISTINCT p.id) AS actual_package_count,
    c.granule_count AS reported_granule_count,
    COUNT(DISTINCT g.id) AS actual_granule_count,
    MAX(p.last_modified) AS latest_package_modified
FROM collections c
LEFT JOIN packages p ON c.id = p.collection_id
LEFT JOIN granules g ON p.id = g.package_id
GROUP BY c.id, c.collection_code, c.collection_name, c.package_count, c.granule_count;

-- View: Packages with granules
CREATE VIEW IF NOT EXISTS v_packages_with_granules AS
SELECT 
    p.package_id,
    p.title AS package_title,
    p.collection_code,
    p.date_issued,
    COUNT(g.id) AS granule_count
FROM packages p
LEFT JOIN granules g ON p.id = g.package_id
GROUP BY p.id, p.package_id, p.title, p.collection_code, p.date_issued
HAVING COUNT(g.id) > 0;
