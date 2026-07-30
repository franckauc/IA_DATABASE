"""Collecteur OpenRouter — API publique officielle des modèles disponibles.

Documentation : https://openrouter.ai/docs/api-reference/list-available-models
Endpoint utilisé : GET https://openrouter.ai/api/v1/models (lecture publique, sans clé).
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
    upsert_pricing_plan,
)
from ia_database.collectors.http import get_json

API_URL = "https://openrouter.ai/api/v1/models"
SOURCE_SLUG = "openrouter-api"

# Correspondance préfixe d'identifiant -> nom d'éditeur lisible.
PROVIDER_NAMES = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google",
    "mistralai": "Mistral AI",
    "meta-llama": "Meta",
    "microsoft": "Microsoft",
    "perplexity": "Perplexity AI",
    "cohere": "Cohere",
    "qwen": "Alibaba",
    "deepseek": "DeepSeek",
}


def _slug_for(model_id: str) -> str:
    return "openrouter-" + model_id.lower().replace("/", "--")


def _price_per_million(raw_price: str | float | None) -> float | None:
    """Convertit un prix par token en prix par million de tokens.

    OpenRouter renvoie -1 pour signaler une tarification dynamique/variable :
    on la traite comme inconnue plutôt que comme un prix négatif invalide.
    """
    if raw_price in (None, ""):
        return None
    try:
        value = float(raw_price)
    except (TypeError, ValueError):
        return None
    if value < 0:
        return None
    return round(value * 1_000_000, 4)


def _is_negative(raw_price: str | float | None) -> bool:
    try:
        return float(raw_price) < 0
    except (TypeError, ValueError):
        return False


def collect(
    connection: sqlite3.Connection, limit: int | None = None, verify: bool = True
) -> CollectionSummary:
    summary = CollectionSummary(source="openrouter")
    source_id = get_or_create_source(
        connection,
        slug=SOURCE_SLUG,
        name="OpenRouter API",
        base_url="https://openrouter.ai/api/v1",
        terms_url="https://openrouter.ai/terms",
        license_note="Modèles et tarifs listés via l'API publique OpenRouter.",
    )
    api_platform_id = ensure_platform(connection, "api", "API")
    category_id = ensure_category(connection, "modeles-ia", "Modèles IA")

    try:
        payload = get_json(API_URL, verify=verify)
    except Exception as error:  # noqa: BLE001
        summary.errors.append(str(error))
        return summary

    models = payload.get("data", [])
    if limit:
        models = models[:limit]

    for model in models:
        model_id = model.get("id")
        if not model_id:
            summary.skipped += 1
            continue

        provider_key = model_id.split("/")[0] if "/" in model_id else None
        company_name = PROVIDER_NAMES.get(provider_key, provider_key.title() if provider_key else None)
        company_id = get_or_create_company(connection, company_name) if company_name else None

        pricing = model.get("pricing") or {}
        raw_prompt, raw_completion = pricing.get("prompt"), pricing.get("completion")
        prompt_price = _price_per_million(raw_prompt)
        completion_price = _price_per_million(raw_completion)
        is_dynamic = any(_is_negative(value) for value in (raw_prompt, raw_completion))
        is_free = not is_dynamic and (prompt_price or 0) == 0 and (completion_price or 0) == 0

        fields = {
            "name": model.get("name") or model_id,
            "description": (model.get("description") or "")[:500] or None,
            "official_url": f"https://openrouter.ai/{model_id}",
            "documentation_url": "https://openrouter.ai/docs",
            "company_id": company_id,
            "works_offline": 0,
            "api_available": 1,
        }

        slug = _slug_for(model_id)
        item_id, created, changes = upsert_catalog_item(connection, slug, "model", fields)

        record_source(
            connection,
            source_id=source_id,
            item_id=item_id,
            external_id=model_id,
            source_url=f"https://openrouter.ai/{model_id}",
        )

        link_item_category(connection, item_id, category_id)
        link_item_platform(connection, item_id, api_platform_id)

        if is_free:
            plan_name, pricing_type = "Accès gratuit", "free"
        elif is_dynamic:
            plan_name, pricing_type = "Tarification variable", "unknown"
        else:
            plan_name, pricing_type = "Tarification à l'usage", "paid"

        upsert_pricing_plan(
            connection,
            item_id=item_id,
            plan_name=plan_name,
            pricing_type=pricing_type,
            price_amount=prompt_price if pricing_type == "paid" else None,
            currency="USD" if pricing_type == "paid" else None,
            billing_period="1M tokens (prompt)" if pricing_type == "paid" else None,
            url=f"https://openrouter.ai/{model_id}",
        )
        if pricing_type == "paid" and completion_price is not None:
            upsert_pricing_plan(
                connection,
                item_id=item_id,
                plan_name="Tarification à l'usage (complétion)",
                pricing_type="paid",
                price_amount=completion_price,
                currency="USD",
                billing_period="1M tokens (complétion)",
                url=f"https://openrouter.ai/{model_id}",
            )

        if created:
            summary.created += 1
        elif changes:
            summary.updated += 1
        else:
            summary.unchanged += 1

    return summary
