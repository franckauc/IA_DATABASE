"""Fonctions minimales d'accès à la base SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(database_path: Path) -> sqlite3.Connection:
    """Ouvre une connexion SQLite en activant les clés étrangères."""
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
