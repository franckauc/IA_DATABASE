# IA_DATABASE

Catalogue local, extensible et sourcé des outils, modèles et services d'intelligence artificielle.

Le projet commence par une base SQLite locale. Les futurs collecteurs importeront uniquement des données accessibles via API ou sous des conditions de réutilisation compatibles.

**Consulter le catalogue en ligne, sans rien installer : https://franckauc.github.io/IA_DATABASE/**
(tableau interactif — recherche, tri, filtre par type ; données brutes aussi disponibles en [CSV](data/exports/catalogue_ia.csv) et [JSON](data/exports/catalogue_ia.json))

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

## « Toutes les IA du monde » ?

Il n'existe pas de registre exhaustif de toute l'intelligence artificielle dans le monde : aucune API ne recense les outils fermés, les projets privés ou ce qui sort chaque jour. Ce projet agrège les plus grandes sources publiques *légales* :

- **Hugging Face Hub** : plus d'1 million de modèles référencés. `collect huggingface --limit 0` pagine automatiquement jusqu'à épuisement du catalogue (plafonné à 20 000 fiches par collecte, pour rester raisonnable) ;
- **OpenRouter** : leur catalogue complet de modèles tient dans un seul appel — `collect openrouter` le récupère déjà en entier ;
- **Ollama** : uniquement les modèles que *toi* tu as téléchargés localement (pas de registre public légal pour tout le catalogue Ollama).

Pour tout avoir de ce qui est accessible :

```powershell
py -m ia_database collect huggingface --limit 0 --insecure
py -m ia_database collect openrouter --insecure
py -m ia_database collect ollama
```

Avec un jeton (`--hf-token`), les quotas de Hugging Face sont plus élevés et une collecte à `--limit 0` a moins de risque d'être ralentie par le rate-limiting anonyme.

## Collecter depuis les API officielles (v0.3)

Trois collecteurs alimentent automatiquement le catalogue depuis des API publiques et documentées, en conservant systématiquement leur source (`sources`/`source_records`) et l'historique des changements (`item_history`) :

```powershell
# Modèles les plus téléchargés sur Hugging Face Hub
py -m ia_database collect huggingface --limit 50

# Modèles et tarifs disponibles sur OpenRouter
py -m ia_database collect openrouter --limit 100

# Modèles déjà téléchargés localement (nécessite `ollama serve` en cours d'exécution)
py -m ia_database collect ollama

# Tout collecter d'un coup
py -m ia_database collect all
```

Si le réseau est filtré par un antivirus ou un proxy qui intercepte le TLS (erreur `CERTIFICATE_VERIFY_FAILED`), deux options :

- définis la variable d'environnement `REQUESTS_CA_BUNDLE` vers le certificat racine approprié ;
- ou ajoute `--insecure` à la commande `collect` pour désactiver la vérification TLS. À réserver à un réseau de confiance (ex. antivirus local qui inspecte le HTTPS) : ne jamais l'utiliser sur un réseau public.

Chaque fiche collectée garde sa provenance (`sources`/`source_records`) et journalise ses changements de champs dans `item_history`. Relancer une collecte est idempotent : les fiches déjà connues sont mises à jour, pas dupliquées.

L'API Hugging Face reste utilisable sans authentification, mais avec des quotas plus stricts. Pour les lever, passe un jeton (créé sur https://huggingface.co/settings/tokens) :

```powershell
py -m ia_database collect huggingface --hf-token hf_xxx
# ou, pour éviter de le taper à chaque fois :
$env:HF_TOKEN = "hf_xxx"
py -m ia_database collect huggingface
```

### Suivre l'état des sources

```powershell
py -m ia_database report
```

Affiche, pour chaque source (Hugging Face, OpenRouter, Ollama, fiches manuelles), le nombre de fiches liées, la dernière date de collecte et le nombre de changements journalisés dans `item_history`.

## Interface de recherche web locale

```powershell
py -m ia_database serve
```

Ouvre `http://127.0.0.1:8765` : recherche par mot-clé, filtre par catégorie et par tag, en lecture seule, avec l'icône du site officiel devant chaque fiche. Aucune dépendance supplémentaire (bibliothèque standard uniquement) ; à réserver à un usage local, sans authentification ni écriture.

## Icônes et popularité

La colonne icône (interface web et classeur Excel) affiche le favicon du site officiel de chaque fiche, via le service public de Google (`s2/favicons`) — aucun logo n'est téléchargé ni redistribué dans le dépôt, conformément au respect des marques.

- **Interface web** : l'icône est chargée directement par ton navigateur. Si elle ne s'affiche pas, ce n'est pas un problème de base de données — vérifie qu'un antivirus ou un proxy n'intercepte pas le TLS de ton navigateur (les images cassées sont masquées automatiquement plutôt que laissées visibles).
- **Classeur Excel** : l'icône est une vraie miniature intégrée. Les fiches qui partagent un domaine (des milliers de modèles Hugging Face, par exemple) ne déclenchent qu'un seul téléchargement grâce à un cache ; l'intégration reste plafonnée aux 300 fiches les plus pertinentes pour garder le fichier léger. Désactive-la avec `export --format xlsx --no-icons` pour un export instantané ou hors ligne. Si l'export affiche « aucune icône n'a pu être téléchargée », relance avec `--insecure` (réseau qui intercepte le TLS).

**Popularité** : le collecteur Hugging Face récupère aussi le nombre de téléchargements et de favoris de chaque modèle. Classe le catalogue par popularité :

```powershell
py -m ia_database search --sort popularity
```

Dans `serve`, un sélecteur « Popularité » fait la même chose ; dans le classeur Excel, la feuille Catalogue est triée par popularité par défaut (les fiches sans données de popularité — collecte OpenRouter, fiches manuelles — restent triées par nom). OpenRouter et Ollama n'exposent pas de métrique de popularité publique : seuls les modèles Hugging Face en ont une pour l'instant.

## Classeur Excel façon tableau de bord

```powershell
py -m ia_database export --format xlsx
```

Génère `data/exports/catalogue_ia.xlsx` avec neuf feuilles :

- **Tableau de bord** : indicateurs clés et graphique des fiches par catégorie ;
- **Catalogue** : toutes les fiches, avec éditeur, catégories, plateformes, tags ;
- **Categories**, **Plateformes**, **Tags** : listes avec nombre de fiches liées ;
- **Tarifs** : contenu de `pricing_plans` (gratuit, freemium, payant, variable...) ;
- **Licences** : contenu de `licenses`, avec les fiches concernées ;
- **Sources** : contenu de `sources`, avec nombre de fiches liées et dernière collecte ;
- **Historique** : contenu de `item_history` (valeurs avant/après par champ modifié).

Chaque feuille est un tableau Excel natif (en-têtes figés, filtres). Le classeur est une photo de la base au moment de l'export ; relance la commande pour le régénérer après une collecte.

## Principes

- Toute information importée conserve sa source et sa date de récupération.
- Les données incertaines restent nulles : une absence n'est jamais une affirmation.
- Les droits des marques, logos, API et annuaires tiers sont respectés.

Voir [la roadmap](docs/ROADMAP.md) pour les prochaines versions.
