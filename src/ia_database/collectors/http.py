"""Client HTTP partagé par les collecteurs."""

from __future__ import annotations

from typing import Any

import requests

USER_AGENT = "ia-database-collector/0.3 (+https://github.com/)"
DEFAULT_TIMEOUT = 20


def get(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    verify: bool = True,
) -> requests.Response:
    """Effectue un GET et retourne la réponse complète (utile pour lire les en-têtes de pagination).

    `verify=False` désactive la vérification du certificat TLS. Ne sert que sur
    un réseau dont l'inspection HTTPS (proxy, antivirus) casse la chaîne de
    confiance par défaut ; à éviter sinon.
    """
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    if not verify:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(
        url, params=params, headers=request_headers, timeout=DEFAULT_TIMEOUT, verify=verify
    )
    response.raise_for_status()
    return response


def get_json(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    verify: bool = True,
) -> Any:
    """Effectue un GET et retourne le JSON décodé, ou lève une erreur explicite."""
    return get(url, params=params, headers=headers, verify=verify).json()
