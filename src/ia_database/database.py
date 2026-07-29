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


def initialize_database(database_path: Path) -> None:
    """Crée la base et son schéma s'ils n'existent pas encore."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(database_path) as connection:
        connection.executescript(schema)


def seed_database(database_path: Path) -> None:
    """Insère le jeu initial idempotent de catégories et de fiches sourcées."""
    initialize_database(database_path)
    seed = SEED_PATH.read_text(encoding="utf-8")
    with connect(database_path) as connection:
        connection.executescript(seed)
