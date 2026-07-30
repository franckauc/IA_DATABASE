"""Collecteur Hugging Face Hub — API publique officielle.

Documentation : https://huggingface.co/docs/hub/api
Endpoint utilisé : GET https://huggingface.co/api/models (lecture publique, sans clé).
"""

from __future__ import annotations

import os
import re
import sqlite3
import time

from ia_database.collectors.base import (
    CollectionSummary,
    ensure_category,
    ensure_platform,
    get_or_create_company,
    get_or_create_license,
    get_or_create_source,
    link_item_category,
    link_item_license,
    link_item_platform,
    record_source,
    upsert_catalog_item,
)
from ia_database.collectors.http import get as http_get

API_URL = "https://huggingface.co/api/models"
SOURCE_SLUG = "huggingface-api"
PAGE_SIZE = 1000
# Le Hub référence plus d'un million de modèles ; ce plafond borne le temps
# d'une collecte "illimitée" (--limit 0) à quelques dizaines de requêtes.
DEFAULT_UNLIMITED_CAP = 20_000
NEXT_LINK_PATTERN = re.compile(r'<([^>]+)>;\s*rel="next"')

# Licences couramment considérées comme open source.
OPEN_LICENSES = {
    "apache-2.0", "mit", "bsd-3-clause", "bsd-2-clause", "gpl-3.0", "lgpl-3.0",
    "openrail", "creativeml-openrail-m", "cc-by-4.0", "cc-by-sa-4.0", "mpl-2.0",
    "llama2", "llama3", "llama3.1", "llama3.2", "gemma",
}

# Valeurs de licence trop vagues pour être enregistrées telles quelles.
VAGUE_LICENSE_VALUES = {"other", "unknown", ""}

# Normalise les identifiants de licence courants vers un nom lisible,
# pour fusionner avec les licences déjà connues plutôt que dupliquer.
LICENSE_DISPLAY_NAMES = {
    "apache-2.0": "Apache License 2.0",
    "mit": "MIT License",
    "bsd-3-clause": "BSD 3-Clause License",
    "bsd-2-clause": "BSD 2-Clause License",
    "gpl-3.0": "GNU General Public License v3.0",
    "lgpl-3.0": "GNU Lesser General Public License v3.0",
    "mpl-2.0": "Mozilla Public License 2.0",
    "cc-by-4.0": "Creative Commons Attribution 4.0",
    "cc-by-sa-4.0": "Creative Commons Attribution-ShareAlike 4.0",
    "creativeml-openrail-m": "CreativeML Open RAIL-M",
}

# Correspondance grossière pipeline_tag -> catégorie existante.
PIPELINE_CATEGORY = {
    "text-generation": "modeles-ia",
    "text2text-generation": "modeles-ia",
    "conversational": "assistant-generaliste",
    "text-to-image": "images",
    "image-to-image": "images",
    "text-to-video": "video",
    "image-to-video": "video",
    "text-to-speech": "voix-audio",
    "automatic-speech-recognition": "voix-audio",
    "audio-to-audio": "voix-audio",
}


def _slug_for(model_id: str) -> str:
    return "hf-" + model_id.lower().replace("/", "--")


def _extract_license(model: dict) -> str | None:
    """Lit la licence depuis cardData (fiche détaillée) ou le tag `license:...` (liste)."""
    card_license = (model.get("cardData") or {}).get("license")
    if card_license:
        return str(card_license)
    for tag in model.get("tags", []):
        if isinstance(tag, str) and tag.startswith("license:"):
            return tag.split(":", 1)[1]
    return model.get("license")


def _iter_pages(headers: dict[str, str] | None, verify: bool):
    """Parcourt les pages de l'API en suivant l'en-tête Link (rel="next")."""
    url: str | None = API_URL
    params: dict[str, object] | None = {
        "sort": "downloads",
        "direction": -1,
        "limit": PAGE_SIZE,
        "full": "true",
    }
    while url:
        response = None
        for attempt in range(3):
            try:
                response = http_get(url, params=params, headers=headers, verify=verify)
                break
            except Exception as error:  # noqa: BLE001
                status = getattr(getattr(error, "response", None), "status_code", None)
                if status == 429 and attempt < 2:
                    time.sleep(2**attempt * 2)
                    continue
                raise
        assert response is not None
        yield response.json()
        match = NEXT_LINK_PATTERN.search(response.headers.get("Link", ""))
        url = match.group(1) if match else None
        params = None  # déjà encodés dans l'URL "next"


def collect(
    connection: sqlite3.Connection,
    limit: int = 50,
    verify: bool = True,
    token: str | None = None,
) -> CollectionSummary:
    """Collecte les modèles les plus populaires du Hub, en paginant si besoin.

    `limit` <= 0 signifie « sans limite » : la pagination continue jusqu'à
    épuisement du catalogue ou jusqu'à `DEFAULT_UNLIMITED_CAP`, ce qui reste
    une fraction du Hub (plus d'un million de modèles au total) — il n'existe
    pas de registre exhaustif de « toute l'IA au monde », seulement de grandes
    sources publiques comme celle-ci.
    `token` (ou la variable d'environnement `HF_TOKEN`) est optionnel : sans
    lui, l'API reste utilisable mais avec des quotas plus stricts, surtout
    pour de grosses collectes.
    """
    summary = CollectionSummary(source="huggingface")
    token = token or os.environ.get("HF_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else None
    source_id = get_or_create_source(
        connection,
        slug=SOURCE_SLUG,
        name="Hugging Face Hub API",
        base_url="https://huggingface.co/api",
        terms_url="https://huggingface.co/terms-of-service",
        license_note="Modèles publics listés via l'API officielle du Hub.",
    )
    api_platform_id = ensure_platform(connection, "api", "API")
    web_platform_id = ensure_platform(connection, "web", "Web")

    target = limit if limit and limit > 0 else DEFAULT_UNLIMITED_CAP
    processed = 0

    try:
        for page in _iter_pages(headers, verify):
            if not page:
                break
            for model in page:
                if processed >= target:
                    break
                processed += 1
                _process_model(connection, model, source_id, api_platform_id, web_platform_id, summary)
            if processed >= target:
                break
    except Exception as error:  # noqa: BLE001 - on garde ce qui a déjà été traité
        summary.errors.append(str(error))

    return summary


def _process_model(
    connection: sqlite3.Connection,
    model: dict,
    source_id: int,
    api_platform_id: int,
    web_platform_id: int,
    summary: CollectionSummary,
) -> None:
    model_id = model.get("id") or model.get("modelId")
    if not model_id:
        summary.skipped += 1
        return

    pipeline_tag = model.get("pipeline_tag")
    license_id = _extract_license(model)
    org = model_id.split("/")[0] if "/" in model_id else None
    company_id = get_or_create_company(connection, org, f"https://huggingface.co/{org}") if org else None

    fields = {
        "name": model_id,
        # Stable : ne pas y mêler downloads/likes (colonnes dédiées, qui elles
        # varient à chaque collecte) sous peine de journaliser un faux
        # changement de description à chaque exécution de `collect`.
        "description": f"Modèle Hugging Face ({pipeline_tag or 'tâche non précisée'}).",
        "official_url": f"https://huggingface.co/{model_id}",
        "documentation_url": f"https://huggingface.co/{model_id}",
        "company_id": company_id,
        "is_open_source": 1 if (license_id or "").lower() in OPEN_LICENSES else 0,
        "works_offline": 1,
        "api_available": 1,
        "downloads": model.get("downloads"),
        "likes": model.get("likes"),
    }

    slug = _slug_for(model_id)
    item_id, created, changes = upsert_catalog_item(connection, slug, "model", fields)

    source_record_id = record_source(
        connection,
        source_id=source_id,
        item_id=item_id,
        external_id=model_id,
        source_url=f"https://huggingface.co/{model_id}",
    )
    if changes:
        # Rejoue la journalisation avec le bon source_record_id (créé après l'upsert).
        for field_name in changes:
            connection.execute(
                """
                UPDATE item_history SET source_record_id = ?
                WHERE item_id = ? AND field_name = ? AND source_record_id IS NULL
                """,
                (source_record_id, item_id, field_name),
            )

    category_slug = PIPELINE_CATEGORY.get(pipeline_tag, "modeles-ia")
    category_id = ensure_category(connection, category_slug, category_slug.replace("-", " ").title())
    link_item_category(connection, item_id, category_id)
    link_item_platform(connection, item_id, api_platform_id)
    link_item_platform(connection, item_id, web_platform_id)

    if license_id and license_id.lower() not in VAGUE_LICENSE_VALUES:
        display_name = LICENSE_DISPLAY_NAMES.get(license_id.lower(), license_id)
        license_row_id = get_or_create_license(connection, name=display_name, spdx_id=license_id)
        link_item_license(connection, item_id, license_row_id)

    if created:
        summary.created += 1
    elif changes:
        summary.updated += 1
    else:
        summary.unchanged += 1
