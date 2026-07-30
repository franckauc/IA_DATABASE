from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ia_database.cli import main

ROOT = Path(__file__).resolve().parents[1]


def _seeded_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "catalog.db"
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    seed = (ROOT / "database" / "seed.sql").read_text(encoding="utf-8")
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema)
        connection.executescript(seed)
    return database_path


def test_report_command_lists_sources(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    database_path = _seeded_database(tmp_path)

    exit_code = main(["report", "--database", str(database_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "OpenAI" in output
    assert "fiches" in output


def test_search_command_filters_by_tag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    database_path = _seeded_database(tmp_path)

    exit_code = main(["search", "--tag", "open-weights", "--database", str(database_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Ollama" in output
    assert "ChatGPT" not in output
