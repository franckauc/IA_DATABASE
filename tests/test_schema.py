from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_schema_creates_core_tables(tmp_path: Path) -> None:
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    database_path = tmp_path / "catalog.db"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema)
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {"catalog_items", "categories", "sources", "source_records"} <= tables
