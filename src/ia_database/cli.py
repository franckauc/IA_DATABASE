"""Interface en ligne de commande du catalogue IA."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path
from typing import Sequence

from ia_database.database import default_database_path, initialize_database, seed_database


def database_path(value: str | None) -> Path:
    """Résout le chemin de base par défaut ou celui fourni par l'utilisateur."""
    return Path(value) if value else default_database_path()


def add_database_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--database", help="Chemin vers le fichier SQLite.")


def query_rows(path: Path, term: str, category: str | None, limit: int) -> list[dict[str, object]]:
    """Recherche les fiches par nom, description ou catégorie."""
    filters = ["(LOWER(item.name) LIKE :term OR LOWER(COALESCE(item.description, '')) LIKE :term)"]
    parameters: dict[str, object] = {"term": f"%{term.lower()}%", "limit": limit}
    if category:
        filters.append(
            "EXISTS (SELECT 1 FROM item_categories AS link "
            "JOIN categories AS category ON category.id = link.category_id "
            "WHERE link.item_id = item.id AND category.slug = :category)"
        )
        parameters["category"] = category

    sql = f"""
        SELECT
            item.slug,
            item.name,
            item.item_type,
            item.description,
            item.official_url,
            item.api_available,
            item.works_offline,
            item.is_open_source,
            company.name AS company,
            COALESCE(GROUP_CONCAT(DISTINCT category.name), '') AS categories
        FROM catalog_items AS item
        LEFT JOIN companies AS company ON company.id = item.company_id
        LEFT JOIN item_categories AS link ON link.item_id = item.id
        LEFT JOIN categories AS category ON category.id = link.category_id
        WHERE {' AND '.join(filters)}
        GROUP BY item.id
        ORDER BY item.name COLLATE NOCASE
        LIMIT :limit
    """
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(sql, parameters)]


def export_rows(path: Path) -> list[dict[str, object]]:
    """Retourne les fiches complètes dans un format plat destiné à l'export."""
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                item.slug, item.name, item.item_type, item.description, item.official_url,
                item.documentation_url, item.github_url, company.name AS company,
                item.api_available, item.works_offline, item.is_open_source,
                COALESCE(GROUP_CONCAT(DISTINCT category.name), '') AS categories,
                COALESCE(GROUP_CONCAT(DISTINCT platform.name), '') AS platforms
            FROM catalog_items AS item
            LEFT JOIN companies AS company ON company.id = item.company_id
            LEFT JOIN item_categories AS item_category ON item_category.item_id = item.id
            LEFT JOIN categories AS category ON category.id = item_category.category_id
            LEFT JOIN item_platforms AS item_platform ON item_platform.item_id = item.id
            LEFT JOIN platforms AS platform ON platform.id = item_platform.platform_id
            GROUP BY item.id
            ORDER BY item.name COLLATE NOCASE
            """
        )
        return [dict(row) for row in rows]


def command_init(args: argparse.Namespace) -> int:
    path = database_path(args.database)
    initialize_database(path)
    print(f"Base initialisée : {path}")
    return 0


def command_seed(args: argparse.Namespace) -> int:
    path = database_path(args.database)
    seed_database(path)
    print(f"Données de démarrage chargées : {path}")
    return 0


def command_search(args: argparse.Namespace) -> int:
    path = database_path(args.database)
    if not path.exists():
        print("Base absente : exécutez d'abord `python -m ia_database seed`.", file=sys.stderr)
        return 2
    rows = query_rows(path, args.term, args.category, args.limit)
    if not rows:
        print("Aucun résultat.")
        return 0
    for row in rows:
        flags = ", ".join(
            label
            for label, active in (
                ("API", row["api_available"]),
                ("local", row["works_offline"]),
                ("open source", row["is_open_source"]),
            )
            if active
        )
        print(f"{row['name']} [{row['item_type']}] — {row['company'] or 'Éditeur inconnu'}")
        print(f"  Catégories : {row['categories'] or '—'} | {flags or '—'}")
        print(f"  {row['official_url'] or '—'}")
    return 0


def command_export(args: argparse.Namespace) -> int:
    path = database_path(args.database)
    if not path.exists():
        print("Base absente : exécutez d'abord `python -m ia_database seed`.", file=sys.stderr)
        return 2
    rows = export_rows(path)
    output = Path(args.output) if args.output else PROJECT_EXPORT_PATH(args.format)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        columns = list(rows[0]) if rows else ["slug", "name"]
        with output.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    print(f"Export créé : {output}")
    return 0


def PROJECT_EXPORT_PATH(format_name: str) -> Path:
    return default_database_path().parents[1] / "data" / "exports" / f"catalogue_ia.{format_name}"


def command_stats(args: argparse.Namespace) -> int:
    path = database_path(args.database)
    if not path.exists():
        print("Base absente : exécutez d'abord `python -m ia_database seed`.", file=sys.stderr)
        return 2
    with sqlite3.connect(path) as connection:
        items = connection.execute("SELECT COUNT(*) FROM catalog_items").fetchone()[0]
        categories = connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        sources = connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    print(f"{items} fiches | {categories} catégories | {sources} sources")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="ia-database", description="Catalogue IA local.")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Crée le schéma SQLite.")
    add_database_option(init)
    init.set_defaults(handler=command_init)

    seed = commands.add_parser("seed", help="Charge les catégories et fiches initiales.")
    add_database_option(seed)
    seed.set_defaults(handler=command_seed)

    search = commands.add_parser("search", help="Recherche des fiches dans le catalogue.")
    search.add_argument("term", nargs="?", default="", help="Mot recherché.")
    search.add_argument("--category", help="Slug de catégorie, ex. programmation.")
    search.add_argument("--limit", type=int, default=30, help="Nombre maximal de résultats.")
    add_database_option(search)
    search.set_defaults(handler=command_search)

    export = commands.add_parser("export", help="Exporte les fiches en CSV ou JSON.")
    export.add_argument("--format", choices=("csv", "json"), default="csv")
    export.add_argument("--output", help="Chemin du fichier généré.")
    add_database_option(export)
    export.set_defaults(handler=command_export)

    stats = commands.add_parser("stats", help="Affiche un résumé du catalogue.")
    add_database_option(stats)
    stats.set_defaults(handler=command_stats)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
