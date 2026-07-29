from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_seed_is_idempotent_and_keeps_sources(tmp_path: Path) -> None:
    database_path = tmp_path / "catalog.db"
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    seed = (ROOT / "database" / "seed.sql").read_text(encoding="utf-8")

    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema)
        connection.executescript(seed)
        connection.executescript(seed)
        item_count = connection.execute("SELECT COUNT(*) FROM catalog_items").fetchone()[0]
        source_count = connection.execute("SELECT COUNT(*) FROM source_records").fetchone()[0]
        local_count = connection.execute(
            "SELECT COUNT(*) FROM catalog_items WHERE works_offline = 1"
        ).fetchone()[0]

    assert item_count == 16
    assert source_count == item_count
    assert local_count >= 4
