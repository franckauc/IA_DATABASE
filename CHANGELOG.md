# Changelog

## [Non publié]

### Ajouté

- colonnes `downloads`/`likes` sur `catalog_items`, remplies par le
  collecteur Hugging Face ; tri par popularité (`search --sort popularity`,
  sélecteur dans `serve`, tri par défaut de la feuille Catalogue) ;
- migration automatique des bases déjà créées (ajout des colonnes sans perte
  de données) ;
- jeton Hugging Face optionnel (`collect --hf-token` ou variable `HF_TOKEN`)
  pour lever les quotas anonymes de l'API ;
- commande `ia-database report` : nombre de fiches et dernière collecte par
  source, nombre de changements journalisés ;
- commande `ia-database serve` : interface de recherche web locale en lecture
  seule (recherche texte, filtre catégorie/tag), sans dépendance
  supplémentaire (bibliothèque standard uniquement) ;
- colonne icône (favicon du site officiel) dans l'interface de recherche et
  dans le classeur Excel (miniatures intégrées, best-effort via
  `export --format xlsx`, désactivable avec `--no-icons`) ;
- pagination réelle du collecteur Hugging Face (suit l'en-tête `Link` de
  l'API) : `collect huggingface --limit 0` récupère jusqu'à 20 000 modèles au
  lieu d'être limité à un seul appel ;
- 35 nouvelles fiches de démarrage vérifiées manuellement le 2026-07-29
  (génération d'images/musique/vidéo, écriture assistée, assistants
  supplémentaires, hébergement de modèles, automatisation) : le catalogue
  passe de 16 à 51 fiches, avec 5 nouvelles catégories (musique, écriture,
  design, traduction, hébergement de modèles).

### Corrigé

- l'export Excel avec icônes pouvait prendre des heures sur un grand
  catalogue (des milliers de fiches partageant le même domaine
  déclenchaient chacune un téléchargement) ; un cache par domaine ramène
  ça à quelques secondes, et l'intégration d'icônes est plafonnée aux 300
  fiches les plus pertinentes (les plus populaires en premier) pour garder
  un fichier léger ;
- la description des modèles Hugging Face intégrait les compteurs de
  téléchargements/favoris en texte, ce qui journalisait un faux changement
  dans `item_history` à chaque collecte ; ces compteurs ont maintenant leurs
  propres colonnes, la description ne bouge plus inutilement.

## [0.3.0] - 2026-07-29

### Ajouté

- collecteurs Hugging Face Hub, OpenRouter et Ollama utilisant leurs API officielles ;
- journalisation automatique des changements de fiches dans `item_history` ;
- tarifs collectés dans `pricing_plans` (OpenRouter) ;
- tags et licences des fiches de démarrage (`tags`, `licenses`) et détection
  automatique de licence par le collecteur Hugging Face ;
- recherche par tag (`search --tag`) et statistiques enrichies (`stats`) ;
- option `collect --insecure` pour les réseaux dont l'inspection HTTPS casse
  la vérification TLS (proxy ou antivirus intercepteur) ;
- commande `ia-database collect <source|all>` ;
- export `--format xlsx` : classeur Excel multi-feuilles (Catalogue, Categories,
  Plateformes, Tags, Tarifs, Licences, Sources, Historique) avec tableaux
  filtrables et tableau de bord (indicateurs + graphique par catégorie).

### Corrigé

- le collecteur OpenRouter plantait sur les modèles à tarification variable
  (prix renvoyé à `-1` par l'API) ; ces tarifs sont maintenant enregistrés
  comme `unknown` plutôt que de violer la contrainte `price_amount >= 0` ;
- le collecteur Hugging Face ne détectait aucune licence car l'API liste les
  modèles avec la licence encodée en tag (`license:apache-2.0`) et non dans
  `cardData` ; les deux formats sont maintenant lus.

## [0.2.0] - 2026-07-28

### Ajouté

- catégories, plateformes et 16 fiches de démarrage sourcées ;
- commande `ia-database` : initialisation, chargement, recherche, statistiques et export ;
- exports CSV et JSON locaux.

## [0.1.0] - 2026-07-28

### Ajouté

- structure initiale du projet ;
- schéma SQLite normalisé ;
- script idempotent d'initialisation ;
- test de validité du schéma ;
- documentation de démarrage et roadmap.
