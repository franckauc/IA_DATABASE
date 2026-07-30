"""Collecteur Ollama — API REST locale officielle.

Documentation : https://github.com/ollama/ollama/blob/main/docs/api.md
Endpoint utilisé : GET http://localhost:11434/api/tags (modèles déjà téléchargés
localement par l'utilisateur). Nécessite qu'Ollama tourne sur la machine.
"""

from __future__ import annotations

import sqlite3

from ia_database.collectors.base import (
    CollectionSummary,
    ensure_category,
    ensure_platform,
    get_or_create_company,
    get_or_create_source,
    link_item_category,
    link_item_platform,
    record_source,
    upsert_catalog_item,
)
from ia_database.collectors.http import get_json

DEFAULT_HOST = "http://localhost:11434"
SOURCE_SLUG = "ollama-local-api"

# Correspondance famille de modèle -> éditeur connu (quand elle est fiable).
FAMILY_COMPANY = {
    "llama": "Meta",
    "gemma": "Google",
    "gemma2": "Google",
    "phi": "Microsoft",
    "phi3": "Microsoft",
    "mistral": "Mistral AI",
    "mixtral": "Mistral AI",
    "qwen": "Alibaba",
    "qwen2": "Alibaba",
}


def _slug_for(name: str) -> str:
    return "ollama-" + name.lower().replace(":", "--").replace("/", "--")


def collect(
    connection: sqlite3.Connection, host: str = DEFAULT_HOST, verify: bool = True
) -> CollectionSummary:
    summary = CollectionSummary(source="ollama")
    source_id = get_or_create_source(
        connection,
        slug=SOURCE_SLUG,
        name="Ollama — API locale",
        base_url=host,
        terms_url="https://ollama.com/terms",
        license_note="Modèles téléchargés localement, listés via l'API REST officielle d'Ollama.",
    )
    local_platform_id = ensure_platform(connection, "windows", "Windows")
    api_platform_id = ensure_platform(connection, "api", "API")
    category_id = ensure_category(connection, "local", "IA locale")
    model_category_id = ensure_category(connection, "modeles-ia", "Modèles IA")

    try:
        payload = get_json(f"{host}/api/tags", verify=verify)
    except Exception as error:  # noqa: BLE001
        summary.errors.append(
            f"Impossible de joindre Ollama sur {host} ({error}). "
            "Lancez `ollama serve` ou l'application Ollama avant de collecter."
        )
        return summary

    for model in payload.get("models", []):
        name = model.get("name") or model.get("model")
        if not name:
            summary.skipped += 1
            continue

        details = model.get("details") or {}
        family = details.get("family")
        base_name = name.split(":")[0]
        company_name = FAMILY_COMPANY.get(family)
        company_id = get_or_create_company(connection, company_name) if company_name else None

        description = "Modèle {family} ({size}, {quant}) disponible localement via Ollama.".format(
            family=family or base_name,
            size=details.get("parameter_size", "taille inconnue"),
            quant=details.get("quantization_level", "quantification inconnue"),
        )

        fields = {
            "name": name,
            "description": description,
            "official_url": f"https://ollama.com/library/{base_name}",
            "documentation_url": "https://ollama.com/library",
            "company_id": company_id,
            "works_offline": 1,
            "api_available": 1,
        }

        slug = _slug_for(name)
        item_id, created, changes = upsert_catalog_item(connection, slug, "model", fields)

        record_source(
            connection,
            source_id=source_id,
            item_id=item_id,
            external_id=model.get("digest") or name,
            source_url=f"https://ollama.com/library/{base_name}",
        )

        link_item_category(connection, item_id, category_id)
        link_item_category(connection, item_id, model_category_id)
        link_item_platform(connection, item_id, local_platform_id)
        link_item_platform(connection, item_id, api_platform_id)

        if created:
            summary.created += 1
        elif changes:
            summary.updated += 1
        else:
            summary.unchanged += 1

    return summary
