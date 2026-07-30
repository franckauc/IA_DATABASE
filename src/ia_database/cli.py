"""Interface en ligne de commande du catalogue IA."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path

from ia_database.database import connect, default_database_path, initialize_database, seed_database
from ia_database.exporters.xlsx import export_workbook


def database_path(value: str | None) -> Path:
    """Résout le chemin de base par défaut ou celui fourni par l'utilisateur."""
    return Path(value) if value else default_database_path()


def add_database_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--database", help="Chemin vers le fichier SQLite.")


POPULARITY_EXPRESSION = "(COALESCE(item.downloads, 0) + COALESCE(item.likes, 0) * 20)"
SORT_ORDERINGS = {
    "name": "item.name COLLATE NOCASE",
    "popularity": f"{POPULARITY_EXPRESSION} DESC, item.name COLLATE NOCASE",
}


def _connect_readonly(path: Path) -> sqlite3.Connection:
    """Ouvre la base en lecture seule au niveau SQLite (`mode=ro`).

    Utilisé par les consommateurs qui ne doivent jamais écrire (ex. le
    serveur web local) : même un bug applicatif ne peut pas y modifier la
    base, la connexion refuse toute écriture au niveau du moteur.
    """
    uri = f"file:{Path(path).resolve().as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def query_rows(
    path: Path,
    term: str,
    category: str | None,
    tag: str | None,
    limit: int,
    sort: str = "name",
    read_only: bool = False,
) -> list[dict[str, object]]:
    """Recherche les fiches par nom, description, catégorie ou tag."""
    filters = ["(LOWER(item.name) LIKE :term OR LOWER(COALESCE(item.description, '')) LIKE :term)"]
    parameters: dict[str, object] = {"term": f"%{term.lower()}%", "limit": limit}
    if category:
        filters.append(
            "EXISTS (SELECT 1 FROM item_categories AS link "
            "JOIN categories AS category ON category.id = link.category_id "
            "WHERE link.item_id = item.id AND category.slug = :category)"
        )
        parameters["category"] = category
    if tag:
        filters.append(
            "EXISTS (SELECT 1 FROM item_tags AS link "
            "JOIN tags AS tag ON tag.id = link.tag_id "
            "WHERE link.item_id = item.id AND tag.slug = :tag)"
        )
        parameters["tag"] = tag

    order_by = SORT_ORDERINGS.get(sort, SORT_ORDERINGS["name"])
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
            item.downloads,
            item.likes,
            company.name AS company,
            COALESCE(GROUP_CONCAT(DISTINCT category.name), '') AS categories,
            COALESCE(GROUP_CONCAT(DISTINCT tag.name), '') AS tags
        FROM catalog_items AS item
        LEFT JOIN companies AS company ON company.id = item.company_id
        LEFT JOIN item_categories AS link ON link.item_id = item.id
        LEFT JOIN categories AS category ON category.id = link.category_id
        LEFT JOIN item_tags AS tag_link ON tag_link.item_id = item.id
        LEFT JOIN tags AS tag ON tag.id = tag_link.tag_id
        WHERE {' AND '.join(filters)}
        GROUP BY item.id
        ORDER BY {order_by}
        LIMIT :limit
    """
    connection = _connect_readonly(path) if read_only else sqlite3.connect(path)
    with connection:
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
                item.downloads, item.likes,
                COALESCE(GROUP_CONCAT(DISTINCT category.name), '') AS categories,
                COALESCE(GROUP_CONCAT(DISTINCT platform.name), '') AS platforms,
                COALESCE(GROUP_CONCAT(DISTINCT tag.name), '') AS tags,
                COALESCE(GROUP_CONCAT(DISTINCT license.name), '') AS licenses
            FROM catalog_items AS item
            LEFT JOIN companies AS company ON company.id = item.company_id
            LEFT JOIN item_categories AS item_category ON item_category.item_id = item.id
            LEFT JOIN categories AS category ON category.id = item_category.category_id
            LEFT JOIN item_platforms AS item_platform ON item_platform.item_id = item.id
            LEFT JOIN platforms AS platform ON platform.id = item_platform.platform_id
            LEFT JOIN item_tags AS item_tag ON item_tag.item_id = item.id
            LEFT JOIN tags AS tag ON tag.id = item_tag.tag_id
            LEFT JOIN item_licenses AS item_license ON item_license.item_id = item.id
            LEFT JOIN licenses AS license ON license.id = item_license.license_id
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
    rows = query_rows(path, args.term, args.category, args.tag, args.limit, args.sort)
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
        if row["tags"]:
            print(f"  Tags : {row['tags']}")
        if row["downloads"] or row["likes"]:
            print(f"  Popularité : {row['downloads'] or 0} téléchargements, {row['likes'] or 0} favoris")
        print(f"  {row['official_url'] or '—'}")
    return 0


def command_export(args: argparse.Namespace) -> int:
    path = database_path(args.database)
    if not path.exists():
        print("Base absente : exécutez d'abord `python -m ia_database seed`.", file=sys.stderr)
        return 2
    output = Path(args.output) if args.output else PROJECT_EXPORT_PATH(args.format)
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "xlsx":
        export_workbook(path, output, with_icons=not args.no_icons, insecure=args.insecure)
        print(f"Classeur créé : {output}")
        return 0

    rows = export_rows(path)
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


def command_collect(args: argparse.Namespace) -> int:
    from ia_database.collectors import huggingface, ollama, openrouter

    path = database_path(args.database)
    initialize_database(path)

    jobs = {
        "huggingface": lambda connection: huggingface.collect(
            connection, limit=args.limit, verify=not args.insecure, token=args.hf_token
        ),
        "openrouter": lambda connection: openrouter.collect(
            connection, limit=args.limit, verify=not args.insecure
        ),
        "ollama": lambda connection: ollama.collect(
            connection, host=args.ollama_host, verify=not args.insecure
        ),
    }
    sources = list(jobs) if args.source == "all" else [args.source]

    exit_code = 0
    with connect(path) as connection:
        for source in sources:
            summary = jobs[source](connection)
            connection.commit()
            print(summary.line())
            for error in summary.errors:
                print(f"  ! {error}", file=sys.stderr)
                exit_code = 1
    return exit_code


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
        companies = connection.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        tags = connection.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        open_source = connection.execute(
            "SELECT COUNT(*) FROM catalog_items WHERE is_open_source = 1"
        ).fetchone()[0]
        offline = connection.execute(
            "SELECT COUNT(*) FROM catalog_items WHERE works_offline = 1"
        ).fetchone()[0]
        with_api = connection.execute(
            "SELECT COUNT(*) FROM catalog_items WHERE api_available = 1"
        ).fetchone()[0]
        by_type = connection.execute(
            "SELECT item_type, COUNT(*) FROM catalog_items GROUP BY item_type ORDER BY item_type"
        ).fetchall()

    print(f"{items} fiches | {companies} éditeurs | {categories} catégories | {tags} tags | {sources} sources")
    print(f"API : {with_api} | hors ligne : {offline} | open source : {open_source}")
    if by_type:
        detail = ", ".join(f"{item_type} : {count}" for item_type, count in by_type)
        print(f"Par type — {detail}")
    return 0


def command_report(args: argparse.Namespace) -> int:
    """Affiche, par source, le nombre de fiches liées et la dernière collecte."""
    path = database_path(args.database)
    if not path.exists():
        print("Base absente : exécutez d'abord `python -m ia_database seed`.", file=sys.stderr)
        return 2
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                source.name,
                source.is_active,
                COUNT(record.id) AS nb_fiches,
                MAX(record.retrieved_at) AS derniere_collecte,
                (
                    SELECT COUNT(*) FROM item_history AS history
                    JOIN source_records AS sr ON sr.id = history.source_record_id
                    WHERE sr.source_id = source.id
                ) AS nb_changements
            FROM sources AS source
            LEFT JOIN source_records AS record ON record.source_id = source.id
            GROUP BY source.id
            ORDER BY derniere_collecte IS NULL, derniere_collecte DESC, source.name
            """
        ).fetchall()

    if not rows:
        print("Aucune source enregistrée.")
        return 0
    for row in rows:
        state = "active" if row["is_active"] else "inactive"
        last = row["derniere_collecte"] or "jamais collectée"
        print(f"{row['name']} [{state}] — {row['nb_fiches']} fiches, {row['nb_changements']} changements")
        print(f"  Dernière collecte : {last}")
    return 0


def command_serve(args: argparse.Namespace) -> int:
    path = database_path(args.database)
    if not path.exists():
        print("Base absente : exécutez d'abord `python -m ia_database seed`.", file=sys.stderr)
        return 2
    from ia_database.webapp import run_server

    run_server(path, host=args.host, port=args.port)
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
    search.add_argument("--tag", help="Slug de tag, ex. open-weights.")
    search.add_argument("--limit", type=int, default=30, help="Nombre maximal de résultats.")
    search.add_argument(
        "--sort",
        choices=("name", "popularity"),
        default="name",
        help="Tri par nom ou par popularité (téléchargements + favoris, quand connus).",
    )
    add_database_option(search)
    search.set_defaults(handler=command_search)

    export = commands.add_parser("export", help="Exporte les fiches en CSV, JSON ou classeur Excel.")
    export.add_argument("--format", choices=("csv", "json", "xlsx"), default="csv")
    export.add_argument("--output", help="Chemin du fichier généré.")
    export.add_argument(
        "--no-icons",
        action="store_true",
        help="N'inclut pas les icônes dans le classeur Excel (plus rapide, fonctionne hors ligne).",
    )
    export.add_argument(
        "--insecure",
        action="store_true",
        help="Désactive la vérification TLS lors du téléchargement des icônes (réseau avec inspection HTTPS cassée).",
    )
    add_database_option(export)
    export.set_defaults(handler=command_export)

    collect = commands.add_parser("collect", help="Collecte des fiches depuis les API publiques.")
    collect.add_argument(
        "source", choices=("huggingface", "openrouter", "ollama", "all"), help="Source à collecter."
    )
    collect.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Nombre maximal de fiches (Hugging Face/OpenRouter). 0 = sans limite "
        "(Hugging Face pagine jusqu'à épuisement du catalogue ou 20000 fiches ; "
        "OpenRouter renvoie tout son catalogue, qui tient déjà en un seul appel).",
    )
    collect.add_argument(
        "--ollama-host", default="http://localhost:11434", help="Adresse de l'API locale Ollama."
    )
    collect.add_argument(
        "--insecure",
        action="store_true",
        help="Désactive la vérification TLS (réseau avec inspection HTTPS cassée). À éviter sinon.",
    )
    collect.add_argument(
        "--hf-token",
        default=None,
        help="Jeton Hugging Face (sinon variable d'environnement HF_TOKEN). Optionnel : augmente les quotas.",
    )
    add_database_option(collect)
    collect.set_defaults(handler=command_collect)

    stats = commands.add_parser("stats", help="Affiche un résumé du catalogue.")
    add_database_option(stats)
    stats.set_defaults(handler=command_stats)

    report = commands.add_parser("report", help="Affiche l'état de synchronisation par source.")
    add_database_option(report)
    report.set_defaults(handler=command_report)

    serve = commands.add_parser("serve", help="Lance une interface de recherche web locale (lecture seule).")
    serve.add_argument("--host", default="127.0.0.1", help="Adresse d'écoute.")
    serve.add_argument("--port", type=int, default=8765, help="Port d'écoute.")
    add_database_option(serve)
    serve.set_defaults(handler=command_serve)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
