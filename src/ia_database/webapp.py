"""Interface de recherche web locale, en lecture seule, sans dépendance externe.

Sert une seule page HTML générée à la demande depuis la base SQLite. Pensée
pour un usage local (`ia-database serve`) : pas d'authentification, pas
d'écriture, pas de dépendance en dehors de la bibliothèque standard.
"""

from __future__ import annotations

import html
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from ia_database.cli import _connect_readonly, query_rows
from ia_database.icons import favicon_url

# Schémas autorisés pour les liens cliquables. Défense en profondeur : même si
# les collecteurs ne produisent que du http(s) aujourd'hui, on refuse de
# transformer un official_url en lien cliquable s'il change un jour de forme
# (ex. javascript:, data:) — quelle qu'en soit la source.
SAFE_URL_SCHEMES = {"http", "https"}


def _safe_link(url: str | None) -> str | None:
    if not url:
        return None
    return url if urlsplit(url).scheme in SAFE_URL_SCHEMES else None

PAGE_STYLE = """
body { font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a1a; background: #fafafa; }
h1 { margin-bottom: 0.25rem; }
p.subtitle { color: #555; margin-top: 0; }
form { display: flex; gap: 0.75rem; flex-wrap: wrap; margin: 1.5rem 0; }
input, select { padding: 0.5rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 4px; }
input[type=text] { flex: 1; min-width: 200px; }
button { padding: 0.5rem 1rem; border: none; border-radius: 4px; background: #1f4e78; color: white; cursor: pointer; }
table { width: 100%; border-collapse: collapse; background: white; }
th, td { text-align: left; padding: 0.5rem 0.75rem; border-bottom: 1px solid #e5e5e5; vertical-align: top; }
td.icon { width: 2.5rem; padding-right: 0; }
td.icon img { display: block; border-radius: 4px; }
th { background: #1f4e78; color: white; position: sticky; top: 0; }
tr:hover { background: #f0f4f8; }
.badge { display: inline-block; background: #e5edf5; color: #1f4e78; border-radius: 3px; padding: 0.1rem 0.4rem; font-size: 0.8rem; margin-right: 0.2rem; }
.count { color: #555; margin-bottom: 0.5rem; }
a { color: #1f4e78; }
"""


def _fetch_options(connection: sqlite3.Connection, table: str, name_column: str = "name") -> list[tuple[str, str]]:
    rows = connection.execute(f"SELECT slug, {name_column} FROM {table} ORDER BY {name_column}").fetchall()
    return [(row[0], row[1]) for row in rows]


def _select_html(field: str, label: str, options: list[tuple[str, str]], selected: str) -> str:
    choices = [f'<option value="">{html.escape(label)} (tous)</option>']
    for slug, name in options:
        is_selected = " selected" if slug == selected else ""
        choices.append(f'<option value="{html.escape(slug)}"{is_selected}>{html.escape(name)}</option>')
    return f'<select name="{field}">' + "".join(choices) + "</select>"


def _format_count(value: object) -> str:
    return f"{int(value):,}".replace(",", " ") if value else "—"


def _sort_select_html(sort: str) -> str:
    options = [("name", "Nom"), ("popularity", "Popularité")]
    choices = "".join(
        f'<option value="{value}"{" selected" if value == sort else ""}>{label}</option>'
        for value, label in options
    )
    return f'<select name="sort">{choices}</select>'


def render_page(database_path: Path, term: str, category: str, tag: str, sort: str = "name") -> str:
    with _connect_readonly(database_path) as connection:
        categories = _fetch_options(connection, "categories")
        tags = _fetch_options(connection, "tags")

    rows = query_rows(
        database_path, term, category or None, tag or None, limit=200, sort=sort, read_only=True
    )

    result_rows = []
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
        categories_html = "".join(
            f'<span class="badge">{html.escape(name)}</span>'
            for name in (row["categories"] or "").split(",")
            if name
        )
        safe_url = _safe_link(row["official_url"])
        link = html.escape(safe_url or "")
        name = html.escape(row["name"])
        favicon = favicon_url(safe_url, size=32)
        # onerror : si le favicon distant ne charge pas (réseau filtré, TLS
        # intercepté...), on masque l'image cassée plutôt que de l'afficher.
        icon_html = (
            f'<img src="{html.escape(favicon)}" width="24" height="24" loading="lazy" alt="" '
            f'onerror="this.style.display=\'none\'">'
            if favicon
            else ""
        )
        popularity = ""
        if row["downloads"] or row["likes"]:
            popularity = f"{_format_count(row['downloads'])} téléchargements<br>{_format_count(row['likes'])} favoris"
        result_rows.append(
            f"<tr><td class=\"icon\">{icon_html}</td>"
            f"<td><a href=\"{link}\" target=\"_blank\" rel=\"noopener\">{name}</a>"
            f"<br><small>{html.escape(row['item_type'])} — {html.escape(row['company'] or 'Éditeur inconnu')}</small></td>"
            f"<td>{categories_html or '—'}</td>"
            f"<td>{html.escape(flags) or '—'}</td>"
            f"<td><small>{popularity or '—'}</small></td>"
            f"<td>{html.escape(row['description'] or '')}</td></tr>"
        )

    table = (
        "<table><thead><tr><th></th><th>Fiche</th><th>Catégories</th><th>Disponibilité</th>"
        "<th>Popularité</th><th>Description</th></tr></thead>"
        f"<tbody>{''.join(result_rows) or '<tr><td colspan=6>Aucun résultat.</td></tr>'}</tbody></table>"
    )

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Catalogue IA</title>
<style>{PAGE_STYLE}</style>
</head>
<body>
<h1>Catalogue IA</h1>
<p class="subtitle">Recherche locale en lecture seule sur la base SQLite du projet. Les icônes viennent du favicon du site officiel (chargées directement par ton navigateur) ; si elles ne s'affichent pas, c'est un blocage réseau côté navigateur (proxy, antivirus), pas la base.</p>
<form method="get">
<input type="text" name="q" placeholder="Rechercher un nom ou une description" value="{html.escape(term)}">
{_select_html("category", "Catégorie", categories, category)}
{_select_html("tag", "Tag", tags, tag)}
{_sort_select_html(sort)}
<button type="submit">Rechercher</button>
</form>
<p class="count">{len(rows)} résultat(s)</p>
{table}
</body>
</html>
"""


# CSP permissive uniquement là où le HTML existant en a besoin (style et
# gestionnaires onerror en ligne, favicons servis par Google) ; tout le reste
# (scripts distants, frames, plugins) reste bloqué.
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "img-src 'self' https://www.google.com; "
    "style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; "
    "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
)

SECURITY_HEADERS = {
    "Content-Security-Policy": CONTENT_SECURITY_POLICY,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}


def _make_handler(database_path: Path) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            if parsed.path not in ("/", ""):
                self.send_response(404)
                self.end_headers()
                return
            params = parse_qs(parsed.query)
            term = params.get("q", [""])[0]
            category = params.get("category", [""])[0]
            tag = params.get("tag", [""])[0]
            sort = params.get("sort", ["name"])[0]
            body = render_page(database_path, term, category, tag, sort).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            for header, value in SECURITY_HEADERS.items():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            print(f"[serve] {self.address_string()} {format % args}")

    return Handler


def run_server(database_path: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    handler = _make_handler(database_path)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Interface de recherche disponible sur http://{host}:{port} (Ctrl+C pour arrêter)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
