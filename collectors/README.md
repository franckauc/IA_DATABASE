# Collecteurs

Chaque collecteur doit utiliser une API officielle ou une source dont la réutilisation est explicitement autorisée. Il enregistre la source, l'identifiant externe, l'URL et la date de récupération dans `source_records`, et journalise les champs modifiés dans `item_history`.

Le code vit dans [`src/ia_database/collectors/`](../src/ia_database/collectors/) :

- `base.py` — upsert des fiches, gestion des sources et de l'historique, commun à tous les collecteurs ;
- `http.py` — client HTTP partagé (User-Agent, timeout) ;
- `huggingface.py` — API publique du Hub Hugging Face (`GET /api/models`) ;
- `openrouter.py` — API publique OpenRouter (`GET /api/v1/models`), inclut les tarifs ;
- `ollama.py` — API REST locale d'Ollama (`GET /api/tags`), nécessite `ollama serve`.

Lancer une collecte : `py -m ia_database collect <huggingface|openrouter|ollama|all>`.
