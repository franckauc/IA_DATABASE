# IA_DATABASE

Catalogue local, extensible et sourcé des outils, modèles et services d'intelligence artificielle.

Le projet commence par une base SQLite locale. Les futurs collecteurs importeront uniquement des données accessibles via API ou sous des conditions de réutilisation compatibles.

## Démarrage rapide

Prérequis : Python 3.11 ou plus récent, installé et accessible via le lanceur `py`.

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
py -m pip install -e ".[dev]"
py scripts/init_database.py
py -m pytest
```

La commande crée `database/ai_catalog.db` depuis le schéma versionné. Cette base locale n'est pas versionnée.

## Utiliser le catalogue v0.2

Installe le projet en mode local, puis charge les données de démarrage :

```powershell
py -m pip install -e ".[dev]"
py -m ia_database seed
py -m ia_database stats
```

Quelques commandes utiles :

```powershell
# Rechercher par nom ou description
py -m ia_database search ollama

# Voir les outils de programmation
py -m ia_database search --category programmation

# Exporter le catalogue
py -m ia_database export --format csv
py -m ia_database export --format json
```

Les exports sont écrits dans `data/exports/`. Le jeu initial contient une sélection de plateformes connues, leurs liens officiels et leur provenance ; il est conçu comme point de départ, pas comme un annuaire exhaustif.

## Principes

- Toute information importée conserve sa source et sa date de récupération.
- Les données incertaines restent nulles : une absence n'est jamais une affirmation.
- Les droits des marques, logos, API et annuaires tiers sont respectés.

Voir [la roadmap](docs/ROADMAP.md) pour les prochaines versions.
