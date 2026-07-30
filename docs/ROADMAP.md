# Roadmap

## v0.1 — Fondation

- [x] arborescence et métadonnées Python ;
- [x] schéma SQLite initial ;
- [x] script d'initialisation et test de schéma.

## v0.2 — Base et données de référence

- [x] catégories et plateformes initiales ;
- [x] jeu de fiches initiales avec URLs et sources officielles ;
- [x] commandes de création, recherche et export CSV/JSON.

## v0.3 — Collecteurs autorisés et classeur Excel

- [x] connecteurs Hugging Face Hub, OpenRouter et Ollama (API officielles, sans scraping) ;
- [x] provenance (`sources`/`source_records`) et historique des changements (`item_history`) ;
- [x] export classeur Excel multi-feuilles filtrable (`export --format xlsx`) avec tableau de bord.

## v0.4 — Rapport et interface de recherche

- [x] tags et licences renseignés (fiches de démarrage + détection automatique
      côté Hugging Face) ;
- [x] jeton Hugging Face optionnel (`--hf-token` / `HF_TOKEN`) pour lever les
      quotas anonymes ;
- [x] commande `report` : état de synchronisation par source ;
- [x] interface de recherche locale (`ia-database serve`), sans dépendance
      supplémentaire.

## v0.5 — Suite

- authentification optionnelle pour OpenRouter (jeton, si des routes privées
  sont ajoutées) ;
- synchronisation planifiée (tâche planifiée / cron côté utilisateur) ;
- gestion de logos lorsque leur licence le permet.
