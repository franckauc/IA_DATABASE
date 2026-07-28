PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    website_url TEXT,
    country_code TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS catalog_items (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('tool', 'model', 'service', 'framework', 'dataset')),
    description TEXT,
    official_url TEXT,
    documentation_url TEXT,
    github_url TEXT,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    launch_year INTEGER CHECK (launch_year BETWEEN 1940 AND 2100),
    is_open_source INTEGER NOT NULL DEFAULT 0 CHECK (is_open_source IN (0, 1)),
    works_offline INTEGER NOT NULL DEFAULT 0 CHECK (works_offline IN (0, 1)),
    api_available INTEGER NOT NULL DEFAULT 0 CHECK (api_available IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'unknown')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS item_categories (
    item_id INTEGER NOT NULL REFERENCES catalog_items(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, category_id)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS item_tags (
    item_id INTEGER NOT NULL REFERENCES catalog_items(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, tag_id)
);

CREATE TABLE IF NOT EXISTS platforms (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS item_platforms (
    item_id INTEGER NOT NULL REFERENCES catalog_items(id) ON DELETE CASCADE,
    platform_id INTEGER NOT NULL REFERENCES platforms(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, platform_id)
);

CREATE TABLE IF NOT EXISTS licenses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    spdx_id TEXT UNIQUE,
    url TEXT
);

CREATE TABLE IF NOT EXISTS item_licenses (
    item_id INTEGER NOT NULL REFERENCES catalog_items(id) ON DELETE CASCADE,
    license_id INTEGER NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, license_id)
);

CREATE TABLE IF NOT EXISTS pricing_plans (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES catalog_items(id) ON DELETE CASCADE,
    plan_name TEXT NOT NULL,
    pricing_type TEXT NOT NULL CHECK (pricing_type IN ('free', 'freemium', 'paid', 'trial', 'unknown')),
    price_amount REAL CHECK (price_amount >= 0),
    currency TEXT,
    billing_period TEXT,
    url TEXT,
    UNIQUE (item_id, plan_name)
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    base_url TEXT NOT NULL,
    terms_url TEXT,
    license_note TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS source_records (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES catalog_items(id) ON DELETE CASCADE,
    external_id TEXT NOT NULL,
    source_url TEXT,
    retrieved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_hash TEXT,
    UNIQUE (source_id, external_id),
    UNIQUE (source_id, item_id)
);

CREATE TABLE IF NOT EXISTS item_history (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES catalog_items(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    source_record_id INTEGER REFERENCES source_records(id) ON DELETE SET NULL,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_catalog_items_name ON catalog_items(name);
CREATE INDEX IF NOT EXISTS idx_catalog_items_type ON catalog_items(item_type);
CREATE INDEX IF NOT EXISTS idx_source_records_item ON source_records(item_id);

INSERT OR IGNORE INTO schema_version(version) VALUES (1);
