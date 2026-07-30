from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ia_database.collectors import base, huggingface, ollama, openrouter

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def connection(tmp_path: Path) -> sqlite3.Connection:
    database_path = tmp_path / "catalog.db"
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(schema)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_upsert_catalog_item_creates_then_updates_with_history(connection: sqlite3.Connection) -> None:
    item_id, created, changes = base.upsert_catalog_item(
        connection, "demo-model", "model", {"name": "Demo", "description": "v1", "api_available": 1}
    )
    assert created is True
    assert changes == {}

    item_id_2, created_2, changes_2 = base.upsert_catalog_item(
        connection, "demo-model", "model", {"description": "v2"}
    )
    assert item_id_2 == item_id
    assert created_2 is False
    assert changes_2 == {"description": ("v1", "v2")}

    history = connection.execute(
        "SELECT field_name, old_value, new_value FROM item_history WHERE item_id = ?", (item_id,)
    ).fetchall()
    assert [dict(row) for row in history] == [
        {"field_name": "description", "old_value": "v1", "new_value": "v2"}
    ]

    # Un appel sans changement ne doit rien journaliser de plus.
    _, created_3, changes_3 = base.upsert_catalog_item(connection, "demo-model", "model", {"description": "v2"})
    assert created_3 is False
    assert changes_3 == {}
    history_after = connection.execute(
        "SELECT COUNT(*) FROM item_history WHERE item_id = ?", (item_id,)
    ).fetchone()[0]
    assert history_after == 1


def test_openrouter_collect_creates_items_and_pricing(monkeypatch: pytest.MonkeyPatch, connection: sqlite3.Connection) -> None:
    fake_payload = {
        "data": [
            {
                "id": "openai/gpt-test",
                "name": "OpenAI: GPT Test",
                "description": "Modèle de test.",
                "pricing": {"prompt": "0.000001", "completion": "0.000002"},
            },
            {
                "id": "meta-llama/free-test",
                "name": "Meta: Free Test",
                "description": "Modèle gratuit de test.",
                "pricing": {"prompt": "0", "completion": "0"},
            },
        ]
    }
    monkeypatch.setattr(openrouter, "get_json", lambda url, **kwargs: fake_payload)

    summary = openrouter.collect(connection, limit=None)
    connection.commit()

    assert summary.created == 2
    assert summary.errors == []

    items = connection.execute("SELECT slug, name FROM catalog_items ORDER BY slug").fetchall()
    assert [dict(row) for row in items] == [
        {"slug": "openrouter-meta-llama--free-test", "name": "Meta: Free Test"},
        {"slug": "openrouter-openai--gpt-test", "name": "OpenAI: GPT Test"},
    ]

    paid_item_id = connection.execute(
        "SELECT id FROM catalog_items WHERE slug = 'openrouter-openai--gpt-test'"
    ).fetchone()[0]
    plans = connection.execute(
        "SELECT plan_name, pricing_type, price_amount FROM pricing_plans WHERE item_id = ? ORDER BY plan_name",
        (paid_item_id,),
    ).fetchall()
    assert len(plans) == 2
    assert {dict(plan)["pricing_type"] for plan in plans} == {"paid"}

    free_item_id = connection.execute(
        "SELECT id FROM catalog_items WHERE slug = 'openrouter-meta-llama--free-test'"
    ).fetchone()[0]
    free_plans = connection.execute(
        "SELECT pricing_type FROM pricing_plans WHERE item_id = ?", (free_item_id,)
    ).fetchall()
    assert [dict(plan)["pricing_type"] for plan in free_plans] == ["free"]


def test_openrouter_collect_handles_dynamic_pricing(monkeypatch: pytest.MonkeyPatch, connection: sqlite3.Connection) -> None:
    # OpenRouter renvoie -1 pour une tarification variable : ne doit pas planter
    # sur la contrainte CHECK (price_amount >= 0) ni être compté comme gratuit.
    fake_payload = {
        "data": [
            {
                "id": "provider/dynamic-test",
                "name": "Dynamic Test",
                "description": "Modèle à tarification variable.",
                "pricing": {"prompt": "-1", "completion": "-1"},
            }
        ]
    }
    monkeypatch.setattr(openrouter, "get_json", lambda url, **kwargs: fake_payload)

    summary = openrouter.collect(connection, limit=None)
    connection.commit()

    assert summary.created == 1
    assert summary.errors == []

    item_id = connection.execute(
        "SELECT id FROM catalog_items WHERE slug = 'openrouter-provider--dynamic-test'"
    ).fetchone()[0]
    plans = connection.execute(
        "SELECT pricing_type, price_amount FROM pricing_plans WHERE item_id = ?", (item_id,)
    ).fetchall()
    assert [dict(plan) for plan in plans] == [{"pricing_type": "unknown", "price_amount": None}]


class _FakePage:
    """Simule une réponse `requests` paginée (JSON + en-tête Link)."""

    def __init__(self, payload: list[dict], next_url: str | None = None) -> None:
        self._payload = payload
        self.headers = {"Link": f'<{next_url}>; rel="next"'} if next_url else {}

    def json(self) -> list[dict]:
        return self._payload


def test_huggingface_collect_extracts_license_from_tags(
    monkeypatch: pytest.MonkeyPatch, connection: sqlite3.Connection
) -> None:
    fake_payload = [
        {
            "id": "acme/open-model",
            "pipeline_tag": "text-generation",
            "downloads": 10,
            "likes": 1,
            "tags": ["transformers", "license:apache-2.0"],
        }
    ]
    monkeypatch.setattr(huggingface, "http_get", lambda url, **kwargs: _FakePage(fake_payload))

    summary = huggingface.collect(connection, limit=10)
    connection.commit()

    assert summary.created == 1
    item = connection.execute(
        "SELECT id, is_open_source FROM catalog_items WHERE slug = 'hf-acme--open-model'"
    ).fetchone()
    assert dict(item)["is_open_source"] == 1

    license_row = connection.execute(
        """
        SELECT license.name FROM licenses AS license
        JOIN item_licenses AS il ON il.license_id = license.id
        WHERE il.item_id = ?
        """,
        (item["id"],),
    ).fetchone()
    assert dict(license_row)["name"] == "Apache License 2.0"


def test_huggingface_collect_reports_api_errors(monkeypatch: pytest.MonkeyPatch, connection: sqlite3.Connection) -> None:
    def boom(url: str, **kwargs: object) -> None:
        raise RuntimeError("réseau indisponible")

    monkeypatch.setattr(huggingface, "http_get", boom)
    summary = huggingface.collect(connection, limit=10)
    assert summary.created == 0
    assert summary.errors and "réseau indisponible" in summary.errors[0]


def test_huggingface_collect_paginates_until_limit_reached(
    monkeypatch: pytest.MonkeyPatch, connection: sqlite3.Connection
) -> None:
    page_one = [{"id": f"acme/model-{i}", "pipeline_tag": "text-generation"} for i in range(2)]
    page_two = [{"id": f"acme/model-{i}", "pipeline_tag": "text-generation"} for i in range(2, 4)]
    pages = [_FakePage(page_one, next_url="https://huggingface.co/api/models?cursor=abc"), _FakePage(page_two)]

    def fake_get(url: str, **kwargs: object) -> _FakePage:
        return pages.pop(0)

    monkeypatch.setattr(huggingface, "http_get", fake_get)

    summary = huggingface.collect(connection, limit=3)
    connection.commit()

    assert summary.created == 3  # s'arrête dès que la limite est atteinte, même en cours de page
    count = connection.execute("SELECT COUNT(*) FROM catalog_items").fetchone()[0]
    assert count == 3


def test_ollama_collect_reports_connection_error(monkeypatch: pytest.MonkeyPatch, connection: sqlite3.Connection) -> None:
    def boom(url: str, **kwargs: object) -> None:
        raise RuntimeError("connexion refusée")

    monkeypatch.setattr(ollama, "get_json", boom)
    summary = ollama.collect(connection)
    assert summary.created == 0
    assert summary.errors
    assert "connexion refusée" in summary.errors[0]
