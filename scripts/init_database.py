"""Crée ou met à niveau la base SQLite locale depuis le schéma versionné."""

from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "database" / "schema.sql"
DATABASE_PATH = ROOT / "database" / "ai_catalog.db"


def main() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(schema)
    print(f"Base prête : {DATABASE_PATH}")


if __name__ == "__main__":
    main()
