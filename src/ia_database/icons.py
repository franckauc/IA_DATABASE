"""Résolution d'icône partagée par l'interface web et l'export Excel.

Utilise le service public de favicons de Google (pas de clé requise) plutôt
que d'héberger des logos de marques tierces dans le dépôt.
"""

from __future__ import annotations

from urllib.parse import urlsplit

FAVICON_SERVICE = "https://www.google.com/s2/favicons?sz={size}&domain={domain}"


def favicon_url(official_url: str | None, size: int = 64) -> str | None:
    if not official_url:
        return None
    domain = urlsplit(official_url).netloc
    if not domain:
        return None
    return FAVICON_SERVICE.format(size=size, domain=domain)
