"""Accès à la base SQLite et chargement des données de démarrage."""

from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
SEED_PATH = PROJECT_ROOT / "database" / "seed.sql"


def default_database_path() -> Path:
    """Retourne l'emplacement de la base locale par défaut."""
    return PROJECT_ROOT / "database" / "ai_catalog.db"


def connect(database_path: Path) -> sqlite3.Connection:
    """Ouvre une connexion SQLite en activant les clés étrangères."""
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    """Ajoute une colonne à une base déjà créée si elle n'existe pas encore.

    `executescript(schema.sql)` ne modifie jamais une table déjà existante :
    cette fonction permet de faire évoluer le schéma sans perdre les données
    déjà collectées par les utilisateurs.
    """
    columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def initialize_database(database_path: Path) -> None:
    """Crée la base et son schéma s'ils n'existent pas encore, et la met à niveau sinon."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(database_path) as connection:
        connection.executescript(schema)
        _ensure_column(connection, "catalog_items", "downloads", "downloads INTEGER")
        _ensure_column(connection, "catalog_items", "likes", "likes INTEGER")
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_catalog_items_downloads ON catalog_items(downloads)"
        )


def seed_database(database_path: Path) -> None:
    """Insère le jeu initial idempotent de catégories et de fiches sourcées."""
    initialize_database(database_path)
    seed = SEED_PATH.read_text(encoding="utf-8")
    with connect(database_path) as connection:
        connection.executescript(seed)
