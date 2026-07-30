"""Fonctions communes aux collecteurs : upsert, provenance et historique."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field


@dataclass
class CollectionSummary:
    """Bilan d'une collecte : nombre de fiches créées, mises à jour ou ignorées."""

    source: str
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    def line(self) -> str:
        parts = [
            f"{self.created} créées",
            f"{self.updated} mises à jour",
            f"{self.unchanged} inchangées",
        ]
        if self.skipped:
            parts.append(f"{self.skipped} ignorées")
        if self.errors:
            parts.append(f"{len(self.errors)} erreurs")
        return f"{self.source} : " + ", ".join(parts)


# Champs de catalog_items qu'un collecteur peut renseigner et dont les
# changements sont journalisés dans item_history.
TRACKED_ITEM_FIELDS = (
    "name",
    "description",
    "official_url",
    "documentation_url",
    "github_url",
    "company_id",
    "launch_year",
    "is_open_source",
    "works_offline",
    "api_available",
    "status",
)

# Champs mis à jour à chaque collecte mais volontairement exclus de
# item_history : ce sont des métriques (popularité) qui varient sans arrêt,
# les y journaliser noierait les changements de champs qui comptent vraiment.
SILENT_UPDATE_FIELDS = ("downloads", "likes")


def get_or_create_source(
    connection: sqlite3.Connection,
    slug: str,
    name: str,
    base_url: str,
    terms_url: str | None = None,
    license_note: str | None = None,
) -> int:
    """Crée la source si nécessaire et retourne son identifiant."""
    connection.execute(
        """
        INSERT INTO sources (slug, name, base_url, terms_url, license_note)
        VALUES (:slug, :name, :base_url, :terms_url, :license_note)
        ON CONFLICT(slug) DO UPDATE SET
            base_url = excluded.base_url,
            terms_url = COALESCE(excluded.terms_url, sources.terms_url),
            license_note = COALESCE(excluded.license_note, sources.license_note)
        """,
        {
            "slug": slug,
            "name": name,
            "base_url": base_url,
            "terms_url": terms_url,
            "license_note": license_note,
        },
    )
    row = connection.execute("SELECT id FROM sources WHERE slug = ?", (slug,)).fetchone()
    return int(row[0])


def get_or_create_company(
    connection: sqlite3.Connection,
    name: str,
    website_url: str | None = None,
    country_code: str | None = None,
) -> int:
    """Crée l'éditeur si nécessaire et retourne son identifiant."""
    connection.execute(
        """
        INSERT INTO companies (name, website_url, country_code)
        VALUES (:name, :website_url, :country_code)
        ON CONFLICT(name) DO UPDATE SET
            website_url = COALESCE(excluded.website_url, companies.website_url),
            country_code = COALESCE(excluded.country_code, companies.country_code),
            updated_at = CURRENT_TIMESTAMP
        """,
        {"name": name, "website_url": website_url, "country_code": country_code},
    )
    row = connection.execute("SELECT id FROM companies WHERE name = ?", (name,)).fetchone()
    return int(row[0])


def ensure_category(
    connection: sqlite3.Connection, slug: str, name: str, description: str | None = None
) -> int:
    connection.execute(
        "INSERT OR IGNORE INTO categories (slug, name, description) VALUES (?, ?, ?)",
        (slug, name, description),
    )
    row = connection.execute("SELECT id FROM categories WHERE slug = ?", (slug,)).fetchone()
    return int(row[0])


def ensure_platform(connection: sqlite3.Connection, slug: str, name: str) -> int:
    connection.execute(
        "INSERT OR IGNORE INTO platforms (slug, name) VALUES (?, ?)", (slug, name)
    )
    row = connection.execute("SELECT id FROM platforms WHERE slug = ?", (slug,)).fetchone()
    return int(row[0])


def link_item_category(connection: sqlite3.Connection, item_id: int, category_id: int) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO item_categories (item_id, category_id) VALUES (?, ?)",
        (item_id, category_id),
    )


def link_item_platform(connection: sqlite3.Connection, item_id: int, platform_id: int) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO item_platforms (item_id, platform_id) VALUES (?, ?)",
        (item_id, platform_id),
    )


def upsert_catalog_item(
    connection: sqlite3.Connection,
    slug: str,
    item_type: str,
    fields: dict[str, object],
    source_record_id: int | None = None,
) -> tuple[int, bool, dict[str, tuple[object, object]]]:
    """Crée ou met à jour une fiche et journalise les changements de champs.

    Retourne (item_id, a_ete_cree, changements) où changements associe un nom
    de champ à (ancienne_valeur, nouvelle_valeur).
    """
    connection.row_factory = sqlite3.Row
    existing = connection.execute("SELECT * FROM catalog_items WHERE slug = ?", (slug,)).fetchone()

    if existing is None:
        columns = ["slug", "item_type", *[key for key in fields if fields[key] is not None]]
        values = {"slug": slug, "item_type": item_type}
        values.update({key: value for key, value in fields.items() if value is not None})
        placeholders = ", ".join(f":{column}" for column in columns)
        connection.execute(
            f"INSERT INTO catalog_items ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )
        item_id = int(connection.execute("SELECT id FROM catalog_items WHERE slug = ?", (slug,)).fetchone()[0])
        return item_id, True, {}

    current = dict(existing)
    item_id = int(current["id"])

    changes: dict[str, tuple[object, object]] = {}
    updates: dict[str, object] = {}
    for name, new_value in fields.items():
        if new_value is None:
            continue
        if name in TRACKED_ITEM_FIELDS:
            old_value = current.get(name)
            if old_value != new_value:
                changes[name] = (old_value, new_value)
                updates[name] = new_value
        elif name in SILENT_UPDATE_FIELDS and current.get(name) != new_value:
            # Métriques qui varient à chaque collecte (popularité) : on les
            # tient à jour sans polluer item_history à chaque changement.
            updates[name] = new_value

    if updates:
        assignments = ", ".join(f"{name} = :{name}" for name in updates)
        updates["id"] = item_id
        connection.execute(
            f"UPDATE catalog_items SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = :id",
            updates,
        )
        for name, (old_value, new_value) in changes.items():
            connection.execute(
                """
                INSERT INTO item_history (item_id, field_name, old_value, new_value, source_record_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (item_id, name, str(old_value) if old_value is not None else None, str(new_value), source_record_id),
            )

    return item_id, False, changes


def record_source(
    connection: sqlite3.Connection,
    source_id: int,
    item_id: int,
    external_id: str,
    source_url: str | None = None,
    raw_hash: str | None = None,
) -> int:
    """Enregistre ou met à jour la provenance d'une fiche et retourne son id."""
    connection.execute(
        """
        INSERT INTO source_records (source_id, item_id, external_id, source_url, raw_hash)
        VALUES (:source_id, :item_id, :external_id, :source_url, :raw_hash)
        ON CONFLICT(source_id, item_id) DO UPDATE SET
            external_id = excluded.external_id,
            source_url = excluded.source_url,
            retrieved_at = CURRENT_TIMESTAMP,
            raw_hash = excluded.raw_hash
        """,
        {
            "source_id": source_id,
            "item_id": item_id,
            "external_id": external_id,
            "source_url": source_url,
            "raw_hash": raw_hash,
        },
    )
    row = connection.execute(
        "SELECT id FROM source_records WHERE source_id = ? AND item_id = ?",
        (source_id, item_id),
    ).fetchone()
    return int(row[0])


def get_or_create_license(
    connection: sqlite3.Connection, name: str, spdx_id: str | None = None, url: str | None = None
) -> int:
    connection.execute(
        """
        INSERT INTO licenses (name, spdx_id, url)
        VALUES (:name, :spdx_id, :url)
        ON CONFLICT(name) DO UPDATE SET
            spdx_id = COALESCE(licenses.spdx_id, excluded.spdx_id),
            url = COALESCE(licenses.url, excluded.url)
        """,
        {"name": name, "spdx_id": spdx_id, "url": url},
    )
    row = connection.execute("SELECT id FROM licenses WHERE name = ?", (name,)).fetchone()
    return int(row[0])


def link_item_license(connection: sqlite3.Connection, item_id: int, license_id: int) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO item_licenses (item_id, license_id) VALUES (?, ?)",
        (item_id, license_id),
    )


def upsert_pricing_plan(
    connection: sqlite3.Connection,
    item_id: int,
    plan_name: str,
    pricing_type: str,
    price_amount: float | None = None,
    currency: str | None = None,
    billing_period: str | None = None,
    url: str | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO pricing_plans (item_id, plan_name, pricing_type, price_amount, currency, billing_period, url)
        VALUES (:item_id, :plan_name, :pricing_type, :price_amount, :currency, :billing_period, :url)
        ON CONFLICT(item_id, plan_name) DO UPDATE SET
            pricing_type = excluded.pricing_type,
            price_amount = excluded.price_amount,
            currency = excluded.currency,
            billing_period = excluded.billing_period,
            url = excluded.url
        """,
        {
            "item_id": item_id,
            "plan_name": plan_name,
            "pricing_type": pricing_type,
            "price_amount": price_amount,
            "currency": currency,
            "billing_period": billing_period,
            "url": url,
        },
    )
