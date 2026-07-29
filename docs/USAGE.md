# Utiliser IA_DATABASE

## Initialisation

Depuis la racine du projet :

```powershell
py -m pip install -e ".[dev]"
py -m ia_database seed
```

`seed` crée la base si nécessaire, installe le schéma et charge les données de démarrage. La commande est idempotente : elle peut être relancée sans créer de doublons.

## Recherche

```powershell
py -m ia_database search "image"
py -m ia_database search --category programmation
py -m ia_database search --category local --limit 10
```

Les slugs de catégories actuellement fournis sont : `assistant-generaliste`, `programmation`, `modeles-ia`, `local`, `images`, `video`, `voix-audio`, `recherche`, `automatisation` et `developpement-web`.

## Exports

```powershell
py -m ia_database export --format csv
py -m ia_database export --format json
py -m ia_database export --format csv --output .\mon-catalogue.csv
```

Un CSV peut être ouvert directement dans Excel. Les fichiers par défaut vont dans `data/exports/`, un répertoire ignoré par Git.

## Édition manuelle avec SQLite

Ouvre `database/ai_catalog.db` avec DB Browser for SQLite. Les tables principales sont :

- `catalog_items` : les fiches d'outils, services, modèles ou frameworks ;
- `companies` et `categories` : référentiels ;
- `item_categories` et `item_platforms` : associations multiples ;
- `sources` et `source_records` : origine de chaque fiche.

Pour une nouvelle fiche manuelle, créer d'abord l'éditeur et la catégorie, ensuite la fiche, puis son association et sa source. Ne pas ajouter de données dont la provenance ou les droits de réutilisation sont inconnus.
