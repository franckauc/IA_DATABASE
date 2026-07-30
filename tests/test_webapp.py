from __future__ import annotations

import sqlite3
from pathlib import Path

from ia_database.webapp import render_page

ROOT = Path(__file__).resolve().parents[1]


def _seeded_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "catalog.db"
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    seed = (ROOT / "database" / "seed.sql").read_text(encoding="utf-8")
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema)
        connection.executescript(seed)
    return database_path


def test_render_page_lists_results_and_escapes_html(tmp_path: Path) -> None:
    database_path = _seeded_database(tmp_path)
    page = render_page(database_path, term="", category="", tag="")

    assert "<table>" in page
    assert "ChatGPT" in page
    assert "16 résultat" in page or "résultat(s)" in page


def test_render_page_filters_by_category(tmp_path: Path) -> None:
    database_path = _seeded_database(tmp_path)
    page = render_page(database_path, term="", category="programmation", tag="")

    assert "Cursor" in page
    assert "ElevenLabs" not in page


def test_render_page_no_results_message(tmp_path: Path) -> None:
    database_path = _seeded_database(tmp_path)
    page = render_page(database_path, term="motintrouvablexyz", category="", tag="")

    assert "Aucun résultat." in page
